# Ansible Inventory Patterns

## Cach Hieu Nhanh

Inventory la source of truth cho viec Ansible se tac dong vao host nao, theo group nao, va voi bien ket noi/cau hinh nao. Sai inventory thuong nguy hiem hon sai task, vi task dung co the chay tren sai host.

Mental model:

```text
static inventory / dynamic inventory
-> host groups and children groups
-> group_vars / host_vars
-> play hosts selector
-> --limit / tags / serial
-> target hosts touched by playbook
```

Trong production, inventory phai duoc review nhu code ha tang.

## Static Inventory

Inventory co ban gom group va host:

```ini
[web]
web-1.example.com
web-2.example.com

[db]
db-1.example.com

[web:vars]
ansible_user=deploy
```

Group nen mo ta vai tro hoac ownership that, khong chi la danh sach host tam thoi:

- `web`, `app`, `db`, `cache`, `logging`, `backup`.
- `prod`, `staging`, `dev` khi can tach environment.
- `ubuntu`, `rhel` neu playbook co OS-specific path.

Guardrails:

- Khong dat password, token, private key noi dung secret trong inventory.
- Bien inline tren host chi nen dung cho connection override nho nhu user/port.
- Inventory static phai co convention dat ten group ro, tranh group qua rong nhu `all-prod-change`.

## Children Groups

Children groups giup tao abstraction tren nhieu group con:

```ini
[app]
app-1.example.com
app-2.example.com

[worker]
worker-1.example.com

[linux:children]
app
worker

[prod:children]
app
worker
```

Gia tri:

- Chay baseline role tren tat ca Linux host.
- Chay patch theo OS family hoac environment.
- Mo ta kien truc ma khong lap lai host o nhieu noi.

Rui ro:

- Group cha qua rong co the lam playbook tac dong nhieu host hon du kien.
- Truoc production run, luon kiem tra:

```bash
ansible-playbook -i inventories/prod site.yml --list-hosts
ansible-playbook -i inventories/prod site.yml --list-tasks
```

## Environment Inventories

Nen tach inventory theo environment de cung mot playbook co the chay voi cau hinh khac:

```text
ansible/
  inventories/
    dev/
      hosts.ini
      group_vars/
    staging/
      hosts.ini
      group_vars/
    prod/
      hosts.ini
      group_vars/
  site.yml
```

Run:

```bash
ansible-playbook -i inventories/dev/hosts.ini site.yml
ansible-playbook -i inventories/prod/hosts.ini site.yml --check --diff --limit app-1.example.com
```

Guardrails:

- Ten inventory path phai ro environment.
- CI/CD nen yeu cau approval rieng cho inventory production.
- Khong de command mac dinh tro vao production inventory.
- Review diff cua inventory cung voi diff playbook/role.

## Inventory Variables

Dung `host_vars` va `group_vars` de tach cau hinh khoi architecture definition.

```text
inventories/prod/
  hosts.ini
  group_vars/
    all.yml
    web.yml
    db.yml
  host_vars/
    db-1.example.com.yml
```

Vi du `group_vars/web.yml`:

```yaml
---
app_port: 8080
app_log_level: info
```

Vi du `host_vars/db-1.example.com.yml`:

```yaml
---
db_memory_profile: large
```

Guardrails:

- `group_vars` cho cau hinh chung theo role/group.
- `host_vars` chi cho ngoai le that su; qua nhieu host override la dau hieu role interface chua tot.
- `group_vars/all.yml` nen gon, vi no tac dong moi host.
- Secret trong `group_vars`/`host_vars` phai duoc ma hoa bang Ansible Vault hoac lay tu secret manager.

## Dynamic Inventory

Dynamic inventory phu hop khi host duoc tao/xoa lien tuc boi cloud, autoscaling, CMDB, virtualization platform hoac internal API.

Workflow:

```text
cloud/CMDB/API
-> inventory plugin/script
-> JSON inventory groups + hostvars
-> ansible-playbook
-> runtime target hosts
```

Safe checks:

```bash
ansible-inventory -i inventory.dynamic.yml --list
ansible-inventory -i inventory.dynamic.yml --graph
ansible all -i inventory.dynamic.yml -m ping --limit app
```

Guardrails:

- Token/API key cho inventory phai nam trong secret store hoac environment duoc bao ve, khong commit vao repo.
- Cache inventory neu API cham hoac rate-limited, nhung phai hieu TTL de tranh deploy vao host da bi xoa/doi role.
- Grouping rule cua dynamic inventory phai deterministic va review duoc.
- Khong tin tag cloud mot cach mu quang; tag sai co the dua host vao group sai.
- Truoc thay doi production, compare `ansible-inventory --graph` voi ky vong.

## Add Host Va Group By

`add_host` them host vao in-memory inventory trong cung playbook run. Pattern nay huu ich khi playbook vua provision host moi, vua configure host do.

```yaml
- name: Add newly provisioned host to runtime group
  add_host:
    name: "{{ new_host_ip }}"
    groups: new_app
    ansible_user: deploy
  changed_when: false

- name: Configure new app hosts
  hosts: new_app
  gather_facts: false
  tasks:
    - name: Wait for SSH
      wait_for:
        host: "{{ inventory_hostname }}"
        port: 22
        timeout: 300
      delegate_to: localhost
```

`group_by` tao group runtime dua tren facts:

```yaml
- name: Group hosts by architecture
  group_by:
    key: "architecture_{{ ansible_machine }}"
```

Guardrails:

- `add_host` chi thay doi inventory trong memory cua run hien tai; khong thay the inventory source of truth.
- Sau provisioning, can wait/readiness check truoc khi configure.
- Cloud create/delete la thao tac co chi phi va rui ro; dung tag/TTL, quota guardrail va cleanup plan.
- Lenh xoa instance, destroy VM hoac delete resource phai co approval, backup/retention policy va validation sau cleanup.

## Mixed Inventory Sources

Ansible co the nhan mot directory inventory gom static files va executable/dynamic inventory. Pattern nay huu ich khi ha tang co nhieu provider.

Guardrails:

- Khong de file tam, backup, output debug hoac script khong lien quan trong inventory directory.
- Moi executable trong inventory directory co the duoc Ansible chay; review permission va noi dung script.
- Dat convention ro: static file, plugin config, generated cache, secrets khong nam chung lung tung.

## Custom Dynamic Inventory

Custom dynamic inventory can output JSON voi group, hosts, vars va `_meta.hostvars`.

Minimal shape:

```json
{
  "app": {
    "hosts": ["app-1.example.com"],
    "vars": {
      "ansible_user": "deploy"
    }
  },
  "_meta": {
    "hostvars": {
      "app-1.example.com": {
        "app_port": 8080
      }
    }
  }
}
```

Production guardrails:

- Script inventory phai co authn/authz ro khi goi API/CMDB.
- Dung HTTPS/TLS va validate certificate khi lay inventory qua network.
- Log audit cho ai/automation nao truy van inventory nhay cam.
- Khong output private token, cloud secret, customer data hoac metadata khong can cho Ansible.
- Test `--list` trong CI va fail neu JSON invalid, group rong bat thuong hoac host nam sai environment.

## Checklist Production

Truoc khi chay playbook voi inventory production:

```bash
ansible-inventory -i inventories/prod/hosts.ini --graph
ansible-playbook -i inventories/prod/hosts.ini site.yml --list-hosts
ansible-playbook -i inventories/prod/hosts.ini site.yml --check --diff --limit app-1.example.com
```

Checklist:

- Inventory target dung environment.
- `--list-hosts` khop voi blast radius mong doi.
- Dynamic inventory da refresh va khong stale.
- Group/children khong vo tinh gom them host khac role.
- Secret khong nam trong inventory plaintext.
- Host key checking khong bi disable trong production run binh thuong.

## Trang Lien Quan

- [Ansible](./overview.md)
- [Ansible Playbook Advanced Patterns](./02-playbook-advanced-patterns.md)
- [Ansible Roles, Includes And Galaxy](./03-roles-includes-and-galaxy.md)
