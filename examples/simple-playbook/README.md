# simple-playbook example

A complete site playbook demonstrating the ansible-designer pattern for a three-tier web application stack.

## Structure

```
simple-playbook/
├── site.yml                      # Main site playbook
├── inventory/
│   └── hosts.yml                 # YAML inventory: webservers, databases, loadbalancers
└── group_vars/
    ├── all.yml                   # Variables for all hosts
    └── webservers.yml            # nginx and app variables for webservers group
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

## Roles expected

This playbook references three roles that must exist in `./roles/` or be available via `roles_path`:
- `common` — baseline packages, NTP, timezone
- `nginx` — web server installation and configuration
- `postgres` — PostgreSQL installation and configuration
