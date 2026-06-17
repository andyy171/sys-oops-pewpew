# Scalability, Availability And Consistency

Ba thuộc tính này thường bị nhắc chung với nhau, nhưng chúng trả lời ba câu hỏi khác nhau:

- **Scalability:** hệ thống có thể tăng capacity khi tải tăng không.
- **Availability:** hệ thống có tiếp tục phục vụ request khi một phần bị lỗi không.
- **Consistency:** các node/client có nhìn thấy cùng một trạng thái dữ liệu tại cùng một thời điểm không.

## CAP Theorem

Trong distributed system, khi xảy ra network partition, hệ thống phải chọn ưu tiên giữa consistency và availability.

| Lựa chọn | Ý nghĩa | Hệ quả |
|---|---|---|
| CP | Ưu tiên consistency khi partition xảy ra | Có thể từ chối request để tránh đọc/ghi sai |
| AP | Ưu tiên availability khi partition xảy ra | Có thể trả dữ liệu cũ hoặc cần reconcile sau |
| CA | Consistent và available khi không có partition | Không phải mô hình thực tế cho hệ thống phân tán qua network không tin cậy |

Partition tolerance không phải thứ có thể bỏ qua trong hệ thống phân tán thật. Network có thể chậm, mất gói, split-brain hoặc timeout.

## Scalability Không Đồng Nghĩa Với Availability

Một hệ thống có thể scale tốt nhưng vẫn kém available nếu:

- Có single point of failure như một database primary không có failover.
- Scale app layer nhưng state/session vẫn nằm trên một node.
- Không có health check, retry budget hoặc circuit breaker.
- Dependency phía sau không scale theo.

Ngược lại, một hệ thống có HA tốt vẫn có thể không scale nếu mọi request đều đổ vào một bottleneck chung.

## Consistency Là Một Spectrum

- **Strong consistency:** đọc sau ghi luôn thấy dữ liệu mới nhất.
- **Read-your-writes:** user đọc lại thấy chính thay đổi của mình.
- **Monotonic reads:** user không thấy dữ liệu quay ngược thời gian.
- **Eventual consistency:** hệ thống sẽ hội tụ sau một khoảng thời gian.

## Câu Hỏi Thiết Kế

- Dữ liệu nào bắt buộc strong consistency.
- Dữ liệu nào chấp nhận eventual consistency.
- Khi dependency lỗi, hệ thống nên fail closed hay degrade gracefully.
- Người dùng có cần thấy trạng thái real-time không hay chỉ cần gần đúng.
- Recovery/reconciliation sau partition diễn ra ở đâu và ai chịu trách nhiệm.

## Liên Quan

- [Availability Vs Consistency](../02-tradeoffs/01-availability-vs-consistency.md)
- [Replication Strategies](../04-reliability-and-dr/05-replication-strategies.md)
