# Gardener CloudProfiles, Credentials Và Provider Extensions

## Overview

`CloudProfile`, credentials binding và provider extensions là cầu nối giữa Gardener core và cloud/provider thật. Đây là nơi nhiều lỗi production xuất hiện vì Gardener object hợp lệ về schema chưa chắc provider bên dưới có quota, permission, network hoặc image tương thích.

## CloudProfile

CloudProfile mô tả những gì platform cho phép user chọn:

- provider type;
- region và zone;
- machine type;
- volume type;
- OS image;
- Kubernetes version;
- constraint hoặc option đặc thù provider.

CloudProfile tốt giúp giảm lỗi ngay từ lúc tạo Shoot vì user chỉ chọn trong tập option đã được platform team kiểm soát.

## Credentials Binding

Credentials binding nối Shoot với secret/credential dùng để tạo hạ tầng.

Checklist:

- Credential thuộc đúng account/subscription/project.
- Có quyền tối thiểu để tạo network, VM, disk, LB, DNS theo provider.
- Có quy trình rotate rõ ràng.
- Không lưu secret thật trong Git hoặc note.
- Có tách môi trường dev/staging/prod nếu cần giảm blast radius.

## Provider Extensions

Provider extensions reconcile phần Gardener core không nên nhúng cứng:

- infrastructure;
- DNS;
- network;
- OS config;
- worker/machine;
- control plane provider-specific settings.

Khi một Shoot reconcile fail, cần xác định extension nào đang báo lỗi thay vì chỉ nhìn `Shoot` tổng quát.

## Design Checklist Cho Platform Team

- Chuẩn hóa CloudProfile theo region/zone đang vận hành thật.
- Gỡ machine type hoặc OS image không còn support.
- Kiểm soát Kubernetes version được phép tạo mới và upgrade.
- Theo dõi health/version của extension controllers.
- Có changelog khi thay đổi CloudProfile vì nó ảnh hưởng cluster mới và upgrade path.

## Safe Checks

```bash
kubectl get cloudprofiles
kubectl describe cloudprofile <cloudprofile-name>
kubectl get shoots -A -o wide
kubectl describe shoot <shoot-name> -n <project-namespace>
```

## Related Pages

- [Gardener Architecture And Core Concepts](./01-architecture-and-core-concepts.md)
- [Projects, Identity Và Access](./03-projects-identity-and-access.md)
- [Shoot Reconcile Failed](./troubleshooting/01-shoot-reconcile-failed.md)
