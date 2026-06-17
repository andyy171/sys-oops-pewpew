# MongoDB Backup And Restore

## Overview

Backup MongoDB phải trả lời được ba câu hỏi: backup có consistent không, restore vào đâu, và restore đã được test chưa. Với replica set/sharded cluster, backup không chỉ là copy một thư mục data bất kỳ.

## Logical Backup

`mongodump` tạo logical dump ở mức database/collection. Nó phù hợp cho database nhỏ-vừa, migration, restore chọn lọc hoặc môi trường không có snapshot hạ tầng.

```bash
mongodump --uri="mongodb://<user>:<password>@<host>:27017/<db>?authSource=admin" --out ./dump
mongorestore --uri="mongodb://<user>:<password>@<host>:27017" ./dump
```

Với production, tránh đưa password trực tiếp vào shell history. Ưu tiên secret manager, prompt, env đã kiểm soát hoặc file config có permission chặt.

## Replica Set Backup

Pattern thường gặp là backup từ secondary để giảm tải primary. Nhưng secondary backup vẫn cần kiểm soát:

- secondary có lag quá xa không;
- dump có dùng option consistency phù hợp không;
- backup có làm secondary lag thêm không;
- restore có tái tạo index/role/user như mong muốn không.

Trước khi backup:

```javascript
rs.status()
rs.printSecondaryReplicationInfo()
```

## Sharded Cluster Backup

Sharded cluster cần consistency giữa shards và config server metadata. Không dump từng shard độc lập rồi giả định restore sẽ đúng. Cần dùng tooling/runbook hỗ trợ sharded backup hoặc dừng/khóa write theo quy trình được kiểm chứng.

Checklist:

- biết backup tool hỗ trợ sharded cluster thế nào;
- ghi lại cluster topology;
- bảo vệ config server backup;
- test restore sang cluster staging;
- verify count/sample query/application smoke test sau restore.

## Physical Snapshot

Storage snapshot nhanh hơn logical dump với dataset lớn, nhưng phải đảm bảo database ở trạng thái consistent. Nếu dùng filesystem/cloud snapshot, cần hiểu journal, write concern, replica set state và crash recovery behavior.

Không copy nóng `dbPath` tùy tiện như backup đáng tin cậy nếu chưa có runbook chứng minh restore được.

## Restore Validation

Restore chưa test thì backup chỉ là hy vọng. Sau restore cần kiểm tra:

```javascript
db.adminCommand({ listDatabases: 1 })
db.<collection>.countDocuments()
db.<collection>.findOne()
db.<collection>.getIndexes()
```

Với app:

- app connect được bằng credential mới/đúng;
- index đã có đủ;
- role/permission đúng;
- dữ liệu sample khớp;
- replication/sharding health bình thường;
- RPO/RTO thực tế được ghi nhận.

## Related Pages

- [MongoDB Replica Set And Sharding](./02-replica-set-and-sharding.md)
- [Database Backup Restore Fundamentals](../../01-database-fundamentals/08-backup-restore-pitr-snapshot-logical-physical.md)
- [Backup Restore Validation](../../08-database-operations-patterns/02-backup-restore-validation.md)
