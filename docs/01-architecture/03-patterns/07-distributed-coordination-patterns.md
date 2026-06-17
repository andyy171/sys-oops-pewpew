# Distributed Coordination Patterns

## Overview

Distributed coordination là nhóm cơ chế giúp nhiều process/node thống nhất cách hành động khi không có shared memory, shared clock tuyệt đối hoặc một điểm quan sát toàn cục. Các bài toán lặp lại gồm ordering event, mutual exclusion, leader election, membership, gossip propagation, event matching và placement theo locality.

Mental model quan trọng: distributed coordination không chỉ là "gửi message". Nó là cách hệ thống quyết định ai được làm gì, theo thứ tự nào, với dữ liệu nào, khi một phần node hoặc network có thể lỗi.

## Time, Ordering And Causality

Không phải hệ thống nào cũng cần thời gian tuyệt đối chính xác. Nhiều hệ chỉ cần biết event nào phải được xử lý trước event nào.

| Cơ chế | Dùng khi | Tradeoff |
|---|---|---|
| Physical clock / NTP | Cần timestamp thực tế cho log, token, certificate, audit, lease hoặc measurement | Bị ảnh hưởng bởi drift, jitter, time source và step/slew policy |
| Lamport clock | Cần total order tương thích với quan hệ happens-before | Không chứng minh được causality chỉ bằng so sánh timestamp |
| Vector clock | Cần phát hiện concurrent update hoặc causal dependency | Metadata tăng theo số participant; khó dùng cho group rất lớn |
| TrueTime-like bounded interval | Cần commit/read ordering theo thời gian có bound | Cần time infrastructure mạnh và có thể phải wait theo uncertainty window |

Lamport clock gắn counter vào event và message. Khi nhận message, receiver đặt counter lớn hơn timestamp đã nhận. Nhờ vậy nếu event `a` happens-before event `b`, timestamp của `a` nhỏ hơn `b`. Nhưng chiều ngược lại không luôn đúng: timestamp nhỏ hơn không tự chứng minh có quan hệ nhân quả.

Vector clock lưu một vector counter theo từng participant. Nó cho phép phân biệt:

- event A causally precedes event B;
- event B causally precedes event A;
- hai event concurrent và có thể conflict.

Production guardrails:

- Đừng dùng wall-clock timestamp làm nguồn ordering duy nhất cho update quan trọng nếu node có thể lệch thời gian.
- Với replicated write, cần rule rõ: total order, causal order, last-write-wins, version vector, quorum hay conflict resolution ở application.
- Metadata causality phải có lifecycle. Vector/version metadata không được tăng vô hạn mà không có compaction hoặc boundary theo shard/session/object.

## Ordered Delivery

Replicated service thường cần mọi replica xử lý operation theo cùng thứ tự. Hai mức phổ biến:

| Semantics | Ý nghĩa | Dùng khi |
|---|---|---|
| Total order multicast | Mọi receiver deliver cùng thứ tự | State machine replication, replicated metadata, ledger |
| Causal order multicast | Chỉ giữ thứ tự cho event có quan hệ nhân quả | Collaboration, chat, cache/event propagation có causal dependency |

Total order dễ hiểu hơn nhưng thường đắt hơn. Causal order giảm constraint cho event độc lập, nhưng middleware không luôn biết business causality. Nếu người dùng trao đổi ngoài hệ thống rồi tạo event mới, causality đó không tự xuất hiện trong message layer.

## Mutual Exclusion And Distributed Locks

Mutual exclusion đảm bảo chỉ một process được truy cập critical section hoặc shared resource tại một thời điểm. Các hướng thiết kế chính:

| Cách | Mental model | Điểm mạnh | Rủi ro |
|---|---|---|---|
| Central coordinator | Một coordinator cấp grant/release | Đơn giản, dễ debug, ít message | Coordinator là bottleneck/SPOF nếu không HA |
| Permission-based distributed | Mỗi node xin OK từ các node khác | Không phụ thuộc một coordinator đơn | Nhiều message, nhạy với crash/membership |
| Token ring | Ai giữ token thì được vào critical section | Fair, tránh starvation nếu token còn sống | Mất token hoặc node chết làm recovery phức tạp |
| Majority/voting | Cần majority coordinator/replica cho lock | Chịu lỗi tốt hơn single coordinator | Contention cao có thể làm utilization giảm |

Trong production, distributed lock nên được xem là lease có timeout, fencing token và ownership rõ, không phải mutex local kéo dài vô hạn.

Guardrails:

- Lock holder crash phải tự giải phóng được bằng session/lease/ephemeral node.
- Mỗi lock acquisition nên trả fencing token tăng đơn điệu; backend ghi dữ liệu phải reject token cũ.
- Có timeout, retry backoff và giới hạn số lần thử; tránh thundering herd khi lock được release.
- Không giữ lock trong khi gọi external dependency không kiểm soát timeout.
- Monitor lock wait time, lock hold time, failed acquisition, session expiry và split-brain signal.

## ZooKeeper-Style Coordination

ZooKeeper cung cấp namespace dạng cây để xây coordination primitive như lock, leader election, config và watch. Một lock đơn giản có thể dùng node đại diện cho lock; client tạo node thành công thì giữ lock, delete node để release. Ephemeral node giúp lock biến mất khi session của client hết hạn.

Điểm cần nhớ:

- Watch/notification phải tránh race giữa lúc client đọc state và lúc đăng ký watch.
- Version number giúp compare-and-set, tránh update dựa trên state đã cũ.
- Client phải xử lý session expiry như mất quyền sở hữu lock/leadership.
- Ensemble cần quorum; khi mất quorum, ưu tiên fail closed hơn là cấp lock/leader không chắc chắn.

ZooKeeper là coordination service, không phải nơi lưu bulk data. Dữ liệu trong node nên nhỏ, phục vụ metadata/coordination.

## Key-Value Store Cho Runtime Configuration

Các hệ như etcd, Consul hoặc ZooKeeper thường được dùng làm nguồn cấu hình runtime, service discovery, leader election và lock. Trong delivery pipeline, pattern phổ biến là image giữ nguyên còn môi trường cung cấp config qua key-value store, orchestrator hoặc secret/config backend.

Mental model:

```text
application / proxy / sidecar
-> read config/service endpoint from KV store
-> render/reload local config or update runtime behavior
```

Guardrails:

- KV/coordination store không phải object store; giá trị nên nhỏ, rõ schema và có owner.
- Cluster cần quorum. Khi mất majority/quorum, hệ thống nên fail closed cho write/update thay vì chấp nhận split-brain config.
- Config thay đổi phải có audit: key nào, value nào, actor/pipeline nào, rollback value là gì.
- Client cần xử lý watch/reconnect, stale value, timeout và backoff; không assume watch event luôn đến đúng một lần.
- Secret không nên lưu plaintext trong KV store nếu store không có encryption, RBAC và audit phù hợp.
- Với rollout, thêm endpoint/backend mới vào service discovery chỉ sau khi backend đã pass health check.

## Service Discovery Catalog Và Health

Service discovery gồm hai phần khác nhau:

- **catalog:** service nào đang tồn tại, endpoint nào thuộc service đó, metadata/tag là gì;
- **health:** endpoint đó có nên nhận traffic ngay lúc này không.

Consul, ZooKeeper, etcd kèm DNS layer, hoặc service registry khác đều có thể làm một phần của mô hình này. Client có thể query qua HTTP API, DNS A/AAAA hoặc SRV record. SRV record hữu ích khi client cần cả hostname và port, nhưng application phải thật sự hỗ trợ SRV thay vì chỉ lookup A record.

Production guardrails:

- endpoint chỉ được publish sau khi readiness/health check pass;
- health check phải chạy trong đúng network namespace và environment mà service sẽ được gọi, tránh check "localhost" sai ngữ cảnh;
- check script cần dependency rõ trong image/host, không cài tay trong container đang chạy rồi coi là production state;
- service ID phải unique cho từng instance, đặc biệt khi nhiều replica cùng tên service;
- DNS/service discovery cần TTL phù hợp với tốc độ rollout và khả năng cache của client;
- nếu registry nằm trong container, volume dữ liệu, backup và quorum của server node phải được thiết kế trước.

## Automatic Service Registration

Một số agent có thể nghe Docker/container runtime events để tự register/deregister service khi container start/stop. Pattern này giảm thao tác thủ công trong môi trường churn cao, nhưng nó chuyển trust boundary sang agent quan sát runtime.

Mental model:

```text
container start/stop event
-> registration agent reads metadata/labels/env/ports
-> update service catalog
-> DNS/API returns only healthy endpoints
```

Guardrails:

- agent cần quyền đọc runtime event; nếu mount Docker socket thì coi như quyền root-equivalent trên host;
- metadata như `SERVICE_NAME`, tag, port và health check phải được chuẩn hóa, không để container name ngẫu nhiên thành public service identity;
- có resync định kỳ để sửa missed event, nhưng resync không thay thế audit log;
- deregister phải xảy ra khi container stop hoặc health critical, nếu không client có thể gọi endpoint chết;
- không để mọi container có published port tự động trở thành service public nếu chưa có allowlist/label rõ.

## Leader Election

Leader election chọn một node làm coordinator/primary/owner cho một vai trò. Thuật toán cụ thể khác nhau, nhưng mục tiêu production giống nhau: tại một thời điểm an toàn chỉ có một leader hợp lệ và follower biết cách chuyển sang leader mới khi leader cũ lỗi.

| Pattern | Ý tưởng | Khi phù hợp |
|---|---|---|
| Bully | Node có ID/priority cao nhất còn sống thắng | Group nhỏ, membership biết trước |
| Ring election | Election message đi quanh logical ring | Topology ring hoặc overlay ổn định |
| ZooKeeper election | Candidate dựa vào transaction mới nhất và quorum follower | Coordination ensemble nhỏ, cần metadata mới nhất |
| Raft election | Follower timeout thành candidate, cần majority vote theo term | Replicated log/state machine |
| Proof-of-work/stake | Chọn leader trong môi trường permissionless | Blockchain/ledger thiếu trust chung |

Raft-style election có các guardrail quan trọng:

- heartbeat đều để follower không election liên tục;
- randomized election timeout để tránh nhiều candidate kéo dài;
- majority vote để tránh hai leader trong cùng term;
- term tăng đơn điệu để loại bỏ message cũ.

Production checks:

```text
leader identity
current term/epoch
quorum member health
replication lag
last committed/applied index
election count and election duration
```

Nếu service liên tục đổi leader, đừng chỉ tăng timeout. Cần kiểm tra network jitter, GC pause, disk latency, CPU starvation, clock/timeouts, packet loss và quorum placement.

## Gossip Coordination

Gossip/epidemic protocol cho node trao đổi thông tin với một số peer ngẫu nhiên thay vì broadcast toàn mạng. Nó phù hợp cho membership, anti-entropy, metadata propagation, peer sampling và overlay maintenance.

Các pattern hay gặp:

- **Aggregation:** node trao đổi giá trị để hội tụ về average, max/min hoặc estimate toàn hệ.
- **Peer sampling service:** mỗi node giữ partial view nhỏ, refresh bằng trao đổi định kỳ để có cảm giác chọn peer ngẫu nhiên từ toàn mạng.
- **Overlay construction:** một layer random duy trì peer sampling; layer trên chọn neighbor theo ranking như latency, topology hoặc proximity.

Guardrails:

- Gossip là eventual; không dùng cho quyết định cần all-or-nothing hoặc strict ordering.
- Partial view cần loại bỏ entry cũ, deduplicate và xử lý node leave/crash.
- Fan-out, interval và TTL phải có budget để tránh traffic storm.
- Nếu dùng topology-aware gossip, vẫn cần một lượng randomness để tránh kẹt local optimum hoặc partition overlay.
- Gossip security không chỉ là authentication. Node authenticated vẫn có thể gửi dữ liệu sai hoặc pollute partial view.

## Secure Gossip

Gossip lan truyền thông tin tốt và cũng lan truyền thông tin độc hại rất nhanh. Một nhóm node xấu có thể cố làm partial view của node tốt chỉ trỏ về attacker, hoặc gửi value sai trong aggregation.

Biện pháp giảm rủi ro:

- rate limit tần suất gossip từ mỗi peer;
- phát hiện indegree bất thường hoặc neighbor xuất hiện quá thường xuyên;
- lấy mẫu từ nhiều peer độc lập trước khi chấp nhận update quan trọng;
- ưu tiên pull hoặc push-pull có kiểm soát khi sợ data injection;
- ký/verify payload khi cần integrity, nhưng vẫn phải có trust/reputation hoặc anomaly detection.

## Publish-Subscribe Event Matching

Event matching quyết định notification nào khớp subscription nào. Topic-based matching dễ scale hơn vì thường map được topic sang broker/rendezvous node. Content-based matching mạnh hơn nhưng khó phân tán, khó tối ưu và khó bảo mật vì broker cần đủ thông tin để match.

| Thiết kế | Ý tưởng | Tradeoff |
|---|---|---|
| Central broker | Một broker lưu subscription và match notification | Đơn giản, bottleneck rõ |
| Rendezvous/hash by topic | Map subscription và notification về broker chung | Scale tốt cho topic, kém hơn cho expression phức tạp |
| Flood subscription hoặc notification | Mỗi broker có đủ thông tin hoặc notification đến mọi broker | Đơn giản nhưng tốn bandwidth/state |
| Selective routing | Router/broker giữ filter để chỉ forward path có subscriber | Giảm traffic, cần update filter đúng lúc |
| Gossip-based grouping | Subscriber có interest giao nhau tạo overlay riêng | Scalable hơn cho range/content, phức tạp hơn |

Security tension:

- Publisher/subscriber muốn referential decoupling và đôi khi mutual anonymity.
- Broker cần match nhưng không nên thấy toàn bộ nội dung nhạy cảm.
- Nếu broker không trusted, cần searchable encryption, secure keyword search hoặc giới hạn expressiveness của subscription.

Production guardrails:

- Ghi rõ subscription model: topic, attribute filter, range, regex hay SQL-like expression.
- Theo dõi subscription count, match latency, broker CPU, fan-out, dropped notification và stale filter.
- Với content-based routing, có cơ chế cancel/expire subscription để filter không phình vô hạn.
- Không đưa dữ liệu nhạy cảm vào topic/key nếu broker/log/metric có thể lộ.

## Logical Positioning And Locality

Large-scale distributed system thường cần chọn peer/replica theo proximity. GPS là physical positioning; còn network coordinate system là logical positioning, đặt node vào không gian hình học sao cho khoảng cách phản ánh latency hoặc cost.

Use case:

- chọn CDN replica gần client;
- chọn peer ít latency hơn trong overlay;
- placement replica theo locality;
- routing bằng local neighbor information.

Guardrails:

- Latency measurement có jitter và có thể vi phạm triangle inequality; coordinate chỉ là estimate.
- Landmark tập trung dễ triển khai nhưng tạo dependency vào landmark quality.
- Vivaldi-like decentralized positioning hội tụ dần, cần damping/adaptive step để tránh oscillation.
- Không dùng proximity đơn độc. Placement còn phải xét capacity, failure domain, data residency, cost và security boundary.

## Operations Checklist

- Hệ thống cần ordering theo wall-clock, total order, causal order hay application conflict rule?
- Coordination service có quorum/fencing/session expiry rõ không?
- Leader election có metric về term/epoch, election count và replication lag không?
- Distributed lock có timeout, fencing token và cleanup khi client chết không?
- Gossip có budget cho fan-out/interval/TTL và chống poisoning không?
- Pub-sub matching đang bottleneck ở broker, routing filter hay subscriber fan-out?
- Node placement có xét latency cùng failure domain và capacity không?

## Related Pages

- [Distributed System Architecture Styles](./06-distributed-system-architecture-styles.md)
- [Distributed Fault Tolerance And Recovery](../04-reliability-and-dr/10-distributed-fault-tolerance-and-recovery.md)
- [Distributed Systems Foundations](../00-foundations/02-distributed-systems-foundations.md)
- [NTP And Time Synchronization](../../02-core-infrastructure/02-network/04-protocols-and-services/05-ntp-time-synchronization.md)
- [AMQP RabbitMQ Core Concepts](../../03-compute-and-orchestration/06-messaging-and-streaming/02-rabbitmq/01-amqp-rabbitmq-core-concepts.md)
