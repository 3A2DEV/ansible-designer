# Playbook Reference

This document is the authoritative runtime reference for playbook generation. All generated playbooks must conform to these patterns.

---

## 1. Playbook Header Format

Every playbook must begin with a YAML comment header:

```yaml
---
# =============================================================================
# Playbook: <filename>
# Author:   <author name / team name>
# Version:  1.0.0
# Description: <one or two sentences describing what this playbook does>
# Usage:
#   ansible-playbook -i inventory/ <filename> [--tags <tag>] [--limit <host>]
# =============================================================================
```

---

## 2. Template 1 — Site Playbook

Orchestrates the full deployment across all component groups.

```yaml
---
# =============================================================================
# Playbook: site.yml
# Author:   Platform Team
# Version:  1.0.0
# Description: Full site deployment — applies all component roles to their
#              respective host groups. Run with --tags to target a component.
# Usage:
#   ansible-playbook -i inventory/ site.yml
#   ansible-playbook -i inventory/ site.yml --tags nginx
#   ansible-playbook -i inventory/ site.yml --limit web01
# =============================================================================

- name: Verify Ansible version
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Assert minimum Ansible version
      ansible.builtin.assert:
        that: ansible_version.full is version('2.15', '>=')
        fail_msg: "Requires ansible-core >= 2.15. Found: {{ ansible_version.full }}"
      tags: [always]

- name: Apply common baseline to all hosts
  hosts: all
  become: true
  gather_facts: true
  vars:
    # Override with -e or group_vars
    deploy_environment: "{{ lookup('env', 'DEPLOY_ENV') | default('production', true) }}"
  pre_tasks:
    - name: Wait for host to be reachable
      ansible.builtin.wait_for_connection:
        timeout: 60
      tags: [always]

    - name: Gather minimal facts
      ansible.builtin.setup:
        gather_subset:
          - min
          - hardware
      tags: [always]
  roles:
    - role: myorg.infra.common
      tags: [common]
  post_tasks:
    - name: Record deployment timestamp
      ansible.builtin.set_fact:
        deployment_timestamp: "{{ ansible_date_time.iso8601 }}"
      tags: [always]

- name: Configure web servers
  hosts: webservers
  become: true
  gather_facts: true
  roles:
    - role: myorg.infra.nginx
      tags: [nginx]
    - role: myorg.infra.app
      tags: [app]

- name: Configure database servers
  hosts: databases
  become: true
  gather_facts: true
  serial: 1                     # roll databases one at a time
  roles:
    - role: myorg.infra.postgres
      tags: [postgres]

- name: Post-deployment validation
  hosts: all
  gather_facts: false
  tasks:
    - name: Verify all services are responding
      ansible.builtin.uri:
        url: "http://{{ ansible_host }}:{{ service_port | default(80) }}/"
        status_code: [200, 301, 302]
      delegate_to: localhost
      tags: [validate]
```

---

## 3. Template 2 — Component Playbook

Single-component deployment targeting a specific host group.

```yaml
---
# =============================================================================
# Playbook: deploy-nginx.yml
# Author:   Platform Team
# Version:  1.0.0
# Description: Deploy and configure nginx on webservers group.
# Usage:
#   ansible-playbook -i inventory/ deploy-nginx.yml
#   ansible-playbook -i inventory/ deploy-nginx.yml --check
# =============================================================================

- name: Deploy nginx web server
  hosts: webservers
  become: true
  gather_facts: true
  vars:
    nginx_port: "{{ deploy_nginx_port | default(80) }}"
    nginx_enable_ssl: "{{ deploy_nginx_ssl | default(false) }}"

  pre_tasks:
    - name: Verify target OS is supported
      ansible.builtin.assert:
        that:
          - ansible_os_family in ['RedHat', 'Debian', 'Solaris', 'Windows']
        fail_msg: "Unsupported OS family: {{ ansible_os_family }}"
      tags: [always]

    - name: Check available disk space
      ansible.builtin.assert:
        that: item.size_available > 524288000   # 500 MB
        fail_msg: "Insufficient disk space on {{ item.mount }}"
      loop: "{{ ansible_mounts | selectattr('mount', 'eq', '/') | list }}"
      tags: [validate]

  roles:
    - role: myorg.infra.nginx
      vars:
        nginx_port: "{{ nginx_port }}"
        nginx_enable_ssl: "{{ nginx_enable_ssl }}"

  post_tasks:
    - name: Confirm nginx is listening
      ansible.builtin.wait_for:
        host: "{{ ansible_host }}"
        port: "{{ nginx_port }}"
        timeout: 30
      delegate_to: localhost
      tags: [validate]

    - name: Print deployment summary
      ansible.builtin.debug:
        msg: "nginx deployed on {{ inventory_hostname }} — port {{ nginx_port }}"
      tags: [validate]
```

---

## 4. Template 3 — AWX-Ready Playbook

Designed for execution from AWX/Automation Controller with survey variables and credential injection.

```yaml
---
# =============================================================================
# Playbook: awx-deploy.yml
# Author:   Platform Team
# Version:  1.0.0
# Description: AWX-ready deployment playbook. Variables are injected via
#              AWX surveys, credentials, and extra_vars.
# AWX Job Template:
#   - Inventory: Dynamic (GCP/OCI plugin)
#   - Credentials: Machine credential, Vault credential
#   - Survey variables: app_version, deploy_environment, target_limit
# =============================================================================

- name: AWX deployment — {{ deploy_environment | default('production') }}
  hosts: "{{ target_limit | default('all') }}"
  become: true
  gather_facts: true

  vars:
    # These variables are expected from AWX surveys or extra_vars:
    # app_version: "1.0.0"
    # deploy_environment: "production"
    # target_limit: "webservers"
    # vault_db_password is injected by AWX Vault credential

    # Derived variables
    app_env: "{{ deploy_environment | default('production') }}"
    deployment_id: "{{ tower_job_id | default(ansible_date_time.epoch) }}"

  pre_tasks:
    - name: Log deployment start
      ansible.builtin.debug:
        msg: >
          Starting deployment:
          env={{ app_env }},
          version={{ app_version | default('not set') }},
          job_id={{ deployment_id }}
      tags: [always]

    - name: Fail if required AWX variables are missing
      ansible.builtin.assert:
        that:
          - app_version is defined
          - deploy_environment is defined
        fail_msg: >
          Required survey variables missing.
          Set app_version and deploy_environment in the AWX job template survey.
      tags: [always]

  roles:
    - role: myorg.infra.app
      vars:
        app_release_version: "{{ app_version }}"
        app_environment: "{{ app_env }}"
      tags: [app]

  post_tasks:
    - name: Notify deployment completed
      ansible.builtin.uri:
        url: "{{ webhook_url | default('http://localhost/noop') }}"
        method: POST
        body_format: json
        body:
          status: success
          version: "{{ app_version }}"
          environment: "{{ app_env }}"
          job_id: "{{ deployment_id }}"
        headers:
          Authorization: "Bearer {{ webhook_token | default('') }}"
      no_log: true
      when: webhook_url is defined
      tags: [notify]
```

---

## 5. include_tasks vs import_tasks

| Feature | `ansible.builtin.include_tasks` | `ansible.builtin.import_tasks` |
|---------|--------------------------------|-------------------------------|
| Processing | Dynamic (at runtime) | Static (at parse time) |
| Variable support | Full — can use variables in `file:` | Limited — file must be a static path |
| Tags | Tags on `include_tasks` do NOT pass through | Tags on `import_tasks` DO pass through |
| When/loops | Supports `when:` and `loop:` | `loop:` not supported |
| Error location | Shown at runtime | Shown at parse time |
| Use when | You need dynamic file selection | You want static analysis, tag pass-through |

### include_tasks example (dynamic, OS-specific)

```yaml
- name: Include OS-specific setup tasks
  ansible.builtin.include_tasks:
    file: "setup_{{ ansible_os_family | lower }}.yml"
  tags: [component, configure]
```

### import_tasks example (static, always included)

```yaml
- name: Import common validation tasks
  ansible.builtin.import_tasks:
    file: validate.yml
# Tags applied to validate.yml tasks will be inherited
```

---

## 6. Error Handling — block/rescue/always

```yaml
- name: Deploy application with rollback
  block:
    - name: Stop application service
      ansible.builtin.service:
        name: "{{ app_service }}"
        state: stopped
      tags: [app, service]

    - name: Deploy new application version
      ansible.builtin.unarchive:
        src: "{{ app_archive_url }}"
        dest: "{{ app_install_dir }}"
        remote_src: true
      tags: [app, install]

    - name: Start application service
      ansible.builtin.service:
        name: "{{ app_service }}"
        state: started
      tags: [app, service]

  rescue:
    - name: Log deployment failure
      ansible.builtin.debug:
        msg: "Deployment failed: {{ ansible_failed_task.name }}"
      tags: [always]

    - name: Rollback — restore previous version
      ansible.builtin.command:
        cmd: "{{ app_install_dir }}/rollback.sh"
        creates: "{{ app_install_dir }}/version_{{ app_previous_version }}"
      tags: [app, install]

    - name: Start service with previous version
      ansible.builtin.service:
        name: "{{ app_service }}"
        state: started
      tags: [app, service]

    - name: Fail the play after rollback
      ansible.builtin.fail:
        msg: "Deployment failed and was rolled back to previous version."
      tags: [always]

  always:
    - name: Record deployment result
      ansible.builtin.set_fact:
        deployment_result: "{{ 'success' if not ansible_failed_task is defined else 'failed' }}"
      tags: [always]
```

---

## 7. vars Block Patterns

### Inline vars (playbook-level)

```yaml
- name: Deploy application
  hosts: webservers
  vars:
    app_port: 8080
    app_log_dir: /var/log/myapp
    app_db_url: "postgresql://{{ db_host }}:{{ db_port }}/{{ db_name }}"
    # Reference vault variable via wrapper variable
    app_db_password: "{{ vault_app_db_password }}"
```

### vars_files (load from file)

```yaml
- name: Deploy application
  hosts: webservers
  vars_files:
    - vars/common.yml
    - "vars/{{ deploy_environment }}.yml"
    - vars/vault.yml                        # ansible-vault encrypted
```

### Prompting (interactive, not suitable for AWX)

```yaml
- name: Interactively prompted deployment
  hosts: webservers
  vars_prompt:
    - name: app_version
      prompt: "Enter version to deploy"
      default: "1.0.0"
      private: false
    - name: deploy_confirm
      prompt: "Type YES to confirm deployment"
      private: false
```

---

## 8. roles vs tasks vs import_playbook

| Pattern | When to use |
|---------|------------|
| `roles:` | Reusable, self-contained component configuration |
| `tasks:` | One-off operations specific to this playbook |
| `ansible.builtin.import_playbook:` | Composing a site.yml from component playbooks |

### import_playbook composition

```yaml
---
# site.yml — composed from individual component playbooks
- ansible.builtin.import_playbook: playbooks/baseline.yml
- ansible.builtin.import_playbook: playbooks/deploy-nginx.yml
- ansible.builtin.import_playbook: playbooks/deploy-postgres.yml
- ansible.builtin.import_playbook: playbooks/deploy-app.yml
- ansible.builtin.import_playbook: playbooks/validate.yml
```
