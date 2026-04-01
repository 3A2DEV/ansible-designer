# Inventory Reference

This reference covers static inventory, inventory directories, variable placement, and safe example patterns.

## Preferred Static Inventory Format

Prefer YAML inventory for generated examples unless the user explicitly wants INI.

Example:

```yaml
---
all:
  vars:
    ansible_user: ansible

  children:
    webservers:
      hosts:
        web01:
          ansible_host: 192.0.2.10
    databases:
      hosts:
        db01:
          ansible_host: 192.0.2.20
```

## Inventory Directory Pattern

Use this shape for richer examples:

```text
inventory/
├── hosts.yml
├── group_vars/
│   ├── all.yml
│   └── webservers.yml
└── host_vars/
    └── web01.yml
```

If vault separation matters, prefer directories:

```text
group_vars/
└── all/
    ├── main.yml
    └── vault.example.yml
```

Do not store real encrypted vault data in repository examples unless the repository explicitly wants committed sample vault files.

## Variable Placement

Use:
- inventory for host/group topology
- `group_vars` for group defaults
- `host_vars` for host overrides
- wrapper vars for secrets

Example:

```yaml
app_db_password: "{{ vault_app_db_password }}"
```

## Dynamic Inventory Guidance

Prefer inventory plugins over ad-hoc scripts in modern guidance.

If documenting dynamic inventory:
- explain which plugin is assumed
- show the plugin config file location
- keep credentials external
- mention that the example is controller-side content

## Windows and Non-Linux Targets

Document connection variables explicitly when examples include Windows:
- `ansible_connection`
- `ansible_port`
- `ansible_winrm_transport`
- `ansible_winrm_scheme`

## Validation Expectations

Inventory examples should make it clear how the user validates them:
- `ansible-inventory -i inventory/hosts.yml --graph`
- `ansible-inventory -i inventory/hosts.yml --list`

## Review Heuristics

Flag:
- hardcoded secrets in inventory
- examples that use `group_vars` or `host_vars` paths inconsistently
- inventory examples that omit required connection details for Windows
- references to groups or hosts that do not exist in the example tree
