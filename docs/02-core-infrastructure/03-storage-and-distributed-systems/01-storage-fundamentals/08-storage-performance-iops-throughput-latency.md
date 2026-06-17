# Storage Performance: IOPS, Throughput, Latency

## Overview

Storage performance là kết quả của toàn bộ đường đi I/O, không chỉ loại disk. NVMe nhanh vẫn có thể chậm nếu queue, filesystem, replication, network hoặc application flush bị nghẽn.

```text
application pattern
  -> syscall / database engine
  -> filesystem / block layer
  -> queue / scheduler
  -> network or controller
  -> media
  -> replication / durability acknowledgement
```

## Ba Chỉ Số Nền Tảng

- IOPS: số thao tác I/O mỗi giây. Quan trọng với random small I/O như database page, VM boot storm.
- Throughput: lượng dữ liệu mỗi giây, thường MB/s hoặc GB/s. Quan trọng với backup, streaming, scan tuần tự.
- Latency: thời gian hoàn thành một I/O. Quan trọng với transaction, VM, filesystem metadata và request đồng bộ.

Ba chỉ số này liên hệ với nhau qua kích thước I/O và queue depth. IOPS cao không luôn có nghĩa latency tốt nếu queue bị chất đầy.

## Workload Pattern

| Pattern | Đặc điểm | Bottleneck hay gặp |
|---|---|---|
| Random read/write nhỏ | Nhiều request nhỏ, không tuần tự | IOPS, latency, queue depth |
| Sequential read/write lớn | Đọc/ghi theo luồng | throughput, bandwidth |
| Metadata-heavy | create/delete/stat nhiều file | filesystem metadata, directory, lock |
| Sync write | Chờ fsync/commit | WAL/journal latency, flush latency |
| Mixed VM workload | Nhiều pattern từ nhiều guest | noisy neighbor, cache miss, queue contention |

## Latency Hierarchy

Thứ tự tương đối thường gặp:

```text
RAM < NVMe SSD < SATA/SAS SSD < HDD < tape/archive
```

Trong distributed storage, latency còn cộng thêm network, placement, replication/erasure coding và quorum/ack policy.

## Cache Và Write Policy

Cache có thể làm benchmark đẹp hơn thực tế nếu test chỉ đọc dữ liệu vừa được ghi hoặc working set nhỏ hơn RAM. Khi đo storage, cần phân biệt:

- cold read vs warm cache read
- buffered I/O vs direct I/O
- write-back acknowledge vs durable fsync
- throughput tuần tự vs random IOPS

Write-back cache có thể giảm latency ghi, nhưng durability phụ thuộc vào flush, power-loss protection, WAL/journal và backend.

## Tiering Và Workload Placement

Storage tier nên xuất phát từ access pattern, không chỉ từ tên thiết bị:

- Performance tier: NVMe/SSD cho latency thấp, random I/O, database, VM disk.
- Balanced tier: SSD/HDD hybrid cho workload cần throughput ổn định với chi phí vừa phải.
- Capacity tier: HDD/object storage cho backup, archive, data lake, log cũ.

Trong private cloud, cùng một platform có thể cần nhiều tier: block volume cho VM, file share cho shared workload, object storage cho backup/archive.

## Distributed Storage Factors

Hiệu năng distributed storage phụ thuộc thêm vào:

- network latency/bandwidth/packet loss
- replication factor hoặc erasure coding
- placement/failure domain
- rebalance/backfill/recovery đang chạy
- metadata path vs data path
- client concurrency và object/file size distribution

Ví dụ: recovery/backfill tăng durability sau lỗi disk, nhưng cũng có thể làm latency người dùng tăng. Runbook cần phân biệt mitigation tạm thời với permanent fix.

## Lệnh Quan Sát An Toàn

```bash
iostat -xz 1 5
vmstat 1 5
pidstat -durh 1 5
lsblk -o NAME,SIZE,TYPE,ROTA,TRAN,MODEL
df -hT
```

Với filesystem/directory lớn:

```bash
findmnt
sudo du -xhd1 /var 2>/dev/null | sort -h
```

## Troubleshooting Checklist

- Xác định workload: random hay sequential, read hay write, sync hay async.
- Kiểm tra latency ở host trước khi kết luận backend storage lỗi.
- Xem queue depth, `%util`, await, service time và saturation.
- Kiểm tra network nếu storage đi qua NFS/iSCSI/Ceph/S3.
- Kiểm tra có backup, scrub, compaction, rebalance, antivirus hoặc batch job đang chạy không.
- So sánh `df` và `du` nếu nghi deleted-but-open files.

## Best Practices

- Benchmark bằng pattern gần production, không chỉ dùng throughput tuần tự.
- Theo dõi percentile latency, không chỉ average.
- Tách pool/tier theo workload có blast radius khác nhau.
- Đừng dùng một storage tier duy nhất cho mọi workload nếu yêu cầu latency/cost/durability khác nhau.
- Luôn gắn performance với reliability: tắt sync/journal/WAL để nhanh hơn có thể phá recovery guarantee.

## Trang Liên Quan

- [Disk And Device Fundamentals](./02-disk-and-device-fundamentals.md)
- [Cache, Buffer, WAL And Journal](./05-cache-buffer-wal-journal.md)
- [Backup, Snapshot And Replication](./07-backup-snapshot-replication.md)
