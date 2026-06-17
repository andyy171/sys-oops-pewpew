# VPC, Subnets, Routing And Endpoints

## Overview

VPC là mạng ảo riêng trong AWS, nằm trong một account và một Region. Các tài nguyên private như EC2, RDS, ECS task thường chạy trong subnet của VPC. Thiết kế VPC tốt quyết định phần lớn khả năng isolation, high availability và private connectivity của workload.

## Core Components

| Component | Scope | Vai trò |
|---|---|---|
| VPC | Regional | Không gian mạng riêng với CIDR riêng |
| Subnet | AZ | Chứa resource trong một AZ |
| Route table | VPC/subnet association | Quyết định next hop |
| Internet Gateway | VPC | Cho public subnet đi/nhận internet |
| NAT Gateway | AZ | Cho private subnet outbound internet |
| Security Group | ENI/resource | Stateful firewall |
| Network ACL | Subnet | Stateless subnet-level filter |

## Public Và Private Subnet

Một subnet được xem là public khi route table có default route ra Internet Gateway và resource có public IP hoặc được expose qua load balancer. Private subnet thường không có inbound internet trực tiếp; outbound internet nếu cần sẽ đi qua NAT Gateway hoặc VPC endpoint.

Với high availability, không đặt toàn bộ workload vào một subnet/AZ. Tối thiểu nên có public/private subnet ở nhiều AZ khi workload yêu cầu HA.

Thiết kế subnet nên bắt đầu từ traffic path, không bắt đầu từ số lượng subnet cho đẹp:

```text
Internet
-> public entry point: ALB / bastion / NAT Gateway
-> private application subnet
-> private data subnet
```

Public subnet là nơi đặt public entry point có chủ đích. Application và database thường không cần public IP trực tiếp. Nếu private subnet cần tải package, gọi API ngoài hoặc cập nhật OS, phải thiết kế egress path ngay từ đầu bằng NAT Gateway, VPC endpoint hoặc proxy/firewall appliance. Một instance trong private subnet không có route egress sẽ không thể tự cài package từ Internet trong bootstrap.

Traffic giữa các subnet trong cùng VPC có local route mặc định. Không thể "tắt" local route bằng route table; nếu cần chặn giữa subnet/workload, dùng Security Group, NACL hoặc network firewall phù hợp.

## VPC Endpoints

VPC Endpoint giúp resource trong VPC truy cập AWS service qua private path thay vì đi qua public internet.

| Endpoint type | Dùng cho | Ghi chú |
|---|---|---|
| Gateway endpoint | S3, DynamoDB | Gắn vào route table, thường đơn giản và tiết kiệm cho S3/DynamoDB |
| Interface endpoint | Nhiều AWS service qua PrivateLink | Tạo ENI trong subnet, cần security group và multi-AZ design nếu cần HA |

Scenario thường gặp:

- EC2 trong private subnet cần đọc S3 mà không có internet: dùng S3 gateway endpoint.
- Ứng dụng phải đảm bảo traffic tới S3 không đi qua internet: dùng endpoint và bucket policy giới hạn source endpoint/VPC nếu cần.
- Private service cần expose sang VPC/account khác: cân nhắc PrivateLink.

## NAT Gateway Pattern

NAT Gateway là tài nguyên AZ-scoped. Nếu private subnet ở nhiều AZ cùng dùng một NAT Gateway ở một AZ, khi AZ đó lỗi, outbound internet của các subnet phụ thuộc cũng bị ảnh hưởng. Thiết kế HA thường dùng NAT Gateway theo từng AZ và route private subnet trong AZ đó tới NAT cùng AZ.

## Hybrid Connectivity

| Requirement | Service |
|---|---|
| Kết nối nhanh qua internet, setup đơn giản | Site-to-Site VPN |
| Băng thông ổn định, latency thấp, private link vật lý | Direct Connect |
| Kết nối nhiều VPC/on-prem theo hub-and-spoke | Transit Gateway |

## Related Pages

- [Route 53, CloudFront And Global Traffic](./02-route53-cloudfront-global-traffic.md)
- [SAA-C03 Scenario Patterns](../07-architecture-patterns/01-saa-c03-scenario-patterns.md)
