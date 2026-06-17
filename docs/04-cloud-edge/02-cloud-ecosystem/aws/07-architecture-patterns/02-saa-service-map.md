# AWS SAA Service Map

## Overview

File thô `_inbox/AWS service.md` là một reference guide rộng cho AWS SAA, liệt kê nhiều dịch vụ từ compute, network, storage, database, security, operations đến CI/CD. Note này không lưu lại các chi tiết dễ thay đổi như runtime mới nhất, instance family mới nhất, quota hoặc rule pricing theo ngày. Thay vào đó, nó giữ service map ổn định để biết dịch vụ nào thuộc domain nào và khi nào nên đọc note chi tiết.

## Compute, Containers And Serverless

| Service | Vai trò | Khi nghĩ tới |
|---|---|---|
| EC2 | VM và compute có quyền kiểm soát OS | cần custom runtime, agent, networking hoặc licensing |
| Auto Scaling | co giãn số lượng instance | workload có traffic biến động |
| ELB | phân phối traffic tới target healthy | HA cho web/app/service |
| ECS | orchestration container native AWS | muốn chạy container với vận hành đơn giản hơn Kubernetes |
| ECR | registry image container | lưu, scan, replicate và lifecycle image |
| EKS | managed Kubernetes control plane | cần Kubernetes ecosystem/API |
| Fargate | serverless container runtime | không muốn quản lý node EC2 |
| Lambda | function/event-driven compute | xử lý ngắn, stateless, theo event |
| API Gateway | managed API front door | expose HTTP/API cho backend hoặc Lambda |

## Networking And Edge

| Service | Vai trò | Khi nghĩ tới |
|---|---|---|
| VPC | network boundary logic | subnet, route, security group, endpoint |
| Route 53 | DNS và traffic routing | public/private DNS, failover, weighted/latency routing |
| CloudFront | CDN và edge cache | static/dynamic content gần user |
| Direct Connect | private connectivity dedicated | hybrid network cần latency/bandwidth ổn định |
| VPN | encrypted tunnel qua internet | hybrid connectivity nhanh hơn, chi phí thấp hơn DX |
| Transit Gateway | hub routing nhiều VPC/on-prem | nhiều network cần kết nối có kiểm soát |

## Storage, Data And Databases

| Service | Vai trò | Khi nghĩ tới |
|---|---|---|
| S3 | object storage | static content, backup, data lake, archive |
| EBS | block volume cho EC2 | boot/data disk gắn vào instance |
| EFS | managed NFS file system | shared file giữa nhiều compute |
| FSx | managed file system chuyên biệt | Windows/Lustre/NetApp/OpenZFS use case |
| RDS | managed relational database | MySQL/PostgreSQL/MariaDB/Oracle/SQL Server managed |
| Aurora | cloud-native relational database | HA/performance/scale read cho MySQL/PostgreSQL compatible |
| DynamoDB | managed NoSQL key-value/document | high-scale lookup, serverless data access |
| ElastiCache | Redis/Memcached managed | cache, session, hot read path |
| Redshift | data warehouse | analytics SQL quy mô lớn |
| Kinesis | streaming data | event stream, real-time analytics, log ingestion |

## Identity, Security And Governance

| Service | Vai trò | Khi nghĩ tới |
|---|---|---|
| IAM | identity và authorization | user, role, policy, least privilege |
| Organizations | multi-account governance | SCP, account structure, consolidated management |
| KMS | key management | encryption key, envelope encryption, audit |
| Cognito | application identity | sign-up/sign-in cho app user |
| GuardDuty | threat detection managed | suspicious API, DNS, VPC Flow, EKS/RDS signals |
| Inspector | vulnerability scanning | EC2, container image, package exposure |
| Macie | sensitive data discovery | PII hoặc sensitive object trong S3 |
| IAM Access Analyzer | policy/access analysis | public/cross-account unintended access |
| Security Hub | security posture aggregation | gom finding và compliance view |

## Observability, Operations, IaC And Delivery

| Service | Vai trò | Khi nghĩ tới |
|---|---|---|
| CloudWatch | metrics, logs, alarms | health, performance, operational alert |
| CloudTrail | API audit trail | ai gọi API gì, lúc nào, từ đâu |
| Config | resource configuration history | drift, compliance, remediation |
| Systems Manager | fleet operations | session, patch, inventory, automation, parameter |
| CloudFormation | AWS-native IaC | stack, change set, StackSets |
| CodePipeline | release workflow | orchestrate source/build/deploy stages |
| CodeBuild | managed build | build/test/package trong container |
| CodeDeploy | deployment automation | EC2/ECS/Lambda deployment strategy |

## Event And Workflow

| Service | Vai trò | Khi nghĩ tới |
|---|---|---|
| SQS | queue decoupling | buffer, retry, backpressure |
| SNS | pub/sub notification | fan-out event tới nhiều subscriber |
| EventBridge | event bus/routing | decouple services bằng event rule |
| Step Functions | workflow orchestration | multi-step process, retry, branching, human/async flow |

## Reading Links

- [EC2, Auto Scaling And Load Balancing](../03-compute-containers-serverless/01-ec2-auto-scaling-load-balancing.md)
- [Lambda, API Gateway And Event-Driven Compute](../03-compute-containers-serverless/02-lambda-api-gateway-event-driven.md)
- [VPC, Subnets, Routing And Endpoints](../02-networking-edge/01-vpc-subnets-routing-endpoints.md)
- [Route 53, CloudFront And Global Traffic](../02-networking-edge/02-route53-cloudfront-global-traffic.md)
- [S3 Object Storage Patterns](../05-storage-data-databases/01-s3-object-storage-patterns.md)
- [RDS, Aurora, DynamoDB And Caching](../05-storage-data-databases/03-rds-aurora-dynamodb-caching.md)
- [CloudWatch, Config, CloudTrail And Cost](../06-observability-operations-cost/01-cloudwatch-config-cloudtrail-cost.md)
- [SAA-C03 Scenario Patterns](./01-saa-c03-scenario-patterns.md)
