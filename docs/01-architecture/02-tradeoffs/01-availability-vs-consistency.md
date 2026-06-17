# Availability Vs Consistency

Availability vs consistency là tradeoff xuất hiện khi hệ thống phân tán gặp network partition, timeout, replication lag hoặc dependency failure. CAP theorem là nền tảng, nhưng quyết định kiến trúc thực tế thường nằm ở từng loại dữ liệu và từng hành vi người dùng.

## Bối Cảnh

Trong hệ thống phân tán thật, partition tolerance gần như bắt buộc vì network có thể chậm, mất gói, split-brain hoặc timeout. Khi hai phần của hệ thống không còn thống nhất được với nhau, bạn phải chọn ưu tiên:

- từ chối hoặc trì hoãn request để bảo vệ correctness;
- tiếp tục phục vụ request và chấp nhận reconcile sau.

## Khi Ưu Tiên Consistency

Ưu tiên consistency khi dữ liệu sai gây hậu quả lớn hơn downtime ngắn:

- số dư tài khoản, giao dịch tài chính, quota critical;
- inventory không được bán vượt;
- quyền truy cập và policy bảo mật;
- workflow cần thứ tự trạng thái chặt.

Chi phí thường gặp:

- request có thể bị reject hoặc timeout;
- write path cần quorum/leader;
- tail latency tăng khi dependency chậm;
- failover phức tạp hơn.

## Khi Ưu Tiên Availability

Ưu tiên availability khi phục vụ gần đúng tốt hơn dừng hẳn:

- feed, timeline, search index, analytics;
- cache và read replica;
- telemetry hoặc event ingestion có thể replay;
- user-facing status không cần real-time tuyệt đối.

Chi phí thường gặp:

- stale read;
- conflict cần resolve;
- reconciliation job;
- UX phải nói rõ trạng thái pending hoặc eventually consistent.

## Safety, Liveness And Partition Decision

Trong CAP, consistency gần với **safety**: không trả kết quả sai, không ghi hai sự thật mâu thuẫn. Availability gần với **liveness**: request cuối cùng sẽ nhận được phản hồi. Khi partition xảy ra, hệ thống không thể giữ cả hai cho cùng một shared state.

Quyết định production nên theo từng operation:

- operation tài chính, quota critical, permission và inventory thường nên fail closed để bảo vệ safety;
- feed, search, analytics, telemetry và cache có thể ưu tiên liveness nếu có reconcile;
- nếu chọn availability, phải có conflict detection, audit và compensation path;
- nếu chọn consistency, phải chấp nhận reject/timeout và có UX hoặc retry policy rõ.

## Decision Checklist

- Dữ liệu này có thể stale bao lâu.
- Có thể replay hoặc compensate khi ghi sai không.
- User cần read-your-writes hay chỉ cần eventual convergence.
- Conflict được resolve ở app, database hay workflow riêng.
- Khi partition xảy ra, fail closed hay degrade gracefully.
- Có metric nào báo replication lag, conflict rate và reconciliation backlog không.

## Liên Quan

- [Scalability, Availability And Consistency](../01-principles/01-scalability-availability-consistency-cap.md)
- [Replication Strategies](../04-reliability-and-dr/05-replication-strategies.md)
- [Distributed Fault Tolerance And Recovery](../04-reliability-and-dr/10-distributed-fault-tolerance-and-recovery.md)
