# Lambda, EventBridge And SQS

## Overview

Serverless trên AWS giúp chạy code hoặc workflow mà không quản lý server trực tiếp. Lambda phù hợp cho function ngắn, stateless, event-driven. EventBridge và SQS giúp decouple producer/consumer.

Serverless không có nghĩa là không vận hành. Bạn vẫn phải quản lý IAM, timeout, retry, DLQ, concurrency, observability, cost và idempotency.

## Lambda Mental Model

Lambda chạy function theo event:

```text
Event source -> Lambda runtime -> handler -> AWS service/API/backend
```

Use case:

- API backend nhỏ.
- Scheduled task.
- Event processing.
- Automation/remediation.
- Glue logic giữa các AWS services.

Không phù hợp nếu:

- Process chạy rất lâu.
- Cần local state bền.
- Cần runtime/kernel control sâu.
- Dependency quá lớn hoặc cold start không chấp nhận được.

## IAM Role For Lambda

Lambda cần execution role:

- Ghi log vào CloudWatch Logs.
- Đọc/ghi S3, DynamoDB, SQS hoặc service khác nếu function cần.
- Không cấp wildcard rộng nếu không cần.

Pattern:

```text
Lambda function
  -> execution role
  -> least privilege policy
```

## Lambda In VPC

Lambda có thể attach vào VPC để gọi private resource. Khi đó cần chú ý:

- Subnet và security group.
- Route ra Internet nếu function cần gọi public endpoint.
- NAT Gateway hoặc VPC Endpoint.
- DNS và timeout.

Nếu Lambda chỉ gọi public AWS service, không nhất thiết phải đưa vào VPC.

## EventBridge

EventBridge phù hợp cho event-driven automation:

- Nhận AWS service event.
- Route event theo rule.
- Trigger Lambda, Step Functions, SQS hoặc target khác.

Use case:

- Tự động tag EC2 instance khi tạo.
- Remediation khi config thay đổi.
- Workflow phản ứng theo event business.

## SQS

SQS là managed queue để decouple producer và consumer.

Core ideas:

- Producer gửi message.
- Consumer poll message.
- Visibility timeout che message trong lúc xử lý.
- Nếu xử lý fail, message quay lại queue.
- DLQ giữ message lỗi sau nhiều lần retry.

SQS không phải message broker đầy đủ. Standard queue không đảm bảo ordering tuyệt đối; FIFO queue có ordering theo message group nhưng throughput/trade-off khác.

Workflow xử lý message an toàn:

```text
Producer
-> SendMessage vào queue
-> Consumer poll message
-> Message bị ẩn trong visibility timeout
-> Consumer xử lý side effect
-> DeleteMessage sau khi xử lý thành công
-> Nếu fail hoặc timeout, message hiện lại để retry
```

Điểm quan trọng là acknowledgement của SQS nằm ở `DeleteMessage`, không phải lúc consumer nhận được message. Vì vậy worker phải chỉ delete sau khi đã commit kết quả cần thiết. Nếu xử lý lâu hơn `VisibilityTimeout`, cùng một message có thể bị worker khác nhận lại và tạo duplicate side effect.

Production guardrails:

- Dùng long polling để giảm empty receive và chi phí poll.
- Đặt `VisibilityTimeout` dài hơn p95/p99 processing time, hoặc extend visibility cho job dài.
- Gắn DLQ với `maxReceiveCount` hợp lý để cô lập poison message.
- Dùng retry với backoff/jitter ở worker, tránh retry dồn dập vào downstream đang lỗi.
- Scale worker theo queue depth, age of oldest message hoặc backlog per worker, không chỉ theo CPU.
- Theo dõi `ApproximateAgeOfOldestMessage`, queue depth, receive/delete rate, DLQ depth và error rate của consumer.
- Không đặt secret hoặc dữ liệu nhạy cảm trực tiếp trong message nếu không cần; lưu payload lớn/nhạy cảm ở S3 hoặc DB riêng và gửi reference đã kiểm soát quyền.
- Với kết quả trả về cho user, dùng trạng thái `pending/processing/succeeded/failed` và correlation ID/job ID thay vì bắt client chờ request dài.

SQS Standard phù hợp khi ưu tiên throughput và chấp nhận at-least-once delivery. Nếu cần ordering theo một nhóm nghiệp vụ, dùng FIFO queue với `MessageGroupId` và hiểu rõ trade-off throughput. Nếu một event cần fanout đến nhiều consumer độc lập, đặt SNS/EventBridge phía trước nhiều SQS queue thay vì để nhiều consumer cạnh tranh trên cùng một queue.

## Queue-Based Scaling

Queue là metric tốt cho worker pool vì backlog thể hiện công việc chưa xử lý. Mental model:

```text
Producer rate
-> queue depth / age
-> worker capacity
-> downstream capacity
-> DLQ/error rate
```

Không nên chỉ scale theo số message nhìn thấy. Một queue có 1.000 message nhưng worker xử lý rất nhanh có thể ít nghiêm trọng hơn queue có 50 message nhưng `ApproximateAgeOfOldestMessage` tăng liên tục. Scaling policy nên cân nhắc:

- Queue depth hoặc backlog per worker.
- Age of oldest message để đo user-facing delay.
- Processing duration p95/p99.
- Error rate và DLQ depth.
- Downstream limit, ví dụ DB/API/S3 rate hoặc external service quota.

Scale out worker quá nhanh có thể chuyển nghẽn từ queue sang database, object storage hoặc API bên ngoài. Đặt `max` capacity, backoff và circuit breaker để bảo vệ downstream. Scale in nên chậm và có drain/visibility timeout phù hợp để không làm job đang xử lý bị duplicate quá nhiều.

## Idempotency

Event-driven system phải giả định message/function có thể chạy lại.

Function/worker nên idempotent:

- Dùng idempotency key.
- Ghi trạng thái xử lý.
- Không tạo side effect trùng lặp khi retry.
- Có DLQ và replay strategy.

## Related Pages

- [CLI, SDK, CloudFormation And SAM](../04-infrastructure-as-code-automation/01-cli-sdk-cloudformation-and-sam.md)
- [High Availability, Decoupling And Fault Tolerance](../09-architecture-resilience/01-high-availability-decoupling-and-fault-tolerance.md)
- [CloudWatch, Alarms, Logs And Budgets](../08-observability-operations-cost/01-cloudwatch-alarms-logs-and-budgets.md)
