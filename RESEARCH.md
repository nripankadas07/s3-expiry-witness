# Candidate brief and comparison — 14 October 2026

**User:** S3 bucket owners reviewing captured expiration rules before operational deployment. **Painful task:** Overlapping prefix/tag/size rules and UTC day rounding obscure the earliest expiration eligibility for a specific object.

**Smallest useful capability:** Evaluate explicit expiration-only rules for captured objects in a never-versioned bucket, explain excluded filters, calculate UTC eligibility and identify every earliest winning rule.

**Acceptance:** the supplied synthetic example must produce the documented installed result; core edge cases and invalid-input paths must pass; a wheel installed outside the checkout must run the CLI and reject malformed input. The public default commit, remote matrix CI and rendered documentation must be verified before LIVE.

**Demand evidence:** inferred from the workflow and relevant accessible documentation/issues, not a verified customer request. **Discovery path:** descriptive repository topics, a runnable example, searchable edge-case documentation and the user's chronological portfolio index. No unsolicited promotion is performed.

**Distinctness:** No S3 lifecycle evaluator existed in the inventory. OCI/TAR tools inspect filesystem/archive effects, not cloud object age/tag/size eligibility. The five selected candidates have different users, state models and acceptance contracts.

## Current comparables

minio/minio is the highest-star relevant S3-compatible storage implementation found in the broader s3 query. The s3 lifecycle query alone was sparse and returned broader products; no exhaustive ranking is claimed. Queries were executed live on GitHub with Sort by Most stars. Search result coverage is bounded to visible first pages, then relevant established repositories; stars inform discovery, not quality or performance.

| Repository | Stars observed | Latest push observed UTC | License metadata | Observation UTC |
| --- | ---: | --- | --- | --- |
| [minio/minio](https://github.com/minio/minio) | 61324 | 2026-04-24T17:54:39Z | AGPL-3.0 | 2026-10-14T06:09:44.017Z |
| [cloud-custodian/cloud-custodian](https://github.com/cloud-custodian/cloud-custodian) | 6085 | 2026-10-13T17:34:59Z | Apache-2.0 | 2026-10-14T06:09:43.329Z |
| [aws/aws-cli](https://github.com/aws/aws-cli) | 17309 | 2026-10-14T04:36:12Z | NOASSERTION | 2026-10-14T06:09:43.049Z |

MinIO implements object storage lifecycle behavior but its current README says unmaintained and the repository is archived. AWS CLI reads/writes real configurations; Cloud Custodian manages cloud policies. This MVP supports review of captured expiration-only inputs without credentials.

Comparables' current READMEs, installation examples and accessible issues were inspected. Established tools supply broader integration, docs and community support; this project's support consists of reproducible GitHub reports, source tests and explicit bounded semantics. Its clean install has no runtime dependencies, but that alone establishes no time-to-first-result or reliability advantage. Comparator install success and benchmark performance were not measured. License metadata marked NOASSERTION is unresolved metadata, not a permissive-reuse claim. No reuse was needed.

[Primary behavior reference](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intro-lifecycle-rules.html). Competitor README blob hashes, exact star query URLs and source observations are retained in the dated profile research receipt. A local success proves our example, not absence of the behavior in a competitor. Negative results and unsupported configurations remain visible; no superiority claim is made.
