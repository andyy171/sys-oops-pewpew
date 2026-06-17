# Cache, Buffer, WAL And Journal

## Overview

Cache, buffer, WAL và journal đều cải thiện performance hoặc recovery, nhưng không giống nhau:

- Buffer điều hòa tốc độ/kích thước truyền dữ liệu giữa các lớp.
- Cache giữ bản sao nhanh của dữ liệu hoặc metadata để giảm latency.
- WAL (Write-Ahead Log) ghi ý định thay đổi trước khi ghi dữ liệu chính.
- Journal trong filesystem là một dạng log transaction, thường tập trung vào metadata hoặc cả metadata/data tùy mode.

```text
write request
  -> cache / buffer
  -> WAL or journal commit
  -> data structure update
  -> flush to durable media
```

## Buffer vs Cache

Buffer là vùng nhớ tạm để dữ liệu đi qua khi hai thành phần có tốc độ hoặc kích thước truyền khác nhau. Ví dụ kernel buffer cho block I/O.

Cache là bản sao dữ liệu nhằm tăng tốc truy cập lần sau. Cache có thể nằm ở:

- disk/controller cache
- OS page cache
- filesystem metadata cache
- database buffer pool
- application cache

Nhầm lẫn quan trọng: dữ liệu "đã ghi vào cache" chưa chắc đã durable trên disk. Với write-back cache, hệ thống cần flush hoặc barrier để đảm bảo dữ liệu thật sự xuống thiết bị.

## Page Cache Và Buffer Cache

Linux hiện đại dùng page cache làm trung tâm cho file data. Buffer cache vẫn liên quan đến block metadata hoặc mapping block-level, nhưng dữ liệu file thường được cache theo page để tránh double caching.

Double caching xảy ra khi cùng dữ liệu bị cache ở nhiều lớp, ví dụ filesystem page cache và database buffer pool. Database thường dùng direct I/O hoặc tuning riêng để kiểm soát hiện tượng này tùy engine.

## Synchronous vs Asynchronous Writes

| Kiểu ghi | Cách hoạt động | Ưu điểm | Rủi ro |
|---|---|---|---|
| Synchronous write | Chờ ghi xuống durable media hoặc ít nhất qua durability boundary | An toàn hơn cho metadata/transaction quan trọng | Latency cao |
| Asynchronous write | Ghi vào cache/buffer trước, flush sau | Throughput tốt hơn | Crash trước khi flush có thể mất dữ liệu |
| Write-through cache | Acknowledge sau khi ghi xuống backend | Dễ reasoning về durability | Chậm hơn |
| Write-back cache | Acknowledge khi vào cache rồi flush sau | Nhanh | Cần bảo vệ cache và cơ chế recovery |

## WAL

WAL yêu cầu ghi log trước khi thay đổi data chính. Ý tưởng cốt lõi: nếu crash xảy ra giữa chừng, hệ thống có thể đọc log để biết transaction nào đã commit, transaction nào cần redo/undo.

WAL thường xuất hiện trong:

- database như PostgreSQL WAL, MySQL redo log/binlog theo mục đích khác nhau
- storage engine
- filesystem journal
- distributed system cần replay state

Nguyên tắc vận hành:

- WAL phải nằm trên storage đủ bền và latency phù hợp.
- WAL đầy hoặc I/O chậm có thể làm toàn hệ thống chậm.
- Backup/PITR cần cả base backup và chuỗi WAL/log liên tục.

## Filesystem Journal

Filesystem journal ghi transaction metadata trước khi cập nhật cấu trúc chính. Sau crash:

- Transaction đã commit nhưng chưa apply xong có thể được redo.
- Transaction chưa commit có thể bị bỏ qua hoặc rollback tùy implementation.

Journal giúp giảm thời gian recovery so với scan toàn bộ metadata bằng `fsck`, nhưng không phải bản backup và không đảm bảo application-level consistency nếu ứng dụng không flush/fsync đúng cách.

## Cache Trong Storage Performance

Cache cải thiện performance khi workload có locality:

- read cache hiệu quả khi dữ liệu được đọc lặp lại.
- write-back cache gom nhiều write nhỏ thành batch.
- metadata cache giảm cost của lookup/path traversal.

Cache kém hiệu quả hoặc gây hiểu lầm khi workload quét tuần tự dữ liệu lớn, working set lớn hơn RAM, hoặc benchmark chỉ đo cache hit thay vì media thực.

## Safe Checks

```bash
free -h
vmstat 1 5
iostat -xz 1 5
cat /proc/meminfo | grep -E 'Cached|Buffers|Dirty|Writeback'
```

Với filesystem mount option:

```bash
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
```

## Best Practices

- Tách performance cache khỏi durability guarantee khi thiết kế.
- Không tắt journal/WAL chỉ để tăng benchmark nếu workload cần recovery.
- Với production database/storage, kiểm tra latency của flush/fsync, không chỉ throughput.
- Với write-back cache phần cứng, theo dõi battery/supercap/cache protection.
- Trước khi repair filesystem hoặc database sau crash, giữ evidence/log và tạo snapshot/backup nếu có thể.

## Trang Liên Quan

- [Filesystem Basics](./04-filesystem-basics.md)
- [Data Integrity, Checksum And Hashing](./06-data-integrity-checksum-hashing.md)
- [Storage Performance: IOPS, Throughput, Latency](./08-storage-performance-iops-throughput-latency.md)
