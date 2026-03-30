---
name: ansible-designer-new-collection
description: Scaffold a new Ansible collection. Triggered by /ansible-designer:new-collection. Collects collection_path, namespace, and collection name, then generates galaxy.yml, README.md, CHANGELOG.md, LICENSE, meta/runtime.yml, plugin skeletons (module, filter, lookup), roles directory, playbooks directory, and docs structure. Shows summary before writing.
---

# new-collection

Scaffold a new Ansible collection with a complete production-ready structure.

---

## Required Inputs

1. **collection_path** — Base directory for the collection (default: `./collections/ansible_collections/` from discovery, or `./collections/ansible_collections/`)
2. **namespace** — Collection namespace (e.g., `myorg`; suggest from existing collections or CLAUDE.md)
3. **collection_name** — Collection name (lowercase, alphanumeric + underscore, no hyphens)
4. **description** — Brief description of the collection's purpose
5. **author** — Author name and email for galaxy.yml

---

## Files to Generate

```
<collection_path>/<namespace>/<name>/
├── galaxy.yml                    ← complete manifest with all fields
├── README.md                     ← collection overview + usage
├── CHANGELOG.md                  ← v0.1.0 initial entry
├── LICENSE                       ← Apache 2.0 full text
├── meta/
│   └── runtime.yml               ← requires_ansible: ">=2.15.0"
├── docs/
│   └── README.md                 ← extended documentation placeholder
├── playbooks/
│   └── site.yml                  ← example playbook using collection roles
├── plugins/
│   ├── modules/
│   │   └── get_info.py           ← complete module skeleton
│   ├── filter/
│   │   └── string_filters.py     ← filter plugin skeleton
│   └── lookup/
│       └── config_value.py       ← lookup plugin skeleton
├── roles/
│   └── .gitkeep                  ← placeholder; add roles with new-role
└── tests/
    ├── integration/
    │   └── .gitkeep
    └── unit/
        └── .gitkeep
```

---

## Content Requirements

### galaxy.yml
Use the complete format from `references/collection.md`. Populate ALL fields including:
- namespace, name, version (0.1.0), readme, description, authors, license, tags
- repository, documentation, homepage, issues
- build_ignore list

### meta/runtime.yml
```yaml
---
requires_ansible: ">=2.15.0"
```

### plugins/modules/get_info.py
Use the complete module skeleton from `references/collection.md`. Customize for the collection's domain:
- DOCUMENTATION block with module name `<namespace>.<name>.get_info`
- argument_spec appropriate to the domain
- Realistic EXAMPLES and RETURN blocks

### plugins/filter/string_filters.py
Use the filter skeleton from `references/collection.md`. Include 2 realistic filters for the collection's domain.

### plugins/lookup/config_value.py
Use the lookup skeleton from `references/collection.md`. Customize for the collection's domain.

### playbooks/site.yml
A working example playbook that uses `<namespace>.<name>.<first_role>`.

---

## Step 3 — Pre-Write Confirmation

Show summary:
```
Will create: ./collections/ansible_collections/myorg/infra/ (18 files)

  galaxy.yml            — namespace: myorg, name: infra, version: 0.1.0
  README.md             — collection overview
  CHANGELOG.md          — v0.1.0 initial
  LICENSE               — Apache 2.0
  meta/runtime.yml      — requires_ansible: >=2.15.0
  docs/README.md
  playbooks/site.yml    — example playbook
  plugins/modules/get_info.py       — module skeleton
  plugins/filter/string_filters.py  — filter plugin skeleton
  plugins/lookup/config_value.py    — lookup plugin skeleton
  roles/.gitkeep
  tests/integration/.gitkeep
  tests/unit/.gitkeep

Proceed? (yes/no)
```

---

## Step 5 — Final Output

Show file tree:
```bash
find <collection_path>/<namespace>/<name> -type f | sort
```

Suggest next step:
```
Next step: Add a role with /ansible-designer:new-role (use FQCN: <namespace>.<name>.<role_name>)
           or run `ansible-galaxy collection build` to test the collection build.
```
