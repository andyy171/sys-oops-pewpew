# HA And Failover Patterns

High availability là khả năng hệ thống tiếp tục phục vụ khi một thành phần lỗi. Failover là quá trình chuyển traffic hoặc workload sang thành phần còn khỏe.

## Đo Availability

Availability thường được tính theo service window:

```text
Availability (%) = available time / total service time * 100
```

`Total service time` không luôn là 24x7. Với hệ thống chỉ cam kết hoạt động trong giờ kinh doanh, service window phải được định nghĩa rõ trong SLA/SLO. Đừng lấy uptime của từng component để suy ra uptime của application nếu dependency chain, maintenance window, monitoring gap và user-visible error chưa được tính.

Cách nói "nhiều số 9" chỉ có ý nghĩa khi đi kèm measurement window, service scope, user-visible availability hay infrastructure availability, exception/maintenance policy, phương pháp đo và nguồn số liệu.

## Dependability Terms

HA không đồng nghĩa với toàn bộ dependability:

- **Availability:** service sẵn sàng tại một thời điểm.
- **Reliability:** service chạy liên tục trong một khoảng thời gian.
- **Safety:** khi lỗi xảy ra, hệ thống không tạo hậu quả nghiêm trọng.
- **Maintainability:** team phát hiện, sửa và khôi phục được nhanh.

Một hệ thống có thể availability cao nhưng reliability kém nếu lỗi nhỏ xảy ra lặp lại liên tục. Với production, health check và SLO nên đo user-visible behavior, không chỉ process còn chạy.

## Pattern Phổ Biến

| Pattern | Ý nghĩa | Tradeoff |
| --- | --- | --- |
| Active-passive | Một node chạy chính, node còn lại chờ | Đơn giản hơn nhưng capacity chờ có thể lãng phí |
| Active-active | Nhiều node cùng phục vụ traffic | Tận dụng tài nguyên tốt hơn nhưng consistency phức tạp hơn |
| N+1 | Có thêm ít nhất một node dự phòng | Cần capacity planning |
| Leader-follower | Một leader nhận write, follower replicate | Failover cần election/promotion |
| Quorum | Quyết định dựa trên đa số node | Chống split-brain tốt hơn nhưng cần số node phù hợp |

## Building Blocks

- Redundancy ở compute, network, storage, database hoặc region.
- Load balancing để phân phối traffic và rút traffic khỏi backend unhealthy.
- Autoscaling dựa trên metric phản ánh bottleneck thật như latency, request rate, queue depth hoặc error rate.
- Health check kiểm tra khả năng phục vụ thật, không chỉ process còn chạy.
- Fault tolerance để hệ thống degrade có kiểm soát thay vì fail toàn bộ.

## Failure Modes

- Split-brain.
- False positive health check.
- Failover quá nhanh gây flapping.
- Failover thành công nhưng dependency phía sau vẫn lỗi.
- Failback không được thiết kế.

## Checklist

- Thành phần nào là single point of failure.
- Health check kiểm tra process hay kiểm tra khả năng phục vụ thật.
- Load balancer có rút traffic khỏi backend lỗi đủ nhanh không.
- Autoscaling trigger có phản ánh bottleneck thật không.
- Failover là manual, semi-automatic hay automatic.
- Có cơ chế tránh split-brain không.
- Sau failover, dữ liệu có mất hoặc rollback không.
## Related Pages

- [Distributed Fault Tolerance And Recovery](./10-distributed-fault-tolerance-and-recovery.md)
