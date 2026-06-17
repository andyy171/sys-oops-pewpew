# Reliability And Disaster Recovery

Folder này chứa nguyên lý HA, failover, replication, DR và performance architecture ở mức thiết kế.

## Suggested Reading

- [HA And Failover Patterns](./01-ha-and-failover-patterns.md)
- [Load Balancer Clusters](./02-load-balancer-clusters.md)
- [Keepalived And HAProxy Pattern](./03-keepalived-haproxy-pattern.md)
- [Multi-Region Architecture](./04-multi-region-architecture.md)
- [Replication Strategies](./05-replication-strategies.md)
- [Caching, CDN And Read Replica](./06-caching-cdn-read-replica.md)
- [RTO/RPO Design](./07-rto-rpo-design.md)
- [IT Infrastructure Security And Resilience](./08-it-infrastructure-security-and-resilience.md)
- [Chaos Testing, Load Testing Và Experiments](./09-chaos-load-testing-and-experiments.md)
- [Distributed Fault Tolerance And Recovery](./10-distributed-fault-tolerance-and-recovery.md)

## Nguyên Tắc

- HA không thay thế backup.
- Replication không thay thế restore test.
- Multi-region không có ý nghĩa nếu data consistency và failback chưa được thiết kế.
- DR phải được đo bằng RTO/RPO và được diễn tập định kỳ.
