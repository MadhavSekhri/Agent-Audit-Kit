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

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_suite({"cases": [{"id": "a", "response": "x"},
                                      {"id": "a", "response": "y"}]})


if __name__ == "__main__":
    unittest.main()
