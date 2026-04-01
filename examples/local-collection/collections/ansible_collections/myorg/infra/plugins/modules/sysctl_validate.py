#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Platform Team <platform@myorg.example>
# SPDX-License-Identifier: Apache-2.0

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sysctl_validate
short_description: Validate sysctl settings against a policy file
description:
  - Reads live sysctl values using C(sysctl -a) and compares them
    against a YAML policy file specifying expected key/value pairs.
  - Returns a list of non-compliant settings without modifying anything.
version_added: "1.0.0"
author:
  - Platform Team (@myorg)
options:
  policy_file:
    description:
      - Path to a YAML file mapping sysctl keys to expected values.
    type: path
    required: true
  fail_on_violation:
    description:
      - If C(true), the module fails when any setting deviates from policy.
    type: bool
    default: false
notes:
  - This module never modifies sysctl settings; use M(ansible.posix.sysctl) for that.
requirements:
  - sysctl binary present on the target
'''

EXAMPLES = r'''
- name: Validate sysctl hardening policy
  myorg.infra.sysctl_validate:
    policy_file: /etc/myorg/sysctl_policy.yml
    fail_on_violation: true
  register: sysctl_report

- name: Show violations
  ansible.builtin.debug:
    var: sysctl_report.violations
'''

RETURN = r'''
violations:
  description: List of sysctl keys whose live value differs from policy.
  type: list
  elements: dict
  returned: always
  sample:
    - key: kernel.dmesg_restrict
      expected: "1"
      actual: "0"
compliant:
  description: Whether all checked keys match the policy.
  type: bool
  returned: always
checked:
  description: Total number of sysctl keys evaluated.
  type: int
  returned: always
'''

import yaml
from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        policy_file=dict(type='path', required=True),
        fail_on_violation=dict(type='bool', default=False),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    policy_file = module.params['policy_file']
    fail_on_violation = module.params['fail_on_violation']

    # Load policy
    try:
        with open(policy_file, 'r') as fh:
            policy = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError) as exc:
        module.fail_json(msg="Failed to read policy file '%s': %s" % (policy_file, str(exc)))

    if not isinstance(policy, dict):
        module.fail_json(msg="Policy file must contain a YAML mapping of sysctl key: value pairs")

    # Read live sysctl values
    sysctl_bin = module.get_bin_path('sysctl', required=True)
    rc, stdout, stderr = module.run_command([sysctl_bin, '-a'], check_rc=False)
    if rc != 0:
        module.fail_json(msg="sysctl -a failed: %s" % stderr)

    live = {}
    for line in stdout.splitlines():
        if '=' in line:
            key, _, val = line.partition('=')
            live[key.strip()] = val.strip()

    violations = []
    for key, expected in policy.items():
        actual = live.get(key)
        if actual is None:
            violations.append(dict(key=key, expected=str(expected), actual='<not found>'))
        elif actual != str(expected):
            violations.append(dict(key=key, expected=str(expected), actual=actual))

    compliant = len(violations) == 0
    result = dict(
        violations=violations,
        compliant=compliant,
        checked=len(policy),
        changed=False,
    )

    if fail_on_violation and not compliant:
        module.fail_json(msg="%d sysctl violation(s) found" % len(violations), **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
