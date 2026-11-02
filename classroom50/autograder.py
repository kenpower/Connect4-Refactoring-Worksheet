#!/usr/bin/env python3
"""classroom50 autograder for the Connect Four refactoring lab.

Builds the project with CMake, runs every GoogleTest test, and writes:
  result.json      - the classroom50/result/v1 score
  release-body.md  - a human-readable summary for the submission Release

The score has two parts:
  Final code  - 1 point for building, plus 1 point per passing test.
  Process     - the lab is about small green steps, so every commit the pair made
                is built and tested too: points for the share of commits that were
                green, and for making enough commits.

The pair's commits are the ones after classroom50's accept commit (the one that
added .classroom50.yaml). Set GRADE_SINCE to a commit to override that; with
neither, the process part is skipped.

Run from the root of the student's checkout. It always exits 0 once it has
written result.json; a failed build or crash is reported as failing tests.
"""

import json
import os
import subprocess
from pathlib import Path

BUILD_DIR = Path("build-autograde")
HISTORY_SOURCE = BUILD_DIR / "history-src"
HISTORY_BUILD = BUILD_DIR / "history-build"
ACCEPT_MARKER = ".classroom50.yaml"
BUILD_POINTS = 1
POINTS_PER_TEST = 1
GREEN_COMMITS_POINTS = 10   # scaled by the share of commits that were green
SMALL_STEPS_POINTS = 5      # scaled by commits made, up to SMALL_STEPS_TARGET
SMALL_STEPS_TARGET = 10
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


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()


def tail(text, lines=MAX_DETAIL_LINES):
    return "\n".join(text.strip().splitlines()[-lines:])


def compiler_errors(text, lines=20):
    """The compiler's error lines, or the end of the output if none are found."""
    errors = [line for line in text.splitlines() if "error" in line.lower()]
    return "\n".join(errors[:lines]) if errors else tail(text, lines)


def build(source, build_dir):
    ok, output = run(["cmake", "-S", str(source), "-B", str(build_dir)], timeout=300)
    if ok:
        ok, output = run(["cmake", "--build", str(build_dir), "-j"], timeout=300)
    return ok, output


def run_tests(build_dir):
    """Run the GoogleTest binary; return (test entries, output), or (None, output) if it crashed."""
    report_path = build_dir / "gtest-results.json"
    report_path.unlink(missing_ok=True)
    _, output = run(
        [str(build_dir / "connect4_tests"), f"--gtest_output=json:{report_path}"], timeout=120
    )
    if not report_path.exists():
        return None, output

    report = json.loads(report_path.read_text())
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


def grade_final_code():
    built, build_output = build(".", BUILD_DIR)
    tests = [{
        "test-name": "Project builds",
        "passed": built,
        "score": BUILD_POINTS if built else 0,
        "max-score": BUILD_POINTS,
        "details": "" if built else compiler_errors(build_output),
    }]
    if built:
        results, run_output = run_tests(BUILD_DIR)
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


def pair_commits():
    """The pair's commits, oldest first, as (sha, subject); None if the start can't be found."""
    if git("rev-parse", "--is-shallow-repository") == "true":
        run(["git", "fetch", "--unshallow", "--quiet"], timeout=120)
    since = os.environ.get("GRADE_SINCE") or git(
        "log", "--diff-filter=A", "--format=%H", "-1", "--", ACCEPT_MARKER
    )
    if not since:
        return None
    lines = git("log", "--reverse", "--no-merges", "--format=%H %s", f"{since}..HEAD")
    return [tuple(line.split(" ", 1)) for line in lines.splitlines() if line]


def commit_status(sha):
    """'green', 'red' or 'broken' (doesn't build) for one commit."""
    run(["git", "-C", str(HISTORY_SOURCE), "checkout", "--quiet", "--force", "--detach", sha], timeout=60)
    built, _ = build(HISTORY_SOURCE, HISTORY_BUILD)
    if not built:
        return "broken"
    results, _ = run_tests(HISTORY_BUILD)
    if results is None or not all(t["passed"] for t in results):
        return "red"
    return "green"


def grade_history():
    """Build and test every commit the pair made: (tests, per-commit report)."""
    commits = pair_commits()
    if commits is None:
        return [], None
    if commits:
        if not HISTORY_SOURCE.exists():
            run(["git", "worktree", "add", "--quiet", "--detach", str(HISTORY_SOURCE), "HEAD"], timeout=60)
        report = [(sha, subject, commit_status(sha)) for sha, subject in commits]
        run(["git", "worktree", "remove", "--force", str(HISTORY_SOURCE)], timeout=60)
    else:
        report = []

    green = sum(status == "green" for _, _, status in report)
    total = len(report)
    green_score = GREEN_COMMITS_POINTS * green // total if total else 0
    steps_score = SMALL_STEPS_POINTS * min(total, SMALL_STEPS_TARGET) // SMALL_STEPS_TARGET
    not_green = [f"{sha[:7]} {status:6} {subject}" for sha, subject, status in report if status != "green"]
    tests = [
        {
            "test-name": f"Every commit green ({green} of {total})",
            "passed": total > 0 and green == total,
            "score": green_score,
            "max-score": GREEN_COMMITS_POINTS,
            "details": "\n".join(not_green) if not_green else ("No commits yet." if not total else ""),
        },
        {
            "test-name": f"Small steps ({total} commits, aiming for {SMALL_STEPS_TARGET}+)",
            "passed": total >= SMALL_STEPS_TARGET,
            "score": steps_score,
            "max-score": SMALL_STEPS_POINTS,
            "details": "" if total >= SMALL_STEPS_TARGET else "Commit after every green step.",
        },
    ]
    return tests, report


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


def checks_table(tests):
    lines = ["| Check | Result | Points |", "|-|-|-|"]
    for t in tests:
        mark = "✅ PASS" if t["passed"] else "❌ FAIL"
        lines.append(f"| `{t['test-name']}` | {mark} | {t['score']}/{t['max-score']} |")
    return lines


def write_release_body(result, final_tests, history_tests, history):
    lines = [f"## Score: {result['score']} / {result['max-score']}", ""]

    lines += ["### Final code", ""] + checks_table(final_tests)

    lines += ["", "### Process: small green steps", ""]
    if history is None:
        lines.append("Not graded: couldn't find where your commits start.")
    else:
        lines += checks_table(history_tests)
        if history:
            lines += ["", "| Commit | Status |", "|-|-|"]
            icons = {"green": "🟢 green", "red": "🔴 red", "broken": "⛔ doesn't build"}
            lines += [f"| `{sha[:7]}` {subject} | {icons[status]} |" for sha, subject, status in history]

    failed = [t for t in final_tests if not t["passed"] and t["details"]]
    if failed:
        lines += ["", "### Failures", ""]
        for t in failed:
            lines += [f"**{t['test-name']}**", "", "```", t["details"], "```", ""]

    Path("release-body.md").write_text("\n".join(lines) + "\n")


def main():
    final_tests = grade_final_code()
    history_tests, history = grade_history()
    tests = final_tests + history_tests
    result = write_result(tests)
    write_release_body(result, final_tests, history_tests, history)
    print(f"Score: {result['score']} / {result['max-score']}")


if __name__ == "__main__":
    main()
