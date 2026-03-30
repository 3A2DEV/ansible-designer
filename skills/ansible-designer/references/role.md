# Role Reference

This document is the authoritative runtime reference for role scaffolding and modification. All generated role content must conform to these patterns.

---

## 1. Standard Role Directory Structure

```
roles/<role_name>/
├── defaults/
│   └── main.yml          # User-overridable defaults (lowest precedence)
├── files/                # Static files to copy to managed hosts
├── handlers/
│   └── main.yml          # Event-driven tasks (restart, reload)
├── meta/
│   └── main.yml          # Role metadata, dependencies, platform matrix
├── tasks/
│   ├── main.yml          # Entry point — imports OS-specific or feature tasks
│   ├── RedHat.yml        # RHEL-specific tasks (if multi-OS)
│   ├── Solaris.yml       # Solaris-specific tasks (if multi-OS)
│   └── Windows.yml       # Windows-specific tasks (if multi-OS)
├── templates/            # Jinja2 templates (.j2 extension)
├── tests/
│   ├── inventory         # Test inventory (localhost)
│   └── test.yml          # Smoke-test playbook
└── vars/
    ├── main.yml          # Internal constants (high precedence)
    ├── RedHat.yml        # RHEL-specific vars (if multi-OS)
    ├── Solaris.yml       # Solaris-specific vars (if multi-OS)
    └── Windows.yml       # Windows-specific vars (if multi-OS)
```

---

## 2. tasks/main.yml Patterns

### Single-platform role

```yaml
---
# tasks/main.yml
# Role: <role_name>
# Description: <brief description>

- name: Verify minimum Ansible version
  ansible.builtin.assert:
    that: ansible_version.full is version('2.15', '>=')
    fail_msg: "This role requires ansible-core >= 2.15"
  tags:
    - <role_name>
    - validate

- name: Install <component> package
  ansible.builtin.package:
    name: "{{ <role_name>_package }}"
    state: present
  tags:
    - <role_name>
    - install

- name: Create configuration directory
  ansible.builtin.file:
    path: "{{ <role_name>_config_dir }}"
    state: directory
    owner: root
    group: root
    mode: "0755"
  tags:
    - <role_name>
    - configure

- name: Deploy <component> configuration
  ansible.builtin.template:
    src: <component>.conf.j2
    dest: "{{ <role_name>_config_dir }}/<component>.conf"
    owner: root
    group: root
    mode: "0644"
    validate: "<component> -t -c %s"
  notify: Restart <component>
  tags:
    - <role_name>
    - configure

- name: Ensure <component> service is started and enabled
  ansible.builtin.service:
    name: "{{ <role_name>_service_name }}"
    state: started
    enabled: true
  tags:
    - <role_name>
    - service

- name: Verify <component> is responding
  ansible.builtin.uri:
    url: "http://localhost:{{ <role_name>_port }}/"
    status_code: 200
  register: healthcheck
  retries: 3
  delay: 5
  until: healthcheck.status == 200
  tags:
    - <role_name>
    - validate
```

### Multi-OS role — tasks/main.yml

```yaml
---
# tasks/main.yml — Multi-OS entry point

- name: Load OS-specific variables
  ansible.builtin.include_vars:
    file: "{{ item }}"
  with_first_found:
    - "{{ ansible_os_family }}.yml"
    - "{{ ansible_distribution }}.yml"
    - "{{ ansible_distribution }}-{{ ansible_distribution_major_version }}.yml"
    - main.yml
  tags:
    - <role_name>
    - configure

- name: Include OS-specific tasks
  ansible.builtin.include_tasks:
    file: "{{ ansible_os_family }}.yml"
  when: ansible_os_family in ['RedHat', 'Solaris', 'Windows']
  tags:
    - <role_name>

- name: Deploy common configuration
  ansible.builtin.template:
    src: <component>.conf.j2
    dest: "{{ <role_name>_config_path }}"
    owner: "{{ <role_name>_owner }}"
    group: "{{ <role_name>_group }}"
    mode: "{{ <role_name>_config_mode }}"
  notify: Restart <component>
  tags:
    - <role_name>
    - configure

- name: Ensure <component> service is started and enabled
  ansible.builtin.service:
    name: "{{ <role_name>_service_name }}"
    state: started
    enabled: true
  when: ansible_os_family != 'Solaris'
  tags:
    - <role_name>
    - service
```

---

## 3. OS-Specific Variable Files

### vars/RedHat.yml

```yaml
---
# vars/RedHat.yml — RHEL / CentOS / Rocky Linux / AlmaLinux

<role_name>_package: <package-name>
<role_name>_service_name: <service-name>
<role_name>_config_dir: /etc/<component>
<role_name>_config_path: /etc/<component>/<component>.conf
<role_name>_log_dir: /var/log/<component>
<role_name>_owner: root
<role_name>_group: <component>
<role_name>_config_mode: "0640"
```

### vars/Solaris.yml

```yaml
---
# vars/Solaris.yml — Oracle Solaris 11

<role_name>_package: <SVR4-package-name>
<role_name>_smf_fmri: svc:/application/<component>:default
<role_name>_config_dir: /etc/<component>
<role_name>_config_path: /etc/<component>/<component>.conf
<role_name>_log_dir: /var/log/<component>
<role_name>_owner: root
<role_name>_group: sys
<role_name>_config_mode: "0640"
```

### vars/Windows.yml

```yaml
---
# vars/Windows.yml — Windows Server 2019 / 2022

<role_name>_package_id: "<MSI product name or chocolatey package>"
<role_name>_service_name: "<Windows service name>"
<role_name>_config_dir: 'C:\ProgramData\<component>'
<role_name>_config_path: 'C:\ProgramData\<component>\<component>.conf'
<role_name>_log_dir: 'C:\ProgramData\<component>\logs'
<role_name>_install_dir: 'C:\Program Files\<component>'
```

---

## 4. OS-Specific Task Files

### tasks/RedHat.yml

```yaml
---
# tasks/RedHat.yml — RHEL-specific package and service management

- name: Ensure required packages are installed (RHEL)
  ansible.builtin.dnf:
    name:
      - "{{ <role_name>_package }}"
      - "{{ <role_name>_package }}-utils"
    state: present
  tags:
    - <role_name>
    - install

- name: Configure SELinux boolean for <component>
  ansible.posix.seboolean:
    name: httpd_can_network_connect
    state: true
    persistent: true
  when: ansible_selinux.status == 'enabled'
  tags:
    - <role_name>
    - security

- name: Open firewall port for <component>
  ansible.posix.firewalld:
    port: "{{ <role_name>_port }}/tcp"
    permanent: true
    state: enabled
    immediate: true
  tags:
    - <role_name>
    - security
```

### tasks/Solaris.yml

```yaml
---
# tasks/Solaris.yml — Solaris SMF and package management

- name: Check if <component> package is installed (Solaris)
  ansible.builtin.command:
    cmd: pkginfo -q "{{ <role_name>_package }}"
  register: pkginfo_result
  changed_when: false
  failed_when: false
  tags:
    - <role_name>
    - install

- name: Install <component> package (Solaris)
  ansible.builtin.command:
    cmd: "pkgadd -d /var/spool/pkg -n {{ <role_name>_package }}"
  when: pkginfo_result.rc != 0
  tags:
    - <role_name>
    - install

- name: Enable <component> SMF service (Solaris)
  ansible.builtin.command:
    cmd: "svcadm enable -s {{ <role_name>_smf_fmri }}"
  register: svcadm_result
  changed_when: "'enabled' not in svcadm_result.stdout"
  tags:
    - <role_name>
    - service

- name: Verify <component> SMF service is online (Solaris)
  ansible.builtin.command:
    cmd: "svcs -H -o state {{ <role_name>_smf_fmri }}"
  register: svcs_state
  failed_when: svcs_state.stdout.strip() != 'online'
  changed_when: false
  tags:
    - <role_name>
    - validate
```

### tasks/Windows.yml

```yaml
---
# tasks/Windows.yml — Windows package and service management

- name: Install <component> on Windows
  ansible.windows.win_package:
    path: "{{ <role_name>_installer_url }}"
    product_id: "{{ <role_name>_product_id }}"
    arguments: /S /D="{{ <role_name>_install_dir }}"
    state: present
  tags:
    - <role_name>
    - install

- name: Create <component> configuration directory (Windows)
  ansible.windows.win_file:
    path: "{{ <role_name>_config_dir }}"
    state: directory
  tags:
    - <role_name>
    - configure

- name: Deploy <component> configuration (Windows)
  ansible.windows.win_template:
    src: <component>_windows.conf.j2
    dest: "{{ <role_name>_config_path }}"
  notify: Restart <component> Windows
  tags:
    - <role_name>
    - configure

- name: Ensure <component> Windows service is started and enabled
  ansible.windows.win_service:
    name: "{{ <role_name>_service_name }}"
    start_mode: auto
    state: started
  tags:
    - <role_name>
    - service
```

---

## 5. defaults/main.yml Pattern

```yaml
---
# defaults/main.yml — User-overridable defaults
# All variables here can be overridden in group_vars, host_vars, or playbook vars.

<role_name>_port: 80
<role_name>_enable_ssl: false
<role_name>_ssl_cert: /etc/ssl/certs/<component>.crt
<role_name>_ssl_key: /etc/ssl/private/<component>.key
<role_name>_max_connections: 100
<role_name>_timeout: 30
<role_name>_log_level: warn
<role_name>_enable_metrics: false

# Package version pin (set to "latest" to always get newest)
<role_name>_version: "present"
```

---

## 6. handlers/main.yml Pattern

```yaml
---
# handlers/main.yml

- name: Reload <component>
  ansible.builtin.service:
    name: "{{ <role_name>_service_name }}"
    state: reloaded
  listen: "reload <component>"

- name: Restart <component>
  ansible.builtin.service:
    name: "{{ <role_name>_service_name }}"
    state: restarted
  listen: "restart <component>"

- name: Reload systemd daemon
  ansible.builtin.systemd:
    daemon_reload: true
  listen: "reload systemd"

- name: Restart <component> Windows
  ansible.windows.win_service:
    name: "{{ <role_name>_service_name }}"
    state: restarted
  listen: "restart <component> windows"
```

---

## 7. meta/main.yml — Complete Format

```yaml
---
# meta/main.yml
galaxy_info:
  role_name: <role_name>
  author: platform-team
  description: "Installs and configures <component> on RHEL, Solaris, and Windows"
  company: "MyOrg"
  license: Apache-2.0
  min_ansible_version: "2.15"

  platforms:
    - name: EL
      versions:
        - "8"
        - "9"
    - name: Solaris
      versions:
        - "11.4"
    - name: Windows
      versions:
        - 2019
        - 2022

  galaxy_tags:
    - linux
    - solaris
    - windows
    - infrastructure

dependencies:
  # List role dependencies here.
  # - role: myorg.common
  #   vars:
  #     common_ntp_servers: "{{ <role_name>_ntp_servers }}"
  []
```

---

## 8. tests/ Pattern

### tests/inventory

```ini
localhost ansible_connection=local
```

### tests/test.yml

```yaml
---
# tests/test.yml — Smoke test for <role_name> role
- name: Test <role_name> role
  hosts: localhost
  become: true
  gather_facts: true

  roles:
    - role: <role_name>
      vars:
        <role_name>_port: 8080
```

---

## 9. Windows/WinRM Notes

- All Windows tasks must use `ansible.windows.*` or `community.windows.*` — never bare module names.
- WinRM connection must be declared at inventory level or group_vars:

```yaml
# group_vars/windows.yml
ansible_connection: winrm
ansible_winrm_transport: kerberos   # or ntlm, basic, certificate
ansible_port: 5986
ansible_winrm_scheme: https
ansible_winrm_server_cert_validation: ignore  # dev only
```

- `become` on Windows uses `runas` method:

```yaml
become: true
become_method: runas
become_user: Administrator
```

- `no_log: true` is mandatory on any task passing Windows passwords.

---

## 10. Solaris SMF Service Management

Ansible has no native Solaris SMF module. Use `ansible.builtin.command`:

```yaml
# Enable with wait for service to reach online state
- name: Enable SMF service
  ansible.builtin.command:
    cmd: svcadm enable -s "{{ smf_fmri }}"
  register: svcadm_enable
  changed_when: svcadm_enable.rc == 0
  tags: [<role_name>, service]

# Restart SMF service
- name: Restart SMF service
  ansible.builtin.command:
    cmd: svcadm restart "{{ smf_fmri }}"
  tags: [<role_name>, service]

# Check SMF state
- name: Get SMF service state
  ansible.builtin.command:
    cmd: "svcs -H -o state {{ smf_fmri }}"
  register: smf_state
  changed_when: false
  failed_when: smf_state.stdout.strip() not in ['online', 'degraded']
  tags: [<role_name>, validate]
```

SMF states: `online`, `offline`, `disabled`, `maintenance`, `degraded`, `legacy_run`
