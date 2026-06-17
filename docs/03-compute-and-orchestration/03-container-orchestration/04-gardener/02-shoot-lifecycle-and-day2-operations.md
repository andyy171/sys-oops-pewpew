# Gardener Shoot Lifecycle Và Day-2 Operations

## Overview

Shoot là Kubernetes cluster được biểu diễn bằng một custom resource trong Garden cluster. Thay đổi `Shoot.spec` là thay đổi desired state của cả cluster, vì vậy cần coi nó giống thao tác platform change có plan, diff, validation và rollback/migration rõ ràng.

## Lifecycle Map

```text
create Shoot
  -> schedule Seed
  -> reconcile infrastructure
  -> deploy control plane
  -> create worker nodes
  -> run health checks
  -> maintain / upgrade / rotate / hibernate / delete
```

## Các Trạng Thái Cần Theo Dõi

- `status.lastOperation`: operation gần nhất đang chạy, thành công hay lỗi.
- `status.conditions`: health của API server, control plane, system components, nodes.
- Events trong namespace Project: lý do reconcile fail thường nằm ở đây.
- Worker pool status: node count, machine state, OS/image/version.

## Create Shoot Checklist

- Chọn đúng `Project`, `CloudProfile`, region, zone và Kubernetes version.
- Kiểm tra network ranges không overlap với hạ tầng hiện có.
- Xác nhận credentials/provider account có quota và permission phù hợp.
- Chọn worker pool machine type, OS image và autoscaling range hợp lý.
- Xác định HA mode, maintenance window và upgrade policy trước khi tạo.

## Update Shoot Checklist

- Phân biệt field mutable, immutable và one-way.
- Dùng GitOps hoặc review manifest thay vì chỉnh tay không lưu lịch sử.
- Đọc `kubectl diff` nếu workflow cho phép.
- Theo dõi `lastOperation`, condition và event sau khi apply.
- Với thay đổi lớn, chuẩn bị phương án recreate/migrate thay vì ép sửa live cluster.

## Hibernation

Hibernation dùng để tạm dừng Shoot khi không cần chạy workload liên tục, thường để tiết kiệm chi phí môi trường dev/test.

Cần nhớ:

- Không dùng hibernation như backup.
- Stateful workload phải có backup/restore riêng.
- Cron/scheduled hibernation cần tránh khung giờ maintenance hoặc batch job quan trọng.
- Sau khi wake up, kiểm tra node, add-ons, DNS, certificate và workload readiness.

## Deletion

Xóa Shoot là thao tác phá hủy cluster và hạ tầng liên quan.

Pre-check tối thiểu:

- Đã backup workload/stateful data.
- Đã export manifest hoặc Git là source of truth.
- Đã xác nhận owner/team và môi trường.
- Đã kiểm tra finalizer hoặc extension có thể làm deletion kẹt.

## Safe Commands

```bash
kubectl get shoots -A
kubectl describe shoot <shoot-name> -n <project-namespace>
kubectl get events -n <project-namespace> --sort-by=.metadata.creationTimestamp
kubectl get shoot <shoot-name> -n <project-namespace> -o yaml
```

## Related Pages

- [Gardener Architecture And Core Concepts](./01-architecture-and-core-concepts.md)
- [Gardener Observability And Troubleshooting Map](./07-observability-and-troubleshooting-map.md)
- [Shoot Reconcile Failed](./troubleshooting/01-shoot-reconcile-failed.md)
