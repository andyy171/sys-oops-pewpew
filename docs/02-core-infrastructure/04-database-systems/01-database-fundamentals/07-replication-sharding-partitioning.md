# Replication, Sharding And Partitioning

## Overview

Replication, sharding và partitioning đều chia dữ liệu theo cách nào đó, nhưng mục tiêu khác nhau:

- **Replication**: sao chép dữ liệu để tăng availability, durability hoặc read scale.
- **Partitioning**: chia dữ liệu trong cùng một logical database/table để dễ quản lý hoặc tăng performance.
- **Sharding**: chia dữ liệu sang nhiều node độc lập để scale dung lượng hoặc throughput.

## Replication

Các mô hình phổ biến:

- Primary-replica: một primary nhận write, replica phục vụ read hoặc standby.
- Multi-primary: nhiều node nhận write, cần conflict resolution.
- Synchronous replication: commit chờ replica xác nhận.
- Asynchronous replication: primary commit trước, replica theo sau.

Tradeoff chính là consistency, latency, data loss risk và failover complexity.

## Replication Lag

Replication lag xảy ra khi replica chậm hơn primary. Nguyên nhân thường gặp:

- Write burst.
- Query lâu trên replica.
- Network latency/loss.
- Replica I/O hoặc CPU yếu.
- Transaction lớn.

Tác động:

- Read-after-write không thấy dữ liệu mới.
- Failover có thể mất dữ liệu nếu async.
- Backup từ replica có thể không đủ mới nếu không kiểm tra lag.

## Partitioning

Partitioning chia table theo rule:

- Range: theo thời gian hoặc numeric range.
- List: theo tenant/region/status.
- Hash: phân bố đều theo hash key.

Lợi ích:

- Prune partition để query ít dữ liệu hơn.
- Quản lý retention/drop old data dễ hơn.
- Tách maintenance theo partition.

Rủi ro:

- Partition key sai làm query vẫn scan nhiều partition.
- Quá nhiều partition gây overhead metadata/planning.
- Unique constraint/global index có thể phức tạp tùy engine.

Partitioning không thay thế index; nó giảm phạm vi scan, còn index trong partition vẫn cần cho predicate selective. Lãi lớn nhất thường đến từ partition pruning và lifecycle operation như detach/drop/archive partition cũ.

## Sharding

Sharding chia dữ liệu sang nhiều node. Nó nên là quyết định có chủ đích vì làm application và operations phức tạp hơn.

Cần thiết kế:

- Shard key.
- Routing layer.
- Rebalancing.
- Cross-shard query.
- Cross-shard transaction.
- Backup/restore theo shard.
- Hot shard detection.

Shard key tốt phải phân bố đều, ổn định, phù hợp access pattern và tránh hotspot.

Chỉ nên sharding khi các hướng đơn giản hơn đã không đủ: query/index đã tối ưu, vertical scaling không còn kinh tế, read replica/cache/partitioning không giải quyết được, và hệ thống có shard key rõ ràng. Sharding đưa thêm cross-shard transaction, scatter-gather query, rebalancing, backup/restore theo shard và hot shard detection vào operational surface.

## HA And Failover Notes

- Replication không thay thế backup.
- Failover phải có runbook và tiêu chí promote rõ.
- Sau failover cần xử lý split-brain, old primary và client routing.
- Read replica không nên dùng cho read-your-writes nếu application không chịu stale read.

## Related Pages

- [Backup, Restore, PITR, Snapshot, Logical, Physical](./08-backup-restore-pitr-snapshot-logical-physical.md)
- [Database Performance](./09-database-performance-latency-throughput-iops.md)
