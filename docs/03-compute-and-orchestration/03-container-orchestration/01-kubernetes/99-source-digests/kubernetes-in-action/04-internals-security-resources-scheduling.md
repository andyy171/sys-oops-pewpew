# Kubernetes In Action Internals, Security, Resources And Scheduling

## Overview

Note này đúc kết nhóm kiến thức "beyond basics": control plane internals, controller cooperation, networking implementation, HA, API authentication/authorization, ServiceAccount/RBAC, node/network security, resource management, autoscaling và advanced scheduling.

## Chapter 11: Kubernetes Internals

Sách bóc Kubernetes thành các control loops và component:

- API Server là entry point và API validation/storage gateway.
- etcd lưu state.
- Scheduler bind Pod vào node.
- Controller Manager chạy nhiều controller.
- kubelet biến PodSpec thành container runtime state.
- kube-proxy hoặc dataplane triển khai Service forwarding.
- add-ons như DNS, dashboard, network/storage plugins mở rộng cluster.

Điểm lớn nhất: Kubernetes là hệ phân tán dựa trên API object, watch và reconciliation. Component không cần gọi nhau trực tiếp quá nhiều; chúng quan sát API và cập nhật object/status.

## API Server, Watch And etcd

API Server làm nhiều việc:

- expose REST API;
- authentication/authorization/admission;
- validate object;
- lưu object vào etcd;
- cung cấp watch stream cho controller/scheduler/kubelet.

etcd là source of truth cho cluster state, không phải database application. Nếu tự quản control plane, etcd backup/restore, quorum, latency, compaction và disk health là critical.

## Scheduler And Controller Cooperation

Sách mô tả chuỗi khi tạo Deployment/Pod:

```text
user apply -> API Server stores object
controller creates dependent resources
scheduler binds unscheduled Pod
kubelet runs Pod on node
status/events flow back through API
```

Scheduler chỉ chọn node. Nó không pull image, không mount volume, không restart container. Sau khi bind, kubelet xử lý phần node/runtime.

Controller cooperation là phần rất quan trọng:

- Deployment controller tạo ReplicaSet.
- ReplicaSet controller tạo Pod.
- EndpointSlice/Endpoints controller cập nhật backend cho Service.
- Node controller phát hiện node NotReady.
- Job controller quản lý Pod của Job.

Debug tốt là lần ngược component nào đang chịu trách nhiệm cho symptom.

## What A Running Pod Really Is

Sách nhấn mạnh Pod không phải object trừu tượng trên giấy. Trên node, Pod là:

- một tập namespace/cgroup;
- container runtime sandbox;
- network namespace với IP riêng;
- volume mounts;
- containers chạy process;
- kubelet liên tục report status/probes.

Hiểu lớp này giúp debug `CrashLoopBackOff`, `OOMKilled`, `FailedMount`, `ImagePullBackOff`, và probe failure.

## Networking And Services Internals

Kubernetes networking yêu cầu:

- mọi Pod có thể nói chuyện với mọi Pod khác không NAT phức tạp ở app layer;
- node có thể nói chuyện với Pod;
- Pod thấy IP thật của Pod khác trong model cluster network.

CNI chịu trách nhiệm setup Pod network. kube-proxy hoặc dataplane tương đương triển khai Service. Sách giải thích iptables mode; hiện đại có thể là iptables, IPVS hoặc eBPF tùy CNI/dataplane.

Mental model vẫn bền:

```text
Service/EndpointSlice object -> node dataplane rules -> traffic to Pod backend
```

## High Availability

Sách tách HA app và HA control plane:

- App HA cần nhiều replica, spread node/zone, readiness, PDB, stateless design hoặc stateful replication đúng.
- Control plane HA cần nhiều API Server/controller/scheduler instance và etcd quorum phù hợp.

Managed Kubernetes che bớt control plane, nhưng app HA vẫn là trách nhiệm của bạn.

## Chapter 12: Securing API Server

Security path:

```text
authentication -> authorization -> admission -> validation -> storage
```

Sách nói user/group, ServiceAccount, token và RBAC. Điểm cốt lõi:

- user không phải Kubernetes object thông thường;
- ServiceAccount là identity cho workload trong cluster;
- Role/RoleBinding scope namespace;
- ClusterRole/ClusterRoleBinding có thể có phạm vi cluster-wide;
- default ClusterRoles có sẵn nhưng cần hiểu trước khi bind;
- cấp quyền theo least privilege.

RBAC không chỉ là "ai đọc Secret". Quyền `create pods`, `create rolebindings`, `impersonate`, `list/watch secrets` đều có blast radius cao.

## Chapter 13: Node And Network Security

Sách trình bày các cách Pod có thể chạm sâu vào host:

- `hostNetwork`;
- host ports;
- `hostPID`;
- `hostIPC`;
- `hostPath`;
- privileged container;
- Linux capabilities;
- chạy container bằng user/root khác nhau;
- read-only root filesystem;
- volume permission với `fsGroup`.

PodSecurityPolicy trong sách là legacy. Diễn giải hiện đại:

- dùng Pod Security Admission baseline/restricted;
- hoặc policy engine như Kyverno/Gatekeeper;
- exception phải có owner/lý do;
- không cho app thường chạy privileged/hostPath/host namespace nếu không cần.

NetworkPolicy dùng để cô lập east-west traffic giữa Pods/namespaces/CIDR. Cần CNI hỗ trợ. Default cluster thường allow all nếu không có policy.

## Chapter 14: Computational Resources

Sách giải thích request/limit rất kỹ:

- request dùng cho scheduling và CPU share;
- limit đặt trần runtime;
- CPU vượt limit thường bị throttle;
- memory vượt limit có thể OOMKilled;
- app trong container có thể nhìn thấy CPU/memory khác với limit nếu runtime/cgroup/tooling cũ;
- custom resources có thể được advertise/request qua node capacity.

QoS class:

- `Guaranteed`: request = limit cho CPU/memory trên mọi container;
- `Burstable`: có request/limit nhưng không đủ Guaranteed;
- `BestEffort`: không request/limit.

Khi node memory pressure, QoS và usage ảnh hưởng eviction/kill decision.

## LimitRange, ResourceQuota And Metrics

LimitRange đặt default/min/max request/limit trong namespace. ResourceQuota giới hạn tổng tài nguyên/object.

Sách cũng nói quota cho:

- CPU/memory;
- persistent storage;
- số object như Pod/Service/Secret/PVC;
- quota theo QoS hoặc scope.

Monitoring resource usage cần metrics pipeline. `kubectl top` chỉ là cửa sổ nhanh; production cần lưu lịch sử để sizing request/limit và autoscaling.

## Chapter 15: Autoscaling

HPA loop:

```text
metrics -> HPA computes replicas -> controller updates replica count -> scheduler places new Pods
```

Scale theo CPU utilization phụ thuộc request CPU hợp lý. Nếu request sai, HPA cũng sai. Sách cũng nhắc memory/custom metrics và việc chọn metric đúng.

Điểm quan trọng:

- HPA không làm app stateless;
- HPA không sửa bottleneck database;
- scale down cần thận trọng với in-flight work;
- scale-to-zero không phải lúc nào cũng có sẵn trong HPA cơ bản;
- VPA đề xuất/đổi request theo quan sát usage;
- Cluster Autoscaler thêm/bớt node dựa trên Pod không schedule được hoặc node dư capacity, không chỉ vì actual CPU cao.

## Chapter 16: Advanced Scheduling

Sách đi qua các primitive:

- taints/tolerations: repel Pods khỏi node, Pod opt-in bằng toleration;
- node affinity: attract/require Pod tới node có label;
- pod affinity: co-locate Pod gần Pod khác;
- pod anti-affinity: tránh đặt Pod cạnh nhau;
- topology key: node/rack/zone/region boundary.

Mental model:

| Primitive | Câu hỏi |
|---|---|
| node selector/affinity | Pod muốn node kiểu nào? |
| taint/toleration | node từ chối Pod nào nếu không opt-in? |
| pod affinity | Pod muốn gần Pod nào? |
| pod anti-affinity | Pod nên tránh Pod nào? |
| topology spread | replica nên trải đều theo failure domain nào? |

Rule quá chặt có thể làm Pod `Pending`. Rule quá lỏng có thể gom replica vào cùng failure domain.

## Canonical Links

- [Control Plane, Node Và Reconciliation](../../00-architecture/01-control-plane-node-and-reconciliation.md)
- [RBAC, Pod Security Và Admission](../../04-security/01-rbac-pod-security-and-admission.md)
- [Resources, Probes, Autoscaling Và Disruption](../../05-operations/01-resources-probes-autoscaling-and-disruption.md)
- [Kubernetes Scheduling, Affinity, Taints, Topology Và Priority](../../05-operations/03-scheduling-affinity-taints-topology-and-priority.md)
- [Service Discovery, Ingress Và Network Policy](../../02-networking/01-service-discovery-ingress-and-network-policy.md)
