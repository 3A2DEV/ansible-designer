# Discovery Reference

Every `ansible-designer` sub-skill starts with discovery unless the user already supplied all required inputs inline. Discovery builds the working context used for generation, review, and update flows.

## Discovery Order

Read sources in this order:

1. `CLAUDE.md`
2. `ansible.cfg`
3. `README.md`
4. filesystem scan

Later sources confirm or refine earlier hints. Filesystem state is the final ground truth.

## What to Collect

Build a context object with these fields:

```yaml
context:
  project_root:
  ansible_cfg_path:
  roles_path: []
  collections_path: []
  inventory_paths: []
  existing_roles: []
  existing_collections: []
  existing_playbooks: []
  existing_examples: []
  namespace_hint:
  collection_hint:
  environment_hint:
  testing_hints: []
```

## Step 1: Read `CLAUDE.md`

Extract:
- repository-specific structure rules
- expected Ansible baseline version
- any explicit `roles_path`, `collections_path`, or inventory conventions
- testing and validation commands

If multiple guidance files exist up the tree, prefer the closest one that governs the current repository.

## Step 2: Read `ansible.cfg`

Search in the normal Ansible order:
1. `ANSIBLE_CONFIG`
2. `./ansible.cfg`
3. `~/.ansible.cfg`
4. `/etc/ansible/ansible.cfg`

Extract at minimum:
- `inventory`
- `roles_path`
- `collections_path`
- `remote_user`
- `fact_caching`
- `fact_caching_connection`
- `vault_password_file`
- `vault_identity_list`
- `callbacks_enabled`

Notes:
- prefer `collections_path` when generating new config examples
- if `collections_paths` is already present in existing content, treat it as legacy-compatible input and preserve user intent during review/update
- resolve relative paths relative to the directory containing `ansible.cfg`

## Step 3: Read `README.md`

Extract:
- project description
- namespace or collection naming clues
- expected platforms
- any documented examples, inventories, roles, or collections
- any developer workflow notes such as `ansible-lint`, `ansible-test`, or syntax-check commands

## Step 4: Scan the Filesystem

### Roles

Search:
- configured `roles_path`
- `./roles`
- collection roles under `*/collections/ansible_collections/*/*/roles`

Record:
- role name
- absolute path
- whether `meta/main.yml` exists
- whether `tests/test.yml` exists

### Collections

Search configured collection roots for:
- `galaxy.yml`
- `meta/runtime.yml`

Record:
- namespace
- collection name
- path
- bundled roles
- plugins present

### Playbooks

Look in:
- repository root
- `playbooks/`
- `examples/*/`

Record files that look like playbooks:
- `.yml` or `.yaml`
- contain at least one play with `hosts:`

### Inventory

Check for:
- configured inventory path
- `inventory/`
- `hosts`
- `inventory.yml`
- `inventory/hosts.yml`
- plugin inventory files under example directories

### Tests and validation

Look for:
- `tests/`
- Molecule files if present
- `ansible-lint` config
- `ansible-test` targets in collection examples
- scripts referenced by docs

### Examples

Under `examples/`, record:
- example name
- main scenario
- key files present
- notable gaps such as missing templates, README mismatches, or missing test files

## How Discovery Should Influence Commands

### Generation commands

Use discovery to:
- suggest existing namespaces and paths
- avoid asking for values that are already inferable
- keep generated examples aligned with the surrounding repository

### Review commands

Use discovery to:
- resolve filenames or role names to actual paths
- judge whether missing content is truly missing or intentionally external
- report context-aware findings such as unresolved role references or collection dependency expectations

### Update commands

Use discovery to:
- modify the correct target file
- preserve current structure and conventions
- avoid introducing path or namespace mismatches

## Edge Cases

### No `ansible.cfg`

Assume:
- roles under `./roles`
- collections under `./collections/ansible_collections`
- inventory not fixed yet

### Multiple role or collection roots

Use the first configured path as the default generation target, but report all discovered roots in working memory.

### Large repositories

Skip obvious noise:
- `.git/`
- virtual environments
- `node_modules/`
- build output

### Existing broken examples

Do not normalize broken state silently in discovery. Record the mismatch so generation or review commands can account for it.
