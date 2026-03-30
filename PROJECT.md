You are about to build a public GitHub repository for a Claude Code skill called ansible-designer.
This is a pure planning-to-execution handoff. All decisions have already been made.
Do not ask for confirmations on already-decided items. Follow the spec exactly.

---

## PROJECT IDENTITY

- Skill name: ansible-designer
- Installation command: npx skills add 3A2DEV/ansible-designer -a claude-code
- Runtime: Claude Code only (requires bash_tool)
- License: Apache 2.0
- All output goes in: ./ansible-designer/

---

## REPOSITORY STRUCTURE TO CREATE

ansible-designer/
├── README.md
├── LICENSE                        (Apache 2.0 full text)
├── CONTRIBUTING.md
├── CHANGELOG.md                   (v0.1.0 initial entry)
│
├── skills/
│   └── ansible-designer/
│       ├── SKILL.md               ← /ansible-designer entry point
│       ├── new-playbook/
│       │   └── SKILL.md           ← /ansible-designer:new-playbook
│       ├── review-playbook/
│       │   └── SKILL.md
│       ├── update-playbook/
│       │   └── SKILL.md
│       ├── new-role/
│       │   └── SKILL.md
│       ├── review-role/
│       │   └── SKILL.md
│       ├── update-role/
│       │   └── SKILL.md
│       ├── new-collection/
│       │   └── SKILL.md
│       ├── review-collection/
│       │   └── SKILL.md
│       ├── update-collection/
│       │   └── SKILL.md
│       ├── new-conf/
│       │   └── SKILL.md
│       ├── review-conf/
│       │   └── SKILL.md
│       ├── update-conf/
│       │   └── SKILL.md
│       └── references/
│           ├── discovery.md
│           ├── best_practices.md
│           ├── playbook.md
│           ├── role.md
│           ├── collection.md
│           ├── inventory.md
│           └── ansible_cfg.md
│
├── examples/
│   ├── simple-playbook/
│   ├── role-rhel/
│   ├── role-multiplatform/
│   └── local-collection/
│
└── .github/
    └── workflows/
        └── validate.yml

---

## DECISIONS ALREADY MADE — DO NOT RE-ASK

- Discovery order: CLAUDE.md → ansible.cfg → README.md → filesystem
- Discovery runs always at command start, unless the user already provided all required parameters inline
- review commands: produce a structured severity report only, never modify files
- update commands: always show a diff and wait for explicit confirmation before writing
- new-role: always ask the user whether multi-OS support is needed (RHEL / Solaris / Windows/WinRM);
  generate OS-specific var files only if confirmed
- FQCN mandatory everywhere (ansible.builtin.copy, never copy)
- no_log: true mandatory on every task handling secrets, passwords, tokens
- Tags mandatory on every task: minimum component name + action category (install, configure, service, validate)
- Never silently overwrite existing files: always show diff + ask confirmation
- All syntax based on current official Ansible documentation (no deprecated syntax)
- ansible.cfg scope: all official sections plus vault (vault_password_file, vault_identity_list),
  environment profiles (dev / CI / AWX), callback plugins (profile_tasks, timer, AWX, ara),
  fact caching (jsonfile, redis, mongodb)
- License: Apache 2.0

---

## GLOBAL RULES THAT APPLY TO ALL COMMANDS

These must appear in the root SKILL.md and be enforced by every sub-skill:

1. Always run discovery first (unless all parameters already provided)
2. Never overwrite files silently — always diff + confirm
3. Always use FQCN for all modules
4. Always add no_log: true on secret-handling tasks
5. Always tag every task
6. review never modifies files
7. update always shows diff before writing
8. After any write operation, show the resulting file tree
9. Suggest the next logical step at the end of every command

---

## STANDARD OPERATIONAL FLOW (every command follows this)

Step 1 — Discovery
  Read in order: CLAUDE.md → ansible.cfg → README.md → filesystem scan
  Build internal context: existing paths, namespaces, collections, roles found

Step 2 — Parameter collection
  If user already provided all required parameters: skip
  Otherwise: ask one question at a time, with smart defaults from discovery context

Step 3 — Pre-write confirmation
  Show summary of what will be created or modified
  For update commands: show diff
  Wait for explicit user confirmation

Step 4 — Execution
  Write or modify files using bash_tool
  Use templates from references/ as the base for all generated content

Step 5 — Final output
  Show file tree of created/modified files
  Suggest next logical step

---

## COMMAND PARAMETERS AND BEHAVIOR

### Playbook commands (use references/playbook.md)

/ansible-designer:new-playbook
  Required: path, filename, target hosts/groups, roles to include
  Generates: complete playbook with proper header, vars block, roles section,
             handlers reference, and tags

/ansible-designer:review-playbook
  Required: path + filename (resolved from discovery if not provided)
  Produces: structured report grouped by severity (critical / warning / info)
  Checks: FQCN usage, idempotency patterns, no_log presence on secret tasks,
          tag coverage, deprecated syntax, style consistency
  Never modifies files.

/ansible-designer:update-playbook
  Required: path + filename + description of requested change
  Behavior: reads existing file, applies requested changes, shows diff, confirms, writes

### Role commands (use references/role.md)

/ansible-designer:new-role
  Required: role_path OR FQCN (namespace.collection.role), role name
  FQCN resolution: looks in ./collections/ansible_collections/<ns>/<col>/roles/
                   and in collections_path from ansible.cfg if present
  Always asks: "Does this role need multi-OS support? (RHEL / Solaris / Windows/WinRM)"
  If yes: generates vars/RedHat.yml, vars/Solaris.yml, vars/Windows.yml
          and OS detection task block using include_vars with_first_found
  Scaffolds: full role directory structure per Ansible standards

/ansible-designer:review-role
  Required: role name or FQCN (resolved from discovery)
  Checks: directory structure completeness, task FQCN, tag coverage, no_log,
          defaults vs vars usage, meta/main.yml validity, handler correctness
  Produces: severity report. Never modifies files.

/ansible-designer:update-role
  Required: role name or FQCN + description of requested change
  Behavior: modifies specific role files, shows diff, confirms, writes

### Collection commands (use references/collection.md)

/ansible-designer:new-collection
  Required: collection_path, namespace, collection name
  Scaffolds: galaxy.yml, README.md, CHANGELOG.md, LICENSE,
             plugins/{modules,filter,lookup}/, roles/, playbooks/, docs/

/ansible-designer:review-collection
  Required: collection identification (resolved from discovery)
  Checks: galaxy.yml completeness and validity, directory structure,
          presence of README.md / CHANGELOG.md / LICENSE
  Produces: severity report. Never modifies files.

/ansible-designer:update-collection
  Required: collection identification + requested change
  Behavior: updates metadata, adds roles/plugins, shows diff, confirms, writes

### ansible.cfg commands (use references/ansible_cfg.md)

/ansible-designer:new-conf
  Required: target environment (dev / CI / AWX)
  Generates: environment-specific ansible.cfg with ALL sections fully documented
  Sections covered: [defaults], [privilege_escalation], [ssh_connection],
                    [persistent_connection], [accelerate], [selinux], [colors],
                    [diff], vault config, callback plugins, fact caching
  All non-default values are commented with explanation.

/ansible-designer:review-conf
  Required: path to ansible.cfg (resolved from discovery)
  Checks: deprecated settings, insecure values (e.g. host_key_checking=False
          without justification), missing critical sections, vault misconfiguration
  Produces: severity report. Never modifies files.

/ansible-designer:update-conf
  Required: path to ansible.cfg + requested change
  Behavior: modifies specific sections, shows diff, confirms, writes

---

## REFERENCES CONTENT REQUIREMENTS

Write each references/ file as a complete, self-contained guide that Claude uses
at runtime to generate correct output. Each file must contain:

### references/discovery.md
- Step-by-step procedure for reading CLAUDE.md, ansible.cfg, README.md, filesystem
- How to extract: roles_path, collections_path, inventory path, namespace, existing roles/collections
- How to build the internal context object used by sub-skills
- Edge cases: missing files, relative vs absolute paths, multiple roles_path entries

### references/best_practices.md
- FQCN rules and examples
- Tag taxonomy (mandatory + recommended)
- no_log usage patterns
- Idempotency checklist
- Variable precedence (when to use defaults/ vs vars/)
- Handler best practices
- Vault usage patterns
- AWX-specific considerations (survey vars, credentials, extra_vars)
- Platform notes: RHEL/Solaris/Windows/WinRM differences

### references/playbook.md
- Complete playbook templates for: site playbook, component playbook, AWX-ready playbook
- Header format (author, version, description)
- vars block patterns
- roles vs tasks vs import_playbook usage
- When to use include_tasks vs import_tasks
- Error handling patterns (block/rescue/always)

### references/role.md
- Full role directory structure (all standard directories)
- tasks/main.yml patterns
- OS-specific var loading block (include_vars with_first_found)
- var files for RHEL, Solaris, Windows
- defaults/ vs vars/ usage rules
- handlers/ patterns
- meta/main.yml complete format including dependencies and platform matrix
- Windows/WinRM specific: ansible.windows modules, win_* vs ansible.windows.*
- Solaris specific: pkgadd, svcadm, SMF service management patterns

### references/collection.md
- galaxy.yml complete format with all fields
- Standard collection directory structure
- How to reference collection roles from playbooks
- Plugin types: modules, filter, lookup — skeleton for each
- Version and dependency management

### references/inventory.md
- Static inventory: INI and YAML format
- group_vars/ and host_vars/ structure and naming
- Dynamic inventory: script-based and plugin-based patterns
- AWX inventory source configuration
- GCP and OCI dynamic inventory plugin patterns

### references/ansible_cfg.md
- Complete annotated ansible.cfg covering every official section
- Dev profile: permissive, verbose, local paths
- CI profile: strict, no host key checking justified, minimal output
- AWX profile: callback plugins, fact caching, credential paths
- Vault section: vault_password_file, vault_identity_list with multiple identities
- Fact caching: jsonfile / redis / mongodb configurations
- Callback plugins: profile_tasks, timer, AWX, ara

---

## EXECUTION ORDER

Build files in this exact order (each depends on the previous):

1.  references/discovery.md
2.  references/best_practices.md
3.  skills/ansible-designer/SKILL.md              (root entry point)
4.  references/role.md
5.  new-role/SKILL.md, review-role/SKILL.md, update-role/SKILL.md
6.  references/playbook.md
7.  new-playbook/SKILL.md, review-playbook/SKILL.md, update-playbook/SKILL.md
8.  references/collection.md
9.  new-collection/SKILL.md, review-collection/SKILL.md, update-collection/SKILL.md
10. references/ansible_cfg.md
11. new-conf/SKILL.md, review-conf/SKILL.md, update-conf/SKILL.md
12. references/inventory.md
13. examples/ (one working example per domain)
14. README.md, CONTRIBUTING.md, CHANGELOG.md, LICENSE
15. .github/workflows/validate.yml

After completing all files, run:
  find ./ansible-designer -type f | sort
and show the full file tree to confirm completeness.

---

## QUALITY REQUIREMENTS

- Every SKILL.md frontmatter must be valid YAML with name and description fields
- name must be kebab-case, max 64 characters
- description must be under 1024 characters, no angle brackets
- Sub-skill descriptions must include the specific slash command that triggers them
- All generated Ansible content must use current official syntax (ansible-core 2.15+)
- No placeholder comments like "# add your tasks here" — all templates must be complete
  and realistic, usable as-is or with minimal modification
- Every role template must include at least 3 realistic example tasks
- Every playbook template must be immediately runnable after filling in inventory

Start now. Work through the execution order without pausing between files.
Report progress after each major section (references, sub-skills group, support files).