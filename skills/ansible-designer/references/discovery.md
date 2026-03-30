# Discovery Reference

This document defines the discovery procedure that every ansible-designer sub-skill runs at the start of a command (unless the user has already provided all required parameters inline).

---

## Purpose

Discovery builds an **internal context object** from the project filesystem. Sub-skills use this context to:
- Suggest smart defaults during parameter collection
- Locate existing roles, collections, playbooks, and inventories
- Resolve FQCN components (namespace, collection, role name)
- Identify the correct ansible.cfg scope

---

## Discovery Order

Read sources in this exact order. Each source can enrich or override earlier context.

```
1. CLAUDE.md           → project notes, overrides, custom paths
2. ansible.cfg         → authoritative Ansible configuration
3. README.md           → human-readable project description
4. Filesystem scan     → ground truth of what actually exists
```

---

## Step-by-Step Procedure

### Step 1: Read CLAUDE.md

Look for `CLAUDE.md` in the current directory, then in parent directories (up to project root / git root).

Extract:
- Any `# Ansible` or `# ansible-designer` section
- Custom `roles_path`, `collections_path`, or inventory overrides
- Notes about the project structure (namespaces, environments)
- Any ansible-designer-specific directives the user has placed here

If not found: continue, no error.

### Step 2: Read ansible.cfg

Search in this order:
1. `ANSIBLE_CONFIG` environment variable (if set)
2. `./ansible.cfg` (current working directory)
3. `~/.ansible.cfg`
4. `/etc/ansible/ansible.cfg`

Use the first file found. Extract the following values:

| Key | Section | Purpose |
|-----|---------|---------|
| `roles_path` | `[defaults]` | Where to look for roles |
| `collections_paths` | `[defaults]` | Where to look for collections |
| `inventory` | `[defaults]` | Default inventory path |
| `remote_user` | `[defaults]` | Default SSH user |
| `vault_password_file` | `[defaults]` | Vault password file path |
| `vault_identity_list` | `[defaults]` | Named vault identities |
| `fact_caching` | `[defaults]` | Fact cache backend |
| `fact_caching_connection` | `[defaults]` | Fact cache connection string |
| `callbacks_enabled` | `[defaults]` | Active callback plugins |

**Handling multiple `roles_path` entries:**
`roles_path` can contain multiple paths separated by `:` (POSIX) or `;` (Windows).
Parse all paths and scan each one.

```
roles_path = ./roles:~/.ansible/roles:/usr/share/ansible/roles
```
→ scan `./roles`, `~/.ansible/roles`, `/usr/share/ansible/roles`

**Relative vs absolute paths:**
- Relative paths in ansible.cfg are relative to the directory containing ansible.cfg, not CWD.
- Resolve them to absolute paths before scanning.

If ansible.cfg not found: use Ansible defaults (`./roles`, `~/.ansible/roles`).

### Step 3: Read README.md

Search for `README.md` in the current directory.

Extract:
- Project name / description
- Mention of namespaces (e.g., "Collection: myorg.infra")
- Environment targets (dev, staging, production)
- Any custom conventions described

If not found: continue, no error.

### Step 4: Filesystem Scan

Scan the project tree to discover actual content:

#### 4a. Roles

For each path in `roles_path` (plus `./roles` if not already included):
```
find <path> -maxdepth 2 -name "tasks" -type d
```
For each found role directory, record:
- Role name (directory name)
- Absolute path
- Whether it has `meta/main.yml` (FQCN-compatible)

#### 4b. Collections

For each path in `collections_paths` (plus `./collections/ansible_collections` if not included):
```
find <path> -maxdepth 3 -name "galaxy.yml" -type f
```
For each found collection, record:
- Namespace (parent directory name)
- Collection name (galaxy.yml `name` field)
- Version (galaxy.yml `version` field)
- Roles inside the collection: `<collection_path>/roles/*/`

#### 4c. Playbooks

Scan current directory and `./playbooks/` for `*.yml` files that start with `---` and contain `hosts:`.

#### 4d. Inventory

Check these locations in order:
1. Path from ansible.cfg `inventory`
2. `./inventory/`
3. `./hosts`
4. `./inventory.yml`
5. `./inventory/hosts.yml`

#### 4e. ansible.cfg locations

Record which ansible.cfg was found and its path.

---

## Internal Context Object

After discovery, build this context structure (conceptual — Claude holds this in working memory):

```yaml
context:
  project_root: /path/to/project
  ansible_cfg_path: /path/to/ansible.cfg        # null if not found

  roles_path:
    - /path/to/project/roles
    - /home/user/.ansible/roles

  collections_path:
    - /path/to/project/collections/ansible_collections

  inventory_path: /path/to/project/inventory    # null if not found

  existing_roles:
    - name: common
      path: /path/to/project/roles/common
      has_meta: true
    - name: nginx
      path: /path/to/project/roles/nginx
      has_meta: true

  existing_collections:
    - namespace: myorg
      name: infra
      version: "1.0.0"
      path: /path/to/project/collections/ansible_collections/myorg/infra
      roles:
        - common
        - webserver

  existing_playbooks:
    - site.yml
    - playbooks/deploy.yml

  vault_config:
    vault_password_file: ~/.vault_pass
    vault_identity_list: null

  namespace_hint: myorg      # extracted from README or existing collections
  environment_hint: dev      # extracted from README or ansible.cfg profile
```

---

## Edge Cases

### Missing CLAUDE.md
No error. Skip to ansible.cfg.

### Missing ansible.cfg
Use Ansible built-in defaults:
- `roles_path`: `./roles`
- `collections_paths`: `./collections/ansible_collections:~/.ansible/collections/ansible_collections`
- No default inventory

### Relative paths in ansible.cfg
Always resolve relative to the directory containing ansible.cfg:
```
# ansible.cfg is at /project/ansible.cfg
roles_path = ./roles   →  /project/roles
roles_path = ../shared/roles   →  /shared/roles
```

### Multiple roles_path entries
Split on `:` (or `;` on Windows). Scan all of them. Merge results. If the same role name appears in multiple paths, the first path wins (matching Ansible's own precedence).

### No collections found
Set `existing_collections: []`. Sub-skills will not suggest FQCN role references.

### No ansible.cfg found
Inform the user during parameter collection: "No ansible.cfg found. Using Ansible defaults." Proceed with defaults.

### Symlinked directories
Follow symlinks during scan but detect cycles (do not recurse into a path already visited).

### Large projects
Limit filesystem scan depth to `maxdepth 4` to avoid scanning node_modules, .git, etc. Skip hidden directories (starting with `.`) except `.github`.

---

## Using Context in Sub-Skills

After discovery, sub-skills use the context as follows:

| Sub-skill | Context used |
|-----------|-------------|
| new-role | `roles_path[0]` as default location, `namespace_hint` for FQCN |
| review-role | `existing_roles` to locate role |
| new-playbook | `existing_roles`, `existing_collections` for role suggestions |
| new-collection | `collections_path[0]` as default location |
| new-conf | `ansible_cfg_path` to avoid overwriting existing; `environment_hint` as default |
| review-conf | `ansible_cfg_path` to locate target file |

---

## Reporting Discovery Results

At the start of each command, briefly report what was found:

```
Discovery complete:
  ansible.cfg: ./ansible.cfg
  Roles found: common, nginx, postgres (./roles/)
  Collections found: myorg.infra (./collections/ansible_collections/)
  Inventory: ./inventory/
```

If discovery finds nothing useful, report that and proceed with parameter collection from scratch.
