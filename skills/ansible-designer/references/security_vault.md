# Security and Vault Reference

Use this reference whenever content touches secrets, vault, credential material, or security-sensitive defaults.

## Secret Handling Rules

- never commit real passwords, tokens, keys, or vault passwords
- use wrapper variables such as `db_password: "{{ vault_db_password }}"`
- mark secret-handling tasks with `no_log: true`
- prefer secret placeholders and explanatory README notes in examples

## Vault Example Pattern

Safe example structure:

```text
group_vars/
└── all/
    ├── main.yml
    └── vault.example.yml
```

`main.yml`:

```yaml
app_db_password: "{{ vault_app_db_password }}"
```

`vault.example.yml`:

```yaml
vault_app_db_password: "REPLACE_ME"
```

Make it explicit that `vault.example.yml` is a placeholder, not a committed real secret.

## Task Pattern

```yaml
- name: Create application user
  ansible.builtin.user:
    name: appuser
    password: "{{ vault_appuser_password | password_hash('sha512') }}"
    state: present
  no_log: true
  tags:
    - app
    - security
```

## ansible.cfg Guidance

Prefer:
- `vault_identity_list` only when the environment is documented
- a file path or external secret source, not inline passwords

Flag:
- world-readable vault password files
- plaintext secrets in URLs or inventory
- examples that normalize insecure shortcuts without a note

## Review Heuristics

Flag:
- secret variables without `no_log: true`
- real-looking credentials in examples
- unwrapped secret usage in playbooks or roles
- secret-handling examples with no operator guidance
