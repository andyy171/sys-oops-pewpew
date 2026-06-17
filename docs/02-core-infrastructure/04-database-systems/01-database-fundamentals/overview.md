# Database Fundamentals

Folder này là lớp nền trước khi đi vào PostgreSQL, MySQL, MongoDB, Redis hay distributed database. Mục tiêu là hiểu database như một hệ thống lưu trữ có cấu trúc, có transaction, concurrency control, query engine, durability và operational risk.

## Reading Order

1. [Database Models](./01-database-models-relational-document-kv-column-graph.md)
2. [SQL vs NoSQL And Selection Patterns](./02-sql-vs-nosql-and-selection-patterns.md)
3. [Transaction, ACID And Isolation Levels](./03-transaction-acid-isolation-levels.md)
4. [Index: B-Tree, LSM, Hash, Full-Text](./04-index-btree-lsm-hash-fulltext.md)
5. [Query Planner And Execution Plan](./05-query-planner-and-execution-plan.md)
6. [Locking, MVCC And Concurrency Control](./06-locking-mvcc-concurrency-control.md)
7. [Replication, Sharding And Partitioning](./07-replication-sharding-partitioning.md)
8. [Backup, Restore, PITR, Snapshot, Logical, Physical](./08-backup-restore-pitr-snapshot-logical-physical.md)
9. [Database Performance: Latency, Throughput, IOPS](./09-database-performance-latency-throughput-iops.md)

## Core Mental Model

Một database production cần cân bằng 5 mục tiêu:

- **Correctness**: dữ liệu đúng, constraint đúng, transaction không phá invariants.
- **Durability**: dữ liệu đã commit không mất khi crash.
- **Concurrency**: nhiều client cùng đọc/ghi mà không phá nhau.
- **Performance**: query đủ nhanh với workload hiện tại và tương lai gần.
- **Operability**: backup, restore, monitoring, failover, migration và RCA làm được trong thực tế.

## Vendor Boundary

Các note trong folder này không khóa vào một sản phẩm. Nếu nguồn học là tài liệu theo vendor, chỉ giữ lại khái niệm chung như schema, index, transaction, backup, replication, sharding, connection, isolation và performance.
