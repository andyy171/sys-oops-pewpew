# Single-Tenant Private Cloud For Data Workloads

Single-tenant private cloud là pattern dùng hạ tầng riêng cho một tổ chức hoặc một nhóm workload quan trọng, thay vì chạy trên môi trường multi-tenant chia sẻ. Pattern này đáng cân nhắc khi workload cần predictable performance, data locality, control sâu hoặc cost model ổn định hơn elastic public cloud.

## Khi Nào Phù Hợp

- Ingest dữ liệu liên tục với throughput ổn định.
- Write-heavy workload như logging pipeline, telemetry, Kafka, analytics database hoặc batch processing lớn.
- Latency và I/O variance gây ảnh hưởng trực tiếp đến SLA.
- Compliance yêu cầu data locality hoặc trust boundary rõ.
- Workload ít idle, khó hưởng lợi từ scale-down theo giờ.

## Vấn Đề Của Multi-Tenant

Multi-tenant không chỉ là chia sẻ tài nguyên. Nó tạo thêm biến số:

- noisy neighbor trên CPU, memory, disk I/O hoặc network;
- resource contention khó quan sát từ app layer;
- billing có thể biến động theo egress, I/O, request hoặc managed-service tier;
- trust boundary phụ thuộc provider/platform;
- debug khó hơn vì người vận hành không nhìn thấy toàn bộ stack.

Với data workload, mất tính dự đoán đôi khi nguy hiểm hơn mất performance tuyệt đối. Một pipeline ingest chậm nhưng ổn định còn dễ thiết kế backpressure hơn một pipeline lúc nhanh lúc nghẽn không rõ nguyên nhân.

## Kiến Trúc Tham Chiếu

```text
dedicated capacity
  -> standardized compute/storage/network baseline
  -> queue / ingest / processing / persistence
  -> observability for throughput, lag, latency, I/O pressure
  -> capacity plan and expansion model
```

Các quyết định quan trọng:

- capacity cố định hay có buffer mở rộng;
- storage backend có đủ throughput và durability không;
- network path có tách ingest, replication và management không;
- workload có cần active/passive site hoặc multi-site DR không;
- team có đủ năng lực vận hành platform không.

## Tradeoff

| Khía cạnh | Single-tenant private cloud | Multi-tenant public cloud |
|---|---|---|
| Predictability | cao hơn nếu capacity được thiết kế đúng | phụ thuộc provider và neighbor |
| Elasticity | thấp hơn, cần capacity planning | cao hơn |
| Control | sâu hơn ở hardware/network/storage | bị giới hạn bởi abstraction |
| Day-2 operations | cần team vận hành mạnh | giảm một phần toil |
| Cost model | dễ mô hình hóa với tải ổn định | tốt cho tải biến động, có thể khó đoán khi I/O/egress lớn |

## Failure Modes

- Tự vận hành private cloud nhưng không có backup, monitoring, upgrade và incident process tương xứng.
- Mua dedicated capacity quá sớm khi workload còn nhỏ hoặc biến động mạnh.
- Tối ưu performance nhưng bỏ qua availability và restore.
- Dùng single-tenant để né noisy neighbor nhưng lại tạo single point of failure nội bộ.

## Trang Liên Quan

- [Workload Patterns](../01-principles/04-workload-patterns.md)
- [Control Vs Abstraction](../02-tradeoffs/04-control-vs-abstraction.md)
- [PoC Evaluation Framework](../02-tradeoffs/05-poc-evaluation-framework.md)
- [IT Infrastructure Security And Resilience](../04-reliability-and-dr/08-it-infrastructure-security-and-resilience.md)
