# Kubernetes In Action Storage, Config, API, Deployments And StatefulSets

## Overview

Note này chuyển hóa phần kiến thức từ stateless Pod/Service sang các vấn đề production hơn: volume, persistent storage, ConfigMap, Secret, Downward API, in-cluster API access, Deployment rollout và StatefulSet. Đây là mảng giúp hiểu vì sao Kubernetes không chỉ là "chạy container", mà là một API platform có nhiều contract vận hành.

## Chapter 6: Volumes

Sách bắt đầu bằng vấn đề: filesystem trong container thường ephemeral. Khi container restart, dữ liệu trong writable layer không phải nơi lưu state đáng tin. Volume là cách gắn storage vào container và chia sẻ dữ liệu giữa containers trong cùng Pod.

Nhóm kiến thức:

- `emptyDir`: volume sống theo Pod, dùng cho cache/scratch/shared files giữa containers.
- source từ Git repo: historical pattern; hiện thường thay bằng init container hoặc image/build pipeline.
- `hostPath`: mount filesystem của node, rất nhạy cảm về security và portability.
- persistent volume backend: cloud disk/NFS/iSCSI/Ceph/... tùy môi trường.

Mental model:

```text
container filesystem ephemeral
Pod volume lifecycle tùy volume type
persistent data cần PV/PVC/backend và backup riêng
```

## Sharing Data Between Containers

Một use case quan trọng của volume là Pod nhiều container:

- main app container đọc file;
- sidecar/init container tạo hoặc sync file;
- cả hai share cùng `emptyDir` hoặc volume khác.

Pattern này tốt khi hai container thật sự share lifecycle. Nếu sidecar cần scale độc lập hoặc fail độc lập, tách thành Service riêng.

## hostPath Warning

`hostPath` cho Pod truy cập filesystem node. Sách dùng để minh họa system Pod và host-level access. Trong production:

- tránh dùng cho app thường;
- chỉ dùng cho node agent/infrastructure component đã review;
- kết hợp Pod Security Admission/policy;
- hiểu rõ node portability: Pod bị schedule sang node khác có thể không có path/data tương tự.

## PV, PVC And StorageClass

Sách tách Pod khỏi backend storage bằng PV/PVC:

```text
Pod -> PVC -> PV -> StorageClass/CSI -> backend storage
```

Giá trị chính:

- app developer request storage qua PVC;
- platform/storage admin cung cấp class/backend;
- Pod không cần biết backend cụ thể;
- dynamic provisioning tạo PV theo PVC khi có StorageClass.

Những điểm cần giữ:

- PVC là namespace-scoped claim;
- PV là resource cluster-scoped;
- reclaim policy quyết định điều gì xảy ra sau khi PVC bị xóa;
- access mode không đảm bảo semantics ứng dụng nếu backend không hỗ trợ;
- backup dữ liệu không phải chỉ backup YAML.

## Chapter 7: ConfigMaps And Secrets

Sách dạy tách config khỏi image. Image nên reusable giữa env; khác biệt dev/staging/prod nằm ở runtime configuration.

Các cách truyền config:

- command/args;
- environment variables;
- ConfigMap key/value;
- ConfigMap mounted as files;
- Secret cho dữ liệu nhạy cảm.

Điểm thực tế:

- env var không đổi trong process đang chạy;
- ConfigMap volume có thể update file nhưng app phải reload;
- config quan trọng thường cần trigger rollout;
- không hardcode config vào image nếu muốn promotion/rollback sạch.

## Secrets

Secret giống ConfigMap về cách consume nhưng dành cho dữ liệu nhạy cảm. Sách nói default token Secret và image pull Secret. Diễn giải hiện đại cần thận trọng:

- Secret không phải encrypted magic nếu chỉ nhìn manifest base64;
- quyền `get/list/watch secrets` rất nhạy cảm;
- app không cần gọi API thì tắt automount token;
- imagePullSecret phải nằm đúng namespace hoặc gắn vào ServiceAccount;
- secret rotation cần rollout/reload plan.

Secret nên được quản lý bằng vault/KMS/External Secrets nếu production có yêu cầu audit/rotation mạnh.

## Chapter 8: Downward API And Kubernetes API

Downward API cho container biết metadata của chính Pod mà không cần gọi API Server:

- Pod name;
- namespace;
- labels/annotations;
- resource requests/limits;
- Pod IP/host info tùy field.

Nên dùng Downward API khi app chỉ cần biết "tôi là ai" trong cluster. Không nên cho app quyền API rộng chỉ để đọc tên Pod/namespace.

## In-Cluster API Access

Sách giải thích cách Pod nói chuyện với API Server bằng ServiceAccount token, CA certificate và API endpoint nội bộ. Giá trị vận hành:

- ServiceAccount là identity của workload;
- RBAC quyết định app được đọc/ghi resource nào;
- controller/operator cần watch/list có backoff/cache;
- app thường không nên gọi API Server nếu không có lý do rõ;
- ambassador sidecar là pattern cũ/hữu ích trong một số trường hợp để proxy auth/TLS.

Khi app gọi API bị `403`, debug bằng:

```bash
kubectl auth can-i <verb> <resource> \
  --as system:serviceaccount:<namespace>:<serviceaccount> \
  -n <namespace>
```

## Chapter 9: Deployments

Sách đi từ update thủ công Pod sang rolling update bằng controller cũ, rồi kết luận Deployment là cách declarative hơn.

Giá trị chính:

- đừng update Pod trực tiếp;
- Deployment quản lý ReplicaSet;
- update Pod template tạo ReplicaSet mới;
- rollout dần scale up new ReplicaSet và scale down old ReplicaSet;
- rollback dựa trên rollout history/revision;
- `maxSurge` và `maxUnavailable` kiểm soát tốc độ và capacity;
- pause/resume giúp gom nhiều thay đổi trước khi rollout;
- readiness probe là điều kiện quan trọng để rollout không gửi traffic tới Pod chưa sẵn sàng.

`kubectl rolling-update` trong sách là historical context. Note hiện đại dùng Deployment/GitOps/progressive delivery.

## Bad Rollout Blocking

Sách mô tả Deployment có thể bị kẹt nếu version mới không Ready. Đây là behavior tốt: Kubernetes không nên xóa hết version cũ khi version mới chưa sẵn sàng.

Debug rollout:

```bash
kubectl rollout status deployment/<name> -n <namespace>
kubectl describe deployment <name> -n <namespace>
kubectl get rs,pod -l app=<app> -n <namespace>
kubectl describe pod <new-pod> -n <namespace>
```

Nguyên nhân hay gặp: image pull fail, readiness fail, quota/capacity thiếu, request quá cao, config/Secret thiếu.

## Chapter 10: StatefulSets

StatefulSet giải quyết nhóm workload cần identity ổn định:

- Pod ordinal: `app-0`, `app-1`, `app-2`;
- stable network identity qua headless Service;
- stable storage mapping qua `volumeClaimTemplates`;
- ordered create/update/delete;
- mỗi replica có PVC riêng.

Khác Deployment: Pod của StatefulSet không hoàn toàn replaceable nếu gắn dữ liệu/identity. Khi Pod recreate, nó nên lấy lại identity/PVC cũ.

## Peer Discovery And Failure

Sách dùng DNS để peer trong StatefulSet discover nhau. Mental model:

```text
headless service -> DNS record per Pod -> app cluster membership
```

Điểm vận hành:

- readiness ảnh hưởng DNS/endpoint discovery tùy cấu hình;
- app vẫn phải tự xử lý replication/quorum/leader election;
- StatefulSet không tự biến database thành HA;
- khi node mất kết nối, xóa Pod stateful cần rất thận trọng vì có nguy cơ split-brain hoặc double attachment nếu storage/cluster chưa đảm bảo.

## Canonical Links

- [Persistent Storage Và StatefulSet](../../03-storage/01-persistent-storage-and-statefulsets.md)
- [ConfigMap, Secret, Downward API Và API Access](../../09-application-integration/01-configmap-secret-downward-api-and-api-access.md)
- [Workload Controllers Và Rollout](../../01-core-objects/02-workload-controllers-and-rollout.md)
- [Application Release Và Environment Organization](../../07-cluster-lifecycle/01-application-release-and-environment-organization.md)
