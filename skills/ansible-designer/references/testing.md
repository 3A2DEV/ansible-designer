# Testing Reference

Use this reference for validation guidance in examples and for review criteria in `review-*` commands.

## Minimum Validation Expectations

### Playbook examples

Provide or recommend:
- `ansible-playbook --syntax-check`
- `ansible-lint`
- one documented validation run such as `--check` or `--tags validate`

### Role examples

Provide:
- `tests/test.yml`
- `tests/inventory`

Optional but useful:
- README commands for `ansible-playbook -i tests/inventory tests/test.yml --syntax-check`

### Collection examples

If a collection contains plugins, document:
- `ansible-test sanity`
- integration or usage examples
- any local prerequisites such as collection paths or required dependencies

## Example Commands

```bash
ansible-playbook -i inventory/hosts.yml site.yml --syntax-check
ansible-lint examples/
ansible-inventory -i inventory/hosts.yml --graph
ansible-test sanity --docker default
```

## Check Mode Guidance

Use `--check --diff` in READMEs when the example is reasonably check-mode friendly.

Do not claim full check-mode support if the example contains unavoidable commands that cannot predict change correctly.

## Review Heuristics

Flag:
- examples with no documented validation path
- roles without a smoke test
- collections with custom modules but no `ansible-test` guidance
- READMEs that advertise commands the example tree cannot support
