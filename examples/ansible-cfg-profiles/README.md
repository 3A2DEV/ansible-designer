# ansible-cfg-profiles example

Three `ansible.cfg` profiles showing how the same project can be tuned for development, CI, and controller-oriented execution.

## Files

- `ansible.dev.cfg`
- `ansible.ci.cfg`
- `ansible.awx.cfg`

## Validation

```bash
ansible --version
ANSIBLE_CONFIG=./ansible.dev.cfg ansible-config dump --only-changed
ANSIBLE_CONFIG=./ansible.ci.cfg ansible-config dump --only-changed
ANSIBLE_CONFIG=./ansible.awx.cfg ansible-config dump --only-changed
```

## Notes

- The examples keep `ansible-core 2.15+` compatibility.
- Security-sensitive choices are annotated inline.
- No real vault paths or credentials are committed.
