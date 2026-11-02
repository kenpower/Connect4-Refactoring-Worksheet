#!/usr/bin/env python3
"""classroom50 autograder for the Connect Four refactoring lab.

Builds the project with CMake, runs every GoogleTest test, and writes:
  result.json      - the classroom50/result/v1 score (1 point per passing test,
                     plus 1 point for building)
  release-body.md  - a human-readable summary for the submission Release

Run from the root of the student's checkout. It always exits 0 once it has
written result.json; a failed build or crash is reported as failing tests.
"""

import json
import os
import subprocess
from pathlib import Path

BUILD_DIR = Path("build-autograde")
TEST_BINARY = BUILD_DIR / "connect4_tests"
GTEST_JSON = BUILD_DIR / "gtest-results.json"
BUILD_POINTS = 1
POINTS_PER_TEST = 1
MAX_DETAIL_LINES = 6


def run(command, timeout):
    """Run a command, returning (succeeded, combined output)."""
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return False, f"Timed out after {timeout} seconds: {' '.join(command)}"
    return completed.returncode == 0, completed.stdout + completed.stderr


def tail(text, lines=MAX_DETAIL_LINES):
    return "\n".join(text.strip().splitlines()[-lines:])


def compiler_errors(text, lines=20):
    """The compiler's error lines, or the end of the output if none are found."""
    errors = [line for line in text.splitlines() if "error" in line.lower()]
    return "\n".join(errors[:lines]) if errors else tail(text, lines)


def build():
    ok, output = run(["cmake", "-S", ".", "-B", str(BUILD_DIR)], timeout=300)
    if ok:
        ok, output = run(["cmake", "--build", str(BUILD_DIR), "-j"], timeout=300)
    return ok, output


def run_tests():
    """Run the GoogleTest binary; return a list of test entries, or None if it crashed."""
    GTEST_JSON.unlink(missing_ok=True)
    _, output = run(
        [str(TEST_BINARY), f"--gtest_output=json:{GTEST_JSON}"], timeout=120
    )
    if not GTEST_JSON.exists():
        return None, output

    report = json.loads(GTEST_JSON.read_text())
    tests = []
    for suite in report.get("testsuites", []):
        for case in suite.get("testsuite", []):
            failures = case.get("failures", [])
            passed = not failures and case.get("result") == "COMPLETED"
            tests.append({
                "test-name": f"{suite['name']}.{case['name']}",
                "passed": passed,
                "score": POINTS_PER_TEST if passed else 0,
                "max-score": POINTS_PER_TEST,
                "details": tail("\n".join(f["failure"] for f in failures)),
            })
    return tests, output


def grade():
    built, build_output = build()
    tests = [{
        "test-name": "Project builds",
        "passed": built,
        "score": BUILD_POINTS if built else 0,
        "max-score": BUILD_POINTS,
        "details": "" if built else compiler_errors(build_output),
    }]
    if built:
        results, run_output = run_tests()
        if results is None:
            tests.append({
                "test-name": "Tests run to completion",
                "passed": False,
                "score": 0,
                "max-score": POINTS_PER_TEST,
                "details": "The test program crashed or timed out.\n" + tail(run_output, 20),
            })
        else:
            tests.extend(results)
    return tests


def write_result(tests):
    result = {
        "schema": "classroom50/result/v1",
        "classroom": os.environ.get("CLASSROOM", ""),
        "assignment": os.environ.get("ASSIGNMENT", ""),
        "submission": os.environ.get("SUBMISSION_TAG", ""),
        "commit": os.environ.get("COMMIT_URL", ""),
        "release": os.environ.get("RELEASE_URL", ""),
        "review": os.environ.get("REVIEW_URL", ""),
        "score": sum(t["score"] for t in tests),
        "max-score": sum(t["max-score"] for t in tests),
        "tests": [{k: v for k, v in t.items() if k != "details"} for t in tests],
    }
    Path("result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def write_release_body(result, tests):
    passed = sum(t["passed"] for t in tests)
    lines = [
        f"## Score: {result['score']} / {result['max-score']}",
        "",
        f"{passed} of {len(tests)} checks passed.",
        "",
        "| Check | Result | Points |",
        "|-|-|-|",
    ]
    for t in tests:
        mark = "✅ PASS" if t["passed"] else "❌ FAIL"
        lines.append(f"| `{t['test-name']}` | {mark} | {t['score']}/{t['max-score']} |")

    failed = [t for t in tests if not t["passed"] and t["details"]]
    if failed:
        lines += ["", "### Failures", ""]
        for t in failed:
            lines += [f"**{t['test-name']}**", "", "```", t["details"], "```", ""]

    Path("release-body.md").write_text("\n".join(lines) + "\n")


def main():
    tests = grade()
    result = write_result(tests)
    write_release_body(result, tests)
    print(f"Score: {result['score']} / {result['max-score']}")


if __name__ == "__main__":
    main()
