# Collection Reference

This document is the authoritative runtime reference for collection scaffolding and modification.

---

## 1. galaxy.yml — Complete Format

```yaml
---
# galaxy.yml — Ansible Collection manifest
namespace: myorg                          # REQUIRED: your organization namespace
name: infra                               # REQUIRED: collection name (lowercase, no hyphens)
version: 1.0.0                            # REQUIRED: semantic version (MAJOR.MINOR.PATCH)
readme: README.md                         # REQUIRED: path to README
description: "Infrastructure automation collection for myorg"

authors:
  - "Platform Team <platform@myorg.example>"

license:
  - Apache-2.0

tags:
  - linux
  - infrastructure
  - rhel
  - solaris
  - networking

dependencies:
  ansible.netcommon: ">=4.0.0"
  ansible.utils: ">=2.0.0"
  community.general: ">=6.0.0"

repository: https://github.com/myorg/ansible-collection-infra
documentation: https://github.com/myorg/ansible-collection-infra/blob/main/docs
homepage: https://myorg.example.com/infrastructure
issues: https://github.com/myorg/ansible-collection-infra/issues

build_ignore:
  - "*.tar.gz"
  - ".github"
  - ".git"
  - "tests/output"
  - "venv"
  - ".venv"
```

---

## 2. Standard Collection Directory Structure

```
collections/ansible_collections/<namespace>/<name>/
├── galaxy.yml                    # Collection manifest (required)
├── README.md                     # Collection overview (required)
├── CHANGELOG.md                  # Version history
├── LICENSE                       # License file (Apache 2.0, GPL, etc.)
├── meta/
│   └── runtime.yml               # Ansible version requirements, routing
├── docs/
│   └── README.md                 # Extended documentation
├── playbooks/
│   └── site.yml                  # Example/included playbooks
├── plugins/
│   ├── modules/
│   │   └── my_module.py          # Custom module
│   ├── module_utils/
│   │   └── helpers.py            # Shared utilities for modules
│   ├── filter/
│   │   └── my_filters.py         # Filter plugins
│   ├── lookup/
│   │   └── my_lookup.py          # Lookup plugins
│   ├── inventory/
│   │   └── my_inventory.py       # Inventory plugins
│   └── callback/
│       └── my_callback.py        # Callback plugins
├── roles/
│   └── my_role/                  # Roles bundled in the collection
│       ├── tasks/main.yml
│       ├── defaults/main.yml
│       └── meta/main.yml
└── tests/
    ├── integration/
    │   └── targets/
    │       └── my_module/
    │           ├── tasks/main.yml
    │           └── aliases
    └── unit/
        └── plugins/
            └── modules/
                └── test_my_module.py
```

---

## 3. meta/runtime.yml

```yaml
---
# meta/runtime.yml
requires_ansible: ">=2.15.0"

# Deprecation notices and routing overrides
# plugin_routing:
#   modules:
#     old_module_name:
#       redirect: myorg.infra.new_module_name
#       deprecation:
#         removal_version: "2.0.0"
#         warning_text: "Use myorg.infra.new_module_name instead"
```

---

## 4. Referencing Collection Roles from Playbooks

### Method 1: FQCN in roles list

```yaml
- name: Configure web servers
  hosts: webservers
  become: true
  roles:
    - role: myorg.infra.nginx
      vars:
        nginx_port: 80
    - role: myorg.infra.app
      tags: [app]
```

### Method 2: collections key + short role name

```yaml
- name: Configure web servers
  hosts: webservers
  become: true
  collections:
    - myorg.infra
  roles:
    - role: nginx           # resolved as myorg.infra.nginx
    - role: app             # resolved as myorg.infra.app
```

**Note:** The `collections:` key is deprecated for modules as of ansible-core 2.12. Prefer FQCN for all module references. The `collections:` key still works for role references.

---

## 5. Module Skeleton — Complete Example

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2024, MyOrg Platform Team
# Apache License 2.0 (see LICENSE file)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: get_service_status
short_description: Retrieve the status of a system service
version_added: "1.0.0"
description:
  - Queries the system service manager and returns the current state,
    process ID, and start time of the named service.
  - Supports systemd on Linux (RHEL 8+) and SCM on Windows.
author:
  - Platform Team (@myorg)
options:
  name:
    description:
      - The name of the service to query.
    required: true
    type: str
  include_pid:
    description:
      - Whether to include the process ID in the output.
      - Requires root privileges on some systems.
    required: false
    type: bool
    default: true
notes:
  - The module does not start or stop services; use M(ansible.builtin.service)
    or M(ansible.windows.win_service) for that purpose.
seealso:
  - module: ansible.builtin.service
  - module: ansible.windows.win_service
"""

EXAMPLES = r"""
- name: Get nginx service status
  myorg.infra.get_service_status:
    name: nginx
  register: nginx_status

- name: Check if nginx is running
  ansible.builtin.debug:
    msg: "nginx is {{ 'running' if nginx_status.is_running else 'stopped' }}"

- name: Get status without PID (unprivileged)
  myorg.infra.get_service_status:
    name: myapp
    include_pid: false
  register: myapp_status
"""

RETURN = r"""
service_name:
  description: The name of the queried service.
  returned: always
  type: str
  sample: nginx
is_running:
  description: Whether the service is currently in a running/active state.
  returned: always
  type: bool
  sample: true
pid:
  description: The main process ID of the service. Null if not running or include_pid is false.
  returned: when is_running is true and include_pid is true
  type: int
  sample: 12345
started_at:
  description: ISO 8601 timestamp of when the service was started. Null if not available.
  returned: when is_running is true
  type: str
  sample: "2024-01-15T08:30:00+00:00"
raw_state:
  description: The raw state string returned by the service manager.
  returned: always
  type: str
  sample: active (running)
"""

import subprocess
import json
from ansible.module_utils.basic import AnsibleModule


def get_systemd_status(module, service_name, include_pid):
    """Query systemd for service status via systemctl."""
    cmd = ['systemctl', 'show', service_name,
           '--property=ActiveState,SubState,MainPID,ExecMainStartTimestamp']

    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(
            msg="Failed to query systemd for service '{}': {}".format(service_name, stderr)
        )

    props = {}
    for line in stdout.splitlines():
        if '=' in line:
            key, _, value = line.partition('=')
            props[key.strip()] = value.strip()

    is_running = props.get('ActiveState') == 'active' and props.get('SubState') == 'running'
    pid = None
    if is_running and include_pid:
        raw_pid = props.get('MainPID', '0')
        pid = int(raw_pid) if raw_pid.isdigit() and int(raw_pid) > 0 else None

    started_at = props.get('ExecMainStartTimestamp') or None
    raw_state = "{} ({})".format(props.get('ActiveState', 'unknown'),
                                  props.get('SubState', 'unknown'))

    return {
        'service_name': service_name,
        'is_running': is_running,
        'pid': pid,
        'started_at': started_at,
        'raw_state': raw_state,
        'changed': False,
    }


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            include_pid=dict(type='bool', default=True),
        ),
        supports_check_mode=True,
    )

    service_name = module.params['name']
    include_pid = module.params['include_pid']

    result = get_systemd_status(module, service_name, include_pid)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
```

---

## 6. Filter Plugin Skeleton

```python
# -*- coding: utf-8 -*-
# plugins/filter/string_filters.py
# Copyright (c) 2024, MyOrg Platform Team
# Apache License 2.0

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re


def to_snake_case(value):
    """Convert a CamelCase or kebab-case string to snake_case.

    Examples:
      MyServiceName   → my_service_name
      my-service-name → my_service_name
    """
    if not isinstance(value, str):
        raise TypeError("to_snake_case expects a string, got {}".format(type(value).__name__))
    # Insert underscore before uppercase letters (CamelCase → snake_case)
    value = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', value)
    # Replace hyphens and spaces with underscores
    value = re.sub(r'[-\s]+', '_', value)
    return value.lower()


def sanitize_hostname(value):
    """Strip invalid characters from a hostname string.

    Keeps only alphanumeric characters, hyphens, and dots.
    Truncates to 253 characters (DNS max).
    """
    if not isinstance(value, str):
        raise TypeError("sanitize_hostname expects a string, got {}".format(type(value).__name__))
    sanitized = re.sub(r'[^a-zA-Z0-9\-\.]', '', value)
    return sanitized[:253]


class FilterModule(object):
    """String manipulation filter plugins for myorg.infra collection."""

    def filters(self):
        return {
            'to_snake_case': to_snake_case,
            'sanitize_hostname': sanitize_hostname,
        }
```

---

## 7. Lookup Plugin Skeleton

```python
# -*- coding: utf-8 -*-
# plugins/lookup/config_value.py
# Copyright (c) 2024, MyOrg Platform Team
# Apache License 2.0

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
name: config_value
author: Platform Team (@myorg)
version_added: "1.0.0"
short_description: Retrieve a value from a configuration file
description:
  - Reads a key from an INI-style configuration file and returns its value.
options:
  _terms:
    description: The key to look up (format: section.key)
    required: true
  file:
    description: Path to the INI configuration file
    required: true
    type: path
"""

EXAMPLES = r"""
- name: Get database host from config
  ansible.builtin.debug:
    msg: "{{ lookup('myorg.infra.config_value', 'database.host', file='/etc/myapp/config.ini') }}"
"""

RETURN = r"""
_raw:
  description: The value associated with the requested key
  type: str
"""

import configparser
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleLookupError


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        config_file = kwargs.get('file')
        if not config_file:
            raise AnsibleLookupError("'file' parameter is required")

        parser = configparser.ConfigParser()
        parser.read(config_file)

        results = []
        for term in terms:
            if '.' not in term:
                raise AnsibleLookupError(
                    "Key must be in 'section.key' format, got: {}".format(term)
                )
            section, key = term.split('.', 1)
            try:
                results.append(parser.get(section, key))
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                raise AnsibleLookupError(
                    "Key '{}' not found in {}: {}".format(term, config_file, str(e))
                )

        return results
```

---

## 8. Version and Dependency Management

### Specifying dependency ranges in galaxy.yml

```yaml
dependencies:
  ansible.netcommon: ">=4.0.0,<6.0.0"
  community.general: ">=6.0.0"
  amazon.aws: ">=5.0.0"
```

### requirements.yml for installing collections

```yaml
# requirements.yml
collections:
  - name: myorg.infra
    version: ">=1.0.0"
    source: https://galaxy.ansible.com

  - name: community.general
    version: "6.4.0"

  - name: ansible.windows
    version: ">=1.13.0"
```

Install with:
```bash
ansible-galaxy collection install -r requirements.yml
```

### Building and publishing

```bash
# Build the collection tarball
ansible-galaxy collection build collections/ansible_collections/myorg/infra/

# Install locally for testing
ansible-galaxy collection install myorg-infra-1.0.0.tar.gz --force

# Publish to Ansible Galaxy
ansible-galaxy collection publish myorg-infra-1.0.0.tar.gz --token <api_token>
```

### Semantic versioning rules

- **PATCH** (1.0.x): Bug fixes, no breaking changes
- **MINOR** (1.x.0): New features, backward-compatible
- **MAJOR** (x.0.0): Breaking changes (module removal, argument changes)
