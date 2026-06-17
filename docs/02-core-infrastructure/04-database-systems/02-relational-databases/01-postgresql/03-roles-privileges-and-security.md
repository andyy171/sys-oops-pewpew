# PostgreSQL Roles, Privileges And Security

## Overview

PostgreSQL dùng role model cho cả user và group. Production nên thiết kế role theo least privilege, tách owner/migration/app/read-only/backup/monitoring, và không dùng superuser cho application.

## Role Basics

Tạo role login:

```sql
CREATE ROLE app_user WITH LOGIN;
```

Đặt password nên dùng cơ chế không ghi password vào shell history hoặc SQL log. Trong `psql`, dùng:

```text
\password app_user
```

Tránh hard-code password trong script. Dùng secret manager hoặc biến môi trường được kiểm soát bởi runtime.

## Database And Schema Access

Pattern khóa public access rồi mở quyền có chủ đích:

```sql
REVOKE CONNECT ON DATABASE appdb FROM PUBLIC;
GRANT CONNECT ON DATABASE appdb TO app_user;

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO app_user;
```

Quyền table/sequence:

```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO app_user;
```

Với object tạo trong tương lai:

```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
```

## Read-Only User

```sql
CREATE ROLE readonly WITH LOGIN;
GRANT CONNECT ON DATABASE appdb TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly;
```

Read-only không nên có quyền tạo function, temporary object nguy hiểm hoặc đọc bảng nhạy cảm nếu chưa phân loại dữ liệu.

## search_path Risk

`search_path` quyết định schema resolution. Cấu hình sai có thể làm app gọi nhầm function/table hoặc tạo object vào schema không mong muốn.

```sql
ALTER ROLE app_user SET search_path = app, public;
SHOW search_path;
```

Với function security-sensitive, cần hiểu `SECURITY DEFINER`, owner và `search_path` để tránh privilege escalation.

## pg_hba.conf Boundary

`pg_hba.conf` kiểm soát client authentication theo type/database/user/address/method. Nó là lớp ngoài SQL privilege:

```text
# TYPE  DATABASE  USER      ADDRESS       METHOD
host    appdb     app_user  10.0.0.0/24   scram-sha-256
```

Thay đổi `pg_hba.conf` cần reload và test từ client thật. Không mở `0.0.0.0/0` nếu không có firewall/TLS/auth policy phù hợp.

## Related Pages

- [Database Operations Patterns](../../08-database-operations-patterns/overview.md)
- [PostgreSQL Operations And Troubleshooting](./06-operations-and-troubleshooting.md)

