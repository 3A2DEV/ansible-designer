# Repository Guidelines

## Project Structure & Module Organization

The repository root is a thin wrapper; the actual distributable content lives in `ansible-designer/`. Use `ansible-designer/skills/ansible-designer/` for the main entry skill, subcommands such as `new-playbook/` and `review-role/`, and shared references under `references/`. Keep runnable examples in `ansible-designer/examples/` (`simple-playbook/`, `role-rhel/`, `role-multiplatform/`, `local-collection/`). Repository-level planning notes live in `PROJECT.md`; packaged contributor docs and release notes live beside the skill in `ansible-designer/CONTRIBUTING.md` and `ansible-designer/CHANGELOG.md`.

## Build, Test, and Development Commands

There is no build step. Validate content directly from the repo root.

- `rg --files ansible-designer` lists the packaged files and helps catch missing paths.
- `python3 -c "..."` using the frontmatter check from `ansible-designer/CONTRIBUTING.md` validates every `SKILL.md` header.
- `ansible-lint ansible-designer/examples/` checks the example playbooks and roles against Ansible standards.
- `git diff -- ansible-designer` reviews the final change set before opening a PR.

## Coding Style & Naming Conventions

Write Markdown concisely and keep slash-command names explicit in descriptions. `SKILL.md` frontmatter must be valid YAML with kebab-case `name` values no longer than 64 characters. For Ansible YAML, use 2-space indentation, FQCN modules such as `ansible.builtin.package`, explicit `state:` values, mandatory task tags, and `no_log: true` on secret-handling tasks. Follow existing directory names and keep new examples realistic rather than placeholder content.

## Testing Guidelines

Every change should be checked at the file, syntax, and behavior-example level. Run the frontmatter validator for skill edits and `ansible-lint ansible-designer/examples/` for YAML changes. Name example files conventionally (`site.yml`, `tasks/main.yml`, `vars/RedHat.yml`) so they match Ansible expectations. There is no coverage gate, so reviewers rely on complete examples and lint-clean output.

## Commit & Pull Request Guidelines

Git history is minimal today (`Initial commit`), so use short imperative commit subjects such as `Add review-conf edge-case guidance`. Keep each PR to one logical change, update `ansible-designer/CHANGELOG.md`, describe the affected commands or references, and include relevant lint output. Add screenshots only when documentation rendering or generated file trees materially change.
