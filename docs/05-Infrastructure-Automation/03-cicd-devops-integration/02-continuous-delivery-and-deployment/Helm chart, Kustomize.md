# Helm Chart Và Kustomize

## Helm Là Gì

Helm là package manager cho Kubernetes. Thay vì copy nhiều manifest YAML rời rạc giữa các môi trường, Helm đóng gói cấu hình ứng dụng thành chart có template, giá trị đầu vào và metadata version.

Một Helm chart thường có:

```text
mychart/
├── Chart.yaml
├── values.yaml
└── templates/
```

## Helm Workflow

Luồng làm việc cơ bản:

1. Developer hoặc platform team tạo chart với `templates/` và `values.yaml`.
2. Chart được lưu trong Git hoặc chart repository để version, review và chia sẻ.
3. Admin/DevOps dùng Helm CLI để install, upgrade hoặc rollback.
4. Helm render template với values tương ứng rồi gửi manifest tới Kubernetes API.
5. Cùng một chart có thể deploy vào `dev`, `staging`, `production` bằng các file values khác nhau.

```bash
helm install myapp ./mychart -f values-dev.yaml
helm upgrade myapp ./mychart -f values-prod.yaml
helm rollback myapp 1
helm history myapp
```

## Vì Sao Dùng Helm

- Một chart có thể tái sử dụng cho nhiều môi trường.
- Dễ version control cùng Git.
- Giảm lỗi do copy/paste YAML thủ công.
- Hỗ trợ upgrade, rollback và history.
- Chuẩn hóa cách deploy cùng một ứng dụng trên nhiều cluster.

## Khi Cần Cẩn Thận

- Không đưa Secret thật vào `values.yaml` trong Git.
- Review manifest render ra trước khi deploy production:

```bash
helm template myapp ./mychart -f values-prod.yaml
helm diff upgrade myapp ./mychart -f values-prod.yaml
```

- Tách rõ values chung và values theo môi trường.
- Không biến chart thành nơi chứa toàn bộ logic ứng dụng; chart nên mô tả deployment, service, ingress, config và dependency hạ tầng gần ứng dụng.

## Related Pages

- [Kubernetes Operations Quick Reference](../../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/01-core-objects/00-kubernetes-operations-quick-reference.md)
