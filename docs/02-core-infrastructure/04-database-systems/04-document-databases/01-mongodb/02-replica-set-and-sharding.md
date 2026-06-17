# MongoDB Replica Set And Sharding

## Overview

MongoDB scale và HA dựa trên hai cơ chế khác nhau:

- **Replica set**: nhiều bản sao của cùng dữ liệu để HA, election và read scaling có kiểm soát.
- **Sharding**: chia dữ liệu theo shard key để scale-out dung lượng/throughput.

Replica set không thay thế sharding; sharding cũng không thay thế backup hoặc thiết kế consistency.

## Replica Set

Replica set có một primary nhận write và các secondary replicate oplog từ primary. Khi primary lỗi, các member đủ điều kiện sẽ election primary mới.

```text
client write -> primary -> oplog -> secondary apply
```

Các điểm vận hành:

- dùng odd voting members để tránh split vote;
- theo dõi replication lag;
- hiểu rõ write concern, ví dụ `majority` cho durability tốt hơn nhưng latency cao hơn;
- không dùng secondary read cho workload cần read-your-write nếu chưa hiểu read preference/read concern;
- backup từ secondary vẫn phải đảm bảo consistency và không làm secondary lag quá nhiều.

Lệnh quan sát:

```javascript
rs.status()
rs.printReplicationInfo()
rs.printSecondaryReplicationInfo()
```

## Replica Set Với TLS/Auth

Replica set production nên bật authentication và TLS cho cả client connection lẫn member-to-member traffic. Các node cần certificate/key phù hợp, hostname/SAN đúng và cấu hình trust thống nhất.

Checklist:

- bật auth trước khi expose network rộng;
- dùng user/role tối thiểu cho app và automation;
- certificate có vòng đời/rotation runbook;
- kiểm tra driver connection string trỏ đủ replica set member;
- test failover với client thật.

## Sharding

Sharded cluster thường có:

- shard: nơi chứa data partition;
- config server replica set: metadata cluster;
- `mongos`: router cho client;
- shard key: field quyết định document thuộc chunk/shard nào.

```text
client -> mongos -> shard theo shard key/chunk metadata
```

Shard key là quyết định kiến trúc. Shard key tốt thường có cardinality cao, phân phối đều và xuất hiện trong query routing. Shard key xấu tạo hotspot, jumbo chunk hoặc scatter-gather query.

## Sharding Risks

- monotonic key như timestamp tăng dần có thể dồn write vào một shard nếu không có chiến lược phù hợp;
- query không có shard key có thể fan-out tới nhiều shard;
- balancing/rebalancing tiêu tốn network và IO;
- unique constraint trong sharded collection có ràng buộc riêng theo shard key;
- backup/restore sharded cluster cần giữ consistency giữa shards và config server.

## Troubleshooting Topology

| Symptom | Kiểm tra |
|---|---|
| write latency tăng | primary health, replication lag, write concern, disk latency |
| election lặp lại | network giữa members, clock, disk stall, member priority/vote |
| read thấy dữ liệu cũ | read preference, secondary lag, read concern |
| shard hotspot | shard key distribution, chunk size, balancer state |
| query chậm trên sharded cluster | query có shard key không, scatter-gather, index trên từng shard |

## Related Pages

- [Backup And Restore](./04-backup-restore.md)
- [Troubleshooting](./06-troubleshooting.md)
- [Replication, Sharding And Partitioning](../../01-database-fundamentals/07-replication-sharding-partitioning.md)
