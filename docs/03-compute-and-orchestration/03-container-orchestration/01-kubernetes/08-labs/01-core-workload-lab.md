# Kubernetes Core Workload Lab

## Goal

Tạo một Deployment đơn giản, quan sát Deployment tạo ReplicaSet và Pod, sau đó rollout image mới và rollback.

## What You Will Learn

- Pod là runtime unit; Deployment là desired state bền vững.
- ReplicaSet giữ số replica theo selector.
- Readiness ảnh hưởng việc Pod có được xem là available hay không.

## Topology

```text
Deployment
-> ReplicaSet
-> Pods
```

## Prerequisites

- Cluster lab.
- `kubectl` dùng context lab.

## Safety Notes

Không chạy lab trong namespace production.

## Steps

```bash
kubectl create ns k8s-lab
kubectl create deployment web --image=nginx:1.25 -n k8s-lab --replicas=2
kubectl get deploy,rs,pod -n k8s-lab -o wide
kubectl rollout status deployment/web -n k8s-lab
```

Rollout image mới:

```bash
kubectl set image deployment/web nginx=nginx:1.26 -n k8s-lab
kubectl rollout status deployment/web -n k8s-lab
kubectl rollout history deployment/web -n k8s-lab
```

Rollback:

```bash
kubectl rollout undo deployment/web -n k8s-lab
kubectl rollout status deployment/web -n k8s-lab
```

## Validation

```bash
kubectl get deploy web -n k8s-lab
kubectl get rs -n k8s-lab
kubectl get pod -n k8s-lab -o wide
```

## Cleanup

```bash
kubectl delete ns k8s-lab
```

## Common Failure Cases

- Image pull fail do tag sai hoặc không có internet/registry access.
- Pod Pending do node thiếu tài nguyên.
- Rollout kẹt do readiness probe sai trong lab mở rộng.

## Related Theory

- [Pods, Labels, Namespaces Và Metadata](../01-core-objects/01-pods-labels-namespaces-and-metadata.md)
- [Workload Controllers Và Rollout](../01-core-objects/02-workload-controllers-and-rollout.md)
