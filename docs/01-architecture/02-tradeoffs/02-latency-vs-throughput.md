# Latency Vs Throughput

Latency là thời gian hoàn thành một request hoặc một đơn vị công việc. Throughput là số lượng công việc hệ thống xử lý trong một đơn vị thời gian.

## Tradeoff Cốt Lõi

- Tối ưu latency thường cần xử lý nhanh từng request, giảm queue, giảm hop và ưu tiên path ngắn.
- Tối ưu throughput thường cần batching, parallelism, queueing và tận dụng tài nguyên theo lô.

Hai mục tiêu này có thể xung đột. Batch lớn giúp throughput cao hơn nhưng làm request chờ lâu hơn. Retry mạnh giúp tăng khả năng hoàn thành nhưng có thể tăng tail latency.

## Ví Dụ

| Thiết kế | Latency | Throughput |
|---|---|---|
| Request đồng bộ trực tiếp DB | Thấp khi tải nhỏ | Dễ nghẽn khi tải lớn |
| Queue + worker batch | Cao hơn do chờ queue | Tốt hơn cho tải lớn |
| Cache gần user | Thấp | Giảm load backend |
| Compression mạnh | Có thể tăng CPU latency | Giảm network bandwidth |

## Tail Latency

Trong production, p95/p99 thường quan trọng hơn average latency. Một hệ thống có average tốt nhưng p99 tệ vẫn gây trải nghiệm kém và timeout dây chuyền.

Nguyên nhân tail latency:

- Queue dài.
- Lock/contention.
- Cold cache.
- GC pause.
- Slow dependency.
- Retry storm.

## Decision Checklist

- User cần phản hồi ngay hay có thể xử lý bất đồng bộ.
- Có thể batch mà không phá SLA không.
- Bottleneck hiện tại là CPU, disk, network hay dependency.
- Nên đo p50, p95, p99, throughput và error rate cùng lúc.
- Khi quá tải, nên backpressure, shed load hay degrade feature.
