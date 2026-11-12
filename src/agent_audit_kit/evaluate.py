"""Deterministic, offline checks for recorded agent responses and tool calls.

This module is for development-time regression tests, not runtime security.
"""
import re
from dataclasses import dataclass, asdict
from typing import Any

SECRET_PATTERNS = (
    ("possible_openai_token", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")),
    ("possible_aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("possible_private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
)


@dataclass
class CaseResult:
    id: str
    passed: bool
    findings: list[str]


def _strings(case: dict[str, Any], key: str, identifier: str) -> list[str]:
    items = case.get(key, [])
    if not isinstance(items, list) or not all(isinstance(x, str) and x for x in items):
        raise ValueError(f"{identifier}: {key} must be a list of nonempty strings")
    return items


def _tool_names(case: dict[str, Any], identifier: str) -> list[str]:
    calls = case.get("tool_calls", [])
    if not isinstance(calls, list):
        raise ValueError(f"{identifier}: tool_calls must be a list")
    names = []
    for call in calls:
        if not isinstance(call, dict) or not isinstance(call.get("name"), str) or not call["name"]:
            raise ValueError(f"{identifier}: every tool call needs a nonempty string name")
        names.append(call["name"])
    return names


def evaluate_case(case: dict[str, Any]) -> CaseResult:
    """Evaluate a single synthetic or recorded case using explicit assertions."""
    if not isinstance(case, dict):
        raise ValueError("case must be an object")
    identifier = case.get("id")
    response = case.get("response")
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("each case requires a nonempty string id")
    if not isinstance(response, str):
        raise ValueError(f"{identifier}: response must be a string")

    findings: list[str] = []
    folded = response.casefold()
    for text in _strings(case, "expected_contains", identifier):
        if text.casefold() not in folded:
            findings.append("missing_expected_text")
    for text in _strings(case, "forbidden_contains", identifier):
        if text.casefold() in folded:
            findings.append("forbidden_text_present")

    for label, pattern in SECRET_PATTERNS:
        if pattern.search(response):
            findings.append(label)
    for marker in _strings(case, "secret_markers", identifier):
        if marker in response:
            findings.append("known_secret_marker_in_response")

    names = _tool_names(case, identifier)
    if "allowed_tools" in case:
        allowed = _strings(case, "allowed_tools", identifier)
        if any(name not in allowed for name in names):
            findings.append("unapproved_tool_call")
    if "forbidden_tools" in case:
        forbidden = _strings(case, "forbidden_tools", identifier)
        if any(name in forbidden for name in names):
            findings.append("forbidden_tool_called")
    if "expected_tool_sequence" in case:
        expected = _strings(case, "expected_tool_sequence", identifier)
        if names != expected:
            findings.append("tool_sequence_mismatch")
    if "max_tool_calls" in case:
        count = case["max_tool_calls"]
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError(f"{identifier}: max_tool_calls must be a nonnegative integer")
        if len(names) > count:
            findings.append("too_many_tool_calls")

    return CaseResult(identifier, not findings, sorted(set(findings)))


def evaluate_suite(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("suite must be a JSON object")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("suite must contain a nonempty cases array")
    results = [evaluate_case(case) for case in cases]
    ids = [case.id for case in results]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate case ids")
    return {
        "passed": all(result.passed for result in results),
        "total": len(results),
        "passed_count": sum(result.passed for result in results),
        "cases": [asdict(result) for result in results],
    }
