# Single Server Deployment Runbook

## Cach Hieu Nhanh

Single-server deployment phu hop cho ung dung nho, internal tool, website it traffic hoac moi truong staging/lab. Rui ro lon nhat la moi thay doi deu tac dong truc tiep den instance duy nhat, nen can pre-check, backup, deploy theo version ro va rollback nhanh.

Mental model:

```text
provision baseline
-> deploy application version
-> run dependency install / migration / asset build
-> restart or reload service
-> smoke test
-> rollback if unhealthy
```

Tach `provision` va `deploy`: provision cai OS/runtime/web server/dependency nen tang; deploy chi doi application version va cac buoc lien quan.

## Workflow

Deployment playbook nen lam cac viec sau:

1. Checkout artifact/code dung version.
2. Render config/secrets tu source an toan.
3. Cai application dependencies.
4. Chay database migration neu can.
5. Build assets/static files neu can.
6. Set ownership/permission.
7. Restart/reload service bang handler khi co thay doi.
8. Chay smoke test.

Vi du skeleton:

```yaml
- name: Deploy application
  hosts: app
  become: true
  vars_files:
    - vars.yml
  tasks:
    - name: Ensure app code is at requested version
      git:
        repo: "https://example.com/app.git"
        version: "{{ app_version }}"
        dest: "{{ app_directory }}"
      register: app_updated
      notify: Restart app

    - name: Render application config
      template:
        src: app.env.j2
        dest: "{{ app_directory }}/.env"
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: "0640"
      notify: Restart app

    - name: Install dependencies when code changed
      command: ./scripts/install-deps.sh
      args:
        chdir: "{{ app_directory }}"
      when: app_updated.changed
      notify: Restart app
```

## Pre-Check

Truoc deploy:

```bash
ansible-playbook -i inventories/prod deploy.yml --list-hosts
ansible-playbook -i inventories/prod deploy.yml --check --diff --limit app-1.example.com
```

Kiem tra:

- `app_version` la tag/commit da build/test.
- Disk con du cho checkout, dependency cache, asset build va log.
- Backup/snapshot da co neu deploy co migration hoac thay doi data.
- Secrets lay tu Vault/secret manager, khong nam trong plaintext vars.
- Service hien tai healthy va co baseline metric/log.
- Rollback version da biet va con artifact/source.

## Secrets

Khong dat secret thang trong `vars.yml` plaintext. Dung:

- Ansible Vault cho vars file ma hoa.
- Secret manager cua platform/cloud/CI.
- File secret render voi permission chat (`0640` hoac nho hon tuy app).

Neu secret da tung commit plaintext, rotate secret va xu ly history theo quy trinh bao mat.

## Database Migration

Migration la phan rui ro nhat cua single-server deployment.

Guardrails:

- Backup database truoc migration.
- Biet migration co backward-compatible voi version cu khong.
- Chay migration dry-run/staging neu framework ho tro.
- Tach migration destructive ra maintenance window.
- Rollback app version khong luon rollback duoc schema/data.

## Validation

Sau deploy:

```bash
systemctl is-active app
curl -fsS http://127.0.0.1:8080/health
journalctl -u app -n 100 --no-pager
```

Validate:

- service active/ready.
- health endpoint pass.
- log khong co error moi.
- migration da xong va app doc/ghi duoc.
- traffic/business flow quan trong hoat dong.

## Rollback

Rollback don gian nhat la deploy lai version truoc:

```bash
ansible-playbook -i inventories/prod deploy.yml -e app_version=<PREVIOUS_VERSION> --limit app-1.example.com
```

Canh bao:

- Khong rollback blindly neu migration da thay doi schema/data khong tuong thich.
- Neu deploy da rotate secret/config, rollback can dung config tuong ung.
- Neu app tao file/generated asset moi, can cleanup neu no gay loi.

## Release Directory Pattern

Voi ung dung can rollback nhanh, dung pattern release directories:

```text
/opt/app/
  releases/
    20260616110000/
    20260616113000/
  shared/
    logs/
    uploads/
  current -> /opt/app/releases/20260616113000
```

Workflow:

```text
create new release dir
-> checkout/copy artifact into release dir
-> link shared files/directories
-> install deps/build assets/migrate if needed
-> switch current symlink atomically
-> reload service
-> smoke test
```

Rollback nhanh co the la tro `current` ve release truoc va reload service. Tuy nhien rollback app code van khong dam bao rollback database schema/data; migration phai co chien luoc rieng.

## Run Once Va Notifications

Mot so task deploy chi nen chay mot lan:

```yaml
- name: Run database migration once
  command: ./scripts/migrate.sh
  args:
    chdir: "{{ app_directory }}"
  run_once: true
  delegate_to: "{{ groups['app'][0] }}"
```

Dung `run_once` + `delegate_to` ro hon pattern `when: inventory_hostname == groups['app'][0]` khi task la thao tac global nhu migration, cache warmup hoac notification.

Deployment tu CI/CD nen co notification o diem bat dau, ket thuc va fail:

- release version.
- environment.
- actor/pipeline id.
- host group/blast radius.
- result va link den log/dashboard.

## Production Guardrails

- Single server khong co capacity du phong; deploy nen co maintenance window neu downtime khong chap nhan.
- Service restart phai qua handler de gom thay doi va tranh restart nhieu lan.
- Khong dung `git force: yes` hoac xoa directory app trong production neu chua biet local change nao se mat.
- Command nhu migration, cleanup, delete cache, reset database can warning va approval rieng.
- Neu deployment lap lai thuong xuyen, dua workflow vao CI/CD voi approval, audit log va artifact immutable.

## Trang Lien Quan

- [Blue/Green, Canary Va Rolling Deployment](./BlueGreen,%20Canary,%20Rolling.md)
- [Secrets handling in CI/CD](./03-Secrets%20handling%20in%20CI%20CD.md)
- [Pipeline Stages: Build, Test, Deploy](../01-continuous-integration/02-Pipeline%20stages%20build,%20test,%20deploy.md)
