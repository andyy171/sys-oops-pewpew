# Gardener

Gardener là một nền tảng quản lý Kubernetes clusters bằng chính mô hình Kubernetes API/controller. Nếu Kubernetes quản lý Pod trên Node, thì Gardener quản lý các Kubernetes cluster con trên các Seed cluster.

Mục tiêu học Gardener trong vault này: hiểu nhanh các object, luồng reconcile và trách nhiệm vận hành quan trọng trước khi đọc sâu tài liệu official vốn khá hàn lâm.

## Cách Hiểu Nhanh

```text
Garden cluster
  -> Gardener API + controllers
  -> Project / CloudProfile / SecretBinding / Shoot
  -> Scheduler chọn Seed
  -> gardenlet trên Seed reconcile Shoot control plane
  -> Shoot worker nodes chạy workload thật
```

So sánh gần đúng với Kubernetes:

| Kubernetes | Gardener |
|---|---|
| Pod | Shoot cluster |
| Node | Seed cluster |
| kube-apiserver | gardener-apiserver |
| kube-controller-manager | gardener-controller-manager |
| kube-scheduler | gardener-scheduler |
| kubelet | gardenlet |

## Khi Nào Cần Gardener

- Cần quản lý nhiều Kubernetes clusters trên nhiều provider hoặc nhiều region.
- Muốn cluster lifecycle có API chuẩn: create, update, reconcile, rotate credentials, upgrade, delete.
- Muốn tách tenant/project, quota, credentials và cloud profile theo mô hình platform.
- Muốn platform team cung cấp Kubernetes như một service nội bộ hoặc public.

Không nên học Gardener như một công cụ deploy app. Gardener quản lý cluster lifecycle; app deployment vẫn thường đi qua GitOps, CI/CD, Helm/Kustomize hoặc platform workflow khác.

## Core Vocabulary

| Thuật ngữ | Ý nghĩa thực dụng |
|---|---|
| Garden cluster | Cluster trung tâm chạy Gardener API/controllers và lưu các resource quản lý |
| Seed cluster | Cluster hạ tầng dùng để host control plane của các Shoot |
| Shoot cluster | Kubernetes cluster được Gardener tạo và quản lý cho user/team |
| Project | Boundary cộng tác và namespace trong Garden cluster cho nhóm Shoot |
| CloudProfile | Mô tả provider, region, zone, machine type, OS image, Kubernetes version khả dụng |
| SecretBinding / CredentialsBinding | Cầu nối từ Shoot tới credentials cloud provider |
| gardener-scheduler | Chọn Seed phù hợp cho Shoot |
| gardenlet | Agent chạy trên Seed, reconcile Shoot thuộc Seed đó |
| Extension | Controller ngoài core dùng cho provider/network/OS/DNS/infrastructure-specific logic |

## Cấu Trúc Note Đề Xuất

```text
04-gardener/
  overview.md
  01-architecture-and-core-concepts.md
  02-shoot-lifecycle-and-day2-operations.md
  03-projects-identity-and-access.md
  04-cloudprofiles-credentials-and-provider-extensions.md
  05-seed-operations-and-capacity.md
  06-backup-restore-upgrade-and-maintenance.md
  07-observability-and-troubleshooting-map.md
  08-openstack-provider-integration.md
  troubleshooting/
    overview.md
    01-shoot-reconcile-failed.md
    02-shoot-access-and-kubeconfig.md
    03-seed-or-gardenlet-not-ready.md
```

Trước mắt nên đọc và phát triển theo thứ tự:

1. [Architecture And Core Concepts](./01-architecture-and-core-concepts.md)
2. Shoot lifecycle và immutable fields.
3. Project, access, short-lived kubeconfig và credentials.
4. Provider extensions, CloudProfile, SecretBinding/CredentialsBinding.
5. Seed capacity, gardenlet health, control plane migration và backup/restore.
6. Observability và troubleshooting theo Garden -> Seed -> Shoot.
7. Nếu chạy trên private cloud, đọc thêm [Gardener OpenStack Provider Integration](./08-openstack-provider-integration.md).

## Những Điều Cần Nhớ Nhất

- Shoot là Kubernetes resource; thay đổi Shoot spec sẽ trigger reconcile giống thay đổi Deployment spec trong Kubernetes.
- Control plane của Shoot thường chạy trong Seed cluster; worker nodes/data plane thuộc infrastructure account của user.
- gardenlet là thành phần then chốt trên Seed; nếu gardenlet lỗi, Shoot trên Seed đó có thể không reconcile đúng.
- Provider-specific config thường do extension xử lý, Gardener core không hiểu hết và không validate được mọi lỗi ngay lúc update.
- Nhiều field của Shoot là immutable hoặc one-way sau khi tạo, ví dụ account hạ tầng, network ranges, upgrade Kubernetes version, một số thiết lập HA.
- Access vào Shoot hiện đại nên dùng short-lived credentials thay vì static kubeconfig dài hạn.

## Related Pages

- [Kubernetes](../01-kubernetes/overview.md)
- [Kubernetes CRD, Operators, Policy Và Multicluster](../01-kubernetes/10-advanced/01-crd-operators-policy-and-multicluster.md)
- [Kubernetes Operations, Resources Và Observability](../01-kubernetes/05-operations/overview.md)
- [Gardener Troubleshooting](./troubleshooting/overview.md)
- [Gardener OpenStack Provider Integration](./08-openstack-provider-integration.md)

## Nguồn Tham Khảo

- [Gardener Architecture](https://gardener.cloud/docs/gardener/concepts/architecture/)
- [Gardener Shoots](https://gardener.cloud/docs/getting-started/shoots/)
- [Gardener API Server Concepts](https://gardener.cloud/docs/gardener/concepts/apiserver/)
- [gardenlet](https://gardener.cloud/docs/gardener/concepts/gardenlet/)
- [Gardener Scheduler](https://gardener.cloud/docs/gardener/concepts/scheduler/)
- [Gardener Extensions](https://gardener.cloud/docs/gardener/extensions/)
