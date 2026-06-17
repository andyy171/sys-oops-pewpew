# Database Sharding And Replication

Replication và sharding đều giúp database scale hoặc tăng resilience, nhưng chúng giải quyết hai vấn đề khác nhau.

## Replication

Replication sao chép dữ liệu giữa nhiều node.

Mục tiêu:

- Tăng availability.
- Hỗ trợ read scaling bằng read replica.
- Giảm rủi ro mất dữ liệu.
- Hỗ trợ failover và DR.

Kiểu phổ biến:

- Primary-replica.
- Multi-primary.
- Synchronous replication.
- Asynchronous replication.
- Quorum-based replication.

Tradeoff chính là latency, consistency và failover complexity.

Replication trong database cần tách hai câu hỏi:

- **Có bao nhiêu bản sao và ai nhận write?** Ví dụ primary-replica, multi-primary, synchronous/asynchronous replication hoặc quorum-based replication.
- **Client được thấy trạng thái nào?** Ví dụ linearizable read, read-your-writes, monotonic read hoặc eventual read từ replica có lag.

Read replica giúp scale read nhưng không miễn phí: nếu application vừa ghi rồi đọc từ replica stale, user có thể thấy dữ liệu cũ. Với workflow cần read-your-writes, cần route read về primary, dùng session/version token, hoặc chỉ đọc replica đã catch up tới commit/version vừa ghi.

Failover phải có fencing/epoch/term rõ để primary cũ không tiếp tục nhận write sau network partition. Trước khi promote replica, kiểm tra replication lag, last applied/committed position và backup/snapshot gần nhất.

## Sharding

Sharding chia dữ liệu thành nhiều phần theo shard key. Mỗi shard chỉ giữ một phần dữ liệu.

Mục tiêu:

- Scale write/read capacity vượt giới hạn một node.
- Giảm kích thước dataset trên mỗi node.
- Tách failure domain theo partition.

Rủi ro:

- Chọn shard key sai gây hot shard.
- Cross-shard query phức tạp.
- Resharding tốn kém và rủi ro.
- Transaction xuyên shard khó hơn.

## Replication Vs Sharding

| Câu hỏi | Replication | Sharding |
|---|---|---|
| Tăng read capacity | Có | Có |
| Tăng write capacity | Hạn chế | Có |
| HA/failover | Có | Cần kết hợp replication |
| Complexity | Trung bình | Cao |
| Query đơn giản | Gần như giữ nguyên | Phụ thuộc shard key |

## Design Checklist

- Dataset lớn do read, write hay storage size.
- Có query nào bắt buộc cross-shard không.
- Shard key có phân phối đều không.
- Failover trong từng shard diễn ra thế nào.
- Backup/restore là theo từng shard hay toàn cụm.
- Rebalancing/resharding có kế hoạch không.

## Related Pages

- [Replication And Consistency Models](./09-replication-consistency-models.md)
