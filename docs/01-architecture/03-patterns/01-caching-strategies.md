# Caching Strategies

Caching giảm latency và tải backend bằng cách lưu dữ liệu gần nơi đọc. Nhưng cache luôn tạo tradeoff về freshness, invalidation và consistency.

## Cache-Aside

Ứng dụng tự đọc cache trước. Nếu miss, ứng dụng đọc database rồi ghi lại vào cache.

Phù hợp cho read-heavy workload và dữ liệu có thể tái tạo từ source of truth.

Rủi ro:

- Cache stampede khi nhiều request miss cùng lúc.
- Dữ liệu stale nếu invalidation không tốt.
- Logic cache nằm trong app.

## Read-Through

Ứng dụng đọc qua cache layer; cache tự load dữ liệu từ backend khi miss.

Ưu điểm là app đơn giản hơn. Nhược điểm là cache layer phải hiểu backend loading logic.

## Write-Through

Ghi vào cache và backend trong cùng flow. Dữ liệu cache mới hơn, nhưng write latency cao hơn.

## Write-Behind

Ghi vào cache/queue trước, backend được cập nhật bất đồng bộ.

Ưu điểm là write nhanh và throughput cao. Rủi ro là mất dữ liệu nếu buffer/cache lỗi trước khi flush.

## Write-Around

Ghi trực tiếp vào backend, không cập nhật cache ngay. Cache chỉ được fill khi có read.

## Cache Invalidation

Các cách phổ biến:

- TTL.
- Explicit delete/update khi write.
- Versioned key.
- Event-driven invalidation.
- Read repair khi phát hiện stale data.

Cache là một replica có consistency contract yếu hơn source of truth. Khi cache giữ dữ liệu mutable, cần chọn cơ chế coherence rõ:

| Cơ chế | Dùng khi | Rủi ro |
|---|---|---|
| TTL/pull | Chấp nhận stale trong một khoảng thời gian | TTL quá dài gây stale, TTL quá ngắn gây tải backend |
| Explicit invalidation | Write ít, cần xóa cache nhanh | Invalidation miss làm cache giữ dữ liệu cũ |
| Push update | Object nhỏ, cần cache luôn mới hơn | Write amplification và update out-of-order |
| Lease | Cache được giữ object trong thời gian có kiểm soát | Lease expiry/clock/timeout sai gây stale hoặc miss storm |

Với production, đo stale read, invalidation failure, miss storm, backend fallback rate và hot key. Không dùng cache để che giấu database query chậm nếu cache miss có thể làm backend sập.

## Failure Modes

- Cache stampede.
- Hot key.
- Stale read.
- Cache penetration với key không tồn tại.
- Cache outage làm backend quá tải.

## Nguyên Tắc

- Xác định source of truth trước khi thêm cache.
- Không cache dữ liệu nhạy cảm nếu chưa rõ TTL, encryption và access control.
- Với production, cần metric hit ratio, eviction, memory usage, latency và backend fallback rate.


## Related Pages

- [Replication And Consistency Models](./09-replication-consistency-models.md)
