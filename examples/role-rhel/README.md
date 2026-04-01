# role-rhel example

A complete nginx role targeting RHEL 8/9 with SELinux and firewalld support.

## Structure

```
role-rhel/
└── roles/
    └── nginx/
        ├── defaults/main.yml       # User-overridable: port, SSL, worker processes
        ├── handlers/main.yml       # Reload nginx, Restart nginx
        ├── meta/main.yml           # Platforms: EL 8/9
        ├── tasks/main.yml          # Install, configure, SELinux, firewalld, service, validate
        ├── templates/
        │   └── nginx.conf.j2       # Jinja2 nginx configuration template
        ├── tests/
        │   ├── inventory           # localhost test inventory
        │   └── test.yml            # Smoke test playbook
        └── vars/main.yml           # Internal constants: package name, paths
```

## What it demonstrates

- FQCN usage throughout (`ansible.builtin.dnf`, `ansible.posix.seboolean`, etc.)
- Tags on every task (component: `nginx`, action: `install/configure/security/service/validate`)
- SELinux configuration via `ansible.posix.seboolean`
- Firewall management via `ansible.posix.firewalld`
- `ansible.builtin.systemd` for service management (not bare `service`)
- Template deployment with `validate:` parameter to test nginx config before applying
- Handler notification pattern (config change → `notify: Reload nginx`)
- Health check with `ansible.builtin.uri` and `retries`/`until`
- `defaults/` for operator-tunable values vs `vars/` for internal constants

## Using this role

```yaml
- name: Deploy nginx
  hosts: webservers
  become: true
  roles:
    - role: nginx
      vars:
        nginx_port: 80
        nginx_enable_ssl: false
```
