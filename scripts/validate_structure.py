#!/usr/bin/env python3
"""Validate ansible-designer skill and example directory structure.

Rules are discovery-based — no hardcoded file lists:

  skills/ansible-designer/
    Must contain SKILL.md (root entry point).

  skills/ansible-designer/references/
    Every .md file must be non-empty.

  skills/{sub-skill}/
    Every immediate subdirectory of skills/ (except ansible-designer/) must
    contain SKILL.md.  These are the installed sub-commands
    (ansible-designer:new-playbook, etc.).

  examples/
    Every immediate subdirectory must contain README.md.

Usage:
  # Check everything
  python3 scripts/validate_structure.py

  # Check only paths touched by a PR (pass changed file list)
  python3 scripts/validate_structure.py --changed path/a path/b ...
"""
import argparse
import pathlib
import sys

SKILLS_ROOT = pathlib.Path("skills")
SKILL_ROOT = SKILLS_ROOT / "ansible-designer"
REFS_ROOT = SKILL_ROOT / "references"
EXAMPLES_ROOT = pathlib.Path("examples")


def _relevant(path: pathlib.Path, changed: set[str] | None) -> bool:
    """Return True if path is in scope (always True when not in PR mode)."""
    if changed is None:
        return True
    p = str(path)
    return any(p in c or c.startswith(p) for c in changed)


def check_subskills(changed: set[str] | None) -> list[str]:
    """Root entry SKILL.md must exist; every dir in skills/ except
    ansible-designer/ must also have SKILL.md (these are the sub-commands)."""
    errors = []

    if not SKILL_ROOT.exists():
        return [f"MISSING directory: {SKILL_ROOT}"]

    root_skill = SKILL_ROOT / "SKILL.md"
    if _relevant(root_skill, changed):
        if root_skill.exists():
            print(f"OK    {root_skill}")
        else:
            errors.append(f"MISSING: {root_skill}")

    # Sub-skills live one level up: skills/{sub-skill}/SKILL.md
    if not SKILLS_ROOT.exists():
        return errors + [f"MISSING directory: {SKILLS_ROOT}"]

    for d in sorted(SKILLS_ROOT.iterdir()):
        if not d.is_dir() or d.name == "ansible-designer":
            continue
        skill_md = d / "SKILL.md"
        if not _relevant(skill_md, changed):
            continue
        if skill_md.exists():
            print(f"OK    {skill_md}")
        else:
            errors.append(f"MISSING: {skill_md}  ('{d.name}/' has no SKILL.md)")

    return errors


def check_references(changed: set[str] | None) -> list[str]:
    """Every .md in references/ must exist and be non-empty."""
    errors = []

    if not REFS_ROOT.exists():
        return [f"MISSING directory: {REFS_ROOT}"]

    refs = sorted(REFS_ROOT.glob("*.md"))
    if not refs:
        return [f"EMPTY directory: {REFS_ROOT} — no .md files found"]

    for ref in refs:
        if not _relevant(ref, changed):
            continue
        if ref.stat().st_size == 0:
            errors.append(f"EMPTY file: {ref}")
        else:
            print(f"OK    {ref}")

    return errors


def check_examples(changed: set[str] | None) -> list[str]:
    """Every example directory must have a README.md."""
    errors = []

    if not EXAMPLES_ROOT.exists():
        return [f"MISSING directory: {EXAMPLES_ROOT}"]

    for example in sorted(EXAMPLES_ROOT.iterdir()):
        if not example.is_dir():
            continue
        if not _relevant(example, changed):
            continue
        readme = example / "README.md"
        if readme.exists():
            print(f"OK    {readme}")
        else:
            errors.append(f"MISSING: {readme}  ('{example.name}/' has no README.md)")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate ansible-designer skill and example structure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--changed",
        nargs="+",
        metavar="PATH",
        help="Limit checks to these paths (PR mode). Omit to check everything.",
    )
    args = parser.parse_args()

    changed: set[str] | None = set(args.changed) if args.changed else None

    if changed is not None:
        print(f"PR mode: scoping checks to {len(changed)} changed path(s).\n")

    errors: list[str] = []

    print("=== Sub-skill SKILL.md files ===")
    errors += check_subskills(changed)
    print()

    print("=== Reference files ===")
    errors += check_references(changed)
    print()

    print("=== Example directories ===")
    errors += check_examples(changed)
    print()

    if errors:
        print(f"FAILED — {len(errors)} issue(s) found:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    print("All structure checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
