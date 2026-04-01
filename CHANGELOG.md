# Changelog

All notable changes to ansible-designer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.7] - 2026-04-02

### Fixed

- Corrected command naming across all skills, docs, and CLAUDE.md: both install paths (marketplace and npx) register skills as top-level commands (`/new-playbook`, `/review-role`, etc.). The `/ansible-designer:X` namespaced form was never available and has been removed from all references.
- `ansible-designer` root skill: removed the incorrect "Command Names by Install Path" table; Available Commands section now shows only the actual top-level form.
- All 12 sub-skill descriptions: reverted from the incorrect dual-form to the correct single top-level trigger.
- `README.md`: updated Installation section, Available Commands table, and all Example Usage code blocks to use top-level command form.
- `CLAUDE.md`: corrected Plugin installation constraints to document that both paths produce top-level commands; removed incorrect namespace source claim.

## [0.1.6] - 2026-04-02

### Changed

- `ansible-designer` (root): Replaced the Available Commands table with a two-column table showing both the marketplace form (`/ansible-designer:<sub-command>`) and the npx form (`/<sub-command>`); added a "Command Names by Install Path" section explaining the namespace difference between the two install paths.
- All 12 sub-skills: Updated frontmatter `description` to mention both trigger forms — `Triggered by /ansible-designer:X (marketplace) or /X (npx)`.

## [0.1.5] - 2026-04-01

### Security

- `ansible-designer`: Removed `Requires bash_tool` from frontmatter description; replaced inline `find` shell command in global rule 8 with a plain description; removed `npx skills add` from SKILL.md (installation belongs in README, not in the skill itself) — addresses Socket LOW alert.
- `new-collection`: Added Input Validation table rejecting shell metacharacters in all user-supplied fields; added prompt injection boundary note instructing the agent to treat user inputs as literal data only; quoted variables in the `find` shell command — addresses Gen MEDIUM COMMAND_EXECUTION + PROMPT_INJECTION.
- `update-conf`: Added Step 2a Secret Scan — scans loaded content for credential-like values and redacts them before any diff display; replaced unauthenticated `redis://localhost:6379/0` example URL with a vault-referenced authenticated form; extended Safety Rules to require inline security comments on sensitive setting changes — addresses Snyk HIGH W007 + W013.
- `update-playbook`: Added Step 2a Secret Scan — scans loaded playbook for credential-like values and redacts before diff display; quoted `find` command — addresses Snyk HIGH W007.
- `update-role`: Added Step 2a Secret Scan — scans all loaded role files (especially `defaults/`, `vars/`) for credential-like values and redacts before diff display; quoted `find` command — addresses Snyk HIGH W007.

## [0.1.4] - 2026-04-01

### Security

- `ansible-designer`: Updated Installation section to recommend the Claude Code marketplace as the primary install path; added a trust warning for the unpinned `npx skills add` alternative.
- `new-collection`: Added input validation rules and prompt injection boundary note; quoted variables in the `find` shell command.
- `update-conf`, `update-playbook`, `update-role`: Added Step 2a Secret Scan with credential redaction before any diff display.

## [0.1.3] - 2026-04-01

### Changed

- Refreshed the runtime references under `skills/ansible-designer/references/` to align playbook, role, collection, inventory, config, testing, plugin, and vault guidance with the repository's `ansible-core 2.15+` contract.
- Added new runtime references: `testing.md`, `security_vault.md`, and `plugins.md`, and wired them into the root skill and sub-skills.
- Expanded `examples/` with self-contained validation-focused content, including bundled roles for `simple-playbook/`, improved multi-platform and local collection examples, and new `ansible-cfg-profiles/` and `inventory-vault/` examples.

## [0.1.2] - 2026-04-01

### Fixed

- Added `.claude-plugin/marketplace.json` — required for Claude Code's native plugin system to
  discover the repo as an installable marketplace. Without it, the plugin system cannot find
  `ansible-designer` and sub-commands are not namespaced correctly.
- Added `.claude-plugin/plugin.json` — plugin manifest that defines the `ansible-designer` namespace
  used for all sub-command skill identifiers (`ansible-designer:review-playbook`, etc.).
- Updated README install instructions: native plugin system (via `extraKnownMarketplaces`) is now
  documented as the recommended path; `npx skills add` is noted as a bare fallback without namespacing.

## [0.1.1] - 2026-04-01

### Fixed

- Restructured `skills/` layout so sub-commands are discoverable by `npx skills`:
  sub-skills moved from `skills/ansible-designer/{sub}/SKILL.md` to `skills/{sub}/SKILL.md`
  (one level deep, matching the superpowers/claude-mem convention)
- Added `package.json` with `name: "ansible-designer"` so the installer uses the correct namespace
- Updated `scripts/validate_structure.py` to scan the new layout

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
