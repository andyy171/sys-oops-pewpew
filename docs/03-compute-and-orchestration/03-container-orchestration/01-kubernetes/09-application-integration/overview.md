# Kubernetes Application Integration, Configuration Và API Access

## Overview

Kubernetes không chỉ chạy container; nó còn là integration layer cho config, secret, service discovery, external resources, API access và automation. App tốt trên Kubernetes cần tách image khỏi config, dùng Service/Secret đúng cách và chỉ gọi API Server khi thật sự cần.

`Secret` trong folder này nói về cách application consume Secret qua env, mounted file hoặc projected volume. Security/hardening của Secret, RBAC và admission policy nằm ở [Kubernetes Security](../04-security/overview.md).

Đọc sâu: [ConfigMap, Secret, Downward API Và API Access](./01-configmap-secret-downward-api-and-api-access.md).

## ConfigMap

ConfigMap dùng cho cấu hình không nhạy cảm:

```bash
kubectl create configmap app-config --from-literal=APP_MODE=prod
kubectl create configmap app-config --from-file=config.yaml
```

Cách consume:

- environment variable,
- file qua volume,
- command argument.

ConfigMap thay đổi không đồng nghĩa app tự reload. Tùy cách mount/inject và behavior của app, có thể cần rollout lại Deployment.

## Secret

Secret dùng cho dữ liệu nhạy cảm, nhưng vẫn cần bảo vệ bằng RBAC và encryption.

```bash
kubectl create secret generic db-credential \
  --from-literal=username=<user> \
  --from-literal=password=<PASSWORD>
```

Best practices:

- Không commit secret thật.
- Không inject secret vào log hoặc command line.
- Hạn chế quyền đọc Secret.
- Dùng external secret manager nếu production yêu cầu.

## Downward API

Downward API inject metadata của Pod vào container mà không cần app gọi API Server.

Use case:

- biết Pod name/namespace,
- expose labels/annotations cho app,
- truyền resource requests/limits vào process.

Ưu tiên Downward API khi app chỉ cần biết chính nó là ai.

## Calling Kubernetes API From Pods

App chỉ nên gọi API Server nếu nó là controller/operator/automation hoặc thật sự cần đọc cluster state.

Checklist:

- ServiceAccount riêng.
- Role tối thiểu.
- Watch/list scope nhỏ nhất có thể.
- Handle retry, rate limit và watch reconnect.
- Không dùng token default nếu không cần.

Kiểm tra quyền:

```bash
kubectl auth can-i list pods \
  --as system:serviceaccount:<namespace>:<serviceaccount> \
  -n <namespace>
```

## External Services

Không phải mọi dependency đều phải chạy trong cluster. Có thể tích hợp:

- managed database,
- legacy service,
- external message queue,
- cloud API.

Pattern:

- Service `ExternalName` cho DNS alias đơn giản.
- Service không selector + EndpointSlice cho endpoint cụ thể.
- Secret/ExternalSecret cho credential.
- NetworkPolicy/egress policy để giới hạn outbound.

## Extending With CRD And Controllers

CRD thêm resource type mới vào Kubernetes API. Controller/operator reconcile custom resource đó.

Mental model:

```text
CustomResource desired state -> custom controller -> external/system state
```

CRD phù hợp khi muốn biến một domain vận hành thành Kubernetes-native API, ví dụ database cluster, certificate, backup, DNS record. Không nên tạo CRD chỉ để thay thế một ConfigMap đơn giản.

## Related Pages

- [ConfigMap, Secret, Downward API Và API Access](./01-configmap-secret-downward-api-and-api-access.md)
- [Pods, Labels, Namespaces Và Metadata](../01-core-objects/01-pods-labels-namespaces-and-metadata.md)
- [Kubernetes Security, RBAC Và Pod Hardening](../04-security/overview.md)
- [Kubernetes Storage, Volumes Và Stateful Workloads](../03-storage/overview.md)
- [Kubernetes Advanced Platform Patterns](../10-advanced/overview.md)
