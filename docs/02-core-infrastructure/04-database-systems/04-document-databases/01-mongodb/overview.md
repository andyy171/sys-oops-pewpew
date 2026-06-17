# MongoDB

MongoDB là document database dùng BSON document, collection và index để phục vụ workload đọc/ghi theo document. Với góc nhìn hạ tầng, cần hiểu ba lớp: mô hình dữ liệu, topology HA/scale, và vận hành backup/security/performance.

## Reading Order

1. [Architecture And Core Concepts](./01-architecture-and-core-concepts.md)
2. [Replica Set And Sharding](./02-replica-set-and-sharding.md)
3. [Index, Query And Performance](./03-index-query-and-performance.md)
4. [Backup And Restore](./04-backup-restore.md)
5. [Operations](./05-operations.md)
6. [Troubleshooting](./06-troubleshooting.md)

## Production Mental Model

- Document design quyết định phần lớn hiệu năng; index chỉ cứu được query pattern hợp lý.
- Replica set cung cấp HA và election, nhưng cần write concern/read concern phù hợp.
- Sharding giải quyết scale-out theo shard key; shard key sai có thể tạo hotspot rất khó sửa.
- Backup phải được test restore, đặc biệt với replica set/sharded cluster.
- Authentication, authorization, TLS và network exposure phải bật từ đầu, không thêm muộn sau khi dữ liệu đã nhạy cảm.
