# PostgreSQL Backup And Restore

## Overview

PostgreSQL có nhiều kiểu backup: logical dump, cluster dump, physical base backup và WAL archive/PITR. Chọn kiểu backup theo RPO/RTO, kích thước DB, nhu cầu restore chọn lọc và topology replication.

## Logical Backup With pg_dump

Custom format linh hoạt hơn plain SQL vì dùng được `pg_restore`, chọn object và parallel restore:

```bash
pg_dump -Fc -f appdb.dump appdb
pg_restore -d appdb_restore appdb.dump
```

Plain SQL:

```bash
pg_dump -f appdb.sql appdb
psql -1 -f appdb.sql appdb_restore
```

`-1` bọc restore trong một transaction khi phù hợp, giúp fail thì rollback toàn bộ. Không phải mọi restore lớn/DDL đều nên ép một transaction; cần test với dataset thật.

## Whole Cluster Dump

```bash
pg_dumpall -f cluster.sql
```

`pg_dumpall` hữu ích để lấy role/global object và nhiều database, nhưng file có thể lớn và restore tuần tự. Config files như `postgresql.conf`, `pg_hba.conf`, certificate, extension package và OS-level dependency không tự nằm đầy đủ trong logical dump.

## COPY Is Not A Full Backup

`COPY` tốt cho export/import table hoặc query result:

```sql
COPY users TO '/path/to/users.csv' WITH (FORMAT csv, HEADER true);
COPY users FROM '/path/to/users.csv' WITH (FORMAT csv, HEADER true);
```

Nhưng CSV không giữ đầy đủ schema, index, sequence, privilege, trigger, extension và dependency. Không xem CSV export là backup production đầy đủ.

## Physical Backup And PITR

Với RPO/RTO nghiêm túc, cần base backup cộng WAL archive để point-in-time recovery. Mental model:

```text
base backup + archived WAL -> restore tới thời điểm mong muốn
```

Các hàm/công cụ backup vật lý thay đổi theo version và toolchain; dùng tài liệu chính thức hoặc backup tool đã chuẩn hóa. Điều bắt buộc là test restore định kỳ, không chỉ kiểm tra job backup exit code.

## Restore Checklist

- Restore vào môi trường cô lập trước.
- Kiểm tra role/privilege/search_path.
- Kiểm tra extension có sẵn.
- Chạy `ANALYZE` nếu restore làm planner thiếu stats.
- Verify row count/sample query/application smoke test.
- Ghi nhận thời gian restore thực tế so với RTO.

## Related Pages

- [Backup Restore Fundamentals](../../01-database-fundamentals/08-backup-restore-pitr-snapshot-logical-physical.md)
- [Backup Restore Validation](../../08-database-operations-patterns/02-backup-restore-validation.md)

