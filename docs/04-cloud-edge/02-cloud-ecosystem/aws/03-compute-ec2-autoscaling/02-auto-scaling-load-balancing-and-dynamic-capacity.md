# Auto Scaling, Load Balancing And Dynamic Capacity

## Overview

Auto Scaling và Elastic Load Balancing giúp biến EC2 từ các server riêng lẻ thành một compute pool có thể tự phục hồi và thay đổi dung lượng theo nhu cầu.

Core idea:

```text
Client
  -> Load Balancer
  -> Target Group
  -> Auto Scaling Group
  -> EC2 instances across multiple AZs
```

## Load Balancer

Load Balancer nhận traffic từ client và phân phối đến target khỏe mạnh.

| Loại | Khi dùng |
| --- | --- |
| Application Load Balancer | HTTP/HTTPS, path/host routing, app workload |
| Network Load Balancer | TCP/UDP/TLS, latency thấp, static IP use case |
| Gateway Load Balancer | appliance/firewall inspection pattern |

Với workload web phổ biến, ALB thường là lựa chọn mặc định.

## Target Group Và Health Check

Target group chứa backend instance/IP/Lambda tùy loại. Health check quyết định target có nhận traffic không.

Điểm cần chú ý:

- Health check path phải phản ánh dependency quan trọng vừa đủ.
- Đừng làm health check quá nặng.
- Grace period cần đủ dài cho bootstrap.
- App should fail fast khi không sẵn sàng.

## Auto Scaling Group

ASG duy trì desired capacity:

- Nếu instance hỏng health check, ASG tạo instance mới.
- Nếu metric vượt ngưỡng, ASG scale out.
- Nếu nhu cầu giảm, ASG scale in.
- Nếu đặt subnet ở nhiều AZ, ASG có thể phân phối instance qua nhiều fault domain.

ASG không "di chuyển" instance hỏng; nó tạo instance mới từ launch template/AMI.

## Scaling Policy

Các kiểu phổ biến:

- Manual scaling: chỉnh desired capacity.
- Scheduled scaling: scale theo lịch.
- Target tracking: giữ metric quanh target, ví dụ CPU 50%.
- Step scaling: scale theo nhiều mức ngưỡng.

Metric phổ biến:

- CPUUtilization.
- Request count per target.
- ALB target response time.
- Queue depth per worker.

Với worker async, queue depth thường tốt hơn CPU vì nó đo backlog thật.

## Multi-AZ Resilience

Để chịu lỗi AZ:

1. Tạo subnet ở ít nhất hai AZ.
2. ALB chọn các subnet đó.
3. ASG dùng launch template và subnet group nhiều AZ.
4. App không giữ state chỉ trong instance local.
5. Data nằm ở service phù hợp như RDS Multi-AZ, S3, EFS hoặc DynamoDB.

Nếu application state nằm trong local disk/session memory, load balancing và ASG chỉ giải quyết được một phần.

## Common Pitfalls

- Health check path luôn trả 200 dù app dependency đã hỏng.
- Instance bootstrap lâu nhưng health check grace period quá ngắn.
- ASG scale theo CPU nhưng bottleneck thật là database/queue/external API.
- Chỉ chạy ASG ở một AZ.
- Scale in làm mất job đang xử lý vì worker không drain graceful.
- Security group của instance không allow inbound từ ALB security group.

## Related Pages

- [EC2 Instance Lifecycle, Networking And Cost](./01-ec2-instance-lifecycle-networking-and-cost.md)
- [CloudWatch, Alarms, Logs And Budgets](../08-observability-operations-cost/01-cloudwatch-alarms-logs-and-budgets.md)
- [High Availability, Decoupling And Fault Tolerance](../09-architecture-resilience/01-high-availability-decoupling-and-fault-tolerance.md)
