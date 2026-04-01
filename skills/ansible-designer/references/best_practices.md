# Ansible Best Practices Reference

This file is the runtime baseline for every `ansible-designer` command. It summarizes the project rules and the upstream Ansible guidance that should shape generated or reviewed content.

## Scope

Use this reference for all content types:
- playbooks
- standalone roles
- roles inside collections
- collection examples
- `ansible.cfg` snippets embedded in docs or examples

Use the companion references for deeper details:
- `playbook.md`
- `role.md`
- `collection.md`
- `inventory.md`
- `testing.md`
- `security_vault.md`
- `plugins.md`

## Core Rules

### 1. Prefer FQCN everywhere

Use fully qualified collection names for all modules and plugins:

```yaml
ansible.builtin.template:
ansible.builtin.systemd:
ansible.posix.sysctl:
community.general.ini_file:
ansible.windows.win_service:
```

Do not generate short module names unless the user is explicitly maintaining legacy content.

### 2. Keep tasks idempotent

Generated tasks must describe desired state, not one-time shell procedures.

Preferred patterns:
- package/file/service/template modules with explicit `state`
- `changed_when: false` for read-only commands
- `creates:` / `removes:` / `changed_when:` / `failed_when:` when `command` or `shell` is unavoidable
- `check_mode`-safe validation tasks where possible

Avoid:
- `shell` for package installation
- `command` when a purpose-built module exists
- tasks that always report changed without justification

### 3. Tag every task

Every task should have:
- one component tag
- one action tag

Recommended action taxonomy:
- `install`
- `configure`
- `service`
- `validate`
- `security`
- `cleanup`

Example:

```yaml
tags:
  - nginx
  - configure
```

### 4. Handle secrets safely

Any task that uses passwords, tokens, vault material, API keys, private keys, or sensitive connection data must use `no_log: true`.

Use wrapper variables instead of hardcoding secrets:

```yaml
db_password: "{{ vault_db_password }}"
```

Do not place real secrets in examples.

### 5. Keep variable precedence clean

Use:
- `defaults/` for operator-tunable values
- `vars/` for internal constants and OS-specific mappings
- inventory or extra vars for environment values
- vault-encrypted vars for secrets

Do not put tunables such as ports, booleans, or feature flags in `vars/` unless there is a strong reason.

### 6. Prefer validation before and after change

Good generated content usually includes one or more of:
- preflight assertions
- OS/platform checks
- file/template validation
- service readiness checks
- API/port checks
- syntax-check or test guidance in the example README

### 7. Preserve compatibility with ansible-core 2.15+

All generated content must stay compatible with the repository baseline:
- use current 2.15-safe YAML and task patterns
- avoid deprecated syntax such as bare `include:`
- do not assume controller-only features newer than 2.15 unless marked optional

## Module Guidance

### Prefer these builtins first

| Use case | Preferred module |
| --- | --- |
| file copy | `ansible.builtin.copy` |
| templating | `ansible.builtin.template` |
| packages | `ansible.builtin.package`, `ansible.builtin.dnf`, `ansible.builtin.apt` |
| services | `ansible.builtin.systemd`, `ansible.builtin.service` |
| commands | `ansible.builtin.command` |
| shell fallback | `ansible.builtin.shell` |
| assertions | `ansible.builtin.assert` |
| failure | `ansible.builtin.fail` |
| includes | `ansible.builtin.include_tasks`, `ansible.builtin.import_tasks` |
| vars loading | `ansible.builtin.include_vars` |

### Common collection-backed modules

| Collection | Example modules |
| --- | --- |
| `ansible.posix` | `ansible.posix.sysctl`, `ansible.posix.seboolean`, `ansible.posix.firewalld` |
| `community.general` | `community.general.ini_file`, `community.general.pam_limits`, `community.general.timezone` |
| `ansible.windows` | `ansible.windows.win_service`, `ansible.windows.win_copy`, `ansible.windows.win_shell` |

If generated content depends on a non-builtin collection, mention that dependency in the example README or collection metadata.

## Task Design Patterns

### Assertions

Use assertions early for:
- minimum Ansible version
- supported operating systems
- required variables
- invalid combinations of options

### Blocks and rescue

Use `block` / `rescue` / `always` when:
- a sequence of changes should be treated as one operation
- cleanup or rollback messaging matters
- failures need a clearer operator explanation

Do not wrap every role in a block by default.

### Handlers

Prefer handlers for restart/reload behavior triggered by config changes.

Good pattern:
- config task notifies handler
- handler uses FQCN
- handler name is specific and reusable

### Validation commands

Template validation is preferred when the managed software supports it:

```yaml
validate: "nginx -t -c %s"
```

Read-only command checks should usually include:
- `changed_when: false`
- explicit `failed_when:` when stderr/stdout semantics are unusual

## Playbook Conventions

Use these defaults unless the repository already has a different standard:
- explicit `gather_facts: true` or `false`
- `become: true` only where needed
- `serial:` for rolling updates on stateful groups
- `delegate_to: localhost` for controller-side validation
- clear play names that describe outcome, not implementation

## Role Conventions

Role examples should usually include:
- `defaults/main.yml`
- `tasks/main.yml`
- `handlers/main.yml` when config changes can restart/reload a service
- `meta/main.yml`
- `tests/test.yml`

Add `vars/` only when there are internal constants, platform maps, or OS-specific values.

## Collection Conventions

Collection examples should usually include:
- `galaxy.yml`
- `meta/runtime.yml`
- `README.md`
- `plugins/` content with valid documentation blocks
- `roles/` or `playbooks/` showing real usage
- `tests/` directories when plugin examples are present

## Review Checklist

Use this checklist when reviewing generated or existing content:
- FQCNs are used consistently
- every task has tags
- secrets use `no_log: true`
- `command`/`shell` tasks are justified and guarded
- examples do not require undocumented prerequisites
- examples do not contain real secrets
- version statements remain compatible with `ansible-core 2.15+`
- role, collection, and config examples are internally consistent
