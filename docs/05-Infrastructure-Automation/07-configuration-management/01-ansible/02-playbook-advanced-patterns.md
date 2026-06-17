# Ansible Playbook Advanced Patterns

## Cach Hieu Nhanh

Playbook nang cao khong chi la them nhieu task. Muc tieu la lam cho automation co the du doan, review duoc, chay lai duoc va giam blast radius khi dung tren production.

Mental model:

```text
inventory
-> variables / facts / vault
-> task condition
-> module result
-> handler / delegation / validation
-> changed/failed signal
```

Neu mot playbook can qua nhieu `shell`, `ignore_errors` hoac bien command-line khong duoc trace, do la dau hieu can thiet ke lai.

## Variables Va Precedence

Dung bien de tach cau hinh khoi logic task. Cac vi tri thuong dung:

| Vi tri | Nen dung cho |
|---|---|
| Role defaults | Gia tri fallback co the override |
| `group_vars` | Cau hinh chung theo nhom host |
| `host_vars` | Ngoai le that su theo host |
| `vars_files` | Cau hinh playbook co version control |
| `vars` trong play/task/block | Gia tri gan voi mot scope nho |
| `register` | Ket qua runtime tu task truoc |
| `--extra-vars` | Override tam thoi, can kiem soat chat |

Guardrails:

- Dat ten bien bang lowercase snake_case, tranh `foo-bar`, `foo.bar`, bien bat dau bang so hoac dau gach duoi.
- Khong nhoi nhieu bien vao inventory inline; dung `group_vars` va `host_vars` de doc va review de hon.
- Giu inventory dong va static inventory cang it bien cang tot, vi bien o day thuong kho nhin khi review playbook.
- Han che `--extra-vars`; no co precedence rat cao va de tao thay doi kho audit.
- Khong truyen password/token bang `--extra-vars` vi de lo trong shell history, CI log hoac process list.

Nen uu tien pattern:

```text
role defaults
-> group_vars / host_vars
-> vars_files reviewed in Git
-> explicit runtime override only for exceptional run
```

## Facts Va Local Facts

Facts la du lieu Ansible thu thap tu managed host, nhu OS family, hostname, interface, memory va disk. Facts huu ich de viet playbook portable:

```yaml
- name: Install package on Debian family
  package:
    name: nginx
    state: present
  when: ansible_os_family == "Debian"
```

Safe checks:

```bash
ansible linux -i inventory.ini -m setup
ansible linux -i inventory.ini -m setup -a "filter=ansible_os_family"
```

Guardrails:

- Chi dat `gather_facts: false` khi playbook khong can facts hoac da co task `setup` rieng.
- Khi fleet da dang OS, hypervisor hoac cloud provider, dung `debug`/`setup` de xac minh fact thuc te truoc khi viet condition.
- Local facts trong `/etc/ansible/facts.d/` phu hop cho thong tin host sinh ra tai runtime, nhung khong nen thay the source of truth tap trung.
- Neu playbook tao local fact va task sau can dung ngay, chay lai `setup` voi filter phu hop de refresh.

## Ansible Vault Va Secret Handling

Secret phai duoc xem la du lieu nhay cam, khong phai bien binh thuong. Lua chon pho bien:

- Secret manager ben ngoai nhu HashiCorp Vault, cloud KMS/Secrets Manager hoac platform secret store.
- Ansible Vault cho file YAML ma hoa nam cung repository playbook.

Production guardrails:

- Khong commit plaintext secret. Neu da commit, rotate secret va xu ly Git history theo quy trinh bao mat.
- Khong commit vault password file.
- Dat permission chat cho password file/script, vi du chi user automation doc duoc.
- Trong CI/CD, lay vault password tu secret store cua pipeline, khong in ra log.
- Tach secret values khoi default config de reviewer co the doc logic ma khong can truy cap secret.

Command an toan de thao tac Vault:

```bash
ansible-vault create group_vars/prod/vault.yml
ansible-vault edit group_vars/prod/vault.yml
ansible-playbook -i inventory.ini site.yml --ask-vault-pass
ansible-playbook -i inventory.ini site.yml --vault-password-file ~/.ansible/vault_pass.txt
```

`ansible-vault decrypt` tao plaintext tren disk; chi dung khi that su can, tranh lam trong working tree production va dam bao cleanup an toan.

## Environment Variables

Co ba lop environment can tach rieng:

| Lop | Cach dung | Luu y |
|---|---|---|
| Task/play environment | `environment:` | Chi anh huong task duoc khai bao |
| User shell environment | `.bash_profile`, `.profile` | Phu thuoc shell/session |
| System-wide environment | `/etc/environment` hoac file service manager | Can `become`, co the anh huong nhieu process |

Vi du proxy theo task:

```yaml
- name: Download artifact through proxy
  get_url:
    url: https://example.com/app.tar.gz
    dest: /tmp/app.tar.gz
    checksum: "sha256:<CHECKSUM>"
  environment:
    http_proxy: http://proxy.example.com:8080/
    https_proxy: http://proxy.example.com:8080/
```

Guardrails:

- Khong dua secret vao environment neu process list, debug log hoac crash dump co the lo gia tri.
- Khi test remote environment bang ad-hoc shell, dung single quote de tranh shell local expand bien truoc:

```bash
ansible node-1 -i inventory.ini -m shell -a 'echo $HTTP_PROXY'
```

- Neu nhieu bien service can stable, uu tien render config/service override bang `template` hon la them nhieu dong `lineinfile`.

## Conditionals Va Runtime Results

`when`, `changed_when`, `failed_when` va `register` giup bien command khong idempotent thanh task co tin hieu ro hon.

Vi du read-only check truoc khi thao tac:

```yaml
- name: Check application status
  command: /usr/local/bin/appctl status
  register: app_status
  changed_when: false

- name: Restart app only when it is unhealthy
  service:
    name: app
    state: restarted
  when: "'unhealthy' in app_status.stdout"
```

Production guardrails:

- Voi `command`/`shell`, dat `changed_when: false` cho check read-only de output khong gay nhieu.
- Dung `failed_when` de mo ta loi that su, nhung khong che loi quan trong chi de playbook xanh.
- `ignore_errors: true` chi nen scope hep va phai co task validation/rescue sau do.
- Neu module co idempotency san, uu tien module thay vi tu viet condition cho shell.

## Delegation Va Local Execution

`delegate_to` va `local_action` dung khi task tac dong len system khac voi host dang duoc configure, vi du load balancer, DNS, monitoring, CMDB hoac control node.

Workflow rolling change an toan:

```text
pre-check host health
-> delegate: remove host from load balancer
-> apply change on host
-> wait_for health/port
-> delegate: add host back to load balancer
-> validate traffic/metrics
```

Guardrails:

- Delegate task thay doi load balancer/DNS phai co rollback ro.
- Dung `serial` de tranh dua ca fleet ra khoi pool cung luc.
- Dung `wait_for` voi timeout huu han, khong dung sleep co dinh khi co the check trang thai that.
- `--connection=local` huu ich cho self-provisioning hoac CI check mode, nhung phai dam bao inventory target dung localhost/127.0.0.1 nhu mong doi.

## Prompts Va Tags

`vars_prompt` phu hop cho gia tri ca nhan hoac interactive run hiem gap. Trong automation production, prompt lam playbook kho chay tu CI/CD va kho lap lai.

Guardrails:

- Uu tien variable file, inventory variable, environment duoc quan ly hoac secret manager thay vi prompt.
- Neu prompt password, dat `private: true`.
- Khong de prompt tro thanh co che secret chinh cho pipeline production.

Tags giup chay subset cua playbook:

```bash
ansible-playbook -i inventory.ini site.yml --tags app
ansible-playbook -i inventory.ini site.yml --skip-tags notifications
```

Rui ro:

- Tags co the bo qua pre-task, dependency hoac validation task neu tagging khong nhat quan.
- Dung tags o muc play/role/task group la chinh; tagging tung task qua day dac lam playbook kho doc.
- Truoc khi chay production voi tags, dung `--list-tasks` va `--list-hosts`.

## Local Workstation Provisioning

Ansible co the chay tren `localhost` de bootstrap workstation, jumpbox hoac control node:

```yaml
- name: Configure local workstation
  hosts: localhost
  connection: local
  gather_facts: true
  vars_files:
    - vars/main.yml
  roles:
    - workstation_packages
  tasks:
    - name: Link managed dotfiles
      file:
        src: "{{ dotfiles_repo }}/{{ item }}"
        dest: "~/{{ item }}"
        state: link
      loop: "{{ dotfiles_files }}"
```

Reusable pattern:

- package manager role cho Homebrew, apt, dnf, Chocolatey hoac winget.
- dotfiles repository lam source of truth cho shell/editor/git config.
- task local chi dung `become` khi can thay doi system path/service.
- secrets cua workstation nhu SSH key, cloud credential, password manager token khong nam trong dotfiles public.

Guardrails:

- Dotfiles automation co the overwrite config ca nhan; backup hoac dry-run/check mode truoc khi link/remove.
- Khong chay script dotfiles bat ky tu Internet tren workstation production/control node neu chua review.
- Neu task can sudo, scope `become: true` theo task, khong bat global neu khong can.
- Workstation automation nen idempotent nhu server automation: chay lan hai khong nen thay doi bat thuong.

## Blocks, Rescue Va Always

Block gom nhom task cung `when`, `become`, tags hoac xu ly loi:

```yaml
- block:
    - name: Apply application config
      template:
        src: app.conf.j2
        dest: /etc/app/app.conf
      notify: Restart app
  rescue:
    - name: Show config failure context
      debug:
        msg: "Config render failed; app was not restarted."
  always:
    - name: Check app service state
      command: systemctl is-active app
      register: app_state
      changed_when: false
      failed_when: false
```

Guardrails:

- Dung `rescue` de cleanup/ghi context, khong de nuot loi khien deployment that bai bi bao thanh cong.
- `always` phu hop cho validation, unlock, remove maintenance flag hoac emit notification.
- Neu co rollback, ghi ro dieu kien kich hoat rollback va validation sau rollback.

## Playbook Readability Va YAML Conventions

Moi task nen co `name` ro khi task co tac dong that, chay lau, hoac co rui ro. Comment chi nen giai thich ly do, risk hoac context khong hien ro tu module/parameter; comment lap lai code se nhanh cu va gay nhieu hon loi.

Khi playbook lon:

- tach task theo cum logic co ownership ro bang `import_tasks`/`include_tasks`;
- tach variable reviewed trong `vars_files`, `group_vars`, `host_vars`;
- giu entrypoint nhu `site.yml` doc duoc nhu workflow tong;
- dung `--list-tasks` de kiem tra thu tu sau khi tach file.

YAML conventions:

- Dung spaces, khong dung tab.
- Quote string de tranh YAML tu ep kieu boolean/number ngoai y muon.
- Voi task co nhieu parameter, uu tien structured YAML multi-line de diff/review ro.
- Dung folded scalar `>` chu yeu cho `command`/`shell` dai; nho rang no noi dong bang space.
- Dung literal scalar `|` khi can giu newline that, vi du config block hoac multiline variable.

Vi du format de review:

```yaml
- name: Render application config
  template:
    src: app.conf.j2
    dest: /etc/app/app.conf
    owner: root
    group: root
    mode: "0644"
  notify: Restart app
```

## Checklist Production

Truoc khi chay playbook nang cao tren production:

```bash
ansible-playbook -i inventory.ini site.yml --list-hosts
ansible-playbook -i inventory.ini site.yml --list-tasks
ansible-playbook -i inventory.ini site.yml --check --diff --limit node-1
```

Checklist:

- Inventory target dung environment va dung host group.
- Secret khong nam trong plaintext, command history hoac CI log.
- Facts/conditionals da duoc test tren it nhat mot host dai dien moi OS/role.
- Tags neu dung khong bo qua pre-check, handler, validation hoac rollback task.
- Restart/reload service co canary, `serial`, health check va rollback/roll-forward plan.
- Delegated task tac dong load balancer/DNS/monitoring co validation rieng.

## Trang Lien Quan

- [Ansible](./overview.md)
