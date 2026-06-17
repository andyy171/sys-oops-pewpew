# Gardener Backup, Restore, Upgrade Và Maintenance

## Overview

Gardener giúp tự động hóa lifecycle cluster, nhưng không thay thế chiến lược backup, restore và upgrade governance. Cần tách rõ backup cho Gardener landscape, backup control plane của Shoot và backup dữ liệu ứng dụng bên trong Shoot.

## Backup Layers

| Lớp | Cần backup gì |
|---|---|
| Garden cluster | Gardener resources, Project, Shoot specs, credentials metadata |
| Seed cluster | gardenlet config, extension state, Shoot control plane namespaces |
| Shoot control plane | API state/etcd hoặc backup mechanism do Gardener/provider hỗ trợ |
| Workload trong Shoot | Database, PVC, object storage, app config và Git source of truth |

## Upgrade Model

Upgrade thường có nhiều tầng:

- Gardener control plane version.
- gardenlet version.
- provider extension version.
- Seed Kubernetes version.
- Shoot Kubernetes version.
- Worker OS/image/container runtime.
- Add-ons trong Shoot.

Không nên coi upgrade Shoot chỉ là đổi `spec.kubernetes.version`. Phải kiểm tra API deprecation, CNI/CSI, admission policy, CRD, webhook và workload compatibility.

## Maintenance Window

Maintenance window giúp Gardener biết thời điểm phù hợp để chạy một số thao tác tự động như upgrade hoặc maintenance liên quan.

Checklist:

- Chọn khung giờ ít traffic.
- Tránh batch window và backup window.
- Thông báo owner cluster.
- Có alert cho operation kẹt quá lâu.
- Có tiêu chí rollback hoặc pause automation khi gặp lỗi lặp lại.

## Restore Thinking

Câu hỏi cần trả lời trước sự cố:

- Restore Garden có khôi phục được danh sách Shoot không?
- Restore Shoot control plane có giữ đúng worker/node relation không?
- App state nằm trong PVC/database nào và ai chịu trách nhiệm restore?
- DNS/LB/IP có thay đổi sau restore không?
- Có test restore định kỳ không?

## Safe Checks

```bash
kubectl get shoots -A
kubectl describe shoot <shoot-name> -n <project-namespace>
kubectl get events -n <project-namespace> --sort-by=.metadata.creationTimestamp
kubectl get seeds
```

## Related Pages

- [Shoot Lifecycle Và Day-2 Operations](./02-shoot-lifecycle-and-day2-operations.md)
- [Seed Operations Và Capacity](./05-seed-operations-and-capacity.md)
- [Kubernetes Operations, Resources Và Observability](../01-kubernetes/05-operations/overview.md)
