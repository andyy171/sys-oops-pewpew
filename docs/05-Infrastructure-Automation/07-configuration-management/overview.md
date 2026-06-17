# Configuration Management

Configuration management la lop tu dong hoa cau hinh ben trong host, service va runtime sau khi ha tang nen da ton tai. Khac voi provisioning thuan tuy, trong tam o day la dua he thong ve desired state lap lai duoc: package, file cau hinh, user, service, firewall, secret reference va quy trinh rollout.

## Khi Dung

- Chuan hoa cau hinh Linux/Windows host.
- Quan ly package, file, template, service va user/group.
- Trien khai application hoac agent len nhieu may.
- Tu dong hoa hardening, patching va operational runbook.
- Ket noi voi CI/CD de kiem tra syntax, dry-run, idempotency va rollout theo lo.

## Cong Cu

- [Ansible](./01-ansible/overview.md)

## Ranh Gioi

- Terraform/OpenTofu va IaC provisioning dat o [Infrastructure as Code](../04-infrastructure-as-code/overview.md).
- Kien thuc Linux host nen tang dat o [Linux](../../02-core-infrastructure/01-linux/overview.md).
- Deployment pipeline va GitOps dat o [CI/CD And DevOps Integration](../03-cicd-devops-integration/overview.md).
