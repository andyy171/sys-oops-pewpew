# Multi-Region Architecture

Multi-region architecture chạy hệ thống qua nhiều region để tăng resilience, giảm latency địa lý hoặc đáp ứng yêu cầu data locality.

## Mô Hình

| Mô hình | Ý nghĩa | Tradeoff |
|---|---|---|
| Backup region | Region phụ chỉ dùng khi DR | Rẻ hơn, RTO dài hơn |
| Active-passive | Một region phục vụ chính, region phụ standby | Dễ kiểm soát hơn active-active |
| Active-active | Nhiều region cùng phục vụ | Latency tốt hơn nhưng consistency và routing phức tạp |
| Cell-based | Chia user/workload thành cell độc lập | Giảm blast radius nhưng vận hành phức tạp |

## Thành Phần Cần Thiết

- Global traffic routing: DNS, GSLB, Anycast hoặc provider traffic manager.
- Data replication strategy.
- Artifact/image distribution gần từng region.
- Secret/config distribution.
- Observability theo region.
- Runbook failover và failback.

## Progressive Global Rollout

Multi-region không chỉ là chạy nhiều bản sao. Release cũng phải đi theo blast radius nhỏ dần:

```text
canary/internal region
-> low-traffic production region
-> high-traffic region có input tương tự
-> region có traffic/input khác biệt
-> parallel rollout khi đã đủ confidence
```

Trước khi rollout rộng, cần integration test và load test đủ gần production. Dataset, request replay và production-like traffic giúp bắt lỗi mà unit test không thấy, nhưng phải xử lý dữ liệu thật như dữ liệu nhạy cảm: sanitize, access control, retention và audit.

`time-to-smoke` là thời gian chờ giữa các wave để lỗi có cơ hội lộ ra. Nó nên dựa trên lịch sử incident của chính hệ thống, không phải một con số cảm tính.

## Câu Hỏi Thiết Kế

- Dữ liệu có được phép rời region không.
- Write diễn ra ở một region hay nhiều region.
- Conflict được xử lý ở application, database hay workflow.
- RTO/RPO mục tiêu là gì.
- Khi một region hồi phục, failback có an toàn không.
- Nếu phải drain traffic khỏi region, mất bao lâu để 90% hoặc 99% traffic rời khỏi region đó.

## Anti-Pattern

- Multi-region app nhưng database chỉ có một primary không có DR test.
- DNS failover TTL dài hơn RTO mong muốn.
- Không có synthetic check theo từng region.
- Không diễn tập failover.
- Rollout đồng thời toàn bộ region mà không có canary/time-to-smoke.

## Trang Liên Quan

- [Kubernetes Environment Promotion, Release Và Rollback](../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/06-packaging-and-gitops/05-environment-promotion-release-and-rollback.md)
