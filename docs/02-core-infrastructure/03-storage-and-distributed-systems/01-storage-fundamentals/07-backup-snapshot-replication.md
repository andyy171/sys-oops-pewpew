# Backup, Snapshot And Replication

## Overview

Backup, snapshot và replication đều bảo vệ dữ liệu, nhưng bảo vệ trước các loại rủi ro khác nhau. Nhầm lẫn ba khái niệm này là lỗi thiết kế rất phổ biến trong production.

```text
primary data
  -> snapshot: point-in-time local/versioned view
  -> replication: copy/change stream to another node/site
  -> backup: independent recoverable copy with retention
```

## Backup

Backup là bản sao có mục tiêu restore. Một backup tốt cần có retention, verification, quyền truy cập được kiểm soát và quy trình restore đã test.

Các kiểu backup cơ bản:

| Loại | Cơ chế | Ưu điểm | Nhược điểm |
|---|---|---|---|
| Full backup | Sao chép toàn bộ dữ liệu được chọn | Restore đơn giản, ít phụ thuộc chuỗi bản sao | Tốn thời gian, dung lượng và băng thông |
| Incremental backup | Sao chép thay đổi từ lần backup gần nhất | Nhanh, tiết kiệm dung lượng | Restore cần full + toàn bộ incremental đúng thứ tự |
| Differential backup | Sao chép thay đổi từ lần full gần nhất | Restore cần full + differential mới nhất | Differential lớn dần đến lần full tiếp theo |

Backup nên được thiết kế theo RPO/RTO:

- RPO: mất tối đa bao nhiêu dữ liệu tính theo thời gian.
- RTO: khôi phục dịch vụ trong bao lâu.

Retention policy phải cân bằng restore need, compliance, storage cost và ransomware resistance:

- hourly/daily backup cho operational recovery ngắn hạn;
- weekly/monthly/yearly backup cho long-term retention hoặc compliance;
- legal hold hoặc investigation hold cần override retention tự động;
- deletion policy cần approval/audit với backup quan trọng;
- backup catalog và credential không nên nằm duy nhất trong cùng fault domain với production.

Backup phải được bảo vệ như primary data: encryption at rest/in transit, RBAC, access log, immutable/offline/offsite copy và restore test định kỳ.

## Snapshot

Snapshot là view tại một thời điểm của volume/filesystem/object set. Snapshot thường nhanh vì chỉ ghi metadata hoặc dùng copy-on-write/redirect-on-write.

Snapshot hữu ích cho:

- rollback nhanh trước thay đổi
- tạo bản nhất quán để backup
- clone môi trường test
- bảo vệ ngắn hạn trước lỗi thao tác

Giới hạn:

- Snapshot thường nằm cùng hệ thống với dữ liệu chính, nên không bảo vệ tốt trước mất cluster/site.
- Snapshot không tự đảm bảo application consistency nếu ứng dụng chưa flush hoặc chưa quiesce.
- Giữ quá nhiều snapshot có thể làm tăng metadata, fragmentation hoặc write amplification.

## Replication

Replication sao chép dữ liệu sang node/site khác để tăng availability hoặc durability.

Các kiểu quan trọng:

- Synchronous replication: ghi được xác nhận khi replica cũng nhận/commit theo yêu cầu. RPO thấp hơn, latency cao hơn.
- Asynchronous replication: primary xác nhận trước, replica theo sau. Latency thấp hơn nhưng có replication lag.
- Quorum-based replication: quyết định read/write dựa trên số replica đồng thuận.

Replication không phải backup. Xóa nhầm, ghi sai hoặc corruption ở application layer có thể được replicate sang bản sao.

## DR Và Restore Flow

Một thiết kế backup/DR thực tế cần trả lời:

- Dữ liệu nào cần bảo vệ?
- RPO/RTO của từng workload là gì?
- Backup nằm ở đâu, có tách quyền với production không?
- Có immutable/offline/offsite copy không?
- Restore test gần nhất khi nào?
- Ai có quyền xóa backup hoặc thay đổi retention?
- Cloud/file-sync service có phải backup thật không hay chỉ replicate trạng thái hiện tại?

Luồng restore an toàn:

```text
identify restore point
  -> verify backup integrity
  -> restore to isolated/staging location
  -> validate application consistency
  -> plan cutover or data copy back
  -> record evidence and lessons learned
```

## Storage Tiering Cho Backup

Backup thường phù hợp với warm/cold tier hơn hot tier, nhưng không nên chỉ tối ưu chi phí. Nếu restore quá chậm so với RTO thì backup rẻ nhưng không đáp ứng mục tiêu vận hành.

Hot/warm/cold nên được map theo access pattern:

- Hot: dữ liệu active, latency thấp, restore nhanh.
- Warm: dữ liệu ít truy cập hơn, vẫn cần truy xuất định kỳ.
- Cold/archive: giữ lâu dài, tối ưu chi phí/durability hơn latency.

## Cloud Storage And Shared Access

Cloud storage giúp truy cập và chia sẻ dữ liệu nhanh, nhưng không tự động thay thế backup:

- File-sync có thể đồng bộ cả xóa nhầm, mã hóa ransomware hoặc corruption sang mọi client.
- Shared link rộng có thể làm lộ dữ liệu dù object vẫn được mã hóa at rest.
- Provider-managed encryption bảo vệ storage backend, nhưng IAM/share policy sai vẫn làm lộ dữ liệu đã decrypt qua API.
- Internet dependency ảnh hưởng restore time; egress fee và bandwidth có thể làm RTO không đạt.

Guardrails:

- Phân biệt rõ `sync`, `replication`, `snapshot` và `backup` trong runbook.
- Dùng MFA/RBAC/least privilege cho admin backup và cloud storage.
- Log access/share/download với dữ liệu nhạy cảm.
- Test restore từ cloud về môi trường tách biệt, bao gồm bandwidth và credential recovery.
- Với dữ liệu nhạy cảm, cân nhắc client-side encryption hoặc KMS key do tổ chức kiểm soát.

## Validation Checklist

- Có ít nhất một restore test định kỳ.
- Có checksum/hash hoặc verification log sau backup.
- Backup catalog không nằm duy nhất trong cùng fault domain với production.
- Retention policy có bảo vệ trước xóa nhầm hoặc compromise tài khoản admin.
- Runbook restore có owner, thời gian ước lượng và bước rollback.

## Rủi Ro

Các thao tác restore overwrite dữ liệu production, xóa snapshot, thay đổi retention hoặc chạy replication resync đều có thể gây mất dữ liệu. Luôn ưu tiên restore ra môi trường tách biệt trước khi ghi đè dữ liệu hiện có.

## Trang Liên Quan

- [Data Integrity, Checksum And Hashing](./06-data-integrity-checksum-hashing.md)
- [Storage Performance: IOPS, Throughput, Latency](./08-storage-performance-iops-throughput-latency.md)
