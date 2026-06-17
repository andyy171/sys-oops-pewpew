# Gardener Projects, Identity Và Access

## Overview

Gardener dùng `Project` để gom Shoot theo team, tenant hoặc môi trường quản trị. Access trong Gardener cần tách rõ: ai được thao tác resource trong Garden cluster, ai được truy cập Shoot cluster, và credentials nào được dùng để tạo hạ tầng cloud.

## Project Model

Project thường trả lời các câu hỏi:

- Team hoặc tenant nào sở hữu Shoot?
- Namespace nào trong Garden cluster chứa Shoot?
- User/group nào có quyền tạo, sửa, xóa hoặc đọc Shoot?
- Credentials provider nào được phép dùng trong Project?

## Identity Layers

| Lớp | Ý nghĩa |
|---|---|
| Garden user/group | Người hoặc automation gọi Gardener API |
| Project role/RBAC | Quyền thao tác Shoot và resource trong Project |
| Shoot access | Kubeconfig hoặc token để truy cập cluster con |
| Cloud credentials | Credentials để Gardener tạo network, VM, LB, DNS, disk |
| Workload identity trong Shoot | ServiceAccount/RBAC của app bên trong cluster |

## Access Principles

- Tách quyền tạo/sửa Shoot khỏi quyền admin bên trong Shoot.
- Ưu tiên short-lived kubeconfig hoặc token thay vì credential dài hạn.
- Không cấp quyền Project rộng cho automation chỉ cần đọc trạng thái.
- Không dùng cùng cloud credentials cho quá nhiều tenant nếu cần blast radius nhỏ.
- Audit thao tác thay đổi Shoot spec, credentials binding và Project membership.

## Common Risks

- User có quyền sửa Shoot nhưng không hiểu tác động immutable field.
- CI/CD dùng credential quá rộng, có thể xóa hoặc update nhầm nhiều cluster.
- Cloud credentials hết hạn hoặc rotate mà Shoot không reconcile được.
- Static kubeconfig bị lưu trong máy cá nhân hoặc pipeline logs.

## Safe Checks

```bash
kubectl get projects
kubectl describe project <project-name>
kubectl get shoots -n <project-namespace>
kubectl auth can-i get shoots -n <project-namespace>
kubectl auth can-i update shoots -n <project-namespace>
```

## Related Pages

- [Gardener Overview](./overview.md)
- [CloudProfiles, Credentials Và Provider Extensions](./04-cloudprofiles-credentials-and-provider-extensions.md)
- [Shoot Access And Kubeconfig](./troubleshooting/02-shoot-access-and-kubeconfig.md)
