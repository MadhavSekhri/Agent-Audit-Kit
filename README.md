# Agent Audit Kit

Run deterministic, offline regression checks on **recorded** AI-agent responses and tool calls.

**Status:** early prototype. Not a security scanner, agent sandbox, comprehensive prompt-injection detector, or proof of any AI-credit eligibility.

## Install

    python -m pip install -e .

## Try it

    agent-audit examples/cases.json --json
    agent-audit examples/cases.json --format junit > results.xml

Fixture format:

    {"cases":[{"id":"sample","response":"Hello world","expected_contains":["Hello"],"forbidden_contains":["sensitive"],"tool_calls":[{"name":"search"}],"allowed_tools":["search"]}]}

## Tool-call assertions

Cases can additionally include:

- `allowed_tools` — approved tool names (empty list disallows all)
- `forbidden_tools` — disallowed tool names
- `expected_tool_sequence` — exact ordered list of tool names
- `max_tool_calls` — maximum number of calls (including zero)

All assertions are deterministic. A tool-call record with no name is rejected even if no allowlist is configured. Reports contain finding codes, not suspected secret values.

Example:

```json
{
  "cases": [
    {
      "id": "safe-search",
      "response": "Finished",
      "allowed_tools": [
        "search"
      ],
      "expected_tool_sequence": [
        "search"
      ],
      "max_tool_calls": 1,
      "tool_calls": [
        {
          "name": "search"
        }
      ]
    }
  ]
}
```

The toolkit does not call model providers or run agent tools. Its secret patterns and content checks are only development heuristics, not a safety guarantee.

## Use as a GitHub Action

This repository now provides a reusable composite GitHub Action. In a downstream repository with a JSON fixture, add:

```yaml
name: Agent regression
on: [push, pull_request]
permissions:
  contents: read
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - uses: MadhavSekhri/Agent-Audit-Kit@main
        with:
          fixture: examples/cases.json
```

The job exits unsuccessfully when fixture assertions fail. For production usage, pin the Action to a reviewed commit SHA or versioned release rather than the moving `main` branch. It operates on fixture files in the calling repository and requires no model API key.

For a downstream workflow that preserves JUnit reports when assertions fail, see the [CI pilot](docs/JUNIT_CI_PILOT.md).

## Test

    python -m unittest discover -s tests -v

## Contribute

See CONTRIBUTING.md and SECURITY.md for reporting guidelines. Contributions should include reproducible tests.

## License

MIT; see LICENSE.

## Architecture and security

This is an actively developed prototype, not a certification or completed production service. Review the [product design and acceptance gates](docs/PRODUCT_PLAN.md), [threat model](docs/THREAT_MODEL.md), and [implementation contract](docs/FIXTURE_CONTRACT.md) before depending on it. Changes are proposed through draft pull requests with automated tests and security-focused code review.
