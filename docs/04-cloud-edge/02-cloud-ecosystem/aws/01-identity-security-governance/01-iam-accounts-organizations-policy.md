# IAM, Accounts, Organizations And Policy

## Overview

IAM kiểm soát ai hoặc workload nào được làm gì trên tài nguyên AWS. Với kiến trúc nhiều account, AWS Organizations và IAM Identity Center giúp chuẩn hóa access, tagging và guardrail ở cấp tổ chức.

## Core Concepts

| Thành phần | Vai trò |
|---|---|
| IAM user | Identity dài hạn cho người hoặc workload cũ; nên hạn chế dùng cho automation mới |
| IAM role | Identity tạm thời có thể assume bởi EC2, Lambda, ECS task, user hoặc account khác |
| Policy | Tài liệu JSON mô tả allow/deny action trên resource |
| AWS Organizations | Quản lý nhiều account, OU, SCP và policy cấp tổ chức |
| IAM Identity Center | Quản lý truy cập người dùng vào nhiều account theo permission set |

## Design Principles

- Ưu tiên IAM role thay vì hard-code access key.
- Gán role cho EC2 instance profile, Lambda execution role hoặc ECS task role.
- Dùng least privilege: chỉ cấp action/resource cần thiết.
- Dùng explicit deny hoặc SCP cho guardrail cấp tổ chức.
- Chuẩn hóa tag bằng policy ở cấp Organizations khi nhiều team cùng tạo resource.
- Root user phải bật MFA, không dùng cho công việc hằng ngày và không nên có access key.

## CLI / SDK Credential Guardrails

AWS CLI và SDK đều gọi AWS API bằng một principal cụ thể. Trước khi chạy automation, luôn xác định principal thật:

```bash
aws sts get-caller-identity
aws configure list
```

Không dùng root user cho CLI/SDK hằng ngày. Tránh tạo IAM user có `AdministratorAccess` và access key dài hạn cho script cá nhân; đây chỉ nên là lab tạm thời nếu không còn lựa chọn khác. Production nên dùng:

- IAM Identity Center/federation cho người dùng.
- IAM role/instance profile/task role/execution role cho workload.
- Permission set hoặc policy theo least privilege.
- Access key dài hạn chỉ cho legacy integration, có owner, rotation, expiration và CloudTrail monitoring.

Nếu phải dùng access key:

- Không commit vào Git, note, ticket, log hoặc shell history.
- Lưu trong secret manager/credential store phù hợp.
- Rotate định kỳ và disable ngay khi không dùng.
- Gắn policy tối thiểu, không dùng wildcard rộng nếu không có guardrail.

## Policy Scope And Role Boundaries

IAM policy không chỉ là danh sách action; nó là boundary giữa principal, action, resource và condition:

```text
principal -> action -> resource ARN -> condition -> allow/deny
```

Một policy dùng `Resource: "*"` có thể hợp lý cho vài action không hỗ trợ resource-level permission, nhưng với production phải xem đó là ngoại lệ cần giải thích. Khi service hỗ trợ ARN cụ thể, hãy giới hạn theo resource, tag, account, VPC endpoint hoặc organization condition nếu phù hợp.

`Deny` luôn thắng `Allow`. Guardrail như SCP, permission boundary hoặc explicit deny trong policy có thể chặn hành động dù identity policy khác đã allow. Vì vậy khi debug `AccessDenied`, đừng chỉ tìm policy allow đầu tiên; phải kiểm tra toàn bộ evaluation chain.

Managed policy phù hợp khi muốn tái sử dụng permission set giữa nhiều principal. Inline policy phù hợp khi quyền gắn chặt với một role/user và không có ý nghĩa độc lập. Với IaC, inline policy dễ version cùng workload, nhưng vẫn cần review blast radius giống mọi thay đổi IAM khác.

IAM role cho EC2 nên dùng instance profile và cấp quyền theo workload cụ thể. Nếu role cho phép instance tự thao tác lên EC2 resource, hãy thêm condition theo tag/stack/application để tránh một instance bị compromise có thể tác động tài nguyên ngoài phạm vi của nó.

## Common Scenario Patterns

| Requirement | Pattern |
|---|---|
| EC2 cần đọc S3 | Tạo IAM role, attach vào EC2 instance profile, bucket policy giới hạn nếu cần |
| Chỉ account trong Organization được truy cập S3 bucket | Dùng condition key `aws:PrincipalOrgID` trong bucket policy |
| Team chỉ được tạo resource nếu tag hợp lệ | Dùng tag policy/guardrail ở Organizations và kiểm tra bằng Config/IaC pipeline |
| Credential database cần rotate | Dùng Secrets Manager và rotation thay vì lưu password trong file |
| Dữ liệu cần key riêng và audit key usage | Dùng customer managed KMS key và CloudTrail/KMS logs |

## Policy Thinking

Khi debug access denied:

1. Identity có đúng account/role không.
2. Identity policy có allow action không.
3. Resource policy có allow principal không.
4. SCP hoặc permission boundary có deny không.
5. KMS key policy có cho phép decrypt/encrypt không.
6. Request có đúng condition như source VPC endpoint, tag hoặc organization ID không.

## Related Pages

- [CloudWatch, Config, CloudTrail And Cost](../06-observability-operations-cost/01-cloudwatch-config-cloudtrail-cost.md)
- [S3 Object Storage Patterns](../05-storage-data-databases/01-s3-object-storage-patterns.md)
- [RDS, Aurora, DynamoDB And Caching](../05-storage-data-databases/03-rds-aurora-dynamodb-caching.md)
