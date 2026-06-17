# Container Orchestration

Container orchestration là lớp điều phối workload container: scheduling, health check, self-healing, rollout, scaling, service discovery và quản lý cấu hình.

## Notes

- [Kubernetes](./01-kubernetes/overview.md)
- [Gardener](./04-gardener/overview.md)

## Core Ideas

- Desired state vs actual state.
- Scheduler chọn node phù hợp cho workload.
- Controller liên tục reconcile trạng thái.
- Service discovery tách endpoint ổn định khỏi Pod/container thay đổi liên tục.
- Cluster lifecycle platform như Gardener dùng lại Kubernetes API/controller pattern để quản lý nhiều Kubernetes clusters.

## Container Platform Selection Framework

Một container platform không chỉ là orchestrator. Nó là tập hợp capability để build, phân phối, chạy, quan sát và kiểm soát container theo cách tổ chức có thể vận hành lâu dài.

Khi chọn platform, tránh bắt đầu bằng câu hỏi "dùng vendor nào". Bắt đầu bằng các câu hỏi vận hành:

- Tổ chức cần managed platform, self-hosted platform hay mô hình lai?
- Team có đủ năng lực vận hành control plane, upgrade, security patch, registry, logging, monitoring và network không?
- Mức lock-in chấp nhận được nằm ở đâu: cloud provider, Kubernetes distribution, registry, CI/CD, identity hay storage/network integration?
- Platform phải phục vụ một nhóm sản phẩm đồng nhất hay nhiều business unit có yêu cầu khác nhau?
- Ai chịu trách nhiệm khi image lỗi thời, secret lộ, registry down, cluster upgrade fail hoặc network policy chặn nhầm traffic?

Buy vs build là trade-off về tốc độ và ownership:

- **Buy/managed** giảm thời gian bootstrap, nhưng cần hiểu rõ shared responsibility model, exit path, billing, support boundary và giới hạn tích hợp.
- **Build/self-hosted** cho nhiều kiểm soát hơn, nhưng dễ thành "pet platform" nếu thiếu team vận hành, automation, test upgrade và roadmap rõ ràng.
- **Build then buy** có thể hợp lý khi cần học requirement nội bộ trước, nhưng phải có tiêu chí dừng; nếu không, platform tự xây sẽ trở thành legacy system riêng.

Checklist capability tối thiểu:

| Capability | Câu hỏi production |
|---|---|
| Build | Dockerfile/build pipeline có reproducible, scan, provenance và secret handling không? |
| Registry | Có auth/RBAC, retention, audit, replication, promotion theo digest và backup không? |
| Runtime | Orchestrator hỗ trợ rollout, health check, scheduling, quota, policy và upgrade path không? |
| Security | Có image signing/scanning, admission policy, secrets management, runtime hardening và incident forensics không? |
| Networking | IP range, service discovery, ingress/LB, TLS/mTLS, NAT/source IP và hybrid connectivity có rõ không? |
| Storage | Stateful workload, backup/restore, region/data boundary và performance profile có được thiết kế không? |
| Observability | Logs, metrics, traces, events và audit trail có gắn được với workload, node, namespace, image digest và deployment không? |

Với tổ chức lớn, nhiều platform song song có thể cần thiết, ví dụ platform nội bộ cho dữ liệu nhạy cảm và managed cloud platform cho workload ít ràng buộc hơn. Rủi ro là chi phí vận hành, policy lệch nhau và developer experience bị phân mảnh; cần chuẩn hóa guardrails, naming, identity, registry, logging và incident workflow ở mức có thể.

## Mediated Platform Access

Cho user chạy trực tiếp `docker run` trên host dùng chung là mô hình rủi ro cao vì Docker API gần tương đương quyền root trên host. Với môi trường multi-tenant, nên đưa người dùng qua một lớp platform có policy và audit, ví dụ Kubernetes/OpenShift/GitOps/CI deploy workflow, thay vì cấp Docker socket trực tiếp.

Lớp platform trung gian nên cung cấp:

- identity/RBAC theo user, team, namespace/project;
- quota và limit range để tránh một workload chiếm toàn bộ host/cluster;
- security context mặc định: non-root, drop capability, seccomp/AppArmor/SELinux hoặc Pod Security;
- registry/image policy: trusted registry, scan, signature/provenance;
- audit trail cho ai build, ai deploy, image digest nào đang chạy;
- route/ingress/service exposure có kiểm soát thay vì user tự publish port tùy ý.

Điểm cần nhớ: platform không chỉ "ẩn Docker CLI". Nó phải thay thế quyền tùy ý bằng workflow có guardrail, validation và rollback. Nếu platform vẫn cho người dùng bypass bằng Docker socket, privileged workload hoặc hostPath rộng, boundary bảo mật gần như không còn.
