# AWS

AWS folder này là knowledge area riêng cho cloud architecture, vận hành và luyện AWS SAA-C03. Cấu trúc mới ưu tiên domain rõ ràng để dễ nạp thêm note từ sách, lab, scenario hoặc troubleshooting mà không tạo một file tổng hợp quá dài.

## Reading Order

1. [Fundamentals](./00-fundamentals/overview.md)
2. [Identity, Security And Governance](./01-identity-security-governance/overview.md)
3. [Networking And Edge](./02-networking-edge/overview.md)
4. [Compute, EC2 And Auto Scaling](./03-compute-ec2-autoscaling/overview.md)
5. [Infrastructure As Code And Automation](./04-infrastructure-as-code-automation/overview.md)
6. [Storage, Data And Databases](./05-storage-data-databases/overview.md)
7. [Serverless And Event Driven](./06-serverless-event-driven/overview.md)
8. [Containers, ECS And Fargate](./07-containers-ecs-fargate/overview.md)
9. [Observability, Operations And Cost](./08-observability-operations-cost/overview.md)
10. [Architecture And Resilience](./09-architecture-resilience/overview.md)

## Canonical Folder Map

```text
aws/
├── 00-fundamentals/
├── 01-identity-security-governance/
├── 02-networking-edge/
├── 03-compute-ec2-autoscaling/
├── 04-infrastructure-as-code-automation/
├── 05-storage-data-databases/
├── 06-serverless-event-driven/
├── 07-containers-ecs-fargate/
├── 08-observability-operations-cost/
├── 09-architecture-resilience/
└── 04-issues-troubleshooting/
```

## Placement Rule

- Service concept hoặc mental model nền tảng đi vào domain service tương ứng.
- IaC/automation AWS-native đi vào `04-infrastructure-as-code-automation/`.
- Lambda, SQS, EventBridge đi vào `06-serverless-event-driven/`.
- ECS/Fargate/container workload đi vào `07-containers-ecs-fargate/`.
- HA, fault tolerance, decoupling, RTO/RPO đi vào `09-architecture-resilience/`.
- Troubleshooting cụ thể giữ trong `04-issues-troubleshooting/`.
- Không hard-code pricing, quota hoặc service limit trong note dài hạn; kiểm tra AWS docs hiện hành khi triển khai thật.
