# role-multiplatform Example

Demonstrates a multi-OS role that configures NTP across RHEL, Solaris, and Windows hosts.

## What this shows

- `include_vars` with `first_found` behavior for OS-specific variable loading
- OS-dispatched task files (`RedHat.yml`, `Solaris.yml`, `Windows.yml`) via `include_tasks`
- `ansible.windows.*` modules for Windows/WinRM targets
- Solaris SMF (`svcadm`/`svccfg`) for service management
- Handler that branches on OS family

## Structure

```
role-multiplatform/
├── site.yml
├── inventory/
│   └── hosts.yml
└── roles/
    └── ntp/
        ├── defaults/main.yml       # shared defaults
        ├── vars/
        │   ├── RedHat.yml          # chrony paths and package names
        │   ├── Solaris.yml         # ntpd / SMF service names
        │   └── Windows.yml         # W32tm service and registry keys
        ├── tasks/
        │   ├── main.yml            # OS detection + dispatch
        │   ├── RedHat.yml          # chrony install + configure
        │   ├── Solaris.yml         # ntpd + svcadm
        │   └── Windows.yml         # w32tm /config + win_service
        ├── handlers/main.yml
        ├── templates/
        │   └── chrony.conf.j2
        └── meta/main.yml
```

## Usage

```bash
# All hosts
ansible-playbook -i inventory/hosts.yml site.yml

# Windows only
ansible-playbook -i inventory/hosts.yml site.yml --limit windows

# RHEL + Solaris, validate tag only
ansible-playbook -i inventory/hosts.yml site.yml --limit rhel,solaris -t validate
```

## Requirements

- ansible-core >= 2.15
- `ansible.windows` collection for Windows targets
- `ansible.posix` collection for RHEL targets
- WinRM configured on Windows hosts (HTTPS recommended in production)

## Validation

```bash
ansible-playbook -i inventory/hosts.yml site.yml --syntax-check
ansible-lint .
```
