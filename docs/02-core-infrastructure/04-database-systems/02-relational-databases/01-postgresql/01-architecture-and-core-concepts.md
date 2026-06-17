# PostgreSQL Architecture And Core Concepts

## Overview

PostgreSQL là RDBMS ACID dùng SQL, schema, table, index, transaction và WAL. Với vận hành production, cần hiểu các lớp: client connection, process/backend, shared memory/cache, WAL, data files, autovacuum và replication.

## Core Concepts

| Concept | Ý nghĩa vận hành |
|---|---|
| Database | Boundary logic bên trong một PostgreSQL instance/cluster |
| Schema | Namespace cho table, view, function, type |
| Table | Quan hệ dữ liệu có column, constraint và index |
| WAL | Write-ahead log dùng cho crash recovery, replication và PITR |
| MVCC | Cho phép reader/writer song song bằng row version |
| Role | User/group privilege model |
| Extension | Module mở rộng như `pgcrypto`, `postgres_fdw` |

## psql And Metadata

`psql` là công cụ nền để kiểm tra object và thao tác SQL:

```bash
psql -h <host> -U <user> -d <database>
```

Một số meta-command:

```text
\l          -- list databases
\dn         -- list schemas
\dt         -- list tables
\d <table>  -- table definition
\d+ <table> -- table definition with extra info
\du         -- list roles
```

Các lệnh này hữu ích khi cần xác nhận nhanh schema thật trong database thay vì chỉ nhìn migration file.

## Data Types

PostgreSQL có type system phong phú: numeric, text, timestamp, interval, boolean, UUID, JSON/JSONB, array, network address, geometric và user-defined type. Chọn type đúng giúp constraint, index và planner làm việc tốt hơn.

Gợi ý:

- dùng `numeric` cho tiền/số cần exact precision;
- dùng `timestamptz` cho thời gian có timezone semantics;
- dùng `jsonb` khi cần document field có index/query, nhưng không thay thế schema quan hệ khi quan hệ rõ;
- tránh lạm dụng array/json nếu cần join, constraint và report thường xuyên.

## WAL And Crash Safety

PostgreSQL ghi WAL trước khi data page được flush. WAL là nền cho:

- crash recovery;
- streaming replication;
- point-in-time recovery;
- logical decoding trong một số mô hình integration.

Unlogged table bỏ qua WAL cho data table nên nhanh hơn trong một số workload tạm, nhưng không crash-safe và không replicate như table thường. Chỉ dùng cho staging/intermediate data có thể tái tạo.

```sql
CREATE UNLOGGED TABLE import_stage (
  id bigint,
  payload jsonb
);
```

## Related Pages

- [Transaction, ACID And Isolation Levels](../../01-database-fundamentals/03-transaction-acid-isolation-levels.md)
- [Locking, MVCC And Concurrency Control](../../01-database-fundamentals/06-locking-mvcc-concurrency-control.md)
- [PostgreSQL Operations And Troubleshooting](./06-operations-and-troubleshooting.md)

