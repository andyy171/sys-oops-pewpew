# PoC Evaluation Framework

Proof of Concept không chỉ là kiểm tra một giải pháp có chạy được hay không. Một PoC kiến trúc tốt kiểm chứng một giả thuyết cụ thể: giải pháp này có cải thiện performance, reliability, cost, operability hoặc security trong điều kiện gần production không.

## Bắt Đầu Bằng Giả Thuyết

PoC nên viết rõ:

- vấn đề đang giải quyết;
- baseline hiện tại;
- metric thành công;
- workload mô phỏng;
- ràng buộc vận hành;
- điều kiện loại bỏ giải pháp.

Nếu không có baseline và metric, PoC dễ biến thành demo cảm tính.

## Đánh Giá Day 1 Và Day 2

Day 1 trả lời: triển khai ban đầu có khả thi không.

Day 2 trả lời: vận hành lâu dài có chịu được không.

| Góc đánh giá | Câu hỏi |
|---|---|
| Deploy | có tự động hóa được không, rollback thế nào |
| Integrate | có khớp với identity, network, CI/CD, logging, monitoring không |
| Operate | ai patch, backup, restore, upgrade và debug |
| Scale | behavior khi tăng tải có giống kỳ vọng không |
| Failure | failure mode nào xuất hiện và recovery mất bao lâu |
| Cost | chi phí theo traffic/storage/egress/support có dự đoán được không |

## Metric Cần Chốt Trước

- latency p50/p95/p99;
- throughput;
- error rate;
- recovery time;
- deployment lead time;
- operational toil;
- cost per unit workload;
- supportability và skill requirement.

## Exit Strategy

Một PoC không có exit strategy dễ tạo lock-in sớm. Cần kiểm tra:

- dữ liệu export được không;
- format có portable không;
- workload có chạy được ở platform khác không;
- dependency nào là provider-specific;
- rollback về trạng thái cũ mất bao lâu.

## Anti-Patterns

- Chọn công nghệ vì demo đẹp nhưng không test failure.
- Dùng toy workload rồi suy luận cho production.
- Bỏ qua vận hành day-2 vì "managed service lo hết".
- Không tính migration/exit cost.
- Chỉ đo average latency, bỏ qua tail latency.

## Trang Liên Quan

- [Control Vs Abstraction](./04-control-vs-abstraction.md)
- [Scalability Vs Maintainability](./03-scalability-vs-maintainability.md)
- [Workload Patterns](../01-principles/04-workload-patterns.md)
