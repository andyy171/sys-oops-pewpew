# Ansible Docker Container Automation

## Overview

Ansible co the quan ly Docker theo hai huong:

- provision Docker host, cai package, daemon config, user/group, firewall, log rotation;
- goi Docker API de build image, pull image, tao container, publish port, mount volume va kiem tra trang thai.

Trong production hien dai, Ansible thuong phu hop nhat cho host bootstrap va orchestration nho. Voi multi-container application, uu tien Docker Compose cho single-host workflow, Kubernetes/Swarm cho orchestration nhieu host, va CI build system cho image build repeatable.

## Mental Model

```text
Ansible control node
-> Docker module / Docker API
-> Docker daemon on target
-> image / container / volume / network state
```

Docker daemon la privileged boundary. User co quyen thao tac Docker socket gan nhu co quyen root tren host.

## When To Use

Dung Ansible voi Docker khi:

- bootstrap Docker host va daemon baseline;
- chay container agent nho tren fleet;
- tao lab/demo lap lai duoc;
- validate container runtime state sau provision;
- migrate script `docker run` roi rac thanh desired state co review.

Can can nhac cong cu khac khi:

- app co nhieu service, network, volume va env phuc tap: Docker Compose;
- can HA, scheduling, rolling update, service discovery nhieu node: Kubernetes/Swarm;
- can image build/promotion chuan: CI pipeline + Dockerfile/BuildKit.

## Build Image With Ansible

Ansible co the build image tu Dockerfile, nhung production pipeline nen dam bao image build reproducible:

- Dockerfile nam trong Git;
- base image pinned tag/digest;
- `.dockerignore` loai secret/artifact thua;
- tag theo Git SHA/build ID, khong dung `latest` lam identity production;
- scan image truoc khi push/promote;
- push vao private registry neu deploy nhieu host.

Dung `docker commit` hoac build image tu container da sua tay chi nen la lab/debug. No kho review, kho rebuild va de dua drift thu cong vao production.

## Configuration Management Inside Image Build

Dockerfile khong thay the hoan toan configuration management. Ve ban chat, Dockerfile la recipe dong goi image; ben trong recipe co the goi Makefile, shell script, Ansible, Chef hoac Puppet neu team da co logic cau hinh san.

Pattern hop ly:

- dung Makefile/script de gom task build, test, render template, tao build context nho va goi `docker build`;
- dung Ansible/Chef de generate config hoac cai package trong build stage khi logic da ton tai va co test;
- chuyen output cuoi ve Dockerfile/multi-stage build co the lap lai;
- luu tat ca file build orchestration trong Git va review nhu code.

Guardrails:

- Khong de tool CM tai secret vao image layer. Dung CI secret store, BuildKit secret mount hoac runtime secret.
- Khong dung playbook/recipe "snowflake server" de tao image production neu khong co lockfile, version pin va test.
- Neu tool CM cai dependency tu internet, pin version/repository va scan image sau build.
- Build phai tao artifact immutable tag/digest; khong deploy image sinh tu container da sua tay.
- Neu build script sinh Dockerfile tam, pipeline phai luu/log duoc Dockerfile rendered de audit.

## Run Container With Ansible

Desired state toi thieu can mo ta ro:

- image/tag/digest;
- container name;
- command/entrypoint neu override;
- published ports;
- env/config/secret source;
- volume/network;
- restart policy;
- health/validation.

Validation read-only:

```bash
docker ps --filter name=<container>
docker inspect <container>
docker logs --tail 100 <container>
docker port <container>
```

## Data, Volume Va Secret

Khong coi container writable layer la noi luu du lieu. Database, upload va state can named volume hoac storage backend ro rang.

Legacy pattern `volumes_from` hoac "data container" co the gap trong he cu/lab. Production nen khai bao named volume truc tiep de de audit, backup va restore.

Secret guardrails:

- khong hard-code password/token trong playbook, inventory, Dockerfile hay command line;
- dung Ansible Vault, CI secret store, Docker/Kubernetes secret hoac secret manager;
- tranh in env secret ra log;
- rotate token neu nghi ngo log/history da lo.

## Docker Connection Plugin Pattern

Ansible co the dung Docker connection plugin de chay task ben trong container. Pattern nay huu ich cho lab hoac build customization dac biet, nhung can than:

- container can co Python/dependency phu hop cho module Ansible;
- task chay trong container khong tu dong la best practice Dockerfile;
- ket qua image build bang `docker commit` kho reproduce hon Dockerfile;
- clean package cache, tool build va Ansible dependency neu tao runtime image.

Voi production image, uu tien Dockerfile/multi-stage build. Neu dung Ansible de generate file/config luc build, ghi ro vi sao Dockerfile/template thong thuong khong du.

## Production Guardrails

- Khong mount `/var/run/docker.sock` vao container CI/CD neu chua chap nhan rui ro root-equivalent.
- Khong publish database port ra `0.0.0.0` neu khong co firewall/TLS/auth policy.
- Khong dung `state: absent`, image/container prune hoac volume prune tren production neu chua co backup/rollback.
- Pin Docker SDK/collection version dung trong automation.
- Chay `--check --diff` khi module ho tro, nhung khong gia dinh Docker module nao cung dry-run day du.
- Validate app health tu client path, khong chi container status `running`.

## Troubleshooting

| Symptom | Checks |
|---|---|
| Module import fail | Python interpreter, Docker SDK, execution environment/collection |
| Permission denied | user trong group `docker`, `become`, socket permission, rootless mode |
| Container exited | `docker logs`, `docker inspect`, command/entrypoint, exit code |
| Port khong vao duoc | `docker port`, app listen address, host firewall, security group |
| Mat data sau recreate | volume mount path, named volume, bind mount, backup |
| Image build khong update | build context, cache, tag immutable, registry pull policy |

## Related Pages

- [Ansible Overview](./overview.md)
- [Ansible CI And Testing](./07-ci-and-testing.md)
- [Docker Practice And Operations Patterns](../../../03-compute-and-orchestration/02-container-runtime/06-docker-practice-and-operations-patterns.md)
- [Image Layer, Dockerfile Best Practices](../../../03-compute-and-orchestration/02-container-runtime/Image%20layer,%20Dockerfile%20best%20practices.md)
- [Docker Volumes, Bind Mount Va tmpfs](../../../03-compute-and-orchestration/02-container-runtime/04-Volumes,%20Bind%20mount,%20tmpfs.md)
