# Kubernetes Persistent Storage Và StatefulSet Deep Dive

## Overview

Storage là nơi Kubernetes dễ đánh lừa người học nhất. Kubernetes có thể recreate Pod rất nhanh, nhưng dữ liệu không được recreate kiểu đó. Stateful workload cần xử lý đồng thời identity, storage, DNS, ordering, backup và recovery.

Hai sách cùng nhấn mạnh một điểm: StatefulSet/PVC giúp Kubernetes quản lý identity và volume attachment, nhưng không tự biến database thành HA.

![](./images/kbp2e-stateful-storage-callout.png)

## Storage Object Chain

```text
Pod -> PVC -> PV -> StorageClass/CSI -> Storage backend
```

Trong đó:

- Pod chỉ biết mount volume.
- PVC là yêu cầu storage trong namespace.
- PV là storage resource thực tế hoặc được provision động.
- StorageClass mô tả loại storage và provisioner.
- CSI driver nối Kubernetes với backend storage.

## CSI Control Plane Và Node Path

CSI tách storage vendor khỏi core Kubernetes. Một CSI driver production thường có hai phần:

- **controller side**: provision/delete volume, attach/detach, snapshot/expand tùy driver;
- **node side**: chạy trên từng node để stage/publish volume, mount vào đường dẫn mà kubelet dùng cho Pod.

Luồng đơn giản khi PVC được dùng:

```text
PVC -> external-provisioner tạo PV/backend volume
Pod được schedule
-> attach/detach nếu backend cần
-> CSI node plugin mount/stage volume trên node
-> kubelet bind mount volume vào container
```

Các sidecar như external-provisioner, external-attacher, external-resizer, external-snapshotter là controller phụ trợ quanh CSI driver. Khi PVC `Pending` hoặc Pod `FailedMount`, cần đọc log đúng phía: controller side cho lỗi provision/attach, node side cho lỗi mount/permission/device.

```bash
kubectl get pods -A | grep -i csi
kubectl describe pvc <pvc> -n <namespace>
kubectl describe pod <pod> -n <namespace>
kubectl logs -n <csi-namespace> <csi-controller-pod>
kubectl logs -n <csi-namespace> <csi-node-pod> -c <driver-container>
```

Dynamic provisioning dựa vào CSI nhưng không đồng nghĩa với CSI. Có thể có PV tĩnh, local PV hoặc volume đã tồn tại trước; điều quan trọng là hiểu ai tạo volume, ai attach, ai mount, ai chịu trách nhiệm backup/restore.

## Volume Mounts Và Khi Nào Nên Dùng

Không phải mọi state đều cần PV/PVC. Volume trong Pod có nhiều mục đích khác nhau:

- `emptyDir` cho scratch data hoặc share file giữa sidecar/adapter/ambassador container trong cùng Pod.
- ConfigMap/Secret/projected volume cho config/credential, thường không nên dùng làm app data store.
- `hostPath` cho node agent hoặc trường hợp cần đọc file host có chủ đích.
- PVC cho dữ liệu cần tồn tại ngoài lifecycle Pod.

Nếu ứng dụng chỉ ghi log nghiệp vụ ra local file, lựa chọn tốt hơn thường là sửa app ghi ra `stdout`/`stderr` hoặc dùng sidecar/log agent có boundary rõ. Đừng dùng PV chỉ để giữ log nếu hệ thống log aggregation có thể xử lý đúng cách.

`hostPath` cần được xem như exception bảo mật: nó gắn Pod với một node cụ thể, không portable, không được scheduler hiểu như storage backend, và có thể mở đường đọc/ghi filesystem của node. Chỉ dùng cho node-level agent hoặc lab đã review.

## Dynamic Provisioning

PVC có `storageClassName` sẽ yêu cầu provisioner tạo volume tương ứng:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
spec:
  storageClassName: fast
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

Debug PVC Pending:

```bash
kubectl describe pvc data -n <namespace>
kubectl get storageclass
kubectl get events -n <namespace> --sort-by=.metadata.creationTimestamp
```

Nguyên nhân thường gặp:

- StorageClass không tồn tại hoặc không default.
- CSI provisioner lỗi.
- quota storage hết.
- access mode không được hỗ trợ.
- zone của volume không match node.

Default StorageClass giúp nhiều Helm chart/app cài đặt dễ hơn, nhưng nó cũng là một quyết định platform thật. Nếu default class trỏ tới storage rẻ/chậm hoặc reclaim policy không phù hợp, app có thể âm thầm tạo volume production sai profile. Platform nên document default class dùng cho workload nào, reclaim policy ra sao, có support expansion/snapshot không và zone binding thế nào.

## Access Mode Reality

`ReadWriteOnce` không có nghĩa "chỉ một Pod". Nó thường nghĩa là một node mount read-write. Nếu nhiều Pod trên cùng node cùng mount một PVC RWO, behavior phụ thuộc controller/backend và không phải pattern an toàn cho app stateful.

`ReadWriteOncePod` là intent chặt hơn: một PVC chỉ nên được dùng bởi một Pod trong cluster. Dùng nó khi workload thật sự cần single-writer ở cấp Pod và storage/CSI hỗ trợ đầy đủ.

`ReadWriteMany` yêu cầu backend hỗ trợ shared filesystem. Không nên giả định block storage cloud hỗ trợ RWX.

## Reclaim Policy Và Volume Binding

PV có `persistentVolumeReclaimPolicy`, thường gặp:

| Policy | Ý nghĩa vận hành |
|---|---|
| `Delete` | xóa PVC có thể kéo theo xóa volume backend nếu provisioner hỗ trợ |
| `Retain` | xóa PVC không xóa dữ liệu ngay, cần xử lý PV/backend thủ công |

Điểm nguy hiểm là người học hay nghĩ xóa StatefulSet sẽ xóa hết state. Thực tế Pod có thể bị xóa, StatefulSet có thể bị xóa, nhưng PVC thường vẫn còn. Đây là cơ chế bảo vệ dữ liệu, nhưng cũng tạo rác storage nếu không có quy trình cleanup.

`volumeBindingMode` của StorageClass cũng ảnh hưởng scheduling:

- `Immediate`: volume có thể được provision ngay khi PVC tạo.
- `WaitForFirstConsumer`: chờ Pod đầu tiên dùng PVC rồi mới chọn zone/topology phù hợp.

Với cluster multi-zone, `WaitForFirstConsumer` giúp tránh tạo volume ở zone A rồi Pod lại bị schedule sang node zone B. Khi Pod `Pending` với PVC, phải đọc cả PVC event, Pod event và topology của node/volume.

Khi thiết kế cluster, luôn xét topology giữa compute và data layer. Volume ở zone A nhưng Pod chạy zone B có thể fail mount hoặc tạo latency/egress cost không mong muốn. Dùng node label, PV node affinity, topology-aware StorageClass và Pod scheduling policy để đặt compute gần data.

Với dữ liệu nhạy cảm hoặc cần forensic, đừng để reclaim policy `Delete` là mặc định không được review. `Retain` giúp giữ lại evidence/data sau khi PVC bị xóa nhầm, nhưng cần runbook cleanup rõ để không tạo rác storage lâu dài.

## StatefulSet Identity

StatefulSet tạo Pod theo ordinal:

```text
web-0
web-1
web-2
```

Nếu dùng headless Service, mỗi Pod có DNS ổn định:

```text
web-0.web.default.svc.cluster.local
```

Identity này quan trọng cho:

- database replica membership,
- peer discovery,
- shard identity,
- ordered rollout,
- stable PVC mapping.

Với headless Service, từng Pod có DNS ổn định theo ordinal. Pattern này hữu ích cho primary/replica hoặc peer discovery, ví dụ client ghi có thể trỏ tới primary cố định còn read traffic có thể đi qua Service chọn nhiều replica. Đây chỉ là routing/identity pattern; database vẫn phải tự đảm bảo replication, failover và consistency.

StatefulSet thường tạo/xóa/update Pod theo thứ tự ordinal. Điều này hữu ích cho cluster có membership nhạy cảm, nhưng cũng làm rollout chậm hơn Deployment. Với một số app, bạn cần `podManagementPolicy: Parallel` để scale nhanh hơn, nhưng chỉ dùng khi app chịu được việc nhiều replica khởi động cùng lúc.

## volumeClaimTemplates

StatefulSet có thể tạo PVC riêng cho từng Pod:

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
data-web-0
data-web-1
data-web-2
```

Khi Pod `web-1` bị recreate, nó gắn lại PVC `data-web-1`. Đây là khác biệt lớn với Deployment stateless.

## StatefulSet Does Not Equal Database HA

StatefulSet không tự xử lý:

- database init/bootstrap,
- leader election,
- replication protocol,
- quorum,
- backup/restore,
- data corruption,
- schema migration,
- failover safety.

Nếu chạy database production trong Kubernetes, nên có operator hoặc runbook engine-specific. Ví dụ PostgreSQL, MongoDB, Kafka, Elasticsearch đều có logic cluster riêng ngoài Kubernetes.

StatefulSet cũng không nhất thiết đồng nghĩa với PVC. Có workload cần ordinal identity, stable DNS hoặc ordered rollout nhưng không cần persistent volume. Ngược lại, có workload cần PVC nhưng vẫn không nên chạy như database nếu app không có logic replication/consistency phù hợp.

## StatefulSet Update Và Recovery

Khi update StatefulSet, cần phân biệt:

- update container image/config;
- update volume size;
- update cluster membership;
- migration dữ liệu hoặc schema.

Rolling update của StatefulSet không hiểu semantics của database. Nó chỉ thay Pod theo thứ tự và chờ readiness. Nếu readiness check quá đơn giản, Pod có thể Ready dù replica chưa catch up dữ liệu. Nếu readiness check quá sâu, rollout có thể kẹt do một dependency tạm thời.

Checklist trước khi update stateful workload:

- backup hoặc snapshot đã test restore;
- biết replica nào là leader/primary;
- biết quorum tối thiểu;
- readiness phản ánh trạng thái phục vụ an toàn;
- PDB không cho phép mất quá nhiều replica cùng lúc;
- rollback image có tương thích data/schema không.

Một rollback image không đảm bảo rollback dữ liệu. Nếu version mới đã thay format dữ liệu, rollback container có thể không đọc được state cũ. Đây là khác biệt rất lớn giữa stateless Deployment và stateful workload.

### Node Mất Kết Nối Và Force Delete

Khi node mất kết nối, Pod thuộc StatefulSet có thể kẹt `Terminating` hoặc `Unknown`. Kubernetes thận trọng vì xóa nhầm một Pod stateful trong khi node cũ vẫn có thể quay lại có thể dẫn tới hai instance cùng identity hoặc cùng data path.

Thứ tự xử lý an toàn hơn:

1. Xác minh node thật sự mất, không chỉ API/network chập chờn.
2. Kiểm tra storage backend đã detach hoặc đã fencing node cũ.
3. Kiểm tra quorum/leader/follower của ứng dụng.
4. Ưu tiên recovery qua operator/runbook engine-specific.
5. Chỉ force delete khi chắc chắn không tạo split-brain.

Lệnh force delete là thao tác rủi ro cao:

```bash
kubectl delete pod <stateful-pod> -n <namespace> --grace-period=0 --force
```

Nếu Pod vẫn kẹt do finalizer, có thể cần patch finalizer, nhưng đây là bước cuối cùng sau khi đã giữ evidence và xác nhận an toàn dữ liệu:

```bash
kubectl patch pod <stateful-pod> -n <namespace> -p '{"metadata":{"finalizers":null}}'
```

Với database/queue có leader election hoặc replication, nên dùng `preStop` hook và termination grace period đủ dài để đóng connection, demote leader hoặc xác nhận replication trước khi Pod bị xóa.

## External Storage And Services

`Up and Running` nhấn mạnh một pattern thực tế: không phải state nào cũng nên chạy trong cluster. Managed database hoặc legacy database ngoài cluster có thể được đưa vào Kubernetes service discovery bằng:

- `ExternalName`;
- Service không selector + EndpointSlice;
- Secret/ExternalSecret cho credential;
- NetworkPolicy/egress policy cho outbound.

Pattern này hữu ích khi migration từng bước từ VM/cloud service sang Kubernetes.

## Backup And Restore

Backup không phải copy YAML. YAML chỉ mô tả desired state, còn data nằm ở volume/backend.

Checklist:

- backup dữ liệu theo engine, không chỉ volume snapshot;
- kiểm tra consistency khi snapshot;
- test restore định kỳ;
- ghi rõ PVC nào thuộc Pod ordinal nào;
- biết reclaim policy của PV;
- biết điều gì xảy ra khi xóa StatefulSet, PVC và namespace.

## Troubleshooting Storage Nhanh

| Symptom | Kiểm tra trước |
|---|---|
| PVC `Pending` | `describe pvc`, StorageClass, quota, CSI provisioner |
| Pod `Pending` kèm PVC | volume binding mode, zone/topology, node affinity của PV |
| `FailedMount` | kubelet event, CSI node plugin, Secret/ConfigMap volume |
| StatefulSet Pod không lên lại | PVC còn không, volume attach được không, app recovery log |
| xóa app nhưng storage còn | PVC/PV reclaim policy, owner cleanup runbook |

Lệnh hữu ích:

```bash
kubectl get pvc,pv -n <namespace>
kubectl describe pvc <pvc> -n <namespace>
kubectl get storageclass -o wide
kubectl describe pod <pod> -n <namespace>
kubectl get events -n <namespace> --sort-by=.metadata.creationTimestamp
```

## Volume Mount Pitfalls

Một số lỗi storage/config không nằm ở backend mà nằm ở cách mount vào Pod:

- `subPath` mount một file/directory cụ thể và thường không nhận update động từ ConfigMap/Secret volume như mount cả volume.
- `hostPath` là node-local, không scheduler-aware và có rủi ro bảo mật cao; chỉ dùng cho node agent hoặc lab có chủ đích.
- Secret/ConfigMap volume lỗi thường xuất hiện dưới dạng `FailedMount`; kiểm tra namespace, key name, optional flag và service account/RBAC liên quan.
- File permission có thể phụ thuộc `runAsUser`, `fsGroup`, readonly mount và behavior của CSI driver.

Nếu app cần config reload runtime, cần test rõ mount mode, reload mechanism và rollout fallback thay vì giả định mọi volume update đều được app nhận ngay.

## Related Pages

- [Storage Overview](./overview.md)
- [Workload Controllers Và Rollout](../01-core-objects/02-workload-controllers-and-rollout.md)
- [Networking, Services Và Ingress](../02-networking/overview.md)
- [Kubernetes Troubleshooting Runbooks](../98-troubleshooting/overview.md)
