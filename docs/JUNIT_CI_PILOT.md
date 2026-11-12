# Run agent regression checks in downstream CI

Use this workflow in a repository that already records agent responses or tool calls. It runs offline assertions on those records and makes the JUnit report available from the workflow run. The evaluation itself needs no API key.

1. Start with a synthetic fixture at `tests/agent-cases.json`. Keep prompts, responses, credentials, and case IDs containing personal data out of committed fixtures.
2. Copy the workflow below to `.github/workflows/agent-regression.yml`.
3. Run it on a PR. In a separate test commit, change an expected value so it cannot match. Confirm the job fails and the artifact contains the failed case. Restore the passing fixture.

```json
{
  "cases": [
    {
      "id": "refund-request-uses-read-only-lookup",
      "response": "I found the order.",
      "expected_contains": ["found the order"],
      "allowed_tools": ["lookup_order"],
      "expected_tool_sequence": ["lookup_order"],
      "max_tool_calls": 1,
      "tool_calls": [{"name": "lookup_order"}]
    }
  ]
}
```

```yaml
name: Agent regression
on: [push, pull_request]
permissions:
  contents: read
jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          persist-credentials: false
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5.6.0
        with:
          python-version: '3.12'
      - name: Install reviewed revision
        run: python -m pip install 'Agent-Audit-Kit @ git+https://github.com/MadhavSekhri/Agent-Audit-Kit@f28c37f4e953edc03d268a314e611dddb78aad18'
      - name: Generate report
        shell: bash
        run: |
          status=0
          agent-audit tests/agent-cases.json --format junit > agent-results.xml.tmp || status=$?
          if [[ "$status" == 0 || "$status" == 1 ]] && [[ -s agent-results.xml.tmp ]]; then
            mv agent-results.xml.tmp agent-results.xml
          fi
          exit "$status"
      - name: Upload report
        if: ${{ !cancelled() && hashFiles('agent-results.xml') != '' }}
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2
        with:
          name: agent-results.xml
          path: agent-results.xml
          retention-days: 7
          if-no-files-found: error
```

Exit code 1 means an assertion failed and a report is still uploaded. Exit code 2 means the fixture could not be evaluated. Start with one recurring regression from your own workflow before expanding coverage.
