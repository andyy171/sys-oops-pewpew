# AWS Interview Service Map

Note này chuyển hóa `_inbox/Aws.docx`, một tài liệu Q&A phỏng vấn AWS khá rộng và có nhiều câu trùng/lỗi diễn đạt. Thay vì giữ dạng hỏi-đáp dài, note này gom các ý thành bản đồ dịch vụ và câu hỏi tư duy thường gặp.

## Cloud Foundation

Các câu hỏi nền thường xoay quanh:

- AWS là public cloud cung cấp compute, storage, network, database, analytics, security và managed services.
- Cloud service model: IaaS, PaaS, SaaS.
- Deployment model: public, private, hybrid.
- AWS Global Infrastructure: Region, Availability Zone, Edge Location.
- Cách truy cập AWS: Management Console, CLI, SDK, API và IaC.

Mental model quan trọng: luôn hỏi service có scope ở đâu.

| Scope | Ví dụ | Ý nghĩa thiết kế |
|---|---|---|
| Global | IAM, Route 53, CloudFront | không gắn vào một AZ cụ thể |
| Regional | VPC, Lambda, DynamoDB, S3 bucket name global nhưng bucket được tạo trong Region | cần chọn Region cho latency/compliance |
| AZ/Zonal | EC2 instance, EBS volume, subnet | cần multi-AZ để HA |

## EC2, AMI, Key Pair Và Pricing

Các điểm hay hỏi:

- EC2 là compute VM theo nhu cầu.
- AMI là image template để launch instance.
- Key pair dùng để SSH vào Linux instance hoặc giải mã Windows password.
- Public IP của EC2 có thể đổi sau stop/start; Elastic IP dùng khi cần địa chỉ tĩnh.
- Instance store là ephemeral; EBS là block storage persistent.

Pricing model nên nhớ ở mức khái niệm:

| Model | Dùng khi |
|---|---|
| On-Demand | workload ngắn hạn, chưa đoán trước |
| Reserved Instance / Savings Plan | workload ổn định, cam kết dùng lâu |
| Spot | batch/stateless, chịu được interruption |
| Dedicated Host/Instance | yêu cầu license/compliance/isolation đặc biệt |

Không hard-code giá, quota hoặc instance family limit trong note dài hạn; luôn kiểm tra AWS docs khi triển khai thật.

## Auto Scaling Và Load Balancing

Auto Scaling Group giữ số lượng instance theo desired/min/max và policy.

Thành phần:

- Launch Template hoặc Launch Configuration.
- Auto Scaling Group.
- Scaling policy.
- Health check.
- Lifecycle hook.
- Load Balancer target group nếu workload web/service.

Các câu hỏi tư duy:

- Nếu traffic tăng dần đã dự báo, dùng scheduled scaling hoặc tăng capacity trước chiến dịch.
- Nếu workload ổn định và cần HA, trải instance qua nhiều AZ và gắn Load Balancer.
- Nếu instance unhealthy, ASG có thể terminate và thay thế.
- Connection draining/deregistration delay giúp request cũ hoàn tất trước khi instance rời khỏi load balancer.

## Storage: S3, EBS, EFS

| Service | Loại storage | Dùng khi |
|---|---|---|
| S3 | object storage | static asset, backup, data lake, log archive |
| EBS | block storage | volume cho EC2, database, filesystem một node |
| EFS | file storage | NFS shared filesystem cho nhiều instance |
| FSx | managed file storage chuyên biệt | Windows File Server, Lustre, NetApp ONTAP, OpenZFS tùy nhu cầu |

S3 cần nắm:

- bucket/object/key;
- storage class và lifecycle;
- versioning;
- encryption với SSE-S3, SSE-KMS hoặc client-side encryption;
- bucket policy/IAM policy;
- replication;
- pre-signed URL cho truy cập tạm thời.

EBS cần nắm:

- volume gắn với AZ;
- snapshot lưu ở cấp Region;
- encryption bằng KMS;
- attach/mount vào EC2;
- chọn volume type theo IOPS/throughput/latency.

## Network: VPC, Security Group, NAT, Peering

Core VPC:

- VPC là private network boundary trong AWS.
- Subnet nằm trong một AZ.
- Route table điều khiển next hop.
- Internet Gateway cho subnet public đi Internet.
- NAT Gateway cho private subnet outbound Internet.
- Security Group là stateful firewall ở ENI/instance level.
- Network ACL là stateless firewall ở subnet level.

Stateful vs stateless:

| Control | Stateful | Level |
|---|---|---|
| Security Group | có | ENI/instance |
| Network ACL | không | subnet |

VPC Peering dùng để nối hai VPC nhưng không hỗ trợ transitive routing. Với nhiều VPC/tài khoản, cân nhắc Transit Gateway.

## Database, Cache Và Queue

| Service | Tư duy chọn |
|---|---|
| RDS/Aurora | relational workload, SQL, join, transaction |
| DynamoDB | key-value/document, scale lớn, latency thấp, access pattern rõ |
| ElastiCache | cache/session/rate limit, Redis/Memcached |
| Redshift | data warehouse/analytics |
| SQS | decoupling bằng queue |
| SNS | pub/sub fanout notification |
| Kinesis/Firehose | streaming/near-real-time ingestion |

Multi-AZ RDS tăng HA/failover, không dùng standby như read replica thông thường. Nếu cần read scaling, dùng read replica hoặc Aurora reader endpoint.

## Observability Và Operations

CloudWatch dùng cho metrics, logs, alarms và dashboard. CloudTrail ghi API activity để audit. AWS Config theo dõi resource configuration và compliance.

Câu hỏi hay gặp:

- Monitor RDS IOPS: CloudWatch metric + alarm.
- Audit ai gọi API: CloudTrail.
- Track config drift/compliance: AWS Config.
- Billing/cost alert: Budgets hoặc Cost Explorer tùy mục tiêu.

## Security Patterns

Các answer phỏng vấn thường quy về:

- Dùng IAM role cho EC2/Lambda thay vì hard-code access key.
- Dùng least privilege.
- Bật MFA cho root và user nhạy cảm.
- Dùng KMS để quản lý key encryption.
- Không public S3 bucket nếu không có lý do rõ.
- Dùng Security Group chặt theo port/source.
- Dùng Organizations/consolidated billing để gom account.

Ví dụ: EC2 cần đọc private S3 bucket thì nên gán IAM role cho instance, không đặt access key trong code.

## Scenario Checklist

Khi gặp câu hỏi kiến trúc AWS, đi theo checklist:

1. Workload stateful hay stateless?
2. Cần HA trong một AZ, multi-AZ hay multi-Region?
3. Data cần consistency, latency, retention và encryption thế nào?
4. Traffic pattern ổn định, spike, hay batch?
5. Có cần decoupling bằng queue/event không?
6. Có yêu cầu compliance/audit không?
7. Có thể dùng managed service để giảm vận hành không?
8. Blast radius nằm ở instance, AZ, Region hay account?

## Expanded Source Coverage From Q&A

Tai lieu nguon co hon 180 cau hoi phong van, nhieu cau bi lap hoac loi ngu phap. Cac nhom kien thuc duoi day la phan bo sung de dam bao khong bo sot cac service/pattern duoc hoi trong source.

### Compute, Deployment And Application Services

| Dich vu / khái niệm | Diem can noi duoc |
|---|---|
| Lightsail | VPS/app hosting don gian cho workload nho, it tuy bien hon EC2/VPC day du |
| Elastic Beanstalk | platform deployment cho app; AWS giup provisioning, health va update o muc platform |
| Lambda | serverless compute theo event, khong quan ly server |
| Lambda@Edge | chay logic gan CloudFront edge de thay doi request/response gan user |
| CloudFormation | IaC engine de tao resource lap lai bang template |
| AMI pipeline | dong goi image chuan de Auto Scaling, blue/green, DR va baseline security |

Beanstalk va CloudFormation khong giong nhau: Beanstalk la abstraction deploy app, CloudFormation la engine khai bao resource. Beanstalk co the dung CloudFormation ben duoi, nhung khi tra loi phong van phai tach dung mental model.

### S3, Archive, Replication And Pre-Signed URL

- Lifecycle rule dung de chuyen object giua storage class hoac expire object.
- Cross-Region Replication dung cho DR, compliance hoac read locality, nhung can versioning va policy dung.
- Glacier/archival storage phu hop luu tru dai han, khong truy xuat thuong xuyen.
- Pre-signed URL cho phep truy cap tam thoi ma khong public bucket.
- EBS snapshot la co che backup block volume; EBS volume gan voi AZ, snapshot co the dung de phuc hoi/tao volume moi.

### Network And Edge

- Internet Gateway cho subnet public di Internet.
- NAT Gateway/NAT Instance cho private subnet outbound Internet.
- VPN/Direct Connect ket noi on-prem voi AWS; Direct Connect phu hop latency/bandwidth on dinh hon.
- Route 53 phu trach DNS/routing policy/health check/failover.
- CloudFront la CDN/edge cache, thuong ket hop ACM certificate, WAF va origin nhu S3/ALB.
- VPC Peering khong transitive; voi nhieu VPC/account nen can nhac Transit Gateway.

Voi ung dung TCP legacy can biet source IP client, phai chon load balancer/proxy design phu hop va kiem tra co can Proxy Protocol hay Network Load Balancer hay khong.

### Database, Analytics, Search And Queue

| Dich vu | Dung khi |
|---|---|
| RDS/Aurora | relational workload, SQL, transaction, join |
| DynamoDB | key-value/document, scale lon, access pattern ro |
| ElastiCache | cache/session/rate limit, Redis/Memcached |
| Redshift | data warehouse va analytic query |
| EMR | Hadoop/Spark ecosystem cho big data processing |
| Kinesis Data Firehose | ingest streaming data vao S3/Redshift/OpenSearch hoac dich vu dich |
| CloudSearch/OpenSearch-style search | search/full-text use case |
| SQS | queue de decouple producer/consumer va hap thu spike |

Multi-AZ RDS la HA/failover, khong dung standby nhu read replica de doc/ghi. Neu can read scaling, dung read replica hoac Aurora reader endpoint.

### Security And Identity Scenarios

| Chu de | Huong tra loi |
|---|---|
| EC2 doc S3 private | gan IAM role cho EC2, khong hard-code access key |
| KMS key sai Region | service o Region khac co the khong thay key; can key strategy dung Region |
| ACM | quan ly TLS certificate cho dich vu AWS duoc ho tro |
| Directory Service / AD integration | dung khi can tich hop Microsoft AD voi workload AWS |
| WAF/Shield | WAF chong layer 7 pattern; Shield chong DDoS |
| GuardDuty/Inspector | detection/vulnerability visibility, can workflow xu ly finding |

### Coverage Matrix

| Nhom cau hoi trong source | Da chuyen hoa vao |
|---|---|
| Q1-Q4, Q111-Q118 cloud/AWS foundation | Cloud Foundation |
| EC2, AMI, key pair, EIP, pricing, instance type | EC2, AMI, Key Pair va Pricing |
| Auto Scaling, ELB, lifecycle hook, connection draining | Auto Scaling va Load Balancing |
| S3, EBS, EFS, snapshot, lifecycle, replication, Glacier | Storage |
| VPC, subnet, security group, NAT, peering, external connectivity | Network |
| RDS, DynamoDB, ElastiCache, Redshift, EMR, Kinesis | Database, Cache va Queue |
| CloudWatch, CloudTrail, cost/billing, Elastic Beanstalk | Observability va Operations |
| IAM role, KMS, ACM, AD integration, WAF/Shield | Security Patterns |
| Scenario HA/DR/decoupling/performance/cost | Scenario Checklist |

## Related Pages

- [AWS Operating Model And Service Scope](./02-aws-operating-model-and-service-scope.md)
- [IAM, Accounts, Organizations And Policy](../01-identity-security-governance/01-iam-accounts-organizations-policy.md)
- [VPC, Subnets, Routing And Endpoints](../02-networking-edge/01-vpc-subnets-routing-endpoints.md)
- [EC2 Instance Lifecycle, Networking And Cost](../03-compute-ec2-autoscaling/01-ec2-instance-lifecycle-networking-and-cost.md)
- [Storage And Database Selection Patterns](../05-storage-data-databases/04-storage-and-database-selection-patterns.md)
