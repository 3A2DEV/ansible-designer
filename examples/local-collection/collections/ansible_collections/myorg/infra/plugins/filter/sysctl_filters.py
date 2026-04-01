"""Filter plugins for sysctl policy examples."""

from ansible.errors import AnsibleFilterError


def normalize_sysctl_value(value):
    if value is None:
        raise AnsibleFilterError("normalize_sysctl_value received None")
    return str(value).strip()


def sysctl_line(key, value):
    if not key:
        raise AnsibleFilterError("sysctl_line requires a non-empty key")
    return f"{key} = {normalize_sysctl_value(value)}"


class FilterModule(object):
    def filters(self):
        return {
            "normalize_sysctl_value": normalize_sysctl_value,
            "sysctl_line": sysctl_line,
        }
