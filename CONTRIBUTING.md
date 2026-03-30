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
name: ansible-designer-<subcommand>    # kebab-case, max 64 characters
description: <under 1024 characters, no angle brackets>
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

### Validate SKILL.md frontmatter

```bash
python3 -c "
import yaml, sys, pathlib
for f in pathlib.Path('skills').rglob('SKILL.md'):
    content = f.read_text()
    if content.startswith('---'):
        front = content.split('---')[1]
        try:
            data = yaml.safe_load(front)
            name = data.get('name', '')
            desc = data.get('description', '')
            assert len(name) <= 64, f'name too long: {name}'
            assert len(desc) <= 1024, f'description too long'
            assert '<' not in desc and '>' not in desc, 'angle brackets in description'
            print(f'OK: {f}')
        except Exception as e:
            print(f'FAIL: {f}: {e}')
            sys.exit(1)
"
```

### Validate examples with ansible-lint

```bash
pip install ansible-lint
ansible-lint examples/
```

### Check all expected files exist

```bash
for f in \
  "skills/ansible-designer/SKILL.md" \
  "skills/ansible-designer/new-playbook/SKILL.md" \
  "skills/ansible-designer/review-playbook/SKILL.md" \
  "skills/ansible-designer/update-playbook/SKILL.md" \
  "skills/ansible-designer/new-role/SKILL.md" \
  "skills/ansible-designer/review-role/SKILL.md" \
  "skills/ansible-designer/update-role/SKILL.md" \
  "skills/ansible-designer/new-collection/SKILL.md" \
  "skills/ansible-designer/review-collection/SKILL.md" \
  "skills/ansible-designer/update-collection/SKILL.md" \
  "skills/ansible-designer/new-conf/SKILL.md" \
  "skills/ansible-designer/review-conf/SKILL.md" \
  "skills/ansible-designer/update-conf/SKILL.md" \
  "skills/ansible-designer/references/discovery.md" \
  "skills/ansible-designer/references/best_practices.md" \
  "skills/ansible-designer/references/playbook.md" \
  "skills/ansible-designer/references/role.md" \
  "skills/ansible-designer/references/collection.md" \
  "skills/ansible-designer/references/inventory.md" \
  "skills/ansible-designer/references/ansible_cfg.md"; do
  [ -f "$f" ] && echo "OK: $f" || echo "MISSING: $f"
done
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
