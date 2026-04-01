# ansible-designer

![GitHub License](https://img.shields.io/github/license/3a2dev/ansible-designer?logo=github&color=blue)
![Claude Code](https://img.shields.io/badge/SKILL-orange?logo=claude&label=Claude%20Code)
![Ansible Designer](https://img.shields.io/badge/skill-orange?logo=claude&label=%2Fansible-designer)
![Ansible Core](https://img.shields.io/badge/2.15%2B-red?logo=ansible&label=Ansible%20Core%20)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/3A2DEV/ansible-designer/validate.yml?branch=main&logo=github&label=Validate%20CI)


```
 ▐▛███▜▌   Claude Code
▝▜█████▛▘  Sonnet 4.6 · Claude
  ▘▘ ▝▝    ansible-designer/
  ⎿  SessionStart:startup says: [ansible-designer 0.1.7]
     ──────────────────────────────────────────────────────────

 █████╗ ███╗   ██╗███████╗██╗██████╗ ██╗     ███████╗         
██╔══██╗████╗  ██║██╔════╝██║██╔══██╗██║     ██╔════╝         
███████║██╔██╗ ██║███████╗██║██████╔╝██║     █████╗           
██╔══██║██║╚██╗██║╚════██║██║██╔══██╗██║     ██╔══╝           
██║  ██║██║ ╚████║███████║██║██████╔╝███████╗███████╗         
╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝╚═════╝ ╚══════╝╚══════╝         
                                                              
██████╗ ███████╗███████╗██╗ ██████╗ ███╗   ██╗███████╗██████╗ 
██╔══██╗██╔════╝██╔════╝██║██╔════╝ ████╗  ██║██╔════╝██╔══██╗
██║  ██║█████╗  ███████╗██║██║  ███╗██╔██╗ ██║█████╗  ██████╔╝
██║  ██║██╔══╝  ╚════██║██║██║   ██║██║╚██╗██║██╔══╝  ██╔══██╗
██████╔╝███████╗███████║██║╚██████╔╝██║ ╚████║███████╗██║  ██║
╚═════╝ ╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝

───────────────────────────────────────────────────────────────
❯ /ansible-designer
───────────────────────────────────────────────────────────────
```

AI-assisted Ansible authoring toolkit for Claude Code. Scaffolds, reviews, and updates playbooks, roles, collections, and `ansible.cfg` files following ansible-core 2.15+ conventions and production best practices.

---

## Installation

### Option A — Claude Code plugin system (recommended)

Using Claude Code:

```bash
/plugin marketplace add 3A2DEV/ansible-designer
```
```bash
/plugin install ansible-designer
```

### Option B — npx skills CLI

```bash
npx skills add 3A2DEV/ansible-designer --skill '*'
```

Both options register each skill as a top-level command (e.g. `/new-playbook`, `/review-role`).

**Requirements:**
- [Claude Code](https://claude.ai/code)
- No additional dependencies — all Ansible knowledge is embedded in the skill

---

## Available Commands

| Command | Description |
|---------|-------------|
| `/ansible-designer` | Show this overview and available commands |
| **Playbooks** | |
| `/new-playbook` | Create a new playbook (site, component, or AWX-ready) |
| `/review-playbook` | Review a playbook — severity report, no file modification |
| `/update-playbook` | Update a playbook — diff + confirm before writing |
| **Roles** | |
| `/new-role` | Scaffold a complete role (asks about multi-OS support) |
| `/review-role` | Review a role — severity report, no file modification |
| `/update-role` | Update a role — diff + confirm before writing |
| **Collections** | |
| `/new-collection` | Scaffold a new collection with galaxy.yml, plugins, roles |
| `/review-collection` | Review a collection — severity report, no file modification |
| `/update-collection` | Update a collection — diff + confirm before writing |
| **ansible.cfg** | |
| `/new-conf` | Generate annotated ansible.cfg for dev, CI, or AWX |
| `/review-conf` | Review ansible.cfg — severity report, no file modification |
| `/update-conf` | Update ansible.cfg — diff + confirm before writing |

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
8. **Testing-aware output** — generated examples and updates include a realistic validation path
9. **Next step suggestion** — every command ends with a concrete next action

---

## Example Usage

### Create a new role for nginx with RHEL + Solaris support

```bash
/new-role

> Role name: nginx
> Location: ./roles/
> Multi-OS support: yes

→ Generates roles/nginx/ with 12 files including OS-specific task and var files
```

### Review an existing playbook

```bash
/review-playbook deploy-app.yml

## Playbook Review: deploy-app.yml

### CRITICAL
- [tasks:line 15] Task "Restart service" uses bare module name 'service' — must use FQCN 'ansible.builtin.service'

### WARNING
- [tasks:line 22] Task "Run migration" uses shell without idempotency guard

### INFO
- Playbook is missing a documentation header
```

### Generate an AWX-optimized ansible.cfg

```bash
/new-conf

> Environment: awx

→ Generates ./ansible.cfg with Redis fact caching, AWX callback configuration,
  strict SSH settings, and annotated vault identity list
```

### Update ansible.cfg with credential-safe diff display

```bash
/update-conf

> Change: enable fact caching with redis

⚠ Warning: 1 line(s) with credential-like values were redacted from this display.
  Review the file directly before applying changes.

--- ansible.cfg (original)
+++ ansible.cfg (proposed)
@@ -8,6 +8,10 @@
 forks                 = 10
 timeout               = 30
+
+# Fact caching: redis (shared across controller nodes; configure auth via REDIS_URL or vault)
+fact_caching          = redis
+fact_caching_connection = redis://:{{ vault_redis_password }}@cache.internal:6379/0
+fact_caching_timeout  = 86400

Apply this change? (yes/no)
```

### Scaffold a new collection with input validation

```bash
/new-collection

> collection_path: ./collections/ansible_collections/
> namespace: myorg
> collection_name: security_baseline
> description: Baseline security hardening collection for RHEL targets
> author: ops-team <ops@example.com>

Will create: ./collections/ansible_collections/myorg/security_baseline/ (13 files)

  galaxy.yml            — namespace: myorg, name: security_baseline, version: 0.1.0
  README.md             — collection overview
  CHANGELOG.md          — v0.1.0 initial
  LICENSE               — Apache 2.0
  meta/runtime.yml      — requires_ansible: >=2.15.0
  plugins/modules/get_info.py
  plugins/filter/string_filters.py
  plugins/lookup/config_value.py
  roles/.gitkeep
  tests/integration/.gitkeep
  tests/unit/.gitkeep

Proceed? (yes/no)
```

---

## Examples

See the [`examples/`](examples/) directory for working Ansible projects:

| Example | Description |
|---------|-------------|
| `simple-playbook/` | Complete site playbook with inventory, group_vars, and bundled example roles |
| `role-rhel/` | Full nginx role targeting RHEL 8/9 |
| `role-multiplatform/` | NTP role for RHEL + Solaris + Windows |
| `local-collection/` | Complete local collection with module, filter, and lookup plugins |
| `ansible-cfg-profiles/` | Development, CI, and controller-oriented `ansible.cfg` profiles |
| `inventory-vault/` | Safe inventory and vault-wrapper example layout |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
