# Changelog

All notable changes to ansible-designer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-31

### Added

- Initial release of the ansible-designer Claude Code skill
- `/ansible-designer:new-playbook` — scaffold site, component, and AWX-ready playbooks
- `/ansible-designer:review-playbook` — CRITICAL/WARNING/INFO severity report for playbooks
- `/ansible-designer:update-playbook` — diff-confirmed playbook updates
- `/ansible-designer:new-role` — scaffold complete roles with optional multi-OS support (RHEL/Solaris/Windows)
- `/ansible-designer:review-role` — severity report for role structure and content
- `/ansible-designer:update-role` — diff-confirmed role updates
- `/ansible-designer:new-collection` — scaffold collections with galaxy.yml, plugin skeletons, roles
- `/ansible-designer:review-collection` — severity report for collection completeness
- `/ansible-designer:update-collection` — diff-confirmed collection updates (version bump, add role/plugin)
- `/ansible-designer:new-conf` — generate annotated ansible.cfg for dev, CI, and AWX environments
- `/ansible-designer:review-conf` — severity report for ansible.cfg security and correctness
- `/ansible-designer:update-conf` — diff-confirmed ansible.cfg updates
- Reference guides:
  - `references/discovery.md` — project discovery procedure and context object
  - `references/best_practices.md` — FQCN, tags, no_log, idempotency, AWX, platform notes
  - `references/playbook.md` — site, component, and AWX playbook templates
  - `references/role.md` — full role structure, OS-specific task/var files, Windows, Solaris
  - `references/collection.md` — galaxy.yml, module/filter/lookup skeletons
  - `references/inventory.md` — static/dynamic inventory, GCP/OCI plugins, AWX sources
  - `references/ansible_cfg.md` — dev/CI/AWX profiles, vault, fact caching, callbacks
- Examples:
  - `examples/simple-playbook/` — site playbook with inventory and group_vars
  - `examples/role-rhel/` — nginx role for RHEL 8/9
  - `examples/role-multiplatform/` — NTP role for RHEL, Solaris, and Windows
  - `examples/local-collection/` — local collection with module, filter, and lookup plugins
