"""Offline bounded s3-expiry-witness analyzer. No operational writes."""

from datetime import datetime,timezone,timedelta,time

def stamp(s):
    if not isinstance(s,str):raise ValueError('timestamp must be string')
    try:v=datetime.fromisoformat(s.replace('Z','+00:00'))
    except ValueError:raise ValueError('invalid timestamp') from None
    if v.tzinfo is None:raise ValueError('timestamp requires timezone')
    return v.astimezone(timezone.utc)

def integer(v,positive=False):
    if type(v)!=int or v<(1 if positive else 0):raise ValueError('nonnegative integer required')
    return v

def filter_rule(f):
    if not isinstance(f,dict):raise ValueError('Filter must be object')
    if 'And' in f:
        if set(f)!={'And'} or not isinstance(f['And'],dict):raise ValueError('invalid And')
        f=f['And']
        allowed={'Prefix','Tags','ObjectSizeGreaterThan','ObjectSizeLessThan'}
        if len(f)<2:raise ValueError('And needs at least two explicit filter elements')
    else:
        allowed={'Prefix','Tag','ObjectSizeGreaterThan','ObjectSizeLessThan'}
        if len(f)>1:raise ValueError('combined filters require And')
    if set(f)-allowed:raise ValueError('unsupported filter element')
    prefix=f.get('Prefix','')
    if not isinstance(prefix,str):raise ValueError('Prefix must be string')
    tags=f.get('Tags',[f['Tag']] if 'Tag' in f else [])
    if not isinstance(tags,list):raise ValueError('Tags must be list')
    tagmap={}
    for tag in tags:
        if not isinstance(tag,dict) or set(tag)!={'Key','Value'} or any(not isinstance(tag[x],str) for x in tag):raise ValueError('invalid Tag')
        if tag['Key'] in tagmap:raise ValueError('duplicate filter tag')
        tagmap[tag['Key']]=tag['Value']
    lower=integer(f['ObjectSizeGreaterThan']) if 'ObjectSizeGreaterThan' in f else None
    upper=integer(f['ObjectSizeLessThan']) if 'ObjectSizeLessThan' in f else None
    if lower is not None and upper is not None and lower>=upper:raise ValueError('empty size interval')
    return prefix,tagmap,lower,upper

def analyze(d):
    if not isinstance(d,dict) or set(d)!={'versioning','now','Rules','objects'} or d['versioning']!='Disabled':raise ValueError('only never-versioned general-purpose buckets supported')
    now=stamp(d['now']);rules=d['Rules'];objects=d['objects']
    if not isinstance(rules,list) or len(rules)>1000 or not isinstance(objects,list) or len(objects)>1000:raise ValueError('at most 1000 rules/objects')
    parsed=[];ids=set()
    for r in rules:
        if not isinstance(r,dict) or set(r)-{'ID','Status','Filter','Expiration'} or not {'ID','Status','Filter','Expiration'}<=set(r):raise ValueError('only explicit ID/Status/Filter/Expiration rules supported')
        rid=r['ID'];status=r['Status'];ex=r['Expiration']
        if not isinstance(rid,str) or not 1<=len(rid)<=255 or rid in ids or status not in ('Enabled','Disabled'):raise ValueError('unique ID and valid Status required')
        ids.add(rid);f=filter_rule(r['Filter'])
        if not isinstance(ex,dict) or set(ex) not in ({'Days'},{'Date'}):raise ValueError('only Days or Date expiration supported')
        if 'Days' in ex:integer(ex['Days'],True)
        else:
            dt=stamp(ex['Date'])
            if dt.time()!=time(0):raise ValueError('expiration Date must be midnight UTC')
        parsed.append((rid,status,f,ex))
    rows=[];keys=set()
    for o in objects:
        if not isinstance(o,dict) or set(o)!={'Key','Size','LastModified','Tags'}:raise ValueError('expected Key/Size/LastModified/Tags')
        key=o['Key'];size=integer(o['Size']);modified=stamp(o['LastModified']);tags=o['Tags']
        if not isinstance(key,str) or key in keys or not isinstance(tags,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in tags.items()):raise ValueError('unique key/string tags required')
        if modified>now:raise ValueError('object timestamp later than capture time')
        keys.add(key);matches=[];excluded=[]
        for rid,status,(prefix,rt,lo,hi),ex in parsed:
            reasons=[]
            if status!='Enabled':reasons.append('disabled')
            if not key.startswith(prefix):reasons.append('prefix')
            if any(tags.get(k)!=v for k,v in rt.items()):reasons.append('tags')
            if lo is not None and size<=lo:reasons.append('size_lower_exclusive')
            if hi is not None and size>=hi:reasons.append('size_upper_exclusive')
            if reasons:excluded.append({'rule':rid,'reasons':reasons});continue
            if 'Date' in ex:due=stamp(ex['Date'])
            else:due=datetime.combine((modified+timedelta(days=ex['Days'])).date()+timedelta(days=1),time(0),timezone.utc)
            matches.append({'rule':rid,'eligible_at':due.isoformat(),'eligible_now':now>=due})
        earliest=min((x['eligible_at'] for x in matches),default=None)
        rows.append({'key':key,'matches':matches,'excluded':excluded,'earliest_eligible_at':earliest,'winning_rules':[x['rule'] for x in matches if x['eligible_at']==earliest],'eligible_now':earliest is not None and now>=stamp(earliest)})
    return {'objects':rows,'deletion_executed':False,'eligibility_not_execution':True}

def _pairs(pairs):
    result={}
    for key,val in pairs:
        if key in result:raise ValueError('duplicate JSON key: '+key)
        result[key]=val
    return result

def main():
    import argparse,json,sys
    from pathlib import Path
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',help='JSON input path; - for stdin')
    args=parser.parse_args()
    try:
        raw=sys.stdin.buffer.read(1048577) if args.input=='-' else Path(args.input).open('rb').read(1048577)
        if len(raw)>1048576:raise ValueError('input exceeds 1 MiB')
        data=json.loads(raw,object_pairs_hook=_pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON number')))
        print(json.dumps(analyze(data),ensure_ascii=True,indent=2));return 0
    except (ValueError,TypeError,KeyError,OverflowError,RecursionError,OSError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
