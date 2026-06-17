# Distributed Systems Foundations

Distributed system là hệ thống trong đó process, data hoặc resource được đặt trên nhiều máy và phối hợp qua network để cung cấp một service có vẻ thống nhất với người dùng.

Điểm quan trọng không phải là "càng phân tán càng tốt". Phân tán chỉ đáng làm khi nó giải quyết một nhu cầu thật: scale capacity, giảm latency theo vị trí, tăng availability/durability, chia sẻ resource, hoặc vượt qua ranh giới tổ chức.

## Distributed Vs Decentralized

Nên tách hai câu hỏi:

- **Distributed:** process/resource được spread đủ để đạt mục tiêu kỹ thuật như scale, HA, locality hoặc fault tolerance.
- **Decentralized:** process/resource bắt buộc phải spread vì ranh giới không thể gom lại, ví dụ nhiều tổ chức độc lập, dữ liệu không được rời domain, thiếu trust chung, hoặc hệ thống trải rộng theo vị trí vật lý.

Một service có thể **logically centralized** nhưng **physically distributed**. DNS là ví dụ kinh điển: namespace nhìn như một cây logic, nhưng backend phục vụ bởi nhiều server và replica. Vì vậy, không nên kết luận "centralized" là không scale hoặc luôn là single point of failure chỉ từ sơ đồ logic.

Production rule:

- Bắt đầu bằng thiết kế đơn giản nhất có thể vận hành được.
- Chỉ thêm distribution khi bottleneck, failure domain, latency hoặc ownership boundary đã rõ.
- Mỗi điểm phân tán mới phải có observability, ownership, retry/backoff, failure handling và runbook.

## Distribution Transparency

Distribution transparency là nỗ lực che bớt việc hệ thống thật ra nằm trên nhiều node. Nó hữu ích cho UX và developer ergonomics, nhưng không miễn phí.

| Loại transparency | Ý nghĩa | Rủi ro nếu che quá mức |
|---|---|---|
| Access | Cùng một interface dù backend/OS/data format khác nhau | Ẩn serialization, compatibility hoặc protocol mismatch |
| Location | Client không cần biết resource nằm ở đâu | Debug routing, DNS, region và data residency khó hơn |
| Relocation / migration | Resource/process có thể di chuyển mà client ít bị ảnh hưởng | Session, connection state và in-flight request dễ lỗi |
| Replication | Client không cần biết có nhiều bản sao | Stale read, conflict, quorum và failover semantics bị hiểu sai |
| Concurrency | Nhiều client dùng chung resource mà không phá state | Lock contention, lost update, transaction conflict |
| Failure | Lỗi và recovery được che khỏi user | Retry storm, timeout kéo dài, khó phân biệt slow với dead |

Không nên cố đạt transparency tuyệt đối. Network latency, partial failure, stale replica và security boundary là sự thật vận hành; nếu che hoàn toàn, application và operator thường đưa ra giả định sai.

## Openness And Interface Contracts

Open distributed system không chỉ là open source. Nó là hệ thống có component có thể tích hợp, thay thế hoặc mở rộng qua interface contract rõ ràng.

Một interface tốt cần hai lớp:

- **Syntax:** method, parameter, response, error type, schema.
- **Semantics:** operation thật sự làm gì, idempotency ra sao, retry có an toàn không, consistency guarantee là gì, timeout có nghĩa là thất bại hay chưa biết kết quả.

Trong production, interface thiếu semantics thường gây lỗi hơn interface thiếu field. Ví dụ RPC timeout không khẳng định remote side chưa thực hiện write; client cần idempotency key, retry budget hoặc reconciliation path.

## Policy Vs Mechanism

Mechanism là khả năng nền tảng cung cấp; policy là quyết định khi nào và dùng như thế nào.

Ví dụ cache:

- Mechanism: lưu object, expire object, invalidate object.
- Policy: TTL bao lâu, object nào được cache, stale data được chấp nhận trong ngữ cảnh nào, ai có quyền purge.

Tách policy khỏi mechanism giúp hệ thống linh hoạt hơn, nhưng có chi phí cấu hình. Nhiều knob hơn nghĩa là nhiều trạng thái sai hơn. Guardrail thực tế là cung cấp default tốt, giới hạn option nguy hiểm, ghi rõ blast radius và đo tác động bằng metric.

## Dependability

Dependability gồm nhiều thuộc tính khác nhau:

| Thuộc tính | Câu hỏi chính |
|---|---|
| Availability | Tại thời điểm này service có sẵn để dùng không |
| Reliability | Service có chạy liên tục trong một khoảng thời gian không |
| Safety | Khi lỗi tạm thời, hệ thống có tránh hậu quả nghiêm trọng không |
| Maintainability | Khi lỗi xảy ra, có phát hiện, sửa và phục hồi được nhanh không |

Availability cao không đồng nghĩa reliability cao. Một service mất 1 ms mỗi giờ có availability rất cao nhưng vẫn có thể gây gián đoạn transaction nếu workload yêu cầu chạy liên tục.

Trong distributed system, lỗi thường là **partial failure**: một node, link, dependency hoặc replica lỗi trong khi phần còn lại vẫn phản hồi. Vì vậy operator phải thiết kế theo chuỗi:

```text
fault -> error state -> user-visible failure
```

Mục tiêu là ngăn fault lan thành failure bằng redundancy, timeout, retry có giới hạn, circuit breaker, quorum, backpressure, graceful degradation và recovery workflow.

## Scalability Dimensions

Scalability cần được đo theo ít nhất ba chiều:

- **Size scalability:** thêm user, request hoặc resource mà không giảm performance quá mức.
- **Geographical scalability:** user/resource xa nhau nhưng latency và bandwidth vẫn trong ngưỡng chấp nhận.
- **Administrative scalability:** hệ thống vẫn quản trị được khi qua nhiều team, tenant, domain hoặc tổ chức.

Ba kỹ thuật scale phổ biến:

| Kỹ thuật | Khi dùng | Tradeoff |
|---|---|---|
| Hide latency | Chuyển synchronous wait thành async, background work, local validation hoặc prefetch | Semantics phức tạp hơn, cần trạng thái pending và retry |
| Partition / distribute work | Chia data, namespace hoặc workload thành phần nhỏ | Routing, rebalancing và hotspot |
| Replication / caching | Đặt bản sao gần user hoặc tăng read capacity | Consistency, invalidation, conflict và replication lag |

Scaling out không tự động tốt hơn scaling up. Nếu bottleneck thật là lock toàn cục, single leader, shared database schema, synchronous cross-region call hoặc team ownership mơ hồ, thêm node có thể chỉ tăng failure mode.

## System Classes

Một số lớp distributed system thường gặp:

- **High-performance distributed computing:** cluster hoặc grid cho workload compute lớn. Cluster thường đồng nhất hơn; grid/federation thường vướng administrative boundary, identity và policy.
- **Distributed information systems:** enterprise integration, transaction processing, RPC/RMI, message-oriented middleware và publish-subscribe.
- **Pervasive / mobile / edge / IoT systems:** nhiều thiết bị nhỏ, di động, wireless, pin hạn chế, cần context awareness và tự quản trị cao.

Với cloud-edge-IoT, tradeoff thường theo hướng:

```text
cloud: nhiều capacity, durability, centralized operations
edge: latency thấp hơn, locality tốt hơn, vận hành phân tán hơn
device/thing: sát hiện trường nhất, constraint mạnh nhất
```

## Common False Assumptions

Khi design distributed application, kiểm tra các giả định sai phổ biến:

- Network reliable.
- Network secure.
- Network homogeneous.
- Topology static.
- Latency zero.
- Bandwidth infinite.
- Transport cost zero.
- One administrator.

Production design nên biến các giả định này thành checklist review: timeout bao nhiêu, retry có bounded không, authn/authz ở đâu, schema/protocol versioning ra sao, topology thay đổi thì service discovery cập nhật thế nào, ai vận hành từng failure domain.

## Production Guardrails

- Đừng che partial failure bằng retry vô hạn; luôn có timeout, retry budget, jitter và circuit breaker.
- Đừng dùng synchronous cross-region path cho request latency-sensitive nếu không có lý do consistency mạnh.
- Đừng coi cache/replica là source of truth nếu không có invalidation và freshness contract.
- Đừng mở rộng qua administrative domain nếu identity, authorization, audit và data ownership chưa rõ.
- Đừng thêm middleware chỉ để "chuẩn hóa" nếu nó tạo thêm coupling, single point of failure hoặc hidden queue.
- Với distributed transaction, ưu tiên idempotency, saga/compensation hoặc outbox khi business cho phép; chỉ dùng atomic distributed commit khi correctness bắt buộc.
- Với edge/IoT, coi network partition, clock drift, intermittent connectivity và device compromise là bình thường.

## Liên Quan

- [Scalability, Availability And Consistency](../01-principles/01-scalability-availability-consistency-cap.md)
- [Availability Vs Consistency](../02-tradeoffs/01-availability-vs-consistency.md)
- [Latency Vs Throughput](../02-tradeoffs/02-latency-vs-throughput.md)
- [Scalability Vs Maintainability](../02-tradeoffs/03-scalability-vs-maintainability.md)
- [Replication Strategies](../04-reliability-and-dr/05-replication-strategies.md)
- [Caching, CDN And Read Replica](../04-reliability-and-dr/06-caching-cdn-read-replica.md)
