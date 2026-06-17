# Architecture

Domain này là nơi giữ các nguyên lý thiết kế hệ thống có thể dùng lại qua nhiều platform: application architecture, system design, tradeoff, reliability, disaster recovery và SRE ở mức mental model.

## Cấu Trúc

```text
01-architecture/
├── 00-foundations/
├── 01-principles/
├── 02-tradeoffs/
├── 03-patterns/
├── 04-reliability-and-dr/
└── 05-sre-and-operations-principles/
```

## Chứa Gì

- Nguyên lý thiết kế: scalability, availability, consistency, stateless/stateful, service boundary.
- Tradeoff kiến trúc: consistency vs availability, latency vs throughput, control vs abstraction, scalability vs maintainability, PoC evaluation.
- Pattern hệ thống: caching, sharding, replication, load balancing, confidential computing, single-tenant data workload placement.
- Reliability và DR: HA, failover, multi-region, RTO/RPO, backup/restore strategy.
- SRE ở tầng nguyên lý: SLI/SLO, error budget, toil, incident lifecycle, operability.

## Không Chứa Gì

- OS, Windows Server, Linux, network, storage, database engine và hardware operations; đặt ở [Core Infrastructure](../02-core-infrastructure/overview.md).
- Container runtime, Kubernetes, service mesh và Kafka runtime; đặt ở [Compute And Orchestration](../03-compute-and-orchestration/overview.md).
- AWS/OpenStack/Azure/GCP service-specific behavior; đặt ở [Cloud Edge](../04-cloud-edge/overview.md).
- Git, CI/CD, Terraform, observability tool và automation command; đặt ở [Infrastructure Automation](../05-infrastructure-automation/overview.md).

## Learning Path

1. [Foundations](./00-foundations/overview.md)
2. [Architecture Principles](./01-principles/overview.md)
3. [Design Tradeoffs](./02-tradeoffs/overview.md)
4. [System Patterns](./03-patterns/overview.md)
5. [Reliability And DR](./04-reliability-and-dr/overview.md)
6. [SRE And Operations Principles](./05-sre-and-operations-principles/overview.md)

## Placement Rule

- Nếu note giải thích "nên thiết kế thế nào và vì sao", đặt ở đây.
- Nếu note giải thích "chạy lệnh nào, cấu hình service nào, debug log nào", đặt sang domain vận hành tương ứng.
- Nếu một note vừa có nguyên lý vừa có thao tác, giữ mental model ở đây và link sang runbook/tool note ở domain khác.
