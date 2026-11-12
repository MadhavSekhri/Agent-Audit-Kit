# Fixture contracts and failure codes

The CLI accepts a UTF-8 JSON object with optional `schema_version: 1` and required `cases` array. Each case has a safe identifier, response string, and optional assertion lists or tool calls. Unknown fields are rejected so misspellings cannot silently pass.

## Resource budgets
- Fixture on disk: at most 1 MiB, no symlinks
- Cases: 1–128; tool calls per case: at most 128
- Case and tool IDs: 1–80 safe ASCII characters (`A-Z a-z 0-9 _ . : -`)
- Response: at most 131,072 characters
- Each assertion list: at most 64 entries; each entry: nonempty, at most 1,024 characters
- max_tool_calls: integer between 0 and 128

## Exit status
- `0`: all contract assertions passed
- `1`: at least one assertion failed
- `2`: fixture unreadable, malformed, unknown schema fields or invalid types/budgets

Outputs contain bounded IDs and generic finding codes; they intentionally never include the raw prompt/response/tool arguments or known-secret markers. An allowlist here only checks recorded events; it does *not* prevent a live agent from calling a tool. Large or highly nested JSON can be rejected instead of processed.

## Quickstart
```sh
python -m pip install -e .
agent-audit examples/cases.json --json
python -m unittest discover -s tests -v
```
