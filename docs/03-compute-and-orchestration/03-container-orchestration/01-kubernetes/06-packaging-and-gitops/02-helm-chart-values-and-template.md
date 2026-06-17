# Kubernetes Helm Chart, Values Và Template

## Why This Exists

Helm giải quyết bài toán đóng gói application Kubernetes có nhiều object, nhiều biến cấu hình và lifecycle release. Thay vì copy nhiều YAML cho từng môi trường, chart giữ template chung và cho phép truyền `values` khác nhau.

Helm phù hợp khi app có cấu trúc lặp lại, cần version release rõ, hoặc cần phân phối cho nhiều cluster/team.

## Mental Model

```text
Chart template + values
-> helm template/render
-> Kubernetes manifest
-> apply/install/upgrade
-> release history
```

Helm không thay Kubernetes object model. Nó là packaging/rendering layer phía trước API server.

## Core Objects / Components Involved

- `Chart.yaml`: metadata và chart version.
- `values.yaml`: default configuration.
- `templates/`: YAML template.
- release: bản cài đặt chart vào namespace.
- hooks: Job/task chạy quanh install/upgrade/delete nếu cần.

## How It Works

Helm render template bằng values để tạo manifest cuối cùng. Manifest đó vẫn gồm Deployment, Service, Ingress, ConfigMap, Secret reference, RBAC hoặc object khác.

Flow an toàn:

```text
choose chart version
-> choose values file
-> render template
-> inspect diff
-> install/upgrade
-> wait rollout
-> verify app
```

Không nên copy nguyên cây YAML cho từng môi trường rồi sửa tay từng file. Cách đó dễ tạo drift ngoài ý muốn giữa dev/staging/prod. Helm phù hợp khi phần lớn object giống nhau, còn khác biệt nằm ở values có chủ ý như replica count, image tag, resource request, hostname, feature flag hoặc storage class.

## Minimal Example

```bash
helm template myapp ./chart -f values-prod.yaml
helm lint ./chart
helm upgrade --install myapp ./chart -n <namespace> -f values-prod.yaml --dry-run
helm upgrade --install myapp ./chart -n <namespace> -f values-prod.yaml --wait
helm history myapp -n <namespace>
```

## How To Inspect

```bash
helm list -A
helm status <release> -n <namespace>
helm get values <release> -n <namespace>
helm get manifest <release> -n <namespace>
kubectl get all -n <namespace> -l app.kubernetes.io/instance=<release>
```

## Common Confusions

| Confusion | Reality |
|---|---|
| Helm chart là source of truth tuyệt đối | Chart + values + chart version mới tạo ra desired manifest cuối cùng |
| `values.yaml` prod nên chứa mọi thứ | Values nên chứa biến môi trường cần thiết, không chứa secret plaintext |
| Helm rollback rollback mọi thứ | Helm rollback manifest release; data và external dependency vẫn cần kế hoạch riêng |
| Template càng thông minh càng tốt | Template quá nhiều logic làm review khó và dễ sinh manifest bất ngờ |

## Release Boundary Và Hooks

Helm release là một instance của chart trong namespace. Khi đóng gói nhiều Kubernetes object vào cùng một chart, hãy hỏi: các object này có cần upgrade và rollback cùng nhau không?

Nên cùng chart/release khi:

- các object là một đơn vị ứng dụng có lifecycle chung;
- rollback một phần sẽ làm app không tương thích;
- hook/migration/backup phải chạy trước hoặc sau upgrade của nhóm object đó.

Nên tách chart/release khi:

- component có lifecycle độc lập;
- một phần được platform team vận hành, phần khác do app team vận hành;
- rollback chung làm tăng blast radius không cần thiết.

Helm hooks hữu ích cho task như backup trước upgrade, migration, smoke test hoặc cleanup. Nhưng hook không biến data rollback thành an toàn tự động. Với production:

- hook Job phải idempotent hoặc có cách detect đã chạy;
- backup phải có restore verification, không chỉ có command dump;
- hook delete policy cần tránh xóa evidence khi upgrade lỗi;
- rollback manifest phải đi cùng kế hoạch cho database/schema/external state.

## Production Notes

- Pin chart version và image digest/tag bất biến.
- Render manifest trong CI để review trước khi apply.
- Không để secret plaintext trong values commit vào Git.
- Dùng `--atomic` cẩn thận: rollback tự động hữu ích nhưng không thay thế validation.
- Nếu dùng GitOps, để GitOps controller quản lý Helm rendering thay vì vừa Helm CLI vừa GitOps ghi cùng object.

### Ansible Va Helm

Ansible co the orchestrate Helm CLI/module, nhung source of truth van nen la chart, values va rendered manifest co review. Tranh de Ansible va GitOps controller cung ghi cung object neu chua co ownership boundary.

Tai lieu cu ve Helm v2/Tiller nen duoc doc nhu legacy context. Voi Helm v3, identity goi Helm la identity goi Kubernetes API, nen RBAC cua runner/operator phai duoc review nhu moi client Kubernetes khac.

## Related Pages

- [Source Of Truth, Manifest Và Drift](./01-source-of-truth-manifest-and-drift.md)
- [GitOps, Argo CD, Flux Và Reconciliation](./04-gitops-argocd-flux-and-reconciliation.md)
- [Environment Promotion, Release Và Rollback](./05-environment-promotion-release-and-rollback.md)
- [Ansible Kubernetes Automation](../../../../05-infrastructure-automation/07-configuration-management/01-ansible/10-kubernetes-automation.md)
