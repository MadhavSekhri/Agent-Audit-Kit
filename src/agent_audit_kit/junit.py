"""JUnit-compatible XML reporting without model output, arguments, or secrets."""
from xml.etree import ElementTree


def render_junit(report: dict) -> str:
    """Convert a validated evaluate_suite result into a JUnit XML test suite."""
    cases = report.get("cases")
    total = report.get("total")
    passed = report.get("passed_count")
    if not isinstance(cases, list) or not isinstance(total, int) or not isinstance(passed, int):
        raise ValueError("expected a validated suite report")
    if len(cases) != total or not 0 <= passed <= total:
        raise ValueError("invalid suite counters")
    root = ElementTree.Element("testsuite", {
        "name": "agent-audit-kit",
        "tests": str(total),
        "failures": str(total - passed),
        "errors": "0",
        "time": "0",
    })
    for item in cases:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not isinstance(item.get("findings"), list):
            raise ValueError("invalid report entry")
        case = ElementTree.SubElement(root, "testcase", {
            "classname": "agent_audit_kit.contract",
            "name": item["id"],
            "time": "0",
        })
        for finding in item["findings"]:
            if not isinstance(finding, str):
                raise ValueError("invalid finding code")
            failure = ElementTree.SubElement(case, "failure", {
                "type": "contract_regression",
                "message": finding,
            })
            failure.text = finding
    return ElementTree.tostring(root, encoding="unicode") + "\n"
