# Kubernetes In Action Foundations And First Workload

## Overview

Note này đúc kết nhánh kiến thức nền từ `Kubernetes in Action`: vì sao orchestration ra đời, container/Docker giải quyết vấn đề gì, image đi từ laptop tới registry/node ra sao, và workload đầu tiên được chạy trong Kubernetes theo mô hình desired state. Giá trị chính không nằm ở command cụ thể của năm 2018, mà nằm ở mental model: Kubernetes là hệ thống quản lý desired state cho workload container chạy trên nhiều node.

## Chapter 1: Why Kubernetes Exists

Luồng kiến thức:

- ứng dụng monolith dễ deploy ban đầu nhưng khó scale, khó release độc lập, và dễ tạo coupling giữa team;
- microservices giúp tách release/scale theo domain nhưng làm vận hành phức tạp hơn;
- container cung cấp packaging nhất quán để app và dependency đi cùng nhau;
- orchestration cần thiết khi số container/node tăng, vì con người không thể tự xếp lịch, restart, expose và scale thủ công mãi.

Điểm nên giữ:

- Kubernetes không làm app tự nhiên trở thành microservices tốt. Nó chỉ cung cấp platform để chạy, scale, self-heal và expose workload.
- Container giải quyết khác biệt môi trường bằng cách đóng gói process, filesystem layer và dependency, nhưng kernel vẫn được share với host.
- Kubernetes tạo một abstraction layer trên hạ tầng: app team khai báo cần gì, platform/control plane quyết định chạy ở đâu và duy trì ra sao.

## Monolith To Microservices

Sách trình bày quá trình chuyển từ app lớn sang nhiều service nhỏ. Khi chuyển sang microservices, lợi ích là:

- scale độc lập từng service;
- release độc lập;
- team ownership rõ hơn;
- technology stack linh hoạt hơn.

Đổi lại, vận hành khó hơn:

- nhiều instance cần service discovery;
- nhiều failure mode qua network;
- observability phức tạp hơn;
- config/secret/release cần automation;
- dependency giữa service dễ thành distributed monolith nếu thiết kế kém.

Kubernetes hữu ích ở đây vì nó cung cấp Pod, Service, labels, controller, rollout và health management. Nhưng design boundary của service vẫn là trách nhiệm kiến trúc ứng dụng.

## Containers Mental Model

Container là process được cô lập bằng Linux primitives như namespace, cgroup và filesystem layer. So với VM:

| VM | Container |
|---|---|
| mỗi VM có guest OS riêng | share kernel của host |
| isolation nặng hơn | nhẹ hơn, start nhanh hơn |
| phù hợp isolation mạnh hoặc OS khác nhau | phù hợp đóng gói process/app |

Điểm quan trọng từ sách:

- container không phải máy ảo nhỏ hoàn chỉnh;
- container image là artifact build/publish/pull;
- registry là nơi phân phối image cho node;
- runtime trên node pull image và chạy container;
- security của container phụ thuộc cả host kernel, runtime, image, capability, filesystem và policy.

## Docker, rkt And Historical Context

Sách nói Docker như platform phổ biến cho image/build/run và cũng nhắc `rkt` như runtime thay thế thời điểm đó. Khi chuyển hóa sang note hiện đại:

- Dockerfile/image/registry vẫn là mental model quan trọng;
- Kubernetes hiện đại nói qua CRI tới runtime như `containerd` hoặc CRI-O;
- `rkt` chủ yếu là historical context, không nên học như hướng triển khai chính;
- dockershim cũ không còn là đường runtime chuẩn trong Kubernetes hiện đại.

Giá trị cần giữ: Kubernetes không nên bị hiểu là "Docker cluster". Kubernetes là API/control plane; container runtime chỉ là một lớp node-level thực thi Pod/container.

## Kubernetes Cluster Architecture

Sách giới thiệu cluster gồm control plane và worker node:

- API Server là cổng vào chính.
- Scheduler chọn node cho Pod.
- Controller Manager chạy các reconcile loop.
- etcd giữ cluster state.
- kubelet trên mỗi node nhận PodSpec và chạy container qua runtime.
- kube-proxy/CNI giúp networking và Service data path.

Mental model:

```text
user/CI/controller -> API Server -> etcd
                         |
                         +-> scheduler/controllers
                                      |
                                      v
                                  kubelet/node
```

Điểm cần nhớ: người dùng không SSH vào node để chạy app production. Người dùng tạo object qua API, còn control plane và kubelet biến desired state thành runtime state.

## Chapter 2: Build, Push, Run

Sách dùng một app Node.js nhỏ để minh họa flow:

1. viết app;
2. tạo Dockerfile;
3. build image;
4. chạy image local;
5. push image lên registry;
6. tạo workload trong Kubernetes;
7. expose workload bằng Service;
8. scale replica.

Ý nghĩa vận hành:

- node trong cluster cần pull được image từ registry;
- image local trên laptop không đủ cho cluster nhiều node;
- tag/digest image ảnh hưởng rollback và reproducibility;
- command tutorial cũ có thể tạo `ReplicationController`, nhưng thực tế hiện đại thường dùng `Deployment`.

## First Pod, Service And Controller

Khi chạy workload đầu tiên, sách cho thấy ba object logic:

- Pod là nơi container thật chạy.
- ReplicationController giữ số replica mong muốn.
- Service tạo endpoint ổn định để client gọi vào Pod.

Diễn giải hiện đại:

- thay `ReplicationController` bằng `Deployment`/`ReplicaSet` trong phần lớn workload stateless;
- Service vẫn là abstraction cốt lõi để tránh client phụ thuộc Pod IP;
- Pod là ephemeral, có thể bị xóa/recreate và nhận IP mới;
- controller mới là thành phần duy trì số lượng Pod.

## Scheduling Means Assigning To Node

Sách nhấn mạnh "scheduling" trong Kubernetes không phải đặt lịch thời gian tương lai. Nó là việc gán Pod vào một node cụ thể. Sau khi Pod được bind vào node, kubelet trên node đó pull image và chạy container.

Debug theo flow:

```bash
kubectl get pods -o wide
kubectl describe pod <pod>
kubectl get events --sort-by=.metadata.creationTimestamp
```

Nếu Pod `Pending`, hãy nghĩ scheduler/image pull/capacity trước khi đọc log app.

## Exposing The First App

Sách dùng Service type `LoadBalancer` để expose app ra ngoài. Mental model:

- `ClusterIP`: endpoint nội bộ cluster.
- `NodePort`: mở port trên node.
- `LoadBalancer`: yêu cầu cloud/load balancer bên ngoài.
- Ingress/Gateway: HTTP/TLS routing layer 7, cần controller.

Không nên học thuộc IP/port trong ví dụ. Cần giữ ý: Pod IP không phải API ổn định cho client; Service mới là contract ổn định.

## Horizontal Scaling

Sách scale workload bằng cách đổi desired replica count. Đây là nguyên tắc Kubernetes rất quan trọng:

```text
không ra lệnh "tạo thêm 2 Pod"
mà khai báo "tôi muốn 3 replica"
```

Controller tự reconcile actual state về desired state. Khi có nhiều Pod sau Service, Service phân phối traffic tới các backend hiện tại.

Giới hạn quan trọng: Kubernetes giúp scale dễ, nhưng app phải tự hỗ trợ scale ngang. Stateful session, local disk, lock, background worker, database connection và idempotency vẫn là trách nhiệm app design.

## What To Merge Into Canonical Notes

- Motivation và architecture: [Control Plane, Node Và Reconciliation](../../00-architecture/01-control-plane-node-and-reconciliation.md)
- Pod/labels/controller: [Pods, Labels, Namespaces Và Metadata](../../01-core-objects/01-pods-labels-namespaces-and-metadata.md)
- Service/load balancing: [Service Discovery, Ingress Và Network Policy](../../02-networking/01-service-discovery-ingress-and-network-policy.md)
- Release/source of truth: [Application Release Và Environment Organization](../../07-cluster-lifecycle/01-application-release-and-environment-organization.md)
