# RDS, Aurora, DynamoDB And Caching

## Overview

Database selection trong AWS nên dựa trên data model, consistency, access pattern, scaling và vận hành. Không chuyển sang DynamoDB chỉ vì muốn "serverless" nếu ứng dụng đang phụ thuộc SQL/relational query phức tạp.

## Service Selection

| Need | Service |
|---|---|
| SQL relational managed DB | RDS |
| MySQL/PostgreSQL-compatible, HA/performance tốt hơn | Aurora |
| Key-value/document, millisecond latency, scale lớn | DynamoDB |
| Cache cho DB/query/session | ElastiCache |
| Cache cho DynamoDB | DAX |
| Connection pooling cho serverless/app scale nhanh | RDS Proxy |

## RDS Operating Model

RDS là managed relational database: AWS vận hành phần lớn OS, engine installation, patching workflow, backup integration và failover automation; team ứng dụng vẫn sở hữu schema, query, user/database permission, parameter choice, network exposure, credential rotation, backup retention và restore validation.

Khi tạo một RDS instance, các quyết định nền tảng gồm:

- Engine/version: MySQL, PostgreSQL, MariaDB, SQL Server, Oracle hoặc engine khác tùy nhu cầu license/tính năng.
- DB instance class: CPU/RAM/network profile.
- Storage type/size/IOPS: ảnh hưởng latency, throughput và cost.
- DB subnet group: subnet/AZ nơi database được đặt.
- Security group: chỉ allow từ app/security group cần kết nối.
- Backup retention/window và maintenance window.
- Encryption, parameter group, option group và deletion protection.
- Public accessibility: production database thường không public.

Endpoint RDS là DNS name cho client kết nối. Không hard-code endpoint rải rác trong app; đặt qua config/secret manager/service discovery để khi restore/failover/migration có thể đổi an toàn.

## Access Layers

Access vào RDS có ba lớp riêng:

| Lớp | Kiểm soát gì | Ví dụ |
|---|---|---|
| IAM | Ai được tạo/sửa/xóa DB instance, snapshot, parameter group | `rds:ModifyDBInstance`, `rds:CreateDBSnapshot` |
| Network | Workload nào được mở TCP tới database endpoint | Security Group cho app -> DB port |
| Database user | User nào được đọc/ghi schema/table nào | MySQL/PostgreSQL role/grant |

IAM không thay thế database user permission. Security Group mở đúng port cũng không có nghĩa app được quyền query. Production nên dùng database user riêng cho từng app/service, quyền tối thiểu, credential lưu trong Secrets Manager hoặc secret store phù hợp, có rotation plan và audit.

Không đưa `MasterUserPassword`, connection string hoặc dump chứa dữ liệu thật vào Git, note, ticket hoặc shell history. Với migration/import, dùng host trung gian trong cùng VPC/Region để giảm latency nhưng phải kiểm soát IAM role, security group, disk encryption và cleanup dump sau khi import.

## Backup, PITR And Restore

RDS backup không chỉ để "có snapshot"; phải chứng minh restore được trong RTO/RPO mong muốn.

Các loại thường gặp:

- Automated backup: phục vụ point-in-time recovery trong retention window.
- Manual snapshot: giữ đến khi tự xóa, phù hợp trước change lớn hoặc mốc release.
- Cross-Region snapshot copy/replica: phục vụ DR hoặc migration, cần kiểm tra compliance dữ liệu.

Restore từ snapshot/PITR thường tạo **DB instance mới**, không ghi đè trực tiếp DB đang chạy. Vì vậy runbook restore cần có bước đổi endpoint/config, kiểm tra dữ liệu, rồi mới cutover traffic.

Pre-check trước restore hoặc delete:

1. Xác nhận đúng account, Region, DB identifier, snapshot identifier và environment.
2. Kiểm tra retention, latest restorable time, encryption/KMS key và subnet/security group đích.
3. Xác nhận app đang dùng endpoint nào và cách đổi endpoint/config.
4. Với dữ liệu nhạy cảm, kiểm tra policy khi copy snapshot sang Region/account khác.
5. Chuẩn bị rollback: giữ DB cũ read-only hoặc giữ snapshot trước cutover nếu phù hợp.

Thao tác nguy hiểm:

- `delete-db-instance --skip-final-snapshot` có thể mất cơ hội backup cuối cùng.
- Xóa manual snapshot có thể xóa mốc restore duy nhất ngoài retention window.
- Restore/cutover nhầm endpoint có thể khiến app ghi vào DB sai.

## High Availability And Read Scaling

RDS Multi-AZ là HA/failover pattern, không phải read-scaling pattern chính. Primary replicate đồng bộ sang standby ở AZ khác; khi sự cố, RDS failover và DNS endpoint trỏ sang instance mới. Ứng dụng phải chịu được reconnect, transaction retry và DNS/cache TTL phù hợp.

Read replica phục vụ read scaling, reporting hoặc migration. Replica thường replicate bất đồng bộ, nên có replica lag; app phải route read/write đúng và chấp nhận read-after-write có thể trễ nếu đọc từ replica.

Promote read replica là thao tác topology lớn:

- Replica có thể restart/unavailable trong lúc promote.
- Sau promote, nó trở thành DB độc lập và không tự đồng bộ ngược về primary cũ.
- Cần cutover plan, validation dữ liệu và rollback rõ ràng.

## Performance And Monitoring

RDS performance thường bị giới hạn bởi một trong các nhóm sau:

- CPU hoặc memory của DB instance class.
- Storage latency/IOPS/throughput.
- Connection count, pool sai cấu hình hoặc connection storm.
- Slow query, missing index, lock wait/deadlock.
- Replica lag hoặc backup/maintenance window trùng peak traffic.

CloudWatch metrics tối thiểu nên theo dõi:

| Metric | Ý nghĩa |
|---|---|
| `CPUUtilization` | CPU saturation hoặc query quá nặng |
| `FreeableMemory` | memory pressure/cache pressure |
| `FreeStorageSpace` | nguy cơ hết dung lượng |
| `DatabaseConnections` | connection pool/connection leak |
| `ReadIOPS` / `WriteIOPS` | workload I/O shape |
| `DiskQueueDepth` | storage bị xếp hàng, có thể thiếu IOPS/throughput |
| `ReplicaLag` | replica đọc trễ, DR/migration risk |

Khi database chậm, đừng scale instance ngay lập tức nếu chưa có signal. Triage nên tách: connection issue, lock wait, slow query, IO saturation, CPU saturation, memory/cache pressure và network/security group issue. Scale up RDS có thể giúp CPU/RAM/IO, nhưng missing index hoặc transaction giữ lock lâu vẫn cần sửa ở schema/query/application.

## RDS vs Aurora

| Capability | RDS | Aurora |
|---|---|---|
| Multi-AZ | HA/failover, không phải read scaling chính | Cluster storage across AZ, replicas có thể dùng đọc và failover |
| Read scaling | Read replicas | Aurora replicas |
| Serverless option | Có tùy engine/version | Aurora Serverless phù hợp workload biến động |
| Global database | Không phải mặc định | Aurora Global Database cho multi-region read/DR |

## Common Scenario Patterns

| Requirement | Pattern |
|---|---|
| DB single EC2 cần HA, ít sửa app | Migrate sang RDS Multi-AZ |
| Read load tăng mạnh | Read replica/Aurora replica + ElastiCache nếu query lặp |
| Lambda làm quá tải connection DB | RDS Proxy hoặc queue-based ingestion |
| Credential DB cần rotate định kỳ | Secrets Manager rotation |
| Workload DynamoDB unpredictable traffic | On-demand capacity |
| Workload DynamoDB predictable test window | Provisioned capacity theo RCU/WCU tính toán |

## DynamoDB Mental Model

DynamoDB là managed key-value/document database. Không giống RDS, DynamoDB không phải nơi đưa nguyên SQL app vào rồi chạy; ứng dụng phải được thiết kế theo access pattern và gọi API/SDK.

Object model:

```text
Table
-> Item
-> Attribute
-> Primary key: partition key hoặc partition key + sort key
-> Optional indexes: LSI / GSI
```

Key design là quyết định khó đổi. Tên table và primary key schema gần như là contract của ứng dụng, nên phải bắt đầu từ câu hỏi "app cần query gì?" thay vì bắt đầu từ entity diagram kiểu relational.

Ví dụ tư duy:

- Cần lookup user theo `user_id`: partition key `user_id`.
- Cần list task của một user theo thời gian: partition key `user_id`, sort key `created_at` hoặc `task_id`.
- Cần query task theo category toàn hệ thống: thêm GSI với partition key `category` nếu access pattern này thật sự quan trọng.

FilterExpression không thay thế key/index design. Query đọc theo key trước rồi filter sau; nếu key condition trả về quá nhiều item, filter vẫn tốn capacity và latency. Scan toàn bảng chỉ phù hợp cho admin job nhỏ, backfill có kiểm soát, hoặc workload đã được phân trang/throttle rõ ràng.

## DynamoDB Consistency, Writes And Transactions

DynamoDB read mặc định là eventually consistent. Với `GetItem`, `Query`, `Scan` trên table/LSI, có thể bật `ConsistentRead=true` khi cần đọc mới nhất, đổi lại tốn nhiều capacity/latency hơn. GSI và streams luôn eventually consistent, nên không dùng GSI cho invariant cần đọc-ngay-sau-ghi tuyệt đối.

Write vào một item là atomic. Với nhiều item, DynamoDB hiện hỗ trợ transactional APIs như `TransactWriteItems` và `TransactGetItems`, nhưng transaction không nên dùng để biến DynamoDB thành relational database:

- Transaction tốn capacity hơn và có conflict behavior riêng.
- Không dùng transaction cho bulk ingest nếu `BatchWriteItem` hoặc idempotent pipeline đủ.
- Transaction của global tables không đảm bảo atomic cross-Region.
- Dùng condition expression để tránh overwrite/delete nhầm, ví dụ chỉ tạo item nếu key chưa tồn tại.

Condition expression cũng là nền tảng cho optimistic locking và idempotent state transition. Pattern phổ biến là lưu thêm thuộc tính `version` hoặc `state`, rồi chỉ update khi giá trị hiện tại đúng với kỳ vọng:

```text
read item version/state
-> compute next state
-> update item IF version/state still matches
-> if condition fails, read lại và retry hoặc trả conflict
```

Ví dụ dùng cho workflow `Created -> Uploaded -> Processed`:

- `PutItem` tạo job mới với điều kiện key chưa tồn tại.
- `UpdateItem` từ `Created` sang `Uploaded` chỉ hợp lệ nếu state hiện tại là `Created` hoặc đã là `Uploaded` với cùng payload idempotent.
- `UpdateItem` từ `Uploaded` sang `Processed` chỉ hợp lệ nếu state hiện tại là `Uploaded` hoặc đã là `Processed` với cùng kết quả.
- Worker xử lý duplicate message phải đọc state trước khi tạo side effect mới.

Optimistic locking phù hợp khi xung đột ghi không quá cao. Nếu nhiều worker cùng ghi vào một item liên tục, retry có thể tạo overhead lớn; khi đó cần xem lại data model, chia nhỏ item, dùng queue partitioning hoặc chuyển invariant sang transaction có kiểm soát.

Streams hữu ích để nối DynamoDB với async pipeline: cache invalidation, Lambda processing, audit/event flow hoặc replication logic. Stream records vẫn cần consumer idempotent vì retry và ordering chỉ có giới hạn theo key/shard.

## DynamoDB Capacity And Hot Partition

DynamoDB có hai capacity mode chính:

| Mode | Khi dùng |
|---|---|
| On-demand | workload khó đoán, traffic biến động, muốn giảm quản trị capacity |
| Provisioned | workload ổn định/dự đoán được, cần cost governance hoặc capacity planning rõ |

Với provisioned mode, cần theo dõi read/write capacity của table và GSI riêng. GSI không "miễn phí": nó tốn storage, write capacity khi table update và có thể throttle riêng. Nếu GSI bị thiếu write capacity, write vào table cũng có thể bị ảnh hưởng.

Các signal cần theo dõi:

- `ConsumedReadCapacityUnits` / `ConsumedWriteCapacityUnits`.
- `ThrottledRequests`.
- `ReadThrottleEvents` / `WriteThrottleEvents`.
- `SuccessfulRequestLatency`.
- `SystemErrors` / `UserErrors`.
- GSI consumed/throttle metrics.

Hot partition xảy ra khi quá nhiều request dồn vào một partition key hoặc một tập key nhỏ. Cách xử lý thường là đổi key design, write sharding, time bucket, adaptive access pattern hoặc caching; chỉ tăng capacity tổng không phải lúc nào cũng sửa được hot key.

## DynamoDB Production Guardrails

- Dùng IAM least privilege theo table/index/action; không cấp `dynamodb:*` rộng cho app.
- Thiết kế key/index từ access pattern, load estimate và cardinality.
- Với delete/update, dùng condition expression khi có invariant cần bảo vệ.
- Bật point-in-time recovery khi dữ liệu quan trọng.
- Thiết kế retry với exponential backoff và idempotency token/condition.
- Không dùng scan thường xuyên trên bảng lớn trong request path.
- Dùng DynamoDB Local chỉ cho dev/test API compatibility, không coi là môi trường production tương đương.

## Caching

Cache không thay thế database. Nó giảm load và latency cho access pattern đọc lặp lại. Khi dùng cache, cần nghĩ về invalidation, TTL, consistency và failure behavior nếu cache unavailable.

## Related Pages

- [Lambda, API Gateway And Event-Driven Compute](../03-compute-containers-serverless/02-lambda-api-gateway-event-driven.md)
- [IAM, Accounts, Organizations And Policy](../01-identity-security-governance/01-iam-accounts-organizations-policy.md)
