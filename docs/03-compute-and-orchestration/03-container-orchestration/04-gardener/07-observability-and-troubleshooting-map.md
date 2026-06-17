# Gardener Observability Và Troubleshooting Map

## Overview

Troubleshooting Gardener phải đi theo ba lớp: Garden, Seed và Shoot. Nếu nhảy thẳng vào workload trong Shoot, dễ bỏ qua lỗi nằm ở scheduler, gardenlet, extension hoặc Shoot control plane đang được host trong Seed.

## Layered Debug Model

```text
Symptom
  -> Garden object: Shoot status, conditions, events
  -> Seed: gardenlet, extension resources, control plane namespace
  -> Shoot: API, nodes, kube-system, workload
  -> Provider: quota, network, DNS, VM, disk, LB
```

## Tín Hiệu Quan Trọng

| Tín hiệu | Đọc ở đâu | Ý nghĩa |
|---|---|---|
| `Shoot.status.lastOperation` | Garden cluster | Operation đang chạy hoặc lỗi ở bước nào |
| `Shoot.status.conditions` | Garden cluster | Health tổng quan của cluster |
| Project events | Garden cluster | Lý do fail gần nhất |
| gardenlet logs | Seed cluster | Reconcile loop và lỗi từ Seed side |
| Extension logs/status | Seed cluster | Provider-specific failure |
| Shoot control plane Pods | Seed cluster | API server/controller/scheduler của Shoot |
| Node và kube-system | Shoot cluster | Data plane và add-ons |

## Troubleshooting Order

1. Xác nhận context: Garden, Seed hay Shoot.
2. Đọc `Shoot.status.lastOperation` và events.
3. Nếu scheduler/Seed issue, kiểm tra Seed conditions và gardenlet.
4. Nếu provider issue, kiểm tra extension resource/log và quota provider.
5. Nếu Shoot API issue, kiểm tra control plane namespace trong Seed.
6. Nếu workload issue, chuyển sang Kubernetes troubleshooting bình thường trong Shoot.

## Common Failure Groups

- Không schedule được Shoot vào Seed.
- Credentials hoặc quota provider sai.
- Network range overlap hoặc VPN/control-plane-to-data-plane lỗi.
- Extension controller lỗi hoặc version không tương thích.
- gardenlet không ready hoặc mất kết nối tới Garden.
- Shoot control plane Pod crash hoặc Pending trong Seed.
- Worker nodes không join Shoot.
- User không lấy được kubeconfig hoặc credential hết hạn.

## Related Runbooks

- [Shoot Reconcile Failed](./troubleshooting/01-shoot-reconcile-failed.md)
- [Shoot Access And Kubeconfig](./troubleshooting/02-shoot-access-and-kubeconfig.md)
- [Seed Or gardenlet Not Ready](./troubleshooting/03-seed-or-gardenlet-not-ready.md)
