# MongoDB Index, Query And Performance

## Overview

MongoDB query performance phụ thuộc vào document model, index và access pattern. Index giúp tránh collection scan, hỗ trợ sort và enforce uniqueness, nhưng index cũng tiêu tốn RAM/disk và làm write chậm hơn.

## Index Types

| Index | Khi dùng |
|---|---|
| `_id` index | Tự có trên `_id`, không drop được trong workload bình thường |
| Single-field | Query/filter/sort theo một field |
| Compound | Query theo nhiều field hoặc filter + sort |
| Unique | Enforce uniqueness |
| Partial | Chỉ index document match filter; nên ưu tiên hơn sparse cho rule rõ |
| Sparse | Chỉ index document có field; hữu ích cho optional field nhưng dễ gây nhầm |
| Hashed | Equality lookup hoặc shard key hashed; không phù hợp range query |
| `2dsphere` | Query geospatial GeoJSON |

## Create, List, Drop

```javascript
db.orders.createIndex({ customer_id: 1, created_at: -1 })
db.orders.getIndexes()
db.orders.dropIndex("customer_id_1_created_at_-1")
```

Compound index cần chú ý thứ tự field. Query theo prefix của index thường dùng index tốt hơn query chỉ dùng field phía sau. Sort cũng cần match direction/order phù hợp, trừ các trường hợp reverse toàn bộ direction được planner hỗ trợ.

## Sparse, Partial Và Unique

Unique index trên field optional có thể fail nếu nhiều document thiếu field vì giá trị thiếu/null bị xem như entry trùng trong nhiều tình huống. Cần cân nhắc partial index:

```javascript
db.users.createIndex(
  { email: 1 },
  {
    unique: true,
    partialFilterExpression: { email: { $exists: true } }
  }
)
```

Partial index biểu đạt điều kiện rõ hơn sparse index vì filter có thể dựa trên nhiều field/điều kiện, không chỉ sự tồn tại của indexed field.

## Query And Aggregation Performance

Checklist:

- `$match` càng sớm càng tốt trong aggregation pipeline.
- Projection giảm dữ liệu trả về nhưng không thay thế index.
- `$lookup` cần index ở field join và kiểm soát cardinality.
- `skip` lớn có thể đắt; pagination theo range/keyset thường ổn định hơn.
- Sort không có index có thể dùng nhiều memory.
- Index nhiều quá làm write chậm và tăng working set.

Lệnh cần dùng khi tối ưu:

```javascript
db.orders.find({ customer_id: "c-001" }).sort({ created_at: -1 }).explain("executionStats")
db.orders.aggregate([ { $match: { status: "paid" } } ], { explain: true })
```

## Bulk Migration Performance

Khi chuyển đổi type/field cho nhiều document, dùng bulk write theo batch thay vì update từng document với nhiều round trip. Cần giới hạn batch size, theo dõi replication lag và chuẩn bị resume marker.

```javascript
db.users.bulkWrite([
  {
    updateOne: {
      filter: { _id: ObjectId("000000000000000000000001") },
      update: { $set: { migrated: true } }
    }
  }
])
```

## Troubleshooting Query Chậm

| Dấu hiệu | Hướng kiểm tra |
|---|---|
| `COLLSCAN` | thiếu index hoặc query không match index |
| `IXSCAN` nhưng vẫn chậm | index không selective, fetch nhiều document, sort/group đắt |
| write latency tăng sau khi thêm index | số lượng index, disk latency, replication lag |
| aggregation OOM/chậm | stage order, `$group` cardinality, `$lookup`, `allowDiskUse`, index |
| sharded query chậm | scatter-gather, thiếu shard key trong filter |

## Related Pages

- [MongoDB Architecture And Core Concepts](./01-architecture-and-core-concepts.md)
- [Database Index Fundamentals](../../01-database-fundamentals/04-index-btree-lsm-hash-fulltext.md)
- [Database Performance](../../01-database-fundamentals/09-database-performance-latency-throughput-iops.md)
