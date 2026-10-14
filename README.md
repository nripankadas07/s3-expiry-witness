# s3-expiry-witness

Evaluate explicit expiration-only rules for captured objects in a never-versioned bucket, explain excluded filters, calculate UTC eligibility and identify every earliest winning rule.

Built for s3 bucket owners reviewing captured expiration rules before operational deployment. Overlapping prefix/tag/size rules and UTC day rounding obscure the earliest expiration eligibility for a specific object.

## Quickstart

Python 3.10+; no runtime dependencies. The build uses setuptools from the official Python registry. This repository is the install source; no external registry release is claimed.

```sh
git clone https://github.com/nripankadas07/s3-expiry-witness.git
cd s3-expiry-witness
python -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/s3-expiry-witness example.json
```

On Windows, use `.venv\Scripts\python` and `.venv\Scripts\s3-expiry-witness`. Windows behavior has not been exercised; Linux CI is configured to verify Python 3.10, 3.12 and 3.14. An input filename or `-` for standard input is required. Valid analysis returns exit 0, including negative findings; malformed or unsupported input returns exit 2 and a JSON error on stderr. Input is bounded to 1 MiB; duplicate JSON keys and nonfinite numbers fail.

The runnable [example](example.json) uses synthetic data. Run `python s3_expiry_witness.py example.json` directly for a source-only demo. Import `analyze(data)` for the Python API; unsupported input raises an exception. The tool makes no network request or operational write.

## Input and output contract

Input has exactly versioning="Disabled", now (timezone-aware ISO timestamp), Rules and objects. Rules use ID, Status, Filter and Expiration with either Days or Date. Filter is empty or one Prefix/Tag/size constraint; combined constraints require And with at least two explicit elements and Tags array. Size bounds are exclusive. Objects use exactly Key, Size, LastModified and Tags (string dictionary). Unique rule IDs/keys required. No unsupported action is silently ignored.

The example's installed behavior is asserted in [test_installed_cli.py](test_installed_cli.py). [Unit cases](test_behavior.py) cover positive decisions and meaningful failure cases. The report records actual captured evidence; absence of a finding does not certify an operational environment.

## Limits

Eligibility is not actual deletion timing. No cloud connection or bucket change. General-purpose never-versioned buckets only; no versioning/suspended state, transitions, noncurrent versions, delete markers, directory buckets, replication/retention locks or billing. LastModified is the caller-supplied creation/modification timestamp. Date must be midnight UTC; Days positive. At most 1000 rules/objects; no prediction of service scheduling.

## Validation and research

Run `python -m unittest -v` and `python -m compileall -q s3_expiry_witness.py`. [Validation](VALIDATION.md) records exercised configurations. [Research and candidate brief](RESEARCH.md) compares current alternatives and states the inferred demand. No customer adoption or measured performance advantage is claimed.

## Contributing and support

[Contribution guide](CONTRIBUTING.md) · [Support](SUPPORT.md) · [Security](SECURITY.md) · [MIT license](LICENSE)

Original implementation developed with AI assistance and reviewed through acceptance tests. No competitor source, branding or prose was copied. Primary specifications informed the explicitly supported semantics.
