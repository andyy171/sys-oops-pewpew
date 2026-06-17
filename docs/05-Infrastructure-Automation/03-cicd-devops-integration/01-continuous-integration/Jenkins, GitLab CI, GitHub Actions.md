# Jenkins, GitLab CI, GitHub Actions

## Overview

Jenkins, GitLab CI va GitHub Actions deu la CI/CD runners: chung nhan trigger tu Git/event/manual action, chay job theo pipeline definition, quan ly secret/credential, luu log va tra ket qua. Khac biet UI/plugin/syntax co the thay doi theo thoi gian; mental model on dinh hon la:

```text
source event
-> runner/job
-> workspace
-> credentials
-> build/test/deploy command
-> artifact/log/result
```

## Khi Dung Cho Infrastructure Automation

Khi pipeline chay Ansible, Terraform, Helm hoac script van hanh, no khong con la "build server" don thuan. Runner tro thanh automation control point co quyen thay doi ha tang.

Can thiet ke:

- source code va pipeline-as-code duoc review;
- credential tach theo environment;
- job production can approval/manual gate khi rui ro cao;
- log co commit, actor, target inventory/environment va result;
- runner khong dung chung credential admin dai han;
- secret khong xuat hien trong console output.

## Jenkins

Jenkins manh o plugin ecosystem va kha nang tuy bien. Khi dung Jenkins de chay Ansible:

- cai Ansible/collection trong agent image hoac toolchain duoc pin;
- dung credential binding/secret store, khong hard-code SSH key/password trong job;
- workspace nen clean giua builds neu co secret/artifact nhay cam;
- console log co the lo bien moi truong, nen mask secret va tranh `set -x` quanh lenh nhay cam;
- job deploy production can RBAC va approval rieng.

Example stage logic:

```text
checkout
-> install/pin dependencies
-> ansible-playbook --syntax-check
-> ansible-lint
-> ansible-playbook --check --diff on safe target
-> approval
-> ansible-playbook with --limit/serial
-> post-run validation
```

### Jenkins Chay Trong Container

Chay Jenkins controller trong container co the giup dong goi version/plugin va backup/restore de hon host install thu cong. Tuy nhien, controller van la stateful service: `JENKINS_HOME`, plugin set, credential store va job config phai duoc backup, versioned policy va test upgrade.

Guardrails:

- Pin Jenkins image tag/digest; khong tu dong keo `latest` vao production.
- Mount `JENKINS_HOME` vao volume/path duoc backup; test restore dinh ky.
- Quan ly plugin bang file/pipeline co review; plugin update co the break job.
- Khong mount `/var/run/docker.sock` vao Jenkins controller neu chua chap nhan rui ro root-equivalent tren host.
- Neu Jenkins can build image, uu tien agent rieng, rootless/buildkit builder, remote builder hoac Kubernetes agent co RBAC rieng.

### Jenkins Agent Trong Container

Containerized agent giup moi team co toolchain rieng ma khong lam ban build host chung. Agent image nen mo ta ro runtime, compiler, browser, cloud CLI va test tool can dung.

Production guardrails:

- Khong hard-code password/SSH key trong Dockerfile agent; dung Jenkins credentials hoac secret manager.
- Khong tat SSH host key verification cho agent production. Neu dung SSH agent, pin host key hoac dung mechanism inbound agent/WebSocket/Kubernetes agent phu hop hon.
- Dung label agent de match job voi tai nguyen thuc te nhu CPU/RAM/GPU/browser, khong de job nang chay tren laptop/dev workstation tuy tien.
- Workspace can duoc clean giua builds neu co secret, artifact nhay cam hoac dependency khong tin cay.
- Neu agent duoc phep truy cap Docker socket, coi job tren agent co quyen host-admin; tach agent build image khoi agent deploy production.

### Jenkins Upgrade Runbook

Upgrade Jenkins container can tach ro image version va state trong `JENKINS_HOME`.

Pre-check:

```bash
docker ps --filter name=jenkins
docker image inspect <jenkins-image>:<target-tag>
docker logs --tail 200 jenkins
```

Truoc upgrade:

- backup `JENKINS_HOME` va xac minh co the restore;
- export/plugin list va note Jenkins/plugin version hien tai;
- test upgrade tren clone cua `JENKINS_HOME` neu Jenkins quan trong;
- doc release note/plugin compatibility voi target version.

Validation sau upgrade:

- Jenkins UI/API len duoc;
- agent reconnect duoc;
- credential binding van hoat dong;
- mot pipeline smoke test build/test/publish chay thanh cong;
- log khong co migration/plugin error nghiem trong.

Rollback: stop container moi, restore `JENKINS_HOME` backup neu da migration state, chay lai image cu da pin. Khong xoa container/image cu cho den khi upgrade da qua validation va backup moi da san sang.

## GitLab CI Va GitHub Actions

GitLab CI va GitHub Actions thuong gan chat voi repository. Diem can quan tam:

- branch/tag/environment rules;
- protected environments;
- ephemeral runner vs self-hosted runner;
- secret scope theo repo/project/environment;
- artifact/cache retention;
- audit trail cua ai approve/deploy.

Self-hosted runner co the truy cap private network nen phai duoc harden nhu server production: patching, log, least privilege, secret cleanup va network egress control.

## Common Failure Modes

| Symptom | Likely Cause | Guardrail |
|---|---|---|
| Pipeline xanh nhung deploy sai target | inventory/environment variable sai | `--list-hosts`, protected environment, approval |
| Secret lo trong log | shell debug hoac echo bien | secret masking, khong dung `set -x`, review script |
| Runner deploy qua nhieu scope | credential qua rong | least privilege, split credential per environment |
| Build phu thuoc plugin/image latest | dependency khong pin | pin agent image, role/collection/plugin version |
| Job khong audit duoc ai lam gi | manual shell tren runner | pipeline-as-code, job log, approval record |

## Related Pages

- [Pipeline Stages: Build, Test, Deploy](./02-Pipeline%20stages%20build,%20test,%20deploy.md)
- [Secrets handling in CI/CD](../02-continuous-delivery-and-deployment/03-Secrets%20handling%20in%20CI%20CD.md)
- [Ansible CI And Testing](../../07-configuration-management/01-ansible/07-ci-and-testing.md)
