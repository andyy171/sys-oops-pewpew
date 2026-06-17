# Storage And Database Selection Patterns

## Overview

AWS có nhiều storage/database service vì workload có nhu cầu khác nhau: object, block, file, relational, key-value, cache, archive và analytics. Chọn sai loại storage thường gây lỗi về durability, latency, sharing hoặc cost.

## Storage Selection

| Nhu cầu | Service thường dùng | Ghi chú |
| --- | --- | --- |
| Object, backup, static asset, data lake | S3 | regional, multi-AZ durability mặc định |
| Block volume cho EC2 | EBS | gắn với một AZ, snapshot ra S3 |
| Temporary high-performance local disk | Instance Store | mất khi instance/host mất |
| Shared Linux filesystem | EFS | regional file system, mount từ nhiều AZ |
| Windows file share/HPC FS | FSx | chọn flavor theo workload |
| Archive dài hạn | S3 Glacier classes | cost thấp hơn, restore chậm hơn |

## S3 Mental Model

S3 là object storage, không phải filesystem POSIX.

Phù hợp cho:

- Static website asset.
- Backup.
- Image/video/document.
- Log archive.
- Data lake.
- Artifact.

Không phù hợp cho:

- Database file cần block semantics.
- Shared POSIX filesystem cần lock/rename behavior như local FS.

Các điểm cần quản trị:

- Bucket policy/IAM.
- Block Public Access.
- Versioning.
- Lifecycle rule.
- Replication.
- Encryption.
- Access log/object-level audit khi cần.

## EBS, Snapshot Và AZ

EBS volume gắn với một AZ và attach vào EC2 trong cùng AZ.

Nếu cần bảo vệ dữ liệu:

- Snapshot EBS.
- Copy snapshot sang Region khác nếu cần DR.
- Không giả định EBS tự sống qua AZ outage.

EBS phù hợp cho database hoặc workload cần block device, nhưng HA của database vẫn cần replication/managed service.

EBS, EFS/S3 và instance store khác nhau ở semantics:

| Need | Tránh nhầm với | Lý do |
| --- | --- | --- |
| Database file, WAL, filesystem cần block device | S3 | S3 không có POSIX/block semantics |
| Nhiều EC2 cùng đọc/ghi file tree | EBS đơn lẻ | EBS thường gắn với một instance/AZ; dùng EFS/FSx nếu cần shared filesystem |
| Cache/scratch tốc độ cao có thể mất | EBS bắt buộc | Instance store có thể hợp lý nếu app chịu mất node |
| Dữ liệu critical cần restore độc lập instance | Instance store | Instance store mất theo lifecycle/host |

Trước khi chọn block/file/object storage, hỏi:

1. App truy cập bằng system call filesystem hay bằng API object?
2. Có cần nhiều instance cùng đọc/ghi không?
3. Dữ liệu có thể mất khi replace instance không?
4. RTO/RPO là gì và restore đã được test chưa?
5. Bottleneck là latency, throughput, IOPS, request rate hay operational complexity?

## EFS

EFS cung cấp shared Linux filesystem cho nhiều instance. Nó phù hợp khi nhiều EC2 cần đọc/ghi cùng file tree.

Use case:

- Shared content.
- Home directory.
- Legacy app cần shared filesystem.
- Container workload cần shared POSIX-like storage.

Điểm cần chú ý:

- Performance mode/throughput mode.
- Security group cho mount target.
- NFS behavior và file locking.

## RDS, Aurora, DynamoDB, ElastiCache

| Nhu cầu | Service |
| --- | --- |
| SQL managed database | RDS |
| MySQL/PostgreSQL-compatible cloud-native relational | Aurora |
| Key-value/document serverless NoSQL | DynamoDB |
| In-memory cache/session/cache-aside | ElastiCache |

Chọn database theo access pattern:

- Query quan hệ phức tạp, transaction SQL: RDS/Aurora.
- Key-value access predictable, scale cao: DynamoDB.
- Cache để giảm latency/load DB: ElastiCache.

## Common Mistakes

- Dùng EBS cho data cần shared multi-AZ access.
- Dùng S3 như filesystem có random write/rename semantics.
- Quên lifecycle/retention khiến S3 cost tăng.
- Không bật backup/snapshot cho data quan trọng.
- Dùng database làm queue thay vì SQS/EventBridge/Kinesis khi workload async.

## Related Pages

- [S3 Object Storage Patterns](./01-s3-object-storage-patterns.md)
- [EBS, EFS, FSx And Data Migration](./02-ebs-efs-fsx-data-migration.md)
- [RDS, Aurora, DynamoDB And Caching](./03-rds-aurora-dynamodb-caching.md)
- [High Availability, Decoupling And Fault Tolerance](../09-architecture-resilience/01-high-availability-decoupling-and-fault-tolerance.md)
