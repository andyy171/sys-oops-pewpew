# VPC Private Subnets, NAT And Endpoints

## Overview

VPC là network boundary trong một Region. Subnet gắn với một Availability Zone. Public/private không phải thuộc tính cố định của subnet, mà là kết quả của route table và cách resource nhận public reachability.

Mental model:

```text
VPC CIDR
  -> public subnet in AZ A
  -> private subnet in AZ A
  -> public subnet in AZ B
  -> private subnet in AZ B
```

## Public Subnet

Subnet thường được gọi là public khi route table có default route tới Internet Gateway:

```text
0.0.0.0/0 -> igw-...
```

Resource trong public subnet vẫn cần public IP hoặc load balancer public để Internet truy cập được. Security Group/NACL vẫn quyết định traffic có được phép hay không.

## Private Subnet

Private subnet thường không có route trực tiếp tới Internet Gateway.

Outbound options:

- NAT Gateway để instance gọi Internet hoặc public AWS endpoint.
- VPC Gateway Endpoint cho S3/DynamoDB.
- VPC Interface Endpoint cho nhiều AWS service qua PrivateLink.
- Egress qua proxy/firewall appliance.

## NAT Gateway

NAT Gateway cho phép resource private subnet mở outbound connection ra Internet mà không expose inbound trực tiếp.

Điểm cần nhớ:

- NAT Gateway là zonal resource.
- Private subnet ở mỗi AZ nên dùng NAT Gateway cùng AZ để giảm cross-AZ dependency.
- NAT Gateway có cost theo giờ và data processing.
- NAT không thay thế security control ở application/IAM.

NAT instance là pattern cũ/tự quản: một EC2 instance trong public subnet tắt source/destination check và làm next hop cho private subnet. Pattern này hữu ích để hiểu NAT, nhưng production thường ưu tiên NAT Gateway hoặc egress appliance được quản lý vì NAT instance tự mang rủi ro patching, capacity, single point of failure và operational ownership.

Nếu private workload chủ yếu gọi AWS service như S3, DynamoDB, SSM, ECR hoặc CloudWatch, đừng mặc định đẩy tất cả qua NAT. VPC endpoint có thể giảm phụ thuộc Internet egress, giảm blast radius của route `0.0.0.0/0` và cho phép policy theo endpoint/VPC.

## VPC Endpoints

VPC Endpoint giúp private workload gọi AWS service mà không cần đi qua public Internet.

| Loại | Dùng cho | Ghi chú |
| --- | --- | --- |
| Gateway Endpoint | S3, DynamoDB | gắn với route table |
| Interface Endpoint | nhiều AWS service | tạo ENI trong subnet, dùng PrivateLink |

Endpoint gắn với subnet/AZ. Với workload multi-AZ, nên tạo endpoint ở các AZ cần dùng để tránh dependency một AZ.

## Security Group Source Pattern

Thay vì allow app port từ `0.0.0.0/0`, dùng source security group:

```text
ALB SG allows 443 from Internet
App SG allows 8080 from ALB SG
DB SG allows 5432 from App SG
```

Cách này làm rule bền hơn khi instance scale out/scale in vì không phụ thuộc IP động.

## Troubleshooting

Khi private instance không ra ngoài được:

1. Kiểm tra route table của subnet.
2. Kiểm tra NAT Gateway state và AZ.
3. Kiểm tra Security Group outbound.
4. Kiểm tra NACL cả inbound/outbound ephemeral port.
5. Kiểm tra DNS resolver.
6. Nếu gọi AWS service, cân nhắc VPC Endpoint policy.

Pre-check trước khi đổi route egress production:

1. Xác định subnet, route table, AZ và workload bị ảnh hưởng.
2. Kiểm tra đang có flow qua NAT/endpoint nào bằng VPC Flow Logs hoặc metric liên quan.
3. Chuẩn bị rollback route về next hop cũ.
4. Áp dụng theo từng subnet/AZ nếu có thể.
5. Validate bằng request read-only từ instance đại diện, ví dụ gọi metadata, DNS, package repo nội bộ hoặc AWS API không phá hủy.

Useful checks:

```bash
aws ec2 describe-route-tables
aws ec2 describe-nat-gateways
aws ec2 describe-vpc-endpoints
```

## Related Pages

- [VPC, Subnets, Routing And Endpoints](./01-vpc-subnets-routing-endpoints.md)
- [Account, IAM, Security Groups And VPC Security](../01-identity-security-governance/02-account-iam-security-groups-and-vpc-security.md)
- [High Availability, Decoupling And Fault Tolerance](../09-architecture-resilience/01-high-availability-decoupling-and-fault-tolerance.md)
