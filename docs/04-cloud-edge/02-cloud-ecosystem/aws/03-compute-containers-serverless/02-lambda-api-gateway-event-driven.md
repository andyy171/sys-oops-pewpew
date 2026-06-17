# Lambda, API Gateway And Event-Driven Compute

## Overview

Lambda phù hợp cho workload stateless, event-driven, thời gian chạy ngắn và không muốn quản lý server. API Gateway thường đứng trước Lambda để tạo REST/HTTP API. SQS, SNS và EventBridge giúp decouple producer/consumer để hệ thống scale bền hơn.

## Core Services

| Service | Vai trò |
|---|---|
| Lambda | Chạy function theo event |
| API Gateway | Expose HTTP API, auth/throttling/integration |
| SQS | Queue bền, decouple producer/consumer |
| SNS | Pub/sub fanout |
| EventBridge | Event bus, routing theo rule |
| Step Functions | Orchestrate workflow nhiều bước |

## Common Patterns

| Requirement | Pattern |
|---|---|
| Upload ảnh rồi xử lý async | S3 event -> SQS -> Lambda |
| Đơn hàng phải xử lý đúng thứ tự | API Gateway -> SQS FIFO -> Lambda/worker |
| Spike ghi vào database làm Lambda quá tải DB | Lambda nhận request -> SQS -> Lambda worker -> DB |
| Một event cần nhiều consumer | SNS topic -> nhiều SQS subscriptions |
| Workflow dài hơn giới hạn Lambda hoặc nhiều bước | Step Functions |

## Why Queue Between Event And Lambda

Không phải lúc nào cũng nên gọi Lambda trực tiếp từ event source. Queue ở giữa giúp:

- Buffer burst traffic.
- Retry có kiểm soát.
- Tách tốc độ producer và consumer.
- Giảm nguy cơ mất event khi downstream lỗi.
- Cho phép scale worker theo queue depth.

## Database Connection Note

Lambda scale nhanh có thể tạo quá nhiều connection tới RDS/Aurora. Với relational database, cân nhắc RDS Proxy, queue-based ingestion hoặc chuyển access pattern phù hợp sang DynamoDB.

## Related Pages

- [RDS, Aurora, DynamoDB And Caching](../05-storage-data-databases/03-rds-aurora-dynamodb-caching.md)
- [CloudWatch, Config, CloudTrail And Cost](../06-observability-operations-cost/01-cloudwatch-config-cloudtrail-cost.md)
