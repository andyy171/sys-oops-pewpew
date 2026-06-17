# Kubernetes Packaging Và GitOps

## Purpose

Phần này gom các kiến thức về cách biến manifest Kubernetes thành một release workflow có thể review, tái tạo, promote và rollback. Đây là canonical home cho source of truth, Helm, Kustomize, GitOps, drift, environment promotion và release safety.

Cluster setup nằm ở `07-cluster-lifecycle`. Workload controller như Deployment/ReplicaSet nằm ở `01-core-objects`. Phần này tập trung vào cách tổ chức và vận hành thay đổi application trên Kubernetes.

## What You Should Understand After This Section

- Vì sao Git/manifest repository phải là source of truth, không phải cluster live state.
- Khi nào dùng raw manifest, Kustomize, Helm hoặc GitOps controller.
- Drift xảy ra như thế nào và vì sao nó làm rollback kém tin cậy.
- Promotion giữa dev/staging/prod nên promote artifact nào: image digest, chart version, Kustomize base revision, config hay policy.
- Rollback Kubernetes không chỉ là `kubectl rollout undo`; data, config, external dependency và feature flag vẫn cần kế hoạch riêng.

## Reading Order

1. [Source Of Truth, Manifest Và Drift](./01-source-of-truth-manifest-and-drift.md)
2. [Helm Chart, Values Và Template](./02-helm-chart-values-and-template.md)
3. [Kustomize Base, Overlay Và Patch](./03-kustomize-base-overlay-and-patch.md)
4. [GitOps, Argo CD, Flux Và Reconciliation](./04-gitops-argocd-flux-and-reconciliation.md)
5. [Environment Promotion, Release Và Rollback](./05-environment-promotion-release-and-rollback.md)

## Knowledge Map

| Topic | File | Why It Matters |
|---|---|---|
| Source of truth | `01-source-of-truth-manifest-and-drift.md` | Giữ production state có thể review và tái tạo |
| Helm | `02-helm-chart-values-and-template.md` | Đóng gói app có template, values và lifecycle release |
| Kustomize | `03-kustomize-base-overlay-and-patch.md` | Quản lý biến thể môi trường mà không fork toàn bộ YAML |
| GitOps | `04-gitops-argocd-flux-and-reconciliation.md` | Biến Git thành desired state và để controller reconcile cluster |
| Promotion/Rollback | `05-environment-promotion-release-and-rollback.md` | Giảm rủi ro khi đưa thay đổi qua nhiều môi trường |

## Prerequisites

- [Workload Controllers Và Rollout](../01-core-objects/02-workload-controllers-and-rollout.md)
- [Resources, Probes, Autoscaling Và Disruption](../05-operations/01-resources-probes-autoscaling-and-disruption.md)
- [RBAC, Pod Security Và Admission](../04-security/01-rbac-pod-security-and-admission.md)

## Related Sections

- [Deployment Models Và Cluster Setup](../07-cluster-lifecycle/overview.md)
- [Application Integration](../09-application-integration/overview.md)
- [Advanced Platform Patterns](../10-advanced/overview.md)
