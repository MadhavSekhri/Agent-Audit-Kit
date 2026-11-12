"""Offline agent-audit CLI."""
import argparse
import json
from pathlib import Path
from .evaluate import evaluate_suite


def main(argv=None):
    parser = argparse.ArgumentParser(prog="agent-audit", description="Offline agent-output regression checks")
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--json", action="store_true", help="Machine-readable report")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.fixture.read_text(encoding="utf-8"))
        report = evaluate_suite(payload)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{report['passed_count']}/{report['total']} checks passed")
        for case in report["cases"]:
            print(f"{'PASS' if case['passed'] else 'FAIL'} {case['id']}: {', '.join(case['findings']) or 'no findings'}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
