# Database Models: Relational, Document, KV, Column, Graph

## Overview

Database model quyết định cách dữ liệu được biểu diễn, truy vấn, ràng buộc và scale. Chọn model sai thường tạo nợ kỹ thuật lớn hơn chọn sai engine, vì application sẽ gắn chặt vào cách dữ liệu được mô hình hóa.

## Core Terms

- **Data**: thông tin thô được lưu và xử lý.
- **Database**: tập dữ liệu được tổ chức để truy cập và quản lý.
- **DBMS**: phần mềm quản lý database, chịu trách nhiệm lưu trữ, truy vấn, transaction, security và recovery.
- **Database system**: DBMS cộng với data, schema, workload, user, application và hạ tầng vận hành.
- **Schema**: cấu trúc logic của dữ liệu: table, field, type, constraint, relationship.
- **Instance**: tiến trình hoặc cụm tiến trình đang chạy để phục vụ database.

## Relational Model

Relational database tổ chức dữ liệu thành table, row, column và relationship. Nó mạnh ở:

- Dữ liệu có cấu trúc rõ.
- Cần constraint, foreign key, transaction và consistency cao.
- Query phức tạp với join, filter, aggregate.
- OLTP như order, billing, inventory, account, core business records.

Điểm cần chú ý là schema migration, index design và join cost khi dữ liệu lớn.

## Row Store Và Column Store

Row store và column store là cách tổ chức dữ liệu vật lý, không chỉ là kiểu database logic. Cùng một table có thể được nhìn như row/column ở tầng SQL, nhưng engine có thể lưu theo row hoặc theo column để tối ưu workload khác nhau.

| Kiểu lưu trữ | Phù hợp | Tradeoff |
| --- | --- | --- |
| Row store | OLTP, point lookup, đọc/ghi nguyên row, transaction ngắn | aggregate theo vài column có thể đọc nhiều dữ liệu thừa |
| Column store | OLAP, scan ít column trên nhiều row, aggregate/reporting, compression | đọc/ghi nguyên row hoặc query cần nhiều column có thể tốn ghép dữ liệu |

Trong row store, một page thường chứa nhiều row với nhiều column của từng row. Khi query tìm được row, engine thường có sẵn nhiều column của row đó. Điều này hợp với workload như order, account, inventory, user profile và transaction nghiệp vụ.

Trong column store, dữ liệu cùng column được đặt gần nhau. Query như `SUM(salary)` hoặc dashboard chỉ đọc vài metric trên rất nhiều row sẽ giảm I/O và nén tốt hơn, vì các giá trị trong cùng column thường có kiểu và phân bố giống nhau.

Không có kiểu nào "tốt hơn" tuyệt đối:

- `SELECT * WHERE id = ...` thường tự nhiên hơn với row store.
- `SELECT SUM(metric) WHERE date BETWEEN ...` thường tự nhiên hơn với column store.
- Query cần nhiều column trong column store có thể phải đọc nhiều segment/column rồi ghép lại.
- Write/update row đơn lẻ trong column store thường phức tạp hơn row store.

## Document Model

Document database lưu dữ liệu dạng document như JSON/BSON. Nó phù hợp khi:

- Entity có cấu trúc thay đổi theo loại đối tượng.
- Application thường đọc/ghi cả document.
- Cần evolve schema nhanh.

Rủi ro chính là duplicate data, thiếu transaction cross-document ở một số hệ thống, và query/index khó kiểm soát nếu document quá linh hoạt.

## Key-Value Model

Key-value store map key sang value. Nó phù hợp cho:

- Cache.
- Session.
- Rate limit.
- Feature flag.
- Lookup latency thấp.

Model này nhanh vì đơn giản, nhưng không phù hợp cho query quan hệ hoặc ad-hoc analytics phức tạp.

## Wide-Column Model

Wide-column database tổ chức dữ liệu theo partition key, clustering key và column family. Nó phù hợp cho write-heavy workload, dữ liệu phân tán lớn và query pattern biết trước.

Thiết kế tốt bắt đầu từ access pattern. Nếu cần join tùy ý như RDBMS, wide-column thường không phải lựa chọn tự nhiên.

## Graph Model

Graph database biểu diễn node, edge và property. Nó phù hợp khi relationship là trung tâm của bài toán:

- Social graph.
- Recommendation.
- Fraud detection.
- Network/path analysis.
- Dependency graph.

Graph mạnh ở traversal, nhưng cần kiểm soát cardinality và query depth để tránh chi phí tăng mạnh.

## Selection Pattern

| Câu hỏi | Gợi ý |
| --- | --- |
| Dữ liệu có schema rõ và cần transaction mạnh không? | relational |
| Cần cache/lookup latency thấp không? | key-value |
| Entity linh hoạt, đọc/ghi theo document không? | document |
| Dữ liệu rất lớn, query pattern cố định theo key không? | wide-column |
| Relationship/path là nghiệp vụ chính không? | graph |

## Related Pages

- [SQL vs NoSQL And Selection Patterns](./02-sql-vs-nosql-and-selection-patterns.md)
- [Transaction, ACID And Isolation Levels](./03-transaction-acid-isolation-levels.md)
