# Gardener Architecture And Core Concepts

## Overview

Gardener áp dụng Kubernetes operator pattern để quản lý Kubernetes clusters. Thay vì tự xây một control plane riêng với object model riêng, Gardener biểu diễn cluster người dùng dưới dạng Kubernetes custom resources trong Garden cluster, rồi dùng controller để reconcile hạ tầng, control plane và worker nodes.

Mental model quan trọng:

```text
Shoot spec = desired state của một Kubernetes cluster
Shoot status / conditions / lastOperation = actual state và tiến trình reconcile
gardenlet + extensions = thành phần biến desired state thành cluster thật
```

## Garden, Seed Và Shoot

| Thành phần | Vai trò |
|---|---|
| Garden cluster | Nơi chạy Gardener control plane và API mở rộng |
| Seed cluster | Nơi host control plane của Shoot và các controller phụ trợ |
| Shoot cluster | Cluster Kubernetes mà user sử dụng để chạy workload |

Điểm khác với managed Kubernetes thông thường: control plane của Shoot không nhất thiết nằm trong cloud provider managed service. Nó được Gardener deploy vào Seed cluster, còn worker nodes nằm trong account hạ tầng của user.

## Control Plane Flow

Luồng tạo Shoot ở mức cao:

```text
User tạo Shoot trong Project namespace
  -> gardener-apiserver validate/lưu object
  -> gardener-scheduler chọn Seed
  -> gardenlet trên Seed nhận trách nhiệm
  -> tạo namespace cho Shoot control plane trong Seed
  -> extension tạo network/infrastructure/DNS/OS config theo provider
  -> deploy Shoot control plane
  -> tạo worker machines và bootstrap kubelet
  -> deploy kube-system add-ons
  -> Shoot chuyển sang healthy/active nếu reconcile thành công
```

Debug Gardener vì vậy phải nhìn cả ba lớp:

- Garden layer: `Project`, `Shoot`, `CloudProfile`, credentials binding, events.
- Seed layer: gardenlet, Shoot control plane namespace, extension resources, machine controller.
- Shoot layer: node, kube-system, workload, CNI/CSI/add-ons.

## Object Model Cốt Lõi

| Object | Dùng để làm gì | Câu hỏi vận hành |
|---|---|---|
| `Project` | Nhóm Shoot và user/team trong Garden cluster | Ai được tạo/quản lý cluster? |
| `CloudProfile` | Provider capabilities: region, zone, machine, OS, version | Shoot có chọn option hợp lệ không? |
| `SecretBinding` / `CredentialsBinding` | Gắn credentials provider vào Shoot | Credentials còn đúng và cùng account không? |
| `Shoot` | Desired state của cluster user | Spec/status/conditions đang nói gì? |
| `Seed` | Nơi đặt Shoot control plane | Seed có capacity/condition phù hợp không? |
| Extension resources | Infrastructure, DNS, network, OS, control plane plugin | Extension nào reconcile fail? |

## Scheduling: Shoot Vào Seed

Gardener scheduler giống kube-scheduler về mental model: chọn nơi phù hợp cho workload, nhưng workload ở đây là Shoot control plane, còn node tương đương là Seed.

Các yếu tố thường ảnh hưởng:

- provider/region của Shoot;
- seed selector và label của Seed;
- taint/toleration giữa Seed và Shoot;
- network range không được overlap vì còn cần kết nối VPN/control-plane-to-data-plane;
- capacity tối đa số Shoot trên Seed;
- yêu cầu HA control plane theo zone.

Sau khi scheduler chọn xong, `spec.seedName` của Shoot được set và gardenlet của Seed đó bắt đầu reconcile.

## Reversed Control Flow Và gardenlet

gardenlet là agent chạy trên Seed, tương tự kubelet ở node. Thay vì Gardener central controller phải trực tiếp truy cập mọi Seed/Shoot, gardenlet chủ động kết nối về Gardener API server và báo trạng thái Seed/Shoot mà nó quản lý.

Ý nghĩa vận hành:

- Seed/Shoot có thể nằm sau firewall dễ hơn vì không cần mọi kết nối inbound trực tiếp từ Garden.
- gardenlet health là tín hiệu cực quan trọng cho khả năng reconcile.
- Nếu gardenlet bootstrap/certificate/permission lỗi, Shoot trên Seed có thể bị kẹt operation.

## Provider Extensions

Gardener core cố tình không nhúng toàn bộ logic provider. Các phần như infrastructure, DNS, OS config, network và provider-specific control plane thường do extension controllers xử lý.

Điều này giống Kubernetes tách CSI/CNI/cloud-controller-manager:

```text
Gardener core: lifecycle framework và object model
Provider extension: cloud/provider-specific reconciliation
```

Hệ quả:

- Lỗi provider-specific có thể chỉ xuất hiện sau khi reconcile, không bị bắt ngay khi update Shoot.
- Khi debug, phải biết extension nào chịu trách nhiệm cho infrastructure/network/DNS/worker.
- Platform team cần quản lý version, registration và health của extensions như một phần của Gardener landscape.

## Access Và Credentials

Gardener hiện đại ưu tiên short-lived credentials cho Shoot access. Static credentials dài hạn không còn là default tốt cho vận hành.

Các lớp credentials cần tách rõ:

- credentials để Gardener tạo hạ tầng trong cloud account;
- credentials/token để user truy cập Shoot cluster;
- internal secrets do Gardener dùng để vận hành control plane;
- ServiceAccount/RBAC bên trong Shoot cho workload.

Không nên đưa cloud credentials thật vào note. Dùng placeholder như `<TOKEN>`, `<SECRET>`, `example-project`.

## Immutable Và One-Way Decisions

Một số quyết định nên chốt kỹ trước khi tạo Shoot:

- infrastructure account hoặc credential boundary;
- VPC/network range, pod CIDR, service CIDR, node CIDR mask;
- region/zone layout;
- HA control plane mode;
- Kubernetes version upgrade path;
- worker pool architecture và OS image support.

Nếu sai những phần này, thường phải recreate/migrate thay vì sửa trực tiếp trên cluster hiện có.

## Quan Sát Nhanh

Các lệnh dưới đây chỉ là hướng đọc object, không thay thế runbook production:

```bash
kubectl get projects
kubectl get shoots -A
kubectl describe shoot <shoot-name> -n <project-namespace>
kubectl get seeds
kubectl describe seed <seed-name>
kubectl get events -n <project-namespace> --sort-by=.metadata.creationTimestamp
```

Ở Seed cluster, cần context đúng trước khi chạy:

```bash
kubectl get pods -n garden
kubectl get pods -A | grep gardenlet
kubectl get ns | grep shoot--
```

Luôn xác nhận kubeconfig/context trước, vì thao tác Gardener thường đi qua nhiều cluster.

## Related Pages

- [Gardener Overview](./overview.md)
- [Kubernetes Control Plane, Node Và Reconciliation](../01-kubernetes/00-architecture/01-control-plane-node-and-reconciliation.md)
- [Kubernetes CRD, Operators, Policy Và Multicluster](../01-kubernetes/10-advanced/01-crd-operators-policy-and-multicluster.md)

## Nguồn Tham Khảo

- [Gardener Architecture](https://gardener.cloud/docs/gardener/concepts/architecture/)
- [Gardener Shoots](https://gardener.cloud/docs/getting-started/shoots/)
- [gardenlet](https://gardener.cloud/docs/gardener/concepts/gardenlet/)
- [Gardener Scheduler](https://gardener.cloud/docs/gardener/concepts/scheduler/)
- [Gardener Extensions](https://gardener.cloud/docs/gardener/extensions/)
