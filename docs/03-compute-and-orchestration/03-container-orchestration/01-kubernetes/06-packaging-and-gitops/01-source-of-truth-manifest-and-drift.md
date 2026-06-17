# Kubernetes Source Of Truth, Manifest Và Drift

## Why This Exists

Kubernetes cluster lưu desired state trong API server/etcd, nhưng production không nên chỉ dựa vào live cluster state. Nếu thay đổi chỉ nằm trong cluster qua `kubectl edit`, `kubectl patch` hoặc một pipeline không ghi lại manifest, team sẽ mất khả năng review, audit, tái tạo môi trường và rollback đáng tin.

Source of truth là nơi team tuyên bố "đây là trạng thái mong muốn": thường là Git repository chứa manifest, Helm values, Kustomize overlay hoặc cấu hình GitOps.

## Mental Model

```text
Git / manifest repository
-> review
-> render / validate
-> diff
-> apply hoặc GitOps sync
-> observe cluster state
-> reconcile drift
```

Cluster state là actual state đang chạy. Git/manifest là desired state có chủ sở hữu, lịch sử và quy trình review.

## Core Objects / Components Involved

- Manifest YAML: Deployment, Service, ConfigMap, Secret reference, Ingress, RBAC, HPA, PDB.
- Render tool: Helm, Kustomize hoặc pipeline build manifest.
- Apply path: `kubectl apply`, CI/CD, Argo CD, Flux.
- Diff path: `kubectl diff`, GitOps diff, admission/policy validation.
- Audit path: Git history, Kubernetes audit log, event/log/metric.

## How It Works

Thay đổi bền vững nên đi qua Git:

1. Developer hoặc platform engineer sửa manifest/values/overlay.
2. Pull request review owner, risk và policy.
3. Pipeline render manifest cuối cùng.
4. Pipeline validate schema, policy, namespace, labels, resource requests và secret references.
5. Diff trước khi apply/sync.
6. Apply hoặc để GitOps controller reconcile.
7. Quan sát rollout, events, metrics, logs và alerts.

Nếu cần hotfix bằng `kubectl`, xem đó là thao tác tạm thời. Sau hotfix phải đưa thay đổi về Git hoặc revert cluster về Git để tránh drift lâu dài.

## Minimal Example

```bash
kubectl diff -f manifests/
kubectl apply -f manifests/
kubectl rollout status deployment/<name> -n <namespace>
```

Với GitOps, thao tác thường là merge PR rồi quan sát sync status:

```bash
kubectl get applications -n argocd
kubectl describe application <app> -n argocd
```

## How To Inspect

```bash
kubectl get deploy,svc,cm,secret,ingress -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl diff -f manifests/
kubectl rollout history deployment/<name> -n <namespace>
```

Với GitOps, kiểm tra:

- app có `OutOfSync` không;
- object nào khác Git;
- controller có bị thiếu RBAC không;
- webhook/admission có mutate object khiến diff lặp lại không.

## Common Confusions

| Confusion | Reality |
|---|---|
| `kubectl apply` một lần là đủ | Nếu manifest không nằm trong source of truth, lần apply đó không tạo được governance lâu dài |
| Cluster là source of truth | Cluster là nơi chạy actual state; source of truth cần audit/review/reproduce |
| Drift luôn xấu | Một số drift do controller/admission mutate là expected; drift không được quản lý mới nguy hiểm |
| Rollback chỉ cần undo Deployment | Config, Secret, database migration, external dependency và feature flag có thể không rollback theo Pod template |

## Production Notes

- Không dùng image tag mutable như `latest` cho production release.
- Gắn label/annotation owner, app, environment, managed-by.
- Tránh nhiều tool cùng quản lý một object/field nếu không có ownership boundary.
- Không commit secret plaintext vào Git; dùng secret manager, sealed secret hoặc external secret pattern tùy platform.
- Luôn có diff/review trước thay đổi rộng.
- Ghi rõ ai được phép hotfix và bước đưa hotfix về Git.

## Related Pages

- [GitOps, Argo CD, Flux Và Reconciliation](./04-gitops-argocd-flux-and-reconciliation.md)
- [Environment Promotion, Release Và Rollback](./05-environment-promotion-release-and-rollback.md)
- [Workload Controllers Và Rollout](../01-core-objects/02-workload-controllers-and-rollout.md)
