"""Offline CLI for agent contract fixtures; never executes tools or models."""
import argparse
import json
from pathlib import Path
from .evaluate import MAX_SUITE_BYTES, evaluate_suite
from .junit import render_junit


def main(argv=None):
    parser = argparse.ArgumentParser(prog="agent-audit", description="Offline agent contract checks")
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--json", action="store_true", help="Machine-readable report")
    parser.add_argument("--format", choices=("text", "json", "junit"), default="text",
                        help="Console, JSON, or JUnit XML report")
    args = parser.parse_args(argv)
    try:
        if args.fixture.is_symlink():
            raise ValueError("fixture must not be a symbolic link")
        with args.fixture.open("rb") as stream:
            raw = stream.read(MAX_SUITE_BYTES + 1)
        if len(raw) > MAX_SUITE_BYTES:
            raise ValueError("fixture exceeds 1 MiB limit")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
            raise ValueError("fixture must be valid UTF-8 JSON within parser nesting limits") from exc
        report = evaluate_suite(payload)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"invalid fixture: {exc}\n")
    output_format = "json" if args.json else args.format
    if output_format == "json":
        print(json.dumps(report, indent=2))
    elif output_format == "junit":
        print(render_junit(report), end="")
    else:
        print(f"{report['passed_count']}/{report['total']} checks passed")
        for case in report["cases"]:
            print(f"{'PASS' if case['passed'] else 'FAIL'} {case['id']}: {', '.join(case['findings']) or 'no findings'}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
