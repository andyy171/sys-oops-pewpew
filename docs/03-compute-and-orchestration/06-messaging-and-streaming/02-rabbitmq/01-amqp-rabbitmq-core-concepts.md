# AMQP And RabbitMQ Core Concepts

## Overview

Message-oriented middleware (MOM) dùng broker/queue để tách producer và consumer theo thời gian. Producer có thể gửi message rồi tiếp tục; consumer có thể xử lý sau, miễn broker giữ được message theo durability/retention policy.

AMQP là protocol cho message-oriented communication. RabbitMQ là broker phổ biến dựa trên AMQP 0-9-1 và có hỗ trợ AMQP 1.0 tùy plugin/version. Trong vận hành, cần tách rõ protocol AMQP, broker RabbitMQ, queue/exchange topology và application semantics.

## Producer / Broker / Consumer Model

```text
producer
-> exchange / broker routing
-> queue
-> consumer
-> acknowledgement
```

Các object chính:

| Object | Vai trò |
| --- | --- |
| Producer | Application publish message |
| Exchange | Nhận message từ producer và route tới queue theo type/routing key/binding |
| Queue | Nơi message được lưu cho consumer |
| Binding | Rule nối exchange với queue |
| Consumer | Application đọc message và ack/nack |
| Connection | TCP connection tương đối lâu dài tới broker |
| Channel | Logical stream bên trong connection, dùng để publish/consume hiệu quả hơn |

Exchange không phải nơi lưu message lâu dài; queue mới là nơi giữ message cho consumer. Nếu route không match queue nào và không có policy xử lý, message có thể bị drop hoặc trả về tùy cấu hình publish.

## Transient vs Persistent Messaging

Transport socket thường là transient: receiver không sẵn sàng thì message có thể mất. Message queue hướng tới persistent asynchronous communication: broker nhận, lưu và deliver sau.

Persistence không tự động có nghĩa là không mất dữ liệu. Cần phối hợp:

- durable queue/exchange;
- persistent message;
- publisher confirm;
- consumer acknowledgement;
- disk/replication/quorum policy của broker;
- retry và dead letter topology.

Nếu thiếu một trong các lớp này, hệ thống có thể "trông như queue bền vững" nhưng vẫn mất message khi broker restart, network partition hoặc consumer crash.

## AMQP Communication Model

AMQP tách connection, channel/session, link/message transfer và settlement:

- Connection thường map xuống TCP connection.
- Channel giúp multiplex nhiều luồng logic trên một connection.
- Flow control có thể dùng credit để receiver kiểm soát sender gửi bao nhiêu message.
- Message có trạng thái unsettled cho tới khi bên nhận/broker xác nhận outcome.
- Settlement quyết định khi nào sender/broker được phép quên message.

Operationally, hãy theo dõi connection count, channel count, flow control/blocking, publisher confirm latency và consumer ack latency. Một broker còn sống nhưng đang flow-control producer vẫn có thể làm application tăng latency hoặc backlog.

## Queue Operations

Mô hình queue cơ bản:

| Operation | Ý nghĩa |
| --- | --- |
| `PUT` / publish | Producer đưa message vào broker/exchange |
| `GET` / consume | Consumer lấy message từ queue |
| `POLL` | Kiểm tra không blocking |
| `NOTIFY` / subscription | Broker gọi consumer khi có message |

Trong RabbitMQ thực tế, consumer thường dùng subscription/push model thay vì polling liên tục. Polling quá dày tạo load không cần thiết; polling quá thưa làm tăng latency xử lý.

## Message Broker And Integration

Message broker giúp tích hợp nhiều application bằng routing, transformation hoặc mediation. Tuy vậy broker không xóa được complexity của schema và business semantics:

- Sender và receiver vẫn phải thống nhất message contract.
- Transformation plugin/rule là code vận hành production, cần versioning và rollback.
- Broker là dependency trung tâm, cần HA, capacity planning và observability.
- Message format linh hoạt như JSON/XML/Avro/Protobuf chỉ giải quyết encoding; không tự giải quyết semantic compatibility.

## Failure Modes

| Symptom | Kiểm tra |
| --- | --- |
| Queue depth tăng | consumer down/chậm, downstream dependency chậm, prefetch quá cao/thấp |
| Producer latency tăng | broker flow control, disk alarm, network issue, publisher confirm chậm |
| Message duplicate | consumer ack sau xử lý bị mất, retry, reconnect, redelivery |
| Message mất | queue/message không durable, publish không confirm, route không match, TTL/expiration |
| Poison message loop | consumer luôn fail cùng một message, thiếu DLX/retry cap |
| Ordering sai | nhiều consumer, redelivery, retry queue hoặc route nhiều queue |

## Safe Checks

RabbitMQ read-only hoặc ít xâm lấn:

```bash
rabbitmqctl status
rabbitmqctl list_queues name messages messages_ready messages_unacknowledged consumers
rabbitmqctl list_exchanges name type durable auto_delete
rabbitmqctl list_bindings source_name source_kind destination_name destination_kind routing_key
rabbitmqctl list_connections name state channels
rabbitmqctl list_channels connection number consumer_count messages_unacknowledged
```

Các lệnh này có thể lộ tên queue/exchange/vhost nội bộ trong output. Không đưa output thật chứa customer data, hostname nội bộ hoặc tenant name vào KB/report public.

## Production Guardrails

- Không delete queue khi còn message nếu chưa có quyết định data-loss rõ.
- Không đổi routing key, binding, exchange type hoặc DLX trong incident nếu chưa hiểu message sẽ đi đâu.
- Dùng publisher confirm cho message quan trọng; "publish call returned" không luôn đồng nghĩa broker đã persist an toàn.
- Consumer phải idempotent vì at-least-once delivery có thể tạo duplicate.
- Đặt retry cap và dead-letter queue để tránh poison message làm kẹt toàn pipeline.
- Theo dõi queue depth, message age, publish/consume rate, ack rate, redelivery rate, disk alarm, memory alarm và connection/channel count.
- Backup/restore broker không thay thế application-level reconciliation; queue thường là transport/state tạm thời, không nên là system of record duy nhất.

## Related Pages

- [Distributed System Architecture Styles](../../../01-architecture/03-patterns/06-distributed-system-architecture-styles.md)
- [Kafka Components](../01-kafka/01-core-concepts/components.md)
