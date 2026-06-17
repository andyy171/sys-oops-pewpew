# Kubernetes Advanced Platform Patterns

## Overview

Advanced Kubernetes không phải học thêm thật nhiều object rời rạc. Nó là cách biến cluster thành platform: scheduling có chủ đích, policy có kiểm soát, service mesh khi cần L7 traffic/security, CRD/operator cho domain riêng, multicluster khi một cluster không đủ về failure domain hoặc tổ chức.

`Kubernetes in Action` đặt nền về internals, API security, node/network security, resources, autoscaling, advanced scheduling và extending Kubernetes. `Kubernetes Up and Running` bổ sung service mesh, policy/governance, multicluster deployment và organizing applications.

Đọc sâu: [CRD, Operators, Policy Và Multicluster](./01-crd-operators-policy-and-multicluster.md).

## Advanced Scheduling

Các công cụ chính:

- nodeSelector: chọn node đơn giản theo label.
- node affinity: chọn node linh hoạt hơn.
- pod affinity/anti-affinity: đặt gần hoặc tránh gần Pod khác.
- taints/tolerations: node từ chối Pod trừ khi Pod chịu được taint.
- topology spread constraints: phân tán Pod theo zone/node/rack.
- priority/preemption: workload quan trọng có quyền chen chỗ.

Luôn bắt đầu từ resource requests đúng. Scheduling rule đẹp nhưng requests sai vẫn tạo Pending hoặc overcommit nguy hiểm.

## Policy And Governance

Policy giúp platform team đặt guardrail:

- image registry được phép,
- không privileged container,
- bắt buộc requests/limits,
- bắt buộc label ownership,
- namespace phải có Pod Security label,
- Ingress host phải theo domain được phép.

Công cụ thường gặp:

- built-in admission,
- Pod Security Admission,
- Kyverno,
- OPA Gatekeeper,
- cloud/provider policy.

Policy tốt nên có chế độ audit/warn trước khi enforce để tránh chặn workload hàng loạt.

## Service Mesh

Service mesh phù hợp khi cần:

- mTLS service-to-service,
- identity-based access giữa service,
- traffic splitting/canary,
- retry/timeout/circuit breaker chuẩn hóa,
- L7 telemetry không cần sửa app nhiều.

Không nên dùng service mesh chỉ vì "hiện đại". Nó thêm sidecar/proxy, control plane, version compatibility, latency và debugging complexity.

## Operators And CRDs

Operator biến kinh nghiệm vận hành thành controller:

```text
spec: desired state of domain
status: observed state of domain
controller: reconcile loop
```

Use case tốt:

- database cluster lifecycle,
- certificate automation,
- backup/restore,
- custom platform service,
- cloud resource provisioning.

Anti-pattern:

- CRD chỉ là wrapper mỏng quanh ConfigMap.
- Operator cần quyền quá rộng nhưng không có review.
- Controller không expose status rõ làm incident khó debug.

## Multicluster

Multicluster có thể cần vì:

- regional availability,
- regulatory/data residency,
- latency gần user,
- blast radius isolation,
- platform/team boundary.

Đổi lại, multicluster làm khó:

- service discovery,
- traffic routing,
- data replication,
- secret/config consistency,
- deployment orchestration,
- observability tập trung.

Không coi multicluster là HA miễn phí. App phải có chiến lược data consistency và failover rõ.

## Application Organization

Một app production nên có metadata và cấu trúc rõ:

- labels chuẩn theo app/component/env/team.
- namespace ownership.
- ResourceQuota/LimitRange.
- ServiceAccount riêng.
- manifest/Helm/Kustomize/GitOps ownership.
- dashboard và alert theo app.
- runbook link qua annotation hoặc repo docs.

Kubernetes cho phép rất nhiều tự do; platform tốt là platform đặt đủ quy ước để app team không phải đoán.

## Related Pages

- [CRD, Operators, Policy Và Multicluster](./01-crd-operators-policy-and-multicluster.md)
- [Kubernetes Scheduling, Affinity, Taints, Topology Và Priority](../05-operations/03-scheduling-affinity-taints-topology-and-priority.md)
- [Kubernetes Security, RBAC Và Pod Hardening](../04-security/overview.md)
- [Kubernetes Networking, Services Và Ingress](../02-networking/overview.md)
- [Kubernetes Integration, Configuration Và API Access](../09-application-integration/overview.md)
- [Kubernetes Operations, Resources Và Observability](../05-operations/overview.md)
