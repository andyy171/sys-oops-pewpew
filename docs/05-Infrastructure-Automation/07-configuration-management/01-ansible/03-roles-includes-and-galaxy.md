# Ansible Roles, Includes And Galaxy

## Cach Hieu Nhanh

Khi playbook lon dan, van de khong con la "Ansible co lam duoc khong" ma la "team co doc, review, test va tai su dung duoc khong". Includes tach task theo cum logic; roles dong goi mot nang luc cau hinh thanh interface co defaults, vars, handlers, files va templates.

Mental model:

```text
site playbook
-> import/include playbooks or tasks
-> roles
-> role defaults/vars/tasks/handlers/templates
-> module execution on target hosts
```

Dung organization pattern de lam playbook ngan gon hon, nhung khong nen tach file qua som khi logic chua on dinh.

## Import Tasks Vs Include Tasks

Tach task thanh file rieng khi mot cum task co muc dich ro, vi du `users.yml`, `apache.yml`, `backup.yml`.

| Pattern | Cach hieu | Nen dung khi |
|---|---|---|
| `import_tasks` | Static import, duoc mo rong truoc khi play chay | File task co the biet truoc, logic gan nhu inline |
| `include_tasks` | Dynamic include trong luc play dang chay | Ten file/pham vi phu thuoc variable, fact, `register` hoac condition runtime |
| `import_playbook` | Import playbook o top-level | Ghep nhieu playbook thanh entrypoint chung |

Vi du dynamic include:

```yaml
- name: Check OS-specific task file
  stat:
    path: "tasks/setup-{{ ansible_os_family }}.yml"
  register: os_task_file
  connection: local
  changed_when: false

- name: Include OS-specific setup
  include_tasks: "tasks/setup-{{ ansible_os_family }}.yml"
  when: os_task_file.stat.exists
```

Guardrails:

- Dat ten task file theo muc dich, khong theo thu tu tam thoi.
- Neu dung `include_tasks` voi ten file dong, validate file ton tai va gioi han gia tri variable dau vao.
- Dung `--list-tasks` de xem task nao se chay truoc production run.
- Neu tach qua nhieu file nho, reviewer se mat context; tach theo cum logic co ownership ro.

## Handler Va Playbook Imports

Handlers co the dat trong file rieng de main playbook tap trung vao workflow:

```yaml
handlers:
  - import_tasks: handlers/main.yml
```

Top-level playbook co the gom nhieu playbook:

```yaml
- import_playbook: baseline.yml
- import_playbook: web.yml
- import_playbook: db.yml
```

Production guardrails:

- Entry point tong nhu `site.yml` phai co scope ro; khong de mot lenh vo tinh thay doi toan bo fleet.
- Truoc khi chay playbook tong, dung `--list-hosts`, `--list-tasks`, `--check --diff` neu module ho tro.
- Handlers restart/reload service nen co health check va rollback/roll-forward plan neu anh huong traffic.

## Role Structure

Role la don vi tai su dung cho mot concern: package repo, firewall, nginx, app deploy, logging agent, backup agent.

Role toi thieu:

```text
roles/
  role_name/
    tasks/
      main.yml
    meta/
      main.yml
```

Role thuc te thuong co them:

```text
roles/
  role_name/
    defaults/
      main.yml
    vars/
      main.yml
    handlers/
      main.yml
    files/
      example.conf
    templates/
      example.conf.j2
    tasks/
      main.yml
    meta/
      main.yml
```

Playbook goi role:

```yaml
- name: Configure app servers
  hosts: app
  become: true
  pre_tasks:
    - name: Check package manager connectivity
      command: true
      changed_when: false
  roles:
    - baseline
    - app_runtime
  tasks:
    - name: Validate application service
      command: systemctl is-active app
      changed_when: false
```

## Defaults Vs Vars

`defaults/main.yml` la interface mac dinh cua role. Dat gia tri co the override o day.

```yaml
app_packages:
  - app-runtime
app_service_name: app
```

`vars/main.yml` co precedence cao hon va nen dung tiet kiem cho gia tri noi bo gan nhu khong muon caller override.

Guardrails:

- Neu user cua role can thay doi gia tri, dat trong `defaults`.
- Dat ten bien co prefix theo role, vi du `nginx_worker_processes`, de tranh collision.
- Khong dat secret trong role defaults/vars; dung Vault hoac secret manager.
- Document variable quan trong trong README cua role neu role duoc dung boi nhieu team.

Khi gia tri phu thuoc OS nhung van can override duoc, dung bien noi bo co prefix nhu `__role_var` trong file vars theo OS, roi set bien public neu caller chua khai bao:

```yaml
- name: Include OS-specific variables
  include_vars: "{{ ansible_os_family }}.yml"

- name: Define package config path
  set_fact:
    app_config_path: "{{ __app_config_path }}"
  when: app_config_path is not defined
```

Pattern nay giu role portable ma van cho phep playbook override bien public. Khong nen dat gia tri caller can override vao `vars/main.yml` vi precedence cao se lam override kho doan.

## Files Va Templates

Dung `files/` cho file tinh, dung `templates/` cho config can bien.

```yaml
- name: Copy static config
  copy:
    src: example.conf
    dest: /etc/example/example.conf
    mode: "0644"

- name: Render managed config
  template:
    src: example.conf.j2
    dest: /etc/example/example.conf
    mode: "0644"
  notify: Restart example
```

Production guardrails:

- Voi config quan trong, dung `template` + `notify`, khong restart service ngay trong task.
- Dung `validate` cua module template/copy khi service ho tro command check config.
- Dung `--check --diff` truoc production de review file changes.
- Tranh template qua thong minh; logic phuc tap nen nam trong variables/tasks ro rang.

## Cross-Platform Role

Role portable nen tach bien va task theo OS family/distribution khi khac biet package name, service name, repo hoac path.

```yaml
- name: Include OS-specific variables
  include_vars: "{{ ansible_os_family }}.yml"

- name: Include OS-specific setup
  include_tasks: "setup-{{ ansible_os_family }}.yml"
```

Guardrails:

- Test role tren moi OS family duoc support bang CI/lab.
- Neu `ansible_os_family` co gia tri khong mong doi, fail ro rang thay vi chay mac dinh nguy hiem.
- Giu task cross-platform o `tasks/main.yml`, tach chi phan thuc su khac nhau.
- Dung facts co kiem chung; khong assume moi distro cung service manager/path.

## Ansible Galaxy Va Requirements

Galaxy va community roles giup tai su dung nhanh, nhung trong production phai xem nhu third-party dependency.

Nen quan ly dependency bang file requirements:

```yaml
---
- src: geerlingguy.firewall
  version: "1.0.0"
- src: https://example.com/platform/ansible-role-baseline.git
  name: baseline
  version: "v2.3.0"
```

Install:

```bash
ansible-galaxy install -r requirements.yml
ansible-galaxy list
```

Production guardrails:

- Pin version role/collection; khong de production pull latest khong review.
- Review source, license, issue history va variable defaults cua community role truoc khi dung.
- Mirror hoac vendor role quan trong neu deployment can repeatable va khong phu thuoc Internet.
- Chay role trong lab/staging, sau do `--check --diff --limit` truoc production.
- Khong dua secret vao requirements file hoac URL co token.

`ansible-galaxy remove <role>` xoa role local; chi lam khi da biet playbook nao dang phu thuoc role do.

## Khi Nen Tach Thanh Role

Tach thanh role khi:

- Mot cum task duoc dung lai o nhieu playbook/environment.
- Cac bien cua no co interface ro va co default hop ly.
- Cum task co handlers/templates/files rieng.
- Team can version, test va release rieng cho capability do.

Chua can tach khi:

- Dang thuc nghiem va workflow con doi lien tuc.
- Task chi dung mot lan trong mot playbook nho.
- Viec tach file lam mat context nhieu hon lam ro ownership.

## Checklist Review

Truoc khi merge role/include moi:

- `ansible-playbook --syntax-check` pass.
- `--list-tasks` cho thay task order de hieu.
- Bien override nam o `defaults` neu caller can tuy bien.
- Handler restart/reload co notify ro va health check lien quan.
- Role third-party da pin version va review.
- Secret khong nam trong role, requirements, inventory plaintext hay CI log.

## Trang Lien Quan

- [Ansible](./overview.md)
- [Ansible Playbook Advanced Patterns](./02-playbook-advanced-patterns.md)
