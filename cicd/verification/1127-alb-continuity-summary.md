# DAY 2 ALB continuity verification (2026-11-27 KST)

Source: user-provided terminal screenshot FINAL RESULT and Release #5 console log. This is a transcription of observed aggregate results, not the raw CSV.

- Sampling: approximately 180 seconds, sequential curl requests with 0.5-second sleep and 3-second timeout; HTTP 200 plus test-v2 or test-v4 required for PASS.
- Local CSV: `/opt/devops/alb-continuity-20261127-120519.csv` (raw file not yet collected).
- Last visible response: 12:08:18.668,200,test-v2,PASS.

| Metric | Observed result |
| --- | ---: |
| Total | 341 |
| PASS | 341 |
| FAIL | 0 |
| Blue test-v2 | 301 |
| Green test-v4 | 40 |
| Success rate | 100.00% |

[Release #5](1127-notice-release-build-5-rollback.log) ran 12:05:57–12:07:01, switch verification 20.23s and rollback verification 21.56s. Earlier visible continuity screenshot shows test-v2 at 12:06:31.572 and test-v4 at 12:06:32.105, both HTTP 200 PASS. Final screenshot shows return to test-v2. [Release #4](1127-notice-release-build-4-rollback.log) independently measured switch 22.98s and rollback 21.64s.

Conclusion: zero failed sampled HTTP requests during this static fixture switch and synthetic assertion-triggered rollback test. Not proof of absolute zero downtime, production RTO, real Pod failure recovery, sustained load handling, or actual notice app data integrity. CI/CD/release automatic chaining and production database/storage integration remain pending. Raw CSV should be archived separately before formal review.
