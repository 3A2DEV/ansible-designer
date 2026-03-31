#!/usr/bin/env python3
"""Validator for ansible-designer CI test output.

Exit 0 on PASS, exit 1 on FAIL.
"""

import argparse
import os
import re
import sys

import yaml

SHORT_MODULES = {
    'copy', 'template', 'file', 'service', 'package', 'yum', 'dnf', 'apt',
    'command', 'shell', 'user', 'group', 'cron', 'lineinfile', 'blockinfile',
    'replace', 'fetch', 'get_url', 'unarchive', 'stat', 'find', 'wait_for',
    'uri', 'debug', 'assert', 'set_fact', 'include_tasks', 'import_tasks',
    'include_role', 'import_role', 'systemd', 'firewalld', 'selinux', 'mount',
    'authorized_key', 'known_hosts', 'pip', 'git',
}


def find_yml_files(directory):
    results = []
    for root, _dirs, files in os.walk(directory):
        for fname in files:
            if fname.endswith('.yml') or fname.endswith('.yaml'):
                results.append(os.path.join(root, fname))
    return sorted(results)


def check_yaml_valid(filepath):
    try:
        with open(filepath, encoding='utf-8') as fh:
            yaml.safe_load(fh)
        return None
    except yaml.YAMLError as exc:
        return str(exc)


def find_short_modules(data, rel_path, violations):
    """Recursively walk YAML structure looking for bare module names as dict keys."""
    if isinstance(data, list):
        for item in data:
            find_short_modules(item, rel_path, violations)
    elif isinstance(data, dict):
        for key, value in data.items():
            if key in SHORT_MODULES:
                violations.append(
                    f"{rel_path}: task uses bare module name '{key}' — must use FQCN"
                )
            find_short_modules(value, rel_path, violations)


def validate(args):
    errors = []
    project_dir = os.path.abspath(args.project_dir)

    # Always: validate all YAML files parse cleanly
    yml_files = find_yml_files(project_dir)
    for yf in yml_files:
        err = check_yaml_valid(yf)
        if err:
            rel = os.path.relpath(yf, project_dir)
            errors.append(f"YAML parse error in {rel}: {err}")

    command = args.command

    if command.startswith('new-') or command.startswith('update-'):
        # Check every expected file exists
        if args.expected_files:
            for rel_path in args.expected_files.split():
                full_path = os.path.join(project_dir, rel_path)
                if not os.path.exists(full_path):
                    errors.append(f"Expected file not found: {rel_path}")

        # Scan all YAML files for non-FQCN module usage
        for yf in yml_files:
            rel = os.path.relpath(yf, project_dir)
            try:
                with open(yf, encoding='utf-8') as fh:
                    data = yaml.safe_load(fh)
                find_short_modules(data, rel, errors)
            except yaml.YAMLError:
                pass  # already caught above

    elif command.startswith('review-'):
        # Check output contains at least one severity marker
        if args.output and os.path.exists(args.output):
            with open(args.output, encoding='utf-8') as fh:
                content = fh.read()
            if not re.search(r'(CRITICAL|WARNING|INFO)\s*[|:\-]', content):
                errors.append(
                    "Output does not contain a severity marker "
                    "(CRITICAL|WARNING|INFO followed by |, :, or -)"
                )
        else:
            errors.append(f"Output file not found: {args.output}")

        # Check no new files were created vs pre-snapshot
        if args.pre_snapshot and os.path.exists(args.pre_snapshot):
            with open(args.pre_snapshot, encoding='utf-8') as fh:
                pre_files = {line.strip() for line in fh if line.strip()}
            current_files = set()
            for root, _dirs, files in os.walk(project_dir):
                for fname in files:
                    rel = os.path.relpath(os.path.join(root, fname), project_dir)
                    current_files.add('./' + rel)
            new_files = current_files - pre_files
            if new_files:
                errors.append(
                    f"review-* command created new files: {sorted(new_files)}"
                )
        elif args.pre_snapshot:
            errors.append(f"Pre-snapshot file not found: {args.pre_snapshot}")

    if errors:
        print(f"FAIL [{command}]")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"PASS [{command}]")


def main():
    parser = argparse.ArgumentParser(
        description='Validate ansible-designer skill output'
    )
    parser.add_argument('--command', required=True,
                        help='Sub-command being tested (e.g. new-playbook)')
    parser.add_argument('--output',
                        help='Path to captured stdout from opencode run')
    parser.add_argument('--project-dir', required=True,
                        help='Path to the ansible project directory after execution')
    parser.add_argument('--expected-files',
                        help='Space-separated list of relative paths that must exist')
    parser.add_argument('--pre-snapshot',
                        help='Path to file listing pre-run files (for review-* commands)')
    args = parser.parse_args()
    validate(args)


if __name__ == '__main__':
    main()
