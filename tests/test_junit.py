"""JUnit XML reports must contain finding IDs, never response contents."""
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

from agent_audit_kit.cli import main
from agent_audit_kit.evaluate import evaluate_suite
from agent_audit_kit.junit import render_junit


class JUnitReportTests(unittest.TestCase):
    def test_serialize_failures_and_successes_without_raw_response(self):
        secret = "SyntheticPrivateMarker_DO_NOT_LOG"
        suite = evaluate_suite({"schema_version": 1, "cases": [
            {"id": "passing", "response": "hello"},
            {"id": "regression", "response": secret, "forbidden_contains": [secret]},
        ]})
        xml = render_junit(suite)
        root = ElementTree.fromstring(xml)
        self.assertEqual(root.tag, "testsuite")
        self.assertEqual(root.attrib["tests"], "2")
        self.assertEqual(root.attrib["failures"], "1")
        cases = root.findall("testcase")
        self.assertEqual(len(cases), 2)
        self.assertEqual(cases[0].attrib["name"], "passing")
        self.assertEqual(cases[1].find("failure").attrib["message"], "forbidden_text_present")
        self.assertNotIn(secret, xml)

    def test_cli_junit_exit_code_and_backward_json_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "suite.json"
            fixture.write_text(json.dumps({"cases": [
                {"id": "x", "response": "fail", "forbidden_contains": ["fail"]}
            ]}), encoding="utf-8")
            with redirect_stdout(StringIO()) as output:
                status = main([str(fixture), "--format", "junit"])
            self.assertEqual(status, 1)
            self.assertEqual(ElementTree.fromstring(output.getvalue()).attrib["failures"], "1")
            with redirect_stdout(StringIO()) as output:
                status = main([str(fixture), "--json"])
            self.assertEqual(status, 1)
            self.assertFalse(json.loads(output.getvalue())["passed"])

    def test_empty_schema_rejected(self):
        with self.assertRaises(ValueError):
            render_junit({"total": 1, "passed_count": 1})


if __name__ == "__main__":
    unittest.main()
