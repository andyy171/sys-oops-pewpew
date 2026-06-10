import argparse
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote


MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_SRC_RE = re.compile(r"""<(?:img|script)\b[^>]*\bsrc=["']([^"']+)["']""", re.IGNORECASE)
HTML_HREF_RE = re.compile(r"""<a\b[^>]*\bhref=["']([^"']+)["']""", re.IGNORECASE)
EXTERNAL_SCHEMES = (
    "http://",
    "https://",
    "mailto:",
    "tel:",
    "data:",
    "ftp://",
    "obsidian://",
)


def strip_code_fences(text: str) -> str:
    output = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            output.append(line)
    return "\n".join(output)


def normalize_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if not target:
        return None
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    target = target.split()[0]
    target = target.split("#", 1)[0]
    target = unquote(target)
    if not target:
        return None
    if target.lower().startswith(EXTERNAL_SCHEMES):
        return None
    return target


def candidate_exists(source_file: Path, target: str, repo_root: Path) -> bool:
    target_path = Path(target)
    if target_path.is_absolute():
        candidate = repo_root / target_path.relative_to(target_path.anchor)
    else:
        candidate = source_file.parent / target_path

    if candidate.exists():
        return True
    if candidate.suffix == "":
        return (candidate / "index.md").exists() or (candidate / "README.md").exists() or candidate.with_suffix(".md").exists()
    return False


def scan_file(path: Path, repo_root: Path):
    text = strip_code_fences(path.read_text(encoding="utf-8"))
    findings = []

    for regex in (MARKDOWN_LINK_RE, HTML_SRC_RE, HTML_HREF_RE):
        for match in regex.finditer(text):
            target = normalize_target(match.group(1))
            if target is None:
                continue
            if not candidate_exists(path, target, repo_root):
                line_number = text.count("\n", 0, match.start()) + 1
                findings.append((line_number, target))

    return findings


def changed_markdown_files(base_ref: str, docs_root: Path, repo_root: Path):
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base_ref}...HEAD", "--", str(docs_root.relative_to(repo_root))],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr.strip())
        return []

    files = []
    for raw_path in result.stdout.splitlines():
        path = repo_root / raw_path
        if path.suffix.lower() == ".md" and path.exists() and "_inbox" not in path.parts:
            files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local Markdown links and local image/script references.")
    parser.add_argument("--docs-root", default="docs", help="Docs directory. Defaults to docs.")
    parser.add_argument("--changed-from", help="Only check Markdown files changed since this git ref/SHA.")
    args = parser.parse_args()

    repo_root = Path.cwd()
    docs_root = (repo_root / args.docs_root).resolve()
    if not docs_root.exists():
        print(f"Docs root does not exist: {docs_root}")
        return 2

    if args.changed_from:
        markdown_files = changed_markdown_files(args.changed_from, docs_root, repo_root)
    else:
        markdown_files = [path for path in docs_root.rglob("*.md") if "_inbox" not in path.parts]

    if not markdown_files:
        print("No Markdown files to check.")
        return 0

    all_findings = {}
    for path in markdown_files:
        findings = scan_file(path, repo_root)
        if findings:
            all_findings[str(path.relative_to(repo_root))] = findings

    if not all_findings:
        print("All local Markdown links resolved.")
        return 0

    print("Broken local Markdown links found:\n")
    for file, findings in all_findings.items():
        print(file)
        for line, target in findings:
            print(f"  line {line}: {target}")
        print()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
