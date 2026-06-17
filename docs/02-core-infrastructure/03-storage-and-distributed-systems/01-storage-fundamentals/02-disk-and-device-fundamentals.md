# Disk And Device Fundamentals

## Overview

Disk và device fundamentals giải thích đường đi từ yêu cầu I/O của ứng dụng đến thiết bị lưu trữ vật lý. Đây là lớp nền trước khi học filesystem, RAID, multipath, SAN, Ceph hoặc performance troubleshooting.

```text
application
  -> syscall / database engine
  -> filesystem or raw block layer
  -> block device / device mapper
  -> driver
  -> controller / bus
  -> disk media
```

## Thành Phần Chính

- Disk: thiết bị lưu trữ vật lý hoặc virtual disk. HDD có cơ học quay, SSD/NVMe dùng flash.
- Controller: bộ điều khiển giao tiếp với disk, có thể là SATA controller, SAS HBA, RAID controller hoặc NVMe controller.
- Driver: phần kernel giúp OS nói chuyện với controller/device.
- Block device: abstraction trong OS như `/dev/sda`, `/dev/nvme0n1`, `/dev/dm-0`.
- Filesystem hoặc database: tầng hiểu cấu trúc dữ liệu cao hơn, ánh xạ file/page/record xuống block.

## Disk Interface

| Interface | Cách hiểu nhanh | Ghi chú vận hành |
|---|---|---|
| SATA | Phổ biến cho HDD/SSD consumer hoặc server entry-level | Dễ dùng, chi phí thấp, không phải lựa chọn tốt nhất cho workload enterprise latency thấp |
| SAS | Phổ biến trong server/storage array | Hỗ trợ enterprise disk, dual-port, enclosure/backplane tốt hơn SATA |
| NVMe | Giao thức cho SSD qua PCIe | Latency thấp, queue depth lớn, phù hợp workload IOPS cao |
| M.2 | Form factor, không phải giao thức | M.2 có thể chạy SATA hoặc NVMe tùy thiết bị/mainboard |
| SCSI | Command model lâu đời cho enterprise storage | Nhiều giao thức như SAS, iSCSI dùng SCSI command set |
| PATA | Chuẩn cũ | Chủ yếu gặp trong hệ thống legacy |

Nhầm lẫn thường gặp: M.2 là hình dạng khe/thiết bị; NVMe là giao thức. Một ổ M.2 không mặc định đồng nghĩa với NVMe.

## Controller, Bus Và Memory-Mapped I/O

Controller thường có các thanh ghi điều khiển/trạng thái/data để CPU hoặc driver thao tác. OS có thể giao tiếp với controller qua port I/O hoặc memory-mapped I/O, trong đó register của thiết bị được ánh xạ vào không gian địa chỉ để CPU đọc/ghi như memory.

Ba cơ chế tương tác host-controller quan trọng:

- Polling: CPU liên tục kiểm tra trạng thái thiết bị. Đơn giản nhưng lãng phí CPU.
- Interrupt: thiết bị báo cho CPU khi có sự kiện hoặc I/O hoàn tất. Hiệu quả hơn polling.
- DMA (Direct Memory Access): controller truyền dữ liệu trực tiếp giữa device và memory, giảm tải CPU cho I/O lớn.

## Buffer Và Cache

- Buffer là vùng nhớ tạm để điều hòa khác biệt tốc độ/kích thước truyền giữa các thành phần.
- Cache giữ bản sao dữ liệu thường truy cập để giảm latency.
- Cache có thể nằm ở controller, OS page cache, filesystem, database hoặc ứng dụng.

Write-back cache cải thiện latency ghi vì acknowledge trước khi dữ liệu thật sự xuống media, nhưng cần cơ chế bảo vệ như battery/supercap, journal hoặc WAL. Write-through an toàn hơn nhưng thường chậm hơn.

## Thiết Bị Vật Lý vs Abstraction Của OS

Trong vận hành, cần phân biệt:

- Physical disk: ổ thật, có serial, firmware, SMART, wear indicator.
- Virtual disk: disk do hypervisor/cloud cung cấp.
- Device mapper: abstraction như LUKS, LVM, multipath, dm-cache.
- Partition: vùng chia trên disk.
- Filesystem: cấu trúc dữ liệu đặt trên partition/block device.
- Mount point: nơi filesystem được gắn vào cây thư mục.

Debug storage đúng lớp giúp tránh kết luận sai. Ví dụ ứng dụng báo I/O chậm có thể do disk media, controller queue, multipath path failover, filesystem journal, network storage hoặc database flush.

## Lệnh Quan Sát An Toàn

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,ROTA,TRAN,MODEL
findmnt
df -hT
cat /proc/partitions
dmesg -T | grep -iE 'error|nvme|scsi|ata|blk|reset'
```

Với disk vật lý, chỉ đọc SMART trước khi can thiệp:

```bash
sudo smartctl -a /dev/sdX
sudo smartctl -a /dev/nvme0n1
```

## Rủi Ro

Các lệnh như `mkfs`, `wipefs`, `parted`, `fdisk`, `dd`, `pvcreate`, `mdadm --create` có thể phá dữ liệu. Trước khi chạy trong production, cần xác nhận đúng device, có backup, có rollback và kiểm tra lại bằng lệnh read-only như `lsblk`.

## Trang Liên Quan

- [Storage Models: Block, File, Object](./01-storage-models-block-file-object.md)
- [RAID, LVM And Multipath](./03-raid-lvm-multipath.md)
- [Filesystem Basics](./04-filesystem-basics.md)
- [Storage Performance: IOPS, Throughput, Latency](./08-storage-performance-iops-throughput-latency.md)
