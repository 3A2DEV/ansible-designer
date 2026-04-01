---
name: ansible-designer
description: "AI-assisted Ansible authoring toolkit for Claude Code. Scaffolds, reviews, and updates playbooks, roles, collections, and ansible.cfg files following production best practices. Sub-commands: new-playbook, review-playbook, update-playbook, new-role, review-role, update-role, new-collection, review-collection, update-collection, new-conf, review-conf, update-conf. Requires bash_tool. Runs discovery (CLAUDE.md to ansible.cfg to README to filesystem) at the start of every command."
---

# ansible-designer

AI-assisted Ansible authoring toolkit. Scaffolds, reviews, and updates Ansible projects with production-quality output following official ansible-core 2.15+ conventions.

---

## Available Commands

### Playbook Commands
| Command | Description |
|---------|-------------|
| `/ansible-designer:new-playbook` | Create a new playbook (site, component, or AWX-ready) |
| `/ansible-designer:review-playbook` | Review an existing playbook — severity report, no file modification |
| `/ansible-designer:update-playbook` | Update a playbook — shows diff, requires confirmation |

### Role Commands
| Command | Description |
|---------|-------------|
| `/ansible-designer:new-role` | Scaffold a complete role — asks about multi-OS support |
| `/ansible-designer:review-role` | Review a role — severity report, no file modification |
| `/ansible-designer:update-role` | Update a role — shows diff, requires confirmation |

### Collection Commands
| Command | Description |
|---------|-------------|
| `/ansible-designer:new-collection` | Scaffold a new collection with galaxy.yml, plugins, roles structure |
| `/ansible-designer:review-collection` | Review a collection — severity report, no file modification |
| `/ansible-designer:update-collection` | Update a collection — shows diff, requires confirmation |

### ansible.cfg Commands
| Command | Description |
|---------|-------------|
| `/ansible-designer:new-conf` | Generate an annotated ansible.cfg for dev, CI, or AWX |
| `/ansible-designer:review-conf` | Review an ansible.cfg — severity report, no file modification |
| `/ansible-designer:update-conf` | Update ansible.cfg — shows diff, requires confirmation |

---

## Global Rules

Every sub-command enforces these rules without exception:

1. **Discovery first** — At command start, read in order: `CLAUDE.md` → `ansible.cfg` → `README.md` → filesystem scan. Build internal context (roles, collections, paths, namespace). Skip if user already provided all required parameters inline. See `references/discovery.md`.

2. **Never overwrite silently** — Before writing any file, show a summary (new files) or unified diff (modifications). Wait for explicit user confirmation (`yes` / `y`). Only write after confirmation.

3. **FQCN mandatory** — Every module reference uses the Fully Qualified Collection Name. `ansible.builtin.copy`, never `copy`. `ansible.builtin.service`, never `service`. See `references/best_practices.md` for the complete mapping table.

4. **no_log: true on secrets** — Every task handling passwords, tokens, API keys, vault variables, or credentials must include `no_log: true`.

5. **Tags on every task** — Minimum: component name + action category (`install`, `configure`, `service`, `validate`, `security`, `cleanup`). No task may be untagged.

6. **review never modifies** — `review-*` commands produce a structured severity report (CRITICAL / WARNING / INFO) only. They never write, modify, or suggest `sed` commands. Report only.

7. **update always diffs** — `update-*` commands read the existing file, compute the change, show a unified diff, and wait for explicit confirmation before writing a single byte.

8. **Show file tree after writes** — After any write operation, run `find <path> -type f | sort` and display the resulting file tree.

9. **Suggest next step** — End every command with a concrete suggestion: which command to run next, or what to validate.

---

## Standard Operational Flow

Every command follows this exact sequence:

### Step 1 — Discovery
```
Read: CLAUDE.md → ansible.cfg → README.md → filesystem scan
Build: internal context (roles_path, collections_path, existing roles, collections, inventory)
Report: "Discovery complete: [summary of what was found]"
```

Skip Step 1 only if the user provided all required parameters inline.

### Step 2 — Parameter Collection
- If the user already provided all required parameters: proceed to Step 3.
- Otherwise: ask **one question at a time**, using discovery context for smart defaults.
- Never ask for something that can be inferred from discovery (e.g., don't ask for namespace if a collection already exists).

### Step 3 — Pre-Write Confirmation
- For **new** files: show a summary of what will be created (paths + brief description).
- For **update** commands: show a unified diff (`--- original`, `+++ proposed`).
- **Wait for explicit user confirmation** (`yes`, `y`, or equivalent) before proceeding.
- If user says no: ask what to change and loop back to Step 2.

### Step 4 — Execution
- Write or modify files using bash commands.
- Follow all global rules: FQCN, tags, no_log.
- Use templates from the appropriate `references/` file as the base.

### Step 5 — Final Output
```
Show file tree of all created/modified files.
Suggest: "Next step: [specific actionable suggestion]"
```

---

## Reference Files

| File | Used by |
|------|---------|
| `references/discovery.md` | All commands — Step 1 |
| `references/best_practices.md` | All commands — FQCN, tags, no_log, idempotency |
| `references/playbook.md` | new-playbook, review-playbook, update-playbook |
| `references/role.md` | new-role, review-role, update-role |
| `references/collection.md` | new-collection, review-collection, update-collection |
| `references/ansible_cfg.md` | new-conf, review-conf, update-conf |
| `references/inventory.md` | All commands — inventory context |

---

## Installation

```bash
npx skills add 3A2DEV/ansible-designer -a claude-code
```

Requires Claude Code with `bash_tool` enabled.
