# inventory-vault example

This example shows a safe inventory layout for projects that keep topology, normal variables, and vault-backed values separate.

## Structure

```text
inventory-vault/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all/
│       ├── main.yml
│       └── vault.example.yml
└── host_vars/
    └── app01/
        └── main.yml
```

## Validation

```bash
ansible-inventory -i inventory/hosts.yml --graph
ansible-inventory -i inventory/hosts.yml --list
```

## Notes

- `vault.example.yml` is a placeholder and must not contain real secrets.
- `main.yml` uses wrapper variables so playbooks and roles do not reference plaintext credentials directly.
