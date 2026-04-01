"""Lookup plugin returning a value from a policy mapping."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase


DOCUMENTATION = r"""
name: policy_value
author: Platform Team (@myorg)
short_description: Return a value from a policy mapping
description:
  - Reads a dictionary provided via the C(policy) option and returns the value for the requested key.
options:
  _terms:
    description:
      - Policy keys to retrieve.
    required: true
  policy:
    description:
      - Mapping of policy keys to values.
    type: dict
    required: true
"""

EXAMPLES = r"""
- name: Resolve expected sysctl value
  ansible.builtin.debug:
    msg: "{{ lookup('myorg.infra.policy_value', 'kernel.dmesg_restrict', policy=baseline_sysctl) }}"
"""

RETURN = r"""
_raw:
  description:
    - Values read from the provided policy mapping.
  type: list
  elements: raw
"""


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        policy = kwargs.get("policy")
        if not isinstance(policy, dict):
            raise AnsibleError("policy_value lookup requires a 'policy' dictionary")

        values = []
        for term in terms:
            if term not in policy:
                raise AnsibleError(f"policy key '{term}' was not found")
            values.append(policy[term])
        return values
