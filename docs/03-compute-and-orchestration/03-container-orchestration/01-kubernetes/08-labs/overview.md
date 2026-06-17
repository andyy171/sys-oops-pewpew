# Kubernetes Labs

## Purpose

Labs giúp biến concept Kubernetes thành thao tác kiểm chứng được. Mỗi lab phải có goal rõ, precheck, validation và cleanup. Không dùng lab như runbook production nếu chưa bổ sung backup, rollback và change approval.

## What You Should Understand After This Section

- Cách tạo workload và đọc trạng thái qua Pod/ReplicaSet/Deployment.
- Cách Service, DNS, Ingress và EndpointSlice nối traffic tới Pod.
- Cách PVC/StatefulSet biểu diễn storage identity.
- Cách RBAC/ServiceAccount giới hạn quyền API.
- Cách probes, HPA và PDB ảnh hưởng vận hành ngày 2.
- Cách render/diff/apply manifest bằng Kustomize/GitOps-style workflow.

## Reading Order

1. [Core Workload Lab](./01-core-workload-lab.md)
2. [Networking Service, Ingress Và DNS Lab](./02-networking-service-ingress-dns-lab.md)
3. [Storage PVC Và StatefulSet Lab](./03-storage-pvc-statefulset-lab.md)
4. [Security RBAC Và ServiceAccount Lab](./04-security-rbac-serviceaccount-lab.md)
5. [Operations HPA, Probes Và PDB Lab](./05-operations-hpa-probes-pdb-lab.md)
6. [Packaging Và GitOps Lab](./06-packaging-gitops-lab.md)

## Knowledge Map

| Lab | Related theory | Why It Matters |
|---|---|---|
| Core workload | `01-core-objects` | Hiểu controller tạo và thay thế Pod như thế nào |
| Networking | `02-networking` | Debug traffic bằng Service, EndpointSlice, DNS và Ingress |
| Storage | `03-storage` | Thấy PVC/PV/StatefulSet khác Deployment stateless ra sao |
| Security | `04-security` | Hiểu RBAC không phải network policy hay Pod security |
| Operations | `05-operations` | Nhìn probes/HPA/PDB qua events và status |
| Packaging/GitOps | `06-packaging-and-gitops` | Thực hành source of truth, render, diff, apply |

## Prerequisites

- Một cluster lab local như kind, minikube hoặc cluster sandbox.
- `kubectl` trỏ đúng context lab.
- Không chạy lab trên production namespace.

## Safety Notes

- Dùng namespace riêng như `k8s-lab`.
- Kiểm tra context trước khi apply:

```bash
kubectl config current-context
kubectl get ns
```

- Cleanup sau lab:

```bash
kubectl delete ns k8s-lab
```

## Related Sections

- [Kubernetes Overview](../overview.md)
- [Troubleshooting Runbooks](../98-troubleshooting/overview.md)
