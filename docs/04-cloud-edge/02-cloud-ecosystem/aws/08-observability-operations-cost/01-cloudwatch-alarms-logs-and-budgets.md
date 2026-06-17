# CloudWatch, Alarms, Logs And Budgets

## Overview

AWS operations cần quan sát ba nhóm tín hiệu:

- Runtime signal: metrics, logs, alarms.
- Control plane signal: API activity, config change.
- Cost signal: spend, anomaly, usage driver.

CloudWatch không chỉ là dashboard; nó còn là nền cho alarm, autoscaling trigger và operational feedback loop.

## CloudWatch Metrics

Metric thường dùng:

- EC2 CPUUtilization, status check.
- ALB request count, target response time, 5xx.
- Lambda duration, errors, throttles, concurrent executions.
- SQS queue depth, age of oldest message.
- RDS CPU, connections, storage, replica lag.

Metric tốt phải gần với user impact hoặc bottleneck thật. CPU không phải lúc nào cũng là metric scale tốt.

## CloudWatch Logs

CloudWatch Logs dùng để lưu application/service logs.

Điểm vận hành:

- Đặt retention, tránh để mặc định giữ quá lâu nếu không cần.
- Dùng structured logging khi có thể.
- Tách log group theo service/environment.
- Cẩn thận không log secret/token/customer data.

Lambda thường ghi log trực tiếp vào CloudWatch Logs. EC2/ECS cần agent hoặc log driver.

## Alarms

Alarm nên action được:

- Notify.
- Trigger autoscaling.
- Trigger remediation.
- Mở incident.

Tránh alarm chỉ vì "metric nhìn xấu" nhưng không có impact hoặc action rõ.

Ví dụ alarm tốt:

```text
ALB 5xx rate high for 5 minutes
SQS oldest message age above threshold
RDS free storage low
Lambda errors above baseline
```

## CloudTrail Và Config

CloudTrail ghi lại AWS API activity: ai gọi gì, khi nào, từ đâu. Nó quan trọng cho audit và incident response.

AWS Config theo dõi resource configuration và compliance rule. Config trả lời câu hỏi "resource đã thay đổi như thế nào theo thời gian".

Kết hợp:

```text
CloudTrail -> ai thay đổi
AWS Config -> resource thay đổi thành gì
CloudWatch -> runtime có ảnh hưởng không
```

## Budgets Và Cost Governance

Cost control nên có từ đầu:

- AWS Budgets cho cảnh báo spend.
- Cost Explorer để phân tích service/account/tag.
- Cost allocation tags.
- Anomaly detection nếu môi trường lớn.
- Lifecycle/retention cho S3/log/snapshot.

Không đợi cuối tháng mới xem bill.

## Related Pages

- [AWS Operating Model And Service Scope](../00-fundamentals/02-aws-operating-model-and-service-scope.md)
- [Auto Scaling, Load Balancing And Dynamic Capacity](../03-compute-ec2-autoscaling/02-auto-scaling-load-balancing-and-dynamic-capacity.md)
- [Lambda, EventBridge And SQS](../06-serverless-event-driven/01-lambda-eventbridge-and-sqs.md)
