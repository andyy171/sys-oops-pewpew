# Secrets Handling In CI/CD

## Overview

CI/CD secrets la credential cho SCM, artifact registry, cloud provider, Kubernetes, database, chat/webhook hoac deployment target. Neu pipeline bi compromise, secret trong runner, environment, log, artifact hoac cache co the tro thanh duong lateral movement vao production.

## Principles

- Secret khong nam trong Git, Dockerfile, artifact, image layer, log hoac command history.
- Moi credential co scope nho: repo, environment, namespace, registry, project.
- Tach credential build, publish, deploy va read-only.
- Uu tien short-lived credential/OIDC federation thay vi token dai han.
- Secret rotation phai duoc test bang rollout thuc.

## Common Leak Paths

| Leak path | Guardrail |
|---|---|
| Environment variable bi print | mask secret, cam debug `env/printenv`, review script |
| Pipeline log | log redaction, khong echo secret, restrict log access |
| Artifact/cache | scan artifact, khong archive workspace nguyen ven |
| Docker build arg/layer | dung secret mount cua builder hoac fetch runtime secret |
| Kubeconfig/cloud key trong runner | short-lived token, least privilege, revoke nhanh |
| Private repo history | secret scanning, pre-commit hook, rotate neu da commit |

## Docker Image Layer Leak Response

Neu secret da vao Docker build context hoac image layer, viec `rm` file o layer sau khong xoa duoc secret khoi history. Xu ly nhu incident:

- revoke/rotate secret truoc;
- xoa image/tag bi anh huong khoi registry va cache theo quy trinh;
- rebuild image tu Dockerfile sach, dung BuildKit secret mount hoac runtime secret;
- scan lai image/artifact/log de xac nhan secret khong con xuat hien;
- ghi nhan commit/pipeline run nao da tao artifact loi de truy vet moi truong da deploy.

Khong coi `docker export | docker import` hoac flatten image la bien phap remediation du cho production, vi no khong giai quyet credential da lo va co the lam mat provenance/audit metadata.

Image squash co the lam gon layer hoac che bot history cua mot image cu, nhung khong phai bien phap xu ly secret da lo. Neu secret tung nam trong build context, Dockerfile, build log, registry cache hoac runner workspace, phai rotate secret va truy vet artifact da publish truoc. Chi dung squash/flatten nhu buoc migration co kiem soat sau khi da xu ly incident, va phai chap nhan rang provenance, SBOM, cache behavior va audit metadata co the bi mat.

## Production Controls

- Bat secret scanning cho repo va pull request.
- Require approval khi workflow thay doi cach doc/inject secret.
- Khong cap secret production cho PR tu fork/untrusted branch.
- Dung environment protection cho production deploy.
- Audit ai/commit/workflow da doc hoac dung deploy credential neu platform ho tro.
- Rotate token khi runner, repo, dependency hoac artifact bi nghi compromise.

## Validation

```bash
git log --all --stat
git grep -n "TOKEN\\|PASSWORD\\|SECRET\\|PRIVATE_KEY"
```

Khong dua ket qua co secret that vao ticket/log chung. Neu tim thay secret that, xu ly nhu incident: revoke/rotate truoc, sau do clean history theo quy trinh.

## Related Pages

- [CI/CD Threat Model And Attack Surface](../03-automation-pipeline-security/04-ci-cd-threat-model-and-attack-surface.md)
- [Pipeline Stages Build, Test, Deploy](../01-continuous-integration/02-Pipeline%20stages%20build,%20test,%20deploy.md)
