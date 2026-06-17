# Kubernetes Debug Flow Từ Symptom Đến Control Plane Decision

## Overview

Khi Kubernetes lỗi, triệu chứng thường hiện ở Pod hoặc Service, nhưng nguyên nhân có thể nằm ở nhiều lớp khác nhau: admission reject object, scheduler không tìm được node, kubelet không pull được image, probe làm Pod không Ready, EndpointSlice không có backend, NetworkPolicy chặn traffic, PVC chưa bind, hoặc controller rollout bị kẹt.

Note này gom cách tiếp cận troubleshooting từ hai tài liệu nguồn thành một flow thực dụng: đi từ symptom, đọc status/event, xác định component nào đã đưa ra quyết định, rồi mới sửa manifest hoặc hạ tầng.

## Mental Model

```text
Symptom
  |
  v
kubectl get/describe/logs/events
  |
  v
Xác định lớp lỗi:
  admission -> scheduler -> kubelet/runtime -> controller -> service/network -> storage
  |
  v
Sửa đúng object hoặc đúng dependency
  |
  v
verify bằng status, events, metrics và traffic thật
```

Không nên bắt đầu bằng `kubectl edit` hoặc restart ngẫu nhiên. Kubernetes đã ghi lại khá nhiều quyết định trong `status`, `conditions` và `events`; đọc đúng chỗ sẽ tiết kiệm nhiều thời gian.

## Bước 1: Khóa Đúng Context Và Namespace

Trước khi debug:

```bash
kubectl config get-contexts
kubectl config view --minify
kubectl get ns
kubectl get pods -A
```

Checklist:

- Đang ở đúng cluster chưa?
- Đang nhìn đúng namespace chưa?
- Lỗi xảy ra với một Pod, một Deployment, một namespace, hay toàn cluster?
- Có sự kiện cluster rộng như node NotReady, CNI lỗi, quota đầy, admission webhook timeout không?

Với production, ghi lại context và namespace trong note sự cố. Nhiều lỗi debug sai cluster bắt đầu từ một terminal đang trỏ nhầm kubeconfig.

## Bước 2: Đọc Events Trước Khi Suy Đoán

Lệnh nền:

```bash
kubectl get events -n <namespace> --sort-by=.metadata.creationTimestamp
kubectl describe pod <pod> -n <namespace>
kubectl describe deployment <deployment> -n <namespace>
```

Events thường cho biết component nào đang nói:

| Event / dấu hiệu | Lớp cần điều tra |
|---|---|
| `FailedScheduling` | scheduler, requests, affinity, taints, quota, volume topology |
| `FailedMount` | kubelet, CSI, PVC/PV, Secret/ConfigMap volume |
| `ErrImagePull`, `ImagePullBackOff` | kubelet/runtime, registry, image tag, pull secret |
| `Unhealthy`, probe failed | kubelet probe, app health endpoint, timeout |
| `BackOff restarting failed container` | container process, command, config, memory, liveness |
| rollout `ProgressDeadlineExceeded` | Deployment controller, new ReplicaSet, readiness |
| Service không có endpoints | labels/selectors, readiness, EndpointSlice |

Nếu events trống hoặc quá cũ, kiểm tra namespace đúng chưa và object có bị controller tạo/xóa liên tục không.

## Bước 3: Pod Pending Là Quyết Định Của Scheduler

Khi Pod `Pending`, container thường chưa từng chạy. Đừng đọc log app trước, vì có thể chưa có container để log.

Lệnh:

```bash
kubectl describe pod <pod> -n <namespace>
kubectl get pod <pod> -n <namespace> -o wide
kubectl describe nodes
kubectl get quota,limitrange -n <namespace>
kubectl get pvc -n <namespace>
```

Phân loại:

- `Insufficient cpu/memory`: request quá cao hoặc cluster thiếu capacity.
- `node(s) had untolerated taint`: Pod thiếu toleration.
- `node(s) didn't match Pod's node affinity/selector`: rule placement quá chặt.
- PVC `Pending`: storage chưa provision/bind, scheduler có thể chờ volume.
- quota exceeded: admission/quota chặn tạo thêm Pod hoặc tài nguyên.

Cách sửa:

- chỉnh request dựa trên metric thật, không hạ bừa để ép schedule;
- thêm/tách node pool nếu workload có yêu cầu đặc biệt;
- sửa affinity/toleration theo intent rõ ràng;
- xử lý StorageClass/CSI/PVC trước khi scale workload;
- cập nhật quota hoặc giảm replica sau khi xác nhận ownership.

## Bước 4: ImagePullBackOff Là Lỗi Kubelet/Registry

Lệnh:

```bash
kubectl describe pod <pod> -n <namespace>
kubectl get secret -n <namespace>
kubectl get serviceaccount <sa> -n <namespace> -o yaml
kubectl get pod <pod> -n <namespace> -o jsonpath='{.spec.imagePullSecrets}'
```

Nguyên nhân thường gặp:

- image tag không tồn tại;
- registry cần auth nhưng imagePullSecret thiếu hoặc sai namespace;
- ServiceAccount không tham chiếu pull secret;
- node không resolve được registry;
- proxy/firewall/certificate chain lỗi;
- dùng tag mutable khiến node này pull image khác node kia.

Sửa theo thứ tự:

1. Xác nhận image name/tag/digest.
2. Xác nhận secret nằm cùng namespace với Pod.
3. Xác nhận ServiceAccount hoặc Pod có `imagePullSecrets`.
4. Kiểm tra network/DNS/certificate từ node nếu nhiều Pod cùng lỗi.
5. Rollout lại sau khi sửa secret hoặc image tag.

## Bước 5: CrashLoopBackOff Là Container Đã Chạy Rồi Chết

Lệnh:

```bash
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace> --previous
kubectl logs <pod> -n <namespace>
kubectl get pod <pod> -n <namespace> -o jsonpath='{.status.containerStatuses}'
```

Hỏi theo thứ tự:

- Exit code là gì?
- App chết vì config/Secret thiếu không?
- Command/args có đúng không?
- Liveness probe có kill app quá sớm không?
- Container có `OOMKilled` không?
- Dependency bên ngoài có làm app exit thay vì retry không?

Nếu `--previous` có log app rõ ràng, sửa app/config. Nếu `describe` cho thấy liveness probe failed liên tục, sửa probe trước khi tăng replica. Nếu OOM, xem memory usage thật và limit hiện tại; chỉ tăng limit khi hiểu nguyên nhân tăng memory.

## Bước 6: Pod Running Nhưng Không Ready

Pod `Running` chỉ nói container process đang chạy. Pod `Ready` mới nói nó được đưa vào Service endpoints.

Lệnh:

```bash
kubectl get pod <pod> -n <namespace>
kubectl describe pod <pod> -n <namespace>
kubectl get endpointslice -n <namespace> -l kubernetes.io/service-name=<service>
```

Nguyên nhân:

- readiness probe fail;
- app bind sai port/interface;
- dependency readiness check quá sâu;
- sidecar chưa ready;
- init container hoàn thành nhưng app chính chưa warm up.

Sửa:

- readiness check nên phản ánh khả năng nhận traffic mới;
- liveness không nên dùng để check dependency tạm thời;
- startup probe cho app khởi động lâu;
- Service `targetPort` phải khớp container port thật.

## Bước 7: Service Không Có Traffic

Service lỗi thường không nằm ở Service object một mình. Cần nối đủ chuỗi:

```text
client -> Service -> EndpointSlice -> Pod IP -> containerPort -> app
```

Lệnh:

```bash
kubectl describe svc <service> -n <namespace>
kubectl get pod -n <namespace> --show-labels
kubectl get endpoints <service> -n <namespace>
kubectl get endpointslice -n <namespace> -l kubernetes.io/service-name=<service>
kubectl describe ingress <ingress> -n <namespace>
```

Checklist:

- selector của Service có khớp label Pod không?
- Pod có Ready không?
- `port`, `targetPort`, `containerPort` có đúng không?
- NetworkPolicy có chặn ingress/egress không?
- DNS resolve đúng service FQDN không?
- Ingress/Gateway controller có route tới Service đúng namespace/port không?

Nếu endpoint rỗng, tập trung vào label/readiness trước. Nếu endpoint có nhưng traffic fail, kiểm tra port, NetworkPolicy, CNI, kube-proxy/dataplane và app bind address.

## Bước 8: Rollout Kẹt

Deployment rollout kẹt thường là new ReplicaSet không tạo được Pod Ready.

```bash
kubectl rollout status deployment/<name> -n <namespace>
kubectl describe deployment <name> -n <namespace>
kubectl get rs,pod -l app=<app> -n <namespace>
kubectl describe pod <new-pod> -n <namespace>
```

Nguyên nhân:

- new image pull lỗi;
- new Pod fail readiness;
- request/quota làm Pod Pending;
- `maxUnavailable=0` và `maxSurge` không đủ room;
- progress deadline quá ngắn so với startup thực tế;
- PDB hoặc policy làm rollout/drain khó hoàn tất.

Rollback khi cần:

```bash
kubectl rollout history deployment/<name> -n <namespace>
kubectl rollout undo deployment/<name> -n <namespace>
kubectl rollout status deployment/<name> -n <namespace>
```

Sau rollback, vẫn cần RCA: lỗi do image, config, migration, capacity hay policy.

## Bước 9: PVC Pending Hoặc Mount Failed

Lệnh:

```bash
kubectl get pvc,pv -n <namespace>
kubectl describe pvc <pvc> -n <namespace>
kubectl get storageclass
kubectl describe pod <pod> -n <namespace>
```

Nguyên nhân:

- StorageClass không tồn tại hoặc không default;
- CSI provisioner lỗi;
- access mode không hỗ trợ;
- volume zone không khớp node;
- quota storage hết;
- Secret/ConfigMap volume bị tham chiếu sai tên;
- reclaim policy hoặc PV cũ gây conflict.

Với StatefulSet, đừng xóa PVC vội. PVC thường giữ state của replica; xóa sai có thể mất dữ liệu. Cần backup/restore plan trước khi thao tác phá hủy.

## Bước 10: Verify Sau Khi Sửa

Sau khi sửa, xác nhận đủ các lớp:

```bash
kubectl get pod -n <namespace> -o wide
kubectl get events -n <namespace> --sort-by=.metadata.creationTimestamp
kubectl rollout status deployment/<name> -n <namespace>
kubectl get endpointslice -n <namespace>
kubectl logs <pod> -n <namespace> --tail=100
```

Nếu là production:

- kiểm tra metric lỗi/latency/saturation;
- kiểm tra traffic thật hoặc synthetic check;
- ghi lại thay đổi manifest/Git commit;
- ghi lại nguyên nhân và guardrail để lần sau không lặp lại.

## Related Pages

- [Kubernetes Troubleshooting Runbooks](./overview.md)
- [Image Pull Errors](./image-pull-errors.md)
- [Resources, Probes, Autoscaling Và Disruption](../05-operations/01-resources-probes-autoscaling-and-disruption.md)
- [Service Discovery, Ingress Và Network Policy](../02-networking/01-service-discovery-ingress-and-network-policy.md)
- [Persistent Storage Và StatefulSet](../03-storage/01-persistent-storage-and-statefulsets.md)
