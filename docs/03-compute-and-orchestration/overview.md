# Compute And Orchestration

Domain này chứa tầng runtime/platform chạy workload: compute model, virtualization, container runtime, Kubernetes/container orchestration, service discovery/mesh, workload identity và messaging/streaming platform.

## Chứa Gì

- Compute foundation: VM, bare metal scheduling model, accelerator/GPU ở mức chạy workload.
- Virtualization: hypervisor concept, KVM/QEMU/libvirt, VMware và VM lifecycle.
- Container runtime: image, Docker, containerd/CRI, registry, volume, network mode và image security.
- Orchestration: Kubernetes, controller, scheduler, workload object, rollout, CNI/CSI và cluster operations.
- Service discovery, service mesh, secrets/workload identity khi chúng phục vụ runtime workload.
- Kafka/RabbitMQ hoặc messaging platform khi note nói về broker, topic, partition, consumer group, lag và operations.

## Không Chứa Gì

- Linux host internals, NIC/disk/hardware hoặc bare metal OS install; đặt ở [Core Infrastructure](../02-core-infrastructure/overview.md).
- AWS/OpenStack/Azure/GCP service implementation; đặt ở [Cloud Edge](../04-cloud-edge/overview.md).
- CI/CD release workflow, Terraform, Prometheus/Grafana và security program; đặt ở [Infrastructure Automation](../05-infrastructure-automation/overview.md).

## Suggested Reading

- [Compute Platforms](./01-compute-platforms/overview.md)
- [Node.js And Express Runtime Operations](./01-compute-platforms/02-nodejs-express-runtime-operations.md)
- [Docker Overview](./02-container-runtime/01-docker/overview.md)
- [Docker Commands](./02-container-runtime/01-docker/00-docker-commands.md)
- [Docker Practice And Operations Patterns](./02-container-runtime/06-docker-practice-and-operations-patterns.md)
- [Docker Compose Services](./02-container-runtime/05-Docker%20Compose%20services.md)
- [Docker Network Modes](./02-container-runtime/03-Network%20mode%20bridge,%20host,%20overlay.md)
- [Docker Volumes](./02-container-runtime/04-Volumes,%20Bind%20mount,%20tmpfs.md)
- [Container Orchestration](./03-container-orchestration/overview.md)
- [Kubernetes](./03-container-orchestration/01-kubernetes/overview.md)
- [Gardener](./03-container-orchestration/04-gardener/overview.md)
- [Private Registry, Nexus, Harbor](./02-container-runtime/Private%20registry,%20NexusHarbor.md)
- [Kafka Components](./06-messaging-and-streaming/01-kafka/01-core-concepts/components.md)
- [AMQP And RabbitMQ Core Concepts](./06-messaging-and-streaming/02-rabbitmq/01-amqp-rabbitmq-core-concepts.md)

## Ghi Chú Refactor

Root hiện có trùng numbering giữa `01-compute-platforms` và `01-virtualization`. Khi dọn sâu, nên chuẩn hóa dần theo hướng:

```text
01-compute-foundations
02-virtualization
03-container-runtime
04-container-orchestration
05-service-discovery-and-mesh
06-secrets-and-identity
07-messaging-and-streaming
```

- Không rename hàng loạt khi chưa kiểm tra link trong toàn vault.
- `02-container-runtime` nên được gom dần theo nhóm: container fundamentals, Docker, containerd/CRI, image build/security và troubleshooting.
- Kubernetes hiện là phần mạnh nhất; các note operations như quick reference, observability và scheduling nên được đặt đúng nhánh operations/core-object khi dọn link.
- Kafka nên bổ sung dần topic/partition/replica/ISR, producer/consumer, offset/retention/commit, KRaft, consumer lag, Kafka Connect, Schema Registry và Debezium.
