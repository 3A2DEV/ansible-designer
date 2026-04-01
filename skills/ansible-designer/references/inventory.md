# Inventory Reference

This document covers static inventory, dynamic inventory, group/host vars, AWX inventory sources, and cloud provider plugins (GCP, OCI).

---

## 1. Static Inventory — INI Format

The simplest inventory format. Suitable for small, stable environments.

```ini
# inventory/hosts

# Ungrouped hosts
jumphost.example.com ansible_host=10.0.0.5

[webservers]
web01 ansible_host=192.168.1.10 ansible_port=22
web02 ansible_host=192.168.1.11 ansible_port=22
web03 ansible_host=192.168.1.12 ansible_port=22

[databases]
db01 ansible_host=192.168.1.20
db02 ansible_host=192.168.1.21

[loadbalancers]
lb01 ansible_host=192.168.1.5

# Group of groups
[production:children]
webservers
databases
loadbalancers

# Group variables (prefer group_vars/ files instead)
[webservers:vars]
ansible_user=webdeploy
nginx_port=80
```

---

## 2. Static Inventory — YAML Format

Preferred over INI for complex inventories. Supports full variable nesting.

```yaml
# inventory/hosts.yml
all:
  vars:
    ansible_user: ansible
    ansible_ssh_private_key_file: ~/.ssh/id_rsa

  children:
    production:
      children:
        webservers:
          hosts:
            web01:
              ansible_host: 192.168.1.10
              nginx_port: 80
            web02:
              ansible_host: 192.168.1.11
              nginx_port: 80
          vars:
            ansible_user: webdeploy
            app_env: production

        databases:
          hosts:
            db01:
              ansible_host: 192.168.1.20
              pg_port: 5432
            db02:
              ansible_host: 192.168.1.21
              pg_port: 5432
          vars:
            ansible_user: dbadmin

        loadbalancers:
          hosts:
            lb01:
              ansible_host: 192.168.1.5

    staging:
      children:
        webservers:
          hosts:
            stg-web01:
              ansible_host: 10.10.1.10
          vars:
            app_env: staging

    windows:
      hosts:
        win-app01:
          ansible_host: 192.168.2.10
          ansible_connection: winrm
          ansible_winrm_transport: kerberos
          ansible_port: 5986
          ansible_winrm_scheme: https
          ansible_winrm_server_cert_validation: ignore
```

---

## 3. group_vars/ and host_vars/ Structure

Ansible automatically loads variable files from `group_vars/` and `host_vars/` directories located next to the inventory file or playbook.

### Directory structure

```
inventory/
├── hosts.yml
├── group_vars/
│   ├── all/
│   │   ├── vars.yml          # Variables for all hosts
│   │   └── vault.yml         # Vault-encrypted secrets for all hosts
│   ├── webservers/
│   │   ├── vars.yml
│   │   └── vault.yml
│   ├── databases.yml         # Single-file format also supported
│   └── production.yml
└── host_vars/
    ├── web01/
    │   ├── vars.yml
    │   └── vault.yml
    └── db01.yml              # Single-file format
```

### Naming rules

- Group name must match exactly: group `webservers` → `group_vars/webservers/` or `group_vars/webservers.yml`
- Host name must match exactly: host `web01` → `host_vars/web01/` or `host_vars/web01.yml`
- All `.yml` files inside a directory are loaded (alphabetical order)
- Use directories (not single files) for groups that need vault separation

### Example group_vars/webservers/vars.yml

```yaml
# group_vars/webservers/vars.yml
nginx_port: 80
nginx_worker_processes: "{{ ansible_processor_vcpus }}"
nginx_client_max_body_size: "20m"
nginx_enable_ssl: true
nginx_ssl_cert: /etc/ssl/certs/app.crt
nginx_ssl_key: /etc/ssl/private/app.key

# Reference vault-encrypted value via a plain wrapper variable
app_db_password: "{{ vault_app_db_password }}"
```

### Example group_vars/webservers/vault.yml (encrypted)

```yaml
# group_vars/webservers/vault.yml — encrypt this file with ansible-vault
vault_app_db_password: "s3cur3P@ssw0rd"
vault_ssl_key_passphrase: "anothersecret"
```

---

## 4. Dynamic Inventory — Script-Based

A script-based dynamic inventory returns JSON to stdout.

### Required JSON structure

```json
{
  "_meta": {
    "hostvars": {
      "web01.example.com": {
        "ansible_host": "192.168.1.10",
        "app_env": "production"
      }
    }
  },
  "webservers": {
    "hosts": ["web01.example.com", "web02.example.com"],
    "vars": {
      "nginx_port": 80
    }
  },
  "all": {
    "children": ["webservers", "databases"]
  }
}
```

### Script requirements

- Must accept `--list` to output all inventory
- Must accept `--host <hostname>` to output hostvars for a single host
- Must be executable (`chmod +x inventory_script.py`)
- Must return valid JSON to stdout

### Example minimal Python inventory script

```python
#!/usr/bin/env python3
# inventory/dynamic_inventory.py

import argparse
import json
import sys

def get_inventory():
    # Replace with actual data source query
    return {
        "_meta": {"hostvars": {}},
        "all": {"children": ["ungrouped"]}
    }

def get_host(hostname):
    return {}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host')
    args = parser.parse_args()

    if args.list:
        print(json.dumps(get_inventory()))
    elif args.host:
        print(json.dumps(get_host(args.host)))
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

---

## 5. Dynamic Inventory — Plugin-Based

Plugin-based inventories are the preferred modern approach (ansible-core 2.4+).

### Configuration file format

```yaml
# inventory/mycloud.yml
plugin: <plugin_name>
# plugin-specific options follow
```

Reference in ansible.cfg:
```ini
[defaults]
inventory = ./inventory/mycloud.yml
```

Or use a directory:
```ini
[defaults]
inventory = ./inventory/
```
Ansible will load all inventory files in the directory.

---

## 6. GCP Dynamic Inventory Plugin

Uses `google.cloud.gcp_compute` plugin. Requires `google-auth` Python library.

```yaml
# inventory/gcp.yml
plugin: google.cloud.gcp_compute
projects:
  - my-gcp-project-id
regions:
  - us-central1
  - europe-west1
auth_kind: serviceaccount
service_account_file: /path/to/service_account.json
# Or use application default credentials:
# auth_kind: application

filters:
  - status = RUNNING
  - labels.environment = production

hostnames:
  - name
  - public_ip
  - private_ip

compose:
  ansible_host: networkInterfaces[0].accessConfigs[0].natIP
  ansible_user: "'ansible'"
  app_env: labels.environment | default('unknown')

keyed_groups:
  - key: labels.role
    prefix: role
  - key: zone
    prefix: zone
  - key: status
    prefix: status

groups:
  webservers: "'web' in name"
  databases: "'db' in name"
```

### GCP ansible.cfg (if using ADC)

```ini
[gcp]
# Application Default Credentials (gcloud auth application-default login)
# No additional config needed
```

---

## 7. OCI Dynamic Inventory Plugin

Uses `oracle.oci.oci` plugin. Requires `oci` Python library.

```yaml
# inventory/oci.yml
plugin: oracle.oci.oci
regions:
  - us-ashburn-1
  - eu-frankfurt-1

compartments:
  - ocid: ocid1.compartment.oc1..aaaaaaaa...
    fetch_hosts_from_subcompartments: true

filters:
  - lifecycle_state: RUNNING

hostname_format: fqdn
# Options: fqdn, private_ip, public_ip, display_name

compose:
  ansible_host: private_ip
  ansible_user: "'opc'"
  app_region: region

keyed_groups:
  - key: freeform_tags.role
    prefix: role
  - key: freeform_tags.environment
    prefix: env
  - key: region
    prefix: region

groups:
  webservers: "'web' in display_name"
  databases: "'db' in display_name"
  production: "freeform_tags.get('environment', '') == 'production'"
```

### OCI authentication configuration

```ini
# ~/.oci/config
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaa...
fingerprint=aa:bb:cc:dd:...
tenancy=ocid1.tenancy.oc1..aaaaaaaa...
region=us-ashburn-1
key_file=~/.oci/oci_api_key.pem
```

---

## 8. AWX Inventory Source Configuration

AWX manages inventory sources through its UI and API. Key configuration patterns:

### AWX-managed inventory YAML export

```yaml
# AWX can export inventory in this format (via awx-manage export_assets)
all:
  hosts:
    web01:
      ansible_host: 192.168.1.10
  vars:
    # AWX injects these via the credential and inventory source
    ansible_user: "{{ awx_credential_username }}"
```

### AWX inventory source: GCP

In AWX:
1. Create a GCP credential (type: Google Compute Engine)
2. Create an inventory source:
   - Source: Google Compute Engine
   - Credential: (the GCP credential)
   - Regions: us-central1, europe-west1
   - Filter: `tag:ansible`
3. Configure update on launch: enabled

### AWX inventory source: file-based (project)

In AWX:
- Source: Sourced from a Project
- Project: (your Ansible project)
- Inventory file: `inventory/hosts.yml`
- Update on project update: enabled

### AWX inventory variables

AWX passes machine credentials automatically. Reference them in playbooks via standard Ansible variables. AWX also supports:
- `TOWER_*` environment variables in job templates
- Extra vars from surveys (highest precedence)
- Schedule-based inventory sync (cron)

---

## 9. Inventory Variable Precedence

From lowest to highest:
1. `group_vars/all`
2. `group_vars/<parent_group>`
3. `group_vars/<child_group>`
4. `host_vars/<hostname>`
5. Playbook `vars:` section
6. Task `vars:` parameter
7. `set_fact`
8. `extra_vars` (command-line `-e` or AWX survey) ← highest

Design inventory variables to sit at the appropriate level. Do not put host-specific values in group_vars; do not put group-level configs in host_vars.
