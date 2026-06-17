# Gardener Shoot Access And Kubeconfig

## Triệu Chứng

- User không truy cập được Shoot API.
- Kubeconfig/token hết hạn.
- RBAC trong Shoot từ chối thao tác.
- API endpoint resolve được nhưng TLS hoặc authentication fail.

## Triage Nhanh

```bash
kubectl config current-context
kubectl describe shoot <shoot-name> -n <project-namespace>
kubectl auth can-i get shoots -n <project-namespace>
```

Sau khi có kubeconfig Shoot hợp lệ:

```bash
kubectl get nodes
kubectl get ns
kubectl auth can-i get pods -A
```

## Phân Biệt Lỗi

| Nhóm lỗi | Dấu hiệu |
|---|---|
| Không có quyền trong Garden | Không đọc/lấy được Shoot hoặc credential |
| Credential hết hạn | Kubeconfig từng dùng được nhưng nay fail auth |
| Shoot API không healthy | Không kết nối được API endpoint hoặc timeout |
| RBAC trong Shoot | Login được nhưng bị forbidden khi thao tác resource |
| Network/DNS | Không resolve hoặc không route tới endpoint |

## Mitigation

- Cấp quyền theo Project thay vì quyền rộng toàn Garden.
- Ưu tiên short-lived credential và hướng dẫn user refresh đúng cách.
- Nếu Shoot API không healthy, chuyển sang runbook reconcile/control plane.
- Nếu RBAC trong Shoot thiếu quyền, sửa Role/RoleBinding trong Shoot, không nhầm với Project permission ở Garden.

## Related Pages

- [Projects, Identity Và Access](../03-projects-identity-and-access.md)
- [Shoot Reconcile Failed](./01-shoot-reconcile-failed.md)
