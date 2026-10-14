import unittest
from s3_expiry_witness import analyze

def fixture(filter=None,expiration=None,modified='2026-10-10T12:00:00Z',size=100,tags=None,now='2026-10-14T00:00:00Z'):
    return {'versioning':'Disabled','now':now,'Rules':[{'ID':'r','Status':'Enabled','Filter':filter or {},'Expiration':expiration or {'Days':3}}],'objects':[{'Key':'logs/a','Size':size,'LastModified':modified,'Tags':tags or {}}]}
class Behavior(unittest.TestCase):
    def test_next_midnight(self):self.assertEqual(analyze(fixture())['objects'][0]['earliest_eligible_at'],'2026-10-14T00:00:00+00:00')
    def test_not_due(self):self.assertFalse(analyze(fixture(now='2026-10-13T23:59:59Z'))['objects'][0]['eligible_now'])
    def test_offset_utc(self):self.assertEqual(analyze(fixture(modified='2026-10-10T23:30:00-02:00'))['objects'][0]['earliest_eligible_at'],'2026-10-15T00:00:00+00:00')
    def test_date(self):self.assertTrue(analyze(fixture(expiration={'Date':'2026-10-12T00:00:00Z'}))['objects'][0]['eligible_now'])
    def test_prefix(self):self.assertEqual(analyze(fixture(filter={'Prefix':'other/'}))['objects'][0]['excluded'][0]['reasons'],['prefix'])
    def test_and_tags(self):self.assertFalse(analyze(fixture(filter={'And':{'Prefix':'logs/','Tags':[{'Key':'x','Value':'y'}]}}))['objects'][0]['eligible_now'])
    def test_lower_exclusive(self):self.assertFalse(analyze(fixture(filter={'ObjectSizeGreaterThan':100}))['objects'][0]['eligible_now'])
    def test_upper_exclusive(self):self.assertFalse(analyze(fixture(filter={'ObjectSizeLessThan':100}))['objects'][0]['eligible_now'])
    def test_shorter_wins(self):
        d=fixture();d['Rules'].append({'ID':'short','Status':'Enabled','Filter':{},'Expiration':{'Days':1}});self.assertEqual(analyze(d)['objects'][0]['winning_rules'],['short'])
    def test_disabled(self):
        d=fixture();d['Rules'][0]['Status']='Disabled';self.assertFalse(analyze(d)['objects'][0]['eligible_now'])
    def test_versioning_rejected(self):
        d=fixture();d['versioning']='Enabled'
        with self.assertRaises(ValueError):analyze(d)
    def test_not_midnight(self):
        with self.assertRaises(ValueError):analyze(fixture(expiration={'Date':'2026-10-12T01:00:00Z'}))
    def test_transition_rejected(self):
        d=fixture();d['Rules'][0]['Transitions']=[]
        with self.assertRaises(ValueError):analyze(d)
    def test_future_object(self):
        with self.assertRaises(ValueError):analyze(fixture(modified='2026-10-15T00:00:00Z'))
    def test_combined_filter_requires_and(self):
        with self.assertRaises(ValueError):analyze(fixture(filter={'Prefix':'logs/','ObjectSizeGreaterThan':10}))

if __name__=="__main__":unittest.main()
