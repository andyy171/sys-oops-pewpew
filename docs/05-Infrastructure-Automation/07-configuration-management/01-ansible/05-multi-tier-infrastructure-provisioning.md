# Ansible Multi-Tier Infrastructure Provisioning

## Cach Hieu Nhanh

Ansible co the dung de configure multi-tier infrastructure va trong mot so truong hop co the provision resource cloud/local VM. Gia tri lon nhat la dung cung mot desired configuration cho local lab, staging va provider that, nhung phai can than voi lifecycle cua resource.

Mental model:

```text
project layout
-> provider provisioner
-> runtime inventory groups
-> role-based server configuration
-> health validation
-> idempotency rerun
-> cleanup/rollback plan
```

Trong production, neu resource lifecycle phuc tap va can state graph dai han, Terraform/OpenTofu thuong la source of truth phu hop hon. Ansible van rat manh cho bootstrap OS, configure service, orchestration sau provision va validation.

## Multi-Tier Topology

Mot ung dung web co nhieu tier thuong gom:

- edge/load balancer hoac reverse proxy.
- web/app servers chay application.
- cache layer nhu Memcached/Redis.
- database primary/replica.
- logging/monitoring/backup components.

Inventory nen map tung tier thanh group ro:

```ini
[edge]
edge-1.example.com

[app]
app-1.example.com
app-2.example.com

[db_primary]
db-1.example.com

[db_replica]
db-2.example.com

[db:children]
db_primary
db_replica

[cache]
cache-1.example.com
```

Guardrails:

- Khong expose cache/database ra Internet; chi allow source tu tier can thiet.
- Khong hard-code plaintext database password trong template/playbook.
- Load balancer config nen sinh tu inventory group, nhung phai co validation de tranh backend rong.
- Database replication/bootstrap can backup va rollback rieng, khong coi nhu package install binh thuong.

## Project Layout

Tach provisioning va configuration de co the thay provider ma khong doi server role:

```text
infra-app/
  inventories/
    dev/
    staging/
    prod/
  playbooks/
    edge/
    app/
    cache/
    db/
  provisioners/
    local.yml
    cloud-a.yml
    cloud-b.yml
  configure.yml
  provision.yml
  requirements.yml
```

Pattern:

- `playbooks/<tier>/main.yml` configure mot tier.
- `configure.yml` import playbook theo tier.
- `provisioners/<provider>.yml` tao resource va add host vao runtime inventory.
- `provision.yml` import provider provisioner roi import `configure.yml`.
- `requirements.yml` pin roles/collections.

## Configure By Tier

Entry point configuration nen doc nhu topology:

```yaml
---
- import_playbook: playbooks/edge/main.yml
- import_playbook: playbooks/app/main.yml
- import_playbook: playbooks/db/main.yml
- import_playbook: playbooks/cache/main.yml
```

Role/task theo tier nen co:

- firewall/security rule gan voi service.
- package/service role.
- template config sinh tu inventory groups.
- handler reload/restart.
- validation task cuoi tier.

Vi du load balancer backend sinh tu inventory:

```yaml
- name: Render load balancer backends
  template:
    src: backends.conf.j2
    dest: /etc/proxy/backends.conf
    validate: "proxy-check -c %s"
  notify: Reload proxy
```

Template nen fail neu backend group rong:

```jinja
{% if groups['app'] | default([]) | length == 0 %}
{{ raise('app group is empty') }}
{% endif %}
```

Neu engine/template khong ho tro `raise`, dung pre-task `assert`.

## Local Lab Parity

Local VM/Vagrant/ephemeral instance giup feedback nhanh:

```text
vagrant up / create lab
-> provision all hosts once
-> run configure.yml
-> validate app/cache/db path
-> rerun configure.yml for idempotency
-> destroy lab resource
```

Guardrails:

- Lab khong thay the staging neu OS image, package repo, network, secret va capacity khac production.
- Dung placeholder IP/hostname trong docs; khong copy IP/public host tu source.
- `vagrant destroy` hoac VM delete la destructive voi lab data; chi chay khi da xac nhan khong can giu state.

## Cloud Provisioner Pattern

Provider-specific provisioner thuong chay tren `localhost` voi connection local:

```yaml
- name: Provision infrastructure
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Create instances with provider module
      provider_instance:
        name: "{{ item.name }}"
        state: present
      loop: "{{ instances }}"
      register: created_instances

    - name: Add instances to runtime inventory
      add_host:
        name: "{{ item.address }}"
        groups: "{{ item.group }}"
        ansible_user: cloud-user
      loop: "{{ created_instances.results }}"
```

Guardrails:

- Cloud credentials phai den tu secret store/environment duoc bao ve, khong commit vao repo.
- Gan tag/label owner, environment, cost center va TTL neu la ephemeral.
- Dat quota/budget alert khi playbook co the tao nhieu resource.
- Tao resource va configure resource nen co validation rieng; provisioning thanh cong khong co nghia app healthy.
- Provider module/version thay doi theo thoi gian; pin collection va test tren staging truoc production.

## Network And Security Rules

Security group/firewall phai theo least privilege:

| Tier | Inbound nen co |
|---|---|
| Edge/load balancer | 80/443 tu client CIDR, SSH tu admin/bastion |
| App | App port tu edge, SSH tu admin/bastion |
| Cache | Cache port tu app group |
| Database | DB port tu app group hoac db replica group |

Canh bao:

- `0.0.0.0/0` cho SSH/database/cache la risky default, khong nen dung production.
- Neu playbook thay doi firewall/security group, chay `--check --diff` neu module ho tro va co console/bastion rollback path.
- Doi network rule co the lam mat ket noi Ansible; can canary host va out-of-band access.

## Database And Cache Guardrails

Database replication va cache validation can tach khoi demo app:

- Database primary/replica can backup/snapshot truoc thay doi schema/replication.
- User/password database phai tu Vault/secret manager.
- Quyen application user nen toi thieu, khong dung wildcard privilege rong neu khong can.
- Cache service bind all interfaces chi an toan khi network/firewall gioi han source ro.
- Validation nen dung read-only query/health check truoc khi chay task co write.

## Idempotency Va Drift

Sau provision/configure:

```bash
ansible-playbook -i inventories/staging/hosts.ini configure.yml --check --diff
ansible-playbook -i inventories/staging/hosts.ini configure.yml
ansible-playbook -i inventories/staging/hosts.ini configure.yml
```

Ky vong:

- Lan dau co `changed` hop ly.
- Lan hai it hoac khong co `changed`.
- Health checks pass.
- Inventory va provider resource list khop voi topology mong doi.

Neu resource bi xoa ngoai band, Ansible co the tao lai neu playbook provisioner duoc viet idempotent. Nhung production can phan biet:

- Recreate stateless app node: thuong chap nhan duoc neu co image/config san.
- Recreate database/cache stateful node: can backup, restore, replication catch-up va data-loss review.

## Cleanup Va Destroy

Destructive operations phai tach ro khoi normal configure path.

Khong nen doi `state: present` sang `state: absent` trong cung file production roi chay lai neu khong co approval. Thay vao do:

- Tao playbook cleanup rieng.
- Yeu cau confirm variable nhu `confirm_destroy: true`.
- Dung `--limit` va environment non-prod truoc.
- Snapshot/backup stateful resource.
- Validate resource da xoa dung scope va khong con DNS/LB target treo.

Canh bao:

```text
Destroy/delete cloud instances, disks, databases, load balancers or security groups
co the gay downtime va mat du lieu. Luon co approval, backup va rollback/restore plan.
```

## Checklist Production

Truoc khi chay multi-tier provisioning/configuration:

- Provider credentials va secret da duoc lay tu secret store.
- Roles/collections da pin version.
- Inventory/provisioned hosts co tag environment ro.
- Security rules theo least privilege, khong expose DB/cache ra Internet.
- `--list-hosts`, `--list-tasks`, `--check --diff` da chay cho configure path.
- Stateful services co backup/snapshot va restore path.
- Load balancer co health check va canary/serial strategy.
- Cleanup/destroy path tach khoi normal apply.

## Trang Lien Quan

- [Ansible](./overview.md)
- [Inventory Patterns](./04-inventory-patterns.md)
- [Roles, Includes And Galaxy](./03-roles-includes-and-galaxy.md)
