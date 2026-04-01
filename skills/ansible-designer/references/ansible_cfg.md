# ansible.cfg Reference

This document provides three complete, annotated ansible.cfg profiles and documents all relevant sections for ansible-designer's new-conf, review-conf, and update-conf commands.

---

## Profile 1: dev — Development Environment

```ini
# =============================================================================
# ansible.cfg — Development profile
# Use: local VMs, Vagrant, developer workstations
# Security: permissive (NOT for production)
# =============================================================================

[defaults]
# Inventory location
inventory             = ./inventory

# Default connection user
remote_user           = ansible

# SSH key for authentication
private_key_file      = ~/.ssh/id_rsa

# SECURITY NOTE: Disable ONLY in dev/local environments where VM keys change
# frequently. Enable for staging and production.
host_key_checking     = False

# Number of parallel forks (start low, tune up based on controller RAM: ~100MB/fork)
forks                 = 10

# SSH timeout in seconds
timeout               = 30

# Log file (useful for debugging; rotate regularly)
log_path              = ./ansible.log

# Roles search path (colon-separated, in order)
roles_path            = ./roles:~/.ansible/roles

# Collections search path
collections_paths     = ./collections:~/.ansible/collections

# Retry files are noisy; disable in dev
retry_files_enabled   = False

# Human-readable output
stdout_callback       = yaml

# Active callback plugins
callbacks_enabled     = profile_tasks, timer

# Fact gathering: implicit (default), explicit, or smart
gathering             = smart

# Fact cache backend (useful even in dev to speed up reruns)
fact_caching          = jsonfile
fact_caching_connection = /tmp/ansible_facts_cache
fact_caching_timeout  = 3600

# Show diffs for file changes (very useful in dev)
[diff]
always                = True
context               = 5

[privilege_escalation]
become                = True
become_method         = sudo
become_user           = root
become_ask_pass       = False

[ssh_connection]
# Pipelining speeds up execution (requires requiretty disabled in /etc/sudoers)
pipelining            = True

# SSH ControlMaster for connection reuse (speeds up multi-task plays)
control_path          = /tmp/ansible-ssh-%%h-%%p-%%r
control_master        = auto
control_persist       = 60s

# Extra SSH arguments (add -v for verbose SSH debugging)
ssh_args              = -C -o ControlMaster=auto -o ControlPersist=60s

[persistent_connection]
connect_timeout       = 30
command_timeout       = 30

[colors]
highlight             = white
verbose               = blue
warn                  = bright purple
error                 = red
debug                 = dark gray
deprecate             = purple
skip                  = cyan
unreachable           = red
ok                    = green
changed               = yellow
```

---

## Profile 2: CI — Continuous Integration

```ini
# =============================================================================
# ansible.cfg — CI profile
# Use: GitHub Actions, GitLab CI, Jenkins, ephemeral runners
# Security: strict validation, minimal output, no host key checking
#           (justified: CI runners are ephemeral and have no known_hosts)
# =============================================================================

[defaults]
# Inventory location (often overridden by CI job via ANSIBLE_INVENTORY env var)
inventory             = ./inventory

# Use a dedicated CI service account
remote_user           = ci-ansible

# Key injected by CI credential system
private_key_file      = ~/.ssh/ci_deploy_key

# SECURITY NOTE: host_key_checking=False is acceptable in CI because:
# 1. Ephemeral runners have no persistent known_hosts
# 2. Target hosts are verified via other controls (cloud metadata, VPC isolation)
# In production-targeting CI pipelines, use strict=True with pre-seeded known_hosts.
host_key_checking     = False

# Higher forks for CI speed (runners typically have more RAM than laptops)
forks                 = 20

# Short timeout — CI jobs must fail fast
timeout               = 15

# Log to stdout for CI log capture (no log_path in ephemeral runners)
# log_path            =                   # intentionally empty

# Roles and collections (populated by ansible-galaxy install in CI pipeline)
roles_path            = ./roles:~/.ansible/roles
collections_paths     = ./collections:~/.ansible/collections

# No retry files in CI
retry_files_enabled   = False

# Minimal, machine-parseable output
stdout_callback       = json

# No profiling callbacks in CI (reduces noise)
callbacks_enabled     =

# Always gather facts (no cache in stateless CI)
gathering             = implicit
fact_caching          = memory

# Fail on undefined variables — catch errors early
error_on_undefined_vars = True

[diff]
always                = True
context               = 3

[privilege_escalation]
become                = True
become_method         = sudo
become_user           = root
become_ask_pass       = False

[ssh_connection]
pipelining            = True
control_path          = /tmp/ansible-ci-%%h-%%p-%%r
control_master        = auto
control_persist       = 30s
# Strict host key checking override already handled by host_key_checking above
ssh_args              = -C -o ControlMaster=auto -o ControlPersist=30s -o BatchMode=yes

[persistent_connection]
connect_timeout       = 15
command_timeout       = 60
```

---

## Profile 3: AWX — Automation Controller / AWX

```ini
# =============================================================================
# ansible.cfg — AWX / Automation Controller profile
# Use: Red Hat Ansible Automation Platform, AWX
# Notes:
#   - AWX injects its own callback plugin automatically (do not add it manually)
#   - Credentials are injected via AWX credential types
#   - Fact caching via Redis enables sharing facts across job templates
#   - Vault passwords come from AWX vault credentials (not vault_password_file)
# =============================================================================

[defaults]
# AWX manages inventory via its inventory sources — this is a fallback only
inventory             = ./inventory

# AWX injects the remote_user from the Machine credential
remote_user           = ansible

# AWX manages SSH keys via Machine credentials
# private_key_file    =                   # set by AWX

host_key_checking     = True

# Forks tuned for AWX worker capacity (AWX operator sets global max)
forks                 = 25

timeout               = 30

# Log path: AWX captures stdout/stderr directly — log_path can cause duplication
# log_path            =                   # intentionally empty

roles_path            = ./roles:~/.ansible/roles
collections_paths     = ./collections:~/.ansible/collections

retry_files_enabled   = False

# AWX has its own output renderer — use minimal callback
stdout_callback       = minimal

# IMPORTANT: Do NOT add profile_tasks or timer in AWX profiles.
# AWX injects its own callback (awx_display) automatically.
# Adding extra callbacks can cause output parsing errors.
callbacks_enabled     =

# Fact gathering: smart (use cache when available)
gathering             = smart

# Redis fact caching — allows fact sharing across AWX job templates
# AWX Redis instance: configure redis via AWX settings if using external Redis
fact_caching          = redis
fact_caching_connection = redis://localhost:6379/0
fact_caching_timeout  = 86400

# Alternatively, use jsonfile for simpler setups:
# fact_caching          = jsonfile
# fact_caching_connection = /tmp/ansible_facts_cache
# fact_caching_timeout  = 86400

# MongoDB fact caching (enterprise option):
# fact_caching          = mongodb
# fact_caching_connection = mongodb://localhost:27017/ansible_facts

[diff]
always                = False             # AWX diffs can generate large job output
context               = 3

[privilege_escalation]
become                = True
become_method         = sudo
become_user           = root
become_ask_pass       = False             # AWX injects become password via credentials

[ssh_connection]
pipelining            = True
control_path          = /tmp/awx-%%h-%%p-%%r
control_master        = auto
control_persist       = 60s
ssh_args              = -C -o ControlMaster=auto -o ControlPersist=60s

[persistent_connection]
connect_timeout       = 30
command_timeout       = 120              # AWX jobs may have longer-running commands
```

---

## Vault Configuration

### vault_password_file (single vault password)

```ini
[defaults]
# Path to file containing the vault password (no newline at end)
# File must be chmod 600 and owned by the Ansible user
vault_password_file   = ~/.vault_pass

# Or use a script that outputs the password (must be executable):
# vault_password_file = ~/.vault_pass_script.sh
```

### vault_identity_list (multiple vault identities)

```ini
[defaults]
# Format: <identity>@<password_source>[,<identity>@<password_source>]
# Password source can be a file or an executable script

vault_identity_list = dev@~/.vault_pass_dev, prod@~/.vault_pass_prod, ci@~/.vault_pass_ci

# Usage: encrypt with specific identity
# ansible-vault encrypt_string --vault-id prod@~/.vault_pass_prod 'secret' --name vault_api_token

# Usage: decrypt (Ansible tries all identities in order)
# ansible-playbook -i inventory site.yml --vault-id dev@~/.vault_pass_dev
```

---

## Callback Plugin Configuration

### profile_tasks (timing per task)

```ini
[defaults]
callbacks_enabled = profile_tasks, timer

[callback_profile_tasks]
# Show the top N slowest tasks
task_output_limit = 20
sort_order = descending
```

### timer (total playbook time)

Included with `ansible.posix` collection. No additional config needed.

### ARA (Ansible Run Analysis)

```ini
[defaults]
callbacks_enabled = ara_default

[ara]
api_client    = offline
api_server    = http://ara.example.com:8000
# For offline client (embedded SQLite):
database      = ~/.ara/ansible.sqlite
```

### AWX callback (do NOT configure manually)

AWX injects `awx_display` automatically via its runner. Do not add `awx_display` to `callbacks_enabled` — it will cause duplicate output.

---

## Fact Caching Configurations

### jsonfile (simple, file-based)

```ini
[defaults]
gathering             = smart
fact_caching          = jsonfile
fact_caching_connection = /tmp/ansible_facts_cache
fact_caching_timeout  = 3600           # seconds (1 hour)
```

- Stores one JSON file per host in the directory.
- Good for single-controller setups.
- Clear cache: `rm -rf /tmp/ansible_facts_cache/*`

### redis (shared, multi-controller)

```ini
[defaults]
gathering             = smart
fact_caching          = redis
fact_caching_connection = redis://localhost:6379/0
# With password:
# fact_caching_connection = redis://:password@localhost:6379/0
fact_caching_timeout  = 86400          # seconds (24 hours)
```

Requires: `pip install redis`

### mongodb (enterprise)

```ini
[defaults]
gathering             = smart
fact_caching          = mongodb
fact_caching_connection = mongodb://username:password@localhost:27017/ansible_facts
fact_caching_timeout  = 86400
```

Requires: `pip install pymongo`

---

## Review Checklist (for review-conf command)

### CRITICAL issues

- `vault_password_file` pointing to a world-readable file (`chmod o+r`)
- Plaintext passwords in `vault_identity_list` (should reference files, not inline passwords)
- `forks` set above 100 without documented justification (risk of OOM on controller)

### WARNING issues

- `host_key_checking = False` without a justification comment
- Missing `[privilege_escalation]` section when `become = True` is used
- `log_path` pointing to a world-readable location
- `fact_caching_connection` containing credentials in plaintext (use vault or env vars)
- `callbacks_enabled` including `awx_display` manually (AWX injects it)
- Deprecated settings: `accelerate` (removed in ansible-core 2.12), `squash_actions`

### INFO notices

- `gathering = implicit` instead of `smart` (performance suggestion)
- `forks` left at default (5) for large inventories (performance suggestion)
- `retry_files_enabled = True` (creates noise, recommend False)
- `stdout_callback = debug` (extremely verbose, suggest `yaml` or `minimal`)
