# PostgreSQL High Availability And Replication

## Overview

PostgreSQL HA thường dựa trên streaming replication, WAL shipping, standby node và failover tooling. Replication giúp có bản sao và giảm RPO, nhưng không tự giải quyết failover an toàn, split-brain, client routing hoặc backup validation.

## Streaming Replication Mental Model

```text
primary writes WAL
-> WAL streamed to standby
-> standby replays WAL
-> standby can serve read-only query if hot standby enabled
```

Các thành phần cần có:

- replication role có quyền replication;
- `pg_hba.conf` cho phép standby connect;
- primary cấu hình WAL/replication phù hợp;
- standby được tạo bằng base backup hoặc tool tương đương;
- monitoring replication lag và replay state.

## Replication User And Access

Ví dụ khái niệm:

```bash
createuser --replication --pwprompt repl_user
```

`pg_hba.conf` cần giới hạn IP standby:

```text
host replication repl_user 10.0.0.20/32 scram-sha-256
```

Không dùng superuser app làm replication user. Credential replication có blast radius lớn vì có thể đọc WAL/data stream.

## Base Backup

`pg_basebackup` tạo bản sao vật lý để khởi tạo standby:

```bash
pg_basebackup -h <primary-ip> -D <data-dir> -U repl_user -v -P --wal-method=stream
```

Trước khi chạy trên production, xác nhận data directory đích trống/đúng, disk đủ, version tương thích và không ghi đè nhầm node đang có dữ liệu.

## Failover Risks

Failover cần giải quyết:

- ai quyết định promote standby;
- làm sao tránh hai primary cùng nhận write;
- client/app đổi endpoint thế nào;
- old primary quay lại cluster ra sao;
- replication slot/WAL retention có làm đầy disk không;
- backup sau failover lấy từ primary mới hay topology mới.

Không nên tự động promote nếu chưa có fencing/quorum/consensus hoặc operational runbook rõ.

## Monitoring

Theo dõi:

- replication lag theo byte/time;
- WAL generation rate;
- replication slot retained WAL;
- standby replay paused hay không;
- primary/standby connection;
- failover event và timeline change.

## Related Pages

- [HA Failover And Switchover](../../08-database-operations-patterns/04-ha-failover-and-switchover.md)
- [Replication, Sharding And Partitioning](../../01-database-fundamentals/07-replication-sharding-partitioning.md)

