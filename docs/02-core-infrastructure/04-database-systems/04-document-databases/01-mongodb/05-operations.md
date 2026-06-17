# MongoDB Operations

## Overview

MongoDB operations tập trung vào process `mongod`/`mongos`, config, user/role, TLS, resource, log và lifecycle upgrade. Các thao tác thay đổi topology, index lớn hoặc schema migration phải có backup/rollback và quan sát replication lag.

## Basic Shell Checks

```javascript
db.adminCommand({ ping: 1 })
db.serverStatus()
db.stats()
db.getCollectionNames()
db.<collection>.stats()
```

Các lệnh này dùng để nắm nhanh service còn phản hồi không, database/collection có dung lượng thế nào và workload có dấu hiệu bất thường không.

## Configuration

Các nhóm cấu hình quan trọng:

- `storage.dbPath`: nơi lưu data, cần disk bền và monitoring dung lượng/latency.
- `net.bindIp`, `net.port`: không bind public nếu không có network control.
- `security.authorization`: bật authorization cho production.
- `net.tls`: bật TLS cho client và internal traffic khi có dữ liệu nhạy cảm.
- replication/sharding section: chỉ cấu hình theo topology đã thiết kế.

Không sửa config và restart production nếu chưa biết tác động tới election, client connection string và driver retry behavior.

## Authentication And Authorization

MongoDB có authentication để xác định danh tính và authorization để kiểm soát quyền. Pattern tối thiểu:

- user app riêng cho từng application/database;
- role tối thiểu, tránh dùng admin/root cho app;
- user backup/monitoring riêng;
- rotation credential có rollout plan;
- audit ai có quyền tạo user, role, index và drop collection.

Ví dụ khái niệm:

```javascript
use appdb
db.createUser({
  user: "app_user",
  pwd: passwordPrompt(),
  roles: [ { role: "readWrite", db: "appdb" } ]
})
```

## Index Và Migration Operations

Tạo index trên collection lớn là thay đổi vận hành, không chỉ thay đổi schema:

- kiểm tra query cần index bằng `explain`;
- tạo trong maintenance window nếu rủi ro cao;
- theo dõi CPU, IO, replication lag;
- tránh tạo nhiều index "để phòng hờ";
- sau migration, drop index không còn dùng nếu đã xác nhận an toàn.

Bulk update hoặc field type migration cần batch nhỏ, idempotent và có marker để resume.

## Upgrade Notes

Upgrade MongoDB cần đọc release notes chính thức theo version đang chạy. Không suy diễn từ tài liệu cũ. Trước khi upgrade:

- backup và test restore;
- kiểm tra driver compatibility;
- kiểm tra featureCompatibilityVersion nếu áp dụng;
- upgrade secondary trước theo runbook replica set;
- kiểm tra app smoke test sau từng bước.

## Operational Checklist

- Monitoring: connection, opcounters, replication lag, disk latency, cache, lock/queue, slow query.
- Logs: bật slow query/profiling có kiểm soát khi cần điều tra.
- Security: auth, TLS, least privilege, không expose port 27017 public.
- Capacity: working set, index size, oplog window, disk free.
- Backup: lịch backup, retention, restore drill.

## Related Pages

- [MongoDB Troubleshooting](./06-troubleshooting.md)
- [Database Observability Patterns](../../08-database-operations-patterns/08-database-observability-patterns.md)
- [Upgrade And Migration](../../08-database-operations-patterns/03-upgrade-and-migration.md)
