# EC2, Auto Scaling And Load Balancing

## Overview

EC2 cung cấp virtual machine trong AWS. Một EC2 instance chạy trong một subnet/AZ, nên bản thân instance không phải high availability. HA thường đến từ Auto Scaling Group nhiều AZ, Elastic Load Balancer và application stateless hoặc externalized state.

## EC2 Basics

| Khái niệm | Ý nghĩa |
|---|---|
| AMI | Template để launch instance |
| Instance type | CPU/memory/network/storage profile |
| EBS volume | Block storage gắn với instance, AZ-scoped |
| Instance store | Local ephemeral storage, mất khi host/instance lifecycle kết thúc |
| Security group | Stateful firewall cho ENI/instance |

## Auto Scaling Group

ASG không "di chuyển" instance lỗi sang AZ khác. Nó tạo instance mới theo launch template/AMI trong subnet được cấu hình. Vì vậy app nên stateless hoặc state phải nằm ngoài instance như RDS, DynamoDB, EFS, S3 hoặc cache có thể tái tạo.

Scaling pattern:

- Dynamic scaling cho workload thay đổi theo metric.
- Scheduled scaling cho traffic peak biết trước theo giờ/ngày.
- Target tracking để giữ metric quanh một giá trị mục tiêu.
- Queue-based scaling khi worker xử lý job từ SQS.

Với workload cần "luôn có một instance", ASG vẫn hữu ích dù `min = desired = max = 1`: nó thay instance khi health check fail hoặc instance bị mất. Để chịu được AZ outage, ASG phải có subnet ở nhiều AZ; nếu chỉ cấu hình một subnet, ASG vẫn bị khóa trong một fault domain.

Launch configuration là khái niệm cũ trong nhiều tài liệu; production mới nên ưu tiên Launch Template vì hỗ trợ nhiều tính năng EC2 hiện đại hơn và versioning tốt hơn. Bất kể dùng cơ chế nào, template phải đủ để tạo lại instance mà không cần SSH sửa tay:

- AMI hoặc image pipeline version.
- Instance type/family policy.
- IAM instance profile.
- Security group.
- User data/bootstrap idempotent.
- Block device mapping.
- Tag propagation.

Pitfall khi dùng ASG cho một service stateful:

- Instance ID, private IP và public IP có thể đổi khi replace.
- EBS volume là AZ-scoped; instance mới ở AZ khác không tự attach được volume cũ.
- Root volume mới từ AMI/snapshot chỉ chứa state tại thời điểm image/snapshot.
- Elastic IP gắn lại qua bootstrap cần IAM permission và có race/failure mode; với service nhận traffic, load balancer hoặc DNS/service discovery thường dễ vận hành hơn.
- Test bằng cách terminate instance là thao tác phá hủy; chỉ làm trong lab hoặc production game day có approval, backup, maintenance window và rollback.

Pre-check trước khi đưa workload vào ASG:

1. App có stateless hoặc state đã externalized chưa.
2. Bootstrap có chạy lại an toàn nhiều lần không.
3. Health check có phát hiện app hỏng thật không.
4. Subnet có trải nhiều AZ không.
5. Endpoint cho client là ALB/NLB/DNS hay IP instance.
6. Log/config/secret có nằm ngoài local disk không.

Dynamic server pool cần ba lớp:

```text
Launch Template / image contract
-> Auto Scaling Group: min, max, desired, subnet/AZ, health check
-> Scaling policy: metric, schedule hoặc target tracking thay đổi desired capacity
```

Guardrails khi thiết kế scaling:

- `min` là năng lực tối thiểu và HA floor; `max` là cost/capacity blast-radius limit; `desired` là trạng thái hiện tại ASG cố đạt.
- `HealthCheckGracePeriod` phải đủ dài cho bootstrap/app warm-up; quá ngắn sẽ làm instance chưa sẵn sàng bị thay liên tục.
- Cooldown hoặc warmup phải tránh scale in/out dao động liên tục khi metric vừa vượt ngưỡng.
- Thường scale out nhanh hơn scale in: thêm capacity sớm khi tải tăng, giảm capacity chậm hơn sau khi backlog/latency ổn định.
- Scheduled scaling phù hợp traffic có lịch; metric/target tracking phù hợp traffic khó đoán.
- Load test cần chạy trong môi trường được phép, có giới hạn rate, budget/cost guardrail và khả năng rollback. Không chạy benchmark lớn vào production hoặc public endpoint khi chưa có approval.
- Với burstable instances, CPU không luôn là metric scaling tốt vì credit có thể làm tín hiệu bị méo; cân nhắc request rate, latency, queue depth, memory custom metric hoặc chọn instance không burstable cho workload ổn định.

## Elastic Load Balancing

| Load balancer | Khi dùng |
|---|---|
| ALB | HTTP/HTTPS, path/host routing, web app |
| NLB | TCP/UDP, latency thấp, static IP, high throughput |
| Gateway Load Balancer | Inline inspection với appliance/firewall |

Load balancer là lớp synchronous decoupling giữa client và backend. Client giữ một endpoint ổn định, còn backend có thể được thêm, thay hoặc loại bỏ mà không bắt client biết instance cụ thể:

```text
Client
-> DNS
-> public hoặc internal load balancer
-> listener / rule
-> target group
-> EC2 instance, container hoặc IP target
```

Network boundary nên tách rõ:

- Internet-facing LB chỉ mở port cần thiết từ client, ví dụ `80/443`.
- Backend instance không nên public trực tiếp nếu chỉ phục vụ qua LB.
- Security group của backend nên allow từ security group của LB, không allow rộng từ Internet.
- Internal LB dùng cho service nội bộ; public LB dùng cho ingress từ Internet.

Health check của LB phải đo được app thật, không chỉ đo port còn mở. Ví dụ endpoint `/healthz` nên kiểm tra dependency tối thiểu cần thiết để phục vụ traffic, nhưng không nên quá nặng đến mức chính health check làm backend quá tải. Khi ASG dùng health check từ LB/target group, cấu hình sai có thể tạo vòng lặp thay instance liên tục.

Pre-check trước khi đổi health check hoặc gắn ASG vào LB:

1. Endpoint health check trả kết quả đúng khi app sẵn sàng nhận traffic.
2. Grace period đủ dài cho bootstrap/deploy.
3. Threshold và interval không quá hung hăng so với thời gian warm-up.
4. Có ít nhất một backend healthy trong mỗi AZ mong muốn trước khi cutover.
5. Có dashboard hoặc metric cho `UnHealthyHostCount`, `TargetResponseTime`, HTTP 5xx và connection error.

TLS termination nên dùng ACM certificate và security policy phù hợp thay vì upload certificate thủ công vào service cũ. Nếu traffic backend cũng cần mã hóa, dùng HTTPS đến target hoặc service mesh/private PKI tùy kiến trúc. Khi thay certificate/listener trong production, cần kiểm tra SNI, chain, expiry, cipher policy và rollback sang certificate/listener rule cũ.

Access log của ALB/NLB nên ghi về S3 bucket riêng có policy tối thiểu. Log hữu ích cho điều tra client IP, status code, target status, latency, bytes và user agent. Không dùng access log như nguồn duy nhất cho SLO thời gian thực vì log có độ trễ; alert vẫn nên dựa trên metric CloudWatch.

Cross-zone load balancing giúp phân phối traffic đều hơn qua target ở nhiều AZ. Trước khi bật/tắt trong production, kiểm tra hành vi hiện tại theo loại LB, chi phí data transfer liên AZ và khả năng từng AZ chịu tải khi một AZ hoặc target group bị suy giảm.

Pattern SAA thường gặp:

- Web tier multi-AZ: ALB + ASG across AZ.
- Predictable daily peak: scheduled scaling trước giờ cao điểm.
- Central traffic inspection: Gateway Load Balancer + appliance VPC.
- App cần internet outbound trong private subnet: NAT Gateway theo AZ hoặc endpoint nếu gọi AWS service.

## Cost And Resilience

- On-Demand linh hoạt nhưng đắt hơn cho workload chạy liên tục.
- Reserved Instances/Savings Plans phù hợp workload ổn định.
- Spot phù hợp batch/stateless/fault-tolerant workload có thể bị gián đoạn.
- Với dev/test ít dùng, tự động stop/start hoặc dùng Spot/mixed instances có thể giảm chi phí.

## Related Pages

- [VPC, Subnets, Routing And Endpoints](../02-networking-edge/01-vpc-subnets-routing-endpoints.md)
- [EBS, EFS, FSx And Data Migration](../05-storage-data-databases/02-ebs-efs-fsx-data-migration.md)
- [SAA-C03 Scenario Patterns](../07-architecture-patterns/01-saa-c03-scenario-patterns.md)
