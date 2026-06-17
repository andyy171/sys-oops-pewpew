# Node.js Và Express Runtime Operations

## Cách Hiểu Nhanh

Node.js là JavaScript runtime phía server. Với vận hành hạ tầng, điểm quan trọng không phải là cú pháp JavaScript mà là mô hình runtime: một process Node thường chạy event loop, xử lý I/O theo hướng non-blocking, bind vào một port và phục vụ HTTP trực tiếp hoặc sau reverse proxy.

Express là framework HTTP phổ biến trên Node.js. Nó ánh xạ `method + path` thành route handler, đọc request qua object `req` và tạo response qua object `res`.

## Event Loop Và Workload Fit

Node.js phù hợp với workload nhiều I/O như HTTP API, gọi database, cache, queue, object storage hoặc service khác. Khi thao tác I/O đang chờ, event loop có thể tiếp tục xử lý request khác.

Rủi ro chính là CPU-bound work:

- vòng lặp tính toán dài,
- xử lý file lớn đồng bộ,
- JSON parse/stringify payload quá lớn,
- crypto/compression nặng,
- recursion hoặc loop không có điều kiện dừng.

Nếu event loop bị block, toàn bộ process có thể tăng latency hoặc ngừng phản hồi dù CPU/memory chưa cạn. Với workload CPU-heavy, cân nhắc worker thread, job queue, process riêng hoặc runtime khác phù hợp hơn.

## Package Và Dependency

Node project nên khai báo dependency qua `package.json` và lock version bằng lockfile như `package-lock.json`.

Guardrails:

- Commit `package.json` và lockfile; không commit `node_modules/`.
- Build/deploy nên dùng dependency install tái lập được từ lockfile.
- Không dùng package không rõ nguồn gốc cho production path nếu chưa qua dependency review/SBOM/SCA.
- Không chạy lệnh cài package trực tiếp trên server production để "sửa nóng" nếu không có rollback và audit trail.
- Khi dependency có CVE hoặc nghi ngờ bị takeover, cần xác định artifact/image nào chứa package đó, rebuild và rotate secret nếu package có thể đã chạy trong CI/runtime.

## HTTP Server Và Port Binding

Một app Node/Express thường tự bind vào host/port:

```javascript
app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`);
});
```

Production guardrails:

- Host/port nên lấy từ environment variable hoặc config của platform, không hardcode vào code.
- Nếu chạy sau load balancer/reverse proxy, app cần xử lý đúng `Host`, scheme gốc và proxy headers theo policy của platform.
- Health check nên kiểm tra route đại diện cho readiness, không chỉ kiểm tra port mở.
- Log startup phải ghi version/build ID/config tối thiểu nhưng không ghi secret.

## Express Routing Và Request Body

Express route được quyết định bởi HTTP method và path. `GET /echo` và `POST /echo` là hai route khác nhau. Nếu method/path không khớp, client có thể nhận `404` hoặc method error tùy cấu hình.

Các nguồn dữ liệu thường gặp:

| Nguồn | Express field | Guardrail |
|---|---|---|
| Query string | `req.query` | Không chứa secret/PII; validate type và range |
| Route parameter | `req.params` | Validate format, ownership và authorization |
| POST form/body | `req.body` | Cần parser middleware đúng `Content-Type`; validate server-side |
| Header | `req.headers` | Không tin header do client tự gửi nếu không được proxy tin cậy chuẩn hóa |
| Cookie | `req.cookies` hoặc session middleware | Xem như credential; ký/mã hóa khi phù hợp |

Nếu `req.body` rỗng dù client có gửi body, kiểm tra:

```javascript
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
```

Chỉ bật parser cần thiết và đặt giới hạn kích thước body để giảm rủi ro memory pressure hoặc DoS.

## Static File, Template Và Response Format

Express có thể phục vụ static asset bằng `express.static()` và render HTML động qua template engine như EJS.

Guardrails:

- Static directory như `public/` chỉ nên chứa file thật sự được phép public.
- Không đặt secret, `.env`, database file, source nội bộ hoặc artifact build nhạy cảm trong static directory.
- HTML template nên tách khỏi route handler để dễ review và giảm trộn logic với presentation.
- Với EJS, dùng escaped output cho dữ liệu user-controlled. Tránh raw output nếu chưa sanitize rõ ràng.
- API nên trả `Content-Type` đúng, ví dụ JSON qua `res.json()` và text qua `res.type('text/plain')`.
- Content negotiation theo `Accept` header là hữu ích, nhưng không dùng header client-provided làm cơ sở authorization.

## Cookie, Session Và CSRF

Cookie có thể định danh client hoặc giữ session reference, nhưng không nên xem cookie raw là bằng chứng tin cậy tuyệt đối.

Production guardrails:

- Dùng session middleware đã review thay vì tự quản lý session phức tạp bằng cookie tự chế.
- Bật `HttpOnly`, `Secure`, `SameSite` phù hợp cho session cookie.
- Không lưu secret hoặc dữ liệu nhạy cảm trực tiếp trong cookie nếu không có ký/mã hóa và rotation.
- Với state-changing request, cần CSRF control khi cookie-based authentication được dùng từ browser.
- Không log raw cookie/session token.

## Database Access Từ Node.js

SQLite hữu ích cho demo, local tool hoặc workload nhỏ đơn process. Với production web service cần scale ngang, HA hoặc nhiều writer, nên đánh giá RDBMS/server database phù hợp hơn.

Guardrails khi app Node truy cập database:

- Không ghép input client trực tiếp vào SQL string. Dùng placeholder, named parameter hoặc prepared statement.
- Ràng buộc `WHERE` bằng cả resource ID và owner/tenant/session khi update/delete dữ liệu user-owned.
- Sau `UPDATE`/`DELETE`, kiểm tra số row thay đổi để phân biệt `204`, `404` hoặc authorization failure.
- Đóng connection/handle khi process shutdown để giảm rủi ro mất dữ liệu chưa flush.
- Với destructive route như `DELETE`, yêu cầu authentication, authorization, audit log và idempotency/confirmation phù hợp.

## Graceful Shutdown

Node process cần xử lý tín hiệu shutdown để dừng nhận request mới, hoàn tất request đang chạy và đóng tài nguyên:

```javascript
process.on('SIGTERM', async () => {
  server.close(() => {
    console.log('HTTP server closed');
  });
});
```

Pre-check khi deploy/restart:

- Instance mới đã pass readiness chưa.
- Reverse proxy/load balancer đã ngừng gửi traffic tới instance cũ chưa.
- Connection database/cache/queue có thể đóng sạch không.
- Log không còn request in-flight hoặc background job quan trọng.

Rollback:

- Giữ artifact/image release trước đó.
- Nếu có migration database, rollback app phải tương thích schema hoặc có plan rollback dữ liệu riêng.
- Validate bằng health check, synthetic request và error-rate/latency sau deploy.

## Troubleshooting Flow

```bash
curl -v http://example.com/health
curl -v -H "Accept: application/json" http://example.com/api/messages
```

Đọc theo lớp:

- Không connect được: DNS, route, firewall, listener, container port, service target.
- `404`: sai method/path, route order, base path, reverse proxy rewrite.
- `415` hoặc body rỗng: sai `Content-Type`, thiếu parser middleware, body size limit.
- `401/403`: auth/session/cookie/CSRF/header forwarding.
- `5xx`: uncaught exception, dependency lỗi, database timeout, event loop block.
- Latency tăng nhưng CPU thấp: chờ downstream I/O, connection pool cạn, DNS/TLS chậm.
- Latency tăng và CPU cao: CPU-bound JavaScript, JSON payload lớn, loop/recursion lỗi, compression/crypto nặng.

## Related Pages

- [HTTP Và Web Application Operations](../../02-core-infrastructure/02-network/04-protocols-and-services/06-http-web-application-operations.md)
- [Twelve-Factor App](../../01-architecture/00-foundations/01-twelve-factor-app.md)
- [SBOM And Dependency Tracking](../../05-Infrastructure-Automation/03-cicd-devops-integration/03-automation-pipeline-security/SBOM%20&%20dependency%20tracking.md)
- [Threat Modeling, Vulnerability Management And Application Security](../../05-Infrastructure-Automation/02-security-and-hardening/00-fundamentals/04-threat-modeling-vulnerability-management-and-application-security.md)
- [Database Models](../../02-core-infrastructure/04-database-systems/01-database-fundamentals/01-database-models-relational-document-kv-column-graph.md)
