# Plugin Reference

Use this reference for collection plugin examples and reviews.

## Supported Example Types

- custom modules
- filter plugins
- lookup plugins

## Module Expectations

A module example should include:
- `DOCUMENTATION`
- `EXAMPLES`
- `RETURN`
- `AnsibleModule`
- predictable return values
- explicit failure messages

Prefer:
- `module.get_bin_path()` for external binaries
- `module.run_command()` for command execution
- `supports_check_mode=True` when practical

## Module Skeleton

```python
from ansible.module_utils.basic import AnsibleModule


def run_module():
    module = AnsibleModule(
        argument_spec=dict(name=dict(type='str', required=True)),
        supports_check_mode=True,
    )

    result = dict(changed=False, name=module.params['name'])
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
```

## Filter Plugin Expectations

Filter plugins should:
- expose a small, focused set of filters
- validate input types
- raise `AnsibleFilterError` for bad input

## Lookup Plugin Expectations

Lookup plugins should:
- derive from `LookupBase`
- return a list
- document expected terms and options
- avoid hidden controller-side side effects

## Review Heuristics

Flag:
- plugin files without documentation blocks
- modules that bypass `AnsibleModule`
- modules with ambiguous return shapes
- plugin examples with no README or playbook usage example
