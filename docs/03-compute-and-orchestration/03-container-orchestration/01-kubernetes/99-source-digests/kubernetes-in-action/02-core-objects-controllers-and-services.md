# Kubernetes In Action Core Objects, Controllers And Services

## Overview

Note này đúc kết lõi Kubernetes object model từ `Kubernetes in Action`: Pod, labels, selectors, namespaces, probes, ReplicationController/ReplicaSet, DaemonSet, Job, CronJob, Service, Endpoints, Ingress, readiness và headless Service. Các API/version trong sách có phần cũ, nhưng mental model vẫn là nền tảng.

## Chapter 3: Pods

Pod là đơn vị deploy nhỏ nhất. Sách nhấn mạnh: Kubernetes không quản lý container đơn lẻ như object top-level; nó quản lý Pod. Pod có thể chứa một hoặc nhiều container cùng:

- network namespace;
- IP và hostname;
- volume;
- lifecycle boundary;
- scheduling decision.

Một Pod nên gom các container cần chạy cùng node, share localhost/volume và scale cùng nhau. Nếu hai process có lifecycle/scale khác nhau, tách thành Pod khác và nói chuyện qua Service.

## Pod Descriptor And kubectl Workflow

Sách đi từ `kubectl get/describe/logs` sang YAML/JSON descriptor. Kiến thức cần giữ:

- manifest là desired state;
- `metadata` chứa name, labels, annotations, namespace;
- `spec` mô tả container, image, ports, volumes, env, probes;
- `status` là phần Kubernetes cập nhật sau khi object được xử lý.

Workflow nền:

```bash
kubectl apply -f pod.yaml
kubectl get pod <pod> -o wide
kubectl describe pod <pod>
kubectl logs <pod> -c <container>
```

Trong production, hiếm khi tạo Pod trực tiếp. Dùng controller như Deployment, StatefulSet, DaemonSet, Job hoặc CronJob để Pod được recreate khi mất.

## Labels, Selectors And Annotations

Labels là cơ chế grouping/query của Kubernetes. Sách dùng labels để:

- group Pod theo app/version/env;
- chọn Pod cho Service;
- chọn Pod thuộc controller;
- filter `kubectl get`;
- ràng buộc scheduling đơn giản;
- tổ chức tài nguyên theo nhiều chiều.

Selectors là query trên labels. Chúng là hợp đồng giữa các object. Nếu selector của Service sai, Service không có backend dù Pod đang chạy tốt.

Annotations không dùng để select. Chúng phù hợp cho metadata phụ như owner, runbook, checksum config, tool/controller hints.

## Namespaces

Namespace chia cluster thành vùng quản trị logic. Sách giới thiệu namespace để:

- tránh đụng tên object;
- group tài nguyên theo team/env;
- scope RBAC/quota/policy;
- thao tác `kubectl -n <namespace>`.

Điểm cần đọc đúng: namespace không phải isolation bảo mật tuyệt đối. Muốn cô lập thật cần RBAC, NetworkPolicy, Pod Security Admission/policy, quota và đôi khi tách cluster.

## Deleting Pods And Resources

Sách có nhiều cách xóa Pod/resources:

- xóa theo tên;
- xóa theo label selector;
- xóa namespace;
- xóa nhiều resource trong namespace.

Ghi nhớ vận hành: nếu Pod thuộc controller, xóa Pod chỉ tạo Pod mới. Muốn dừng workload, phải scale/sửa/xóa controller. Khi xóa namespace production, cần hiểu object nào bị cascade và PVC/PV nào còn giữ dữ liệu.

## Chapter 4: Health And Controllers

Sách bắt đầu bằng liveness probe rồi đi vào controller. Liveness probe trả lời: container có cần restart không? Nếu probe sai, Kubernetes có thể làm app outage bằng cách restart liên tục.

Probe types trong sách:

- HTTP GET;
- TCP socket;
- command/exec.

Thiết kế liveness tốt:

- chỉ restart khi app kẹt thật sự;
- có `initialDelaySeconds`/threshold hợp lý;
- không check dependency ngoài theo kiểu dependency chập chờn là restart toàn bộ app;
- dùng `kubectl logs --previous` khi container đã restart.

## ReplicationController And ReplicaSet

ReplicationController trong sách là cách cũ để giữ số Pod replica. ReplicaSet là phiên bản selector mạnh hơn và hiện thường nằm sau Deployment.

Mental model:

```text
controller desired replicas -> selector -> matching Pods -> create/delete to converge
```

Kiến thức quan trọng:

- controller không sở hữu Pod bằng tên cố định;
- selector quyết định Pod nào nằm trong phạm vi controller;
- đổi label có thể đưa Pod vào/ra khỏi controller;
- đổi Pod template chỉ ảnh hưởng Pod mới, không tự sửa Pod cũ nếu dùng controller cũ;
- scale là đổi desired replica count.

Trong Kubernetes hiện đại, dùng Deployment cho stateless rollout thay vì tạo ReplicaSet trực tiếp.

## DaemonSet, Job And CronJob

DaemonSet chạy một Pod trên mỗi node phù hợp. Use case:

- log agent;
- node exporter;
- CNI/storage plugin;
- security/monitoring daemon.

DaemonSet không dùng để scale web service theo traffic.

Job chạy task có điểm kết thúc. CronJob tạo Job theo lịch. Điểm vận hành:

- đặt `backoffLimit`;
- đặt deadline nếu job có thể treo;
- lưu output ngoài Pod;
- hiểu concurrency policy với CronJob;
- job idempotent giúp retry an toàn.

## Chapter 5: Services

Service giải quyết vấn đề Pod ephemeral và IP thay đổi. Sách đi từ Service nội bộ tới external access.

Core chain:

```text
Service selector -> Endpoints/EndpointSlice -> Pod IP/port -> kube-proxy/dataplane
```

Khi Service không có traffic, kiểm tra theo chain này trước khi sửa Ingress.

## Service Discovery

Sách nói hai cách discover Service:

- environment variables được inject vào Pod lúc start;
- DNS tên Service trong cluster.

DNS là pattern bền hơn vì không yêu cầu restart Pod để thấy Service mới. Tuy vậy client DNS cache vẫn có thể gây stale behavior.

## External Services And Endpoints

Sách có pattern kết nối service ngoài cluster:

- Service không selector + Endpoints/EndpointSlice thủ công;
- `ExternalName` để alias DNS ngoài cluster.

Pattern này hữu ích cho migration từng bước, khi app trong Kubernetes cần gọi database/legacy service bên ngoài. Cần bổ sung NetworkPolicy/egress policy/Secret management trong production.

## NodePort, LoadBalancer And Ingress

Sách trình bày:

- NodePort mở port trên node;
- LoadBalancer yêu cầu cloud load balancer;
- Ingress route HTTP/TLS qua một external endpoint.

Diễn giải hiện đại:

- Ingress chỉ là object cấu hình; cần Ingress Controller;
- Gateway API là hướng mới hơn cho role model rõ hơn;
- annotation nâng cao của Ingress thường phụ thuộc controller;
- Service type và L7 routing là hai lớp khác nhau.

## Readiness And Headless Service

Readiness probe quyết định Pod có được đưa vào Service endpoints không. Pod `Running` chưa chắc nhận traffic.

Readiness tốt trả lời: "Pod này đã sẵn sàng nhận request mới chưa?" Nó khác liveness. Khi readiness fail, Pod thường bị rút khỏi endpoints; khi liveness fail, container bị restart.

Headless Service dùng khi client cần thấy từng Pod riêng, nhất là StatefulSet/peer discovery. DNS có thể trả về nhiều record thay vì một ClusterIP ảo.

## Troubleshooting Services

Flow từ sách, viết lại theo Kubernetes hiện đại:

```bash
kubectl get svc <service> -n <namespace>
kubectl describe svc <service> -n <namespace>
kubectl get endpointslice -n <namespace> -l kubernetes.io/service-name=<service>
kubectl get pod -n <namespace> --show-labels
kubectl describe pod <pod> -n <namespace>
```

Các lỗi hay gặp:

- selector không match labels;
- readiness fail nên endpoints rỗng;
- `targetPort` sai;
- Pod bind sai port/interface;
- NetworkPolicy chặn;
- Ingress route sai Service/port.

## Canonical Links

- [Pods, Labels, Namespaces Và Metadata](../../01-core-objects/01-pods-labels-namespaces-and-metadata.md)
- [Workload Controllers Và Rollout](../../01-core-objects/02-workload-controllers-and-rollout.md)
- [Service Discovery, Ingress Và Network Policy](../../02-networking/01-service-discovery-ingress-and-network-policy.md)
- [Debug Flow Từ Symptom Đến Control Plane Decision](../../98-troubleshooting/01-symptom-to-control-plane-debug-flow.md)
