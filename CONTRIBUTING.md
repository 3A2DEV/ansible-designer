# Contributing to ansible-designer

Thank you for improving ansible-designer. This document covers how to report issues, submit improvements, and maintain quality standards.

---

## Reporting Issues

Open an issue at the repository with:
- Which command you ran (`/ansible-designer:new-role`, etc.)
- What you expected to happen
- What actually happened
- The relevant Ansible version (`ansible --version`)
- Example input (anonymized if needed)

---

## Submitting Improvements

### Pull request process

1. Fork the repository
2. Create a branch: `git checkout -b fix/review-playbook-fqcn-check`
3. Make your changes (see guidelines below)
4. Test your changes (see Testing section)
5. Submit a pull request with a clear description

### What makes a good PR

- One logical change per PR
- Updated CHANGELOG.md entry
- No regressions in existing examples

---

## Skill File Guidelines

### SKILL.md frontmatter

Every `SKILL.md` must have valid YAML frontmatter:

```yaml
---
name: ansible-designer-new-role        # kebab-case, max 64 characters
description: "Scaffold a new Ansible role. Triggered by /ansible-designer:new-role."
---
```

- `name`: must be kebab-case, max 64 characters
- `description`: must be under 1024 characters, no `<` or `>` characters
- Description should name the triggering slash command explicitly

### Content quality

All content in SKILL.md files must be:
- **Complete** — no `# TODO`, no `# add your tasks here` placeholders
- **Realistic** — use actual component names, realistic paths, real package names
- **Current** — ansible-core 2.15+ syntax only (no deprecated `include:`, no bare module names)
- **Self-contained** — a command must be usable knowing only its own SKILL.md + the references it cites

---

## Ansible Content Standards

All Ansible YAML (tasks, playbooks, roles, examples) must follow:

### FQCN is mandatory

```yaml
# WRONG
- name: Install nginx
  package:
    name: nginx
    state: present

# CORRECT
- name: Install nginx
  ansible.builtin.package:
    name: nginx
    state: present
```

### Tags are mandatory

```yaml
# WRONG
- name: Deploy config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf

# CORRECT
- name: Deploy config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  tags:
    - nginx
    - configure
```

### no_log on secret-handling tasks

```yaml
# WRONG
- name: Set DB password
  community.postgresql.postgresql_user:
    name: app
    password: "{{ db_password }}"

# CORRECT
- name: Set DB password
  community.postgresql.postgresql_user:
    name: app
    password: "{{ db_password }}"
  no_log: true
  tags:
    - postgres
    - configure
```

### Idempotency

- Prefer modules over shell/command
- When shell/command is unavoidable: add `creates:`, `removes:`, or `changed_when:`
- Always use `state:` parameter explicitly

---

## Testing Skill Changes

Two validation scripts in `scripts/` cover what CI checks. Run them locally before opening a PR.

### Install the dependency

```bash
pip install pyyaml
# macOS (PEP 668): use a venv instead
python3 -m venv /tmp/ad-venv && /tmp/ad-venv/bin/pip install pyyaml
```

### Validate SKILL.md frontmatter

Checks `name` (kebab-case, max 64 chars) and `description` (max 1024 chars, no angle brackets) for every `SKILL.md` under `skills/`.

```bash
# All files
python3 scripts/validate_frontmatter.py

# Specific files only (useful when working on one sub-skill)
python3 scripts/validate_frontmatter.py skills/ansible-designer/new-role/SKILL.md
```

### Validate skill and example structure

Discovery-based — no hardcoded file lists. Checks:
- Every subdirectory of `skills/ansible-designer/` (except `references/`) has a `SKILL.md`
- Every `.md` file in `references/` is non-empty
- Every directory in `examples/` has a `README.md`

```bash
# All directories
python3 scripts/validate_structure.py

# Scoped to changed paths (mirrors what CI does on PRs)
python3 scripts/validate_structure.py --changed skills/ansible-designer/new-role/SKILL.md
```

### Validate examples with ansible-lint

```bash
pip install ansible-lint
ansible-lint examples/
```

---

## Changelog

Update `CHANGELOG.md` with every change. Use this format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Description of new feature or file

### Changed
- Description of modification

### Fixed
- Description of bug fix
```
