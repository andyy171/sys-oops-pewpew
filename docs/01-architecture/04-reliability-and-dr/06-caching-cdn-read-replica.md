# Caching, CDN And Read Replica

Caching, CDN và read replica là các lớp giảm tải và giảm latency, nhưng chúng không giống nhau.

## Cache

Cache lưu dữ liệu thường đọc gần application hoặc user hơn. Cache phù hợp với dữ liệu đọc nhiều, thay đổi ít hoặc chấp nhận stale trong thời gian ngắn.

## CDN

CDN đưa static content hoặc cacheable response ra edge gần user. CDN tốt cho asset, image, video, static page và API response có cache-control rõ ràng.

CDN hoạt động bằng hai cơ chế chính:

- **Redirection:** đưa client tới edge phù hợp bằng DNS, HTTP redirect, anycast hoặc provider-specific routing.
- **Edge caching:** edge fetch từ origin khi cache miss, lưu response theo TTL/cache-control rồi phục vụ request sau gần user hơn.

DNS redirection thường trong suốt với client nhưng độ chính xác locality phụ thuộc resolver mà client dùng, TTL và cách CDN nhìn vị trí nguồn truy vấn. HTTP redirection linh hoạt ở mức URL/document hơn nhưng visible với browser/user và có thể bị bookmark hoặc cache sai nếu policy không rõ.

Dynamic content chỉ nên đưa ra CDN khi cache key và privacy boundary rõ. Cache key phải bao gồm các dimension ảnh hưởng response như host, path, query cần thiết, locale, device class, auth state hoặc feature flag. Response có dữ liệu user-specific mặc định nên dùng `private` hoặc `no-store`, trừ khi có thiết kế fragment/cache partition an toàn.

Edge selection không chỉ dựa vào latency gần nhất. CDN hoặc routing layer còn phải xét health, capacity, origin cost, data residency và failure domain. Khi edge trả sai hoặc stale, cần có đường bypass/purge và metric để phát hiện tỷ lệ hit bất thường, origin fetch surge, stale response và 5xx theo edge.

## Read Replica

Read replica sao chép database để tách read workload khỏi primary. Nó giúp giảm tải primary nhưng có replication lag.

## Tradeoff

| Lớp | Giảm latency | Giảm tải backend | Rủi ro |
|---|---|---|---|
| Cache app | Có | Có | Stale data, stampede |
| CDN | Rất tốt cho edge | Có | Invalidation khó |
| Read replica | Tốt cho read DB | Có | Lag, read-after-write issue |

## Checklist

- Dữ liệu có cache được không.
- TTL nên theo business freshness hay technical convenience.
- Có cần read-your-writes không.
- Cache/CDN invalidation do ai quản lý.
- Khi cache/CDN lỗi, backend có chịu được tải không.
- CDN có bypass/purge/rollback path không nếu cache sai nội dung.
- Origin có rate limit/backpressure để tránh cache miss storm không.

## Related Pages

- [Replication And Consistency Models](../03-patterns/09-replication-consistency-models.md)
