# MongoDB Troubleshooting

## Overview

Troubleshooting MongoDB nên đi từ symptom tới lớp lỗi: client connection, auth/TLS, query/index, replication, sharding, storage/disk hoặc resource. Tránh bắt đầu bằng restart nếu chưa đọc log và status.

## Quick Triage

```javascript
db.adminCommand({ ping: 1 })
db.serverStatus()
rs.status()
db.currentOp()
```

Trên host:

```bash
systemctl status mongod
journalctl -u mongod
ss -lntp
df -h
iostat -xz 1
```

## Symptom Map

| Symptom | Kiểm tra trước |
|---|---|
| client không connect | bind IP, firewall, DNS, TLS, authSource, user/password, replica set name |
| query chậm | `explain`, index, collection scan, sort memory, `$lookup`, working set/cache |
| write chậm | write concern, primary disk latency, journaling, index count, replication lag |
| replication lag | secondary CPU/IO, network, oplog window, long-running operation |
| election liên tục | node health, heartbeat/network, disk stall, clock, config votes/priority |
| shard imbalance | shard key, chunk distribution, balancer, jumbo chunk |
| backup restore lỗi | version/tool mismatch, auth/role, dump consistency, sharded metadata |

## Query Chậm

Luồng đọc:

```javascript
db.collection.find(<filter>).explain("executionStats")
db.collection.getIndexes()
db.collection.stats()
```

Nếu thấy `COLLSCAN`, cần hỏi:

- query có filter đúng field không;
- có index phù hợp không;
- index có selective không;
- sort/group có được index hỗ trợ không;
- projection có làm giảm network nhưng vẫn fetch quá nhiều document không.

## Replication Và Election

```javascript
rs.status()
rs.printSecondaryReplicationInfo()
```

Điểm cần chú ý:

- state của từng member;
- primary hiện tại;
- optime/lag;
- member unreachable;
- election reason trong log.

Nếu replication lag tăng sau index build/bulk migration/backup, cần giảm tải hoặc tạm dừng batch thay vì để oplog window bị vượt.

## Storage Và Disk

MongoDB rất nhạy với disk latency. Khi latency tăng:

- kiểm tra disk full/inode;
- kiểm tra IOPS/throughput/saturation;
- kiểm tra filesystem mount option và underlying storage;
- xem WiredTiger cache pressure;
- kiểm tra checkpoint/journal stall trong log.

## Safety

- Không chạy `dropDatabase`, `dropCollection`, resync member hoặc xóa `dbPath` nếu chưa có backup và người chịu trách nhiệm xác nhận.
- Với replica set, thao tác trên primary/secondary có tác động khác nhau; luôn xác nhận node role trước.
- Với sharded cluster, không sửa metadata thủ công nếu không có runbook chuyên biệt.

## Related Pages

- [MongoDB Operations](./05-operations.md)
- [Index, Query And Performance](./03-index-query-and-performance.md)
- [Database Incident Response Patterns](../../08-database-operations-patterns/07-database-incident-response-patterns.md)
