# RAID, LVM And Multipath

## Overview

RAID, LVM và multipath đều nằm giữa physical disk và filesystem/application, nhưng giải quyết các bài toán khác nhau:

- RAID gom nhiều disk thành một logical array để tăng redundancy, performance hoặc cả hai.
- LVM tạo lớp quản lý volume linh hoạt: physical volume, volume group, logical volume.
- Multipath cung cấp nhiều đường I/O đến cùng một LUN để tăng availability và failover ở SAN/iSCSI/Fibre Channel.

```text
disk / LUN paths
  -> RAID or multipath
  -> LVM / device mapper
  -> filesystem / database / application
```

## RAID Mental Model

RAID tạo một logical device từ nhiều disk. RAID có thể tăng performance bằng striping, tăng redundancy bằng mirroring/parity, nhưng không thay thế backup. Nếu ứng dụng ghi sai, xóa nhầm hoặc dữ liệu bị mã hóa bởi ransomware, lỗi đó vẫn có thể nằm trên toàn bộ array.

Các mức RAID thường gặp:

| Level | Cách hoạt động | Chịu lỗi | Phù hợp | Lưu ý |
|---|---|---:|---|---|
| Linear | Ghi đầy disk này rồi sang disk khác | Không | Gom dung lượng lab | Không tăng an toàn dữ liệu |
| RAID 0 | Striping qua nhiều disk | Không | Scratch/temp, workload cần tốc độ và có thể mất dữ liệu | Một disk hỏng là mất array |
| RAID 1 | Mirroring | Có | OS disk, workload cần đơn giản và an toàn | Dung lượng hiệu dụng thấp |
| RAID 5 | Striping + distributed parity | 1 disk | Dung lượng cân bằng với đọc nhiều | Rebuild lâu, rủi ro cao với disk lớn |
| RAID 6 | Striping + double parity | 2 disk | Dung lượng lớn, yêu cầu an toàn hơn RAID 5 | Write penalty cao hơn |
| RAID 10 | Mirror + stripe | Tùy cặp mirror | Database, VM, latency/IOPS tốt | Cần nhiều disk hơn |

## Hardware RAID vs Software RAID

Hardware RAID dùng controller chuyên dụng để quản lý array. OS thường chỉ thấy một logical disk, nên vận hành phụ thuộc vào tool/firmware của controller.

Software RAID trong Linux thường dùng `mdadm`, OS nhìn rõ các disk thành viên hơn và có thể giám sát bằng công cụ chuẩn Linux.

Trade-off:

- Hardware RAID có thể đơn giản với OS, nhưng controller là thành phần quan trọng cần theo dõi firmware, cache battery/supercap và khả năng thay thế.
- Software RAID minh bạch hơn với Linux, dễ quan sát bằng `mdadm`, nhưng vẫn cần hiểu boot, initramfs và quy trình rebuild.

## mdadm Operations

Lệnh quan sát an toàn:

```bash
cat /proc/mdstat
sudo mdadm --detail /dev/md0
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
```

Tạo array là thao tác có rủi ro phá dữ liệu. Chỉ chạy sau khi xác nhận đúng disk và có backup:

```bash
sudo mdadm --create --verbose /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc
```

Các thao tác như `--stop`, `--remove`, `--fail`, `--add` có thể làm mất redundancy hoặc ngừng dịch vụ nếu chạy sai device. Trong production, luôn ghi lại trạng thái trước/sau bằng `cat /proc/mdstat` và `mdadm --detail`.

## LVM Mental Model

LVM tách quản lý dung lượng thành ba lớp:

- PV (Physical Volume): disk/partition/block device được đưa vào LVM.
- VG (Volume Group): pool dung lượng gom từ nhiều PV.
- LV (Logical Volume): volume cấp cho filesystem/application.

LVM giúp resize, snapshot, di chuyển dữ liệu giữa PV và chia dung lượng linh hoạt hơn partition tĩnh. Tuy vậy, LVM không tự tạo redundancy nếu backend bên dưới không có RAID/replication.

Lệnh quan sát an toàn:

```bash
pvs
vgs
lvs -a -o +devices
lsblk
```

## Multipath I/O

Multipath xuất hiện khi một host có nhiều đường vật lý/logical đến cùng một storage LUN. Thay vì OS nhìn nhiều device trùng dữ liệu, multipath gom chúng thành một device ổn định qua device mapper.

Mục tiêu:

- Failover khi một path/controller/switch bị lỗi.
- Load balancing tùy policy và storage array.
- Giảm rủi ro mount nhầm từng path riêng lẻ.

Lệnh quan sát an toàn:

```bash
multipath -ll
lsblk
dmsetup ls
```

Nhầm lẫn thường gặp: multipath không nhân bản dữ liệu. Nó chỉ cung cấp nhiều đường đến cùng một LUN. Nếu backend storage mất dữ liệu, multipath không cứu được dữ liệu.

## DRBD

DRBD (Distributed Replicated Block Device) replication block device giữa nhiều node qua network. Nó thường dùng cho HA ở cấp block trong các thiết kế nhỏ hoặc legacy.

Điểm cần hiểu:

- Primary/Secondary là vai trò ghi/đọc tùy cấu hình.
- Split brain xảy ra khi nhiều node cùng tin mình là primary hoặc có lịch sử ghi không thể hòa giải tự động.
- Dual Primary chỉ an toàn khi filesystem/cluster stack phía trên hỗ trợ truy cập đồng thời đúng cách, ví dụ clustered filesystem và fencing.

DRBD liên quan trực tiếp đến rủi ro consistency, nên mọi thao tác repair/failover cần có fencing, backup và xác nhận nguồn dữ liệu đúng.

## Best Practices

- Không coi RAID/replication là backup.
- Theo dõi rebuild/resync vì quá trình này tăng I/O và giảm redundancy tạm thời.
- Dùng ổ cùng class/capacity khi thiết kế RAID để tránh bottleneck và lãng phí.
- Với production, ưu tiên read-only checks trước khi thay disk, fail disk hoặc assemble array.
- Ghi lại mapping disk serial, slot, `/dev` name và array member để tránh thay nhầm ổ.

## Trang Liên Quan

- [Disk And Device Fundamentals](./02-disk-and-device-fundamentals.md)
- [Backup, Snapshot And Replication](./07-backup-snapshot-replication.md)
- [Storage Performance: IOPS, Throughput, Latency](./08-storage-performance-iops-throughput-latency.md)
