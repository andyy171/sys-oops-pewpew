# Data Integrity, Checksum And Hashing

## Overview

Data integrity là khả năng phát hiện hoặc ngăn dữ liệu bị sai lệch ngoài ý muốn. Trong storage, integrity không chỉ là "dữ liệu còn tồn tại", mà còn là dữ liệu đọc ra có đúng với dữ liệu đã ghi hay không.

Các cơ chế thường gặp:

- checksum để phát hiện lỗi ngẫu nhiên
- cryptographic hash để chống sửa đổi có chủ ý tốt hơn
- redundancy/replication/erasure coding để có bản khác phục hồi
- scrub/deep scrub để kiểm tra định kỳ
- WAL/journal để giữ consistency khi crash

## Hashing

Hashing biến dữ liệu đầu vào thành giá trị đại diện có kích thước cố định hoặc tương đối cố định. Tùy mục tiêu, hashing có thể dùng cho hash table, deduplication, checksum hoặc security.

Điểm cần phân biệt:

- Hash code là kết quả của hàm hash, không phải bản thân thuật toán.
- Hash cho data structure ưu tiên phân phối đều và tốc độ.
- Cryptographic hash ưu tiên chống đảo ngược, chống collision và avalanche effect.

## Checksum

Checksum là giá trị tính từ dữ liệu để phát hiện lỗi ngẫu nhiên như bit flip, lỗi truyền mạng hoặc corruption trên disk.

Ví dụ thường gặp: CRC32, Adler-32, Internet checksum.

Đặc điểm:

- Nhanh và phù hợp với kiểm tra integrity cơ bản.
- Không chống giả mạo có chủ ý vì attacker có thể sửa dữ liệu rồi tính checksum mới.
- Hữu ích trong filesystem, network protocol, object storage, backup verification.

## Cryptographic Hash

Cryptographic hash như SHA-256 được thiết kế để khó tìm input từ hash, khó tìm hai input khác nhau có cùng hash và thay đổi nhỏ ở input tạo ra output khác mạnh.

Phù hợp cho:

- kiểm tra artifact/package không bị sửa
- content-addressed storage
- chữ ký số khi kết hợp với private key
- xác minh backup/export ở mức file/object

Không nên coi hash là encryption. Hash một chiều không giúp khôi phục dữ liệu gốc.

## Integrity vs Durability vs Availability

| Khái niệm | Câu hỏi trả lời | Ví dụ |
|---|---|---|
| Integrity | Dữ liệu có đúng không? | checksum, scrub, hash verification |
| Durability | Dữ liệu có tồn tại sau lỗi không? | replication, erasure coding, backup |
| Availability | Dữ liệu có truy cập được lúc cần không? | failover, quorum, multipath |
| Consistency | Các node/client có thấy trạng thái hợp lệ không? | transaction, quorum, locking |

Một hệ thống có thể durable nhưng mất integrity nếu dữ liệu bị corruption và corruption đó được replicate. Vì vậy cần checksum/scrub và backup versioning.

## Scrub Và Verification

Scrub là quá trình đọc/kiểm tra dữ liệu hoặc metadata định kỳ để phát hiện corruption sớm. Deep scrub thường kiểm tra sâu hơn, có thể tốn I/O nhiều hơn.

Trong vận hành:

- Lên lịch scrub vào khung giờ phù hợp.
- Theo dõi latency khi scrub chạy.
- Không tự động repair dữ liệu khi chưa hiểu nguồn đúng, nhất là khi nhiều replica không khớp.

## Backup Verification

Backup chỉ có giá trị khi restore được. Integrity của backup nên được kiểm tra bằng:

- checksum/hash sau copy
- test restore định kỳ
- so sánh sample dữ liệu sau restore
- lưu log backup/restore và retention rõ ràng

## Best Practices

- Dùng checksum/hash để phát hiện sai lệch, nhưng cần redundancy/backup để phục hồi.
- Với dữ liệu quan trọng, dùng versioning hoặc immutable backup để chống delete/sửa nhầm.
- Không lưu hash/checksum cùng một nơi duy nhất nếu threat model có attacker sửa cả dữ liệu và checksum.
- Với production, tách cảnh báo "corruption detected" khỏi hành động repair tự động.

## Trang Liên Quan

- [Cache, Buffer, WAL And Journal](./05-cache-buffer-wal-journal.md)
- [Backup, Snapshot And Replication](./07-backup-snapshot-replication.md)
- [Storage Performance: IOPS, Throughput, Latency](./08-storage-performance-iops-throughput-latency.md)
