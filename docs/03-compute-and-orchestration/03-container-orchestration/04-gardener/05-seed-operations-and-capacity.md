# Gardener Seed Operations Và Capacity

## Overview

Seed là cluster hạ tầng dùng để host control plane của nhiều Shoot. Nếu Shoot là workload ở cấp cluster, Seed là nơi workload đó chạy. Vận hành Seed vì vậy giống vận hành một cluster platform có blast radius lớn hơn cluster app thông thường.

## Seed Responsibilities

- Chạy gardenlet.
- Host Shoot control plane namespaces.
- Chạy provider extensions và controller phụ trợ.
- Cung cấp capacity cho số lượng Shoot control plane.
- Kết nối tới Garden API và hạ tầng provider.

## Capacity Model

Các yếu tố cần theo dõi:

- số Shoot đang chạy trên Seed;
- CPU/memory cho control plane namespaces;
- quota và node capacity của Seed;
- network/VPN tunnel;
- extension controller saturation;
- etcd/control plane backup footprint nếu áp dụng;
- maintenance window và upgrade wave.

## Health Signals

- Seed conditions.
- gardenlet readiness và logs.
- Shoot control plane Pods trong Seed.
- Extension controller health.
- API latency của Seed.
- Resource pressure trên Seed nodes.

## Operational Guardrails

- Không đặt quá nhiều Shoot quan trọng lên cùng một Seed nếu chưa tính blast radius.
- Seed upgrade cần wave và rollback plan.
- gardenlet certificate/bootstrap phải được theo dõi như thành phần critical.
- Extension outage có thể làm nhiều Shoot reconcile fail cùng lúc.
- Seed failure không nhất thiết làm workload trong Shoot chết ngay, nhưng làm lifecycle/control plane operations bị ảnh hưởng.

## Safe Checks

```bash
kubectl get seeds
kubectl describe seed <seed-name>
kubectl get pods -A | grep gardenlet
kubectl get ns | grep shoot--
kubectl top nodes
kubectl top pods -A
```

## Related Pages

- [Gardener Architecture And Core Concepts](./01-architecture-and-core-concepts.md)
- [Backup, Restore, Upgrade Và Maintenance](./06-backup-restore-upgrade-and-maintenance.md)
- [Seed Or gardenlet Not Ready](./troubleshooting/03-seed-or-gardenlet-not-ready.md)
