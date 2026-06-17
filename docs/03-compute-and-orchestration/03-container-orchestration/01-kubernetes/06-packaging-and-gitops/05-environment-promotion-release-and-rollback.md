# Kubernetes Environment Promotion, Release Và Rollback

## Why This Exists

Deploy lên Kubernetes không chỉ là `kubectl apply`. Production release cần quyết định artifact nào được promote, môi trường nào đại diện cho prod, ai review, rollout quan sát bằng gì và rollback xử lý đến đâu.

Đây là canonical home cho application release và environment organization trong Kubernetes.

## Mental Model

```text
dev
-> staging
-> prod canary/region low traffic
-> prod broader rollout
-> observe
-> rollback or continue
```

Promotion tốt không copy YAML bằng tay. Nó promote artifact có định danh rõ: image digest, Helm chart version, Kustomize base revision, config version hoặc policy revision.

## Version, Release Và Runtime Revision

Trong Kubernetes production, cần tách rõ nhiều lớp version:

- **application version**: version business/API của toàn ứng dụng hoặc service, thường theo semantic versioning;
- **container image version/digest**: artifact runtime cụ thể được build từ commit/pipeline;
- **Pod template revision**: thay đổi trong `spec.template` như image, env, ConfigMap checksum, resource hoặc probe;
- **release name/number**: ID của lần phát hành từ CI/CD hoặc Helm release để trace ai/commit/pipeline nào tạo ra trạng thái hiện tại.

Các lớp này không bắt buộc tăng cùng lúc. Ví dụ image có thể giữ nguyên nhưng Pod template đổi vì thêm Secret reference, ConfigMap checksum hoặc resource request; khi đó rollback phải biết đang rollback application behavior, manifest revision hay image artifact.

Semantic versioning hữu ích cho API compatibility: patch không phá contract, minor thêm tính năng backward-compatible, major báo hiệu breaking change. Với microservices, đây là tín hiệu để service phụ thuộc biết có cần đổi client/API contract hay không.

## Core Objects / Components Involved

- Deployment/StatefulSet rollout.
- Image registry và immutable tag/digest.
- Helm values hoặc Kustomize overlay.
- ConfigMap/Secret references.
- Job migration nếu có data/schema change.
- HPA/PDB/probes/requests.
- GitOps application hoặc CI/CD pipeline.

## How It Works

Checklist trước release:

- image tag bất biến hoặc digest;
- manifest/rendered diff đã review;
- requests/limits phù hợp quota;
- readiness/liveness/startup probe đúng;
- migration plan nếu có database change;
- rollback target rõ;
- metric cần theo dõi đã có dashboard/alert;
- owner trực release biết namespace/context.

Pipeline tối thiểu:

```text
render manifest
-> schema validate
-> policy validate
-> diff
-> apply/sync
-> wait rollout
-> post-check
```

## Release Strategy Trong Kubernetes

Deployment rolling update chỉ là một cơ chế rollout ở cấp Kubernetes object. Release strategy ở production còn bao gồm traffic routing, schema compatibility, feature flag, observability gate và rollback decision.

![](./images/kbp2e-global-rollout-callout-01.png)

Ba strategy phổ biến:

- **Rolling update**: dễ bắt đầu, built-in với Deployment, nhưng trong thời gian rollout sẽ có nhiều version cùng chạy.
- **Blue/green**: chạy song song version cũ/mới và switch traffic ở Service/Ingress/Gateway/LB; rollback nhanh nhưng tốn capacity và phức tạp với database migration.
- **Canary**: chuyển một phần traffic sang version mới, quan sát steady state rồi tăng dần; cần metric theo version và routing control tốt.

Checklist trước khi chọn blue/green hoặc canary:

- dependency/API contract có chịu được nhiều version cùng lúc không;
- database schema có backward/forward compatibility không;
- metric có tách được version cũ và mới không;
- traffic router có hỗ trợ percentage/header/region/user segment không;
- rollback có an toàn với data đã ghi bởi version mới không.

Chi tiết strategy nằm ở note CI/CD: [Blue/Green, Canary Và Rolling](../../../../05-infrastructure-automation/03-cicd-devops-integration/02-continuous-delivery-and-deployment/BlueGreen,%20Canary,%20Rolling.md).

## Global Rollout Và Time-To-Smoke

Rollout toàn cầu không nên mở đồng thời tất cả region. Mỗi region production là một cơ hội phát hiện lỗi mà staging, integration test hoặc load test chưa bắt được.

![](./images/kbp2e-global-rollout-callout-02.png)

Một thứ tự an toàn hơn:

```text
pre-rollout validation
-> canary region / internal traffic
-> low-traffic region giống canary
-> high-traffic region giống canary
-> region có input/traffic khác biệt
-> parallel rollout khi các nhóm rủi ro chính đã được kiểm chứng
```

`time-to-smoke` là khoảng thời gian cần chờ sau một rollout để lỗi có xác suất cao bộc lộ qua metric, log, alert hoặc phản hồi người dùng. Ví dụ memory leak có thể mất hàng giờ mới hiện ra, nên rollout vùng kế tiếp ngay sau khi Pod Ready là quá vội.

Khi lập rollout plan, phân loại region theo:

- traffic thấp/cao;
- loại client như mobile/web/API;
- ngôn ngữ/input Unicode;
- dependency hoặc data locality khác nhau;
- yêu cầu compliance/data sovereignty.

Canary region vẫn là production về monitoring, scale và operational discipline, nhưng người dùng/consumer của nó phải hiểu rằng đây là nơi nhận release sớm hơn để phát hiện vấn đề trước khi mở rộng.

![](./images/kbp2e-global-rollout-callout-03.png)

## Khi Global Rollout Có Vấn Đề

Runbook phản ứng sự cố rollout cần viết sẵn và diễn tập trước:

- dừng rollout pipeline hoặc GitOps wave tiếp theo;
- xác định region/version bị ảnh hưởng;
- chuyển traffic khỏi region lỗi nếu có thể;
- rollback/roll-forward theo artifact đã biết;
- xác nhận data/schema/queue/external dependency có tương thích rollback không;
- giữ evidence: events, deployment revision, metric, logs, traces, CI/CD run.

Traffic drain cần được rehearsal. DNS-based traffic shifting có thể bị cache lâu hơn kỳ vọng, nên RTO thật phải đo bằng thực nghiệm: mất bao lâu để drain 50%, 90%, 99% traffic khỏi region. Nếu không đạt mục tiêu, cần thay đổi kiến trúc hoặc automation thay vì chỉ viết runbook đẹp hơn.

## Minimal Example

```bash
kubectl diff -f manifests/
kubectl apply -f manifests/
kubectl rollout status deployment/<name> -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
```

Rollback Deployment:

```bash
kubectl rollout history deployment/<name> -n <namespace>
kubectl rollout undo deployment/<name> -n <namespace>
kubectl rollout status deployment/<name> -n <namespace>
```

## How To Inspect

```bash
kubectl get deploy,rs,pod -n <namespace> -l app=<app>
kubectl describe deployment <name> -n <namespace>
kubectl rollout history deployment/<name> -n <namespace>
kubectl get hpa,pdb -n <namespace>
kubectl top pods -n <namespace>
```

Post-release check nên nhìn thêm error rate, latency, saturation, logs và business metric nếu có.

## Common Confusions

| Confusion | Reality |
|---|---|
| Staging xanh là prod chắc xanh | Staging chỉ đáng tin nếu quota, policy, dependency và traffic model đủ gần prod |
| `rollout status` xanh là release xong | Pod available không đảm bảo app business flow đúng |
| Rollback luôn an toàn | Schema migration, queue message, external dependency và config có thể không rollback |
| Canary chỉ cần ít replica | Canary cần metric, traffic routing và quyết định dừng/tiếp rõ |
| Version app, image và release là một | Chúng là các lớp khác nhau; phải trace được từng lớp về Git/CI/CD/runtime |
| Đổi label nào cũng tạo rollout | Deployment chỉ rollout khi `spec.template` đổi; label ngoài Pod template thường không tạo ReplicaSet mới |

## Production Notes

- Với service quan trọng, dùng `maxUnavailable=0` nếu không muốn mất capacity trong rolling update.
- Dùng readiness probe để Pod mới chỉ nhận traffic khi thật sự sẵn sàng; dùng `preStop`/graceful shutdown để giảm rớt connection khi Pod cũ bị terminate.
- Giữ image cũ trong registry đủ lâu để rollback.
- Chuẩn hóa label/annotation release như `app.kubernetes.io/version`, `app.kubernetes.io/instance`, `app.kubernetes.io/managed-by` hoặc convention nội bộ tương đương để dashboard, audit và rollback nhìn cùng một ngôn ngữ.
- Release number nên trỏ về CI/CD run hoặc Git SHA; tránh label mơ hồ như `stable` nếu không có rule rõ ai được chuyển trạng thái đó.
- Không release từ kubeconfig admin trên máy cá nhân.
- Dùng feature flag để tách deploy khỏi release khi phù hợp.
- Dọn feature flag cũ; flag lâu ngày trở thành cấu hình production khó kiểm soát.
- Với multi-region, rollout theo thứ tự có chủ đích và chờ đủ "mean time to smoke" trước khi mở rộng.

## Related Pages

- [Source Of Truth, Manifest Và Drift](./01-source-of-truth-manifest-and-drift.md)
- [Helm Chart, Values Và Template](./02-helm-chart-values-and-template.md)
- [Kustomize Base, Overlay Và Patch](./03-kustomize-base-overlay-and-patch.md)
- [Workload Controllers Và Rollout](../01-core-objects/02-workload-controllers-and-rollout.md)
