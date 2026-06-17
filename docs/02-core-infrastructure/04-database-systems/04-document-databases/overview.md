# Document Databases

Document database lưu dữ liệu theo document semi-structured, thường là JSON/BSON. Mô hình này phù hợp khi schema thay đổi nhanh, aggregate root tự nhiên là một document, và ứng dụng cần đọc/ghi theo object hơn là join quan hệ phức tạp.

## Reading Order

1. [MongoDB](./01-mongodb/overview.md)

## Placement Notes

- Đặt kiến thức engine-specific như replica set, sharding, index, aggregation pipeline, `mongodump` và authorization vào thư mục MongoDB.
- Đặt khái niệm chung như document model, SQL vs NoSQL, consistency trade-off vào `../01-database-fundamentals/`.
- Không giả định document database tự động giải quyết HA hoặc consistency; topology, write concern, read concern, backup và restore vẫn phải thiết kế rõ.
