# RTO/RPO Design

RTO và RPO là hai chỉ số cốt lõi của disaster recovery.

- **RTO (Recovery Time Objective):** thời gian tối đa chấp nhận để khôi phục service.
- **RPO (Recovery Point Objective):** lượng dữ liệu tối đa chấp nhận mất, tính theo thời gian.

## Ví Dụ

| Hệ thống | RTO | RPO | Ý nghĩa |
| --- | ---: | ---: | --- |
| Static website | 1 giờ | 24 giờ | Có thể rebuild từ source |
| Internal tool | 4 giờ | 1 giờ | Chấp nhận downtime có kiểm soát |
| Payment API | 5 phút | Gần 0 | Cần HA, replication và failover mạnh |

## RTO/RPO Ảnh Hưởng Thiết Kế

- RTO ngắn cần automation, warm standby hoặc active-active.
- RPO thấp cần replication gần real-time, backup thường xuyên hoặc transaction log shipping.
- RTO/RPO càng thấp, chi phí và độ phức tạp càng cao.

## Backup Không Đủ

Backup chỉ có ý nghĩa khi restore được. DR design cần:

- Backup schedule.
- Retention policy.
- Restore procedure.
- Restore test định kỳ.
- Owner và escalation path.

Replication, multi-zone và snapshot không thay thế restore test. Nếu chưa từng restore thành công trong điều kiện gần production, RTO/RPO đang ghi chỉ là giả định.

## DR Plan

Một disaster recovery plan production nên ghi rõ:

- service tier và recovery priority;
- stakeholder, owner, approver và communication channel;
- pre-check trước khi failover;
- các bước failover/failback;
- validation sau khi khôi phục;
- rollback hoặc fallback nếu failover không đạt;
- evidence cần lưu lại cho post-incident review;
- lịch drill định kỳ.

DR drill giúp phát hiện gap trong quyền truy cập, DNS, dependency, backup integrity, automation, documentation và khả năng phối hợp của team. Không nên chờ sự cố thật mới kiểm chứng runbook.

## Checklist

- Business chấp nhận downtime bao lâu.
- Business chấp nhận mất dữ liệu bao nhiêu.
- Dependency nào có RTO/RPO thấp nhất.
- Restore đã từng được diễn tập chưa.
- Có runbook failover và failback không.
- Có ai đủ quyền thực hiện trong tình huống khẩn cấp không.
