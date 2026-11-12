# Agent Audit Kit

Run deterministic, offline regression checks on **recorded** AI-agent responses and tool calls.

**Status:** early prototype. Not a security scanner, agent sandbox, comprehensive prompt-injection detector, or proof of any AI-credit eligibility.

## Install

    python -m pip install -e .

## Try it

    agent-audit examples/cases.json --json

Fixture format:

    {"cases":[{"id":"sample","response":"Hello world","expected_contains":["Hello"],"forbidden_contains":["sensitive"],"tool_calls":[{"name":"search"}],"allowed_tools":["search"]}]}

The toolkit does not call model providers or run agent tools. Its secret patterns and content checks are only development heuristics, not a safety guarantee.

## Test

    python -m unittest discover -s tests -v

## Contribute

See CONTRIBUTING.md and SECURITY.md for reporting guidelines. Contributions should include reproducible tests.

## License

MIT; see LICENSE.
