# AKS Multi-Tenancy, Scheduling And Identity

## Overview

Multi-tenancy trong Kubernetes là bài toán cho nhiều team hoặc nhiều workload cùng dùng chung nền tảng nhưng không giẫm lên tài nguyên, quyền hạn và ranh giới vận hành của nhau. Với AKS, tài liệu Microsoft nhấn mạnh rằng nên bắt đầu từ logical isolation trước khi tách thành nhiều cluster vật lý.

Nói ngắn gọn: tách cluster là cách mạnh nhưng đắt và tăng gánh vận hành; tách namespace + RBAC + quota + scheduling policy là cách nên thử trước cho phần lớn team nội bộ đáng tin cậy.

## Khi Nào Tách Cluster

Nên cân nhắc cluster riêng khi workload có một trong các đặc điểm sau:

- yêu cầu compliance, billing hoặc ownership rất khác nhau;
- team cần quyền cluster-admin độc lập;
- workload không cùng vòng đời upgrade, network hoặc policy;
- blast radius không được phép lan sang workload khác;
- workload có profile tài nguyên đặc biệt, ví dụ GPU, high I/O, dedicated node pool hoặc latency-sensitive.

Không nên tách cluster chỉ vì muốn "dễ phân quyền hơn" nếu bài toán có thể giải bằng namespace, RBAC và policy. Cluster càng nhiều thì upgrade, observability, capacity planning, backup và platform governance càng khó nhất quán.

## Logical Isolation Bằng Namespace

Namespace là ranh giới tổ chức tài nguyên, không phải security boundary tuyệt đối. Dùng namespace để chia app/team/environment, sau đó khóa bằng các lớp bổ sung:

- `Role`/`RoleBinding` để giới hạn hành động trong namespace.
- `ResourceQuota` để giới hạn tổng CPU, memory, storage và số object.
- `LimitRange` để ép mỗi container có request/limit hợp lý.
- `NetworkPolicy` để giảm mặc định "pod nào cũng nói chuyện với pod nào".
- Pod security label hoặc policy engine để chặn pod quá đặc quyền.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-quota
  namespace: team-a
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 64Gi
    limits.cpu: "40"
    limits.memory: 128Gi
    pods: "80"
```

## Scheduler Controls

Scheduler không chỉ là thành phần "đặt pod lên node". Trong cluster nhiều workload, scheduler là công cụ kiểm soát phân bố rủi ro và tài nguyên.

Các lớp nên hiểu rõ:

- `requests` quyết định scheduler có thể đặt pod ở đâu.
- `limits` giới hạn mức container được dùng sau khi đã chạy.
- `PodDisruptionBudget` giữ số replica tối thiểu trong voluntary disruption như upgrade node hoặc rollout.
- `nodeSelector` là cách chọn node đơn giản theo label.
- node affinity/anti-affinity cho phép biểu đạt rule mềm hoặc cứng hơn.
- pod affinity/anti-affinity giúp gom hoặc tách pod theo topology.
- taint/toleration dùng để giữ node pool riêng cho workload đặc biệt.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: api
```

## Taint, Toleration Và Dedicated Node Pool

Taint đặt lên node để nói "pod bình thường đừng vào đây". Toleration đặt lên pod để nói "pod này được phép chịu taint đó". Cặp này rất hợp cho ingress controller, GPU workload, batch nặng, workload có license ràng buộc hoặc workload cần node pool hardened riêng.

Tuy vậy, toleration chỉ cho phép pod vào node có taint; nó không bắt buộc pod phải vào node đó. Nếu muốn vừa cho phép vừa ưu tiên/bắt buộc placement, kết hợp toleration với node affinity.

## Identity And RBAC

Luồng truy cập tốt nên đi theo hướng:

1. Người dùng hoặc workload xác thực qua identity provider.
2. Kubernetes API server xác minh token.
3. RBAC quyết định người đó được làm gì, trên resource nào, trong scope nào.
4. Policy/admission kiểm tra object có đạt chuẩn an toàn không.

Không cấp `cluster-admin` cho user hằng ngày. Tách quyền theo vai trò:

- platform team: quản lý cluster-wide resource, node pool, admission, observability;
- app team: quản lý workload trong namespace của mình;
- read-only/support: xem log, describe object, đọc event, không sửa object;
- CI/CD identity: chỉ được apply vào namespace/release được giao.

## Workload Identity

Không nên nhúng credential cloud service trực tiếp trong image, ConfigMap hoặc biến môi trường dài hạn. Với AKS, mental model tốt là để pod lấy token ngắn hạn thông qua workload identity/managed identity rồi truy cập dịch vụ như Key Vault, storage hoặc registry theo quyền tối thiểu.

Điểm cần nhớ:

- identity của workload phải độc lập với identity của node;
- quyền cloud IAM nên hẹp theo resource và action;
- rotate secret vẫn cần kế hoạch nếu app còn dùng secret truyền thống;
- RBAC Kubernetes không thay thế cloud IAM, và cloud IAM không thay thế RBAC Kubernetes.

## Checklist

- Mỗi team/app có namespace rõ ràng.
- Namespace có quota, limit default và owner.
- Không có user thường dùng quyền cluster-admin.
- PDB tồn tại cho workload cần availability.
- Node pool đặc biệt có taint và label.
- Pod placement rule được viết bằng affinity/anti-affinity khi cần.
- Credential cloud được thay bằng workload identity hoặc vault pattern.
