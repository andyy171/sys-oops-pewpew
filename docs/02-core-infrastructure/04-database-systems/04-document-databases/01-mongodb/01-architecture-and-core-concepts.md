# MongoDB Architecture And Core Concepts

## Overview

MongoDB lưu dữ liệu trong **database -> collection -> document**. Document là BSON object, có `_id` duy nhất, có thể chứa field lồng nhau và array. Điểm mạnh của mô hình này là gom dữ liệu thường được đọc cùng nhau vào một document, giảm nhu cầu join runtime.

## Core Terms

| Term | Ý nghĩa |
|---|---|
| Database | Boundary logic chứa collection |
| Collection | Nhóm document, gần giống table nhưng schema linh hoạt hơn |
| Document | BSON record có `_id`, field, nested object và array |
| `_id` | Primary key mặc định; nếu không truyền, MongoDB tự tạo `ObjectId` |
| Cursor | Kết quả query có thể iterate, limit, skip, sort |
| Aggregation pipeline | Chuỗi stage xử lý dữ liệu như `$match`, `$project`, `$group`, `$sort`, `$lookup` |

## CRUD Mental Model

Các thao tác cơ bản:

```javascript
db.orders.insertOne({ order_id: "o-001", status: "new", total: 120 })
db.orders.find({ status: "new" }).pretty()
db.orders.updateOne({ order_id: "o-001" }, { $set: { status: "paid" } })
db.orders.deleteOne({ order_id: "o-001" })
```

`findOne()` dừng sau document đầu tiên phù hợp; `find()` trả cursor và có thể tiếp tục scan nếu không có index/selectivity tốt. Với collection lớn, query phải được thiết kế cùng index.

## Update, Upsert Và Bulk Write

Update operator như `$set`, `$inc`, `$push`, `$pull` giúp sửa field cụ thể thay vì replace toàn bộ document.

```javascript
db.users.updateOne(
  { email: "user@example.com" },
  { $set: { last_login_at: new Date() } },
  { upsert: true }
)
```

`upsert` tạo document nếu không tìm thấy match. Pattern này hữu ích cho idempotent write, nhưng filter phải đủ unique; filter lỏng có thể tạo document sai hoặc update nhầm.

Bulk write giúp giảm round trip khi cần ghi nhiều document:

```javascript
db.events.bulkWrite([
  { insertOne: { document: { event_id: "e-001", type: "login" } } },
  { updateOne: { filter: { event_id: "e-002" }, update: { $set: { processed: true } } } }
])
```

Với migration dữ liệu lớn, chia batch, theo dõi replication lag, write concern, lock/IO và có rollback plan.

## Aggregation Pipeline

Aggregation pipeline xử lý dữ liệu theo từng stage:

```javascript
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $group: { _id: "$customer_id", total: { $sum: "$total" } } },
  { $sort: { total: -1 } }
])
```

Các stage thường gặp:

- `$match`: lọc sớm để giảm dữ liệu đi tiếp.
- `$project`: chọn/biến đổi field.
- `$group`: aggregate theo key.
- `$unwind`: bung array thành nhiều record.
- `$lookup`: join với collection khác, cần cẩn trọng về cardinality và index.

Nếu pipeline lớn dùng nhiều memory, cần xem execution plan, index hỗ trợ và cân nhắc `allowDiskUse` theo chính sách vận hành.

## Storage Engine Notes

WiredTiger là storage engine phổ biến của MongoDB hiện đại. Các đặc điểm vận hành cần nhớ:

- document-level concurrency giúp nhiều write song song tốt hơn collection-level lock cũ;
- compression giảm dung lượng nhưng đổi lại CPU;
- update không nên được hiểu như ghi đè in-place đơn giản; storage engine có cơ chế versioning/page/cache riêng;
- cache, dirty page, checkpoint và disk latency ảnh hưởng trực tiếp tới write/read latency.

Khi đổi storage engine hoặc major storage layout, dùng dump/restore hoặc migration path được vendor hỗ trợ; không trỏ `dbPath` cũ sang engine khác.

## Related Pages

- [Replica Set And Sharding](./02-replica-set-and-sharding.md)
- [Index, Query And Performance](./03-index-query-and-performance.md)
- [Database Models](../../01-database-fundamentals/01-database-models-relational-document-kv-column-graph.md)
