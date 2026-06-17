# Kubernetes Troubleshooting Runbooks

## Overview

Troubleshooting Kubernetes nên đi từ symptom đến control plane decision. Đừng chỉ nhìn log app. Với Kubernetes, nhiều lỗi nằm ở scheduling, image pull, probe, Service selector, EndpointSlice, NetworkPolicy, PVC binding hoặc quota.

Runbook này tổng hợp hướng tiếp cận từ hai nguồn DOCX và gom thành flow vận hành dễ dùng.

## Deep Dive Notes

- [Debug Flow Từ Symptom Đến Control Plane Decision](./01-symptom-to-control-plane-debug-flow.md)
- [Ingress And Service Troubleshooting Lab](./02-ingress-service-troubleshooting-lab.md)

## First Checks

Luôn xác nhận context và namespace:

```bash
kubectl config get-contexts
kubectl config view --minify
kubectl get ns
```

Xem trạng thái tổng quát:

```bash
kubectl get pods -A
kubectl get nodes
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

## Pod Pending

Kiểm tra:

```bash
kubectl describe pod <pod> -n <namespace>
kubectl get events -n <namespace> --sort-by=.metadata.creationTimestamp
kubectl describe nodes | grep -A8 "Allocated resources"
kubectl get quota -n <namespace>
```

Nguyên nhân thường gặp:

- thiếu CPU/memory theo requests,
- nodeSelector/affinity quá chặt,
- taint không có toleration,
- PVC chưa bind,
- quota vượt giới hạn,
- image pull secret/admission bị chặn.

## CrashLoopBackOff

```bash
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace> --previous
kubectl logs <pod> -n <namespace>
```

Hỏi:

- app exit vì config/secret thiếu?
- command/entrypoint sai?
- dependency chưa sẵn sàng?
- liveness probe kill quá sớm?
- memory limit gây OOMKilled?

## ImagePullBackOff

```bash
kubectl describe pod <pod> -n <namespace>
kubectl get secret -n <namespace>
kubectl describe secret <image-pull-secret> -n <namespace>
```

Nguyên nhân:

- image tag không tồn tại,
- registry auth sai,
- secret ở sai namespace,
- node không resolve registry,
- registry certificate/proxy/firewall lỗi.

## Service Không Có Traffic

```bash
kubectl get pod -l app=<app> -o wide -n <namespace>
kubectl describe svc <service> -n <namespace>
kubectl get endpoints <service> -n <namespace>
kubectl get endpointslice -n <namespace> -l kubernetes.io/service-name=<service>
```

Kiểm tra:

- Pod có Ready không.
- Service selector có khớp label Pod không.
- `port` và `targetPort` đúng không.
- NetworkPolicy có chặn không.
- Ingress/Gateway controller có route đúng không.

## Rollout Bị Kẹt

```bash
kubectl rollout status deployment/<name> -n <namespace>
kubectl describe deployment <name> -n <namespace>
kubectl get rs,pod -l app=<app> -n <namespace>
kubectl describe pod <new-pod> -n <namespace>
```

Nguyên nhân:

- new Pod không Ready,
- readiness probe sai,
- image lỗi,
- quota/capacity thiếu,
- `maxUnavailable=0` và `maxSurge` không đủ room,
- PodDisruptionBudget hoặc policy liên quan.

Rollback:

```bash
kubectl rollout history deployment/<name> -n <namespace>
kubectl rollout undo deployment/<name> -n <namespace>
```

## PVC Pending Or Mount Failed

```bash
kubectl get pvc -n <namespace>
kubectl describe pvc <pvc> -n <namespace>
kubectl get storageclass
kubectl describe pod <pod> -n <namespace>
```

Nguyên nhân:

- StorageClass không tồn tại hoặc không default,
- CSI provisioner lỗi,
- access mode không được hỗ trợ,
- volume zone không khớp node,
- quota storage hết,
- reclaim policy/old PV conflict.

## Node NotReady

```bash
kubectl describe node <node>
kubectl get pods -A -o wide --field-selector spec.nodeName=<node>
```

Trên node, nếu có quyền:

```bash
systemctl status kubelet
journalctl -u kubelet -n 200
crictl ps
crictl images
```

Nguyên nhân:

- kubelet down,
- container runtime lỗi,
- disk pressure,
- memory pressure,
- CNI lỗi,
- network tới API Server lỗi,
- certificate/node auth vấn đề.

## Related Pages

- [Image Pull Errors](./image-pull-errors.md)
- [Kubernetes Operations Quick Reference](../01-core-objects/00-kubernetes-operations-quick-reference.md)
- [Kubernetes Networking, Services Và Ingress](../02-networking/overview.md)
- [Kubernetes Storage, Volumes Và Stateful Workloads](../03-storage/overview.md)
- [Kubernetes Operations, Resources Và Observability](../05-operations/overview.md)
