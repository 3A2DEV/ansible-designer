# local-collection Example

Demonstrates developing and consuming a local Ansible collection (`myorg.infra`) without publishing to Galaxy.

## What this shows

- `collections_path = ./collections` in `ansible.cfg` to use a local collection
- FQCN usage: `myorg.infra.baseline` (role) and `myorg.infra.sysctl_validate` (module)
- Custom module skeleton (`plugins/modules/sysctl_validate.py`) with DOCUMENTATION, EXAMPLES, RETURN
- `pre_tasks` / `post_tasks` wrapping a role for validation gates

## Structure

```
local-collection/
├── ansible.cfg                          # sets collections_path = ./collections
├── site.yml                             # playbook using the local collection
├── inventory/
│   └── hosts.yml
├── files/
│   └── sysctl_policy.yml                # policy for sysctl_validate module
└── collections/
    └── ansible_collections/
        └── myorg/
            └── infra/
                ├── galaxy.yml
                ├── README.md
                ├── CHANGELOG.md
                ├── roles/
                │   └── baseline/        # RHEL baseline: packages, sysctl, limits
                │       ├── defaults/main.yml
                │       ├── tasks/main.yml
                │       └── meta/main.yml
                └── plugins/
                    └── modules/
                        └── sysctl_validate.py
```

## Usage

```bash
cd examples/local-collection

# Check syntax
ansible-playbook -i inventory/hosts.yml site.yml --syntax-check

# Run against real hosts
ansible-playbook -i inventory/hosts.yml site.yml

# Validate sysctl only
ansible-playbook -i inventory/hosts.yml site.yml -t validate

# Run sanity tests on the collection
cd collections/ansible_collections/myorg/infra
ansible-test sanity --docker default -v
```

## Requirements

- ansible-core >= 2.15
- `ansible.posix` collection (for `sysctl` and `pam_limits`)
- `community.general` collection (for `pam_limits`)
