# Ansible

## Tong Quan

Ansible la automation/configuration management tool dung SSH hoac connection plugin phu hop de chay task tren nhieu host ma khong can agent thuong tru tren managed node. Gia tri chinh cua Ansible khong nam o viec chay lenh nhanh hon, ma o viec bien thao tac van hanh thanh desired state co the review, chay lai va kiem chung.

Mental model:

```text
Inventory
-> playbook / ad-hoc command
-> module execution over SSH or plugin
-> remote host state
-> changed/ok/failed result
```

## Khi Nen Dung

- Chuan hoa cau hinh package, file, user, service va firewall.
- Bootstrap VM hoac bare-metal sau khi ha tang duoc cap phat.
- Chay runbook lap lai tren nhieu host.
- Deploy application don gian hoac agent van hanh.
- Kiem tra nhanh trang thai fleet bang ad-hoc command read-only.

Khong nen dung Ansible nhu mot tap shell script khong idempotent. Neu task co module chuan, uu tien module thay vi `shell` hoac `command`.

## Inventory Co Ban

Inventory anh xa host vao group va chua thong tin connection toi thieu:

```ini
[linux]
node-1 ansible_host=10.0.0.10 ansible_user=ubuntu
node-2 ansible_host=10.0.0.11 ansible_user=ubuntu

[linux:vars]
ansible_python_interpreter=/usr/bin/python3
```

Guardrails:

- Khong dat password, private key hoac token truc tiep trong inventory.
- Tach inventory theo environment nhu `dev`, `staging`, `prod`.
- Dung `group_vars`/`host_vars` cho cau hinh, nhung giu secret trong Ansible Vault hoac secret manager.
- Voi production, inventory phai duoc review nhu code vi no quyet dinh host nao bi tac dong.

## Ad-Hoc Command

Ad-hoc command huu ich cho kiem tra nhanh hoac thao tac nho:

```bash
ansible linux -i inventory.ini -m ping
ansible linux -i inventory.ini -m command -a "uptime"
ansible linux -i inventory.ini -m command -a "df -h"
```

Production guardrails:

- Uu tien read-only command truoc khi thay doi.
- Dung `--limit` de thu hep blast radius.
- Dung `command` thay vi `shell` neu khong can pipe, redirect, glob hoac shell expansion.
- Khi can privilege escalation, dung `--become` ro rang va log lai command da chay.
- Khong chay ad-hoc destructive command tren broad group neu chua co approval, backup/rollback va validation plan.

Ad-hoc command nen duoc xem la operational probe hoac thao tac khan cap nho, khong phai noi luu tru cau hinh dai han. Neu thay minh lap lai cung nhom lenh, chuyen chung thanh playbook co `name`, variables, handler va validation.

## Ad-Hoc Operations Guardrails

### Parallelism Va Forks

Ansible chay tren nhieu host song song theo so forks. Dieu nay nhanh hon SSH tung may, nhung cung co the tao spike len package repo, database, load balancer hoac network.

```bash
ansible linux -i inventory.ini -m command -a "hostname" --forks 1
ansible linux -i inventory.ini -m command -a "hostname" --forks 10
```

Guardrails:

- Dung `--forks 1` hoac `serial` trong playbook khi thao tac can thu tu ro.
- Tang forks dan dan khi fleet lon, theo doi latency/error cua downstream.
- Khong chay patch/restart dong loat tren toan bo production group neu service khong co HA.

### Targeting Va Limit

Dung inventory group de mo ta ownership va vai tro, vi du `app`, `db`, `linux`, `prod`. `--limit` huu ich cho canary hoac mot host dang incident, nhung neu dung lap lai cung pattern thi nen tao group ro rang.

```bash
ansible app -i inventory.ini -m command -a "uptime" --limit node-1
```

### Module Thay Vi Shell

Uu tien module idempotent:

```bash
ansible linux -i inventory.ini -b -m package -a "name=git state=present"
ansible linux -i inventory.ini -b -m service -a "name=nginx state=started enabled=true"
ansible linux -i inventory.ini -b -m cron -a "name='daily-job' hour=4 job='/usr/local/bin/job.sh'"
```

Can canh bao ro voi:

- `state=absent` tren `user`, `file`, `package`, `cron`.
- Restart/reload service tren nhieu host.
- Firewall rule thay doi, dac biet flush rule.
- Package upgrade toan he thong.
- Command co pipe/redirect/glob can `shell`.

Truoc khi thay doi production, chay read-only check:

```bash
ansible linux -i inventory.ini -m command -a "systemctl is-active nginx"
ansible linux -i inventory.ini -m command -a "df -h"
ansible linux -i inventory.ini -m command -a "free -m"
```

### Async Jobs

Tac vu lau nhu patching, backup, migration hoac report lon co the chay async:

```bash
ansible linux -i inventory.ini -b -B 3600 -P 0 -m command -a "dnf -y update"
ansible linux -i inventory.ini -b -m async_status -a "jid=<JOB_ID>"
```

Production guardrails:

- Luu `JOB_ID`, inventory, command va thoi diem chay.
- Co alert/log rieng cho job fail; khong de async task "ban ra roi quen".
- Voi patching production, can backup, maintenance window, canary, reboot plan va rollback/restore plan.

### Log Checks

Ad-hoc log check phu hop cho mau nho:

```bash
ansible linux -i inventory.ini -b -m command -a "tail /var/log/messages"
```

Khong dung Ansible de stream `tail -f` lau dai hoac `cat` file log lon tren nhieu host. Dung logging stack tap trung neu can dieu tra tren nhieu may; Ansible chi nen la cong cu triage nhanh.

## Idempotency

Idempotency nghia la chay cung automation nhieu lan van dua he thong ve cung trang thai, khong tao side effect thua. Day la khac biet lon giua configuration management va shell script thu cong.

Vi du:

- `package: state=present` chi cai package neu thieu.
- `service: state=started enabled=true` chi thay doi khi service chua dung trang thai.
- `template` chi bao changed khi noi dung file render thay doi.

Voi task khong idempotent san, can dung guard nhu `creates`, `removes`, `changed_when`, `failed_when` hoac dieu kien `when`. Neu khong the chung minh idempotent, coi task do la risky operation va chay theo canary/maintenance window.

## Playbook Structure

Playbook la noi luu desired state co the review. Mot playbook co ban nen doc duoc nhu runbook:

```yaml
- name: Configure web servers
  hosts: web
  become: true
  vars_files:
    - vars.yml
  pre_tasks:
    - name: Refresh package metadata if needed
      package:
        update_cache: true
  tasks:
    - name: Ensure nginx is installed
      package:
        name: nginx
        state: present
  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

Playbook production nen co:

- `name` ro cho play va task de log/doc ket qua de hieu.
- `hosts` khong qua rong; dung inventory group co y nghia.
- `become` ro rang, tranh privilege escalation ngam.
- `vars_files`/`group_vars` cho cau hinh, secret tach rieng.
- `pre_tasks` cho dieu kien nen nhu package metadata hoac pre-check.
- `handlers` cho restart/reload chi khi config thay doi.

## Running Playbooks Safely

Truoc khi chay production:

```bash
ansible-playbook -i inventory.ini site.yml --list-hosts
ansible-playbook -i inventory.ini site.yml --check --diff --limit node-1
ansible-playbook -i inventory.ini site.yml --limit web
```

Guardrails:

- `--list-hosts` de xac nhan blast radius.
- `--check --diff` de xem thay doi du kien neu module ho tro.
- `--limit` cho canary hoac mot nhom nho.
- `--forks` phu hop voi suc chiu cua dependency.
- Khong dua password bang `--extra-vars` trong shell history; dung prompt, Vault hoac secret manager.

## Modules Va File Changes

Dung module co y nghia thay vi shell script:

| Need | Module / pattern |
|---|---|
| Package | `package`, `apt`, `yum` |
| Service | `service`, `systemd` |
| File copy nho | `copy` |
| Config render | `template` |
| Mot dong config | `lineinfile` |
| Download artifact | `get_url` voi checksum |
| Extract archive | `unarchive` |
| Git checkout | `git` voi branch/tag/commit ro |

Neu download artifact quan trong, dung checksum. Neu chay installer/script bat buoc, dung `creates`/`removes` de tranh chay lai vo han:

```yaml
- name: Run installer only once
  command: /opt/app/install.sh
  args:
    creates: /opt/app/.installed
```

Voi config service, dung `template` + `notify` thay vi restart ngay lap tuc:

```yaml
- name: Render service config
  template:
    src: app.conf.j2
    dest: /etc/app/app.conf
  notify: Restart app
```

## Handler Guardrails

Handler chay mot lan o cuoi play neu duoc notify. Dieu nay giup gom nhieu thay doi config thanh mot lan restart/reload.

Can chu y:

- Handler khong chay neu task notify bi skip.
- Handler co the khong chay neu play fail truoc khi toi cuoi play.
- Dung `--force-handlers` chi khi da hieu rui ro, vi service co the restart sau mot play fail.
- Restart service production nen co health check va rollback/canary neu anh huong traffic.

## Local Infrastructure Testing

Playbook nen duoc test tren moi truong local/lab truoc khi chay vao production. Vagrant, VM, container hoac ephemeral cloud instance co the dung de tao "infrastructure-in-a-box" cho team lap lai test nhanh.

Workflow an toan:

```text
local VM / ephemeral host
-> run playbook
-> inspect ok/changed/failed
-> rerun de kiem tra idempotency
-> destroy lab resource khi xong
```

Vagrant co the goi Ansible provisioner de chay playbook khi `vagrant up` hoac `vagrant provision`. Gia tri cua pattern nay la feedback loop ngan: sua playbook, tao lai VM, chay lai automation va xac minh task co idempotent khong.

Guardrails:

- Khong coi lab VM la production-equivalent neu OS, package repo, network, secret va capacity khac production.
- Giu Vagrantfile/playbook trong Git de review thay doi ha tang nhu code.
- Chay lai playbook lan thu hai; neu con `changed` bat thuong thi can xem lai idempotency.
- Lenh `vagrant destroy` xoa VM local; chi dung voi lab resource va dam bao khong co du lieu can giu.
- Neu test tren cloud instance tinh phi theo gio, gan tag/TTL va cleanup de tranh roi resource.

## Cai Dat Va Version

Khong hard-code huong dan cai dat theo mot ban phan phoi cu. Voi moi truong that:

- Pin version Ansible/collection theo project.
- Uu tien virtual environment, execution environment hoac container de co lap dependency.
- Kiem tra `ansible --version` trong CI va tren control node.
- Doc release note truoc khi nang major version hoac collection quan trong.

### Control Node Tren Windows Workstation

Ansible control node nen chay trong moi truong Linux/Unix-like on dinh. Tren Windows workstation, uu tien WSL, Linux VM, dev container hoac execution environment thay vi co gang chay Ansible native neu toolchain khong on dinh.

Guardrails:

- Giu playbook/inventory trong Git va chay tu filesystem co permission/line ending on dinh.
- Can than khi dung path Windows mount vao WSL/VM vi permission, symlink va line ending co the lam task sai khac.
- Khong dung default insecure Vagrant key/VM lab cho production target.
- Pin Ansible/collection trong virtual environment hoac execution environment; khong cai global bang `sudo pip` tren control node production.
- Neu workstation chi la client, can nhac runner tap trung nhu AWX/Tower/CI de co audit, RBAC, secret handling va log tap trung.

## Core Notes

- [Playbook Advanced Patterns](./02-playbook-advanced-patterns.md): variables, facts, Vault, conditionals, delegation, tags, blocks va production safety.
- [Roles, Includes And Galaxy](./03-roles-includes-and-galaxy.md): tach playbook, role structure, defaults/vars, templates, cross-platform role va dependency guardrails.
- [Inventory Patterns](./04-inventory-patterns.md): static/dynamic inventory, environment split, `group_vars`, `host_vars`, `add_host`, `group_by` va target safety.
- [Multi-Tier Infrastructure Provisioning](./05-multi-tier-infrastructure-provisioning.md): pattern local/cloud provisioning, tier configuration, runtime inventory, security rules, idempotency va cleanup safety.
- [Security Hardening Patterns](./06-security-hardening-patterns.md): SSH, sudoers, firewall, patching, logs, fail2ban va SELinux/AppArmor rollout bang Ansible.
- [CI And Testing](./07-ci-and-testing.md): syntax/lint/check mode, role matrix, idempotence, functional tests va runner guardrails.
- [TLS Certificate Automation](./08-tls-certificate-automation.md): self-signed/internal/public certificate workflow, ACME renewal, Nginx TLS termination va HTTPS reverse proxy guardrails.
- [Docker Container Automation](./09-docker-container-automation.md): Docker host bootstrap, image/container state, volume/secret guardrails va Docker connection plugin caveats.
- [Kubernetes Automation](./10-kubernetes-automation.md): cluster bootstrap, Kubernetes API modules, Helm guardrails va `kubectl` connection plugin caveats.

## Related Pages

- [Git va Ansible cho Sysadmin](../../../02-core-infrastructure/01-linux/04-shell-automation-advanced/04-ansible-git-for-sysadmin.md)
- [Configuration Management](../overview.md)
