# Control Vs Abstraction

Control là khả năng can thiệp sâu vào stack: hardware, OS, network, storage, runtime và security. Abstraction là việc dùng platform/provider che bớt chi tiết để tăng tốc triển khai.

## Khi Cần Nhiều Abstraction

- Team nhỏ, cần release nhanh.
- Workload phổ thông, không cần tuning sâu.
- Chấp nhận giới hạn provider/platform.
- Ưu tiên managed service để giảm toil.

## Khi Cần Nhiều Control

- Workload latency-sensitive hoặc I/O-heavy.
- Cần custom kernel, driver, network, storage policy.
- Có yêu cầu compliance/data locality nghiêm ngặt.
- Cần predictable performance hoặc single-tenant isolation.

## Full Control Infrastructure

Full control infrastructure nghĩa là team vận hành có quyền can thiệp đủ sâu vào hardware, OS, network, storage, runtime và security policy. Nó không đồng nghĩa với "ai cũng có root"; nó nghĩa là platform có thể được thiết kế, tự động hóa, harden và audit ở đúng tầng cần kiểm soát.

Full control đáng giá khi:

- abstraction của provider/platform che mất failure signal quan trọng;
- workload cần tuning ở kernel, driver, network hoặc storage path;
- security control phải được định nghĩa bởi tổ chức thay vì chỉ nhận default của provider;
- cost/performance cần được mô hình hóa theo capacity thật.

Rủi ro là day-2 operations tăng mạnh: patching, backup, monitoring, incident response, access control và upgrade đều quay lại thành trách nhiệm nội bộ.

## Tradeoff

| Khía cạnh | Abstraction cao | Control cao |
|---|---|---|
| Tốc độ ban đầu | Nhanh | Chậm hơn |
| Vận hành day-2 | Ít việc hơn | Cần năng lực sâu hơn |
| Tuning | Bị giới hạn | Linh hoạt |
| Cost predictability | Có thể khó đoán | Dễ mô hình hóa hơn nếu capacity ổn định |
| Lock-in | Cao hơn | Thấp hơn nếu thiết kế tốt |

## Nguyên Tắc

- Dùng abstraction cho phần không tạo lợi thế cạnh tranh.
- Giữ control ở phần ảnh hưởng trực tiếp đến performance, security hoặc cost model.
- Trước khi tự vận hành, phải tính đủ backup, patching, monitoring, incident và upgrade.

## Trang Liên Quan

- [Infrastructure Consistency](../01-principles/05-infrastructure-consistency-and-platform-thinking.md)
- [Platform Engineering And Infrastructure As Product](../01-principles/06-platform-engineering-and-infrastructure-as-product.md)
- [Single-Tenant Private Cloud For Data Workloads](../03-patterns/05-single-tenant-private-cloud-for-data-workloads.md)
