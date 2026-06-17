# Locking, MVCC And Concurrency Control

## Overview

Concurrency control giúp nhiều transaction chạy song song mà dữ liệu vẫn đúng. Hai cơ chế thường gặp là locking và MVCC. Engine thực tế có thể kết hợp cả hai.

## Locking

Lock giới hạn ai được đọc/ghi một object tại một thời điểm.

Các phạm vi lock thường gặp:

- Row lock.
- Table lock.
- Metadata/schema lock.
- Page/key-range/predicate lock tùy engine.

Lock giúp bảo vệ correctness nhưng có thể gây lock wait, deadlock và throughput thấp nếu transaction giữ lock quá lâu.

## MVCC

MVCC giữ nhiều version của row để reader không nhất thiết block writer. Transaction đọc snapshot phù hợp với isolation level.

Điểm mạnh:

- Read/write concurrency tốt hơn trong nhiều workload.
- Reader ít bị block bởi writer.

Tradeoff:

- Cần cleanup old version.
- Transaction quá dài có thể giữ old version lâu, gây bloat hoặc storage pressure.
- Vacuum/compaction/garbage collection trở thành tác vụ vận hành quan trọng.

## Deadlock

Deadlock xảy ra khi transaction A giữ lock mà B cần, trong khi B giữ lock mà A cần. Database thường chọn một transaction làm nạn nhân để rollback.

Giảm deadlock bằng cách:

- Update object theo thứ tự nhất quán.
- Giữ transaction ngắn.
- Dùng index để tránh lock quá rộng.
- Retry transaction an toàn ở application.
- Tránh user interaction hoặc external API call trong transaction.

## Operational Signals

Theo dõi:

- Lock wait time.
- Deadlock count.
- Long-running transaction.
- Idle transaction.
- Row version/bloat/compaction pressure.
- Replication lag do transaction lớn.

## Troubleshooting Flow

1. Xác định session/query nào đang chờ lock.
2. Tìm blocker.
3. Kiểm tra transaction age và statement đang chạy.
4. Đánh giá có thể kill session không, dựa vào rủi ro rollback.
5. Sau incident, sửa query/index/transaction boundary để tránh lặp lại.

## Related Pages

- [Transaction, ACID And Isolation Levels](./03-transaction-acid-isolation-levels.md)
- [Query Planner And Execution Plan](./05-query-planner-and-execution-plan.md)
