# Kubernetes Security, RBAC Và Pod Hardening

## Overview

Kubernetes security có nhiều lớp: ai được gọi API, workload chạy với quyền gì, Pod có thể dùng namespace/capability nào, traffic giữa Pod có bị giới hạn không, secret có được bảo vệ không, và admission policy có chặn cấu hình rủi ro không.

`Kubernetes in Action` giải thích authentication, ServiceAccount, RBAC, security context, host namespace, PodSecurityPolicy và NetworkPolicy. Vì tài liệu này dựa trên Kubernetes cũ, phần PodSecurityPolicy cần được đọc như lịch sử: PodSecurityPolicy đã bị deprecate và removed; hiện nên dùng Pod Security Admission hoặc policy engine như Kyverno/Gatekeeper tùy platform.

Đọc sâu: [RBAC, Pod Security Và Admission Deep Dive](./01-rbac-pod-security-and-admission.md).

## Security Layers

| Lớp | Câu hỏi |
|---|---|
| API access | user/service account nào được làm gì |
| Namespace boundary | workload/team nào nằm ở đâu |
| RBAC | quyền đọc/sửa/xóa object nào |
| Pod security | container có chạy root/privileged/hostPath không |
| Secret handling | secret được lưu, đọc, rotate ra sao |
| NetworkPolicy | Pod nào được gọi Pod nào |
| Admission policy | cấu hình rủi ro có bị chặn trước khi chạy không |
| Image supply chain | image có trusted registry, scan, ký không |

## ServiceAccount

ServiceAccount là identity cho Pod khi gọi Kubernetes API.

Best practices:

- Không dùng `default` ServiceAccount cho workload quan trọng.
- Tạo ServiceAccount riêng theo app/component.
- Tắt automount token nếu app không cần gọi API Server.
- Chỉ bind quyền tối thiểu.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: checkout-api
automountServiceAccountToken: false
```

## RBAC

RBAC gồm:

- `Role`: quyền trong namespace.
- `ClusterRole`: quyền cluster-wide hoặc reusable role.
- `RoleBinding`: gán Role/ClusterRole trong namespace.
- `ClusterRoleBinding`: gán quyền cluster-wide.

Ví dụ Role read-only Pod trong namespace:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
```

Kiểm tra quyền:

```bash
kubectl auth can-i get pods -n <namespace>
kubectl auth can-i delete pods -n <namespace> --as system:serviceaccount:<namespace>:<serviceaccount>
```

Tránh:

- bind `cluster-admin` cho CI/CD mặc định,
- cho quyền `get/list/watch secrets` rộng,
- dùng wildcard `*` khi không cần,
- dùng ClusterRoleBinding cho quyền chỉ cần trong một namespace.

## Security Context

Security context kiểm soát quyền runtime của Pod/container.

Ví dụ baseline tốt:

```yaml
securityContext:
  runAsNonRoot: true
  seccompProfile:
    type: RuntimeDefault
containers:
- name: app
  image: example.com/app:<tag>
  securityContext:
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: true
    capabilities:
      drop:
      - ALL
```

Cần cẩn trọng với:

- `privileged: true`,
- `hostNetwork: true`,
- `hostPID: true`,
- `hostIPC: true`,
- `hostPath`,
- thêm Linux capabilities rộng,
- chạy container bằng root nếu không cần.

## Pod Security Admission

Pod Security Admission áp Pod Security Standards ở namespace level qua label. Ba mức phổ biến:

- `privileged`: ít hạn chế, dành cho system/infra workload đặc biệt.
- `baseline`: chặn cấu hình nguy hiểm phổ biến.
- `restricted`: hardening mạnh hơn, phù hợp workload thường nếu app tương thích.

Ví dụ namespace enforce baseline, warn restricted:

```bash
kubectl label namespace app \
  pod-security.kubernetes.io/enforce=baseline \
  pod-security.kubernetes.io/warn=restricted \
  pod-security.kubernetes.io/audit=restricted
```

Với policy phức tạp hơn, dùng Kyverno/Gatekeeper hoặc admission controller tương đương.

## Secrets

Secret không phải nơi "an toàn tuyệt đối". Nó cần RBAC, encryption at rest, audit và rotation.

Checklist:

- Không commit Secret manifest chứa giá trị thật.
- Hạn chế quyền đọc Secret.
- Bật encryption at rest nếu tự quản lý cluster.
- Dùng External Secrets/Vault/cloud secret manager nếu có.
- Rotate secret và đảm bảo app reload hoặc rollout đúng cách.

## NetworkPolicy

NetworkPolicy là lớp giảm blast radius. Nếu cluster hỗ trợ, nên có default deny ở namespace quan trọng rồi mở rule theo nhu cầu.

```bash
kubectl get networkpolicy -A
kubectl describe networkpolicy <name> -n <namespace>
```

Không có NetworkPolicy thường đồng nghĩa east-west traffic quá rộng.

## Security Review Checklist

- Mỗi workload có ServiceAccount riêng.
- Không có quyền cluster-wide nếu không cần.
- Không chạy privileged/host namespace trừ workload hạ tầng.
- Có Pod Security Admission hoặc policy engine.
- Secret không nằm trong ConfigMap, image layer hoặc Git plaintext.
- NetworkPolicy áp dụng cho namespace production.
- Image đến từ registry được phép và được scan.
- Audit log/API access có thể truy vết.

## Related Pages

- [RBAC, Pod Security Và Admission Deep Dive](./01-rbac-pod-security-and-admission.md)
- [Kubernetes Workload Design And Best Practices](../01-core-objects/03-workload-design-and-best-practices.md)
- [Pods, Labels, Namespaces Và Metadata](../01-core-objects/01-pods-labels-namespaces-and-metadata.md)
- [Kubernetes Networking, Services Và Ingress](../02-networking/overview.md)
- [Kubernetes Operations, Resources Và Observability](../05-operations/overview.md)
