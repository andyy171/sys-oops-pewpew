# Kubernetes

Kubernetes là nền tảng container orchestration dùng để chạy, scale, tự phục hồi và quản lý workload container theo mô hình desired state. Folder này nên được dùng như cổng ôn tập và tra cứu: bắt đầu từ mental model, đi qua object model, sau đó mới vào networking, storage, security, operations, GitOps, lab và troubleshooting.

## Cách Dùng Folder Này

| Mục tiêu | Bắt đầu từ đâu | Kết quả cần đạt |
|---|---|---|
| Học lại nền tảng | [Architecture](./00-architecture/overview.md) -> [Core Objects](./01-core-objects/overview.md) | Hiểu control plane, node, Pod, controller và reconciliation |
| Thiết kế workload | [Workload Controllers Và Rollout](./01-core-objects/02-workload-controllers-and-rollout.md) -> [Workload Design](./01-core-objects/03-workload-design-and-best-practices.md) | Chọn đúng Deployment/StatefulSet/DaemonSet/Job, rollout an toàn |
| Debug incident | [Troubleshooting Runbooks](./98-troubleshooting/overview.md) -> [Debug Flow](./98-troubleshooting/01-symptom-to-control-plane-debug-flow.md) | Tách được lỗi scheduler, kubelet, image, probe, Service, PVC |
| Làm lab để nhớ lâu | [Labs](./08-labs/overview.md) | Biến lý thuyết thành thao tác quan sát được |

## Learning Path

1. [Kubernetes Architecture](./00-architecture/overview.md): control plane, worker node, API server, scheduler, controller-manager, etcd, kubelet và container runtime.
2. [Control Plane, Node Và Reconciliation](./00-architecture/01-control-plane-node-and-reconciliation.md): Kubernetes lưu desired state rồi liên tục reconcile actual state.
3. [Orchestrator Internals From Scratch](./00-architecture/02-orchestrator-internals-from-scratch.md): task state machine, manager/worker loop, scheduling, metrics, failure recovery và persistent state.
4. [Core Objects](./01-core-objects/overview.md): Pod, label, selector, namespace, metadata, Deployment, ReplicaSet, StatefulSet, DaemonSet, Job và CronJob.
5. [Networking, Services Và Ingress](./02-networking/overview.md): Service, EndpointSlice, DNS, readiness, Ingress, Gateway và NetworkPolicy.
6. [Storage, Volumes Và Stateful Workloads](./03-storage/overview.md): Volume, PVC, PV, StorageClass, CSI và StatefulSet.
7. [Security, RBAC Và Pod Hardening](./04-security/overview.md): ServiceAccount, Role, ClusterRole, admission, Pod Security và Secret handling.
8. [Operations, Resources Và Observability](./05-operations/overview.md): requests, limits, QoS, probes, HPA, PDB, events, logs, metrics và traces.
9. [Packaging Và GitOps](./06-packaging-and-gitops/overview.md): app release workflow với manifest, Helm, Kustomize, source of truth, drift, promotion và rollback.
10. [Cluster Lifecycle](./07-cluster-lifecycle/overview.md): cluster setup, bootstrap, foundation checklist, upgrade path và cluster lifecycle.
11. [Application Integration](./09-application-integration/overview.md): ConfigMap, Secret consumption, Downward API, projected volume, env injection và in-cluster API access.
12. [Advanced Platform Patterns](./10-advanced/overview.md): CRD, Operator, policy, multicluster và platform governance.
13. [Troubleshooting Runbooks](./98-troubleshooting/overview.md): symptom-based flow cho các lỗi phổ biến.

## Structure Assessment

| Section | Vai trò đúng | Mức hữu ích hiện tại | Nhận xét |
|---|---|---:|---|
| `00-architecture` | Mental model cluster, control plane, node, reconciliation | 8/10 | Đủ tốt để học nền tảng; có thể bổ sung thêm etcd backup/API request lifecycle sau. |
| `01-core-objects` | Pod, metadata, controller, rollout, workload design | 8/10 | Đã là điểm học chính cho object model. Một số file legacy được giữ làm pointer để không vỡ link. |
| `02-networking` | Service, DNS, EndpointSlice, Ingress, Gateway, NetworkPolicy | 8/10 | Nội dung thực dụng, có flow traffic và troubleshooting; có thể tách Service Mesh riêng nếu sau này mở rộng. |
| `03-storage` | PVC, PV, StorageClass, CSI, StatefulSet | 8/10 | Đúng canonical home cho storage K8s; nên bổ sung runbook PVC/mount failure nếu có incident thật. |
| `04-security` | RBAC, ServiceAccount, admission, Pod Security | 8/10 | Có chiều sâu tốt; nên tách Secret management/image supply chain nếu nội dung lớn thêm. |
| `05-operations` | Resource, probe, autoscaling, scheduling, observability, runbook | 9/10 | Hữu ích nhất cho day-2 operations; đúng nơi đặt scheduling và observability. |
| `06-packaging-and-gitops` | Manifest source of truth, Helm, Kustomize, GitOps, promotion/rollback | 9/10 | Ranh giới rõ với cluster setup; rất hữu ích để ôn release workflow. |
| `07-cluster-lifecycle` | Cluster setup/bootstrap/lifecycle | 7/10 | Tên này tránh nhầm với Deployment object và app deployment. App release thuộc GitOps. |
| `08-labs` | Thực hành theo từng domain | 8/10 | Tốt cho ôn tập bằng thao tác; lab hiện ở mức guided, chưa phải lab production đầy đủ. |
| `09-application-integration` | ConfigMap, Secret consumption, Downward API, API access | 8/10 | Rõ hơn `integration`; Secret ở đây là cách app consume Secret, còn hardening nằm ở `04-security`. |
| `10-advanced` | CRD, Operator, policy, multicluster, platform pattern | 7/10 | Nên giữ là advanced; tránh biến thành nơi chứa mọi thứ khó phân loại. |
| `98-troubleshooting` | Debug theo symptom | 9/10 | Tách khỏi theory flow; viết kiểu runbook, không viết kiểu bài giảng. |

## Proposed Folder Contract

```text
01-kubernetes/
├── overview.md                         # cổng vào học/ôn/tra cứu
├── 00-architecture/                    # Kubernetes hoạt động như thế nào
├── 01-core-objects/                    # object model và workload design
├── 02-networking/                      # Service/DNS/Ingress/Gateway/NetworkPolicy
├── 03-storage/                         # PVC/PV/StorageClass/CSI/Stateful storage
├── 04-security/                        # RBAC/ServiceAccount/admission/Pod hardening
├── 05-operations/                      # resources/probes/autoscaling/scheduling/observability/runbooks
├── 06-packaging-and-gitops/            # manifest/Helm/Kustomize/GitOps/release
├── 07-cluster-lifecycle/               # cluster setup/bootstrap/lifecycle
├── 08-labs/                            # lab theo domain
├── 09-application-integration/         # app config, Secret consumption, Downward API, API access
├── 10-advanced/                        # CRD/Operator/policy/multicluster
├── 98-troubleshooting/                 # symptom-based runbooks
```

Quy tắc sắp xếp: root chỉ giữ `overview.md`, asset chung và pointer giữ link cũ; kiến thức học chính phải nằm trong folder domain. Nếu một file chỉ trỏ sang canonical home, nó được tính là legacy pointer chứ không phải nội dung cần học.

## Review Checklist

### Object Model

- Pod là runtime unit; Deployment, StatefulSet, DaemonSet, Job và CronJob mới là durable intent.
- Label/selector nối controller với Pod và nối Service với backend. Sai selector thường tạo lỗi "object tồn tại nhưng không có traffic".
- Namespace là boundary tổ chức và quota, không tự động là security boundary.
- StatefulSet cho identity ổn định và PVC ổn định, không tự biến database thành HA.

### Control Plane Vs Data Plane

- `kubectl apply` gửi intent vào API server; etcd lưu desired state; controller/scheduler/kubelet mới biến intent thành runtime.
- `kubectl get` cho biết trạng thái hiện tại, nhưng `describe` và events thường giải thích vì sao trạng thái bị kẹt.
- API server khỏe không có nghĩa Pod traffic khỏe; data plane còn phụ thuộc kubelet, CNI, kube-proxy, DNS, Service endpoint và ứng dụng.

### Workload Và Rollout

- Readiness quyết định Pod có nhận traffic hay không; liveness quyết định restart; startup probe bảo vệ app khởi động chậm.
- Requests ảnh hưởng scheduling; limits ảnh hưởng runtime và OOM behavior.
- Rollback image không luôn rollback được database schema, queue message, external dependency hoặc data migration.
- `kubectl diff`, dry-run và rollout status nên đi trước thay đổi production.

### Networking

- Service không forward traffic nếu EndpointSlice không có backend ready.
- Ingress là object cấu hình; Ingress Controller hoặc Gateway implementation mới xử lý traffic thật.
- DNS resolve thành công không chứng minh route, NetworkPolicy, Service endpoint, TLS hoặc app health đều đúng.
- NetworkPolicy chỉ có hiệu lực khi CNI hỗ trợ và policy được viết đúng chiều ingress/egress.

### Storage

- PVC là claim; PV/backend storage mới là nơi dữ liệu thật tồn tại.
- StorageClass và CSI quyết định provisioning, attach, mount và failure mode.
- Xóa Pod thường không xóa PVC; xóa PVC/PV có thể ảnh hưởng dữ liệu thật tùy reclaim policy.

### Security

- ServiceAccount là workload identity; user identity và workload identity cần được tách rõ.
- RBAC nên cấp theo least privilege; cẩn thận với wildcard verbs/resources và ClusterRoleBinding rộng.
- Secret không nên xuất hiện trong manifest public, log, shell history hoặc troubleshooting bundle.
- Pod Security, SecurityContext, admission policy và image supply chain là các lớp bổ sung, không thay thế RBAC.

## Practice Map

- [Core Workload Lab](./08-labs/01-core-workload-lab.md): Pod, Deployment, rollout và Service cơ bản.
- [Networking, Service, Ingress, DNS Lab](./08-labs/02-networking-service-ingress-dns-lab.md): traffic path từ DNS tới Pod.
- [Storage PVC StatefulSet Lab](./08-labs/03-storage-pvc-statefulset-lab.md): PVC/PV/StatefulSet lifecycle.
- [Security RBAC ServiceAccount Lab](./08-labs/04-security-rbac-serviceaccount-lab.md): quyền và workload identity.
- [Operations HPA, Probes Và PDB Lab](./08-labs/05-operations-hpa-probes-pdb-lab.md): availability, autoscaling và disruption.
- [Packaging Và GitOps Lab](./08-labs/06-packaging-gitops-lab.md): manifest source of truth và promotion.
