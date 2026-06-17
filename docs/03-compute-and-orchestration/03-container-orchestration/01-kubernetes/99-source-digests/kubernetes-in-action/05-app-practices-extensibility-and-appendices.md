# Kubernetes In Action App Practices, Extensibility And Appendices

## Overview

Note này chuyển hóa phần app/platform-level: lifecycle, graceful shutdown, image/tag/logging/label practice, dev/test workflow, CRD/controller, custom API server, Service Catalog, OpenShift/Helm, kubeconfig multi-cluster, kubeadm, runtime thay thế và Cluster Federation.

## Chapter 17: App Lifecycle

Sách nhấn mạnh app chạy trong Kubernetes phải chấp nhận bị kill, relocate và recreate. Pod không phải server cố định.

Ứng dụng tốt cần:

- startup không phụ thuộc thứ tự cứng giữa service;
- retry/backoff khi dependency chưa sẵn sàng;
- readiness để chưa nhận traffic khi chưa sẵn sàng;
- liveness thận trọng để restart khi thật sự kẹt;
- shutdown graceful để xử lý request đang chạy;
- log ra stdout/stderr;
- không giữ state quan trọng trong local container filesystem.

## Pod Startup And Shutdown

Điểm quan trọng:

- Kubernetes không đảm bảo start Pod theo thứ tự tùy ý cho app stateless;
- init container có thể chuẩn bị trước app chính;
- lifecycle hook như `postStart` và `preStop` có thể giúp tích hợp với quá trình start/stop;
- SIGTERM là tín hiệu app nên bắt để shutdown sạch;
- sau grace period, container có thể bị SIGKILL;
- readiness nên chuyển fail trước khi Pod thật sự dừng nhận traffic.

Graceful shutdown flow:

```text
Pod terminating -> endpoint removed/readiness false -> app receives SIGTERM -> drain in-flight requests -> exit before grace timeout
```

Nếu app không xử lý shutdown, rollout/drain có thể gây lỗi client dù Kubernetes object nhìn vẫn "đúng".

## Handling Client Requests

Sách nói hai cạnh:

- khi Pod start: tránh nhận traffic trước khi warm up;
- khi Pod shutdown: tránh cắt đứt client connection đang xử lý.

Pattern:

- readiness probe phản ánh khả năng nhận request mới;
- preStop hook hoặc app shutdown logic rút Pod khỏi traffic trước;
- timeout/grace period đủ dài cho request thật;
- load balancer/Ingress/Service mesh có delay/connection draining riêng cần hiểu;
- app nên idempotent hoặc có retry-safe behavior.

## Manageable Images, Labels And Logs

Best practices từ sách:

- image nhỏ, predictable, không phụ thuộc mutable tag khó kiểm soát;
- image tag/digest phục vụ rollback;
- `imagePullPolicy` hiểu đúng để tránh pull bất ngờ hoặc không pull bản mới;
- labels nhiều chiều: app, component, version, env, owner;
- annotations cho mô tả/runbook/tooling;
- app nên ghi termination reason hữu ích;
- log ra stdout/stderr để collector lấy.

Diễn giải hiện đại: tag production nên bất biến hoặc dùng digest. Không dựa vào `latest`.

## Development And Testing

Sách nói chạy app ngoài Kubernetes, Minikube, version manifest, auto-deploy và CI/CD. Một số tool như Ksonnet là historical context.

Giá trị cần giữ:

- dev loop cần nhanh nhưng không được làm prod drift;
- manifest nên nằm trong Git;
- CI render/validate/diff trước khi apply;
- environment overlay cần rõ ràng;
- không thao tác production lâu dài bằng `kubectl edit`;
- local cluster hữu ích nhưng không thay thế staging/prod policy.

## Chapter 18: Extending Kubernetes

CRD cho phép định nghĩa resource type mới. Nhưng CRD chỉ là API/schema; giá trị thật đến từ controller/operator reconcile resource đó.

Mental model:

```text
CustomResource spec -> controller watches -> creates/updates dependent resources -> status conditions
```

Một CRD tốt cần:

- spec rõ;
- status rõ;
- validation/defaulting;
- versioning;
- finalizer nếu cần cleanup external resources;
- RBAC tối thiểu cho controller;
- condition/event/log/metric để debug.

## Custom Controllers And Custom API Servers

Sách phân biệt:

- CRD + custom controller: phù hợp đa số extension;
- custom API server: khi cần behavior/API semantics phức tạp hơn CRD cơ bản.

Diễn giải hiện đại:

- ưu tiên CRD/controller khi đủ;
- dùng admission webhook/policy cho validate/mutate request;
- chỉ xây aggregated/custom API server khi có yêu cầu rất rõ về API behavior;
- controller phải idempotent và cập nhật status khi fail.

## Service Catalog And Platform Ecosystem

Sách nói Kubernetes Service Catalog và Open Service Broker API. Đây là phần lịch sử quan trọng: ý tưởng là app trong Kubernetes có thể provision/bind external managed service qua API platform.

Diễn giải hiện đại:

- Service Catalog kiểu trong sách không còn là hướng phổ biến như thời điểm đó;
- ý tưởng vẫn sống trong Crossplane, operators, external-secrets, cloud controllers, platform APIs;
- cần phân biệt "provision infrastructure" và "consume service endpoint/credential";
- binding/deprovisioning phải có lifecycle, owner và cleanup rõ.

## OpenShift, Helm And Platform On Kubernetes

Sách giới thiệu OpenShift, Deis Workflow và Helm như platform/tooling trên Kubernetes.

Giá trị cần giữ:

- Kubernetes là nền API; platform có thể thêm build, route, policy, registry, developer workflow;
- Helm giúp packaging/release Kubernetes resources;
- platform layer phải làm rõ ownership giữa app team và platform team;
- chart/template mạnh nhưng có thể tạo drift/complexity nếu không kiểm soát.

## Appendix A: kubectl With Multiple Clusters

Appendix A nói kubeconfig/context. Kiến thức cần giữ:

- kubeconfig chứa cluster, user/credential và context;
- context = cluster + user + namespace mặc định;
- nhiều cluster cần quản lý context cẩn thận;
- trước khi thao tác production luôn kiểm tra context.

Lệnh nền:

```bash
kubectl config get-contexts
kubectl config current-context
kubectl config view --minify
kubectl config set-context --current --namespace=<namespace>
```

## Appendix B: kubeadm Multi-Node Cluster

Appendix B là hướng setup kubeadm theo thời điểm sách. Giá trị hiện nay:

- hiểu bootstrap cluster gồm control plane, node join, CNI, kubelet;
- không copy command/version cũ vào production;
- cần official docs đúng version;
- cần plan cho certificate, HA control plane, etcd, CNI, upgrade, backup.

Use case của phần này là lab/mental model, không phải runbook production hiện đại.

## Appendix C: Other Container Runtimes

Sách nói runtime khác Docker như rkt. Diễn giải hiện đại:

- Kubernetes dùng CRI để nói chuyện với runtime;
- containerd/CRI-O là runtime phổ biến;
- Dockerfile/image registry knowledge vẫn hữu ích;
- runtime choice ảnh hưởng node operations, logs, image management và security.

## Appendix D: Cluster Federation

Cluster Federation trong sách là hướng cũ để quản lý nhiều cluster. Giá trị conceptual:

- nhiều cluster giúp tách failure domain/region/team;
- routing, config, secret, data replication và observability phức tạp hơn;
- multicluster không tự tạo HA cho stateful data.

Diễn giải hiện đại: xem multicluster như kiến trúc riêng. Có thể dùng GitOps fleet management, service mesh multicluster, global DNS/load balancer, backup/DR tooling tùy bài toán.

## Canonical Links

- [Application Release Và Environment Organization](../../07-cluster-lifecycle/01-application-release-and-environment-organization.md)
- [CRD, Operators, Policy Và Multicluster](../../10-advanced/01-crd-operators-policy-and-multicluster.md)
- [Resources, Probes, Autoscaling Và Disruption](../../05-operations/01-resources-probes-autoscaling-and-disruption.md)
- [Debug Flow Từ Symptom Đến Control Plane Decision](../../98-troubleshooting/01-symptom-to-control-plane-debug-flow.md)
