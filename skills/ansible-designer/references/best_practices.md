# Ansible Best Practices Reference

This document is the authoritative runtime reference for ansible-designer. All generated content must conform to these rules.

---

## 1. Fully Qualified Collection Names (FQCN)

**Rule:** Every module reference in tasks, handlers, and role includes must use the FQCN. Never use short names.

### Core module mappings

| Short name (FORBIDDEN) | FQCN (REQUIRED) |
|------------------------|-----------------|
| `copy` | `ansible.builtin.copy` |
| `template` | `ansible.builtin.template` |
| `file` | `ansible.builtin.file` |
| `package` | `ansible.builtin.package` |
| `yum` | `ansible.builtin.yum` |
| `dnf` | `ansible.builtin.dnf` |
| `apt` | `ansible.builtin.apt` |
| `service` | `ansible.builtin.service` |
| `systemd` | `ansible.builtin.systemd` |
| `user` | `ansible.builtin.user` |
| `group` | `ansible.builtin.group` |
| `command` | `ansible.builtin.command` |
| `shell` | `ansible.builtin.shell` |
| `raw` | `ansible.builtin.raw` |
| `script` | `ansible.builtin.script` |
| `get_url` | `ansible.builtin.get_url` |
| `uri` | `ansible.builtin.uri` |
| `stat` | `ansible.builtin.stat` |
| `find` | `ansible.builtin.find` |
| `lineinfile` | `ansible.builtin.lineinfile` |
| `blockinfile` | `ansible.builtin.blockinfile` |
| `replace` | `ansible.builtin.replace` |
| `include_tasks` | `ansible.builtin.include_tasks` |
| `import_tasks` | `ansible.builtin.import_tasks` |
| `include_vars` | `ansible.builtin.include_vars` |
| `set_fact` | `ansible.builtin.set_fact` |
| `debug` | `ansible.builtin.debug` |
| `assert` | `ansible.builtin.assert` |
| `fail` | `ansible.builtin.fail` |
| `meta` | `ansible.builtin.meta` |
| `wait_for` | `ansible.builtin.wait_for` |
| `pause` | `ansible.builtin.pause` |
| `cron` | `ansible.builtin.cron` |
| `mount` | `ansible.builtin.mount` |
| `unarchive` | `ansible.builtin.unarchive` |
| `fetch` | `ansible.builtin.fetch` |
| `slurp` | `ansible.builtin.slurp` |
| `tempfile` | `ansible.builtin.tempfile` |
| `hostname` | `ansible.builtin.hostname` |
| `reboot` | `ansible.builtin.reboot` |
| `wait_for_connection` | `ansible.builtin.wait_for_connection` |
| `add_host` | `ansible.builtin.add_host` |
| `group_by` | `ansible.builtin.group_by` |
| `git` | `ansible.builtin.git` |
| `pip` | `ansible.builtin.pip` |
| `known_hosts` | `ansible.builtin.known_hosts` |
| `include_role` | `ansible.builtin.include_role` |
| `import_role` | `ansible.builtin.import_role` |
| `rpm_key` | `ansible.builtin.rpm_key` |
| `firewalld` | `ansible.posix.firewalld` |
| `synchronize` | `ansible.posix.synchronize` |
| `seboolean` | `ansible.posix.seboolean` |
| `selinux` | `ansible.posix.selinux` |
| `sysctl` | `ansible.posix.sysctl` |
| `authorized_key` | `ansible.posix.authorized_key` |
| `acl` | `ansible.posix.acl` |
| `patch` | `ansible.posix.patch` |
| `win_copy` | `ansible.windows.win_copy` |
| `win_command` | `ansible.windows.win_command` |
| `win_shell` | `ansible.windows.win_shell` |
| `win_service` | `ansible.windows.win_service` |
| `win_package` | `ansible.windows.win_package` |
| `win_file` | `ansible.windows.win_file` |
| `win_template` | `ansible.windows.win_template` |
| `win_user` | `ansible.windows.win_user` |
| `win_group` | `ansible.windows.win_group` |
| `win_regedit` | `ansible.windows.win_regedit` |
| `win_stat` | `ansible.windows.win_stat` |

### community.general — system and infrastructure modules

`community.general` must be installed separately (`ansible-galaxy collection install community.general`). These are among the most commonly needed modules in enterprise infrastructure work:

| Short name | FQCN |
|------------|------|
| `ini_file` | `community.general.ini_file` |
| `pam_limits` | `community.general.pam_limits` |
| `alternatives` | `community.general.alternatives` |
| `timezone` | `community.general.timezone` |
| `modprobe` | `community.general.modprobe` |
| `nmcli` | `community.general.nmcli` |
| `ufw` | `community.general.ufw` |
| `git_config` | `community.general.git_config` |
| `mail` | `community.general.mail` |
| `make` | `community.general.make` |
| `npm` | `community.general.npm` |
| `snap` | `community.general.snap` |
| `archive` | `community.general.archive` |
| `htpasswd` | `community.general.htpasswd` |
| `java_keystore` | `community.general.java_keystore` |
| `locale_gen` | `community.general.locale_gen` |
| `supervisorctl` | `community.general.supervisorctl` |
| `redhat_subscription` | `community.general.redhat_subscription` |
| `rhsm_repository` | `community.general.rhsm_repository` |
| `yum_versionlock` | `community.general.yum_versionlock` |

### Other third-party collections

| Module | FQCN |
|--------|------|
| `postgresql_db` | `community.postgresql.postgresql_db` |
| `mysql_db` | `community.mysql.mysql_db` |
| `docker_container` | `community.docker.docker_container` |
| `helm` | `kubernetes.core.helm` |
| `k8s` | `kubernetes.core.k8s` |
| `gcp_compute_instance` | `google.cloud.gcp_compute_instance` |
| `oci_compute_instance` | `oracle.oci.oci_compute_instance` |

---

## 2. Tag Taxonomy

**Rule:** Every task must have at least two tags: a **component name** and an **action category**.

### Mandatory tag format

```yaml
tags:
  - <component_name>    # e.g., nginx, postgres, ntp, firewall
  - <action_category>   # one of: install, configure, service, validate, cleanup
```

### Action categories

| Category | When to use |
|----------|-------------|
| `install` | Package installation, binary download |
| `configure` | Config file writes, template rendering, fact setup |
| `service` | Service start/stop/enable/disable/reload |
| `validate` | Assertions, health checks, connectivity tests |
| `cleanup` | Removing files, uninstalling, purging |
| `security` | Firewall rules, SELinux, file permissions, vault ops |
| `vault` | Vault-specific operations |
| `always` | Reserved for tasks that must run on every play regardless of tags |
| `never` | Reserved for tasks that should only run when explicitly tagged |

### Example

```yaml
- name: Install nginx package
  ansible.builtin.package:
    name: nginx
    state: present
  tags:
    - nginx
    - install

- name: Deploy nginx configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: "0644"
  notify: Reload nginx
  tags:
    - nginx
    - configure

- name: Ensure nginx is started and enabled
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true
  tags:
    - nginx
    - service
```

### Recommended additional tags

- Environment: `dev`, `ci`, `prod`
- Urgency: `hotfix`, `maintenance`
- AWX job template targeting: use consistent tag names that match AWX survey options

---

## 3. no_log Usage

**Rule:** `no_log: true` is mandatory on every task that handles secrets, passwords, tokens, keys, or credentials.

### When no_log is required

- Any task using `ansible.builtin.user` with `password:` parameter
- Any task using vault-encrypted variables as task arguments
- Any task running a command that includes a password in arguments
- Any task writing a secret to a file
- Any task setting a fact derived from a secret

### Pattern

```yaml
- name: Set database user password
  community.postgresql.postgresql_user:
    name: "{{ app_db_user }}"
    password: "{{ app_db_password }}"
    state: present
  no_log: true
  tags:
    - postgres
    - configure

- name: Create system user with password
  ansible.builtin.user:
    name: appuser
    password: "{{ vault_appuser_password | password_hash('sha512') }}"
    state: present
  no_log: true
  tags:
    - users
    - configure
```

### What no_log does NOT protect

- It suppresses task output in logs, but does not encrypt memory.
- Vault-encrypted variables should still use no_log when passed as arguments.
- Do not rely on no_log as the sole protection — also use vault encryption for variable values.

---

## 4. Idempotency Checklist

All generated tasks must be idempotent. Check these patterns:

### File operations
- Use `ansible.builtin.copy` or `ansible.builtin.template` (always idempotent).
- Use `ansible.builtin.file` with explicit `state:` (present/absent/directory/link).
- Avoid `ansible.builtin.shell` for file creation — use appropriate modules.

### Package management
- Always specify `state: present` (or `state: latest` when explicitly requested).
- Use `ansible.builtin.package` (OS-agnostic) unless OS-specific features are needed.

### Service management
- Always specify both `state:` and `enabled:`.

### Command/shell use
- When `ansible.builtin.command` or `ansible.builtin.shell` is unavoidable, use `creates:` or `removes:` to make it idempotent:

```yaml
- name: Initialize the database
  ansible.builtin.command:
    cmd: /usr/bin/myapp --init-db
    creates: /var/lib/myapp/.initialized
  tags:
    - myapp
    - configure
```

- Or use `changed_when:` and `failed_when:` to control idempotency:

```yaml
- name: Check if service is already configured
  ansible.builtin.command: myapp status
  register: myapp_status
  changed_when: false
  failed_when: myapp_status.rc not in [0, 1]
  tags:
    - myapp
    - validate
```

### User/group management
- Use `state: present` and specify all attributes explicitly.
- Avoid removing users unless that is the explicit intent.

---

## 5. Variable Precedence — defaults/ vs vars/

### defaults/main.yml

Use for variables that **operators should override** to customize the role behavior:
- Port numbers, package versions, file paths users may want to change
- Feature flags (enable_tls: false)
- Timeouts, retry counts
- Any variable documented in the role's README as "configurable"

```yaml
# defaults/main.yml — operator-overridable defaults
nginx_port: 80
nginx_worker_processes: "{{ ansible_processor_vcpus }}"
nginx_client_max_body_size: "10m"
nginx_log_dir: /var/log/nginx
nginx_enable_ssl: false
```

### vars/main.yml

Use for variables that are **internal constants** and should not normally be overridden:
- OS-specific package names (when not using OS var files)
- Fixed internal paths
- Version pins that require code changes to update safely

```yaml
# vars/main.yml — internal constants
_nginx_config_dir: /etc/nginx
_nginx_service_name: nginx
_nginx_user: nginx
```

### OS-specific vars (vars/RedHat.yml, vars/Solaris.yml, vars/Windows.yml)

Use for platform-specific values loaded via `include_vars` + `with_first_found`:
- Package names that differ by OS
- Service names that differ by OS
- Config file paths that differ by OS

---

## 6. Handler Best Practices

### Naming

Handler names must be descriptive and unique across the entire role:

```yaml
# handlers/main.yml
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
  listen: reload nginx

- name: Restart nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
  listen: restart nginx

- name: Reload systemd daemon
  ansible.builtin.systemd:
    daemon_reload: true
  listen: reload systemd
```

### Triggering

Use `notify:` on the task that changes configuration. Multiple tasks can notify the same handler:

```yaml
- name: Deploy nginx config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: Reload nginx
  tags: [nginx, configure]
```

### Handler ordering

Handlers run in the order they are defined in `handlers/main.yml`, not in the order they are notified. If reload must happen before restart, order them accordingly.

---

## 7. Vault Usage Patterns

### Variable naming convention

Prefix vault-encrypted variables with `vault_`:

```yaml
# group_vars/all/vault.yml (encrypted)
vault_db_password: "supersecretpassword"
vault_api_token: "tok-abc123"

# group_vars/all/vars.yml (plaintext)
db_password: "{{ vault_db_password }}"
api_token: "{{ vault_api_token }}"
```

### Encrypt only values, not entire files

Prefer `ansible-vault encrypt_string` over encrypting entire var files. This keeps diffs readable.

### Multiple vault identities

```ini
# ansible.cfg
vault_identity_list = dev@~/.vault_pass_dev, prod@~/.vault_pass_prod
```

Usage:
```bash
ansible-vault encrypt_string --vault-id prod@~/.vault_pass_prod 'my_secret' --name 'vault_api_token'
```

### never expose vault variables directly

Always use an intermediate non-vault variable:
```yaml
# WRONG
password: "{{ vault_db_password }}"

# CORRECT
password: "{{ db_password }}"    # db_password references vault_db_password
```

---

## 8. AWX-Specific Considerations

### Survey variables

AWX survey variables are passed as `extra_vars` and have the highest variable precedence. Design roles to accept them cleanly:

```yaml
# defaults/main.yml
app_version: "1.0.0"          # overridable via AWX survey
deploy_environment: "dev"      # overridable via AWX survey
```

### Credentials

AWX injects credentials as environment variables or files. Reference them via environment variables when possible:

```yaml
- name: Authenticate to registry
  ansible.builtin.command:
    cmd: "docker login -u {{ registry_user }} -p {{ registry_password }} {{ registry_url }}"
  no_log: true
  environment:
    REGISTRY_PASSWORD: "{{ registry_password }}"
  tags: [registry, configure]
```

### Callback plugins for AWX

AWX has its own callback. Do not enable `profile_tasks` or `timer` in AWX profiles as they can interfere:

```ini
# AWX ansible.cfg — no profile_tasks
callbacks_enabled =
```

### Fact caching in AWX

AWX can use Redis for fact caching across job runs:

```ini
fact_caching = redis
fact_caching_connection = redis://localhost:6379/0
fact_caching_timeout = 86400
```

---

## 9. Platform Notes

### RHEL / CentOS / Rocky Linux

- Use `ansible.builtin.dnf` for RHEL 8+ (not `ansible.builtin.yum`)
- Use `ansible.posix.firewalld` for firewall management
- Use `ansible.posix.selinux` and `ansible.posix.seboolean` for SELinux
- Use `ansible.builtin.systemd` for service management (not `ansible.builtin.service` alone)
- Check `ansible_os_family == 'RedHat'` and `ansible_distribution_major_version`

### Solaris

- Package management: `ansible.builtin.command` calling `pkgadd`/`pkgrm` (no Ansible module for SVR4 packages)
- Service management: `ansible.builtin.command` calling `svcadm enable/disable/restart`
- SMF service states: `online`, `offline`, `disabled`, `maintenance`
- Check `ansible_os_family == 'Solaris'` or `ansible_distribution == 'Solaris'`
- `become` on Solaris uses `pfexec` or `sudo` — verify the target system's sudo configuration

```yaml
- name: Enable NTP service on Solaris
  ansible.builtin.command:
    cmd: svcadm enable svc:/network/ntp:default
  register: svcadm_result
  changed_when: "'svc:/network/ntp' not in svcadm_result.stdout"
  tags: [ntp, service]
```

### Windows / WinRM

- All Windows tasks use `ansible.windows.*` or `community.windows.*` collections
- Connection: `ansible_connection: winrm`, `ansible_winrm_transport: kerberos` or `ntlm`
- Use `ansible.windows.win_service` (not `ansible.builtin.service`)
- Use `ansible.windows.win_package` for MSI/EXE installation
- Use `ansible.windows.win_regedit` for registry management
- no_log is equally important on Windows for password-handling tasks

```yaml
- name: Install IIS feature
  ansible.windows.win_feature:
    name: Web-Server
    state: present
  tags: [iis, install]

- name: Configure WinRM HTTPS listener
  ansible.windows.win_shell: |
    $selector = 'winrm/config/Listener?Address=*+Transport=HTTPS'
    winrm set $selector '@{Enabled="true"}'
  no_log: true
  tags: [winrm, configure]
```
