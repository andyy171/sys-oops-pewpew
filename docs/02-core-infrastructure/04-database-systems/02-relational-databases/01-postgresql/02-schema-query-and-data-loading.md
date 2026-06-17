# PostgreSQL Schema, Query And Data Loading

## Overview

PostgreSQL mạnh ở schema rõ ràng, constraint, SQL expressive và bulk data loading. Khi vận hành, schema design và data loading phải đi cùng transaction boundary, lock impact, index maintenance và rollback plan.

## Table And Constraint Basics

```sql
CREATE TABLE agencies (
  id bigserial PRIMARY KEY,
  name text NOT NULL
);

CREATE TABLE users (
  id bigserial PRIMARY KEY,
  agency_id bigint REFERENCES agencies(id) DEFERRABLE INITIALLY DEFERRED,
  email text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now()
);
```

Constraint nên biểu đạt invariant thật của dữ liệu. Nếu app chỉ enforce trong code, dữ liệu có thể bị phá bởi batch job, script hoặc service khác.

## Create Table From Select

```sql
CREATE TABLE users_over_30 AS
SELECT *
FROM users
WHERE age > 30;
```

Pattern này hữu ích cho staging/report/migration, nhưng table mới không tự giữ đầy đủ index, constraint, privilege và comment như table nguồn. Cần bổ sung nếu dùng lâu dài.

## COPY For Bulk Load

`COPY` là cơ chế bulk load/export nhanh hơn nhiều so với insert từng dòng khi dữ liệu lớn.

```sql
COPY import_stage(id, payload)
FROM '/path/to/import.csv'
WITH (FORMAT csv, HEADER true);

COPY (
  SELECT id, email
  FROM users
) TO '/path/to/users.csv'
WITH (FORMAT csv, HEADER true);
```

Lưu ý vận hành:

- file path là phía server khi dùng SQL `COPY`;
- với client-side file, dùng `psql \copy`;
- load lớn có thể tạo WAL, lock, disk pressure và replication lag;
- staging table + validate + insert vào table chính thường an toàn hơn import trực tiếp.

## INSERT RETURNING And UPSERT

`RETURNING` giúp lấy giá trị sinh ra bởi database như id/default:

```sql
INSERT INTO users(email)
VALUES ('user@example.com')
RETURNING id;
```

UPSERT dùng `ON CONFLICT`:

```sql
INSERT INTO users(email, created_at)
VALUES ('user@example.com', now())
ON CONFLICT (email)
DO UPDATE SET created_at = EXCLUDED.created_at
RETURNING id;
```

UPSERT cần unique constraint/index phù hợp. Nếu conflict target sai hoặc update quá rộng, có thể gây write amplification và lock contention.

## CTE, Window Function, Trigger

CTE (`WITH`) giúp tách query phức tạp thành bước đọc được. Window function xử lý ranking/running total mà không collapse row như `GROUP BY`. Trigger chạy function khi `INSERT/UPDATE/DELETE` hoặc DDL event xảy ra.

Trigger hữu ích cho audit, denormalized field hoặc guardrail gần dữ liệu, nhưng cần cẩn thận:

- trigger ẩn side effect khỏi app;
- trigger lỗi làm transaction gốc fail;
- trigger nặng làm write latency tăng;
- event trigger cho DDL rất nhạy, cần quản trị như policy/code production.

## Related Pages

- [Query Planner And Execution Plan](../../01-database-fundamentals/05-query-planner-and-execution-plan.md)
- [Database Performance](../../01-database-fundamentals/09-database-performance-latency-throughput-iops.md)

