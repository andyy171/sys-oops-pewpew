# HTTP Và Web Application Operations

## Cách Hiểu Nhanh

HTTP là application protocol để client yêu cầu tài nguyên hoặc thao tác từ server. Trong vận hành hạ tầng, HTTP không chỉ là port `80` hay `443`; nó là chuỗi xử lý từ DNS, TCP, TLS, Host header, reverse proxy, route ứng dụng, backend dependency, cache, session và log.

Một request web thông thường đi theo flow:

```text
Browser/client
-> DNS resolve hostname
-> TCP connect tới IP:port
-> TLS handshake nếu dùng HTTPS
-> HTTP request: method, path, headers, optional body
-> web server / reverse proxy / application server
-> static file, API handler hoặc backend dependency
-> HTTP response: status code, headers, optional body
```

Khi debug production, cần tách rõ lỗi ở network transport, TLS, HTTP routing, application logic hay dependency phía sau.

## Web Application Architecture

Một web application thường tách thành các lớp:

| Lớp | Vai trò | Tín hiệu vận hành |
|---|---|---|
| Client | Browser, mobile app, CLI hoặc service khác gửi HTTP request | User agent, request pattern, cookie, retry behavior |
| Web server / reverse proxy | Nhận traffic, TLS termination, static content, routing, rate limit | Access log, error log, upstream status, latency |
| Application server | Chạy business logic, API, render dynamic response | App log, trace, dependency error, thread/event loop saturation |
| Database/cache/object storage | Lưu dữ liệu động hoặc asset | Query latency, connection pool, lock, cache hit ratio |

Static content như image, CSS, JavaScript, file download có thể được phục vụ trực tiếp từ web server, object storage hoặc CDN. Dynamic content thường được sinh bởi application server dựa trên database, cache, queue hoặc service nội bộ.

Production guardrails:

- Không expose trực tiếp backend HTTP nếu đã có reverse proxy/load balancer làm public entrypoint.
- Tách static asset khỏi dynamic API khi cần scale, cache hoặc deploy độc lập.
- Health check phải kiểm tra đúng route đại diện cho backend, không chỉ kiểm tra process proxy còn sống.
- Access log nên có `request_id`, status code, upstream status, latency, bytes, user agent và source IP đã chuẩn hóa qua proxy header.

## API, REST Và Web Client Boundary

API là contract để client, frontend, service nội bộ hoặc bên thứ ba gọi capability của hệ thống mà không cần biết implementation phía sau. Trong web application, API thường chạy trên HTTP và là ranh giới quan trọng giữa frontend, backend, database và service phụ thuộc.

Các mô hình client thường gặp:

| Mô hình | Đặc điểm | Guardrail vận hành |
|---|---|---|
| Thin client | Browser/client chủ yếu hiển thị UI, phần lớn xử lý nằm ở backend | cần backend capacity, session/auth rõ, network latency ảnh hưởng trực tiếp UX |
| Thick client | Client xử lý/lưu trữ nhiều hơn, backend chỉ đồng bộ hoặc cung cấp API phụ trợ | cần update client, offline-state reconciliation, kiểm soát dữ liệu nhạy cảm trên endpoint |
| SPA | Một HTML shell, dữ liệu cập nhật qua API mà không reload toàn trang | cần cache/versioning asset chặt, API auth/CORS/CSP đúng, observability theo route client-side |
| MPA | Mỗi thao tác thường trả một page mới hoặc reload page | đơn giản hơn cho SEO/log page view, nhưng cần tối ưu cache, redirect và form/session flow |

REST không chỉ là "dùng JSON qua HTTP". Với production API, các nguyên tắc thực tế cần giữ là:

- Client-server separation: client gọi resource/API contract ổn định; backend có thể refactor database, service nội bộ hoặc layer bảo mật mà không bắt client đổi cùng lúc.
- Stateless request: mỗi request phải mang đủ authentication/context cần thiết. Nếu dùng session/cookie, session store hoặc token strategy phải có HA, rotation và revocation rõ.
- Layered architecture: client không cần biết request đi qua CDN, WAF, API gateway, reverse proxy hay service nội bộ nào; mỗi layer phải preserve header/tracing/security policy cần thiết.
- API phụ thuộc bên thứ ba phải có timeout, retry có backoff, circuit breaker hoặc degradation path nếu dữ liệu đó không bắt buộc cho mọi request.
- API contract cần versioning/deprecation, error model nhất quán, rate limit, audit log và test backward compatibility trước khi release.

## HTTP Request

Request gồm request line, headers và tùy trường hợp có body:

```text
GET /api/products?page=1 HTTP/1.1
Host: example.com
Accept: application/json
User-Agent: curl/8.0
```

Các phần quan trọng:

- **Method:** `GET` thường dùng để đọc, `POST` để gửi dữ liệu/tạo thao tác, `PUT/PATCH` để cập nhật, `DELETE` để xóa theo API design.
- **Path và query string:** route logic của server, ví dụ `/api/products?page=1`.
- **Host header:** cho phép một IP/web server phục vụ nhiều virtual host; sai `Host` hoặc SNI có thể route nhầm site.
- **Headers:** mang metadata như `Accept`, `Content-Type`, `Authorization`, `Cookie`, tracing header hoặc proxy header.
- **Body:** thường gặp với `POST`, `PUT`, `PATCH`, form upload hoặc JSON API.

Không đưa secret vào URL query string vì URL dễ xuất hiện trong browser history, access log, proxy log và monitoring. Token/session nên đi qua header hoặc cookie có thuộc tính bảo vệ phù hợp.

## URL, Static Asset Và Fragment

Browser resolve URL từ HTML theo ngữ cảnh của document đang tải:

- `logo.png` là relative URL theo đường dẫn hiện tại của document.
- `/assets/logo.png` là root-relative URL trên cùng origin.
- `https://static.example.com/logo.png` trỏ tới origin/CDN khác.

Từ góc nhìn vận hành, server HTTP không bắt buộc map path 1-1 với file trên filesystem. Reverse proxy hoặc application router có thể trả static file, render dynamic page, proxy sang upstream khác, hoặc trả lời `404` tùy theo rule. Khi debug ảnh/CSS/JavaScript không tải được, cần kiểm tra cả URL mà browser request, `Host` header, rewrite rule, CDN cache và MIME type response.

Fragment URL sau dấu `#`, ví dụ `/docs/runbook#rollback`, là phần client-side. Browser có thể dùng nó để scroll đến phần tử có `id`, nhưng fragment không được gửi trong HTTP request. Không thiết kế routing, authorization hoặc server-side tracking dựa vào fragment nếu server cần nhìn thấy giá trị đó.

Static asset guardrails:

- Dùng `alt` cho image quan trọng để giữ accessibility và fallback khi asset lỗi.
- Đặt đúng kích thước hoặc tỉ lệ ảnh để giảm layout shift, nhưng không dùng `width`/`height` để "tối ưu" bằng cách tải ảnh rất lớn rồi thu nhỏ trong browser.
- Chọn định dạng phù hợp: JPEG cho ảnh chụp, PNG cho hình có màu phẳng/cần transparency, SVG cho icon/diagram vector nếu nguồn đáng tin cậy.
- CSS nên được tách thành file external khi dùng lại trên nhiều page để browser/CDN cache được. Khi deploy CSS mới, cần có cache-busting bằng filename hash hoặc versioned URL; nếu không client có thể giữ CSS cũ trong khi HTML/app đã đổi.
- Khi debug visual regression, kiểm tra CSS nào thật sự được tải, HTTP status/MIME type của file CSS, thứ tự stylesheet, rule override/cascade, `!important`, media query và viewport thực tế.
- Responsive CSS dựa trên media query được browser đánh giá lại khi viewport đổi. Validation nên chạy trên kích thước màn hình đại diện, không chỉ một desktop viewport.
- JavaScript external file cũng là static asset được browser tải bằng HTTP `GET`. Khi script lỗi, kiểm tra URL, status code, `Content-Type`, cache version, CSP, SRI nếu có, và thứ tự tải script.
- Với iframe hoặc embedded content từ domain khác, cần review CSP, `X-Frame-Options`, sandbox/clickjacking risk và dữ liệu nào được truyền qua URL.

## Client-side JavaScript Operations

JavaScript chạy trong browser có thể ảnh hưởng trực tiếp đến thời gian render, hành vi UI và dữ liệu gửi về server. Với web operations, cần xem script như một phần của request path, không chỉ là code frontend.

Các điểm cần kiểm tra:

- `<script src="...">` tải file từ cùng origin, CDN hoặc domain khác bằng HTTP `GET`; lỗi DNS/TLS/cache/CORS/CSP đều có thể làm tính năng client-side hỏng dù HTML vẫn trả `200`.
- Script đặt sớm trong document có thể block parsing/render. `defer` thường phù hợp cho script cần DOM đầy đủ và muốn giữ thứ tự thực thi; `async` phù hợp cho script độc lập vì thứ tự chạy phụ thuộc thời điểm tải xong.
- `DOMContentLoaded` cho biết HTML đã được parse xong; nếu script thao tác DOM trước thời điểm phần tử tồn tại, lỗi có thể chỉ xuất hiện ở một số path hoặc browser.
- Browser console là nguồn đầu tiên để kiểm tra JavaScript error, failed resource, CSP violation, mixed content, CORS và source map warning.
- Không tin validation phía client, kể cả logic JavaScript, `required`, type của form, hidden input hoặc disabled field. Backend vẫn phải validate input, authz và state transition.

Security guardrails:

- Không đưa dữ liệu không tin cậy trực tiếp vào `innerHTML`; ưu tiên text-only API hoặc sanitize rõ ràng để giảm XSS.
- Tránh log token, cookie, PII hoặc response nhạy cảm ra console trong production.
- Inline event handler như `onClick` làm CSP khó siết chặt hơn; với production app, ưu tiên bind event trong script được quản lý và deploy qua pipeline.

## HTTP Response Và Status Code

Response gồm status line, headers và body:

```text
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: no-store
```

Nhóm status code:

| Nhóm | Ý nghĩa vận hành |
|---|---|
| `1xx` | Informational, ít khi là trọng tâm debug app thông thường |
| `2xx` | Request được xử lý thành công |
| `3xx` | Redirect hoặc cần hành động tiếp theo |
| `4xx` | Client request không hợp lệ, thiếu auth, bị cấm hoặc resource không tồn tại |
| `5xx` | Server/proxy/backend không xử lý được request hợp lệ |

Các mã thường gặp:

- `200 OK`: request thành công.
- `301/302`: redirect vĩnh viễn/tạm thời; kiểm tra loop HTTP-to-HTTPS hoặc sai canonical host.
- `401`: thiếu hoặc sai authentication.
- `403`: đã hiểu request nhưng policy không cho phép.
- `404`: route/resource không tồn tại hoặc app không muốn tiết lộ resource.
- `500`: lỗi application/server chung.
- `502`: proxy/gateway nhận response lỗi hoặc không hợp lệ từ upstream.
- `503`: service tạm unavailable, overload, maintenance hoặc backend bị rút khỏi pool.
- `504`: gateway/proxy timeout khi chờ upstream.

## Cache Và CDN

HTTP cache giảm latency và giảm tải origin, nhưng cũng có thể làm phát sinh lỗi stale content nếu header sai. Cần phân biệt:

- **Private cache:** cache trong browser hoặc client local.
- **Shared cache:** CDN, forward proxy hoặc cache gateway dùng chung cho nhiều client.

Header hay gặp:

| Header | Vai trò |
|---|---|
| `Cache-Control` | Policy chính: `no-store`, `no-cache`, `max-age`, `s-maxage`, `private`, `public` |
| `ETag` | Định danh version của resource để revalidate |
| `Last-Modified` | Timestamp phục vụ conditional request |
| `Vary` | Cho cache biết response thay đổi theo header nào, ví dụ `Accept-Encoding` |

Guardrails:

- Không cache response chứa dữ liệu user-specific ở shared cache nếu thiếu `private` hoặc `no-store`.
- Static asset nên dùng filename có hash và cache TTL dài.
- HTML shell hoặc API dynamic cần TTL thận trọng, đặc biệt khi có auth/session.
- Khi purge CDN/cache, validate từ client path thật thay vì chỉ kiểm tra origin.

## Cookie Và Session

HTTP về bản chất là request/response rời rạc. Session thường được duy trì bằng cookie chứa session ID hoặc token tham chiếu tới state phía server.

Server đặt cookie qua `Set-Cookie`; client gửi lại qua `Cookie` trong các request tiếp theo. Với production, cookie/session phải được coi là credential:

- Bật `Secure` để cookie chỉ gửi qua HTTPS.
- Dùng `HttpOnly` cho session cookie để giảm rủi ro bị đọc bởi JavaScript khi có XSS.
- Dùng `SameSite=Lax` hoặc `Strict` khi phù hợp để giảm CSRF.
- Không lưu secret nhạy cảm trực tiếp trong cookie nếu không có cơ chế ký/mã hóa và rotation rõ ràng.
- Session store cần HA/replication hoặc stateless token design có revocation strategy.

Session hijacking thường xảy ra khi attacker lấy được cookie/session token. Vì vậy access log, debug log và APM trace không được ghi raw cookie/token.

## Form Submission Và Upload

HTML form là cách browser đóng gói dữ liệu người dùng thành HTTP request. Các thuộc tính quan trọng với backend/proxy:

- `action`: endpoint nhận request; tuân theo cùng quy tắc relative/absolute URL như link và static asset.
- `method`: `GET` đưa field vào query string, `POST` đưa dữ liệu vào request body.
- `name`: tên field được server nhận; `id` chủ yếu phục vụ DOM/label phía client.
- `enctype`: cách encode body; file upload cần `multipart/form-data`.

Production guardrails:

- Dùng `GET` cho thao tác đọc, search, filter hoặc request idempotent có thể bookmark/cache. Dùng `POST` cho thao tác tạo/sửa, dữ liệu lớn, dữ liệu binary, hoặc dữ liệu nhạy cảm.
- Không đưa password, token, PII hoặc secret vào query string vì chúng dễ xuất hiện trong access log, browser history, referrer, cache và monitoring.
- Client-side validation như `required`, `type=email`, `accept`, `min/max` chỉ là UX hint. Server phải validate lại schema, length, range, MIME/content và authorization.
- Hidden input không phải secret. Client có thể sửa giá trị trước khi submit; server phải verify chữ ký, expiry, CSRF token và ownership nếu giá trị ảnh hưởng đến state.
- File upload cần giới hạn size, validate content thay vì chỉ tin extension/MIME header, scan malware nếu phù hợp, randomize filename, và lưu ngoài executable web root hoặc object storage private.
- Log request form cần redact field nhạy cảm. Dùng allowlist field khi debug production thay vì dump toàn bộ body.

## HTTPS Và TLS

HTTPS là HTTP chạy trong kênh TLS. TLS bảo vệ HTTP headers và body trên đường truyền sau khi handshake hoàn tất, nhưng metadata như destination IP, port và một phần thông tin handshake vẫn có thể quan sát được tùy cấu hình.

Điểm cần kiểm tra khi lỗi HTTPS:

```bash
curl -vk https://example.com/
openssl s_client -connect example.com:443 -servername example.com
```

Checklist:

- DNS trỏ đúng endpoint.
- TCP port `443` reachable.
- Certificate còn hạn, đúng hostname/SAN, chain đầy đủ.
- Client gửi đúng SNI nếu một IP phục vụ nhiều hostname.
- Reverse proxy forward đúng `Host` và `X-Forwarded-Proto` nếu app cần biết scheme gốc.
- Không tạo redirect loop giữa load balancer, proxy và app.

## Troubleshooting Flow

Kiểm tra theo lớp, từ ngoài vào trong:

```bash
dig example.com
curl -v http://example.com/
curl -vk https://example.com/
curl -vk https://example.com/health
```

Đọc kết quả:

- DNS fail: kiểm tra record, resolver, TTL, split-horizon DNS.
- TCP timeout: route, firewall, security group, load balancer listener.
- TLS fail: certificate, chain, SNI, TLS policy, client compatibility.
- `301/302` loop: HTTP-to-HTTPS redirect, canonical host, `X-Forwarded-Proto`.
- `401/403`: auth, policy, WAF, missing header/cookie.
- `404`: route, virtual host, deployment artifact, rewrite rule.
- `5xx`: proxy upstream, app crash, dependency failure, pool saturation.

Khi thay đổi cấu hình web server/reverse proxy trong production:

1. Backup config hoặc bảo đảm thay đổi đi qua Git/IaC.
2. Chạy config test nếu tool hỗ trợ.
3. Reload thay vì restart khi có thể.
4. Validate bằng request thật qua public/internal entrypoint.
5. Có rollback về config/listener/rule trước đó.

## Trang Liên Quan

- [Common Network Protocols And Ports](./01-common-network-protocols-and-ports.md)
- [DNS, DHCP And Core Network Protocols](./02-dns-dhcp-and-core-protocols.md)
- [Proxy, Load Balancer, VPN And Expose Endpoints](./03-proxy-load-balancer-vpn-and-expose-endpoints.md)
- [Network Troubleshooting Tools](../07-network-operations-lifecycle/03-network-troubleshooting-tools.md)
- [Node.js Và Express Runtime Operations](../../../03-compute-and-orchestration/01-compute-platforms/02-nodejs-express-runtime-operations.md)
