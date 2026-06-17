# Ansible CI And Testing

## Overview

Ansible playbook la infrastructure code. CI cho Ansible khong chi kiem tra YAML hop le, ma phai tra loi:

- playbook co parse duoc khong;
- role co chay duoc tren OS/support matrix khong;
- lan chay thu hai co con `changed` bat thuong khong;
- service/config sau khi apply co dung ky vong khong;
- pipeline co credential, approval va audit log phu hop khong.

## Test Layers

| Layer | Muc tieu | Tin hieu |
|---|---|---|
| Syntax | YAML/playbook parse duoc | `ansible-playbook --syntax-check` |
| Lint | Bat deprecated pattern, style, risk | `ansible-lint` hoac policy noi bo |
| Dry run | Xem drift/thay doi du kien | `--check --diff` |
| Integration | Role/playbook chay duoc tren moi truong sach | VM/container/ephemeral host |
| Idempotence | Lan chay thu hai khong doi state bat thuong | recap `changed=0 failed=0` |
| Functional | Service that su hoat dong | HTTP check, port check, command check, serverspec/goss |

Unit test theo nghia application thuong khong phai diem manh cua Ansible. Gia tri lon hon nam o syntax/lint, integration, idempotence va functional checks.

## Built-In Playbook Checks

Pre-merge checks toi thieu:

```bash
ansible-playbook -i inventory.ini site.yml --syntax-check
ansible-playbook -i inventory.ini site.yml --list-hosts
ansible-playbook -i inventory.ini site.yml --list-tasks
ansible-playbook -i inventory.ini site.yml --check --diff --limit node-1
```

`--check` huu ich de phat hien drift va thay doi du kien, nhung khong phai module nao cung support hoan hao. Neu mot task tao bien cho task sau, can can nhac `check_mode: false` cho task read-only can thiet, va ghi ro vi sao.

## Assertions Trong Playbook

`debug`, `fail` va `assert` giup playbook tu validate gia dinh cua no:

```yaml
- name: Fail if required variable is missing
  assert:
    that:
      - app_version is defined
      - app_version | length > 0
    fail_msg: "app_version must be provided"

- name: Check service health endpoint
  uri:
    url: "http://127.0.0.1:8080/healthz"
    status_code: 200
  changed_when: false
```

Guardrails:

- Khong in secret bang `debug`.
- Dung `assert` cho dieu kien bat buoc truoc khi thay doi host.
- Dung `changed_when: false` cho validation/read-only command.
- Validation failure nen dung message hanh dong duoc, khong chi "failed".

## Role Testing Matrix

Role portable can duoc test tren cac OS family/distribution ma no support. Moi truong test co the la:

- local VM/Vagrant;
- ephemeral cloud instance;
- Docker/container co systemd/sysvinit neu role can service manager;
- Molecule scenario.

Container test nhanh va re, nhung khong thay the VM khi role phu thuoc kernel, systemd behavior, storage, network stack, SELinux/AppArmor hoac package repository production.

## Idempotence Test

Pattern co ban:

```text
run role/playbook first time
-> run same role/playbook second time
-> fail if recap shows changed > 0 or failed > 0
```

Khong ep moi task thanh `changed=0` gia. Neu task that su tao side effect moi lan, sua logic bang module idempotent, `creates`, `removes`, `changed_when`, state file hoac pre-check ro rang.

## CI Runner Pattern

Jenkins, GitLab CI, GitHub Actions, AWX/Automation Controller hoac runner khac deu can cung cac guardrails:

- playbook nam trong Git, khong copy thu cong len runner;
- role/collection dependency duoc pin version;
- inventory production can approval rieng;
- credential luu trong secret store cua platform, khong in vao log;
- runner identity co least privilege theo environment;
- job log giu du thong tin: commit, inventory, user, limit, tags, result;
- production apply tach khoi syntax/lint/test gate.

## AWX / Automation Controller

AWX/Automation Controller phu hop khi team can UI, RBAC, job template, credential store, schedule, audit history va inventory/project sync. Dung no de bien playbook run thanh controlled operation:

```text
Git project
-> inventory
-> credential
-> job template
-> approval/schedule/survey if needed
-> job result and audit log
```

Khong bien survey/extra vars thanh noi nhap secret thu cong. Secret phai di qua credential store hoac secret manager.

## Functional Testing Tools

Serverspec, Goss, Molecule hoac script smoke test deu co the dung sau khi Ansible apply xong. Chon tool theo tin hieu can kiem:

- service listen port nao;
- package/file/user co ton tai khong;
- endpoint tra HTTP status nao;
- config render dung khong;
- log khong co error moi.

Functional test can doc nhu production validation, khong chi la "build xanh".

## Related Pages

- [Ansible Overview](./overview.md)
- [Ansible Roles, Includes And Galaxy](./03-roles-includes-and-galaxy.md)
- [Pipeline Stages: Build, Test, Deploy](../../03-cicd-devops-integration/01-continuous-integration/02-Pipeline%20stages%20build,%20test,%20deploy.md)
- [Jenkins, GitLab CI, GitHub Actions](../../03-cicd-devops-integration/01-continuous-integration/Jenkins,%20GitLab%20CI,%20GitHub%20Actions.md)
