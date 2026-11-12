"""Bounded deterministic contract checks for recorded AI-agent output.

This is a developer regression checker, not a runtime security mechanism.
Reports never contain the recorded response, tool arguments or secret markers.
"""
from dataclasses import dataclass, asdict
import re
from typing import Any

MAX_SUITE_BYTES = 1_048_576
MAX_CASES = 128
MAX_RESPONSE_CHARS = 131_072
MAX_TOOL_CALLS = 128
MAX_ASSERTIONS = 64
MAX_ASSERTION_CHARS = 1024
MAX_IDENTIFIER_CHARS = 80

IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}$")
SECRET_PATTERNS = (
    ("possible_openai_token", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")),
    ("possible_aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("possible_private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
)
CASE_KEYS = frozenset({
    "id", "response", "expected_contains", "forbidden_contains",
    "secret_markers", "tool_calls", "allowed_tools", "forbidden_tools",
    "expected_tool_sequence", "max_tool_calls",
})
TEXT_FIELDS = (
    "expected_contains", "forbidden_contains", "secret_markers",
    "allowed_tools", "forbidden_tools", "expected_tool_sequence",
)


@dataclass
class CaseResult:
    id: str
    passed: bool
    findings: list[str]


def _strings(case: dict[str, Any], key: str, identifier: str) -> list[str]:
    items = case.get(key, [])
    if not isinstance(items, list) or len(items) > MAX_ASSERTIONS:
        raise ValueError(f"{identifier}: {key} must be a list of at most {MAX_ASSERTIONS} strings")
    if any(
        not isinstance(item, str)
        or not item
        or len(item) > MAX_ASSERTION_CHARS
        for item in items
    ):
        raise ValueError(f"{identifier}: {key} entries must be nonempty short strings")
    return items


def _tool_names(case: dict[str, Any], identifier: str) -> list[str]:
    calls = case.get("tool_calls", [])
    if not isinstance(calls, list) or len(calls) > MAX_TOOL_CALLS:
        raise ValueError(f"{identifier}: tool_calls must be a bounded list")
    names = []
    for call in calls:
        if not isinstance(call, dict) or not isinstance(call.get("name"), str):
            raise ValueError(f"{identifier}: each tool call needs a name")
        name = call["name"]
        if not IDENTIFIER.fullmatch(name):
            raise ValueError(f"{identifier}: tool names must be safe identifiers")
        names.append(name)
    return names


def evaluate_case(case: dict[str, Any]) -> CaseResult:
    if not isinstance(case, dict):
        raise ValueError("each case must be an object")
    identifier = case.get("id")
    if not isinstance(identifier, str) or not IDENTIFIER.fullmatch(identifier):
        raise ValueError("case id must contain 1-80 safe identifier characters")
    if set(case) - CASE_KEYS:
        raise ValueError(f"{identifier}: unknown fixture fields")
    response = case.get("response")
    if not isinstance(response, str) or len(response) > MAX_RESPONSE_CHARS:
        raise ValueError(f"{identifier}: response must be a bounded string")

    fields = {key: _strings(case, key, identifier) for key in TEXT_FIELDS}
    findings: list[str] = []
    folded = response.casefold()
    if any(term.casefold() not in folded for term in fields["expected_contains"]):
        findings.append("missing_expected_text")
    if any(term.casefold() in folded for term in fields["forbidden_contains"]):
        findings.append("forbidden_text_present")
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(response):
            findings.append(label)
    if any(term in response for term in fields["secret_markers"]):
        findings.append("known_secret_marker_in_response")

    names = _tool_names(case, identifier)
    if "allowed_tools" in case and any(
        name not in fields["allowed_tools"] for name in names
    ):
        findings.append("unapproved_tool_call")
    if any(name in fields["forbidden_tools"] for name in names):
        findings.append("forbidden_tool_called")
    if "expected_tool_sequence" in case and names != fields["expected_tool_sequence"]:
        findings.append("tool_sequence_mismatch")
    if "max_tool_calls" in case:
        count = case["max_tool_calls"]
        if isinstance(count, bool) or not isinstance(count, int) or not 0 <= count <= MAX_TOOL_CALLS:
            raise ValueError(f"{identifier}: max_tool_calls must be 0-{MAX_TOOL_CALLS}")
        if len(names) > count:
            findings.append("too_many_tool_calls")
    return CaseResult(identifier, not findings, sorted(set(findings)))


def evaluate_suite(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("suite must be a JSON object")
    if set(payload) - {"cases", "schema_version"}:
        raise ValueError("unknown suite fields")
    version = payload.get("schema_version", 1)
    if isinstance(version, bool) or version != 1:
        raise ValueError("unsupported fixture schema_version (expected 1)")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not 1 <= len(cases) <= MAX_CASES:
        raise ValueError(f"suite requires 1-{MAX_CASES} cases")
    results = [evaluate_case(case) for case in cases]
    ids = [case.id for case in results]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate case ids")
    return {
        "schema_version": 1,
        "passed": all(result.passed for result in results),
        "total": len(results),
        "passed_count": sum(result.passed for result in results),
        "cases": [asdict(result) for result in results],
    }
