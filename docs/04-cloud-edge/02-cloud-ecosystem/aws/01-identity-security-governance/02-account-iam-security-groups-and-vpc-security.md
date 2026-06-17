# Account, IAM, Security Groups And VPC Security

## Overview

AWS security bắt đầu từ account và identity, sau đó mới tới network rule. Một kiến trúc an toàn cần đồng thời kiểm soát:

- Ai được gọi AWS API?
- Resource nằm trong network boundary nào?
- Traffic nào được phép đi vào/đi ra?
- Log/audit có ghi lại hành động không?
- Credential và secret được cấp phát/xoay vòng thế nào?

## Root User

Root user có toàn quyền với AWS account. Production account nên:

- Bật MFA cho root.
- Không dùng root cho công việc hằng ngày.
- Không tạo access key cho root.
- Giữ email/phone/payment ownership rõ ràng.
- Dùng root chỉ cho tác vụ bắt buộc.

## IAM User, Group, Role

| Thành phần | Khi dùng |
| --- | --- |
| IAM user | người dùng hoặc legacy integration cần identity dài hạn |
| IAM group | gom permission cho IAM user |
| IAM role | quyền tạm thời cho AWS service, workload hoặc federation |
| IAM policy | định nghĩa allow/deny action trên resource |

Trong kiến trúc hiện đại, ưu tiên role và federation hơn access key dài hạn.

## IAM Policy Mental Model

Policy trả lời:

```text
Principal nào được phép Action gì trên Resource nào, trong Condition nào?
```

Khi debug AccessDenied:

1. Xác định principal thật bằng `sts get-caller-identity`.
2. Kiểm tra identity policy.
3. Kiểm tra resource policy nếu service hỗ trợ.
4. Kiểm tra permission boundary/SCP/session policy.
5. Kiểm tra explicit deny.

## Security Groups

Security Group là firewall stateful ở cấp ENI/resource.

Đặc điểm:

- Stateful: reply traffic được tự động cho phép.
- Rule là allow-only.
- Có inbound và outbound rule.
- Có thể reference security group khác thay vì CIDR.

Pattern tốt:

```text
Internet -> ALB SG -> App SG -> Database SG
```

App instance không cần mở port từ Internet; chỉ cần allow từ ALB security group.

Khi rule dùng CIDR, inbound rule lọc theo source và outbound rule lọc theo destination. `0.0.0.0/0` nghĩa là mọi IPv4 source/destination, nên chỉ nên dùng cho traffic công khai có chủ đích như HTTP/HTTPS qua load balancer. SSH/RDP từ Internet nên bị hạn chế bằng VPN, bastion, SSM Session Manager hoặc source CIDR tạm thời có owner và expiry.

Source security group thường bền hơn source IP khi workload scale:

```text
Bastion SG allows 22 from VPN/admin CIDR
Private Server SG allows 22 from Bastion SG
DB SG allows 5432 from App SG
```

Cách này mô tả quan hệ giữa workload thay vì danh sách IP động. Tuy vậy, bastion không nên trở thành "máy admin tổng hợp". Production bastion cần hardening, MFA/federated access nếu có, session log, patching, không lưu private key dài hạn trên host và không chạy service không liên quan.

SSH agent forwarding tiện cho lab nhưng có rủi ro nếu bastion bị compromise. Với production, ưu tiên SSM Session Manager, short-lived certificate, Teleport/VPN, hoặc cơ chế access có audit thay vì forward key dài hạn qua nhiều hop.

## Network ACL

NACL là stateless rule ở subnet level.

NACL phù hợp cho guardrail coarse-grained. Không nên dùng NACL để thay thế hoàn toàn Security Group vì dễ sai ephemeral port và chiều reply traffic.

Khác với Security Group, NACL không tự cho phép reply traffic. Nếu allow inbound `22/tcp`, bạn vẫn cần rule phù hợp cho outbound ephemeral port để SSH hoạt động; chiều kết nối ngược lại cũng cần cặp rule tương ứng. Vì vậy NACL nên giữ đơn giản, ít rule, dùng cho boundary cấp subnet hoặc deny list rõ ràng; kiểm soát workload-level nên đặt ở Security Group.

## VPC Security

Các lớp cần kết hợp:

- Public/private subnet.
- Route table.
- Security Group.
- NACL.
- NAT Gateway hoặc VPC Endpoint.
- Flow Logs.
- IAM role/service policy.

Một resource nằm trong private subnet chưa chắc đã an toàn nếu IAM role quá rộng hoặc outbound không kiểm soát.

## Related Pages

- [IAM, Accounts, Organizations And Policy](./01-iam-accounts-organizations-policy.md)
- [VPC, Subnets, Routing And Endpoints](../02-networking-edge/01-vpc-subnets-routing-endpoints.md)
- [CloudWatch, Alarms, Logs And Budgets](../08-observability-operations-cost/01-cloudwatch-alarms-logs-and-budgets.md)
