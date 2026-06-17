# Kubernetes Up And Running Source Coverage

## Overview

> Trạng thái canonicalization: legacy source-derived note set. Các file dài trong bộ này cần được bóc thành knowledge atom, merge vào canonical Kubernetes notes, rồi giữ lại ở đây như coverage matrix ngắn.

Nguồn đúc kết chính: `_inbox/kubernetes-up-and-running-9781098110208.docx`.

Mục tiêu của cụm note này là chuyển hóa kiến thức từ `Kubernetes: Up and Running, Third Edition` thành ghi chú tiếng Việt dễ học, không chép lại sách. File DOCX có khoảng **89,718 words**, **3,432 paragraphs** và **279 PNG media**. Trong đó có **16 figure caption chính**; các hình hữu ích đã được trích vào thư mục `images/` cạnh note.

Sách này mới hơn `Kubernetes in Action` và thiên về cách nhìn cloud native/application/platform hơn: velocity, immutability, declarative config, team scaling, API separation, service mesh, policy/governance, multicluster và tổ chức manifest trong source control.

## Knowledge Map

| Nhánh kiến thức | Vị trí trong nguồn | Note chuyển hóa | Hình chính |
|---|---:|---|---:|
| Cloud native, containers, cluster, kubectl | Preface + Ch.1-4 | [Foundations, Containers, Cluster And kubectl](./01-foundations-containers-cluster-kubectl.md) | 1 |
| Pods, labels, Service, Ingress, ReplicaSet, Deployment | Ch.5-10 | [Core Objects, Networking And Rollouts](./02-core-objects-networking-rollouts.md) | 6 |
| DaemonSet, Job, Config/Secret, RBAC, mesh, storage | Ch.11-16 | [Workload Patterns, Config, RBAC, Mesh And Storage](./03-workload-patterns-config-rbac-mesh-storage.md) | 3 |
| CRD, API clients, application security, policy/governance | Ch.17-20 | [Extensibility, API Clients, Security And Policy](./04-extensibility-api-security-policy.md) | 4 |
| Multicluster, source organization, lab cluster | Ch.21-22 + appendix | [Multicluster, Source Organization And Lab Cluster](./05-multicluster-source-organization-lab-cluster.md) | 2 |
| Index + author/colophon pages | cuối sách | Không chuyển hóa vì không phải kiến thức kỹ thuật reusable | 0 |

## Figures Used In These Notes

| Figure | Local image |
|---|---|
| 1-1 API separation across operations layers | `./images/figure-01-01-api-decoupled-ops.png` |
| 5-1 Pod with two containers and shared filesystem | `./images/figure-05-01-pod-shared-filesystem.png` |
| 6-1 Labels applied to deployments | `./images/figure-06-01-labels-visualization.png` |
| 7-1 Cluster IP and kube-proxy flow | `./images/figure-07-01-cluster-ip.png` |
| 8-1 Software Ingress controller | `./images/figure-08-01-ingress-controller.png` |
| 10-1 Decoupled vs coupled application architectures | `./images/figure-10-01-decoupled-vs-coupled-app.png` |
| 10-2 Deployment lifecycle | `./images/figure-10-02-deployment-lifecycle.png` |
| 12-1 Parallel jobs | `./images/figure-12-01-parallel-jobs.png` |
| 13-1 kuard environment | `./images/figure-13-01-kuard-environment.png` |
| 13-2 Config directory | `./images/figure-13-02-config-directory.png` |
| 17-1 API server request flow | `./images/figure-17-01-api-server-request-flow.png` |
| 17-2 CRD interactions | `./images/figure-17-02-crd-interactions.png` |
| 19-1 RuntimeClass flow | `./images/figure-19-01-runtimeclass-flow.png` |
| 20-1 API request through admission | `./images/figure-20-01-api-request-admission-flow.png` |
| 22-1 Cherry-pick workflow | `./images/figure-22-01-cherry-pick-workflow.png` |
| 22-2 Development tag workflow | `./images/figure-22-02-development-tag-workflow.png` |

## Placement Decision

| Knowledge area from source | Canonical destination | Source-digest role |
|---|---|---|
| Cloud native principles, immutability, declarative config, team scaling | `00-architecture`, `07-cluster-lifecycle` | preserve book-level operating model |
| Container images, Dockerfile, image registry, cluster bootstrap, kubectl workflow | `02-container-runtime`, `01-core-objects`, `07-cluster-lifecycle` | keep learning path and command mental model |
| Pods, labels, Service, Ingress, ReplicaSet, Deployment | `01-core-objects`, `02-networking`, `07-cluster-lifecycle` | giữ mạch học theo object và link về note canonical |
| DaemonSet, Jobs, ConfigMap, Secret, RBAC, service mesh, storage | `01-core-objects`, `04-security`, `09-application-integration`, `03-storage` | preserve production patterns |
| CRD, API clients, security context, policy/governance | `10-advanced`, `04-security` | map modern platform extension and governance concepts |
| Multicluster and source organization | `10-advanced`, `07-cluster-lifecycle` | preserve application lifecycle and release organization model |

## Cách Đọc Cụm Note Này

Nhóm note này được viết để:

- mọi chapter technical 1-22 đã được đọc theo paragraph range;
- appendix "Building Your Own Kubernetes Cluster" đã được chuyển hóa ở mức conceptual/runbook safety;
- mọi figure caption chính đã được map và ảnh đã được trích;
- nội dung được viết lại bằng lời Việt, không sao chép dài;
- phần index, author bio và colophon không được convert vì không phải reusable technical knowledge.

## Related Canonical Notes

- [Kubernetes Overview](../../overview.md)
- [Pods, Labels, Namespaces Và Metadata](../../01-core-objects/01-pods-labels-namespaces-and-metadata.md)
- [Service Discovery, Ingress Và Network Policy](../../02-networking/01-service-discovery-ingress-and-network-policy.md)
- [Resources, Probes, Autoscaling Và Disruption](../../05-operations/01-resources-probes-autoscaling-and-disruption.md)
- [ConfigMap, Secret, Downward API Và API Access](../../09-application-integration/01-configmap-secret-downward-api-and-api-access.md)
- [CRD, Operators, Policy Và Multicluster](../../10-advanced/01-crd-operators-policy-and-multicluster.md)
