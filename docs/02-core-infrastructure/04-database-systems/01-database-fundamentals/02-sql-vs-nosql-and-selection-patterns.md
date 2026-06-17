# SQL vs NoSQL And Selection Patterns

## Overview

SQL và NoSQL không phải là "cũ vs mới". Đây là hai nhóm tradeoff khác nhau về data model, consistency, query flexibility, scale pattern và operational complexity.

## SQL

SQL database thường là relational database dùng schema rõ ràng và ngôn ngữ truy vấn chuẩn hóa. Điểm mạnh:

- Transaction và ACID mạnh.
- Constraint, foreign key, unique key.
- Query linh hoạt với join, aggregate, subquery.
- Tooling, backup, monitoring và skill market trưởng thành.

Điểm cần cân nhắc:

- Scale write ngang thường khó hơn read scale.
- Schema migration cần discipline.
- Query linh hoạt có thể tạo workload khó dự đoán nếu thiếu governance.

## NoSQL

NoSQL là nhóm rộng gồm key-value, document, wide-column, graph và search engine. Điểm mạnh:

- Scale-out theo workload cụ thể.
- Schema linh hoạt hơn.
- Tối ưu cho access pattern rõ.
- Phù hợp một số workload latency thấp hoặc dữ liệu rất lớn.

Điểm cần cân nhắc:

- Consistency và transaction có thể khác RDBMS.
- Query thường phải thiết kế theo access pattern.
- Application có thể phải xử lý nhiều logic hơn.
- Backup/restore và migration phụ thuộc engine nhiều hơn.

## Selection Questions

Trước khi chọn database, trả lời:

- Workload là OLTP, OLAP, cache, search, time-series hay event/log?
- Dữ liệu có quan hệ chặt và cần join không?
- Invariant nghiệp vụ có cần transaction mạnh không?
- Read/write ratio là gì?
- Query pattern cố định hay thay đổi thường xuyên?
- Dữ liệu tăng theo tenant, time, object hay event?
- RPO/RTO yêu cầu bao nhiêu?
- Team vận hành có kinh nghiệm với engine nào?

## Practical Rules

- Nếu chưa có lý do rõ để rời relational database, bắt đầu bằng RDBMS thường an toàn.
- Dùng cache để giảm latency đọc, không biến cache thành source of truth nếu chưa thiết kế durability.
- Dùng search engine cho search/analytics, không ép RDBMS làm full-text/search workload quá nặng nếu đã vượt ngưỡng.
- Dùng time-series database khi dữ liệu metric/event theo thời gian quá lớn và retention/downsampling là yêu cầu chính.
- Polyglot persistence chỉ đáng làm khi mỗi database giải quyết một workload rõ ràng.

## Anti-Patterns

- Chọn NoSQL chỉ vì "scale tốt hơn" nhưng không biết access pattern.
- Chọn managed/vendor database vì tiện ban đầu nhưng không có exit plan.
- Dùng một database cho mọi thứ: OLTP, cache, log, analytics, search.
- Không kiểm tra restore trước khi production.

## Related Pages

- [Database Models](./01-database-models-relational-document-kv-column-graph.md)
- [Replication, Sharding And Partitioning](./07-replication-sharding-partitioning.md)
