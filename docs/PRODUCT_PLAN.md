# Agent Audit Kit — Product & Engineering RFC

## Mission
A provider-neutral **contract test runner for recorded AI agent workflows**, not a real-time safety firewall. Reviewer demo: a real GitHub Action fails a PR when the recorded tool sequence or response contract changes, shows a non-sensitive finding code, and passes after correction.

## Audience and competition
Primary users: backend engineers, AI platform engineers and maintainers shipping agents that call tools. General benchmarks judge model behavior probabilistically, while ordinary unit tests miss multi-step policy and tool call contracts. Differentiate through reproducible offline fixtures, zero model credentials and actionable stable CI diagnostics.

## Jobs to be done
1. Detect regression when a tool outside a documented allowlist is invoked.
2. Check forbidden-tool, exact ordered sequence, call budget and output substring contracts.
3. Verify that known *synthetic* secret markers were not emitted.
4. Run tests offline as a CLI, Python library or pinned GitHub Action; exit 0=all passed, 1=contract failures, 2=invalid input/config.
5. Fail fast on malformed or excessively large fixture files; never echo potentially sensitive response or tool arguments into CI logs.

## Architecture
Bounded file loader -> JSON validator/fixture schema version -> typed Case -> pure deterministic rules -> stable Finding IDs -> safe JSON/human and future JUnit/SARIF output. Keep adapters for OpenAI/LangChain/other frameworks outside the core; do not call a live model inside deterministic tests. Rule engine and reporting must remain independently testable.

## Explicit non-goals
Guaranteed detection of prompt injection, runtime enforcement of tool permissions, blanket DLP, evaluating open-ended semantics with deterministic truth, unrestricted execution of third-party fixtures, collecting end-user prompts.

## Priority architecture decisions
- Strict input budgets: fixture bytes, JSON nesting, number of cases, response characters, tool calls, identifier length, lists of assertions. Invalid types must produce explicit validation errors.
- Default reports contain only bounded case IDs and finding codes. Do not surface raw responses, tools arguments, suspected tokens or secrets.
- Stable schema semantics and versioning; future configurable rules must be sandbox-safe (declarative, no eval).
- Unit, negative, property-style boundary and CLI integration tests with real fixture samples.

## Roadmap
**P0 (initial PR):** safe bounded loader, strict validation across all assertion types, negative tests; document exit codes.
**P1:** published JSON schema v1, rule registry with safe extension model, JUnit/SARIF exports, samples for popular agent orchestration tools.
**P2:** opt-in record adapters, golden trace versioning and deterministic replay of metadata (never arbitrary tool execution).
**P3:** synthetic public benchmark suite with reproducible false-positive measurements, signed releases and action pinning guidance.

## Acceptance criteria
No network and no secrets required; no raw fixture content in normal diagnostics; Python 3.10/3.12 CI, integration test for the composite Action, documented schema/limits, stable codes; test an intentionally failing fixture and prove nonzero CI exit.

## Adoption and differentiation
A third-party maintainer should copy a 15-line workflow and run meaningful tests on a production-like redacted agent trace. Measure genuine external dependents/issues and useful contributions, not vanity PR counts or generated test spam.

## Integration
PolicyTrace revisions can provide cited golden fixtures; OTel Agent Observer events may be transformed into opt-in metadata-only fixtures; OSS Readiness checks contributor hygiene. Do not force any other project as a runtime dependency.

## Review questions
Versioned fixture schema design, safe escape hatch for fuzzy assertions, maximum resource budgets and how to avoid false safety claims. These decisions must be documented before accepting plugins.
