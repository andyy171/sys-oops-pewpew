# Image Scanning And Registry Integrity

## Overview

Image scanning chi la mot phan cua container supply chain security. Production can ket hop scan, immutable tag/digest, registry RBAC, signing/provenance va runtime validation.

## Threats

- Image chua CVE nghiem trong hoac package khong duoc patch.
- Dockerfile copy secret vao image layer.
- Attacker push image doc hai vao registry bang credential pipeline.
- Tag production bi overwrite nhung manifest van tham chieu cung tag.
- Base image bi doi ngoai y muon vi dung floating tag.

## Guardrails

- Dung image tag bat bien hoac digest cho deploy production.
- Pin base image theo version/digest theo policy.
- Scan image trong CI truoc khi push/promote.
- Fail gate theo severity/policy da thong nhat, khong fail tuy tien.
- Han che quyen push/delete/overwrite image trong registry.
- Ky image hoac luu provenance de truy vet commit, builder, workflow va artifact digest.
- Khong luu secret trong Dockerfile, build args, image layer hoac registry metadata.

## Validation

```bash
docker image inspect <image>:<tag>
docker history <image>:<tag>
```

Voi production, uu tien dung scanner/registry policy cua platform va luu ket qua scan gan voi build ID/artifact digest.

## Related Pages

- [CI/CD Threat Model And Attack Surface](./04-ci-cd-threat-model-and-attack-surface.md)
- [Pipeline Stages Build, Test, Deploy](../01-continuous-integration/02-Pipeline%20stages%20build,%20test,%20deploy.md)
- [Image Layer Va Dockerfile Best Practices](../../../03-compute-and-orchestration/02-container-runtime/Image%20layer,%20Dockerfile%20best%20practices.md)
