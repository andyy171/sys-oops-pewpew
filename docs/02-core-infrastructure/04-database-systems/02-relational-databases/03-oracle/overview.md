# Oracle Database Operations Overview

## Overview

Oracle Database là RDBMS lớn, thường xuất hiện trong hệ thống enterprise cần transaction, dữ liệu quan trọng, backup/restore nghiêm ngặt và kiểm soát quyền chặt. Note này chuyển hóa từ inbox `Pro_Oracle_Database_23c_Administration_Michelle_Malcher_2024_Apress.docx` ở mức vận hành tổng quan; không ghi lại chi tiết vendor/version chưa được xác minh.

## Mental Model

```text
client session
  -> listener / service name
  -> instance memory and background processes
  -> database objects: schema, table, index, view
  -> transaction and redo
  -> data files / control files / redo logs / archive logs
  -> backup, restore, recovery, monitoring
```

Khi vận hành Oracle, cần tách rõ database logical object và file vật lý. Một lỗi query, lỗi listener, lỗi tablespace đầy, lỗi redo/archive log hoặc lỗi storage bên dưới có triệu chứng khác nhau và cách xử lý khác nhau.

## Thành Phần Cần Nắm

- Oracle Home: nơi chứa binary và thư viện của một bản cài.
- Oracle Base/Inventory: cấu trúc quản lý cài đặt và inventory.
- Listener/network config: lớp nhận kết nối client.
- Instance: memory + background processes đang chạy.
- Database: tập hợp data files, control files, redo logs và metadata.
- Tablespace/data file: mapping giữa logical storage và file vật lý.
- Control file: metadata quan trọng để database biết cấu trúc file/log.
- Online redo log và archived redo log: nền tảng cho recovery/PITR.
- User/schema/role/privilege: mô hình quyền và ownership object.

## Operations Topics

Các mảng vận hành chính:

- Installation and environment: OS user/group, kernel/resource prerequisite, Oracle Home, environment variables.
- Database creation: tạo database, service, listener và cấu hình cơ bản.
- Storage management: tablespace, data file, temp/undo, capacity monitoring.
- Security: user, role, privilege, password/profile, auditing.
- Backup and recovery: RMAN, backup catalog/reporting, restore, media recovery, archived redo.
- Multitenant: CDB/PDB là mô hình cần hiểu riêng khi vận hành Oracle hiện đại.
- Automation and troubleshooting: script health check, log collection, job scheduling, alert log.
- Migration/fleet management: thay đổi version/topology cần rehearsal và rollback.

## Safe Checks

Ví dụ nhóm kiểm tra an toàn ở mức ý tưởng:

```sql
SELECT name, open_mode FROM v$database;
SELECT instance_name, status FROM v$instance;
SELECT tablespace_name, status FROM dba_tablespaces;
SELECT username, account_status FROM dba_users;
```

Tùy môi trường, quyền truy cập các view có thể khác nhau. Không chạy thao tác thay đổi schema, user, storage hoặc recovery nếu chưa có backup và maintenance plan.

## Rủi Ro Vận Hành

- Restore nhầm lên production có thể ghi đè dữ liệu.
- Xóa archived redo log khi chưa có backup coverage có thể phá PITR.
- Thay đổi tablespace/data file cần hiểu filesystem/storage bên dưới.
- Kill session hoặc thay đổi lock/schema có thể ảnh hưởng transaction đang chạy.
- Patch/upgrade cần kiểm tra compatibility, backup, rollback và window rõ ràng.

## Trang Liên Quan

- [Database Systems](../../overview.md)
- [Database Operations Patterns](../../08-database-operations-patterns/overview.md)
- [Backup Restore Validation](../../08-database-operations-patterns/02-backup-restore-validation.md)
- [HA Failover And Switchover](../../08-database-operations-patterns/04-ha-failover-and-switchover.md)
