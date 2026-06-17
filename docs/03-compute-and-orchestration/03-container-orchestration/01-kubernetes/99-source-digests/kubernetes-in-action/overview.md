# Kubernetes In Action Source Coverage

## Overview

> Trạng thái canonicalization: legacy source-derived note set. Các file dài trong bộ này cần được bóc thành knowledge atom, merge vào canonical Kubernetes notes, rồi giữ lại ở đây như coverage matrix ngắn.

Nguồn đúc kết chính: `_inbox/Kubernetes_in_Action_Marko_Luksa.docx`.

Mục tiêu của cụm note này là chuyển hóa kiến thức từ `Kubernetes in Action` thành ghi chú tiếng Việt theo mental model vận hành. Vì file DOCX này được convert theo kiểu mỗi trang là một đoạn lớn và có **628 ảnh JPG dạng full-page screenshot**, phần hình không được nhúng hàng loạt vào vault. Các hình có giá trị minh họa đã được xử lý ở các pass trước hoặc được thay bằng diễn giải/diagram note gần chủ đề.

Điểm cần đọc thận trọng: sách xuất bản năm 2018 nên nhiều API/ví dụ trong sách đã là lịch sử, ví dụ `ReplicationController`, `extensions/v1beta1 Ingress`, `apps/v1beta1 Deployment`, `PodSecurityPolicy`, `kubectl rolling-update`, `rkt`, `Ksonnet`, `Service Catalog`, `Cluster Federation` kiểu cũ. Note trong vault giữ lại giá trị conceptual và gắn nhãn legacy khi cần.

## Knowledge Map

| Nhánh kiến thức | Vị trí trong nguồn | Note chuyển hóa |
|---|---:|---|
| Nền tảng, Docker, workload đầu tiên | Ch.1-2, trang 1-54 | [Foundations And First Workload](./01-foundations-and-first-workload.md) |
| Pod, controller, Service | Ch.3-5, trang 55-158 | [Core Objects, Controllers And Services](./02-core-objects-controllers-and-services.md) |
| Storage, config, API access, rollout, StatefulSet | Ch.6-10, trang 159-308 | [Storage, Config, API, Deployments And StatefulSets](./03-storage-config-api-deployments-statefulsets.md) |
| Internals, security, resources, autoscaling, scheduling | Ch.11-16, trang 309-476 | [Internals, Security, Resources And Scheduling](./04-internals-security-resources-scheduling.md) |
| App practices, extensibility, kubectl contexts, kubeadm, runtimes, federation | Ch.17-18 + appendices, trang 477-560 | [App Practices, Extensibility And Appendices](./05-app-practices-extensibility-and-appendices.md) |
| Index | trang 561 | Không chuyển hóa vì chỉ là phần tra cứu |

## Placement Decision

| Knowledge area from source | Canonical destination | Source-digest role |
|---|---|---|
| Kubernetes motivation, container model, first workload | `00-architecture`, `01-core-objects`, `07-cluster-lifecycle` | keep source learning flow and legacy notes |
| Pod, labels, namespace, liveness, controllers, Service | `01-core-objects`, `02-networking`, `98-troubleshooting` | giữ mạch học của nguồn và link về note canonical |
| Volumes, ConfigMap, Secret, Downward API, API access, Deployment, StatefulSet | `03-storage`, `09-application-integration`, `07-cluster-lifecycle` | record source-specific operational lessons |
| Internals, API server, scheduler, controllers, kubelet, kube-proxy | `00-architecture` | deepen control plane/data plane mental model |
| RBAC, ServiceAccount, node security, NetworkPolicy, resources, HPA, advanced scheduling | `04-security`, `05-operations` | keep legacy-to-modern mapping |
| App lifecycle, graceful shutdown, development workflow, CRD, Service Catalog, OpenShift/Helm, appendices | `10-advanced`, `07-cluster-lifecycle`, `98-troubleshooting` | preserve older ecosystem concepts and modern interpretation |

## Cách Đọc Cụm Note Này

Nhóm note này được viết để:

- mọi chapter/appendix technical đã được đọc theo page range và map vào digest;
- mọi section/subsection chính trong mục lục đã có diễn giải tương ứng;
- kiến thức reusable được viết lại bằng lời Việt, không copy dài từ sách;
- API/công cụ cũ được giữ ở dạng historical context thay vì hướng dẫn hiện đại;
- các link canonical giúp đi từ note chuyển hóa sang note vận hành chính.

Không chuyển hóa thành note:

- index cuối sách, vì chỉ là lookup reference;
- từng pixel của 628 ảnh full-page JPG;
- exact command output/listing dài từ sách;
- behavior version-specific cũ nếu trái với Kubernetes hiện đại.

## Related Canonical Notes

- [Control Plane, Node Và Reconciliation](../../00-architecture/01-control-plane-node-and-reconciliation.md)
- [Pods, Labels, Namespaces Và Metadata](../../01-core-objects/01-pods-labels-namespaces-and-metadata.md)
- [Workload Controllers Và Rollout](../../01-core-objects/02-workload-controllers-and-rollout.md)
- [Service Discovery, Ingress Và Network Policy](../../02-networking/01-service-discovery-ingress-and-network-policy.md)
- [Persistent Storage Và StatefulSet](../../03-storage/01-persistent-storage-and-statefulsets.md)
- [RBAC, Pod Security Và Admission](../../04-security/01-rbac-pod-security-and-admission.md)
- [Resources, Probes, Autoscaling Và Disruption](../../05-operations/01-resources-probes-autoscaling-and-disruption.md)
- [ConfigMap, Secret, Downward API Và API Access](../../09-application-integration/01-configmap-secret-downward-api-and-api-access.md)
- [CRD, Operators, Policy Và Multicluster](../../10-advanced/01-crd-operators-policy-and-multicluster.md)
