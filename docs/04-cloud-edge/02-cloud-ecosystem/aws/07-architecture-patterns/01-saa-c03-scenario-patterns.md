# SAA-C03 Scenario Patterns

## Overview

File `_inbox/AWS SAA-03 Solution.txt` là ngân hàng scenario rất dài, có hơn 600 marker câu hỏi. Thay vì tạo hàng trăm note rời, trang này gom các pattern lặp lại để dùng khi ôn AWS SAA-C03 và khi thiết kế kiến trúc thật.

## Storage And Data Patterns

| Requirement | Pattern | Vì sao |
|---|---|---|
| Upload dữ liệu lớn từ nhiều châu lục vào S3 nhanh | S3 Transfer Acceleration + multipart upload | Tận dụng edge path và upload song song |
| Query log JSON trong S3 on-demand | Athena trực tiếp trên S3, Glue catalog nếu cần | Serverless, ít vận hành |
| Data lake cần dashboard | QuickSight connect S3/RDS datasets | Managed BI, chia sẻ dashboard theo user/group |
| Dữ liệu archive lâu dài ít truy cập | S3 lifecycle sang Glacier class phù hợp | Tối ưu storage cost theo access pattern |
| Shared file giữa nhiều EC2 | EFS hoặc FSx tùy Linux/Windows/Lustre | EBS không share across instance/AZ theo kiểu này |
| Large on-prem transfer, tránh nghẽn VPN | Snowball Edge | Offline transfer giảm áp lực network |
| Continuous file sync S3/EFS | DataSync changed-data mode | Ít custom code, đồng bộ incremental |

## Network And Edge Patterns

| Requirement | Pattern | Vì sao |
|---|---|---|
| Private subnet cần truy cập S3 không qua internet | S3 gateway endpoint | Private path, không cần NAT/IGW |
| Private service/API dùng nội bộ nhiều VPC/account | PrivateLink/interface endpoint | Expose service riêng tư, giảm coupling network |
| Private subnet cần outbound internet HA | NAT Gateway theo AZ + route cùng AZ | Tránh phụ thuộc NAT ở AZ khác |
| Global static + dynamic web latency thấp | CloudFront nhiều origin: S3 + ALB/API | Edge cache và origin routing |
| Multi-region failover | Route 53 failover/latency routing + health checks | DNS-level steering |
| Inline inspection bằng appliance | Gateway Load Balancer | Scale appliance insertion ít vận hành hơn |

## Compute And Integration Patterns

| Requirement | Pattern | Vì sao |
|---|---|---|
| Web tier stateless HA | ALB + Auto Scaling Group across AZ | Tự thay instance lỗi và phân phối traffic |
| Peak traffic biết trước | Scheduled scaling | Scale trước khi metric phản ứng |
| Worker xử lý job biến động | SQS queue + ASG scale theo queue depth | Decouple producer/consumer |
| Một message cần nhiều consumer | SNS topic fanout tới nhiều SQS queue | Mỗi consumer xử lý độc lập |
| Xử lý ảnh upload async | S3 event -> SQS -> Lambda | Durable, stateless, retry tốt |
| Thứ tự đơn hàng phải giữ | SQS FIFO + consumer | Ordering theo message group |
| Container ít muốn quản lý node | ECS/Fargate + service auto scaling | Managed runtime, ít vận hành EC2 |

## Web Application Production Guardrails

Một web app chạy sau load balancer không tự động trở thành HA nếu instance vẫn giữ state cục bộ. Với WordPress hoặc app tương tự, cần kiểm tra:

- Upload, plugin, cache file và session có nằm trên local disk không.
- Database đã được tách sang managed database hoặc cụm database có backup/restore rõ ràng chưa.
- Web tier có thể bị terminate/recreate mà không mất dữ liệu hoặc config không.
- Security group có đi theo luồng traffic tối thiểu: internet -> ALB, ALB -> web tier, web tier -> database.
- Health check đo đúng endpoint ứng dụng, không chỉ đo port mở.

Pattern an toàn hơn:

```text
User
-> DNS / CDN nếu cần
-> ALB
-> stateless web tier across AZ
-> managed database
-> object/file storage cho upload/static state
```

Nếu vẫn cần lưu file dùng chung, chọn storage phù hợp như S3 cho object/static content hoặc EFS/FSx cho shared filesystem. Không dựa vào EBS local-to-instance cho dữ liệu phải sống qua thay instance.

## Database Patterns

| Requirement | Pattern | Vì sao |
|---|---|---|
| MySQL/PostgreSQL cần HA ít sửa app | RDS Multi-AZ | Managed failover |
| Read-heavy relational workload | Read replica/Aurora replica + cache | Tách read load khỏi primary |
| Lambda/app scale nhanh làm cạn DB connection | RDS Proxy | Connection pooling |
| Credential DB cần rotate | Secrets Manager rotation | Giảm vận hành secret dài hạn |
| DynamoDB traffic unpredictable | On-demand capacity | Không cần capacity planning chi tiết |
| DynamoDB workload định kỳ biết RCU/WCU | Provisioned capacity | Tối ưu cost khi tải đoán trước |

## Security, Governance And Cost Patterns

| Requirement | Pattern | Vì sao |
|---|---|---|
| Chỉ account trong AWS Organization truy cập S3 | `aws:PrincipalOrgID` trong bucket policy | Không phải liệt kê từng account |
| Chuẩn hóa tag ứng dụng | Organizations tag policy + Config/IaC guardrail | Governance nhiều account |
| Audit infrastructure change | CloudFormation/IaC + AWS Config + CloudTrail | Tự động hóa và có lịch sử thay đổi |
| Detect config drift/noncompliance | AWS Config rule | Theo dõi resource configuration |
| Enforce encryption at rest | KMS + Config + remediation | Phát hiện và sửa tự động |
| Cost spike bất thường | Cost Anomaly Detection | Tối ưu cho phát hiện spending bất thường |
| EBS snapshot cost tăng | Data Lifecycle Manager retention | Xóa snapshot cũ theo policy |

## Exam Heuristics

- "Least operational overhead" thường nghiêng về managed/serverless service.
- "Without internet" với S3/DynamoDB trong VPC thường là VPC endpoint.
- "Shared files across EC2" thường là EFS/FSx, không phải EBS riêng lẻ.
- "Read scaling" khác "high availability": RDS Multi-AZ là HA; read replica/Aurora replica là read scaling.
- "Known peak" nên nghĩ scheduled scaling; "unpredictable spike" nên nghĩ queue/auto scaling/serverless.
- "Global low latency" thường có CloudFront hoặc Route 53 latency/geolocation.
- "Need exact ordering" thường có FIFO queue, nhưng phải hiểu throughput/order trade-off và verify current service quota.

## Related Pages

- [S3 Object Storage Patterns](../05-storage-data-databases/01-s3-object-storage-patterns.md)
- [VPC, Subnets, Routing And Endpoints](../02-networking-edge/01-vpc-subnets-routing-endpoints.md)
- [EC2, Auto Scaling And Load Balancing](../03-compute-containers-serverless/01-ec2-auto-scaling-load-balancing.md)
- [Lambda, API Gateway And Event-Driven Compute](../03-compute-containers-serverless/02-lambda-api-gateway-event-driven.md)
- [CloudWatch, Config, CloudTrail And Cost](../06-observability-operations-cost/01-cloudwatch-config-cloudtrail-cost.md)
