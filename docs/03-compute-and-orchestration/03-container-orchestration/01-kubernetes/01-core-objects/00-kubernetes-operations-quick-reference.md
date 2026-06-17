# Kubernetes Operations Quick Reference

## Overview

Note này gom các ảnh Kubernetes trong `_inbox` thành một bản tham chiếu vận hành ngắn gọn. Mục tiêu không phải học thuộc toàn bộ lệnh, mà là biết khi nào dùng nhóm lệnh nào khi cần kiểm tra cluster, Pod, Deployment, Service, Ingress, ConfigMap, Secret và Namespace.

Khi thao tác với cluster thật, luôn xác nhận đúng context, namespace và môi trường trước khi `apply`, `delete`, `scale` hoặc `rollout`.

## Cluster Và Context

`kubectl` nói chuyện với Kubernetes API Server. Context trong kubeconfig quyết định lệnh đang chạy vào cluster nào, user nào và namespace mặc định nào.

```bash
kubectl cluster-info
kubectl config get-contexts
kubectl config use-context <context-name>
kubectl get nodes
kubectl top nodes
```

Checklist trước khi thay đổi production:

- Kiểm tra context hiện tại bằng `kubectl config get-contexts`.
- Kiểm tra namespace hiện tại bằng `kubectl config view --minify`.
- Kiểm tra node health bằng `kubectl get nodes`.
- Nếu dùng `kubectl top`, đảm bảo cluster đã có metrics-server.

## Pod

Pod là đơn vị deploy nhỏ nhất trong Kubernetes. Một Pod có thể chứa một hoặc nhiều container, chia sẻ network namespace và có vòng đời ngắn hơn Deployment.

```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl logs -f <pod-name>
kubectl exec -it <pod-name> -- /bin/sh
```

Luồng debug Pod cơ bản:

1. `kubectl get pods` để xem trạng thái, restart count và tuổi Pod.
2. `kubectl describe pod <pod-name>` để xem event, condition, image pull, scheduling và mount.
3. `kubectl logs <pod-name>` để đọc lỗi từ container.
4. `kubectl exec -it <pod-name> -- /bin/sh` chỉ khi cần kiểm tra bên trong container.
5. Sửa manifest hoặc configuration, sau đó verify lại bằng `get`, `describe`, `logs`.

Không nên xem `kubectl delete pod` là cách sửa lỗi lâu dài. Nếu Pod thuộc Deployment, ReplicaSet hoặc StatefulSet, controller sẽ tạo Pod mới. Nếu root cause nằm ở image, config, secret, resource limit hoặc node, Pod mới vẫn có thể lỗi lại.

## Deployment Và Rollout

Deployment quản lý ReplicaSet và duy trì số lượng Pod mong muốn cho workload stateless.

```bash
kubectl create deployment nginx --image=nginx:1.25
kubectl get deployments
kubectl describe deployment nginx
kubectl scale deployment nginx --replicas=5
kubectl set image deployment/nginx nginx=nginx:1.26
kubectl rollout status deployment/nginx
kubectl rollout history deployment/nginx
kubectl rollout undo deployment/nginx
```

Khi vận hành:

- Dùng Deployment cho ứng dụng stateless.
- Luôn đặt resource requests/limits phù hợp.
- Dùng readiness probe để tránh đưa Pod chưa sẵn sàng vào Service.
- Dùng liveness probe cẩn thận; probe quá hung hăng có thể tạo restart loop.
- Theo dõi rollout trước khi coi deployment là thành công.

## Job Và CronJob

Job dùng cho workload chạy đến khi hoàn thành, ví dụ batch processing, migration hoặc task một lần. CronJob dùng cho Job chạy theo lịch.

```bash
kubectl get jobs
kubectl describe job <job-name>
kubectl get pods --selector=job-name=<job-name>
kubectl logs job/<job-name>

kubectl get cronjobs
kubectl describe cronjob <cronjob-name>
kubectl create job manual-run --from=cronjob/<cronjob-name>
```

Khi debug Job:

1. Xem `COMPLETIONS`, `DURATION`, `AGE`.
2. Tìm Pod do Job tạo ra bằng label `job-name`.
3. Xem log Pod hoặc `kubectl logs job/<job-name>`.
4. Kiểm tra `backoffLimit`, `activeDeadlineSeconds`, image, command và environment.

## Service, Endpoint Và Ingress

Service cung cấp một endpoint ổn định cho tập Pod động. Selector của Service quyết định Pod nào nhận traffic.

```bash
kubectl get svc
kubectl describe svc <service-name>
kubectl get endpoints <service-name>
kubectl expose deployment app --port=80 --target-port=8080 --type=ClusterIP --name=app-service
kubectl port-forward svc/app-service 8080:80
kubectl get ingress
kubectl describe ingress <ingress-name>
```

Các loại Service thường gặp:

| Type | Khi dùng | Lưu ý |
|---|---|---|
| `ClusterIP` | Giao tiếp nội bộ trong cluster | Default, chỉ reachable bên trong cluster |
| `NodePort` | Lab hoặc bare metal đơn giản | Expose qua `<NodeIP>:<NodePort>`, khó quản lý ở production lớn |
| `LoadBalancer` | Cloud provider có LB tích hợp | Phụ thuộc cloud controller và chi phí LB |
| `ExternalName` | Trỏ Service name tới DNS bên ngoài | Không proxy traffic, chỉ tạo CNAME |
| Headless Service | Service discovery trực tiếp tới Pod IP | Hay dùng với StatefulSet |

Khi user không truy cập được ứng dụng qua Service hoặc Ingress, kiểm tra theo thứ tự:

1. Pod có `Ready` không.
2. Service selector có khớp label của Pod không.
3. `kubectl get endpoints <service-name>` có Pod IP không.
4. Port của Service có trỏ đúng `targetPort` không.
5. Ingress Controller có chạy không.
6. DNS, TLS, firewall hoặc external load balancer có đúng không.

## DNS Trong Kubernetes

Kubernetes thường dùng CoreDNS để tạo DNS record cho Service và Pod.

```text
<service-name>.<namespace>.svc.cluster.local
```

Ví dụ:

```text
my-svc.default.svc.cluster.local
```

Với headless Service, DNS có thể trả về nhiều Pod IP thay vì một ClusterIP. Điều này hữu ích cho StatefulSet hoặc ứng dụng cần tự quản lý peer discovery.

## ConfigMap Và Secret

ConfigMap dùng cho cấu hình không nhạy cảm. Secret dùng cho dữ liệu nhạy cảm như password, token, key. Secret trong Kubernetes được base64 encode, không tự động đồng nghĩa với mã hóa an toàn ở mọi lớp vận hành.

```bash
kubectl create configmap app-config --from-literal=APP_MODE=prod
kubectl create configmap app-config --from-file=config.properties
kubectl get configmaps
kubectl describe configmap app-config

kubectl create secret generic db-secret --from-literal=DB_USER=<user> --from-literal=DB_PASSWORD=<password>
kubectl get secrets
kubectl describe secret db-secret
```

Cách đưa ConfigMap/Secret vào Pod:

- Mount thành file qua volume.
- Inject thành environment variable.

Best practices:

- Không lưu dữ liệu nhạy cảm trong ConfigMap.
- Hạn chế quyền đọc Secret bằng RBAC.
- Không đưa Secret thật vào Git.
- Với production, cân nhắc external secret manager như Vault, cloud secret manager hoặc controller chuyên dụng.
- Rotate Secret định kỳ và kiểm tra workload có reload config đúng cách không.

## Namespace Và Resource Control

Namespace giúp tách workload theo môi trường, team hoặc project. Đây là boundary quản trị logic, không phải sandbox bảo mật tuyệt đối.

```bash
kubectl get ns
kubectl create ns dev
kubectl config set-context --current --namespace=dev
kubectl get quota -n dev
kubectl describe quota dev-quota -n dev
```

Namespace thường dùng để:

- Tách `dev`, `qa`, `staging`, `prod`.
- Áp dụng ResourceQuota và LimitRange.
- Giảm rủi ro đặt tên trùng.
- Áp dụng RBAC, NetworkPolicy và policy theo phạm vi nhỏ hơn cluster.

Trước khi apply manifest:

```bash
kubectl config view --minify | grep namespace
kubectl get all -n <namespace>
```

## Lệnh Quản Lý Manifest

```bash
kubectl apply -f app.yaml
kubectl delete -f app.yaml
kubectl apply -f app.yaml --dry-run=client
kubectl diff -f app.yaml
kubectl get events --sort-by=.metadata.creationTimestamp
```

Với YAML, luôn giữ đủ `apiVersion`, `kind`, `metadata` và `spec`. Dùng space thay vì tab, đặt tên có ý nghĩa và review diff trước khi apply vào môi trường quan trọng.

## Related Pages

- [Kubernetes Workload Design And Best Practices](./03-workload-design-and-best-practices.md)
- [Kubernetes Architecture](../00-architecture/overview.md)
- [Core Objects Overview](./overview.md)
- [Scheduling, Affinity, Taints, Topology Và Priority](../05-operations/03-scheduling-affinity-taints-topology-and-priority.md)
- [Observability Logs, Metrics, Events Và Traces](../05-operations/02-observability-logs-metrics-events-and-traces.md)
- [Image Pull Errors](../98-troubleshooting/image-pull-errors.md)
