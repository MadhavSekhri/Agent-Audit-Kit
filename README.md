# Agent Audit Kit

Run deterministic, offline regression checks on **recorded** AI-agent responses and tool calls.

**Status:** early prototype. Not a security scanner, agent sandbox, comprehensive prompt-injection detector, or proof of any AI-credit eligibility.

## Install

    python -m pip install -e .

## Try it

    agent-audit examples/cases.json --json

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

## Test

    python -m unittest discover -s tests -v

## Contribute

See CONTRIBUTING.md and SECURITY.md for reporting guidelines. Contributions should include reproducible tests.

## License

MIT; see LICENSE.
