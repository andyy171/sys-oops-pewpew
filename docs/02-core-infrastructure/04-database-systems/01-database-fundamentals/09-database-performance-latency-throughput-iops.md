# Database Performance: Latency, Throughput, IOPS

## Overview

Database performance không chỉ là query nhanh. Nó là kết quả của query design, index, transaction, lock, memory, storage I/O, network, connection pool và workload shape.

## Key Metrics

| Metric | Ý nghĩa |
| --- | --- |
| Latency | thời gian hoàn thành một query/transaction |
| Throughput | số query/transaction xử lý mỗi giây |
| IOPS | số operation đọc/ghi storage mỗi giây |
| CPU utilization | mức dùng CPU cho parse, plan, execute, compression, encryption |
| Memory/cache hit | khả năng phục vụ read từ memory thay vì disk |
| Lock wait | thời gian chờ lock |
| Connection count | số connection đang mở/active/idle |
| Replication lag | độ trễ replica so với primary |

P95/P99 latency thường quan trọng hơn average latency trong production.

## Bottleneck Patterns

### Query/Index

Triệu chứng:

- Một vài query chiếm phần lớn thời gian.
- Full scan hoặc sort lớn.
- CPU cao khi workload đọc tăng.

Hướng xử lý:

- Đọc execution plan.
- Thêm hoặc sửa index có kiểm chứng.
- Rewrite query.
- Giảm dữ liệu trả về.

### Lock/Transaction

Triệu chứng:

- Query đơn giản cũng chậm.
- Lock wait/deadlock tăng.
- Transaction age cao.

Hướng xử lý:

- Tìm blocker.
- Rút ngắn transaction.
- Update theo thứ tự nhất quán.
- Thêm index để giảm phạm vi lock.

### Storage I/O

Triệu chứng:

- Disk latency cao.
- IOPS/throughput chạm trần.
- Checkpoint/flush/compaction gây spike.

Hướng xử lý:

- Tối ưu working set và cache.
- Tách workload nặng.
- Kiểm tra storage tier, queue depth, filesystem, snapshot overhead.

### Connection Pool

Triệu chứng:

- Quá nhiều connection idle.
- Database CPU/context switch cao.
- Application timeout dù database chưa hết tài nguyên chính.

Hướng xử lý:

- Đặt pool size theo capacity thật.
- Timeout rõ ràng.
- Tránh mở connection theo request không kiểm soát.

Pool không phải càng lớn càng tốt. Pool quá nhỏ làm request chờ connection; pool quá lớn làm database tắc nghẽn bởi context switch, memory và lock contention. Transaction giữ connection quá lâu cũng có thể làm cạn pool dù query đơn lẻ không chậm.

Checklist:

- Đo active vs idle connection, không chỉ total connection.
- Cấu hình connect timeout, idle timeout và max lifetime.
- Tìm request/transaction giữ connection lâu bằng database view và application trace.
- Đặt pool theo service instance; tổng pool của toàn bộ replicas mới là áp lực thật lên database.

## Tuning Principles

- Measure trước, thay đổi sau.
- Tối ưu query chạy thường xuyên trước query hiếm.
- Test bằng dữ liệu và concurrency gần production.
- Mỗi thay đổi cần rollback plan.
- Theo dõi tác động phụ lên write latency, storage và replication.

## Related Pages

- [Query Planner And Execution Plan](./05-query-planner-and-execution-plan.md)
- [Locking, MVCC And Concurrency Control](./06-locking-mvcc-concurrency-control.md)
