# AWS Attack Paths And Defensive Controls

## Overview

AWS security incident thường không bắt đầu bằng một “lỗ hổng AWS” duy nhất, mà bằng chuỗi sai cấu hình: credential bị lộ, IAM permission quá rộng, resource policy cho external principal, snapshot/image bị share, EC2 metadata bị đọc, hoặc deployment pipeline cho phép sửa runtime không kiểm soát.

Note này chuyển các pattern offensive phổ biến thành mô hình phòng thủ: nhận diện attack path, đặt guardrail, log/detect và phản ứng an toàn.

```text
credential or runtime access
  -> enumerate identity and permissions
  -> discover data/resources
  -> modify policy/share artifact
  -> exfiltrate data or establish persistence
  -> cover with weak logging/tagging/governance
```

## Defensive Mental Model

| Lớp | Câu hỏi cần trả lời |
|---|---|
| Identity | Principal nào có thể gọi API nhạy cảm? Có dùng role tạm thời thay vì access key dài hạn không? |
| Resource policy | S3 bucket, Lambda, KMS, snapshot, AMI có cho external account hoặc `Principal: "*"` không? |
| Data protection | S3/EBS/RDS có encryption, backup, sharing control và KMS policy đúng không? |
| Runtime | EC2 user data, instance metadata, local filesystem và instance role có bị lộ credential không? |
| Deployment | IaC/CI/CD có review thay đổi security group, Lambda code, policy và tag không? |
| Detection | CloudTrail, Config, GuardDuty/Security Hub hoặc alert nội bộ có bắt event nhạy cảm không? |

## Sanitized Examples

Các ví dụ dưới đây chỉ dùng để nhận diện pattern rủi ro trong review, detection hoặc incident response. Không lưu real access key, session token, password, private key, customer account ID hoặc raw CloudTrail nhạy cảm vào KB/ticket/chat; hãy redacted trước khi chia sẻ.

### S3 Bucket Policy Cho External Account

Pattern nguy hiểm là bucket policy cho account ngoài Organization đọc object hoặc list bucket. Khi review, chú ý `Principal`, `Action`, `Resource` và condition boundary.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ExternalReadExample",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<external-account-id>:root"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::example-bucket",
        "arn:aws:s3:::example-bucket/*"
      ]
    }
  ]
}
```

Guardrail tốt hơn thường là explicit allow cho principal hợp lệ, thêm condition như `aws:PrincipalOrgID`, yêu cầu TLS/KMS nếu phù hợp, và bật Block Public Access ở account/bucket.

### IMDS Credential Response Redacted

IMDS có thể trả về temporary credential cho instance role. Credential này ngắn hạn nhưng vẫn đủ để gọi AWS API theo quyền của instance profile, nên không được copy nguyên vào log hoặc note.

```json
{
  "Code": "Success",
  "Type": "AWS-HMAC",
  "AccessKeyId": "ASIA<redacted>",
  "SecretAccessKey": "<redacted>",
  "Token": "<redacted-session-token>",
  "Expiration": "YYYY-MM-DDTHH:MM:SSZ"
}
```

Khi debug hợp lệ, chỉ ghi lại role name, account, region, expiration và scope quyền cần kiểm tra. Không ghi `SecretAccessKey` hoặc `Token`.

### CloudTrail Event Cần Alert

Ví dụ event đã rút gọn cho thay đổi sharing snapshot. Khi thấy event kiểu này, cần kiểm tra principal, target account, snapshot ID, KMS key policy và các event copy/restore sau đó.

```json
{
  "eventSource": "ec2.amazonaws.com",
  "eventName": "ModifySnapshotAttribute",
  "userIdentity": {
    "type": "AssumedRole",
    "arn": "arn:aws:sts::<account-id>:assumed-role/<role-name>/<session-name>"
  },
  "requestParameters": {
    "snapshotId": "snap-<redacted>",
    "attributeType": "CREATE_VOLUME_PERMISSION",
    "createVolumePermission": {
      "add": {
        "items": [
          {
            "userId": "<external-account-id>"
          }
        ]
      }
    }
  },
  "sourceIPAddress": "<redacted>"
}
```

### Cognito Attribute Change

Với Cognito, rủi ro thực tế không chỉ là token bị lộ mà là token hợp lệ có thể sửa thuộc tính định danh như email/phone mà thiếu verification hoặc step-up authentication.

```bash
aws cognito-idp update-user-attributes \
  --region <region> \
  --access-token '<redacted-access-token>' \
  --user-attributes Name=email,Value=<new-email@example.com>
```

Detection nên tập trung vào `UpdateUserAttributes`, admin update user, password reset, thay đổi email/phone, IP/device lạ và token xuất hiện trong log frontend/backend/proxy.

## High-Risk Attack Paths

| Attack path | API/action đáng chú ý | Rủi ro | Guardrail |
|---|---|---|---|
| Public hoặc external S3 access | `s3:PutBucketPolicy`, `s3:PutBucketAcl`, `s3:GetObject`, `s3:ListBucket` | Exfiltrate object hoặc backdoor bucket policy | Block Public Access, SCP deny public/external policy ngoài allowlist, Access Analyzer |
| Lambda resource policy backdoor | `lambda:AddPermission` | External account invoke function để persistence hoặc abuse event path | Review resource-based policy, restrict principal/source ARN, alert AddPermission |
| Lambda code overwrite | `lambda:UpdateFunctionCode`, `lambda:UpdateFunctionConfiguration` | Chèn logic exfiltration hoặc persistence vào runtime | CI/CD-only deploy, code signing nếu phù hợp, version/alias control, CloudTrail alert |
| RDS snapshot sharing | `rds:ModifyDBSnapshotAttribute` | External account restore DB snapshot | Deny sharing ngoài Organization, monitor snapshot attribute change |
| EBS snapshot sharing | `ec2:ModifySnapshotAttribute`, `ec2:CreateSnapshot`, `ec2:DescribeVolumes` | Copy/mount volume để đọc filesystem, SSH keys, app secrets | Restrict snapshot create/share, encrypt with controlled KMS key, monitor share changes |
| AMI sharing | `ec2:ModifyImageAttribute`, `ec2:ResetImageAttribute` | External account launch image chứa software/data/config nhạy cảm | Allowlist target accounts, Config/CloudTrail alert, image inventory |
| EC2 user data abuse | `ec2:DescribeInstanceAttribute`, `ec2:ModifyInstanceAttribute`, `ec2:StopInstances`, `ec2:StartInstances` | Đọc secret trong user data hoặc sửa user data để chạy lệnh khi boot | Không đặt secret trong user data, restrict modify/start/stop, launch template review |
| Unauthorized EC2 termination | `ec2:TerminateInstances` | Xóa nhầm hoặc phá hoại instance quan trọng | Termination protection cho instance critical, IAM/SCP guardrail, backup/ASG recovery plan |
| Windows password retrieval | `ec2:GetPasswordData` | Lộ credential Windows instance nếu private key/permission bị lộ | Restrict action, rotate key pair/credential, prefer SSM Session Manager |
| EC2 metadata credential theft | IMDS role credentials, `sts:GetCallerIdentity` | SSRF/local compromise lấy temporary credential của instance role | Enforce IMDSv2, least-privilege instance profile, egress/SSRF control |
| IAM Roles Anywhere misuse | `rolesanywhere:CreateTrustAnchor`, profile/trust policy/certificate changes | External workload assume role trái phép bằng certificate hoặc trust anchor không được kiểm soát | Certificate lifecycle control, trust anchor/profile review, role trust condition bằng `aws:SourceArn`, CloudTrail alert, least privilege |
| Cognito token/user attribute abuse | `cognito-idp:UpdateUserAttributes`, token misuse | Account takeover hoặc identity attribute tampering | MFA/verification flow, app client hardening, token handling, audit attribute changes |

## IAM And Policy Guardrails

Các action dưới đây không nên cấp rộng cho workload thông thường:

```text
s3:PutBucketPolicy
lambda:AddPermission
lambda:UpdateFunctionCode
rds:ModifyDBSnapshotAttribute
ec2:ModifySnapshotAttribute
ec2:ModifyImageAttribute
ec2:CreateSnapshot
ec2:DescribeInstances
ec2:DescribeSnapshots
ec2:DescribeSecurityGroups
ec2:DescribeVolumes
ec2:TerminateInstances
ec2:GetPasswordData
ec2:ModifyInstanceAttribute
iam:CreateAccessKey
iam:AttachRolePolicy
iam:PutRolePolicy
sts:AssumeRole
```

Nguyên tắc thiết kế:

- Dùng IAM role tạm thời cho workload; hạn chế IAM user/access key dài hạn.
- Tách role đọc dữ liệu, role deploy, role backup và role break-glass.
- Với cross-account access, dùng allowlist account/Organization ID thay vì `Principal: "*"`.
- Dùng SCP hoặc permission boundary để chặn resource sharing ra ngoài Organization nếu môi trường không có nhu cầu đó.
- KMS key policy phải được review cùng S3/EBS/RDS policy; encrypt mà key policy mở rộng vẫn có thể tạo rủi ro.
- Không coi việc “bắt exception AccessDenied trong code” là security control. Control thật nằm ở IAM/resource policy, guardrail và review pipeline.
- Không hard-code static access key trong code để “kiểm soát truy cập”. Với workload AWS-native, instance profile, task role, Lambda execution role hoặc federation ngắn hạn là hướng an toàn hơn.

## Permission Enumeration And Blast Radius

Sau khi có credential hợp lệ, bước quan trọng nhất của attacker thường là xác định identity và quyền thực tế trước khi chọn đường đi tiếp theo. Trong phòng thủ, cần xem các hành vi này là tín hiệu điều tra sớm, không chỉ là lệnh kiểm tra vô hại.

| Hành vi | Ý nghĩa phòng thủ |
|---|---|
| `sts:GetCallerIdentity` từ host, IP, user agent hoặc session name lạ | Credential có thể vừa bị lấy ra khỏi ngữ cảnh ban đầu |
| Nhiều lệnh `Describe*`, `List*`, `Get*` liên tiếp | Principal đang bị enumerate để tìm quyền có thể abuse |
| Nhiều lỗi `AccessDenied` trên IAM, EC2, RDS, S3, Lambda | Có thể là thử quyền bằng tay hoặc bằng tool enumeration |
| Principal ứng dụng gọi API quản trị như snapshot, policy mutation, image sharing | Instance role hoặc service role có blast radius lớn hơn nhu cầu runtime |

Điều cần kiểm soát:

- Mỗi workload role nên có permission boundary rõ: đọc/ghi tài nguyên ứng dụng, không có quyền account administration.
- Tách quyền discovery read-only khỏi quyền mutation nhạy cảm; không cấp `Describe*` quá rộng nếu môi trường yêu cầu hạn chế inventory.
- Alert khi một role ứng dụng bình thường bắt đầu gọi STS/IAM hoặc gọi nhiều service không thuộc baseline.
- Không print hoặc lưu raw response của `DescribeInstances`, `DescribeSnapshots`, `DescribeSecurityGroups`, `DescribeVpcs` vào log/debug artifact. Inventory cloud có thể lộ topology, security group, subnet, public IP, volume/snapshot ID và đường đi tấn công tiếp theo.
- Với incident, luôn map lại `userIdentity.arn`, `sessionContext`, source IP, user agent, assumed role session name và chuỗi API sau thời điểm credential có thể bị lộ.

## Storage And Snapshot Protection

S3:

- Bật S3 Block Public Access ở account/bucket trừ trường hợp public hosting có thiết kế rõ.
- Dùng bucket policy có điều kiện `aws:PrincipalOrgID`, VPC endpoint, TLS và KMS nếu phù hợp.
- Monitor policy/ACL thay đổi, đặc biệt external account principal hoặc wildcard principal.
- Không xem policy `Deny` toàn bộ là thiết kế truy cập hoàn chỉnh. Thiết kế tốt thường là Block Public Access, explicit allow cho principal hợp lệ, condition rõ ràng và kiểm tra bằng Access Analyzer/Config.

RDS/EBS/AMI:

- Snapshot và AMI là dữ liệu có thể mang secret, SSH key, config và database content.
- Restrict quyền create/share snapshot; share chỉ qua approved account.
- Encrypt snapshot bằng KMS key được quản lý chặt; kiểm tra key policy trước khi share.
- Có inventory định kỳ cho public/shared snapshots và shared AMIs.
- Backup plan phải có RPO/RTO, retention, restore test và owner rõ ràng. Việc tạo snapshot lẻ không đủ để kết luận hệ thống có DR tốt.
- Với EC2 launch template hoặc automation, block device mapping cần được review: volume encryption, volume type/size, delete-on-termination và tag propagation.
- Khi điều tra snapshot exfiltration, kiểm tra cả hai lớp: event tạo snapshot (`CreateSnapshot`, `CreateDBSnapshot`) và event mở quyền cho account khác (`ModifySnapshotAttribute`, `ModifyDBSnapshotAttribute`, `ModifyImageAttribute`). Chỉ thấy snapshot được tạo chưa đủ để kết luận đã bị exfiltrate, nhưng là tín hiệu cần correlate với sharing/copy/restore event.

## EC2 Runtime Exposure

EC2 instance bị compromise có thể trở thành điểm pivot vào AWS API nếu instance profile quá rộng.

```text
shell trên EC2
  -> đọc filesystem/env/user data
  -> gọi IMDS để lấy role credential
  -> sts:GetCallerIdentity
  -> enumerate allowed API
  -> create/share snapshot hoặc sửa resource policy
```

Giảm rủi ro:

- Enforce IMDSv2 và giảm metadata hop limit khi kiến trúc cho phép.
- Không lưu secret trong user data, AMI, home directory, log hoặc file config plaintext.
- Dùng SSM Parameter Store/Secrets Manager/KMS thay vì file secret tĩnh.
- Instance role chỉ có quyền ứng dụng cần, không có quyền quản trị account/storage/snapshot.
- Dùng SSM Session Manager thay vì mở SSH/RDP rộng.
- Monitor `sts:GetCallerIdentity`, API discovery bất thường, snapshot/share/policy mutation từ role vốn chỉ nên chạy app.
- Không copy credential tạm thời lấy từ IMDS vào `~/.aws/credentials` hoặc artifact build/log. Nếu cần debug, dùng session ngắn hạn, scope hẹp và cleanup rõ ràng.
- Khi phải kiểm tra metadata trong môi trường được phép, chỉ ghi nhận identity/role/scope cần thiết; không lưu Access Key, Secret Access Key hoặc Session Token vào note vận hành, ticket, chat, shell history hay log pipeline.
- User data chỉ nên chứa bootstrap không nhạy cảm. Nếu cần thay đổi user data, coi đó là thay đổi có rủi ro runtime: review diff, kiểm tra launch template, dừng/chạy lại theo maintenance window và có rollback.
- Sau khi một EC2 bị compromise, coi filesystem, environment variables, home directory, application logs và temporary directory là vùng có thể chứa secret. Điều tra cần thu thập bằng quy trình forensic có kiểm soát, đồng thời rotate secret có khả năng đã xuất hiện trong các vị trí này.
- Hạn chế lateral movement bằng security group tối thiểu, subnet segmentation, VPC Flow Logs/EDR nếu có, và baseline rõ cho traffic east-west. Port scan nội bộ từ một instance ứng dụng bình thường nên được xem là tín hiệu bất thường.

## IAM Roles Anywhere Controls

IAM Roles Anywhere dùng X.509 certificate để workload ngoài AWS lấy temporary credential. Trust boundary không nằm ở một access key tĩnh mà ở ba lớp: trust anchor, profile và IAM role trust policy.

Điểm cần review:

- Trust anchor phải tham chiếu CA được phê duyệt; certificate lifecycle cần có owner, expiry, rotation và revocation process.
- IAM role trust policy nên ràng buộc IAM Roles Anywhere bằng condition như `aws:SourceArn` trỏ tới trust anchor/profile phù hợp.
- Profile nên giới hạn role được assume và dùng session policy để giảm quyền runtime.
- Alert các thay đổi trên trust anchor/profile/role trust policy, đặc biệt khi tạo mới hoặc enable lại resource đã disable.
- Không dùng các API IAM certificate/service-specific credential như một mô hình thay thế cho IAM Roles Anywhere trust anchor; đây là boundary khác và dễ dẫn tới kiểm soát sai.

## Lambda And Serverless Persistence

Lambda có hai bề mặt quan trọng:

- resource-based policy quyết định ai có thể invoke function;
- function code/config quyết định logic runtime thực thi gì.

Guardrail:

- Deploy Lambda qua pipeline có review, artifact integrity và rollback.
- Hạn chế quyền `lambda:AddPermission` và `lambda:UpdateFunctionCode`.
- Review resource policy để tránh external principal không mong muốn.
- Theo dõi CloudTrail events như `AddPermission`, `RemovePermission`, `UpdateFunctionCode`, `UpdateFunctionConfiguration`.
- Dùng alias/version để tách traffic production khỏi code mới; rollback bằng alias shift thay vì sửa tay trong console.

## Deployment And Configuration Management

Các lỗi deployment thường gặp:

- security group quá rộng;
- resource thiếu tag owner/environment/data-classification;
- user data chứa secret hoặc script khó audit;
- block device/snapshot không encrypt;
- IAM role dùng chung quá nhiều workload;
- instance critical không bật termination protection hoặc không nằm sau Auto Scaling/backup recovery path;
- thay đổi manual ngoài IaC không được review.

Guardrail tốt:

- IaC là source of truth cho security group, IAM, Lambda, S3 policy và tagging.
- CI/CD chạy policy-as-code trước khi apply.
- AWS Config/Security Hub hoặc rule nội bộ phát hiện drift.
- Tag bắt buộc cho owner, environment, data classification và cost center.
- Với resource quan trọng, yêu cầu review cho thay đổi security group, user data, launch template, block device mapping và termination protection.

## Detection Map

| Điều cần phát hiện | CloudTrail event / tín hiệu |
|---|---|
| S3 policy/ACL thay đổi | `PutBucketPolicy`, `PutBucketAcl`, `PutPublicAccessBlock` |
| Lambda invoke policy thay đổi | `AddPermission`, `RemovePermission` |
| Lambda code/config thay đổi | `UpdateFunctionCode`, `UpdateFunctionConfiguration` |
| RDS snapshot share | `ModifyDBSnapshotAttribute` |
| EBS snapshot share | `ModifySnapshotAttribute` |
| AMI launch permission thay đổi | `ModifyImageAttribute`, `ResetImageAttribute` |
| EC2 user data thay đổi | `ModifyInstanceAttribute`, `StopInstances`, `StartInstances` |
| EC2 instance bị terminate | `TerminateInstances` |
| Windows password retrieval | `GetPasswordData` |
| EC2 nội bộ scan/pivot | VPC Flow Logs, EDR/process telemetry, security group accept/reject bất thường |
| IAM policy mutation | `AttachRolePolicy`, `PutRolePolicy`, `CreatePolicyVersion`, `CreateAccessKey` |
| STS or permission discovery bất thường | `GetCallerIdentity`, nhiều `AccessDenied`, nhiều `Describe*` từ principal lạ |
| IAM Roles Anywhere boundary thay đổi | `CreateTrustAnchor`, `UpdateTrustAnchor`, `CreateProfile`, `UpdateProfile`, role trust policy update |
| Cognito user attribute change | `UpdateUserAttributes`, admin update user events |

## Cognito And User Attribute Controls

Cognito rủi ro nhất khi token hợp lệ có thể sửa thuộc tính định danh như email/phone mà không có verification hoặc business check đủ mạnh. Khi đó attacker không cần “hack AWS account”; họ lợi dụng flow identity của ứng dụng để chiếm tài khoản người dùng.

Guardrail:

- Không cho app client public dùng auth flow hoặc scope rộng hơn nhu cầu thật.
- Bật MFA hoặc step-up authentication cho hành động nhạy cảm.
- Email/phone change phải có verification và audit trail.
- Token không được log ở frontend, backend, reverse proxy hoặc analytics.
- Monitor `UpdateUserAttributes`, admin update user, password reset và bất thường theo IP/device/user agent.

## Incident Response Checklist

Khi nghi ngờ credential hoặc EC2 role bị abuse:

1. Xác định principal: `userIdentity.arn`, account, session name, source IP, user agent trong CloudTrail.
2. Scope event nhạy cảm: policy mutation, snapshot/AMI sharing, Lambda update, S3 access, STS calls.
3. Revoke hoặc contain credential: disable access key, remove session path nếu có thể, detach risky policy, rotate secrets.
4. Kiểm tra resource policy của S3/Lambda/KMS và sharing attribute của RDS/EBS/AMI.
5. Nếu EC2 liên quan, snapshot forensic theo quy trình nội bộ trước khi terminate; kiểm tra user data, instance profile, IMDS và local secrets.
6. Kiểm tra IAM Roles Anywhere trust anchors/profiles và Cognito user attribute changes nếu CloudTrail cho thấy token hoặc identity flow bị abuse.
7. Rotate secrets có khả năng đã nằm trong filesystem, user data, AMI, snapshot hoặc logs.
8. Thêm guardrail để ngăn lặp lại: SCP, permission boundary, Config rule, pipeline policy, alert CloudTrail.

## Related Pages

- [IAM, Accounts, Organizations And Policy](./01-iam-accounts-organizations-policy.md)
- [Shared Responsibility, Compliance And Threat Protection](./03-shared-responsibility-compliance-and-threat-protection.md)
- [CloudWatch, Alarms, Logs And Budgets](../08-observability-operations-cost/01-cloudwatch-alarms-logs-and-budgets.md)
- [S3 Object Storage Patterns](../05-storage-data-databases/01-s3-object-storage-patterns.md)
- [EC2 Instance Lifecycle, Networking And Cost](../03-compute-ec2-autoscaling/01-ec2-instance-lifecycle-networking-and-cost.md)
