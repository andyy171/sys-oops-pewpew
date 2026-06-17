# Kubernetes Architecture

## Overview

Kubernetes là một API platform để chạy workload container theo mô hình desired state. Người vận hành khai báo trạng thái mong muốn, còn control plane liên tục quan sát cluster và reconcile để đưa actual state về gần trạng thái đó nhất có thể.

Điểm quan trọng: Kubernetes không phải chỉ là "Docker cluster". Container runtime nằm ở node và thường là `containerd` hoặc CRI-O qua CRI. Kubernetes cung cấp API, scheduling, controller, service discovery, storage integration, policy và automation để tách trách nhiệm giữa application team, platform team và hạ tầng bên dưới.

## Cluster Mental Model

```text
Control plane
  API Server
  etcd
  Scheduler
  Controller Manager
  Cloud Controller Manager

Worker nodes
  kubelet
  container runtime
  kube-proxy or CNI dataplane
  Pods
```

Cluster là tập hợp control plane và worker nodes. Control plane quyết định và lưu desired state; worker node chạy workload thật. Một application có thể tiếp tục phục vụ khi một node lỗi nếu workload có đủ replica, placement hợp lý, network/storage còn hoạt động và dependency bên ngoài không trở thành single point of failure.

Để hiểu sâu hơn cách các mảnh này tương tác nếu tự xây một orchestrator tối thiểu, đọc thêm [Orchestrator Internals From Scratch](./02-orchestrator-internals-from-scratch.md).

## Control Plane

Các thành phần chính:

- API Server là cổng vào của Kubernetes API cho `kubectl`, CI/CD, controller, scheduler và kubelet.
- etcd lưu cluster state; với self-managed cluster cần backup, quorum và restore runbook rõ.
- Scheduler chọn node cho Pod dựa trên requests, affinity, taint/toleration, topology và volume constraint.
- Controller Manager chạy các reconciliation loop như Deployment, ReplicaSet, Job, Node và EndpointSlice controller.
- Cloud Controller Manager tích hợp với cloud provider cho LoadBalancer, node lifecycle hoặc volume tùy môi trường.

Control plane không chạy container thay kubelet. Nó tạo/sửa object qua API; node agent mới biến PodSpec thành container runtime thực tế.

## Worker Node

Worker node chịu trách nhiệm chạy Pod:

- kubelet nhận PodSpec đã được bind vào node, pull image, mount volume, chạy probe và report status.
- container runtime chạy container qua CRI.
- CNI plugin cấp Pod network và có thể enforce NetworkPolicy.
- kube-proxy hoặc dataplane thay thế lập rule cho Service traffic.

Nếu Pod đã được schedule nhưng container không chạy, thường cần nhìn kubelet event/log, image pull, volume mount, probe và runtime state thay vì chỉ nhìn Deployment.

## Cloud Native Principles

Kubernetes hỗ trợ các nguyên tắc cloud native:

- immutable image: build một lần, promote qua môi trường bằng tag bất biến hoặc digest;
- declarative configuration: manifest/Git là source of truth;
- self-healing: controller tạo lại Pod, reconcile object và cập nhật endpoint;
- separation of concerns: app team tập trung app, platform team quản lý policy, cluster, storage, network và guardrail;
- velocity with safety: rollout, rollback, autoscaling, policy và observability giúp thay đổi nhanh hơn nhưng vẫn có kiểm soát.

Tự động hóa của Kubernetes chỉ tốt khi tín hiệu khai báo đúng. Selector sai, probe sai, request sai hoặc policy quá rộng đều làm control plane reconcile rất chăm chỉ về một trạng thái không tốt.

## Runtime And Legacy Notes

Khi đọc tài liệu cũ, cần dịch mental model sang Kubernetes hiện đại:

- "master node" nên hiểu là control plane node.
- Docker Engine không còn là runtime trực tiếp theo dockershim cũ; ưu tiên hiểu CRI, `containerd` và CRI-O.
- `ReplicationController`, `PodSecurityPolicy`, `kubectl rolling-update`, rkt, Service Catalog và federation đời cũ là bối cảnh lịch sử, không nên dùng làm default design mới.

## Related Pages

- [Control Plane, Node Và Reconciliation](./01-control-plane-node-and-reconciliation.md)
- [Orchestrator Internals From Scratch](./02-orchestrator-internals-from-scratch.md)
- [Kubernetes Operations Quick Reference](../01-core-objects/00-kubernetes-operations-quick-reference.md)
- [Kubernetes Networking, Services Và Ingress](../02-networking/overview.md)
- [Kubernetes Security, RBAC Và Pod Hardening](../04-security/overview.md)
