# GKE, Anthos And Container Platforms

## Tổng Quan

GCP có nhiều lớp để chạy container. **Google Kubernetes Engine (GKE)** là managed Kubernetes cho workload container cần Kubernetes API, scheduling, Service, storage integration, policy và autoscaling. **Anthos** là lớp quản trị hybrid/multi-cloud cho các Kubernetes environment và một số modernization workflow trên nhiều hạ tầng.

Không nên đọc GKE như "Compute Engine có thêm Docker". GKE là Kubernetes managed service: Google giảm phần vận hành control plane và một số lifecycle của cluster, còn team platform/application vẫn chịu trách nhiệm về workload design, IAM, network exposure, image security, secret, observability, backup/DR và cost governance.

## GKE Service Boundary

| Thành phần | Google quản lý nhiều hơn | Team vẫn phải quản lý |
|---|---|---|
| Control plane | API server/control-plane lifecycle tùy mode và configuration | Kubernetes object, RBAC, admission/policy, upgrade impact lên workload |
| Worker capacity | Node provisioning/maintenance nhiều hơn ở Autopilot; Standard cho nhiều quyền cấu hình node hơn | Requests/limits, node pool design, workload placement, autoscaling policy |
| Networking | Integration với VPC, load balancer, cluster networking primitives | Private/public exposure, firewall, NetworkPolicy, ingress/gateway, DNS/TLS |
| Security | Managed primitives như IAM integration, node/workload identity option, security posture features tùy cấu hình | Least privilege, image scanning, secret handling, Pod security, supply chain control |
| Observability | Integration với Cloud Logging/Monitoring nếu bật đúng | SLO, alert rule, dashboard, trace/log context, incident response |

## Autopilot Vs Standard

| Mode | Mental model | Dùng khi | Tradeoff |
|---|---|---|---|
| Autopilot | GKE quản lý nhiều hơn về node/capacity | Team muốn giảm day-2 node operations, workload theo best practice tương đối chuẩn | Ít quyền tinh chỉnh node/daemon/host-level behavior hơn; cần kiểm tra constraint của workload |
| Standard | Team cấu hình cluster/node pool rõ hơn | Cần custom node pool, daemon, accelerator, networking/security setting riêng, migration phức tạp | Nhiều trách nhiệm hơn về node lifecycle, capacity, upgrade và cost cleanup |

Lựa chọn mode nên dựa trên workload constraint và operating model, không chỉ dựa trên cảm giác "serverless" hay "kiểm soát nhiều hơn".

## Cluster Placement Decisions

Khi tạo GKE cluster production, các quyết định nên được review như một architecture decision:

- **Location type**: zonal, multi-zonal hoặc regional ảnh hưởng availability, latency và cost. Workload production quan trọng thường cần tránh single-zone failure.
- **Node pool design**: tách workload theo profile CPU/memory/GPU, trust level, lifecycle và autoscaling behavior.
- **Release channel/upgrade policy**: chọn tốc độ nhận update phù hợp với appetite rủi ro; cần test workload trên non-prod trước khi production bị upgrade.
- **Networking**: ưu tiên private cluster/private node khi phù hợp; kiểm soát endpoint control plane, authorized networks, ingress/egress và NAT.
- **Identity**: dùng least privilege cho service account và workload identity; tránh gán quyền rộng cho default service account.
- **Storage**: hiểu StorageClass/CSI, reclaim policy, backup/restore và behavior khi Pod/node bị thay thế.
- **Observability**: bật log/metric/event cần thiết, thêm alert cho saturation, crashloop, pending Pod, unavailable replica và error budget burn.

## GKE Production Guardrails

Pre-check trước khi deploy workload:

```bash
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.lastTimestamp
kubectl auth can-i create deployments -n <namespace>
```

Khi thay đổi production:

- Chạy `kubectl diff` hoặc dry-run trước khi apply manifest.
- Đặt requests/limits, readiness/liveness/startup probe và PodDisruptionBudget cho service quan trọng.
- Kiểm tra EndpointSlice/Service sau rollout; Deployment available không đồng nghĩa traffic đã đi đúng backend.
- Có rollback manifest/image và biết giới hạn rollback với database migration hoặc external state.
- Cảnh báo rõ với thao tác destructive như delete namespace, delete PVC/PV, drain node, patch finalizer hoặc scale về `0`. Ưu tiên read-only checks và change window.

Validation sau rollout:

```bash
kubectl rollout status deployment/<name> -n <namespace>
kubectl get deploy,rs,pod,svc,endpointslice -n <namespace>
kubectl describe deployment/<name> -n <namespace>
kubectl logs deployment/<name> -n <namespace> --tail=100
```

## Anthos

Anthos phù hợp khi organization cần quản trị Kubernetes trên GCP, cloud khác, VMware/bare metal/on-premises hoặc edge theo một operating model thống nhất. Giá trị chính không phải là "thêm một console", mà là standardization:

- quản lý configuration/policy theo Git-style source of truth;
- visibility và governance cho nhiều cluster;
- modernization path cho workload đang ở VM/on-premises;
- service mesh cho traffic management, observability và security giữa microservices;
- policy/compliance guardrails nhất quán giữa environment.

Rủi ro cần review trước khi chọn Anthos:

- dependency vào Google ecosystem và agent/control plane integration;
- permission scope của agent trong cluster ngoài GCP;
- network path, latency và egress giữa clusters;
- ownership rõ ràng giữa platform team, security team và application team;
- cost/licensing và operational maturity cho multi-cluster governance.

## Khi Chọn Các Lựa Chọn Container Trên GCP

| Nhu cầu | Lựa chọn thường hợp lý |
|---|---|
| Cần Kubernetes API, controller, Service, policy và portability cao | GKE |
| Muốn giảm node operations tối đa cho workload phù hợp constraint | GKE Autopilot |
| Cần tinh chỉnh node pool, host-level config, daemon hoặc migration phức tạp | GKE Standard |
| Cần quản trị Kubernetes hybrid/multi-cloud/on-premises | Anthos |
| Chạy HTTP container stateless, muốn giảm vận hành Kubernetes | [Cloud Run](./04-app-engine-cloud-run-and-cloud-functions.md) |
| Cần VM/OS control đầy đủ | Compute Engine |

## Trang Liên Quan

- [Google Cloud Platform Overview](./overview.md)
- [GCP Compute Engine, VMware Engine And Bare Metal](./02-compute-engine-vmware-and-bare-metal.md)
- [App Engine, Cloud Run And Cloud Functions](./04-app-engine-cloud-run-and-cloud-functions.md)
- [Container Vs VM Concepts](../../../03-compute-and-orchestration/02-container-runtime/Container%20vs%20VM%20concepts.md)
- [Kubernetes](../../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/overview.md)
- [Kubernetes Architecture](../../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/00-architecture/overview.md)
