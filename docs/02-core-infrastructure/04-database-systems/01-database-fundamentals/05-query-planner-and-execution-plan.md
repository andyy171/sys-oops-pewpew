# Query Planner And Execution Plan

## Overview

Query planner chọn cách thực thi SQL: dùng index hay scan, join theo thứ tự nào, dùng nested loop/hash/merge join, sort ở đâu và estimate bao nhiêu row. Khi query chậm, execution plan là bản đồ đầu tiên cần đọc.

## Planner Inputs

Planner thường dựa vào:

- SQL text và predicate.
- Table statistics: row count, cardinality, histogram.
- Index hiện có.
- Cost model của engine.
- Memory/work_mem/sort buffer.
- Data distribution và partition.

Statistics sai thường dẫn đến plan sai.

## Common Operations

| Operation | Ý nghĩa | Cẩn thận |
| --- | --- | --- |
| Sequential/table scan | quét nhiều hoặc toàn bộ table | có thể đúng nếu query trả phần lớn dữ liệu |
| Index scan | đọc qua index rồi fetch row | tốt khi predicate selective |
| Index-only scan | đọc đủ dữ liệu từ index | cần visibility/statistics phù hợp tùy engine |
| Nested loop join | lặp outer rows để tìm inner rows | tốt khi outer nhỏ và inner có index |
| Hash join | build hash table để join | cần memory, có thể spill ra disk |
| Merge join | join hai input đã sort | tốt khi input sorted hoặc có index phù hợp |
| Sort | sắp xếp dữ liệu | tốn memory/disk khi result lớn |

## Reading A Plan

Khi đọc plan, tập trung:

- Estimate rows so với actual rows.
- Operation nào tốn thời gian/I/O nhất.
- Có scan lớn bất ngờ không.
- Join order có hợp lý không.
- Sort/hash có spill ra disk không.
- Predicate có dùng được index không.

## Tuning Pattern

1. Xác nhận query chậm thật bằng latency percentile và frequency.
2. Lấy execution plan có actual runtime nếu engine hỗ trợ.
3. Kiểm tra statistics và row estimate.
4. Kiểm tra index phù hợp với predicate/join/sort.
5. Rewrite query nếu predicate không sargable hoặc join/filter sai hướng.
6. Test với dữ liệu gần production, không chỉ sample nhỏ.
7. Theo dõi tác động tới write path và các query khác.

## Anti-Patterns

- Thêm index theo cảm tính.
- Tối ưu query hiếm khi chạy nhưng bỏ qua query chạy hàng nghìn lần/phút.
- Dùng `SELECT *` trong path latency-sensitive.
- Để pagination offset lớn quét quá nhiều dữ liệu.
- Không cập nhật statistics sau bulk load hoặc data distribution thay đổi lớn.

## Pagination Pattern

`OFFSET` lớn không miễn phí: database vẫn phải đếm hoặc bỏ qua nhiều row trước khi trả về page cần lấy.

```sql
SELECT *
FROM posts
ORDER BY id
LIMIT 20 OFFSET 1000000;
```

Với bảng lớn, ưu tiên keyset/cursor pagination khi workflow không cần nhảy ngẫu nhiên tới page xa:

```sql
SELECT *
FROM posts
WHERE id > :last_seen_id
ORDER BY id
LIMIT 20;
```

Sort key cần ổn định và có index phù hợp, ví dụ `(created_at, id)` khi sắp theo thời gian nhưng cần tie-breaker duy nhất.

## Related Pages

- [Index: B-Tree, LSM, Hash, Full-Text](./04-index-btree-lsm-hash-fulltext.md)
- [Database Performance](./09-database-performance-latency-throughput-iops.md)
