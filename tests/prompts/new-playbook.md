/ansible-designer:new-playbook

Create a new component playbook with all parameters provided inline:
- path: playbooks/
- filename: deploy_nginx.yml
- target_hosts: webservers
- playbook_type: component
- become: true
- handlers: yes

Confirm: yes
