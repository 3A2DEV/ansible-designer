# ansible-designer

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Ansible](https://img.shields.io/badge/ansible--core-2.15%2B-red.svg)](https://docs.ansible.com/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-purple.svg)](https://claude.ai/code)

AI-assisted Ansible authoring toolkit for Claude Code. Scaffolds, reviews, and updates playbooks, roles, collections, and `ansible.cfg` files following current ansible-core 2.15+ conventions and production best practices.

---

## Installation

```bash
npx skills add 3A2DEV/ansible-designer -a claude-code
```

**Requirements:**
- [Claude Code](https://claude.ai/code) with `bash_tool` enabled
- No additional dependencies — all Ansible knowledge is embedded in the skill

---

## Available Commands

| Command | Description |
|---------|-------------|
| `/ansible-designer` | Show this overview and available commands |
| **Playbooks** | |
| `/ansible-designer:new-playbook` | Create a new playbook (site, component, or AWX-ready) |
| `/ansible-designer:review-playbook` | Review a playbook — severity report, no file modification |
| `/ansible-designer:update-playbook` | Update a playbook — diff + confirm before writing |
| **Roles** | |
| `/ansible-designer:new-role` | Scaffold a complete role (asks about multi-OS support) |
| `/ansible-designer:review-role` | Review a role — severity report, no file modification |
| `/ansible-designer:update-role` | Update a role — diff + confirm before writing |
| **Collections** | |
| `/ansible-designer:new-collection` | Scaffold a new collection with galaxy.yml, plugins, roles |
| `/ansible-designer:review-collection` | Review a collection — severity report, no file modification |
| `/ansible-designer:update-collection` | Update a collection — diff + confirm before writing |
| **ansible.cfg** | |
| `/ansible-designer:new-conf` | Generate annotated ansible.cfg for dev, CI, or AWX |
| `/ansible-designer:review-conf` | Review ansible.cfg — severity report, no file modification |
| `/ansible-designer:update-conf` | Update ansible.cfg — diff + confirm before writing |

---

## How Discovery Works

Every command begins by scanning the project for context:

```
CLAUDE.md → ansible.cfg → README.md → filesystem scan
```

Discovery extracts:
- `roles_path` — where roles live
- `collections_paths` — where collections live
- Existing roles and collections (for FQCN suggestions)
- Inventory location
- Vault configuration
- Namespace hints

This context is used to suggest smart defaults, resolve FQCNs, and skip questions the user doesn't need to answer.

---

## Global Rules

Every command enforces these rules:

1. **FQCN everywhere** — `ansible.builtin.copy`, never `copy`
2. **Tags on every task** — component name + action category (`install`, `configure`, `service`, `validate`)
3. **no_log: true on secrets** — mandatory on tasks handling passwords, tokens, vault variables
4. **Never overwrite silently** — every write shows a summary or diff first, then waits for confirmation
5. **review never modifies** — review commands produce reports only
6. **update always diffs** — update commands show unified diffs before writing
7. **File tree after writes** — every write operation ends with a file tree
8. **Next step suggestion** — every command ends with a concrete next action

---

## Example Usage

### Create a new role for nginx with RHEL + Solaris support

```
/ansible-designer:new-role

> Role name: nginx
> Location: ./roles/
> Multi-OS support: yes (RHEL + Solaris)

→ Generates roles/nginx/ with 12 files including OS-specific task and var files
```

### Review an existing playbook

```
/ansible-designer:review-playbook deploy-app.yml

## Playbook Review: deploy-app.yml

### CRITICAL
- [tasks:line 15] Task "Restart service" uses bare module name 'service' — must use FQCN 'ansible.builtin.service'

### WARNING
- [tasks:line 22] Task "Run migration" uses shell without idempotency guard

### INFO
- Playbook is missing a documentation header
```

### Generate an AWX-optimized ansible.cfg

```
/ansible-designer:new-conf

> Environment: awx

→ Generates ./ansible.cfg with Redis fact caching, AWX callback configuration,
  strict SSH settings, and annotated vault identity list
```

---

## Examples

See the [`examples/`](examples/) directory for working Ansible projects:

| Example | Description |
|---------|-------------|
| `simple-playbook/` | Complete site playbook with inventory, group_vars |
| `role-rhel/` | Full nginx role targeting RHEL 8/9 |
| `role-multiplatform/` | NTP role for RHEL + Solaris + Windows |
| `local-collection/` | Complete local collection with module, filter, and lookup plugins |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
