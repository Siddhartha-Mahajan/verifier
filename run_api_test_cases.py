#!/usr/bin/env python3
import argparse
import datetime as dt
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CommandResult:
    index: int
    total: int
    returncode: int
    command: str
    stdout: str
    stderr: str


def extract_curl_blocks(markdown_text: str) -> list[str]:
    pattern = re.compile(r"```bash\n(.*?)```", re.DOTALL)
    blocks = []
    for match in pattern.finditer(markdown_text):
        block = match.group(1).strip()
        if "curl" in block:
            blocks.append(block)
    return blocks


def run_command(command: str, cwd: Path) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        shell=True,
        cwd=str(cwd),
        executable="/bin/bash",
        capture_output=True,
        text=True,
    )
    return completed.returncode, completed.stdout, completed.stderr


def write_log_header(log_file: Path, markdown_file: Path, total_commands: int, base_url: str) -> None:
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = [
        "=" * 100,
        "API TEST CASE CURL RUNNER",
        "=" * 100,
        f"Timestamp (UTC): {timestamp}",
        f"Source file    : {markdown_file}",
        f"Base URL       : {base_url}",
        f"Total commands : {total_commands}",
        "",
    ]
    log_file.write_text("\n".join(header), encoding="utf-8")


def append_result(log_file: Path, result: CommandResult) -> None:
    body = [
        "-" * 100,
        f"Command {result.index}/{result.total}",
        "-" * 100,
        "COMMAND:",
        result.command,
        "",
        f"RETURN CODE: {result.returncode}",
        "",
        "STDOUT:",
        result.stdout.strip() if result.stdout else "<empty>",
        "",
        "STDERR:",
        result.stderr.strip() if result.stderr else "<empty>",
        "",
    ]
    with log_file.open("a", encoding="utf-8") as f:
        f.write("\n".join(body))


def append_summary(log_file: Path, total: int, passed: int, failed: int) -> None:
    summary = [
        "=" * 100,
        "SUMMARY",
        "=" * 100,
        f"Total commands: {total}",
        f"Succeeded     : {passed}",
        f"Failed        : {failed}",
        "",
    ]
    with log_file.open("a", encoding="utf-8") as f:
        f.write("\n".join(summary))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all curl requests from API_TEST_CASES.md and write outputs to a log file."
    )
    parser.add_argument(
        "--file",
        default="API_TEST_CASES.md",
        help="Path to the markdown file containing bash curl test cases.",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8080",
        help="Base URL to replace occurrences of http://localhost:8080 in extracted commands.",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Optional explicit log file path. If omitted, writes to tests/logs/api-curl-run-<timestamp>.log",
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop immediately when a command fails.",
    )
    args = parser.parse_args()

    workspace = Path(__file__).resolve().parent
    markdown_file = (workspace / args.file).resolve()
    if not markdown_file.exists():
        raise FileNotFoundError(f"Could not find markdown file: {markdown_file}")

    raw_text = markdown_file.read_text(encoding="utf-8")
    commands = extract_curl_blocks(raw_text)
    if not commands:
        raise RuntimeError("No curl commands found in the markdown file.")

    normalized_commands = [cmd.replace("http://localhost:8080", args.base_url) for cmd in commands]

    logs_dir = workspace / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    if args.log_file:
        log_file = (workspace / args.log_file).resolve()
        log_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%SZ")
        log_file = logs_dir / f"api-curl-run-{stamp}.log"

    write_log_header(log_file, markdown_file, len(normalized_commands), args.base_url)

    passed = 0
    failed = 0
    total = len(normalized_commands)

    print(f"Found {total} curl command block(s).")
    print(f"Writing output to: {log_file}")

    for idx, command in enumerate(normalized_commands, start=1):
        print(f"[{idx}/{total}] Running command block...")
        returncode, stdout, stderr = run_command(command, workspace)
        if returncode == 0:
            passed += 1
        else:
            failed += 1

        append_result(
            log_file,
            CommandResult(
                index=idx,
                total=total,
                returncode=returncode,
                command=command,
                stdout=stdout,
                stderr=stderr,
            ),
        )

        if returncode != 0 and args.stop_on_failure:
            print(f"Stopping due to failure in command block {idx}.")
            break

    append_summary(log_file, total=passed + failed, passed=passed, failed=failed)
    print(f"Completed. Success: {passed}, Failed: {failed}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())