# Kubernetes Packaging Và GitOps Lab

## Goal

Thực hành source-of-truth workflow tối giản bằng Kustomize: render, diff, apply, thay đổi overlay và quan sát rollout.

## What You Will Learn

- Manifest trong folder là desired state có thể review.
- `kubectl diff -k` giúp thấy thay đổi trước khi apply.
- Overlay tách biến thể môi trường khỏi base.

## Topology

```text
base/
-> overlays/dev
-> render
-> diff
-> apply
-> observe
```

## Prerequisites

- Cluster lab.
- `kubectl` hỗ trợ Kustomize.

## Safety Notes

Dùng namespace `k8s-lab`. Không apply overlay lab vào production cluster.

## Steps

Tạo cấu trúc local:

```text
apps/web/base/
apps/web/overlays/dev/
```

Base gồm Deployment và Service. Overlay dev set namespace và replica.

Render và apply:

```bash
kubectl kustomize apps/web/overlays/dev
kubectl diff -k apps/web/overlays/dev
kubectl apply -k apps/web/overlays/dev
kubectl rollout status deployment/web -n k8s-lab
```

## Validation

```bash
kubectl get deploy,svc,pod -n k8s-lab
kubectl describe deploy web -n k8s-lab
```

## Cleanup

```bash
kubectl delete -k apps/web/overlays/dev
kubectl delete ns k8s-lab
```

## Common Failure Cases

- Overlay thiếu namespace nên apply vào namespace hiện tại.
- Patch không match object name.
- Service selector không match Deployment label.
- Diff khác liên tục do controller/admission mutate field.

## Related Theory

- [Source Of Truth, Manifest Và Drift](../06-packaging-and-gitops/01-source-of-truth-manifest-and-drift.md)
- [Kustomize Base, Overlay Và Patch](../06-packaging-and-gitops/03-kustomize-base-overlay-and-patch.md)
