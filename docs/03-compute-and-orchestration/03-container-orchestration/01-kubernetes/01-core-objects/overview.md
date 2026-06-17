# Kubernetes Core Objects

Core objects là lớp cần nắm chắc trước khi đi vào networking, storage, security và operations. Mục tiêu của phần này là hiểu Kubernetes quản lý workload bằng object model và reconciliation, không chỉ nhớ lệnh `kubectl`.

## Reading Order

1. [Kubernetes Operations Quick Reference](./00-kubernetes-operations-quick-reference.md): tra nhanh context, Pod, Deployment, Service, Ingress, ConfigMap, Secret, Namespace và ResourceQuota.
2. [Pods, Labels, Namespaces Và Metadata](./01-pods-labels-namespaces-and-metadata.md): Pod, label/selector, annotation, namespace, metadata, Downward API và probe.
3. [Workload Controllers Và Rollout](./02-workload-controllers-and-rollout.md): Deployment, ReplicaSet, DaemonSet, Job, CronJob, StatefulSet và rollout/rollback.
4. [Workload Design And Best Practices](./03-workload-design-and-best-practices.md): checklist thiết kế workload từ image, config, secret, RBAC, network, rollout đến observability.

## Mental Model

```text
Manifest / kubectl command
-> API server
-> desired state in etcd
-> controller / scheduler decision
-> kubelet on node
-> Pod runtime state
-> status / events / logs / metrics
```

Khi debug core objects, luôn hỏi:

- Object nào giữ intent lâu dài: Pod hay controller?
- Selector có match đúng label của Pod không?
- Desired state đã được API server nhận chưa?
- Scheduler đã chọn node chưa?
- Kubelet đã pull image, mount volume và start container chưa?
- Readiness có cho Pod vào Service endpoint không?

## Object Map

| Object | Dùng để làm gì | Nhầm lẫn phổ biến |
|---|---|---|
| Pod | Đơn vị runtime nhỏ nhất chạy một hoặc nhiều container cùng network namespace | Tạo Pod trần cho workload lâu dài thay vì dùng controller |
| Label / selector | Gắn metadata và chọn tập object | Selector sai làm Service hoặc controller không thấy Pod |
| Namespace | Tổ chức resource, quota và scope tên | Tưởng namespace tự đủ để cô lập bảo mật |
| Deployment | Quản lý ReplicaSet và rolling update cho app stateless | Rollback image nhưng quên state/data/schema bên ngoài |
| ReplicaSet | Đảm bảo số lượng Pod theo selector | Sửa selector/template tùy tiện có thể orphan Pod |
| StatefulSet | Workload cần identity ổn định và storage theo ordinal | Dùng cho database nhưng không thiết kế replication/backup |
| DaemonSet | Chạy Pod trên mỗi node phù hợp | Quên taint/toleration hoặc node selector làm Pod không chạy đủ node |
| Job / CronJob | Task chạy tới completion hoặc theo lịch | Dùng Deployment cho batch job hoặc quên cleanup/history limit |

## Review Checklist

- Phân biệt Pod, controller và container.
- Biết đọc `kubectl describe` và events trước khi đoán nguyên nhân.
- Biết `Ready`, `Running`, `Available`, `Completed`, `CrashLoopBackOff`, `ImagePullBackOff` khác nhau thế nào.
- Biết Service chỉ có backend khi Pod ready và selector match.
- Biết rollout phụ thuộc image pull, readiness probe, resource, scheduling và dependency ngoài cluster.
- Biết khi nào phải dùng Deployment, StatefulSet, DaemonSet, Job hoặc CronJob.
- Biết kiểm tra workload trước production: image tag/digest, probes, requests/limits, Service selector, Secret/RBAC, rollout và observability.

## Related Pages

- [Kubernetes Architecture](../00-architecture/overview.md)
- [Kubernetes Networking, Services Và Ingress](../02-networking/overview.md)
- [Kubernetes Storage, Volumes Và Stateful Workloads](../03-storage/overview.md)
- [Kubernetes Operations, Resources Và Observability](../05-operations/overview.md)
- [Kubernetes Troubleshooting Runbooks](../98-troubleshooting/overview.md)
