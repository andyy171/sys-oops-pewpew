# Distributed Fault Tolerance And Recovery

## Overview

Fault tolerance là khả năng hệ thống tiếp tục phục vụ đúng mức chấp nhận được khi một phần node, network, process hoặc dependency lỗi. Điểm khác biệt của distributed system là **partial failure**: một phần hệ thống chết, chậm hoặc sai, trong khi phần còn lại vẫn chạy và có thể nhìn như bình thường.

Production mental model:

- lỗi không chỉ là node down; lỗi có thể là timeout, mất message, reply sai, stale membership, split-brain hoặc side effect chạy hai lần;
- fault tolerance cần redundancy, nhưng redundancy chỉ an toàn khi có quorum, fencing, membership, ordering và recovery rõ;
- recovery không chỉ là restart service; phải đưa state về một điểm đúng hoặc reconcile có kiểm soát.

## Dependability Terms

| Thuật ngữ | Ý nghĩa | Câu hỏi vận hành |
|---|---|---|
| Availability | Service sẵn sàng tại một thời điểm | User có gọi được API ngay lúc này không? |
| Reliability | Service chạy liên tục trong một khoảng thời gian | Có bị gián đoạn lặp lại dù uptime tổng cao không? |
| Safety | Khi lỗi xảy ra, hệ thống không tạo hậu quả nghiêm trọng | Có fail closed thay vì ghi sai/chuyển tiền sai/cấp quyền sai không? |
| Maintainability | Khả năng phát hiện, sửa và khôi phục nhanh | Có runbook, automation, rollback và evidence không? |

Phân biệt `fault`, `error`, `failure`:

- **Fault:** nguyên nhân gốc, ví dụ bug, disk lỗi, packet loss, operator mistake.
- **Error:** trạng thái sai bên trong hệ thống, ví dụ memory corrupt, replica lệch version.
- **Failure:** service không còn giữ contract với client.

## Failure Models

| Failure model | Mô tả | Guardrail |
|---|---|---|
| Crash failure | Process/node dừng và không phát sinh hành vi mới | Cần restart, failover, quorum và recovery state |
| Omission failure | Không nhận hoặc không gửi message cần thiết | Timeout không đủ để kết luận node chết; cần retry budget và idempotency |
| Timing failure | Response quá sớm/quá muộn so với SLO/contract | Deadline, backpressure và load shedding phải rõ |
| Response failure | Trả kết quả sai hoặc đi sai state transition | Cần validation, invariant check và canary/rollback |
| Arbitrary/Byzantine failure | Có thể trả message bất kỳ, không nhất quán giữa các peer | Cần authentication, quorum lớn hơn, audit và BFT nếu môi trường không trusted |

Fault có thể transient, intermittent hoặc permanent. Transient/intermittent thường hợp với retry có backoff, nhưng permanent fault cần repair hoặc replace. Retry mù trước permanent fault chỉ làm tăng tải và kéo dài incident.

## Network Fault Injection And Partition Testing

Network failure không chỉ là "mất kết nối". Một dependency có thể chậm thêm 100 ms, mất 1% packet, chỉ drop một chiều, hoặc bị partition thành nhiều nhóm node vẫn sống nhưng không thấy nhau. Những trạng thái này dễ làm lộ bug về timeout, retry storm, split-brain, stale cache và duplicate side effect.

Fault injection có giá trị khi nó được thiết kế như một experiment có blast radius rõ ràng, không phải thao tác ngẫu hứng trên host production.

Pre-check trước khi inject lỗi:

- xác định service, container, namespace hoặc interface nằm trong phạm vi test;
- ghi baseline latency, packet loss, throughput và error rate;
- xác nhận test đang ở lab/staging hoặc có phê duyệt chaos experiment cho production;
- kiểm tra alert, dashboard, log và synthetic check đã sẵn sàng;
- chuẩn bị rollback/stop condition trước khi áp rule.

Các signal đọc an toàn:

```bash
ping -c 20 <dependency-host>
curl -w '%{time_connect} %{time_starttransfer} %{time_total}\n' -o /dev/null -s <url>
tc -s qdisc show dev <interface>
docker network inspect <network>
```

Guardrails:

- công cụ dùng `tc`, `iptables`, `NET_ADMIN`, `--privileged` hoặc mount Docker socket có blast radius cao, vì có thể thay đổi packet path hoặc điều khiển host/container khác;
- ưu tiên dry-run hoặc command hiển thị rule trước khi apply nếu tool hỗ trợ;
- không chạy network fault injection trên host dùng chung nếu chưa giới hạn đúng interface/container;
- luôn có bước stop/rollback bằng cùng tool đã apply rule và xác minh `tc -s qdisc` hoặc metric network đã trở về baseline;
- test partition phải kiểm tra invariant của hệ thống, ví dụ quorum fail closed, write không split-brain, retry không làm quá tải dependency và job side effect không chạy hai lần.

## Redundancy Patterns

Ba dạng redundancy chính:

- **Information redundancy:** thêm checksum, parity, ECC, signature hoặc erasure coding để phát hiện/sửa dữ liệu lỗi.
- **Time redundancy:** retry, retransmit, redo transaction; phù hợp khi operation idempotent hoặc có deduplication.
- **Physical/process redundancy:** nhiều node/process/zone/region cùng cung cấp service.

Replication cần đủ số lượng replica theo failure model:

| Failure assumption | Số replica tối thiểu để chịu `k` lỗi | Lý do |
|---|---:|---|
| Crash/fail-silent | `k + 1` | Nếu `k` replica dừng, còn ít nhất một replica đúng |
| Majority/quorum crash tolerance | `2k + 1` | Cần majority còn sống để tránh split-brain |
| Byzantine/arbitrary | `3k + 1` | Cần quorum giao nhau có ít nhất một nonfaulty replica |

Các con số này không thay thế capacity planning. Replica còn sống phải đủ CPU, memory, disk I/O, network và dependency để gánh tải sau failover.

## Process Groups And Membership

Process group làm nhiều process trông như một logical service. Có hai kiểu phổ biến:

- **Flat group:** peer ngang nhau, quyết định qua vote/quorum; ít single point of failure hơn nhưng coordination đắt hơn.
- **Hierarchical group:** có coordinator/primary; dễ điều phối nhưng cần leader election, fencing và failover rõ.

Membership là phần dễ bị đánh giá thấp. Join/leave/crash phải được đưa vào cùng dòng event với data message. Nếu một node được coi là member ở replica A nhưng không ở replica B, các guarantee về quorum, delivery và ownership có thể sai.

Guardrails:

- Mọi membership change cần version/view/epoch tăng đơn điệu.
- Không promote leader/primary nếu không có quorum hoặc fencing primary cũ.
- Health check phải phân biệt process alive với service có khả năng phục vụ đúng.
- Khi nhiều node đồng thời cố rebuild group, cần leader election hoặc coordination service để tránh group split.

## Consensus And Replicated Logs

Consensus là bài toán để các nonfaulty process chọn cùng một giá trị hoặc cùng một command order dù có lỗi. Trong production, consensus thường xuất hiện dưới dạng replicated log: mọi replica apply cùng command theo cùng thứ tự.

### Raft Mental Model

Raft dùng leader, term và replicated log:

- client gửi write tới leader;
- leader append operation vào log;
- operation được coi là committed khi majority replica đã ghi nhận;
- leader mới chỉ hợp lệ nếu log đủ mới để không làm mất committed operation.

Operational checks:

```text
leader
term/epoch
quorum health
commit index
applied index
replication lag
election count
snapshot/install-snapshot progress
```

Nếu leader crash sau khi đã commit nhưng chưa thông báo đủ follower, leader mới phải hoàn tất hoặc replay committed entry đó. Vì vậy client phải chịu được retry và duplicate response.

### Paxos And PBFT View

Paxos dùng proposer, acceptor và learner để đảm bảo một proposal đã được chọn thì proposal timestamp cao hơn không chọn operation khác. Paxos mạnh nhưng khó vận hành và thường xuất hiện gián tiếp trong hệ thống như Ceph MON hoặc các consensus layer.

PBFT xử lý arbitrary/Byzantine failure bằng pre-prepare, prepare, commit và view-change trên `3k + 1` replica. Nó cần xác thực message, quorum lớn và static/controlled membership, nên chi phí vận hành cao hơn crash-fault consensus.

Guardrails cho consensus system:

- Không chạy even-number quorum nếu không hiểu failure mode; 3 hoặc 5 node thường dễ vận hành hơn 2 hoặc 4.
- Disk/fsync latency trên consensus node là availability risk, không chỉ performance issue.
- Network partition phải fail closed cho write nếu không còn quorum.
- Client request cần idempotency key hoặc request ID để xử lý retry sau timeout.

## Failure Detection

Failure detector thực tế dựa vào timeout, probe, heartbeat hoặc gossip. Trong partially synchronous system, timeout chỉ tạo **suspect**, không tạo sự thật tuyệt đối. Node chậm, GC pause, packet loss hoặc network partition có thể bị nhìn giống crash.

Production guardrails:

- Dùng adaptive timeout hoặc phi-accrual style detector khi latency thay đổi mạnh.
- Không để một node đơn lẻ quyết định loại bỏ peer quan trọng; lấy xác nhận từ nhiều vantage point.
- Tách node failure khỏi link/path failure nếu có thể.
- Alert riêng cho false positive, election churn, heartbeat delay và membership flap.
- Khi detector nghi ngờ lỗi, hành động phải tương ứng risk: mark unhealthy, drain traffic, remove from quorum hay fence node là các mức khác nhau.

## RPC Failure Semantics

RPC không thể giữ illusion "giống local call" khi server hoặc network lỗi. Các semantics thường gặp:

| Semantics | Contract | Dùng khi |
|---|---|---|
| At-least-once | Retry cho đến khi có response; operation có thể chạy nhiều lần | Read/idempotent write |
| At-most-once | Deduplicate để operation không chạy quá một lần; có thể không chạy | Side effect không được nhân đôi |
| Effectively-once | At-least-once delivery cộng idempotency/dedup/reconciliation | Payment/order/job orchestration |
| Exactly-once tuyệt đối | Thường không đạt được qua network không tin cậy | Tránh dùng làm contract nếu không định nghĩa rõ boundary |

Lost request thường xử lý bằng retry. Lost reply nguy hiểm hơn: server có thể đã commit side effect nhưng client không nhận được response. Vì vậy non-idempotent operation cần request ID, idempotency key, dedup store và response replay.

Client crash có thể để lại orphan computation. Thay vì cố kill mọi orphan, production system thường nên thiết kế job/operation có owner, lease, TTL, cancellation token và reconciliation để orphan tự hết hạn hoặc được claim lại an toàn.

## Reliable Group Communication

Reliable multicast đảm bảo message được deliver tới các nonfaulty member trong group. Với group nhỏ, gửi point-to-point tới từng member và đợi ACK có thể đủ. Với group lớn, ACK từ mọi receiver gây feedback implosion.

Scalable options:

- negative ACK thay vì ACK mọi message;
- feedback suppression bằng random delay;
- hierarchy/coordinator theo subgroup;
- gossip/anti-entropy để repair eventual state.

Atomic multicast mạnh hơn reliable multicast: message được deliver tới tất cả nonfaulty member hoặc không member nào, và thường cần total order. Virtual synchrony mô hình hóa group thành các view/epoch; message không được vượt qua view-change boundary. Pattern này hữu ích cho replicated database, metadata service và group membership nhất quán.

## Distributed Commit

Distributed commit đảm bảo nhiều participant cùng commit hoặc cùng abort. Đây là atomicity ở mức workflow/transaction, không phải chỉ là message delivery.

Two-phase commit:

1. Coordinator gửi vote-request.
2. Participant vote commit/abort và ghi state bền vững.
3. Coordinator quyết định global commit nếu tất cả đồng ý, ngược lại abort.
4. Participant apply decision.

Rủi ro chính: 2PC là blocking protocol. Nếu participant đã ở READY và coordinator crash trước khi gửi quyết định, participant có thể phải chờ coordinator recover hoặc hỏi participant khác. Vì vậy 2PC cần persistent log, timeout, termination protocol và runbook recovery.

Three-phase commit thêm PRECOMMIT để tránh một số trạng thái blocking trong fail-stop model, nhưng ít phổ biến trong production vì điều kiện giả định và độ phức tạp.

Production guardrails:

- Không dùng distributed transaction rộng nếu saga/outbox/idempotent workflow đủ đáp ứng business.
- Nếu dùng 2PC, log quyết định trước khi gửi message và test recovery từ từng state.
- Coordinator là critical dependency; cần HA hoặc cách recover decision rõ.
- Timeout không được tự ý commit khi chưa có quyết định hợp lệ.

## Recovery, Checkpointing And Message Logging

Recovery có hai hướng:

- **Backward recovery:** rollback về checkpoint/snapshot đúng rồi replay.
- **Forward recovery:** sửa state hiện tại thành state đúng mới, chỉ khả thi khi biết trước lỗi và cách sửa.

Distributed checkpointing cần recovery line nhất quán: nếu checkpoint ghi nhận đã receive message, phải có checkpoint khác ghi nhận send message đó. Independent checkpoint có thể gây domino effect, rollback dây chuyền về rất xa. Coordinated checkpoint đơn giản hơn nhưng có thể block hoặc tăng latency.

Message logging giảm số lần checkpoint bằng cách replay nondeterministic event/message sau checkpoint. Pessimistic logging ghi ổn định trước khi process tạo dependency mới, tránh orphan process nhưng tăng latency. Optimistic logging nhanh hơn lúc bình thường nhưng recovery phức tạp hơn vì phải rollback các orphan dependency.

Runbook recovery nên có:

- snapshot/log/version trước khi repair;
- source of truth rõ;
- thứ tự restore: metadata/quorum trước, data plane sau;
- validation bằng invariant, sample read/write và lag/offset/index;
- rollback/fallback nếu replay hoặc reconcile tạo lỗi mới.

## Operations Checklist

- Failure model giả định là crash, omission, timing, response hay Byzantine?
- Operation nào idempotent, operation nào cần deduplication?
- Quorum/membership/fencing có bảo vệ split-brain không?
- Failure detector có false positive budget và multi-vantage check không?
- Consensus node có đủ disk I/O, network và failure-domain spread không?
- Distributed commit có persistent decision log và recovery test không?
- Checkpoint/backup có tạo recovery line nhất quán không?
- Sau recovery, invariant nào chứng minh state đúng?

## Related Pages

- [HA And Failover Patterns](./01-ha-and-failover-patterns.md)
- [Replication Strategies](./05-replication-strategies.md)
- [RTO/RPO Design](./07-rto-rpo-design.md)
- [Availability Vs Consistency](../02-tradeoffs/01-availability-vs-consistency.md)
- [Distributed Coordination Patterns](../03-patterns/07-distributed-coordination-patterns.md)
- [Replication And Consistency Models](../03-patterns/09-replication-consistency-models.md)
- [Distributed System Architecture Styles](../03-patterns/06-distributed-system-architecture-styles.md)
