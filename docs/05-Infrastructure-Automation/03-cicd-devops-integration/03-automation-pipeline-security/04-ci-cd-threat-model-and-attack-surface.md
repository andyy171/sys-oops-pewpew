# CI/CD Threat Model And Attack Surface

## Overview

CI/CD pipeline la mot control plane cua delivery. Neu attacker chiem duoc pipeline, tac dong khong dung o build fail: ho co the thay doi source, artifacts, image registry, deployment target, logs, secrets va cloud/Kubernetes resources ma pipeline duoc phep truy cap.

Mental model:

```text
SCM / pull request
-> pipeline definition
-> runner / agent
-> dependency source
-> build artifact / image registry
-> deployment credential
-> runtime environment
-> logs / audit trail
```

Bao mat pipeline phai coi moi hop trong flow nay la trust boundary.

## Threat Map

| Attack surface | Risk | Defensive control |
|---|---|---|
| SCM token, PAT, SSH key | Clone repo, push code, bypass review | least privilege token, SSO/MFA, short-lived credential, secret scanning |
| Pipeline definition | Pipeline poisoning qua PR/config change | protected branches, required review, CODEOWNERS, restrict workflow change |
| Build script/test script | Indirect poisoning qua Makefile/test/helper script | review script path, pin tools, run untrusted PR with restricted token |
| Dependency source | dependency confusion, typosquatting, package takeover | private registry priority, lockfile, allowlist, SBOM, dependency review |
| Artifact storage | artifact injection or tampering | immutable artifact, checksum/signature, provenance, retention policy |
| Image registry | malicious image push or tag overwrite | immutable tags, digest pinning, signing, registry RBAC, scan gate |
| Runner/agent host | credential theft, lateral movement, crypto mining, local DoS | ephemeral runner, isolation, patching, egress control, resource quota |
| Deployment credential | spread to cloud/Kubernetes/prod resources | environment-scoped identity, JIT/short-lived token, RBAC, approvals |
| Logs | secret leakage or evidence tampering | mask secrets, immutable log shipping, audit trail, restricted log write/delete |

## Pipeline Poisoning

Pipeline poisoning xay ra khi thay doi trong repo hoac trong script duoc pipeline tin tuong lam runner thuc thi logic khong mong muon.

Phan biet:

- Direct poisoning: thay doi file pipeline nhu `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`.
- Indirect poisoning: thay doi script ma pipeline goi, vi du `Makefile`, `scripts/deploy.sh`, test helper, build tool wrapper.
- Public pipeline poisoning: open-source PR/fork lam pipeline chay voi quyen cao hon muc can thiet.

Guardrails:

- Workflow/pipeline file can owner review rieng.
- Pull request tu fork/untrusted user khong duoc nhan secret hoac token ghi.
- Tach job build/test untrusted khoi job deploy/publish trusted.
- Pin action/plugin/tool version theo tag/digest/commit, khong dung floating ref neu risk cao.
- Log ro commit SHA, actor, workflow version va artifact digest sinh ra.

## Secrets And Credentials

Pipeline credential la blast radius chinh. Tranh de mot token lam du ca build, push image, deploy production va doc secrets.

Controls:

- Tach credential theo environment va purpose: read repo, push artifact, deploy staging, deploy prod.
- Dung OIDC federation/short-lived token voi cloud provider neu co.
- Khong in environment variables, token, kubeconfig, SAS/SPN/API key ra log.
- Masking log chi la lop giam thiet hai, khong phai secret control chinh.
- Rotate/revoke token ngay khi repo, runner hoac pipeline bi compromise.

## Artifact, Registry And Provenance

Artifact va image phai tra loi duoc: "ai build, tu commit nao, bang workflow nao, da qua gate nao, digest nao dang chay".

Controls:

- build once, promote same artifact;
- immutable version/tag or digest pinning;
- checksum/signature/provenance;
- restrict overwrite/delete in registry;
- retention policy cho rollback;
- scan image/dependency/IaC truoc deploy;
- alert khi image tag production bi overwrite hoac artifact bi replace.

## Runner And Environment Isolation

Runner la compute thuc thi code do repo/pipeline cung cap, nen phai coi no la untrusted execution boundary.

Guardrails:

- Uu tien ephemeral runner cho workload untrusted.
- Khong reuse runner workspace giua repo/moi truong co trust level khac nhau.
- Han che network egress tu runner den metadata service, internal admin endpoint va production data plane.
- Khong mount Docker socket hoac cloud credential rong vao job neu khong can.
- Dat resource limit/timeout de giam crypto mining, DDoS va local DoS.
- Ship runner logs/audit ra he thong khong bi job ghi de.

### Containerized Runner / Jenkins Agent

Chay runner/agent trong container giup dong goi toolchain va scale nhanh, nhung khong tu dong tao security boundary manh. Ranh gioi thuc su phu thuoc vao quyen duoc mount/cap cho container.

High-risk patterns:

- mount `/var/run/docker.sock` vao agent de build image;
- mount workspace/cache dung chung giua repo hoac trust level khac nhau;
- agent co credential deploy production trong khi chay job build/test untrusted;
- SSH agent voi host key verification bi tat;
- long-lived agent tren laptop/dev workstation co network/secret ca nhan.

Guardrails:

- Tach agent build, scan, publish va deploy theo credential rieng.
- Uu tien ephemeral agent/runner cho job untrusted hoac PR tu fork.
- Neu can Docker build, dung builder co isolation ro nhu remote BuildKit, rootless builder, Kubernetes build pod hoac dedicated build host.
- Lam sach workspace/cache giua jobs; cache phai keyed theo lockfile/checksum va khong chua secret.
- Dat resource limit, timeout va network egress policy cho agent.
- Ghi log agent identity, label, image digest, job id va commit SHA de truy vet.

## Detection Signals

Can alert hoac review khi co:

- workflow/pipeline file thay doi ngoai owner expected;
- branch protection, required review, required status check bi tat/sua;
- token moi duoc tao, scope token tang, credential dung tu runner la;
- artifact/image tag production bi push lai;
- runner goi metadata service bat thuong;
- job co egress bat thuong den domain la;
- log bi xoa/sua hoac thieu bat thuong;
- pipeline doc/clone repo ngoai scope expected;
- deploy credential dung ngoai pipeline chuan.

## Incident Response Checklist

Khi nghi pipeline bi compromise:

1. Tam dung pipeline/deploy job co lien quan.
2. Revoke token, PAT, SSH key, cloud credential, registry credential va kubeconfig lien quan.
3. Freeze hoac snapshot logs, workflow run metadata, artifact digest, registry event va audit log.
4. Xac dinh commit/workflow/runner bi anh huong.
5. Kiem tra artifact/image da publish trong thoi gian compromise.
6. Rebuild artifact tu commit trusted tren runner sach.
7. Rotate secret co the da lo trong repo, logs, artifact hoac image layer.
8. Restore branch protection va required checks.
9. Them detection/control de ngan lap lai.

## Related Pages

- [Pipeline Stages Build, Test, Deploy](../01-continuous-integration/02-Pipeline%20stages%20build,%20test,%20deploy.md)
- [Secrets handling in CI/CD](../02-continuous-delivery-and-deployment/03-Secrets%20handling%20in%20CI%20CD.md)
- [SBOM & dependency tracking](./SBOM%20&%20dependency%20tracking.md)
- [Image scanning](./01-Image%20scanning.md)
