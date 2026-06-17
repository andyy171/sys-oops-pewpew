# Kubernetes Cluster Lifecycle Và Setup

## Overview

Kubernetes cluster lifecycle có hai lớp cần tách rõ:

- Triển khai cluster: tạo control plane, node, network, storage, auth, upgrade path.
- Triển khai application: dùng manifest/GitOps/Helm/Kustomize để đưa workload vào cluster.

`Kubernetes in Action` có phần setup Minikube/cloud cluster theo bối cảnh học tập. `Kubernetes Up and Running` đi theo hướng thực dụng hơn: local cluster để học, managed cluster cho cloud, và tự dựng cluster chỉ khi hiểu rõ trách nhiệm vận hành.

Đọc sâu về application release/source of truth ở [Packaging Và GitOps](../06-packaging-and-gitops/overview.md). Folder này chỉ giữ cluster setup, bootstrap, foundation checklist, upgrade path và các quyết định managed/self-managed.

## Cluster Setup Options

| Mô hình | Khi dùng | Trách nhiệm chính |
|---|---|---|
| Local cluster | học/lab/dev | cài nhanh, không đại diện production đầy đủ |
| Managed Kubernetes | production phổ biến | cloud lo control plane, team vẫn lo workload/platform policy |
| kubeadm/bare metal | private cloud, lab sâu, edge | tự quản control plane, etcd, upgrade, backup |
| Kubernetes in Docker | test CI/local | nhanh, ephemeral |

Không chọn mô hình chỉ vì dễ cài. Chọn theo năng lực vận hành, yêu cầu network/storage/security, upgrade và backup.

## kubeadm Bootstrap Mental Model

`kubeadm` là công cụ bootstrap cluster, không phải toàn bộ platform lifecycle manager. Nó chuẩn hóa các bước khó của self-managed Kubernetes như tạo static Pod manifest cho control plane, sinh hoặc dùng PKI, tạo kubeconfig ban đầu, cấu hình kubelet/kube-proxy, bootstrap worker node và hỗ trợ upgrade path.

Luồng tối giản:

```text
prepare host runtime/kubelet
-> kubeadm init control plane
-> install CNI
-> join worker nodes with bootstrap token
-> install platform add-ons
-> validate backup, auth, observability, upgrade path
```

Trước khi dùng kubeadm cho production, cần hiểu ranh giới trách nhiệm:

- `kubeadm` không tự chọn CNI/storage/ingress/monitoring/logging/service mesh cho bạn.
- kubelet và container runtime là service trên host, thường do systemd và package manager quản lý.
- Control plane component thường chạy bằng static Pod manifest do kubelet quản lý trên control-plane node.
- `admin.conf` là credential bootstrap quyền rất cao; không dùng làm kubeconfig hằng ngày cho user hoặc CI/CD.
- Runtime nên tuân theo CRI và được kiểm tra tương thích với version Kubernetes mục tiêu. Tài liệu cũ có thể nhắc Docker/rkt; production hiện đại thường cần dịch mental model sang `containerd` hoặc CRI-O.

### Control Plane, PKI Và etcd

Cluster tự quản phải xem PKI, etcd và API endpoint là foundation, không phải chi tiết cài đặt phụ.

- PKI trong `/etc/kubernetes/pki` bảo vệ API Server, kubelet client, front-proxy và ServiceAccount signing; private key cần backup/rotation theo runbook.
- Nếu tổ chức có CA nội bộ/compliance, có thể chuẩn bị certificate trước rồi để kubeadm dùng thay vì tự sinh toàn bộ.
- Với HA, API Server nên đứng sau load balancer endpoint ổn định để worker và client không phụ thuộc một node.
- etcd chứa cluster state và Secret đã persist; Kubernetes component có thể thay, nhưng mất/restore sai etcd là rủi ro nền tảng.
- Production self-managed nên có etcd HA, snapshot định kỳ, restore drill và monitoring quorum/latency.

Secret trong etcd cần encryption at rest nếu cluster tự quản và dữ liệu nhạy cảm. Đừng bê nguyên flag từ tài liệu cũ; hãy kiểm tra đúng API/flag của version cluster. Mental model cần giữ là:

```text
Kubernetes Secret object
-> API Server encryption provider
-> encrypted payload persisted in etcd
-> key management / rotation / backup policy
```

Nếu key encryption nằm cùng disk/quyền truy cập với etcd data, encryption chỉ giảm một phần rủi ro. Thiết kế production nên tách quyền truy cập key, backup và node/control-plane filesystem càng rõ càng tốt.

### Worker Join Và Bootstrap Token

Worker node join cluster qua API endpoint bằng bootstrap token và CA pinning/hash để xác minh đúng control plane. Token join nên được xem như credential tạm thời:

```bash
kubeadm token create --ttl <duration>
kubeadm join <api-endpoint> \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

Sau khi node join, kubelet dùng TLS bootstrap/CSR để có credential runtime. Trong production, cần kiểm soát ai được approve CSR, token sống bao lâu, node image có trusted không và node sau khi join đã có label/taint/monitoring baseline chưa.

### Add-ons Và Upgrade Path

Sau `kubeadm init`, cluster chưa production-ready nếu thiếu CNI, DNS ổn định, observability, storage, ingress/gateway, policy và backup. `kubeadm` có thể quản lý một số thành phần nền như DNS/kube-proxy tùy version/config, nhưng các add-on platform vẫn cần owner và lifecycle riêng.

### Ansible Bootstrap Boundary

Ansible co the chuan bi host, cai runtime/kubelet/kubeadm, render config va goi `kubeadm init/join`. Tuy nhien Ansible khong thay the lifecycle manager day du cho production cluster: van can owner cho API endpoint, etcd backup, PKI, CNI, CSI, ingress, observability, upgrade va DR.

Neu dung Ansible cho kubeadm bootstrap, runbook nen co pre-check host, pin version, disable/configure swap, CIDR khong conflict, validate node `Ready`, validate system Pod, va khong phat tan `admin.conf` lam kubeconfig cho user/CI.

Upgrade self-managed cluster nên theo thứ tự an toàn:

```text
backup/restore check
-> kubeadm upgrade plan
-> upgrade control plane first
-> upgrade kubelet/kubectl/container runtime with package manager
-> drain/cordon workers as needed
-> validate API, nodes, DNS, CNI, workloads, metrics/logs
```

Với HA control plane, tháo từng API Server khỏi load balancer khi bảo trì, upgrade có kiểm soát, rồi đưa lại sau khi health check ổn. Với worker node, ưu tiên rolling drain để workload có replica/PDB được reschedule trước khi kernel/runtime/kubelet thay đổi.

## Disaster Recovery Và Backup

Kubernetes tự reconcile workload, nhưng không tự thay thế một chiến lược DR. Cần tách rõ:

- **control plane state**: etcd, PKI, kubeconfig/admin credential, encryption provider key;
- **worker node**: nên có thể rebuild/join lại bằng automation;
- **application state**: PV/PVC, database, object storage, external dependency;
- **manifest/source of truth**: GitOps/IaC để dựng lại desired state.

Control plane HA làm giảm xác suất downtime, nhưng không thay thế backup. API Server/controller/scheduler lỗi thường không làm Pod đang chạy chết ngay; data plane có thể vẫn phục vụ traffic cũ, nhưng cluster mất khả năng thay đổi, reschedule hoặc tự phục hồi đầy đủ cho đến khi control plane trở lại.

### etcd Và Cluster State

Với cluster tự quản, etcd là source of truth của Kubernetes object. Backup bằng snapshot native của etcd thường an toàn và rõ ràng hơn việc copy filesystem thô:

```bash
ETCDCTL_API=3 etcdctl snapshot save <snapshot-file>
ETCDCTL_API=3 etcdctl snapshot restore <snapshot-file> --name <member-name>
```

Runbook production cần ghi rõ endpoint, certificate, member name, data dir, quorum expectation và thứ tự restore từng member. Snapshot phải được offload ra nơi ngoài cluster/failure domain, encrypt nếu chứa Secret, và test restore định kỳ. Nếu dùng aggregated API server, CNI/policy backend hoặc component khác có etcd riêng, backup primary Kubernetes etcd chưa đủ.

### Application Data Và Local State

PV/PVC backup phụ thuộc backend: CSI snapshot, storage array snapshot, database-native backup, object storage replication hoặc tool cấp Kubernetes. Đừng coi snapshot là backup đầy đủ nếu chưa restore thử vào namespace/cluster khác.

Local node data là rủi ro hay bị bỏ quên. `emptyDir` mất theo Pod/node lifecycle; `hostPath` phụ thuộc node cụ thể và dễ làm worker không còn replaceable. Workload production có dữ liệu quan trọng không nên giả định local disk sẽ sống qua drain, rebuild hoặc node retirement nếu chưa có backup/replication riêng.

### Velero/Ark Mental Model

Ark trong tài liệu cũ hiện được biết đến rộng rãi hơn dưới tên Velero. Giá trị của lớp tool này là backup qua Kubernetes API thay vì restore mù toàn bộ etcd:

- backup theo namespace/label/resource;
- restore sang namespace hoặc cluster khác;
- ưu tiên restore một phần workload quan trọng trước;
- tích hợp snapshot persistent volume khi backend hỗ trợ;
- lưu backup off-cluster, ví dụ S3-compatible object storage.

DR chỉ đáng tin khi được diễn tập. Một checklist tối thiểu:

- biết RTO/RPO cho cluster và từng app quan trọng;
- restore được etcd hoặc resource backup vào môi trường test;
- restore được PV/database bằng dữ liệu thật đã được sanitize nếu cần;
- credential/PKI/encryption key có backup an toàn;
- runbook có owner, tần suất backup, retention, alert khi backup fail;
- sau restore có validation app, DNS, ingress, auth, metrics/logs.

## Cluster Foundation Checklist

- API Server endpoint ổn định.
- etcd backup/restore strategy nếu tự quản lý.
- CNI được chọn và test NetworkPolicy nếu cần.
- CSI/storage class phù hợp workload.
- Ingress/Gateway layer rõ owner.
- DNS/CoreDNS health.
- Metrics/logging/alerting có sẵn.
- RBAC baseline và namespace model.
- Pod Security Admission/policy baseline.
- Upgrade path và node lifecycle runbook.

## Application Deployment Flow

Luồng application deployment chi tiết nằm ở [Environment Promotion, Release Và Rollback](../06-packaging-and-gitops/05-environment-promotion-release-and-rollback.md). Ở đây chỉ giữ ranh giới với cluster setup:

```text
source code -> image build -> scan/sign -> registry -> manifest render -> diff/review -> apply/sync -> verify -> observe
```

Với môi trường quan trọng:

- Không deploy image tag mutable như `latest`.
- Không chứa secret thật trong manifest Git.
- Dùng `kubectl diff`, PR review hoặc GitOps sync preview nếu có.
- Rollout phải gắn với metric/alert.
- Rollback phải dùng version đã biết tốt.

## Imperative Vs Declarative

Imperative hữu ích khi học/lab:

```bash
kubectl create deployment web --image=nginx:1.25
kubectl expose deployment web --port=80
```

Declarative phù hợp production:

```bash
kubectl apply -f manifests/
kubectl diff -f manifests/
```

Mental model: Kubernetes là declarative API platform. File YAML không phải "config phụ"; nó là hợp đồng desired state của hệ thống.

## Environment Promotion

Tách môi trường bằng:

- namespace,
- cluster riêng,
- folder/overlay riêng,
- values riêng,
- policy riêng.

Ví dụ maturity:

```text
dev namespace -> staging cluster -> prod cluster
```

Không để dev có quyền ghi production. Không reuse kubeconfig admin cho CI/CD.

## Development Cluster Workflow

Development cluster cần tối ưu cho vòng lặp của developer nhưng vẫn có guardrail:

- Shared cluster thường tiết kiệm hơn cluster-per-user, nhưng cần namespace, RBAC, quota và cleanup automation rõ.
- Cluster-per-user đơn giản về isolation nhưng tốn chi phí và khó quản lý fleet nếu không có automation tạo/xóa cluster.
- Namespace dev nên có owner/team/purpose/TTL annotation để tính cost và garbage collect.
- Onboarding nên ưu tiên external identity provider và token ngắn hạn; certificate/kubeconfig dài hạn chỉ nên là fallback có quy trình revoke.
- Cluster-level logging/metrics giúp developer debug mà không cần quyền rộng vào node hoặc namespace khác.
- Test flakiness trong dev cluster là tín hiệu vận hành thật: noisy neighbor, thiếu quota hoặc dependency shared không ổn định sẽ làm developer mất niềm tin vào CI.

## Related Pages

- [3 Node Basic Setup](./3-node-basic-setup.md)
- [Ansible Kubernetes Automation](../../../../05-infrastructure-automation/07-configuration-management/01-ansible/10-kubernetes-automation.md)
- [Packaging Và GitOps](../06-packaging-and-gitops/overview.md)
- [Kubernetes Architecture](../00-architecture/overview.md)
- [Kubernetes Control Plane, Node Và Reconciliation](../00-architecture/01-control-plane-node-and-reconciliation.md)
- [Kubernetes Operations, Resources Và Observability](../05-operations/overview.md)
- [Kubernetes Security, RBAC Và Pod Hardening](../04-security/overview.md)
