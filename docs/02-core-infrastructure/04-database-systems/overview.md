# Database Systems

Domain này chứa kiến thức về database ở góc nhìn hạ tầng và vận hành: mô hình dữ liệu, SQL/NoSQL, transaction, index, query planner, locking, replication, backup/restore, performance, HA, migration và troubleshooting.

## Chứa Gì

- Database fundamentals: data model, schema, table, index, transaction, isolation, lock, MVCC.
- Relational database: PostgreSQL, MySQL/MariaDB và các pattern vận hành RDBMS.
- Cache/key-value store: Redis, Memcached và các workload latency thấp.
- Document database: MongoDB và mô hình document-oriented.
- Distributed database: replication, sharding, partitioning, consistency và topology.
- Search/analytics database: Elasticsearch/OpenSearch, ClickHouse.
- Time-series database: Prometheus TSDB, InfluxDB.
- Operations patterns: capacity planning, backup/restore, migration, failover, performance troubleshooting, observability.

## Không Chứa Gì

- Managed database service theo vendor cụ thể nếu trọng tâm là service map, billing hoặc cloud console; đặt ở `04-cloud-edge/`.
- Application ORM pattern thuần code nếu không có tác động vận hành database.
- Storage backend internals như disk, filesystem, RAID, Ceph; đặt ở `03-storage-and-distributed-systems/`.

## Learning Path

1. [Database Fundamentals](./01-database-fundamentals/overview.md)
2. [Relational Databases](./02-relational-databases/overview.md)
3. [Cache And Key-Value Stores](./03-cache-and-key-value-stores/overview.md)
4. [Document Databases](./04-document-databases/overview.md)
5. [Distributed Databases](./05-distributed-databases/overview.md)
6. [Search And Analytics Databases](./06-search-and-analytics-databases/overview.md)
7. [Time-Series Databases](./07-time-series-databases/overview.md)
8. [Database Operations Patterns](./08-database-operations-patterns/overview.md)

## Intake Notes

- Kiến thức nạp từ tài liệu database vendor-specific chỉ được giữ ở mức nguyên lý chung.
- Không đưa tên dịch vụ, CLI, giới hạn sản phẩm, SKU hoặc behavior riêng của vendor vào note canonical nếu chưa được xác minh độc lập.
