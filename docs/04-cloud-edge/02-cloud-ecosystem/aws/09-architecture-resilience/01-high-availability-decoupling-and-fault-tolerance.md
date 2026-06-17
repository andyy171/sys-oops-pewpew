# High Availability, Decoupling And Fault Tolerance

## Overview

AWS resilience không đến từ một service đơn lẻ. Nó đến từ cách kết hợp fault domain, load balancing, autoscaling, durable storage, queue, retry, idempotency và observability.

Core principle:

```text
Assume failure -> isolate blast radius -> retry safely -> recover automatically -> observe impact
```

## Fault Domains

| Fault domain | Ví dụ ảnh hưởng | Pattern giảm rủi ro |
| --- | --- | --- |
| Instance | EC2 hỏng | ASG replace instance |
| AZ | subnet/EBS/instance trong AZ mất | multi-AZ ALB/ASG/RDS/EFS |
| Region | regional service unavailable | multi-region DR, Route 53 failover |
| Dependency | DB/API/queue chậm hoặc lỗi | timeout, retry, circuit breaker, queue |

Không phải service nào cũng multi-AZ hoặc multi-region theo cùng cách. Cần đọc service scope trước khi thiết kế.

Một nhầm lẫn phổ biến là coi "khôi phục lại một instance" tương đương "ứng dụng đã HA". EC2 instance chạy trong một subnet/AZ; nếu state nằm trong root EBS hoặc local disk, thay instance có thể khôi phục compute nhưng chưa chắc khôi phục được dữ liệu, endpoint hoặc session.

Phân loại nhanh:

| Kiểu recovery | Xử lý được | Không xử lý được tốt |
|---|---|---|
| EC2 recovery action theo status check | host/system failure trong cùng AZ, giữ instance identity tùy điều kiện | AZ outage, instance store, app-level failure |
| ASG replace instance | instance unhealthy/terminated, có thể chạy multi-AZ | state local, endpoint IP cố định, bootstrap không idempotent |
| Multi-AZ managed service | AZ failure trong phạm vi service hỗ trợ | region-wide outage, bad write, lỗi app/schema |

Thiết kế resilience phải nối compute recovery với data recovery và endpoint recovery:

```text
Compute: instance/container/function có được thay tự động không?
Data: state nằm ở đâu, RPO là bao nhiêu?
Endpoint: client sẽ tìm backend mới bằng DNS/LB/service discovery nào?
Validation: health check đo app thật hay chỉ đo máy còn sống?
```

## High Availability Pattern

Web workload cơ bản:

```text
Route 53
  -> ALB across AZs
  -> Auto Scaling Group across AZs
  -> stateless app instances
  -> managed data service
```

Yêu cầu:

- App stateless hoặc state externalized.
- Health check đúng.
- Deploy qua template/AMI/container image.
- Data tier có backup/replication phù hợp.

## Synchronous Decoupling

Load balancer là synchronous decoupling:

```text
Client waits
  -> Load Balancer
  -> Backend
  -> Response
```

Phù hợp request/response web/API. Nhưng nếu backend xử lý lâu hoặc dễ fail, client vẫn bị ảnh hưởng.

Mental model: synchronous decoupling che giấu danh tính backend, không che giấu latency của công việc. Nó phù hợp với tác vụ ngắn, cần trả response ngay, có timeout rõ ràng và retry an toàn ở client hoặc gateway.

## Asynchronous Decoupling

Queue là asynchronous decoupling:

```text
Producer
  -> Queue
  -> Worker
  -> Result/side effect
```

Ưu điểm:

- Absorb traffic spike.
- Retry worker failure.
- Scale worker theo backlog.
- Giảm coupling giữa producer và consumer.

Nhược điểm:

- Eventual consistency.
- Cần idempotency.
- Cần DLQ/replay.
- User experience cần thiết kế trạng thái pending/processing.

Mental model: asynchronous decoupling tách request nhận việc khỏi việc hoàn tất. Producer nên trả về job ID hoặc status URL, worker xử lý sau, còn user/API đọc trạng thái từ store bền vững. Pattern này giảm áp lực peak traffic nhưng chuyển độ phức tạp sang idempotency, retry, observability và quy trình xử lý DLQ.

## Retry Và Idempotency

Retry mà không idempotency có thể gây double charge, duplicate order, duplicate email hoặc inconsistent state.

Pattern:

- Dùng idempotency key.
- Ghi trạng thái operation.
- Thiết kế state transition rõ ràng.
- Retry với backoff/jitter.
- Có DLQ và manual replay.

Với workflow nhiều bước, cách an toàn là biến nghiệp vụ thành state machine nhỏ và chỉ cho phép transition hợp lệ. Ví dụ một job xử lý file có thể đi qua:

```text
Created -> Uploaded -> Processed
```

API hoặc worker không cần lưu tiến độ nội bộ như "upload 30%" nếu hệ thống chỉ cần biết mốc hoàn tất. Điều quan trọng là mỗi transition phải idempotent:

- Lặp lại `Created -> Uploaded` với cùng id/file key không tạo thêm job sai.
- Lặp lại `Uploaded -> Processed` không ghi đè kết quả đã commit bằng dữ liệu lỗi.
- Message duplicate từ queue không làm side effect bên ngoài bị nhân đôi.
- Transition không hợp lệ phải fail rõ ràng và không mutate state.

Khi một bước gọi hệ thống bên thứ ba không hỗ trợ idempotency, không phải lúc nào cũng đạt được "exactly once". Team phải chọn rủi ro nghiệp vụ: chấp nhận at-least-once, at-most-once, hoặc thêm reconciliation/manual review. Đây là quyết định sản phẩm và vận hành, không chỉ là chi tiết code.

Pre-check cho retry/idempotency trong production:

1. Mỗi request/job có correlation ID hoặc idempotency key.
2. State nằm trong store bền vững, không nằm trên local disk của worker.
3. Update state dùng conditional write/optimistic locking nếu có concurrent writer.
4. Side effect bên ngoài có log/audit để reconcile.
5. DLQ có alert và runbook replay an toàn.

## RTO Và RPO

| Khái niệm | Câu hỏi |
| --- | --- |
| RTO | mất bao lâu để khôi phục service? |
| RPO | có thể mất tối đa bao nhiêu dữ liệu? |

Thiết kế DR phải bắt đầu từ RTO/RPO, không bắt đầu từ tên service.

RTO/RPO cần gắn với từng failure mode. Ví dụ cùng một Jenkins/EC2 đơn lẻ:

- Host failure cùng AZ: EC2 recovery hoặc ASG có thể đưa service lên lại sau một khoảng downtime ngắn.
- AZ outage: ASG multi-AZ có thể tạo instance mới ở AZ khác, nhưng dữ liệu trên EBS AZ cũ không tự đi theo.
- Bad config hoặc xóa nhầm job: replication/ASG không giúp; cần backup/snapshot/versioning và restore test.

Nếu RPO phải gần bằng 0, đừng dựa vào snapshot thưa của một EBS volume đơn lẻ. Hãy tách state sang managed storage/database multi-AZ hoặc hệ thống replication được vận hành nghiêm túc. Nếu RTO ngắn, bootstrap instance phải nhanh, image phải được chuẩn hóa và health check/cutover phải tự động.

## Related Pages

- [Disaster Recovery And Resilience](../disaster-recovery-and-resilience.md)
- [Auto Scaling, Load Balancing And Dynamic Capacity](../03-compute-ec2-autoscaling/02-auto-scaling-load-balancing-and-dynamic-capacity.md)
- [Lambda, EventBridge And SQS](../06-serverless-event-driven/01-lambda-eventbridge-and-sqs.md)
