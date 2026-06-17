# CLI, SDK, CloudFormation And SAM

## Overview

AWS có nhiều lớp automation:

- AWS CLI cho thao tác lệnh và script.
- SDK cho application/tool tự gọi AWS API.
- CloudFormation cho Infrastructure as Code native của AWS.
- SAM/CDK/Terraform là các lớp cao hơn tùy nhu cầu.

Điểm chung: mọi lớp đều nên hướng tới quản lý hạ tầng theo desired state, có review và có khả năng rollback.

## AWS CLI

AWS CLI phù hợp cho:

- Kiểm tra nhanh resource.
- Script vận hành.
- Runbook read-only.
- Automation nhỏ trong CI/CD.

Ví dụ:

```bash
aws sts get-caller-identity
aws ec2 describe-instances
aws s3 ls
```

Trước khi chạy lệnh thay đổi production, luôn xác nhận account, region và profile:

```bash
aws sts get-caller-identity
aws configure list
echo "$AWS_PROFILE"
echo "$AWS_REGION"
```

CLI script là "executable documentation", nhưng vẫn là imperative automation: script nói từng bước phải làm, không tự động hiểu toàn bộ desired state như CloudFormation/Terraform. Vì vậy script production cần:

- `set -euo pipefail` hoặc cơ chế fail-fast tương đương.
- Pre-check account/region/profile trước mọi lệnh thay đổi.
- Read-only discovery trước khi create/update/delete.
- Idempotency hoặc logic kiểm tra resource đã tồn tại.
- Cleanup path rõ cho resource tạm như security group, EC2, Elastic IP.
- Không ghi access key/secret vào script, log hoặc shell history.

Với output JSON, dùng `--query`/JMESPath để lấy đúng field thay vì parse text thủ công:

```bash
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query "Reservations[].Instances[].InstanceId" \
  --output text
```

## SDK

SDK phù hợp khi application cần gọi AWS service:

- Upload object lên S3.
- Publish message vào SQS/SNS.
- Query DynamoDB.
- Start/stop workflow.

Không hard-code credential trong code. Dùng IAM role cho EC2, Lambda, ECS task role hoặc workload identity tương ứng.

SDK thường xử lý authentication chain, request signing, retry/backoff, HTTPS transport và JSON serialization. Điểm cần thiết kế là boundary của application:

```text
application code
-> AWS SDK client
-> IAM role / temporary credential
-> AWS API
-> CloudTrail evidence
```

Khi SDK tạo hoặc xóa hạ tầng, áp dụng cùng tiêu chuẩn với IaC: least privilege, dry-run/plan nếu service hỗ trợ, idempotency token khi có, structured logging và rollback/cleanup rõ ràng.

## CloudFormation Mental Model

CloudFormation template mô tả resource và dependency. Stack là đơn vị deploy/update/delete.

Các phần thường gặp:

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: Example stack
Parameters: {}
Resources: {}
Outputs: {}
```

Core idea:

- Template là desired state.
- Stack là trạng thái CloudFormation quản lý.
- Change set giúp xem trước thay đổi.
- Update có thể replace resource nếu property yêu cầu.
- Deletion policy quan trọng với data resource.

CloudFormation không chỉ tạo resource riêng lẻ. Nó tạo cả dependency graph: load balancer, instance/ASG, database, security group, IAM role, output endpoint và tag. Khi stack tạo xong, `Outputs` thường là contract để operator hoặc pipeline biết endpoint/tên resource cần dùng.

Với application stack hoàn chỉnh, template thường không chỉ có compute. Nó nên mô tả rõ các dependency vận hành:

- Storage/data resource như S3 bucket, DynamoDB table, RDS instance hoặc queue.
- Compute/deployment layer như ASG, Elastic Beanstalk, ECS service hoặc Lambda.
- IAM role riêng cho từng runtime, ví dụ API server được gửi message và ghi object, worker được nhận/xóa message và cập nhật state.
- DLQ, alarm, log group, metric và output endpoint.
- Parameter cho environment-specific value, nhưng không chứa secret thô.

Tách role theo runtime giúp blast radius nhỏ hơn. Một web/API server không nhất thiết cần quyền `sqs:ReceiveMessage` hay `sqs:DeleteMessage`; worker không nhất thiết cần quyền tạo job mới. Nếu template buộc phải cấp quyền rộng vì nền tảng managed yêu cầu, cần ghi rõ lý do và theo dõi để thu hẹp khi có thể.

Phân biệt quan trọng:

| Khái niệm | Ý nghĩa |
|---|---|
| Template | source mô tả desired state |
| Stack | một bản triển khai cụ thể từ template |
| Parameter | input để customize stack |
| Resource | object CloudFormation quản lý |
| Output | value expose ra ngoài stack |
| Reference / dependency | quan hệ để CloudFormation tính thứ tự tạo/update/delete |

CloudFormation dùng declarative/descriptive approach: người vận hành mô tả trạng thái mong muốn, còn engine tính dependency graph và thứ tự API call. Đây là lý do template dễ review hơn một chuỗi click hoặc script dài.

## CloudFormation Safety

Trước khi update:

1. Tạo change set.
2. Review resource create/update/delete/replace.
3. Kiểm tra resource có data không.
4. Xác định rollback behavior.
5. Xác nhận đúng account/region.

Với resource chứa dữ liệu như RDS, S3, EBS, DynamoDB, cần cân nhắc:

```yaml
DeletionPolicy: Retain
UpdateReplacePolicy: Retain
```

Khi xóa stack, CloudFormation có thể xóa hầu hết resource mà nó quản lý. Đây là điểm mạnh cho lab/ephemeral environment, nhưng là thao tác nguy hiểm trong production.

Pre-check trước khi delete stack:

```bash
aws sts get-caller-identity
aws cloudformation describe-stacks --stack-name <stack-name>
aws cloudformation list-stack-resources --stack-name <stack-name>
```

Guardrails:

- Xác nhận đúng account, region, stack name và owner.
- Kiểm tra resource chứa dữ liệu: RDS, S3, EBS, EFS, DynamoDB.
- Snapshot/backup hoặc export dữ liệu trước nếu có yêu cầu khôi phục.
- Dùng `DeletionPolicy: Retain` cho data resource không được phép mất.
- Sau khi delete, verify resource thật sự biến mất hoặc được retain đúng chủ đích; đồng thời kiểm tra chi phí còn lại như NAT Gateway, Elastic IP, snapshot, log retention.

## EC2 User Data Và Bootstrap

CloudFormation có thể truyền `UserData` cho EC2 để chạy bootstrap script khi instance boot. Pattern này hữu ích để biến một AMI nền thành instance đã cài package, config service và đăng ký vào workload.

Mental model:

```text
AMI nền
-> EC2 launch
-> cloud-init / user data
-> package install + config render
-> service start
-> health check
```

Guardrails:

- User data chạy với quyền cao trong OS; review như production script.
- Không đặt secret dài hạn trong user data, vì instance có thể đọc lại metadata/user-data và log boot có thể lộ nội dung.
- Script phải idempotent hoặc fail rõ ràng; tránh trạng thái nửa cài đặt nửa lỗi.
- Log bootstrap nên được ship ra ngoài instance để debug khi SSH/SSM không vào được.
- Với bootstrap lớn, cân nhắc golden AMI, image pipeline, configuration management hoặc artifact deploy riêng.

Khi cập nhật ứng dụng bằng cách "start from scratch", flow an toàn hơn là:

```text
build artifact / image / AMI
-> launch instance mới từ template
-> chạy bootstrap
-> health check + smoke test
-> chuyển traffic qua LB/DNS
-> giữ instance cũ đủ lâu để rollback
-> terminate instance cũ sau khi xác nhận
```

Đây là biến thể gần với blue/green hoặc immutable deployment. Không nên cập nhật thủ công trực tiếp trên instance đang phục vụ production nếu muốn rollback đáng tin cậy.

## AWS Deployment Service Fit

Các dịch vụ như Elastic Beanstalk, OpsWorks hoặc các lớp deployment managed khác nên được chọn theo trade-off giữa convention và control, không theo việc "service nào có wizard nhanh hơn".

| Mô hình | Phù hợp khi | Rủi ro cần kiểm tra |
|---|---|---|
| CloudFormation + user data/script | môi trường custom, cần control cao | script dài, secret leakage, bootstrap fail, rollback thủ công |
| Managed application platform | web app theo runtime/convention được hỗ trợ | lock-in, platform version, extension point, giới hạn cấu hình |
| Configuration management layer | nhiều layer/service trên VM, cần quản lý package/config | tool lifecycle, agent/recipe drift, quyền quá rộng |

Trước khi chọn một AWS deployment service cho production, luôn kiểm tra tài liệu AWS hiện tại về service availability, supported platform/runtime, lifecycle/deprecation notice và migration path.

## SAM

AWS SAM là extension cho serverless application, thường dùng cho Lambda/API Gateway/EventBridge/SQS.

SAM giúp:

- Đóng gói function code.
- Định nghĩa event source.
- Deploy serverless stack qua CloudFormation.
- Local invoke/test ở mức nhất định.

SAM phù hợp khi serverless app còn nhỏ/vừa và muốn dùng abstraction đơn giản hơn CloudFormation thô.

## Khi Dùng Terraform

Trong vault này Terraform nằm ở domain IaC riêng. Với AWS, Terraform phù hợp khi:

- Cần multi-cloud hoặc provider ecosystem rộng.
- Team đã chuẩn hóa Terraform workflow.
- Muốn module hóa hạ tầng theo platform boundary.

CloudFormation/CDK phù hợp khi muốn bám sát AWS-native control plane.

## Related Pages

- [AWS Operating Model And Service Scope](../00-fundamentals/02-aws-operating-model-and-service-scope.md)
- [Terraform Overview](../../../../05-infrastructure-automation/04-infrastructure-as-code/01-terraform/overview.md)
- [Lambda, EventBridge And SQS](../06-serverless-event-driven/01-lambda-eventbridge-and-sqs.md)
