# Stateless Vs Stateful

Stateless và stateful là cách hệ thống quản lý trạng thái giữa các request hoặc giữa các lần process restart.

## Stateless

Một service stateless không phụ thuộc vào state cục bộ để xử lý request tiếp theo. Mọi state cần thiết nằm trong request, token hoặc backing service như database/cache/object storage.

Ưu điểm:

- Dễ scale ngang bằng cách thêm instance.
- Dễ rolling update và thay node lỗi.
- Load balancer không cần sticky session.
- Phù hợp với container orchestration và immutable infrastructure.

Rủi ro:

- Dependency vào backing service tăng lên.
- Latency có thể tăng nếu mỗi request phải đọc state từ ngoài.
- Cần thiết kế cache/session/token cẩn thận.

## Stateful

Một service stateful giữ dữ liệu quan trọng trong memory/disk/local process hoặc cần identity ổn định giữa các lần chạy.

Ví dụ:

- Database primary/replica.
- Kafka broker.
- Redis khi dùng làm state store.
- Stateful workload có local disk, WAL, shard hoặc quorum membership.

## Soft State, Session State Và Permanent State

Không phải state nào cũng có cùng yêu cầu durability:

| Loại state | Ý nghĩa | Nếu mất thì sao |
| --- | --- | --- |
| Soft state | Server giữ tạm theo TTL/lease, hết hạn thì quay về default behavior | Client có thể renew, poll lại hoặc chịu degrade ngắn |
| Session state | Gắn với một phiên/user/workflow trong thời gian giới hạn | Có thể buộc user retry hoặc re-issue request nếu thiết kế cho phép |
| Permanent state | Dữ liệu bền vững như order, payment, account, object metadata, WAL | Mất state là mất dữ liệu hoặc vi phạm consistency |

Thiết kế tốt không chỉ hỏi "stateless hay stateful" mà hỏi state nằm ở đâu, ai sở hữu, TTL bao lâu, recover ra sao và client có thể replay request an toàn không. Cookie, token hoặc client-side cache có thể giúp server stateless hơn, nhưng cũng chuyển một phần rủi ro sang bảo mật, freshness và revoke.

## Quy Tắc Thiết Kế

- App/API layer nên stateless nếu có thể.
- State bền vững nên nằm trong storage/database/queue được thiết kế cho durability.
- Session user nên đặt ở cache/database hoặc token, không đặt trong RAM của một web instance.
- Stateful service cần runbook backup, restore, failover và capacity planning riêng.
- Nếu dùng soft state, cần TTL, renewal interval và behavior khi lease hết hạn rõ ràng.
- Nếu dùng session state, cần quyết định sticky session, shared session store hoặc stateless token; đừng để load balancer affinity là cơ chế recovery duy nhất.

## Anti-Pattern

- Lưu file upload trên local disk của web server nhưng lại scale nhiều instance.
- Dùng sticky session để che lỗi thiết kế state.
- Chạy database như container stateless mà không thiết kế persistent volume, backup và recovery.

## Liên Quan

- [Twelve-Factor App](../00-foundations/01-twelve-factor-app.md)
- [RTO/RPO Design](../04-reliability-and-dr/07-rto-rpo-design.md)
