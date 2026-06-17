# Replication Strategies

Replication sao chép dữ liệu hoặc state giữa nhiều node/region để tăng durability, availability hoặc read scalability.

## Synchronous Replication

Write chỉ được xem là thành công khi replica xác nhận.

Ưu điểm:

- RPO thấp.
- Giảm nguy cơ mất dữ liệu.

Nhược điểm:

- Tăng write latency.
- Khi replica/network chậm, availability có thể giảm.

## Asynchronous Replication

Primary xác nhận write trước, replica nhận sau.

Ưu điểm:

- Write latency thấp hơn.
- Phù hợp cross-region hơn.

Nhược điểm:

- Có replication lag.
- Failover có thể mất dữ liệu gần nhất.

## Quorum Replication

Write/read cần số node tối thiểu xác nhận. Mô hình này cân bằng consistency và availability bằng quorum.

## Multi-Primary

Nhiều node có thể nhận write. Phù hợp khi cần local write ở nhiều region, nhưng conflict resolution phức tạp.

## Checklist

- RPO chấp nhận được là bao nhiêu.
- Replication lag được đo và alert chưa.
- Failover chọn replica nào.
- Có nguy cơ split-brain không.
- Restore test có kiểm tra dữ liệu replicated không.
## Related Pages

- [Distributed Fault Tolerance And Recovery](./10-distributed-fault-tolerance-and-recovery.md)
- [Replication And Consistency Models](../03-patterns/09-replication-consistency-models.md)
