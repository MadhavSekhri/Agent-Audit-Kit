import unittest
from agent_audit_kit.evaluate import evaluate_case, evaluate_suite


class EvaluatorTests(unittest.TestCase):
    def test_expected_and_forbidden(self):
        case = {"id": "a", "response": "Hello world", "expected_contains": ["HELLO"],
                "forbidden_contains": ["world"]}
        r = evaluate_case(case)
        self.assertFalse(r.passed)
        self.assertIn("forbidden_text_present", r.findings)

    def test_allowed_tools(self):
        r = evaluate_case({"id": "a", "response": "ok", "tool_calls": [{"name": "shell"}],
                           "allowed_tools": ["search"]})
        self.assertEqual(r.findings, ["unapproved_tool_call"])

    def test_known_secret_is_not_echoed(self):
        r = evaluate_case({"id": "x", "response": "password=DO_NOT_SHARE_THIS",
                           "secret_markers": ["DO_NOT_SHARE_THIS"]})
        self.assertEqual(r.findings, ["known_secret_marker_in_response"])

    def test_safe_suite(self):
        report = evaluate_suite({"cases": [{"id": "a", "response": "ok"},
                                           {"id": "b", "response": "ready"}]})
        self.assertEqual(report["passed_count"], 2)
        self.assertTrue(report["passed"])

    def test_sequence_mismatch_and_max_calls(self):
        result = evaluate_case({
            "id": "workflow", "response": "done",
            "tool_calls": [{"name": "read"}, {"name": "write"}],
            "allowed_tools": ["read", "write"],
            "expected_tool_sequence": ["write", "read"],
            "max_tool_calls": 1,
        })
        self.assertFalse(result.passed)
        self.assertEqual(
            result.findings, ["tool_sequence_mismatch", "too_many_tool_calls"]
        )

    def test_forbidden_tools_even_without_allowed_tools(self):
        result = evaluate_case({
            "id": "unsafe", "response": "ok",
            "tool_calls": [{"name": "delete_repo"}],
            "forbidden_tools": ["delete_repo"],
        })
        self.assertEqual(result.findings, ["forbidden_tool_called"])

    def test_invalid_tool_calls_rejected_without_allowlist(self):
        with self.assertRaises(ValueError):
            evaluate_case({"id": "invalid", "response": "ok",
                           "tool_calls": [{"wrong_key": "read"}]})

    def test_invalid_text_assertion_type_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_case({"id": "invalid", "response": "ok",
                           "expected_contains": "ok"})

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_suite({"cases": [{"id": "a", "response": "x"},
                                      {"id": "a", "response": "y"}]})


if __name__ == "__main__":
    unittest.main()
