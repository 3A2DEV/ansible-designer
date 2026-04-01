#!/usr/bin/env python3
"""Validate SKILL.md frontmatter (name, description length/chars).

Usage:
  # Check all SKILL.md files under skills/
  python3 scripts/validate_frontmatter.py

  # Check specific files only (PR mode — pass changed paths)
  python3 scripts/validate_frontmatter.py skills/ansible-designer/new-role/SKILL.md
"""
import argparse
import pathlib
import sys

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def validate_file(path: pathlib.Path) -> list[str]:
    """Return a list of error strings; empty list means the file is valid."""
    content = path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        return ["no YAML frontmatter block"]

    parts = content.split("---", 2)
    if len(parts) < 3:
        return ["malformed frontmatter — missing closing '---'"]

    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        return [f"YAML parse error: {exc}"]

    if not isinstance(data, dict):
        return ["frontmatter is not a YAML mapping"]

    errors = []
    name = data.get("name", "")
    desc = data.get("description", "")

    if not name:
        errors.append("missing 'name' field")
    elif len(name) > 64:
        errors.append(f"'name' too long ({len(name)} chars, max 64): {name!r}")

    if not desc:
        errors.append("missing 'description' field")
    elif len(desc) > 1024:
        errors.append(f"'description' too long ({len(desc)} chars, max 1024)")
    elif "<" in desc or ">" in desc:
        errors.append("angle brackets not allowed in 'description'")

    return errors


def collect_targets(paths: list[str]) -> list[pathlib.Path]:
    """Resolve explicit paths, keeping only SKILL.md files that exist."""
    targets = []
    for p in paths:
        path = pathlib.Path(p)
        if path.name == "SKILL.md" and path.exists():
            targets.append(path)
    return sorted(targets)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate SKILL.md frontmatter fields.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Specific SKILL.md paths to check. Omit to check all under skills/.",
    )
    args = parser.parse_args()

    if args.files:
        targets = collect_targets(args.files)
        if not targets:
            # None of the changed files were SKILL.md — nothing to do
            print("No SKILL.md files in the provided list — skipping.")
            return 0
    else:
        targets = sorted(pathlib.Path("skills").rglob("SKILL.md"))

    if not targets:
        print("No SKILL.md files found.", file=sys.stderr)
        return 1

    failed = 0
    for f in targets:
        errors = validate_file(f)
        if errors:
            for e in errors:
                print(f"FAIL  {f}: {e}", file=sys.stderr)
            failed += 1
        else:
            print(f"OK    {f}")

    print()
    if failed:
        print(f"{failed}/{len(targets)} file(s) failed.", file=sys.stderr)
        return 1

    print(f"{len(targets)} file(s) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
