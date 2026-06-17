# Transaction, ACID And Isolation Levels

## Overview

Transaction gom nhiều thao tác đọc/ghi thành một đơn vị logic. Mục tiêu là giữ dữ liệu đúng ngay cả khi có lỗi giữa chừng, nhiều client chạy song song hoặc hệ thống crash.

## ACID

| Thuộc tính | Ý nghĩa |
| --- | --- |
| Atomicity | transaction thành công toàn bộ hoặc rollback toàn bộ |
| Consistency | dữ liệu sau transaction vẫn thỏa constraint và invariant |
| Isolation | transaction song song không nhìn thấy trạng thái trung gian sai |
| Durability | dữ liệu đã commit không mất sau crash trong phạm vi đảm bảo của engine |

ACID không tự động đảm bảo mọi logic nghiệp vụ. Application vẫn phải dùng constraint, transaction boundary và retry đúng.

## Transaction Boundary

Transaction boundary nên đủ lớn để bảo vệ invariant, nhưng đủ nhỏ để tránh lock lâu.

Một transaction thường đi qua các trạng thái:

- **BEGIN**: mở phạm vi làm việc logic.
- **COMMIT**: xác nhận toàn bộ thay đổi và yêu cầu engine làm bền dữ liệu theo cơ chế durability của nó.
- **ROLLBACK**: hủy toàn bộ thay đổi chưa commit.
- **Unexpected end**: nếu session, process hoặc host lỗi trước commit, engine phải recovery như rollback phần chưa commit.

Transaction không chỉ dùng cho ghi dữ liệu. Read-only transaction cũng hữu ích khi cần một snapshot nhất quán, ví dụ chạy report trong lúc hệ thống vẫn có nhiều transaction khác đang cập nhật dữ liệu.

Ví dụ invariant:

- Số dư tài khoản không âm.
- Một order chỉ được thanh toán một lần.
- Inventory không bán vượt số lượng.
- Username/email là duy nhất.

## Isolation Levels

| Level | Bảo vệ | Rủi ro còn lại |
| --- | --- | --- |
| Read Uncommitted | thấp nhất | dirty read, non-repeatable read, phantom |
| Read Committed | không đọc dữ liệu chưa commit | non-repeatable read, phantom |
| Repeatable Read | một row đã đọc giữ ổn định trong transaction | phantom tùy engine |
| Snapshot | đọc theo snapshot tại một mốc thời gian logic | conflict/retry tùy engine, không đồng nghĩa với serializable trong mọi hệ |
| Serializable | kết quả như chạy tuần tự | throughput thấp hơn, dễ conflict/retry |

Tên isolation giống nhau nhưng behavior có thể khác giữa engine. Khi cần chính xác, phải kiểm tra tài liệu của engine cụ thể.

## Common Anomalies

- **Dirty read**: đọc dữ liệu chưa commit.
- **Non-repeatable read**: đọc cùng row hai lần ra giá trị khác vì transaction khác đã commit.
- **Phantom read**: chạy cùng predicate hai lần nhưng tập row thay đổi.
- **Lost update**: hai transaction cùng đọc rồi ghi đè update của nhau.
- **Write skew**: mỗi transaction thấy dữ liệu hợp lệ, nhưng commit cùng nhau phá invariant.

Các anomaly này thường đến từ việc database cho phép một transaction nhìn thấy một phần thay đổi của transaction khác, hoặc cho phép hai transaction cùng dựa trên cùng một trạng thái cũ rồi ghi kết quả mới. Khi business invariant quan trọng, đừng chỉ dựa vào isolation mặc định; cần kết hợp constraint, lock phù hợp, optimistic retry hoặc serializable tùy workload.

## Consistency Trong ACID

Consistency trong ACID chủ yếu nói về việc transaction đưa database từ một trạng thái hợp lệ sang một trạng thái hợp lệ khác. "Hợp lệ" không tự sinh ra; nó đến từ schema, constraint, foreign key, unique key, check constraint và logic application.

Cần tách hai lớp consistency:

- **Consistency của dữ liệu**: dữ liệu sau commit vẫn thỏa invariant, ví dụ tổng số like khớp với bảng like chi tiết hoặc order không tham chiếu customer không tồn tại.
- **Consistency của đọc**: sau khi một transaction commit, transaction mới có nhìn thấy thay đổi ngay không. Trong hệ phân tán hoặc NoSQL, eventual consistency có thể làm read sau write chưa thấy dữ liệu mới trong một khoảng thời gian.

Relational database thường mạnh ở consistency của dữ liệu nhờ constraint và transaction local. Tuy nhiên, khi có replica, cache, async replication hoặc read từ node phụ, consistency của đọc vẫn là vấn đề vận hành cần thiết kế rõ.

## Durability Và WAL

Durability không chỉ là "đã trả về commit là xong". Engine cần đảm bảo thay đổi đã commit tồn tại sau crash trong phạm vi cấu hình durability. Cơ chế phổ biến là ghi log trước rồi mới flush data page sau:

```text
client commit
-> ghi bản ghi thay đổi vào WAL / redo log / journal
-> fsync hoặc đồng bộ theo cấu hình durability
-> trả commit thành công
-> data page có thể được flush xuống disk sau
```

WAL giúp commit không phải ghi ngay mọi data page và index page xuống disk, nhưng vẫn có đường recovery sau crash. Nếu log đã bền, engine có thể replay thay đổi đã commit và rollback phần chưa commit.

Điểm vận hành cần nhớ:

- OS page cache có thể nhận write trước khi dữ liệu thật sự xuống non-volatile storage.
- `fsync` hoặc cơ chế tương đương làm tăng độ bền nhưng có chi phí latency.
- Tắt hoặc nới lỏng durability setting có thể tăng throughput, nhưng đổi lại có nguy cơ mất transaction đã được application tưởng là commit.
- Replication không thay thế durability local; nếu primary mất dữ liệu trước khi replicate bền, hệ thống vẫn có thể mất commit.

## Operational Notes

- Transaction dài làm tăng lock wait, MVCC bloat hoặc replication lag.
- Retry logic cần idempotent khi gặp deadlock, serialization failure hoặc failover.
- Không giữ transaction mở khi chờ user input, network call hoặc job dài.
- Dùng constraint ở database cho invariant quan trọng, không chỉ kiểm tra ở application.
- Monitor lock wait, deadlock, rollback rate và transaction age.

Với bài toán double booking, ưu tiên để database enforce invariant:

```sql
CREATE UNIQUE INDEX uniq_booking_slot
ON bookings(room_id, booking_date, slot_id);
```

Nếu cần serialize thao tác trên resource, dùng lock có phạm vi ngắn và retry khi conflict:

```sql
BEGIN;
SELECT *
FROM rooms
WHERE id = 1
FOR UPDATE;
-- validate slot and insert booking
COMMIT;
```

Serializable có thể bảo vệ logic mạnh hơn nhưng application phải sẵn sàng retry khi database abort transaction do conflict.

## Related Pages

- [Locking, MVCC And Concurrency Control](./06-locking-mvcc-concurrency-control.md)
- [Database Performance](./09-database-performance-latency-throughput-iops.md)
