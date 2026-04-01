# Role Reference

This reference describes how `ansible-designer` should generate, update, and review roles.

## Standard Role Layout

Minimum recommended layout:

```text
roles/<role_name>/
├── defaults/main.yml
├── handlers/main.yml
├── meta/main.yml
├── tasks/main.yml
├── templates/
├── tests/
│   ├── inventory
│   └── test.yml
└── vars/
```

Optional additions:
- `files/`
- OS-specific task files
- OS-specific var files
- `README.md`
- `meta/argument_specs.yml`

## Variable Placement

Use:
- `defaults/main.yml` for tunables
- `vars/main.yml` or OS-specific vars for internal constants
- `meta/argument_specs.yml` when the role interface needs explicit validation

Good defaults examples:
- ports
- booleans such as `*_manage_firewall`
- package versions
- feature flags

Good vars examples:
- service names
- config paths
- package names that differ by platform

## Single-Platform Role Pattern

```yaml
---
- name: Assert supported operating system
  ansible.builtin.assert:
    that:
      - ansible_os_family == 'RedHat'
    fail_msg: "This role currently supports RedHat-family systems only"
  tags:
    - nginx
    - validate

- name: Install package
  ansible.builtin.dnf:
    name: "{{ nginx_package }}"
    state: present
  tags:
    - nginx
    - install

- name: Render configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: "{{ nginx_config_path }}"
    mode: "0644"
    validate: "nginx -t -c %s"
  notify: Reload nginx
  tags:
    - nginx
    - configure

- name: Ensure service is enabled and started
  ansible.builtin.systemd:
    name: "{{ nginx_service_name }}"
    enabled: true
    state: started
  tags:
    - nginx
    - service
```

## Multi-Platform Role Pattern

Use an explicit dispatcher in `tasks/main.yml`:

```yaml
---
- name: Load platform-specific variables
  ansible.builtin.include_vars:
    file: "{{ lookup('ansible.builtin.first_found', params) }}"
  vars:
    params:
      files:
        - "{{ ansible_distribution }}-{{ ansible_distribution_major_version }}.yml"
        - "{{ ansible_distribution }}.yml"
        - "{{ ansible_os_family }}.yml"
        - "main.yml"
      paths:
        - "{{ role_path }}/vars"
  tags:
    - ntp
    - configure

- name: Include platform-specific tasks
  ansible.builtin.include_tasks: "{{ ansible_os_family }}.yml"
  when: ansible_os_family in ['RedHat', 'Solaris', 'Windows']
  tags:
    - ntp
    - configure

- name: Fail on unsupported platform
  ansible.builtin.fail:
    msg: "Unsupported platform: {{ ansible_os_family }}"
  when: ansible_os_family not in ['RedHat', 'Solaris', 'Windows']
  tags:
    - ntp
    - validate
```

Prefer `lookup('ansible.builtin.first_found', ...)` over older loop-based patterns when generating new content.

## Handlers

Handlers should:
- use FQCN
- have names that read well in output
- match `notify` calls exactly or use `listen`

Example:

```yaml
---
- name: Reload nginx
  ansible.builtin.systemd:
    name: "{{ nginx_service_name }}"
    state: reloaded
```

## `meta/main.yml`

Recommended fields:
- `role_name`
- `author`
- `description`
- `license`
- `min_ansible_version`
- `platforms`
- `galaxy_tags`
- `dependencies`

Keep the metadata realistic and aligned with the actual tasks.

## `meta/argument_specs.yml`

Use this when role inputs are non-trivial or enterprise-sensitive.

Example:

```yaml
---
argument_specs:
  main:
    short_description: Main entrypoint for nginx role
    options:
      nginx_port:
        type: int
        default: 80
      nginx_enable_ssl:
        type: bool
        default: false
```

## Testing

Role examples should include at least a smoke test playbook:
- `tests/test.yml`
- `tests/inventory`

The test playbook should:
- target `localhost` or a documented group
- set the minimum variables needed
- keep secrets out of the repo

## Review Heuristics

Flag these role problems:
- missing `tasks/main.yml`
- FQCN drift
- `defaults` and `vars` misused
- handlers defined but never notified
- `notify` names with no matching handler
- OS-specific files referenced but missing
- missing `tests/test.yml`
- missing `meta/main.yml` fields
