# ECS And Fargate Container Architecture

## Overview

AWS có nhiều cách chạy container:

- ECS on EC2: AWS orchestrator, tự quản lý EC2 capacity.
- ECS on Fargate: chạy task không quản lý node.
- EKS: Kubernetes managed control plane.
- App Runner/Elastic Beanstalk: abstraction cao hơn cho một số app.

ECS/Fargate phù hợp khi muốn chạy container production mà không cần vận hành Kubernetes.

## ECS Concepts

| Khái niệm | Ý nghĩa |
| --- | --- |
| Cluster | logical group để chạy service/task |
| Task Definition | template mô tả container, CPU/memory, port, env, IAM role |
| Task | instance đang chạy của task definition |
| Service | duy trì số lượng task mong muốn và tích hợp LB |
| Capacity Provider | nguồn capacity: Fargate hoặc EC2 ASG |

## Fargate

Fargate chạy container mà không quản lý EC2 instance.

Ưu điểm:

- Ít day-2 node operation.
- Scale theo task/service.
- Tách biệt capacity ở mức task.
- Phù hợp microservice, API, worker, scheduled task.

Điểm cần chú ý:

- Giới hạn CPU/memory theo cấu hình Fargate.
- Networking dùng ENI trong VPC.
- Cost tính theo vCPU/memory/time.
- Cold start/task startup phụ thuộc image size và dependency.

## ECS Service Với ALB

Pattern web service:

```text
Route 53 / Client
  -> ALB
  -> Target Group
  -> ECS Service
  -> Fargate Tasks
```

Cần cấu hình:

- Task definition container port.
- Service desired count.
- Target group health check.
- Security group: ALB -> task.
- Subnet private/public tùy kiến trúc.

## IAM Roles

ECS có hai role quan trọng:

- **Task execution role**: ECS agent/Fargate dùng để pull image, ghi log.
- **Task role**: application trong container dùng để gọi AWS API.

Không nhét AWS access key vào image hoặc env nếu có thể dùng task role.

## Observability

Tối thiểu cần:

- Container logs vào CloudWatch Logs hoặc log pipeline.
- Metrics service/task CPU/memory.
- ALB target health.
- Deployment event.
- Error rate/latency ở application layer.

## Related Pages

- [Private Registry, Nexus, Harbor Và OCI Distribution](../../../../03-compute-and-orchestration/02-container-runtime/Private%20registry,%20NexusHarbor.md)
- [Lambda, EventBridge And SQS](../06-serverless-event-driven/01-lambda-eventbridge-and-sqs.md)
- [High Availability, Decoupling And Fault Tolerance](../09-architecture-resilience/01-high-availability-decoupling-and-fault-tolerance.md)
