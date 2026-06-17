# Replication And Consistency Models

## Overview

Replication giữ nhiều bản sao của cùng một dữ liệu hoặc service để tăng availability, giảm latency, scale read workload và giảm blast radius khi một node/site lỗi. Đổi lại, hệ thống phải trả lời câu hỏi khó hơn: khi nhiều replica nhận read/write ở thời điểm khác nhau, client được thấy trạng thái nào là hợp lệ?

Consistency model là contract giữa hệ thống và người dùng. Nó không chỉ là thuộc tính của database; cùng một vấn đề xuất hiện trong cache, CDN, replicated metadata, filesystem, message log, object store và control plane.

Mental model thực tế:

- replication giúp hệ thống sống sót và phục vụ gần người dùng hơn;
- consistency quyết định dữ liệu stale, out-of-order hoặc conflict được phép đến mức nào;
- càng muốn guarantee mạnh, hệ thống càng phải trả thêm latency, coordination, quorum hoặc throughput cost.

## Why Replicate

Các lý do chính:

| Mục tiêu | Ý nghĩa | Rủi ro đi kèm |
|---|---|---|
| Reliability | Mất một replica không làm mất service hoặc dữ liệu | Failover sai có thể tạo split-brain |
| Performance | Đặt dữ liệu gần client hoặc gần workload đọc | Replica gần hơn có thể stale hơn |
| Read scaling | Tách read khỏi primary hoặc origin | Read-after-write issue nếu đọc nhầm replica |
| Geo distribution | Giảm latency theo vùng | Conflict và compliance phức tạp hơn |
| Maintenance | Có thể drain/upgrade từng node | Cần kiểm soát lag và quorum trước khi thao tác |

Replication không tự làm hệ thống an toàn hơn nếu promotion, conflict resolution, backup và recovery không rõ. Một bản sao dữ liệu lỗi có thể lan rất nhanh sang nhiều replica.

## Data-Centric Consistency

Data-centric consistency mô tả trạng thái mà storage/service được phép trả về, độc lập với session cụ thể của client.

| Model | Contract | Khi phù hợp | Production note |
|---|---|---|---|
| Linearizability | Mỗi operation trông như xảy ra tức thời tại một điểm giữa request và response | Lock, metadata quan trọng, payment state, leadership | Đắt vì cần coordination mạnh; latency tail nhạy với network |
| Sequential consistency | Mọi process thấy một thứ tự operation hợp lệ giống nhau, nhưng không nhất thiết theo real time | Replicated state khi real-time order không bắt buộc | Dễ gây bất ngờ nếu user kỳ vọng read ngay sau write |
| Causal consistency | Nếu operation B phụ thuộc A, mọi replica phải thấy A trước B | Collaboration, feed, event propagation | Cần metadata causality/version; khó khi dependency đi ngoài hệ thống |
| Eventual consistency | Nếu không còn write mới, các replica cuối cùng hội tụ | DNS/cache/object metadata/read-heavy workload | Cần định nghĩa "cuối cùng" qua SLO, TTL, repair và anti-entropy |
| Strong eventual consistency | Replica nhận cùng tập update sẽ hội tụ không phụ thuộc thứ tự nhận | CRDT-like state, counters/sets đặc biệt | Chỉ dùng được khi data type và merge rule thật sự commutative/idempotent |
| Continuous consistency | Cho phép deviation có bound về staleness, số lượng update hoặc thứ tự | Monitoring, approximate view, edge cache | Phải biến bound thành metric/SLO thay vì câu "gần đúng" mơ hồ |

Linearizability thường bị nhầm với sequential consistency. Điểm khác biệt quan trọng là linearizability tôn trọng real-time order: nếu write đã thành công trước khi read bắt đầu, read phải thấy write đó hoặc write mới hơn. Sequential consistency chỉ yêu cầu tất cả process đồng ý về một thứ tự hợp lệ.

## Client-Centric Consistency

Client-centric consistency tập trung vào trải nghiệm của một client/session khi client có thể đọc từ nhiều replica khác nhau.

| Model | Contract | Ví dụ lỗi nếu thiếu |
|---|---|---|
| Monotonic reads | Một client đã thấy version mới thì lần đọc sau không bị quay lại version cũ | Refresh dashboard thấy dữ liệu "lùi thời gian" |
| Monotonic writes | Write của cùng một client được apply theo đúng thứ tự | Update cấu hình B bị apply trước cấu hình A mà nó phụ thuộc |
| Read your writes | Client đọc lại sẽ thấy write của chính nó | User đổi password/profile nhưng request sau vẫn thấy giá trị cũ |
| Writes follow reads | Write sau khi đọc một version phải được apply sau version đó | Reply/comment tham chiếu nội dung chưa tồn tại ở replica nhận write |

Các guarantee này thường rẻ hơn linearizability toàn hệ thống, nhưng cần session stickiness, version token, causal metadata hoặc routing theo replica đã đủ mới.

Production guardrails:

- API write nên trả version/etag/commit timestamp/LSN nếu client cần đọc lại chính xác.
- Read path cần biết khi nào phải route về primary hoặc replica đã catch up.
- Với multi-region, ghi rõ operation nào được phép stale và operation nào phải đọc strong.
- Session affinity là optimization, không nên là guarantee duy nhất nếu client có thể đổi device, region hoặc load balancer path.

## Replication Protocol Patterns

### Primary-Based Replication

Một primary nhận write, sắp thứ tự operation rồi truyền sang replica. Đây là model dễ hiểu và phổ biến.

Biến thể:

- **Remote write / primary-backup:** client gửi write tới primary cố định; replica nhận state hoặc log từ primary.
- **Local write / moving primary:** primary cho object có thể di chuyển tới nơi client/workload ghi nhiều hơn.
- **Synchronous replication:** write chỉ thành công sau khi replica cần thiết đã xác nhận.
- **Asynchronous replication:** primary trả thành công trước, replica catch up sau.

Guardrails:

- Failover phải có fencing/epoch/term để primary cũ không tiếp tục nhận write sau partition.
- Trước khi promote replica, kiểm tra replication lag, last committed/applied index và durability của log.
- Không coi asynchronous replica là bản sao không mất dữ liệu; RPO phải được ghi rõ.
- Nếu moving primary, cần ownership transfer rõ ràng và reject write từ owner cũ.

### Active Replication

Tất cả replica xử lý cùng operation theo cùng thứ tự, thường dựa trên total order broadcast hoặc replicated log. Pattern này phù hợp với state machine replication, metadata control plane và service cần failover nhanh.

Điều kiện quan trọng:

- operation phải deterministic hoặc mọi non-determinism phải được quyết định trước khi replicate;
- mọi replica phải apply cùng một log/order;
- side effect bên ngoài như email, payment, webhook phải idempotent hoặc chỉ phát ra sau commit an toàn.

### Quorum-Based Replication

Quorum dùng nhiều replica cho read/write. Với `N` replica, chọn read quorum `NR` và write quorum `NW` sao cho:

```text
NR + NW > N
NW > N / 2
```

Điều kiện đầu giúp read quorum giao với write quorum, điều kiện sau giúp hai write quorum giao nhau. Đây là nền tảng để tránh hai write độc lập cùng được coi là thắng mà không có điểm gặp.

Quorum không tự động giải quyết mọi thứ. Hệ thống vẫn cần versioning, conflict detection, hinted handoff/read repair/anti-entropy và rule xử lý replica chậm.

## Cache Coherence And Replica Freshness

Cache là một dạng replica có contract yếu hơn. Khi cache lưu object mutable, cần quyết định cache nhận thay đổi bằng cách nào:

| Cách | Mental model | Dùng khi | Rủi ro |
|---|---|---|---|
| Invalidation | Backend báo cache xóa object cũ | Dữ liệu thay đổi ít, cache có thể refetch | Miss storm nếu invalidation diện rộng |
| Update state | Backend đẩy giá trị mới sang cache | Object nhỏ, update ít, cần freshness tốt | Write amplification và stale update out-of-order |
| Operation propagation | Đẩy operation để cache tự apply | State có operation rõ, tiết kiệm bandwidth | Operation phải idempotent/order-safe |
| Pull/TTL | Cache tự hết hạn hoặc hỏi lại | Đơn giản, chịu stale được | Freshness phụ thuộc TTL và clock |
| Lease | Cache được giữ object trong thời gian/điều kiện cụ thể | Muốn giảm invalidation liên tục | Lease expiry và clock/timeout phải được kiểm soát |

Với workload đọc nhiều và ghi ít, push/invalidation có thể hiệu quả. Với object thay đổi thường xuyên hoặc có nhiều cache không ổn định, pull/TTL hoặc lease thường dễ vận hành hơn.

## Web, CDN And Edge Replication

Web cache và CDN dùng replication để giảm latency và tải origin. Đối tượng phù hợp nhất là content immutable, static asset, image/video hoặc response có `Cache-Control` rõ.

Dynamic content có thể cache được nếu tách đúng boundary:

- cache public fragment tách khỏi dữ liệu user-specific;
- key cache gồm đầy đủ dimension ảnh hưởng response như locale, auth state, device class hoặc feature flag;
- response sensitive mặc định `private` hoặc `no-store`;
- purge/invalidation có audit và rollback path.

CDN placement không chỉ là "gần nhất". Edge selection nên cân nhắc health, latency, capacity, origin cost, data residency và failure domain. Nếu edge sai hoặc stale, cần có bypass/purge route và metric để phát hiện.

## Production Checklist

Trước khi chọn hoặc thay đổi replication/consistency design:

- Object nào cần strong consistency, object nào được eventual?
- User workflow nào bắt buộc read-your-writes?
- Replica lag được đo bằng gì: time, log offset, version, queue depth hay applied index?
- Failover/promotion có fencing không?
- Backup/restore có độc lập với replication không, hay lỗi logic sẽ bị replicate sang mọi bản sao?
- Có metric cho stale read, conflict rate, read repair, anti-entropy backlog và quorum failure không?
- Có runbook rollback nếu cache/CDN/replica trả sai dữ liệu không?

Khi vận hành sự cố:

1. Xác định phạm vi: stale read, lost write, divergent replica, split-brain hay cache pollution.
2. Tạm giảm rủi ro bằng read-only mode, route read về primary, disable cache layer hoặc stop promotion tự động nếu cần.
3. Lấy snapshot/log/version trước khi repair thủ công.
4. Chọn source of truth và reconcile theo rule đã định, không merge bằng phỏng đoán.
5. Validate bằng sample read, version comparison, lag metric và business invariant.

## Related Pages

- [Database Sharding And Replication](./02-database-sharding-and-replication.md)
- [Caching Strategies](./01-caching-strategies.md)
- [Distributed Coordination Patterns](./07-distributed-coordination-patterns.md)
- [Distributed Naming And Discovery](./08-distributed-naming-and-discovery.md)
- [Caching, CDN And Read Replica](../04-reliability-and-dr/06-caching-cdn-read-replica.md)
- [NFS, SMB/CIFS và iSCSI Network Storage](../../02-core-infrastructure/01-linux/02-storage-networking/03-nfs-smb-iscsi-network-storage.md)
