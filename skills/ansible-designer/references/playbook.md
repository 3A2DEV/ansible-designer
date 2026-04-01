# Playbook Reference

This reference defines the default shape for generated or updated playbooks.

## Design Goals

Playbooks produced by `ansible-designer` should be:
- readable
- explicit about scope and prerequisites
- safe to run in check mode when practical
- easy to validate with `ansible-lint` and `ansible-playbook --syntax-check`

## Header Pattern

Use a compact header for standalone examples:

```yaml
---
# =============================================================================
# Playbook: site.yml
# Description: Apply the baseline, web, and database roles for the example site.
# Usage:
#   ansible-playbook -i inventory/hosts.yml site.yml
# =============================================================================
```

## Common Playbook Structure

Use this ordering unless the repository already has another standard:

1. preflight play on `localhost` if version or input validation matters
2. one or more configuration plays
3. post-change validation tasks

## Baseline Template

```yaml
---
- name: Verify controller prerequisites
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Assert supported ansible-core version
      ansible.builtin.assert:
        that: ansible_version.full is version('2.15', '>=')
        fail_msg: "This playbook requires ansible-core 2.15 or newer"
      tags:
        - always

- name: Apply role to target hosts
  hosts: webservers
  become: true
  gather_facts: true

  pre_tasks:
    - name: Validate required variables
      ansible.builtin.assert:
        that:
          - app_environment is defined
        fail_msg: "Set app_environment before running this playbook"
      tags:
        - app
        - validate

  roles:
    - role: myorg.infra.web
      tags:
        - web

  post_tasks:
    - name: Verify application port is reachable
      ansible.builtin.wait_for:
        host: "{{ ansible_host | default(inventory_hostname) }}"
        port: "{{ web_listen_port }}"
        timeout: 30
      delegate_to: localhost
      tags:
        - web
        - validate
```

## Playbook Types

### Site playbook

Use when:
- several host groups are coordinated
- the playbook is the main entrypoint
- rolling updates or ordering matter

Recommended features:
- named plays per component
- `serial:` on stateful services
- shared inventory-driven vars
- validation after each major phase

### Component playbook

Use when:
- one role or one subsystem is targeted
- operators need a narrow entrypoint
- examples should stay small and runnable

### Controller-ready playbook

Use when:
- the playbook is meant for AWX or Automation Controller
- inventory, credentials, and extra vars are externalized

Recommended features:
- documented required survey or extra vars
- no embedded secrets
- controller-friendly callbacks or logging assumptions kept out of the play itself

## Variable Guidance

Prefer:
- inventory or `group_vars` for environment data
- role defaults for tunables
- extra vars for release-specific values

Avoid:
- hardcoded IPs unless the example is explicitly static-inventory focused
- embedding vault data directly in the playbook

## Validation Patterns

Choose one or more validation tasks based on the component:
- `ansible.builtin.wait_for` for ports
- `ansible.builtin.uri` for HTTP endpoints
- `ansible.builtin.command` with `changed_when: false` for read-only service checks
- `ansible.builtin.assert` for derived facts or registered results

Example:

```yaml
- name: Check service status
  ansible.builtin.command:
    cmd: systemctl is-active nginx
  register: nginx_status
  changed_when: false
  failed_when: nginx_status.stdout.strip() != 'active'
  tags:
    - nginx
    - validate
```

## Error Handling

Use `block` / `rescue` when a group of tasks should fail with clearer operator feedback:

```yaml
- name: Apply application deployment
  block:
    - name: Render application config
      ansible.builtin.template:
        src: app.conf.j2
        dest: /etc/myapp/app.conf
        mode: "0640"
  rescue:
    - name: Report deployment failure
      ansible.builtin.fail:
        msg: "Application deployment failed before service validation"
```

Do not add `block` wrappers to every play by default.

## Inventory Expectations

Generated examples should assume one of:
- inventory directory next to the playbook
- inventory file explicitly passed on the command line

If the example depends on `group_vars/` or `host_vars/`, keep those files in the same example tree.

## Review Heuristics

Flag these in playbooks:
- short module names
- missing `gather_facts`
- untagged tasks
- `command`/`shell` without idempotency guard
- controller-side checks run on remote hosts by mistake
- missing validation for service-oriented examples
