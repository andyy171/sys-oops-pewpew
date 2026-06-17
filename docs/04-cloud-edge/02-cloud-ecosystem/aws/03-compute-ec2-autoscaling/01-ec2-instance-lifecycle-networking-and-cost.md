# EC2 Instance Lifecycle, Networking And Cost

## Overview

EC2 cung cấp virtual machine trong AWS. Đây là lựa chọn phù hợp khi cần kiểm soát hệ điều hành, package, daemon, agent, kernel setting hoặc runtime không phù hợp với serverless/container abstraction.

EC2 không nên được hiểu là "server vĩnh viễn". Trong cloud architecture, EC2 nên được tạo từ template, gắn với IAM role, nằm trong subnet rõ ràng, có security group tối thiểu và được thay thế khi hỏng.

## Launch Mental Model

Khi launch EC2, các quyết định chính gồm:

- AMI: image hệ điều hành và baseline software.
- Instance type: CPU, memory, network, storage profile.
- Key pair hoặc access method: SSH/SSM Session Manager.
- Subnet/AZ: vị trí mạng và fault domain.
- Security group: inbound/outbound policy stateful.
- IAM role: quyền ứng dụng hoặc agent dùng để gọi AWS API.
- Storage: root EBS, extra EBS hoặc instance store.
- User data: bootstrap script.

EC2 instance gắn với một AZ. Nếu AZ có sự cố, instance và EBS trong AZ đó cũng bị ảnh hưởng.

AMI là baseline để launch instance, không phải bằng chứng rằng workload đã sẵn sàng production. Khi chọn AMI/instance type, cần kiểm tra:

- AMI còn được vendor/community support không.
- OS/kernel/agent có phù hợp với monitoring, patching và security baseline không.
- Instance type có đúng profile CPU, RAM, network, EBS throughput và architecture không.
- Workload có cần burstable CPU, sustained CPU, memory-heavy, network-heavy hay storage-optimized không.
- Default public IP, key pair, root volume deletion và security group có đúng policy không.

Với access, key pair SSH chỉ nên là fallback có kiểm soát. Production nên ưu tiên SSM Session Manager, short-lived access, bastion/VPN, audit log và không mở SSH/RDP rộng ra Internet.

## AMI, Launch Template Và Bootstrap

Production nên tránh "click tạo server rồi sửa tay". Pattern tốt hơn:

```text
Base image / AMI
        |
Launch Template
        |
Auto Scaling Group
        |
EC2 instances across subnets/AZs
```

Launch Template nên chứa các phần ổn định:

- AMI hoặc parameter reference tới AMI.
- Instance type hoặc danh sách instance type.
- IAM instance profile.
- Security group.
- User data.
- Block device mapping.

Bootstrap bằng user data phù hợp cho cài đặt nhỏ. Với setup nặng, nên dùng golden AMI, configuration management hoặc image pipeline.

## Networking

EC2 nằm trong subnet của một VPC:

- Public subnet thường có route tới Internet Gateway và instance có public IP hoặc đi qua load balancer.
- Private subnet không nhận inbound trực tiếp từ Internet; outbound có thể qua NAT Gateway hoặc VPC Endpoint.
- Security Group stateful, thường dùng để allow traffic từ ALB security group hoặc CIDR cụ thể.

Không nên expose SSH/RDP rộng ra Internet. Ưu tiên SSM Session Manager, bastion có kiểm soát hoặc VPN.

Public IP động không phải identity ổn định của workload. Khi stop/start hoặc replace instance, public IP có thể đổi. Nếu cần endpoint ổn định, ưu tiên DNS trỏ tới Load Balancer. Elastic IP chỉ nên dùng khi thật sự cần static public IPv4 cho một instance/NAT/appliance cụ thể.

Elastic IP và ENI cần được hiểu riêng:

| Object | Scope / vai trò | Lưu ý vận hành |
|---|---|---|
| Private IP | địa chỉ trong subnet/VPC | instance biết private IP, app có thể bind theo private IP |
| Public IP auto-assigned | public reachability tạm thời | có thể đổi khi stop/start hoặc replace |
| Elastic IP | static public IPv4 gắn với account/Region | có thể phát sinh phí nếu không dùng; cần release khi cleanup |
| ENI | network interface trong subnet/AZ | có security group, private IP; có thể attach/detach theo giới hạn instance type |

Thêm ENI hoặc nhiều public IP vào một EC2 làm tăng độ phức tạp routing, security group, OS interface config và app binding. Với web app thông thường, host/path routing qua ALB hoặc DNS thường dễ vận hành hơn.

## Monitoring Và Debug

Các lớp cần kiểm tra:

```bash
aws ec2 describe-instances --instance-ids <instance-id>
aws ec2 describe-instance-status --instance-ids <instance-id>
aws cloudwatch get-metric-statistics ...
```

Trên OS:

```bash
uptime
journalctl -xe --no-pager
df -h
free -m
ss -lntup
```

Các nhóm lỗi thường gặp:

- Instance status check fail: vấn đề nền tảng/host.
- System status check fail: vấn đề AWS infrastructure dưới instance.
- Application không trả lời: process, port, firewall, health check path.
- Không SSH được: security group, route, NACL, key, OS firewall, user.

EC2 console system log hữu ích khi không SSH được hoặc instance lỗi boot, nhưng log có độ trễ và không thay thế log shipping. CloudWatch metric mặc định thường có CPU, network, disk I/O/status check; memory, filesystem usage chi tiết và process-level signal thường cần CloudWatch Agent/custom metric.

Runbook tối thiểu khi instance có vấn đề:

1. Xác nhận đúng account, Region, instance ID và AZ.
2. Kiểm tra instance state, system status check và instance status check.
3. Kiểm tra security group, route table, NACL và public/private reachability.
4. Xem system log/console screenshot nếu không SSH/SSM được.
5. Kiểm tra OS log, disk full, memory pressure, process listen port và application log.
6. Nếu instance nằm sau load balancer, so sánh target health với reachability trực tiếp trong VPC.

## Patching Và Security Updates

EC2 tự quản cần quy trình patching rõ ràng cho OS, package và runtime. Không nên chỉ dựa vào việc SSH thủ công từng server rồi chạy update, vì cách đó khó audit, khó rollback và dễ lệch cấu hình giữa các instance.

Production pattern:

1. Theo dõi advisory từ vendor/OS và inventory instance đang chạy.
2. Test patch trên môi trường staging hoặc canary.
3. Cập nhật AMI/image pipeline hoặc bootstrap package version.
4. Roll out qua Auto Scaling Group/Launch Template thay vì sửa tay từng máy nếu workload cho phép.
5. Validate health check, application smoke test, log và metric.
6. Rollback bằng AMI/Launch Template version trước hoặc thay instance bằng version cũ nếu patch gây lỗi.

User data có thể cài security update lúc boot, nhưng `yum -y update` hoặc lệnh tương tự làm instance mới phụ thuộc vào trạng thái package repo tại thời điểm launch. Với workload cần reproducible build, pin version quan trọng, dùng golden AMI hoặc image pipeline. Với kernel/security patch cần reboot, lên lịch maintenance hoặc rolling replacement; đừng reboot đồng loạt toàn bộ capacity của một service.

Read-only checks trước khi patch:

```bash
yum --security check-update
dnf updateinfo list security
uname -a
```

Lệnh update/reboot là thao tác có thể gây gián đoạn. Trước khi chạy hàng loạt, cần xác nhận backup/snapshot nếu instance giữ state, kiểm tra Auto Scaling/Load Balancer capacity, drain traffic nếu cần và có rollback path rõ ràng.

## Cost Model

EC2 cost phụ thuộc vào:

- Instance type và thời gian chạy.
- Pricing option: On-Demand, Savings Plans/Reserved, Spot.
- EBS volume, snapshot và IOPS/throughput.
- Data transfer.
- Elastic IP không dùng, NAT Gateway hoặc Load Balancer liên quan.

Không ghi nhớ giá cụ thể trong note; hãy nhớ trade-off:

| Option | Khi dùng |
| --- | --- |
| On-Demand | workload ngắn hạn, không đoán trước |
| Savings Plans/Reserved | workload ổn định dài hạn |
| Spot | batch/stateless/fault-tolerant workload |

Lifecycle ảnh hưởng trực tiếp tới chi phí và dữ liệu:

| Action | Ý nghĩa | Rủi ro / guardrail |
|---|---|---|
| Stop | dừng compute, có thể start lại | EBS, snapshot, Elastic IP hoặc resource liên quan vẫn có thể phát sinh phí |
| Reboot | restart OS trên cùng instance lifecycle | không xử lý được lỗi cấu hình hạ tầng hoặc AZ/host nghiêm trọng |
| Terminate | xóa instance | root EBS có thể bị xóa theo `DeleteOnTermination`; cần snapshot/backup trước với dữ liệu quan trọng |
| Replace | tạo instance mới từ template/AMI | cần externalized state, automation và health check đúng |

Spot phù hợp cho workload chịu gián đoạn: batch processing, queue worker idempotent, render/transcode, test hoặc job có checkpoint. Không dùng Spot đơn lẻ cho database, stateful primary, bastion duy nhất hoặc workload không có retry/checkpoint. Khi dùng Spot, thiết kế graceful interruption handling, checkpoint và capacity fallback.

Reserved Instances/Savings Plans giảm cost cho baseline ổn định, nhưng không thay thế scaling design. Nên giữ phần baseline bằng commitment, còn burst/unpredictable capacity dùng On-Demand hoặc Spot tùy tolerance.

## Best Practices

- Chạy workload production qua Auto Scaling Group thay vì EC2 đơn lẻ.
- Dùng IAM role thay vì access key trên máy.
- Không dùng instance store cho dữ liệu quan trọng nếu không có replication.
- Patch OS và application đều đặn.
- Đặt tag owner, environment, cost center.
- Thiết kế replaceable instance: log ra ngoài, config qua IaC/SSM, data tách khỏi compute.

## Related Pages

- [VPC, Subnets, Routing And Endpoints](../02-networking-edge/01-vpc-subnets-routing-endpoints.md)
- [High Availability, Decoupling And Fault Tolerance](../09-architecture-resilience/01-high-availability-decoupling-and-fault-tolerance.md)
- [CloudWatch, Alarms, Logs And Budgets](../08-observability-operations-cost/01-cloudwatch-alarms-logs-and-budgets.md)
