# Distributed Naming And Discovery

## Overview

Naming trả lời câu hỏi "đối tượng này là gì?", discovery/location trả lời "truy cập nó ở đâu và bằng cách nào?". Trong distributed system, hai câu hỏi này thường bị tách ra vì entity có thể di chuyển, có nhiều replica, đổi access point hoặc được cache/route qua nhiều tầng.

Một thiết kế naming tốt giúp service đổi IP, scale replica, migrate location và thay backend mà client không phải đổi logic. Một thiết kế naming kém làm address bị dùng như identity, khiến migration, failover và multi-region trở nên giòn.

## Names, Identifiers And Addresses

| Loại | Ý nghĩa | Ví dụ | Guardrail |
|---|---|---|---|
| Name | Chuỗi dùng để tham chiếu entity | `api.example.com`, `/srv/data/report.csv` | Có thể human-friendly nhưng không nhất thiết unique toàn cục |
| Identifier | Tên ổn định, không tái sử dụng cho entity khác | UUID, content hash, object ID | Không nên encode location nếu muốn location-independent |
| Address | Tên của access point | IP:port, endpoint URL, MAC address | Có thể đổi hoặc được tái gán; không dùng làm identity lâu dài |

Identifier-location split là nguyên tắc quan trọng: entity nên có identity ổn định, còn location/access point nên được resolve riêng. Nếu client lưu trực tiếp IP, mount path hoặc instance address như identity, failover và migration sẽ cần sửa client hoặc chấp nhận reference lỗi.

## Flat Naming

Flat name là identifier không có cấu trúc và không chứa hint để tìm entity. Muốn resolve flat name, hệ thống cần location service.

| Cách resolve | Mental model | Điểm mạnh | Rủi ro |
|---|---|---|---|
| Broadcast/multicast | Hỏi toàn bộ hoặc một nhóm node "ai giữ entity này?" | Đơn giản trong LAN | Không scale, tạo interrupt/traffic rộng |
| Forwarding pointer | Entity di chuyển thì để lại pointer tới nơi mới | Dễ triển khai cho mobility | Chain dài, pointer hỏng làm mất đường |
| Home location | Một home agent biết location hiện tại | Dễ bootstrap, cache được home | Home là dependency; đường đi có thể vòng xa |
| Distributed Hash Table | Hash key vào identifier space, route tới node chịu trách nhiệm | Scale tốt, lookup thường `O(log N)` | Churn, hot key, proximity, Sybil/eclipse attack |
| Hierarchical location service | Domain tree lưu pointer theo locality | Khai thác locality, hỗ trợ nhiều replica | Root/logical top phải được triển khai HA và phân tán đúng |

Production guardrails:

- Cache location cần TTL/invalidation rõ; cache quá lâu sẽ làm client bám endpoint cũ.
- Mobility/failover cần cơ chế cleanup pointer cũ và phát hiện broken link.
- Home agent hoặc root logical phải có HA, backup, observability và DDoS/rate-limit strategy.
- Nếu entity có nhiều replica, resolver phải có policy chọn replica: locality, health, capacity, cost, compliance.

## DHT And Chord-Style Lookup

DHT map key vào một identifier space lớn. Trong Chord-like ring, key thuộc về successor node gần nhất theo chiều ring. Mỗi node giữ successor/predecessor và finger table để forward lookup theo bước nhảy tăng dần, thay vì đi tuyến tính quanh ring.

Operational points:

- Successor entry phải đúng trước; finger table tối ưu lookup nhưng stale finger không được làm ring mất khả năng tiến tới successor.
- Background stabilization cần chạy đều để xử lý join/leave/failure.
- Lookup path logic có thể đúng nhưng network path tệ nếu overlay không biết proximity.
- Hot key cần replication, caching hoặc virtual nodes; DHT không tự giải quyết skew workload.
- Node identity cần chống giả mạo nếu chạy trong môi trường không trusted; DHT mở dễ bị Sybil/eclipse attack.

Proximity-aware DHT có ba hướng:

- gán identifier theo topology, nhưng dễ tạo correlated failure;
- proximity routing, chọn next hop gần nhất trong nhiều candidate hợp lệ;
- proximity neighbor selection, ưu tiên neighbor gần khi xây routing table.

## Hierarchical Name Spaces

Structured name thường được tổ chức thành name space dạng cây hoặc DAG. Directory node ánh xạ label sang node identifier; leaf node chứa entity hoặc metadata để truy cập entity.

Các khái niệm cần phân biệt:

- **Absolute path:** bắt đầu từ root của name space cụ thể.
- **Relative path:** được hiểu từ một directory/context hiện tại.
- **Global name:** resolve giống nhau ở mọi nơi vì closure/context thống nhất.
- **Local name:** nghĩa phụ thuộc context, ví dụ biến môi trường, working directory, container root.
- **Closure mechanism:** cách hệ thống biết bắt đầu resolve ở đâu, ví dụ root filesystem, DNS resolver, mount namespace hoặc `chroot`.

Aliases có hai kiểu phổ biến:

- hard link: nhiều path trỏ cùng node/entity;
- symbolic link: node chứa path khác và resolution tiếp tục theo path đó.

Mounting là cách ghép name space khác vào name space hiện tại. Trong distributed system, mount point thường cần ba thông tin: access protocol, server name/address và remote mounting point.

## DNS As Naming Service

DNS là distributed naming service lớn cho Internet. Nó map human-friendly name sang resource records như `A`, `AAAA`, `CNAME`, `MX`, `NS`, `SRV`, `PTR`, `TXT`, `SOA`.

Mental model:

- Domain là subtree logic.
- Zone là phần name space được một authority vận hành.
- Authoritative server giữ dữ liệu chính thức của zone.
- Recursive resolver hỏi thay client và cache theo TTL.
- CNAME giống symbolic link ở DNS level.
- SRV giúp client tìm service theo tên service/protocol thay vì hardcode host.

DNS scale nhờ hierarchy, caching, replication và tách logical design khỏi physical deployment. Ví dụ root logical có thể được anycast/replicate ở nhiều site.

## Attribute-Based Naming

Attribute-based naming tìm entity theo mô tả `(attribute, value)` thay vì path/identifier cố định. LDAP, Active Directory và nhiều resource discovery system dùng mô hình này.

Tradeoff chính:

- mạnh cho search và policy;
- cần schema/attribute governance;
- search phân tán đắt hơn lookup theo key;
- index phải cân bằng giữa latency, consistency, privacy và write amplification.

Với directory service production, cần quản lý:

- schema và naming convention;
- index cho attribute hay query phổ biến;
- replication delay và stale read;
- access control trên attribute nhạy cảm;
- audit cho thay đổi group, role, email, owner, service account.

## Named-Data Networking

Named-data networking hoặc information-centric networking bỏ bước "resolve name ra address rồi connect tới host". Client yêu cầu dữ liệu theo tên; network route interest theo name prefix, trả data và có thể cache data trên router.

Mental model của NDN router:

- **Content store:** cache data theo name.
- **Pending interest table:** nhớ request nào đang chờ để trả data về đúng interface.
- **Forwarding information base:** quyết định forward interest theo prefix/policy.

Guardrails:

- Data nên immutable hoặc versioned; nếu data đổi nhưng tên không đổi, cache rất khó đúng.
- Name phải gắn được với content bằng signature/hash nếu không muốn tin toàn bộ path/router.
- Cache policy cần xét sensitivity, freshness, revocation và poisoning risk.
- NDN phù hợp với content distribution/read-heavy workload hơn là transaction mutable state.

## Design Checklist

- Entity có identifier ổn định tách khỏi address không?
- Resolver/cache có TTL, invalidation và negative cache policy rõ không?
- Lookup path có HA và observability không?
- Resolver chọn replica theo health/capacity/locality hay chỉ trả record tĩnh?
- Naming system có chống stale pointer, hijack, spoofing, Sybil hoặc cache poisoning không?
- Attribute/search query có index và access control đủ không?
- Client có fallback khi resolver lỗi hoặc trả nhiều endpoint không?

## Related Pages

- [Distributed System Architecture Styles](./06-distributed-system-architecture-styles.md)
- [Distributed Coordination Patterns](./07-distributed-coordination-patterns.md)
- [DNS, DHCP And Core Network Protocols](../../02-core-infrastructure/02-network/04-protocols-and-services/02-dns-dhcp-and-core-protocols.md)
- [NFS, SMB/CIFS và iSCSI Network Storage](../../02-core-infrastructure/01-linux/02-storage-networking/03-nfs-smb-iscsi-network-storage.md)
- [Identity, Authentication And Authorization](../../05-infrastructure-automation/02-security-and-hardening/01-access-control/01-identity-authentication-authorization.md)
