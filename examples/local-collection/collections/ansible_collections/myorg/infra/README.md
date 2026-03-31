# myorg.infra Collection

Infrastructure automation collection providing baseline roles and a custom module for myorg environments.

## Included Content

### Roles

| Name | Description |
|------|-------------|
| `baseline` | Common baseline configuration for RHEL servers (sysctl, limits, packages) |

### Modules

| Name | Description |
|------|-------------|
| `sysctl_validate` | Validates sysctl settings against a policy file |

## Installation

```bash
# Install locally for development
ansible-galaxy collection install . --force

# Or reference via collections_path in ansible.cfg
```

## Requirements

- ansible-core >= 2.15
- Python >= 3.9

## Usage

```yaml
- name: Apply baseline configuration
  hosts: rhel_servers
  collections:
    - myorg.infra
  roles:
    - role: myorg.infra.baseline
```

## Development

```bash
# Lint
ansible-lint roles/ playbooks/

# Run sanity tests
cd collections/ansible_collections/myorg/infra
ansible-test sanity --docker default

# Run unit tests
ansible-test units --docker default
```
