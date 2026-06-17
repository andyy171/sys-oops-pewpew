# Scalability Vs Maintainability

Scalability giúp hệ thống chịu tải lớn hơn. Maintainability giúp hệ thống dễ hiểu, dễ thay đổi và dễ vận hành lâu dài.

## Tradeoff Cốt Lõi

Một thiết kế scale tốt thường thêm nhiều thành phần: cache, queue, replica, shard, service, region. Mỗi thành phần tăng capacity nhưng cũng tăng cognitive load, failure mode và chi phí vận hành.

## Dấu Hiệu Over-Engineering

- Tách microservice khi team chưa cần release độc lập.
- Dùng distributed cache khi database vẫn chưa tối ưu index/query.
- Dùng multi-region trước khi có backup/restore test ở single region.
- Thêm queue nhưng không có dashboard queue lag, retry và DLQ.
- Sharding trước khi có số liệu capacity rõ ràng.

## Nguyên Tắc

- Scale theo bottleneck thật, không scale theo cảm giác.
- Ưu tiên thiết kế đơn giản cho đến khi metric chứng minh cần phức tạp hơn.
- Mỗi thành phần mới phải có owner, dashboard, alert, backup hoặc runbook nếu cần.
- Khi thêm abstraction, ghi rõ nó giảm vấn đề gì và tạo thêm rủi ro gì.

## Decision Checklist

- Tải hiện tại và tải dự báo là bao nhiêu.
- Bottleneck đã được đo chưa.
- Giải pháp đơn giản hơn có đáp ứng 6-12 tháng tới không.
- Team có đủ năng lực vận hành thành phần mới không.
- Nếu thành phần mới lỗi, blast radius là gì.
