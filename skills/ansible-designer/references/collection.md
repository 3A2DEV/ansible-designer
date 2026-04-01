# Collection Reference

Use this reference for collection generation, review, and update flows.

## Standard Collection Layout

```text
collections/ansible_collections/<namespace>/<name>/
├── galaxy.yml
├── README.md
├── CHANGELOG.md
├── meta/
│   └── runtime.yml
├── plugins/
│   ├── modules/
│   ├── filter/
│   └── lookup/
├── roles/
├── playbooks/
└── tests/
    ├── integration/
    └── unit/
```

Additional files are fine, but generated examples should start from this shape.

## `galaxy.yml`

Recommended baseline:

```yaml
---
namespace: myorg
name: infra
version: 0.1.0
readme: README.md
description: Infrastructure automation content for the myorg platform team

authors:
  - Platform Team <platform@myorg.example>

license:
  - Apache-2.0

tags:
  - infrastructure
  - linux

dependencies: {}

repository: https://github.com/myorg/infra
documentation: https://github.com/myorg/infra/tree/main/docs
homepage: https://myorg.example.com/platform
issues: https://github.com/myorg/infra/issues

build_ignore:
  - "*.tar.gz"
  - ".git"
  - ".github"
  - "tests/output"
```

Guidance:
- keep the description short and factual
- include dependencies only when the content really needs them
- use semantic versioning

## `meta/runtime.yml`

Use at minimum:

```yaml
---
requires_ansible: ">=2.15.0"
```

Add plugin routing or deprecation data only when needed.

## Plugins

If the example includes plugins:
- each module must have `DOCUMENTATION`, `EXAMPLES`, and `RETURN`
- module code should use `AnsibleModule`
- filters and lookups should be small and purpose-specific
- plugin examples should be backed by at least one usage example in README or playbooks

See `plugins.md` for skeleton details.

## Roles in Collections

Collection roles should:
- live under `roles/<role_name>/`
- use the same role conventions as standalone roles
- be referenced by FQCN in playbooks when clarity matters

Example:

```yaml
roles:
  - role: myorg.infra.baseline
```

## Testing Expectations

Collection examples should include enough structure to demonstrate how the content would be validated:
- `ansible-test sanity` for plugin-bearing collections
- integration target directories when custom modules are present
- a local example playbook that exercises at least one role or plugin

The tests do not need to be exhaustive, but the structure should not contradict official collection practices.

## Review Heuristics

Flag these as high-signal issues:
- missing `galaxy.yml`
- missing required `galaxy.yml` fields
- missing `meta/runtime.yml`
- Python plugin syntax problems
- plugin modules missing documentation blocks
- collection example lacks any runnable usage path
- roles exist but playbooks or README do not show how to consume them
