# Kubernetes Operations, Resources Và Observability

## Overview

Vận hành Kubernetes không chỉ là `kubectl apply`. Một workload chạy tốt cần resource request/limit đúng, probe hợp lý, rollout có quan sát, autoscaling có metric, log/metric/event đủ để debug và runbook rõ khi sự cố xảy ra.

`Kubernetes in Action` cung cấp nền về resource request/limit, QoS, LimitRange, ResourceQuota, HPA, Cluster Autoscaler và advanced scheduling. `Kubernetes Up and Running` bổ sung góc nhìn kubectl workflow, production app organization và vận hành theo nhóm.

## Day-2 Operations Map

| Mảng | Cần có |
|---|---|
| Health | readiness/liveness/startup probe |
| Capacity | requests, limits, quota, node allocatable |
| Rollout | rollout status, rollback, release metrics |
| Scaling | HPA/VPA/Cluster Autoscaler hoặc KEDA nếu dùng event-driven |
| Observability | metrics, logs, traces, events |
| Debug | describe, logs, exec, ephemeral container nếu policy cho phép |
| Governance | namespace, RBAC, policy, cost ownership |

## Deep Dive Notes

- [Kubernetes Operations Runbooks](./runbooks/overview.md)

- [Resources, Probes, Autoscaling Và Disruption](./01-resources-probes-autoscaling-and-disruption.md)
- [Observability Logs, Metrics, Events Và Traces](./02-observability-logs-metrics-events-and-traces.md)
- [Scheduling, Affinity, Taints, Topology Và Priority](./03-scheduling-affinity-taints-topology-and-priority.md)
- [Machine Learning, GPU Và Batch Workloads](./04-machine-learning-gpu-and-batch-workloads.md)

## Requests, Limits Và QoS

Requests dùng cho scheduling. Limits dùng để đặt trần runtime.

```yaml
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 1
    memory: 512Mi
```

QoS:

- `Guaranteed`: mọi container có request = limit cho CPU và memory.
- `Burstable`: có request/limit nhưng không đủ điều kiện Guaranteed.
- `BestEffort`: không có request/limit.

Khi node thiếu tài nguyên, QoS ảnh hưởng thứ tự eviction. Memory limit vượt quá có thể dẫn đến `OOMKilled`; CPU limit thường gây throttling.

## LimitRange Và ResourceQuota

LimitRange đặt default/min/max cho container trong namespace. ResourceQuota giới hạn tổng tài nguyên namespace.

```bash
kubectl get limitrange -n <namespace>
kubectl describe limitrange -n <namespace>
kubectl get resourcequota -n <namespace>
kubectl describe resourcequota -n <namespace>
```

Nếu Pod Pending hoặc bị reject khi apply, kiểm tra event và quota trước khi tăng replica bừa.

## Probes

Probe tốt giúp Kubernetes đưa traffic và restart đúng lúc. Probe xấu có thể tạo outage.

Checklist:

- `readinessProbe`: kiểm tra app đã phục vụ traffic thật chưa.
- `livenessProbe`: chỉ dùng để restart khi app không thể tự hồi phục.
- `startupProbe`: dùng cho app khởi động lâu.
- Timeout và failure threshold phải phản ánh latency thật.
- Probe không nên phụ thuộc toàn bộ dependency nếu dependency outage sẽ làm tất cả Pod bị rút khỏi Service cùng lúc.

## Autoscaling

HPA scale replica theo metric:

```bash
kubectl get hpa
kubectl describe hpa <name>
kubectl top pods
kubectl top nodes
```

Điều kiện cần:

- metrics-server hoặc metric adapter phù hợp.
- requests CPU/memory hợp lý nếu scale theo resource utilization.
- workload có thể scale ngang.
- dependency phía sau chịu được replica tăng.

Cluster Autoscaler thêm node khi Pod không schedule được do thiếu capacity, không phải khi CPU actual đang cao. HPA và Cluster Autoscaler thường phối hợp: HPA tăng Pod, scheduler thấy thiếu chỗ, Cluster Autoscaler thêm node.

## Observability

Ba nguồn tín hiệu Kubernetes hay dùng:

- Metrics: xu hướng, alert, SLO.
- Logs: chi tiết hành vi app/container.
- Events: quyết định của control plane và kubelet.

Lệnh nền:

```bash
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl describe pod <pod>
kubectl logs <pod> -c <container>
kubectl top pod
kubectl top node
```

Chỉ nhìn log app thường chưa đủ. Với lỗi scheduling, image pull, volume mount, probe, OOM, hãy đọc `describe` và events.

## Rollout Operations

```bash
kubectl rollout status deployment/<name>
kubectl rollout history deployment/<name>
kubectl rollout undo deployment/<name>
kubectl pause deployment/<name>
kubectl resume deployment/<name>
```

Runbook rollout nên có:

- target version/image,
- pre-check capacity/quota,
- rollout command hoặc GitOps PR,
- metric cần theo dõi,
- rollback command,
- tiêu chí dừng rollout.

## Debug Safety

Trước khi thao tác:

```bash
kubectl config get-contexts
kubectl config view --minify
kubectl get ns
```

Debug theo thứ tự ít xâm lấn:

1. `kubectl get`.
2. `kubectl describe`.
3. `kubectl logs`.
4. `kubectl exec` nếu cần.
5. debug/ephemeral container nếu cluster cho phép.
6. thay đổi manifest qua review/dry-run/diff.

Tránh sửa tay object production bằng `kubectl edit` nếu GitOps/CI đang là source of truth.

## Related Pages

- [Kubernetes Operations Quick Reference](../01-core-objects/00-kubernetes-operations-quick-reference.md)
- [Kubernetes Scheduling, Affinity, Taints, Topology Và Priority](./03-scheduling-affinity-taints-topology-and-priority.md)
- [Kubernetes Observability Logs, Metrics, Events Và Traces](./02-observability-logs-metrics-events-and-traces.md)
- [Kubernetes Workload Controllers Và Rollout](../01-core-objects/02-workload-controllers-and-rollout.md)
- [Kubernetes Troubleshooting Runbooks](../98-troubleshooting/overview.md)
