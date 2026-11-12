# Agent Audit Kit — Threat Model

Assets: CI runner availability, confidential test fixtures, developer secrets and trustworthy pass/fail status.
Untrusted boundary: JSON fixture from a PR or local file -> parser -> rule engine -> log / report.

| Threat | Failure | Control |
|---|---|---|
| Oversized fixtures | CPU, disk or memory exhaustion | finite byte, case and text budgets |
| Unexpected nested structures | recursion, crashes, unbounded loops | strict shape/type validation, limited nesting |
| Secret leakage | response or tool args printed to CI | only bounded case IDs and generic finding codes |
| Log injection | terminal control sequences in attacker IDs | conservative identifier grammar and length |
| Misleading safety claims | users assume runtime sandbox or DLP | explicit offline regression-only scope |
| Mutable dependencies | Action behavior changes unexpectedly | SHA pinning in consumers and tagged release practices |
| Insecure fixture execution | malicious commands in data executed | no exec/eval/plugins or network in the core |
| Third-party data | unconsented prompts stored in repo | synthetic fixtures, redact before recording, privacy docs |

Exit criteria: typed validated fixture, deterministic bounded work, no model/provider API calls, safe exit codes and tests for every known malformed input family.
