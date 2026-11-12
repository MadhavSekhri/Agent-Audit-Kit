import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path

from agent_audit_kit.cli import main
from agent_audit_kit.evaluate import (
    MAX_CASES, MAX_SUITE_BYTES, evaluate_case, evaluate_suite,
)


class EvaluatorTests(unittest.TestCase):
    def test_expected_and_forbidden(self):
        result = evaluate_case({"id": "a", "response": "Hello world",
                                "expected_contains": ["HELLO"],
                                "forbidden_contains": ["world"]})
        self.assertEqual(result.findings, ["forbidden_text_present"])

    def test_allowed_tools_and_sequence(self):
        result = evaluate_case({
            "id": "workflow", "response": "ok",
            "tool_calls": [{"name": "read"}, {"name": "write"}],
            "allowed_tools": ["read"], "expected_tool_sequence": ["write", "read"],
            "max_tool_calls": 1,
        })
        self.assertEqual(result.findings, ["too_many_tool_calls",
                                          "tool_sequence_mismatch", "unapproved_tool_call"])

    def test_known_secret_not_printed(self):
        result = evaluate_case({"id": "x", "response": "password=DO_NOT_SHARE_THIS",
                                "secret_markers": ["DO_NOT_SHARE_THIS"]})
        self.assertEqual(result.findings, ["known_secret_marker_in_response"])
        self.assertNotIn("DO_NOT_SHARE_THIS", repr(result))

    def test_forbidden_tool(self):
        result = evaluate_case({"id": "unsafe", "response": "ok",
                                "tool_calls": [{"name": "delete_repo"}],
                                "forbidden_tools": ["delete_repo"]})
        self.assertEqual(result.findings, ["forbidden_tool_called"])

    def test_safe_suite(self):
        result = evaluate_suite({"schema_version": 1, "cases": [
            {"id": "one", "response": "ok"}, {"id": "two", "response": "ready"}]})
        self.assertTrue(result["passed"])
        self.assertEqual(result["passed_count"], 2)

    def test_duplicate_case_ids(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            evaluate_suite({"cases": [{"id": "a", "response": "x"},
                                      {"id": "a", "response": "y"}]})

    def test_reject_control_characters_in_ids(self):
        with self.assertRaisesRegex(ValueError, "safe identifier"):
            evaluate_case({"id": "bad\ninjected", "response": "ok"})

    def test_reject_bad_types_and_unknown_fields(self):
        for bad in (
            {"id": "a", "response": "ok", "expected_contains": "ok"},
            {"id": "a", "response": "ok", "tool_calls": [None]},
            {"id": "a", "response": "ok", "max_tool_calls": True},
            {"id": "a", "response": "ok", "extra": "not supported"},
            {"id": "a", "response": 42},
        ):
            with self.subTest(case=bad):
                with self.assertRaises(ValueError):
                    evaluate_case(bad)

    def test_reject_oversized_fields(self):
        with self.assertRaises(ValueError):
            evaluate_case({"id": "x" * 81, "response": "ok"})
        with self.assertRaises(ValueError):
            evaluate_case({"id": "x", "response": "r" * 131073})
        with self.assertRaises(ValueError):
            evaluate_case({"id": "x", "response": "r",
                           "tool_calls": [{"name": "a"}] * 129})
        with self.assertRaises(ValueError):
            evaluate_suite({"cases": [{"id": str(i), "response": ""} for i in range(MAX_CASES + 1)]})

    def test_reject_schema_version_and_root_fields(self):
        with self.assertRaises(ValueError):
            evaluate_suite({"schema_version": 2, "cases": [{"id": "a", "response": "x"}]})
        with self.assertRaises(ValueError):
            evaluate_suite({"cases": [{"id": "a", "response": "x"}], "unknown": True})

    def test_cli_bounded_file_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.json"
            path.write_text(json.dumps({"cases": [{"id": "ok", "response": "safe"}]}),
                            encoding="utf-8")
            with redirect_stdout(StringIO()):
                self.assertEqual(main([str(path)]), 0)
            path.write_text(json.dumps({"cases": [{"id": "bad", "response": "leaked",
                                                   "forbidden_contains": ["leaked"]}]}),
                            encoding="utf-8")
            with redirect_stdout(StringIO()):
                self.assertEqual(main([str(path)]), 1)
            path.write_bytes(b" " * (MAX_SUITE_BYTES + 1))
            with redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    main([str(path)])
            self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
