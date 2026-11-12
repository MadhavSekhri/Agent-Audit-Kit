# Ecosystem review and positioning

Review date: 2026-11-12.

## Existing alternatives
- DeepEval agent evaluation: https://deepeval.com/docs/getting-started-agents — agent traces, tool-using agents, component and end-to-end testing in CI.
- promptfoo agent evaluation: https://github.com/promptfoo/promptfoo/blob/main/site/docs/guides/evaluate-coding-agents.md — structured assertions, trace checks, cost/latency limits and agent tests.

## Product decision
Do **not** try to outperform entire evaluation suites or claim AI safety certification. Agent Audit Kit should be a tiny, dependency-light **offline contract engine for deterministic recorded events**. It answers objective questions such as 'Did a forbidden tool appear?', 'Was the exact call order preserved?' and 'Did this known synthetic secret marker appear?', without an LLM judge or credentials.

## Reviewable demo
Use synthetic failing and passing JSON fixtures, with exact stable finding codes in GitHub Actions and deterministic exit statuses. Verify reporting never includes response text or secrets. Explain that recording a forbidden call does not prevent it in a live agent.

## Interoperability direction
Offer adapters for selected exported trace schemas only after schemas are versioned. A future test could import metadata from OTel Agent Observer without keeping raw prompts. JUnit/SARIF outputs should be designed around existing CI tools instead of building a reporting dashboard.

## Adoption evidence
An external codebase integrating the Action, bug reports about real-world trace formats, and meaningful external tests or adapters. Do not open superficial automated PRs for metrics.
