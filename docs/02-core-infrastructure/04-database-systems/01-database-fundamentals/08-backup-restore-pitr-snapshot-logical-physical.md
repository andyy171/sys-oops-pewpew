# Backup, Restore, PITR, Snapshot, Logical, Physical

## Overview

Backup chỉ có giá trị khi restore được. Trong production, chiến lược backup phải gắn với RPO, RTO, retention, encryption, access control và restore drill định kỳ.

## Backup Types

| Loại | Ý nghĩa | Khi dùng |
| --- | --- | --- |
| Logical backup | export schema/data ở mức logical như SQL dump | migration nhỏ, object-level restore, portability |
| Physical backup | copy data files theo format engine | database lớn, restore nhanh hơn logical trong nhiều trường hợp |
| Snapshot | snapshot volume/storage | nhanh, nhưng cần đảm bảo consistency |
| Incremental/differential | chỉ lưu phần thay đổi | giảm dung lượng backup |
| PITR | restore tới thời điểm cụ thể bằng base backup + logs | giảm data loss khi cần quay về trước lỗi logic |

## RPO And RTO

- **RPO**: tối đa mất bao nhiêu dữ liệu.
- **RTO**: tối đa mất bao lâu để khôi phục dịch vụ.

Backup strategy không thể đánh giá nếu thiếu RPO/RTO. Ví dụ backup mỗi ngày không phù hợp nếu RPO là 5 phút.

## Consistency

Backup phải nhất quán:

- Crash-consistent: giống trạng thái sau crash, engine tự recovery.
- Application-consistent: application/database flush trạng thái cần thiết trước snapshot.
- Transaction-consistent: restore không có transaction commit nửa vời.

Snapshot storage nhanh nhưng không tự động đảm bảo consistency cho mọi database nếu không phối hợp với engine.

## Restore Runbook

Runbook restore nên có:

1. Xác định loại sự cố: data corruption, accidental delete, host loss, region loss.
2. Chọn backup point theo RPO và thời điểm lỗi.
3. Restore vào môi trường cách ly trước nếu nghi ngờ lỗi logic.
4. Verify schema, row count, checksum hoặc application-level validation.
5. Quyết định cutover.
6. Ghi lại thời gian restore thực tế để kiểm chứng RTO.
7. Sau restore, kiểm tra backup chain tiếp tục hoạt động.

## Security

- Encrypt backup at rest và in transit.
- Giới hạn quyền đọc/xóa backup.
- Tách quyền production database và quyền backup storage nếu có thể.
- Bảo vệ backup khỏi ransomware bằng immutability, versioning hoặc offline copy.
- Không lưu secrets/token trong dump mà không kiểm soát access.

## Common Failure Modes

- Có backup nhưng chưa từng restore thử.
- Backup cùng failure domain với database.
- Backup bị corruption nhưng không có checksum/verification.
- Retention quá ngắn, không phát hiện lỗi logic kịp.
- PITR thiếu log segment nên chain bị đứt.

## Related Pages

- [Replication, Sharding And Partitioning](./07-replication-sharding-partitioning.md)
- [Database Operations Patterns](../08-database-operations-patterns/overview.md)
