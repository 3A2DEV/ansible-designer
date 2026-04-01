# simple-playbook example

A complete site playbook demonstrating the ansible-designer pattern for a three-tier web application stack.

## Structure

```
simple-playbook/
├── site.yml                      # Main site playbook
├── inventory/
│   └── hosts.yml                 # YAML inventory: webservers, databases, loadbalancers
├── group_vars/
│   ├── all.yml                   # Variables for all hosts
│   └── webservers.yml            # nginx and app variables for webservers group
└── roles/
    ├── common/                   # lightweight baseline role for the example
    ├── nginx/                    # example web role
    └── postgres/                 # example database role
```

## What it demonstrates

- Multi-play site playbook with version assertion
- YAML inventory with group hierarchy (production: children: webservers, databases)
- `group_vars/` structure with vault variable references
- Role-based deployment with `tags:` for targeted runs
- `pre_tasks` / `post_tasks` pattern with validation
- `serial: 1` for rolling database updates
- `delegate_to: localhost` for health check tasks

## Running it

```bash
# Full deployment
ansible-playbook -i inventory/ site.yml

# Deploy nginx only
ansible-playbook -i inventory/ site.yml --tags nginx

# Check mode (dry run)
ansible-playbook -i inventory/ site.yml --check --diff

# Target a single host
ansible-playbook -i inventory/ site.yml --limit web01
```

## Validation

```bash
ansible-playbook -i inventory/hosts.yml site.yml --syntax-check
ansible-lint .
ansible-playbook -i inventory/hosts.yml site.yml --check --tags validate
```

## Included roles

This example now includes lightweight `common`, `nginx`, and `postgres` roles under `./roles/` so the playbook can be syntax-checked without relying on external content.
