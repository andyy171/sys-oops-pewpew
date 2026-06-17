# AWS Operating Model And Service Scope

## Overview

AWS là public cloud cung cấp tài nguyên hạ tầng và platform qua API. Người vận hành không quản lý trực tiếp datacenter, nhưng vẫn phải hiểu rõ service scope, fault domain, billing model và trách nhiệm bảo mật của từng lớp.

Mental model quan trọng:

- AWS service là API-driven: console, CLI, SDK, CloudFormation và Terraform cuối cùng đều gọi API.
- Không phải service nào cũng có cùng phạm vi resilience: có service global, regional, hoặc gắn với Availability Zone.
- Pay-per-use giúp scale nhanh nhưng cũng khiến chi phí tăng nhanh nếu không có governance.
- Automation là một phần của operating model, không chỉ là tiện ích.

## Service Scope

| Scope | Ý nghĩa | Ví dụ thường gặp |
| --- | --- | --- |
| Global | tài nguyên/namespace không gắn với một Region cụ thể | IAM, Route 53, CloudFront |
| Regional | resource tồn tại trong một Region | VPC, S3 bucket, Lambda, DynamoDB table |
| Zonal | resource gắn với một Availability Zone | subnet, EC2 instance, EBS volume |

Khi thiết kế, luôn hỏi:

```text
Nếu một AZ hỏng thì service này còn hoạt động không?
Nếu cả Region hỏng thì dữ liệu/control plane còn ở đâu?
Service này cần replicate bằng cấu hình của mình hay AWS đã làm sẵn?
```

## Cách Tương Tác Với AWS

Các cách chính:

- **Management Console**: phù hợp học/lab và thao tác nhỏ.
- **AWS CLI**: phù hợp automation, runbook, kiểm tra nhanh.
- **SDK**: phù hợp application hoặc tool tự động gọi AWS API.
- **IaC**: CloudFormation, CDK hoặc Terraform để quản lý desired state.

Trong production, thao tác qua console nên là ngoại lệ. Hạ tầng quan trọng nên có IaC, review change và rollback path.

## API-First Mental Model

Console, CLI, SDK và IaC khác nhau về trải nghiệm thao tác, nhưng điểm chung là đều đi qua AWS API. Vì vậy khi debug production, đừng chỉ hỏi "người vận hành bấm gì trên console" mà hãy truy vết:

```text
Actor / tool
-> AWS API action
-> IAM authorization
-> control-plane state
-> runtime data-plane effect
-> CloudTrail / Config / CloudWatch evidence
```

Console phù hợp để học, lab và khám phá nhanh. Với hạ tầng sống lâu, CLI/SDK/IaC giúp tạo lại được thao tác, review được thay đổi và giảm sai khác giữa môi trường.

## Billing Và Cost Awareness

AWS tính phí theo nhiều chiều:

- Runtime của compute.
- Storage capacity và request.
- Data transfer.
- Managed service throughput.
- Log/metric/trace ingestion và retention.
- NAT Gateway, Load Balancer, Elastic IP hoặc endpoint theo giờ/dung lượng.

Không nên ghi nhớ giá cụ thể trong note dài hạn vì pricing thay đổi. Nên ghi nhớ **cost driver** của từng service và kiểm tra pricing/current quota ở AWS docs khi thiết kế thật.

Tag là một phần của operating model, không chỉ để "đặt tên đẹp". Nếu resource được tag theo `Application`, `Environment`, `Owner` và `CostCenter`, team có thể group resource, phân bổ chi phí, tìm blast radius khi incident và cleanup lab/test stack có kiểm soát hơn.

## Shared Responsibility

AWS chịu trách nhiệm bảo mật **of the cloud**: datacenter, hardware, managed control plane theo từng service.

Người dùng chịu trách nhiệm bảo mật **in the cloud**:

- IAM principal, policy và credential.
- Network exposure: security group, NACL, route, public IP.
- OS patching với EC2 tự quản.
- Data classification, encryption, backup và retention.
- Application security.
- Logging, monitoring và incident response.

Managed service càng cao thì AWS gánh càng nhiều phần vận hành, nhưng identity, data và configuration vẫn là trách nhiệm của người dùng.

Với EC2 tự quản, đừng hiểu shared responsibility là AWS sẽ patch hoặc harden thay toàn bộ server. AWS vận hành phần nền tảng bên dưới, còn team vận hành vẫn phải có quy trình cho OS patching, package update, SSH/SSM access, firewall rule, log, backup và incident response. Với managed service, phần OS/control plane được AWS gánh nhiều hơn, nhưng IAM policy, network exposure, encryption choice và dữ liệu đưa vào service vẫn là trách nhiệm của workload owner.

## Related Pages

- [Cloud, Global Infrastructure And Resilience](./01-cloud-global-infrastructure-and-resilience.md)
- [IAM, Accounts, Organizations And Policy](../01-identity-security-governance/01-iam-accounts-organizations-policy.md)
- [CLI, SDK, CloudFormation And SAM](../04-infrastructure-as-code-automation/01-cli-sdk-cloudformation-and-sam.md)
