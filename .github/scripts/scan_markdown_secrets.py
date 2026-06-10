import argparse
import re
import sys
from pathlib import Path


TARGET_EXT = {".md"}

PATTERNS = {
    "JWT": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "AWS_ACCESS_KEY_ID": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "PRIVATE_KEY_BLOCK": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "SECRET_ASSIGNMENT": re.compile(
        r"\b(?:api[_-]?key|secret|token|password|passwd|access[_-]?key)\b\s*[:=]\s*['\"]?(?!<|YOUR_|your_|example|sample|changeme|redacted)[A-Za-z0-9+/=_:.-]{12,}",
        re.IGNORECASE,
    ),
}

SAFE_FRAGMENTS = {
    "example.com",
    "localhost",
    "127.0.0.1",
    "10.0.0.",
    "192.168.",
    "<token>",
    "<password>",
    "<secret>",
    "<redacted>",
    "your_token",
    "your_password",
    "your-password",
    "your_secret",
    "sample_token",
    "example_token",
}


def is_safe_line(line: str) -> bool:
    lower = line.lower()
    return any(fragment in lower for fragment in SAFE_FRAGMENTS)


def scan_file(filepath: Path):
    results = []
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return results

    for line_number, line in enumerate(lines, 1):
        if is_safe_line(line):
            continue
        for name, pattern in PATTERNS.items():
            if pattern.search(line):
                results.append((line_number, name, line.strip()))
    return results


def iter_markdown_files(base_dir: Path):
    for path in base_dir.rglob("*"):
        if "_inbox" in path.parts:
            continue
        if path.is_file() and path.suffix.lower() in TARGET_EXT:
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan Markdown files for likely committed secrets.")
    parser.add_argument("--base", default="docs", help="Directory to scan. Defaults to docs.")
    args = parser.parse_args()

    base_dir = Path(args.base)
    if not base_dir.exists():
        print(f"Scan base does not exist: {base_dir}", file=sys.stderr)
        return 2

    all_findings = {}
    for path in iter_markdown_files(base_dir):
        findings = scan_file(path)
        if findings:
            all_findings[str(path)] = findings

    if not all_findings:
        print("No likely secrets found in Markdown files.")
        return 0

    print("Potential secrets detected:\n")
    for file, issues in all_findings.items():
        print(f"File: {file}")
        for line_num, tag, content in issues:
            print(f"  - [{tag}] line {line_num}: {content[:100]}")
        print()

    print("Guidance:")
    print("- Replace real values with placeholders such as `<TOKEN>`, `<PASSWORD>`, or `<SECRET>`.")
    print("- If this is a false positive, rewrite the example to make the placeholder explicit.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
