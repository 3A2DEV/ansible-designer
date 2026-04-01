# ansible.cfg Reference

This reference provides practical `ansible.cfg` profiles for development, CI, and controller-oriented usage.

## Notes

- Keep generated config compatible with `ansible-core 2.15+`.
- Prefer the singular `collections_path` key in new examples.
- Existing content using `collections_paths` should be treated as legacy-compatible input during review or update flows.
- Every security-sensitive choice should be documented inline.

## Development Profile

```ini
[defaults]
inventory = ./inventory/hosts.yml
roles_path = ./roles
collections_path = ./collections
remote_user = ansible
host_key_checking = False
forks = 10
timeout = 30
retry_files_enabled = False
stdout_callback = yaml
callbacks_enabled = ansible.posix.profile_tasks, ansible.posix.timer
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts_cache
fact_caching_timeout = 3600

[diff]
always = True
context = 5

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
ssh_args = -C -o ControlMaster=auto -o ControlPersist=60s
control_path = /tmp/ansible-ssh-%%h-%%p-%%r

[persistent_connection]
connect_timeout = 30
command_timeout = 30
```

Use this profile for:
- local examples
- developer laptops
- disposable lab environments

Document why `host_key_checking = False` is acceptable when you generate it.

## CI Profile

```ini
[defaults]
inventory = ./inventory/hosts.yml
roles_path = ./roles
collections_path = ./collections
remote_user = ci-ansible
host_key_checking = False
forks = 20
timeout = 20
retry_files_enabled = False
stdout_callback = json
gathering = implicit
fact_caching = memory
error_on_undefined_vars = True

[diff]
always = True
context = 3

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
ssh_args = -C -o ControlMaster=auto -o ControlPersist=30s -o BatchMode=yes
control_path = /tmp/ansible-ci-%%h-%%p-%%r

[persistent_connection]
connect_timeout = 20
command_timeout = 60
```

Use this profile for:
- ephemeral runners
- fast-fail validation jobs
- examples that emphasize machine-readable output

## Controller / AWX-Oriented Profile

```ini
[defaults]
inventory = ./inventory/hosts.yml
roles_path = ./roles
collections_path = ./collections
host_key_checking = True
forks = 25
timeout = 30
retry_files_enabled = False
stdout_callback = yaml
gathering = smart
fact_caching = memory

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
ssh_args = -C -o ControlMaster=auto -o ControlPersist=60s
```

Notes:
- keep controller examples conservative and avoid manually adding AWX-only callbacks
- document that credentials should come from the controller, not from committed files

## Review Heuristics

Flag:
- insecure vault file references
- plaintext credentials in `fact_caching_connection`
- world-writable `log_path`
- deprecated or invalid settings
- unnecessary controller-specific callbacks
- missing `collections_path` when local collections are clearly part of the project
