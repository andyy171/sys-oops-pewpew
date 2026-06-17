# Workload Patterns

Workload pattern mô tả cách hệ thống tiêu thụ CPU, memory, disk, network và dependency theo thời gian. Hiểu workload là bước trước khi chọn kiến trúc.

## Các Pattern Phổ Biến

| Pattern | Đặc điểm | Gợi ý kiến trúc |
|---|---|---|
| Steady-state | Tải ổn định, dễ dự đoán | Reserved/fixed capacity, private cloud, capacity planning |
| Spiky | Tải tăng đột biến theo sự kiện | Autoscaling, queue, CDN, rate limit |
| Batch | Chạy theo lô, có cửa sổ thời gian | Job scheduler, retry, checkpoint |
| Real-time | Cần latency thấp và ổn định | Low-latency path, backpressure, dedicated capacity |
| Write-heavy | Ghi nhiều hơn đọc | Partitioning, log-structured storage, queue buffer |
| Read-heavy | Đọc nhiều hơn ghi | Cache, read replica, CDN |

## Câu Hỏi Thiết Kế

- Peak load khác average load bao nhiêu lần.
- Bottleneck chính nằm ở CPU, memory, disk I/O, network hay dependency.
- Tải có thể queue được không hay phải xử lý đồng bộ.
- Khi quá tải, hệ thống nên reject, degrade hay delay.
- Workload cần predictable performance hay chỉ cần elastic capacity.

## Workload Placement

Workload placement là quyết định workload nên chạy trên shared cloud, managed service, private cloud, bare metal hay dedicated capacity. Quyết định này không nên dựa vào thói quen platform, mà dựa vào pattern tiêu thụ tài nguyên.

| Workload cần tối ưu | Placement thường phù hợp |
|---|---|
| spiky traffic, nhiều idle time | elastic cloud, autoscaling, queue |
| steady-state, high-volume data | reserved/dedicated capacity, private cloud |
| latency-sensitive hoặc I/O-heavy | low-latency path, dedicated node, bare metal khi cần |
| regulated/sensitive data | private cloud, strict boundary, confidential computing nếu cần |
| batch có thể delay | scheduler, spot/preemptible capacity nếu risk chấp nhận được |

## Liên Quan

- [Latency Vs Throughput](../02-tradeoffs/02-latency-vs-throughput.md)
- [Scalability Vs Maintainability](../02-tradeoffs/03-scalability-vs-maintainability.md)
- [Single-Tenant Private Cloud For Data Workloads](../03-patterns/05-single-tenant-private-cloud-for-data-workloads.md)
