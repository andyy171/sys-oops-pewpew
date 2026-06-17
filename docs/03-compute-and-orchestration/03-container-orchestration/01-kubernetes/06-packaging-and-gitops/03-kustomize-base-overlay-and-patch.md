# Kubernetes Kustomize Base, Overlay Và Patch

## Why This Exists

Kustomize giúp quản lý nhiều biến thể của cùng một application bằng `base` và `overlay`, không cần template language. Nó phù hợp khi YAML gốc khá rõ ràng nhưng mỗi môi trường cần khác replica, image, label, namespace, config hoặc Ingress host.

## Mental Model

```text
base manifests
-> overlay dev/staging/prod
-> patches / generators / transformers
-> rendered manifests
-> apply or GitOps sync
```

Base giữ phần giống nhau. Overlay chỉ chứa khác biệt thật sự của môi trường.

## Core Objects / Components Involved

- `kustomization.yaml`
- `resources`
- `patches`
- `images`
- `configMapGenerator`
- `secretGenerator` nếu dùng, nhưng cần cẩn thận với secret plaintext
- `namespace`, `namePrefix`, `labels`, `annotations`

## How It Works

Ví dụ layout:

```text
apps/
  checkout/
    base/
      deployment.yaml
      service.yaml
      kustomization.yaml
    overlays/
      dev/
        kustomization.yaml
      prod/
        kustomization.yaml
        patch-resources.yaml
```

Render:

```bash
kubectl kustomize apps/checkout/overlays/prod
kubectl diff -k apps/checkout/overlays/prod
kubectl apply -k apps/checkout/overlays/prod
```

## How To Inspect

```bash
kubectl kustomize <overlay-path>
kubectl diff -k <overlay-path>
kubectl apply -k <overlay-path> --dry-run=server
```

Sau khi apply:

```bash
kubectl get deploy,svc,ingress -n <namespace>
kubectl describe deploy <name> -n <namespace>
```

## Common Confusions

| Confusion | Reality |
|---|---|
| Overlay là bản copy đầy đủ của base | Overlay chỉ nên chứa khác biệt cần thiết |
| Patch càng nhiều càng linh hoạt | Patch quá nhiều làm prod khác staging và khó review |
| Kustomize thay thế GitOps | Kustomize render manifest; GitOps là reconciliation workflow |
| `configMapGenerator` tự làm app reload | App reload phụ thuộc cách consume ConfigMap và rollout strategy |

## Parameterization Theo Region

Khi application chạy ở nhiều region, khác biệt giữa region thường gồm:

- image registry gần region nếu không dùng geo-replicated registry;
- replica count, resource request/limit và HPA target theo traffic;
- Ingress/Gateway hostname, certificate, region label;
- endpoint dependency theo locality hoặc data sovereignty;
- feature flag hoặc config liên quan đến compliance địa phương.

Không nên copy nguyên manifest cho từng region rồi sửa tay. Pattern bền hơn:

```text
base/
  deployment.yaml
  service.yaml
overlays/
  us-east/
    kustomization.yaml
    patch-replicas.yaml
  eu-west/
    kustomization.yaml
    patch-registry.yaml
```

Base giữ object model chung; overlay chỉ giữ khác biệt thật sự. Nếu mỗi overlay chứa quá nhiều patch riêng, staging sẽ không còn đại diện cho production và drift theo region sẽ tăng rất nhanh.

## Khi Gặp Tool Khác Như Carvel ytt/kapp

Một số tài liệu dùng Carvel `ytt`/`kapp` để minh họa packaging application. Có thể đọc chúng theo mental model chung:

- `ytt` là template/overlay engine cho YAML;
- `kapp` quản lý apply, diff, ownership và lifecycle của một tập resource;
- Kustomize là overlay/patch không có template language;
- Helm là packaging/template ecosystem phổ biến hơn.

Điểm quan trọng không nằm ở tên tool, mà là quy trình phải render được manifest cuối cùng, review diff được, apply lặp lại được và có ownership rõ. Trong KB này, Kustomize/GitOps vẫn là baseline; các tool khác nên được ghi như biến thể khi môi trường thật sự dùng.

## Production Notes

- Giữ base nhỏ, ổn định và dễ đọc.
- Prod overlay không nên có patch "bí mật" khiến staging không còn đại diện cho prod.
- Dùng image digest hoặc image tag bất biến.
- Kiểm tra rendered manifest trong CI.
- Không để secret plaintext trong overlay nếu repo không được thiết kế cho secret encryption.

## Related Pages

- [Source Of Truth, Manifest Và Drift](./01-source-of-truth-manifest-and-drift.md)
- [ConfigMap, Secret, Downward API Và API Access](../09-application-integration/01-configmap-secret-downward-api-and-api-access.md)
- [Environment Promotion, Release Và Rollback](./05-environment-promotion-release-and-rollback.md)
