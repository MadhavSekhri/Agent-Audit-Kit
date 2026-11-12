# P1 — Versioned fixtures and CI report formats

The contract test runner is **offline and deterministic**, with no provider API calls.
Every suite supports `schema_version: 1` (omitted means 1). The published
[JSON Schema](../schemas/fixture-v1.schema.json) documents allowed keys, types,
limits, and identifier patterns. It is documentation for external validation;
the built-in validator remains authoritative for resource budgets and duplicate IDs.

## CI report formats

```shell
agent-audit examples/cases.json --format text
agent-audit examples/cases.json --format json
agent-audit examples/cases.json --format junit > agent-contract-results.xml
# The backward-compatible alias still works
agent-audit examples/cases.json --json
```

The JUnit XML uses one `testcase` per fixture case and one `failure` per finding.
It **does not** embed recorded agent output, tool arguments, synthetic secret
markers, or prompts. It emits only safe case identifiers and finding codes.
Use the test report in any JUnit-compatible CI reporter.

Exit codes: `0` means all assertions passed; `1` means at least one contract
failed; `2` means invalid or unreadable fixture. Redirecting JUnit output
to a file does not change the exit status.

## Remaining roadmap

- JUnit report consumers in external repositories with pinned GitHub Action SHAs
- Optional SARIF output with grounded rule IDs and known-safe artifact locations
- Explicit version migrations and adapters for synthetic/redacted recordings

The runner only tests recorded data; it cannot enforce live permissions.
