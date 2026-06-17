# PostgreSQL Operations And Troubleshooting

## Overview

PostgreSQL troubleshooting nên đi từ connection, lock, query plan, vacuum/bloat, WAL/disk, replication và config. Đừng restart trước khi đọc log, `pg_stat_activity` và metric chính; restart có thể che mất bằng chứng.

## Quick Checks

```sql
SELECT version();
SELECT now();
SELECT datname, numbackends FROM pg_stat_database;
SELECT pid, usename, state, wait_event_type, wait_event, query
FROM pg_stat_activity;
```

Trên host:

```bash
systemctl status postgresql
journalctl -u postgresql
df -h
iostat -xz 1
ss -lntp
```

## Connection Issues

Kiểm tra theo thứ tự:

- service listen đúng host/port chưa;
- firewall/security group;
- `listen_addresses`;
- `pg_hba.conf` match đúng database/user/source IP/method;
- password/auth method;
- TLS requirement;
- database/role tồn tại;
- connection pool có cạn connection không.

## Slow Query

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...
```

Hỏi:

- planner dùng index hay seq scan hợp lý;
- stats cũ cần `ANALYZE` không;
- filter có selective không;
- sort/hash có spill ra disk không;
- query bị lock wait hay thật sự CPU/IO bound;
- app có N+1 query hoặc transaction giữ lâu không.

## Locks And Long Transactions

```sql
SELECT pid, state, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE state <> 'idle';
```

Long transaction giữ row version cũ, làm vacuum không dọn được và có thể tạo bloat. Khi kill query/backend, phải hiểu app impact và transaction rollback cost.

## Vacuum, Analyze And Bloat

MVCC tạo dead tuples sau update/delete. Autovacuum dọn dead tuples và analyze cập nhật planner stats. Nếu autovacuum không theo kịp:

- table/index bloat tăng;
- query chậm do scan nhiều page;
- transaction ID wraparound risk;
- disk usage tăng.

Không tắt autovacuum trong production nếu không có chiến lược thay thế.

## FDW, dblink And Extensions

`postgres_fdw` và `dblink` cho phép truy cập database khác, hữu ích cho migration/integration. Nhưng chúng đưa network latency, remote permission và failure mode vào query local.

Checklist:

- timeout rõ;
- credential được quản lý an toàn;
- query remote có filter pushdown/index;
- không để transaction local chờ remote vô hạn;
- monitoring cả hai phía.

## Symptom Map

| Symptom | Kiểm tra |
|---|---|
| `too many connections` | pool, max_connections, idle transaction, app leak |
| query chậm | `EXPLAIN`, stats, lock wait, IO, work_mem spill |
| disk đầy | WAL retention, replication slot, bloat, temp files, logs |
| replica lag | WAL rate, network, standby IO/CPU, long query on standby |
| permission denied | role membership, schema usage, table/sequence privilege, default privileges |
| restore lỗi | extension missing, owner/role missing, version mismatch, search_path |

## Related Pages

- [PostgreSQL Backup And Restore](./04-backup-restore.md)
- [PostgreSQL HA And Replication](./05-high-availability-and-replication.md)
- [Database Performance Troubleshooting](../../08-database-operations-patterns/05-performance-troubleshooting.md)

