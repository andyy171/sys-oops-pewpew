# Cloud, Global Infrastructure And Resilience

## Overview

AWS là public cloud theo mô hình on-demand self-service, broad network access, resource pooling, rapid elasticity và measured service. Với người học kiến trúc, phần quan trọng nhất không phải tên dịch vụ, mà là hiểu dịch vụ đó nằm ở fault domain nào và chịu lỗi ra sao.

## Cloud Models

Các mô hình triển khai thường gặp:

| Model | Ý nghĩa |
|---|---|
| Public cloud | Dùng cloud provider công cộng như AWS |
| Private cloud | Cloud tự vận hành trong hạ tầng riêng |
| Hybrid cloud | Kết hợp public cloud với private/on-premises |
| Multi-cloud | Dùng nhiều public cloud provider |

Hybrid cloud không đơn giản là "public cloud + legacy on-premises". Nó cần kết nối, identity, network, security và vận hành thống nhất giữa hai phía.

## AWS Global Infrastructure

| Thành phần | Vai trò |
|---|---|
| Region | Khu vực địa lý độc lập, chứa nhiều AZ |
| Availability Zone | Một hoặc nhiều datacenter độc lập trong cùng Region |
| Edge Location | Điểm hiện diện gần user, dùng cho CDN/DNS/edge acceleration |

Region giúp tách biệt về địa lý, pháp lý và độ trễ. AZ giúp thiết kế high availability trong một Region. Edge giúp giảm latency cho user hoặc tối ưu đường truyền tới dịch vụ.

## Resilience Scope

Khi đọc một dịch vụ AWS, nên gắn nó vào một trong các nhóm sau:

| Scope | Ý nghĩa thiết kế |
|---|---|
| Global | Không gắn với một Region duy nhất, ví dụ identity/DNS/global edge tùy service |
| Regional | Dữ liệu/control plane nằm trong một Region và thường trải qua nhiều AZ |
| AZ-scoped | Tài nguyên gắn với một AZ; lỗi AZ có thể làm tài nguyên đó không khả dụng |

Ví dụ tư duy:

- EC2 instance chạy trong một AZ; cần Auto Scaling Group nhiều AZ nếu muốn HA.
- EBS volume nằm trong một AZ; cần snapshot/copy nếu muốn phục hồi ngoài AZ.
- S3 Standard là regional object storage, tự phân tán qua nhiều AZ trong Region.
- Route 53 và CloudFront thường được dùng để đưa traffic ra ngoài phạm vi một Region.

## HA, Fault Tolerance Và DR

- High Availability giảm thời gian gián đoạn bằng redundancy và failover.
- Fault Tolerance hướng tới tiếp tục phục vụ dù có thành phần lỗi.
- Disaster Recovery tập trung khôi phục sau sự cố lớn, thường dùng RTO/RPO để thiết kế.

Trong bài toán SAA-C03, nếu yêu cầu "không downtime khi một AZ lỗi", thường cần multi-AZ. Nếu yêu cầu "chịu lỗi cả Region", cần multi-region, data replication và traffic failover.

## Related Pages

- [Disaster Recovery And Resilience](../disaster-recovery-and-resilience.md)
- [VPC, Subnets, Routing And Endpoints](../02-networking-edge/01-vpc-subnets-routing-endpoints.md)
- [EC2, Auto Scaling And Load Balancing](../03-compute-containers-serverless/01-ec2-auto-scaling-load-balancing.md)
