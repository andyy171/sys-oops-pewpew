# Kubernetes Storage, Volumes Và Stateful Workloads

## Overview

Kubernetes làm rất tốt với stateless workload, nhưng storage là phần dễ tạo hiểu lầm nhất. Pod có lifecycle ngắn; dữ liệu quan trọng cần nằm ngoài lifecycle Pod. Volume, PersistentVolume, PersistentVolumeClaim, StorageClass, CSI và StatefulSet là các abstraction để tách app khỏi chi tiết storage backend.

`Kubernetes in Action` đi từ volume chia sẻ trong Pod, `emptyDir`, `hostPath`, PV/PVC, StorageClass và StatefulSet. `Kubernetes Up and Running` bổ sung góc nhìn tích hợp storage solution, service không có selector và stateful app như database.

Đọc sâu: [Persistent Storage Và StatefulSet Deep Dive](./01-persistent-storage-and-statefulsets.md).

## Volume Types

| Loại | Khi dùng | Lưu ý |
|---|---|---|
| `emptyDir` | scratch space, share file giữa container trong cùng Pod | mất khi Pod bị xóa khỏi node |
| `configMap` / `secret` | mount config/secret thành file | không dành cho dữ liệu app |
| `hostPath` | agent/node-level workload cần file node | rủi ro bảo mật, không portable |
| PVC volume | dữ liệu bền cho workload | phụ thuộc storage backend |

`emptyDir` phù hợp cho cache tạm, không phù hợp cho database state cần giữ.

## PersistentVolume Và PersistentVolumeClaim

PV là storage resource trong cluster. PVC là yêu cầu storage từ namespace/user.

```text
Pod -> PVC -> PV -> Storage backend
```

PVC mẫu:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: fast
```

Pod dùng PVC:

```yaml
volumes:
- name: data
  persistentVolumeClaim:
    claimName: data
```

Kiểm tra:

```bash
kubectl get pvc
kubectl describe pvc data
kubectl get pv
```

## StorageClass Và Dynamic Provisioning

StorageClass mô tả loại storage có thể cấp phát động: provisioner, parameter, reclaim policy, expansion support.

```bash
kubectl get storageclass
kubectl describe storageclass <name>
```

Khi PVC được tạo, dynamic provisioner có thể tạo PV tương ứng nếu StorageClass hỗ trợ. Nếu PVC Pending, kiểm tra:

- `storageClassName` có tồn tại không,
- provisioner/CSI driver có chạy không,
- quota hoặc capacity backend có đủ không,
- access mode có được backend hỗ trợ không,
- zone/node affinity của volume có khớp node không.

## Access Modes

| Access mode | Ý nghĩa |
|---|---|
| `ReadWriteOnce` | một node mount read-write |
| `ReadOnlyMany` | nhiều node mount read-only |
| `ReadWriteMany` | nhiều node mount read-write |
| `ReadWriteOncePod` | một Pod duy nhất mount read-write nếu backend/cluster hỗ trợ |

Access mode không tự biến filesystem thành distributed lock. App vẫn phải tương thích với kiểu ghi nhiều node nếu dùng RWX.

## StatefulSet Storage Pattern

StatefulSet thường dùng `volumeClaimTemplates` để mỗi Pod có PVC riêng:

```yaml
volumeClaimTemplates:
- metadata:
    name: data
  spec:
    accessModes:
    - ReadWriteOnce
    resources:
      requests:
        storage: 10Gi
```

Kết quả:

```text
data-db-0
data-db-1
data-db-2
```

Mỗi replica giữ storage identity riêng. Khi Pod `db-1` được recreate, nó gắn lại PVC của `db-1`.

## Stateful App Reality Check

StatefulSet chỉ giải quyết identity và storage attachment. Nó không tự xử lý:

- database replication,
- leader election của app,
- backup/restore,
- schema migration,
- split-brain,
- quorum,
- data corruption,
- cross-zone latency.

Với database quan trọng, cần operator hoặc runbook riêng cho từng engine.

## Services Without Selectors

Service không selector có thể dùng để đưa resource ngoài cluster vào DNS/service model của Kubernetes.

Use case:

- database managed bên ngoài cluster,
- service legacy,
- migration từ outside-in.

Nhưng cần quản lý EndpointSlice/endpoint thủ công hoặc bằng controller riêng. Không nên dùng nếu chỉ để che giấu kiến trúc khó hiểu.

## Backup And Restore Checklist

- Backup application data, không chỉ backup YAML.
- Biết PVC/PV reclaim policy.
- Test restore vào namespace/cluster khác.
- Với StatefulSet, ghi rõ thứ tự restore PVC và workload.
- Với CSI snapshot, kiểm tra VolumeSnapshotClass và quyền restore.
- Không coi replica là backup; replica cũng có thể sao chép lỗi.

## Related Pages

- [Persistent Storage Và StatefulSet Deep Dive](./01-persistent-storage-and-statefulsets.md)
- [Kubernetes Workload Controllers Và Rollout](../01-core-objects/02-workload-controllers-and-rollout.md)
- [Kubernetes Networking, Services Và Ingress](../02-networking/overview.md)
- [Kubernetes Operations, Resources Và Observability](../05-operations/overview.md)
- [Kubernetes Troubleshooting Runbooks](../98-troubleshooting/overview.md)
