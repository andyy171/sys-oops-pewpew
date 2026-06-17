# LVM, RAID, Backup và Restore

## 1. LVM Concept: PV, VG, LV, PE

LVM cho phép quản lý storage linh hoạt hơn partition truyền thống.

LVM nằm trên device mapper: kernel expose logical block device dưới `/dev/mapper/*` hoặc symlink thân thiện như `/dev/vg_data/lv_app`. Vì vậy khi debug, cần tách rõ physical disk/LUN, partition, PV, VG, LV, filesystem và mount point.

| Thành phần | Ý nghĩa |
| --- | --- |
| PV | Physical Volume, thường là disk/partition như `/dev/sdb1` |
| VG | Volume Group, pool gom nhiều PV |
| LV | Logical Volume, volume cấp cho filesystem |
| PE | Physical Extent, block cấp phát nội bộ của VG |

Kiểm tra:

```bash
pvs
vgs
lvs
lvs -a -o +devices
lsblk
```

## 2. Create, Extend, Reduce, Remove LV

Tạo LVM:

```bash
sudo pvcreate /dev/sdb1
sudo vgcreate vg_data /dev/sdb1
sudo lvcreate -L 100G -n lv_app vg_data
sudo mkfs.xfs /dev/vg_data/lv_app
sudo mkdir -p /data/app
sudo mount /dev/vg_data/lv_app /data/app
```

Extend LV kèm filesystem:

```bash
sudo lvextend -r -L +50G /dev/vg_data/lv_app
```

Hoặc dùng toàn bộ free space trong VG:

```bash
sudo lvextend -r -l +100%FREE /dev/vg_data/lv_app
```

Giảm LV rủi ro cao, chỉ làm khi đã backup và hiểu filesystem hỗ trợ. `lvreduce` có thể làm mất dữ liệu ngay lập tức nếu kích thước mới nhỏ hơn filesystem hoặc sai device.

```bash
# Ví dụ ext4, cần unmount
sudo umount /data/app
sudo e2fsck -f /dev/vg_data/lv_app
sudo resize2fs /dev/vg_data/lv_app 80G
sudo lvreduce -L 80G /dev/vg_data/lv_app
sudo mount /data/app
```

Xóa LV:

```bash
sudo umount /data/app
sudo lvremove /dev/vg_data/lv_app
```

## 3. LVM Snapshot Concept

Snapshot ghi lại trạng thái LV tại một thời điểm, hữu ích để backup nhất quán trong thời gian ngắn.

```bash
sudo lvcreate -s -L 10G -n lv_app_snap /dev/vg_data/lv_app
sudo mkdir -p /mnt/lv_app_snap
sudo mount /dev/vg_data/lv_app_snap /mnt/lv_app_snap
```

Sau khi backup:

```bash
sudo umount /mnt/lv_app_snap
sudo lvremove /dev/vg_data/lv_app_snap
```

Notes:

- Snapshot không thay thế backup độc lập.
- Snapshot đầy có thể bị invalid.
- Với database, nên flush/lock hoặc dùng backup tool native.

## 4. RAID/mdadm Overview

RAID tăng availability hoặc performance tùy level, nhưng không phải backup.

| Level | Đặc điểm |
| --- | --- |
| RAID 0 | Striping, tăng performance, mất một disk là mất dữ liệu |
| RAID 1 | Mirroring, chịu lỗi một disk |
| RAID 5 | Parity, chịu lỗi một disk, write penalty |
| RAID 6 | Double parity, chịu lỗi hai disk |
| RAID 10 | Mirror + stripe, performance và availability tốt |

Ví dụ tạo RAID1 bằng `mdadm`:

```bash
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc
cat /proc/mdstat
sudo mdadm --detail /dev/md0
sudo mkfs.xfs /dev/md0
```

Kiểm tra array đang chạy:

```bash
cat /proc/mdstat
sudo mdadm --detail /dev/md0
```

Persist config:

```bash
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf
sudo update-initramfs -u
```

Trên RHEL-family, đường dẫn và lệnh rebuild initramfs có thể khác, ví dụ `dracut`.

`mdadm --create`, `pvcreate`, `vgremove`, `lvremove` và thao tác reinitialize RAID/LVM đều có thể phá dữ liệu nếu chọn sai device. Trước khi chạy, kiểm tra read-only bằng `lsblk -f`, serial/WWID, mountpoint, `/proc/mdstat`, `pvs`, `vgs`, `lvs` và backup/snapshot. RAID giúp chịu lỗi thiết bị tùy level nhưng không bảo vệ khỏi xóa nhầm, corruption, ransomware hoặc lỗi application.

## 4.1 Multipath Overview

Device Mapper Multipathing dùng khi server có nhiều path tới cùng một SAN/iSCSI/FC LUN. App và filesystem không nên mount trực tiếp từng path riêng lẻ như `/dev/sdX`; nên dùng logical multipath device.

```text
server HBA/NIC path A -> storage LUN
server HBA/NIC path B -> storage LUN
             -> /dev/mapper/mpathN
             -> partition/LVM/filesystem
```

Lệnh quan sát an toàn:

```bash
multipath -ll
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL
systemctl status multipathd
kpartx -l /dev/mapper/mpathN
```

Production notes:

- Xác nhận nhiều path trỏ tới cùng WWID trước khi tạo filesystem hoặc LVM.
- Không format từng path thành nhiều filesystem riêng nếu chúng thực chất là cùng một LUN.
- Khi path mất, kiểm tra storage fabric, zoning, iSCSI session, multipath policy và `multipathd` trước khi thao tác dữ liệu.
- Nếu multipath device có partition table, `kpartx` có thể tạo mapping partition dưới `/dev/mapper/`; cần xác nhận đúng mapping trước khi mount, fsck hoặc tạo PV.

## 4.2 Backup Strategy Dimensions

Backup không chỉ là chọn một command. Trước khi viết job backup, cần xác định dữ liệu nào đáng bảo vệ, thay đổi nhanh tới đâu, restore cần nhanh mức nào và ai chịu trách nhiệm kiểm chứng.

Các câu hỏi tối thiểu:

- **Scope**: file cấu hình, application data, database, package list, systemd unit custom, secrets hay toàn bộ disk image?
- **RPO**: có thể mất tối đa bao nhiêu dữ liệu, ví dụ vài phút, vài giờ hay một ngày?
- **RTO**: service cần khôi phục trong bao lâu và có staging environment để test restore không?
- **Consistency**: workload có cần quiesce, snapshot, dump native hoặc lock để tránh backup ở trạng thái nửa ghi không?
- **Location**: backup có nằm độc lập khỏi host gốc, volume gốc và quyền xóa của cùng một account không?
- **Verification**: backup được kiểm checksum, đọc thử, restore thử và ghi lại kết quả ở đâu?
- **Retention**: giữ bao lâu, có legal/compliance hold không, và ai được phép xóa backup?

Với hệ thống nhỏ, `rsync`, `tar` hoặc snapshot có thể đủ nếu có lịch chạy, retention, checksum và restore test. Với production quan trọng, ưu tiên thiết kế backup theo RPO/RTO, mã hóa, immutable/offsite copy, monitoring job failure và runbook restore rõ ràng. Backup chưa từng restore thử chỉ nên xem là hy vọng, chưa phải control vận hành đáng tin.

## 5. Backup With `rsync` và `tar`

`rsync` phù hợp sync file/directory:

```bash
rsync -aHAX --numeric-ids --dry-run /source/ /backup/source/
rsync -aHAX --numeric-ids --info=progress2 /source/ /backup/source/
rsync -aHAX --delete /source/ backup-host:/backup/source/
```

`tar` phù hợp đóng gói:

```bash
sudo tar --xattrs --acls -czf /backup/etc-$(date +%F).tar.gz /etc
sudo tar -tzf /backup/etc-2026-05-20.tar.gz | head
```

`cpio` hữu ích khi muốn archive từ danh sách file do command khác sinh ra, ví dụ `find`. Ưu tiên path tương đối hoặc restore vào thư mục staging để tránh ghi đè bất ngờ:

```bash
cd /etc
find . -xdev -type f -print0 | cpio --null -ov -H newc > /backup/etc-files.cpio
cpio -itv < /backup/etc-files.cpio
mkdir -p /tmp/restore-cpio
cd /tmp/restore-cpio
cpio -idv --no-absolute-filenames < /backup/etc-files.cpio
```

`dd` tạo bản sao block-level và có blast radius rất cao vì `if=` và `of=` đảo ngược là có thể ghi đè dữ liệu nguồn. Không có dry-run thật sự cho `dd`; trước khi chạy phải xác nhận device bằng `lsblk -f`, `findmnt`, serial/WWID, trạng thái mount và backup/maintenance window.

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,SERIAL
findmnt
sudo dd if=/dev/sdX of=/backup/disk-sdX.img bs=64M status=progress conv=fsync
sha256sum /backup/disk-sdX.img
```

Không dùng `dd` để wipe disk trong runbook chung nếu chưa có ticket, xác nhận đúng thiết bị, phương án rollback và chính sách xử lý media. Với disk loại bỏ khỏi production, ưu tiên quy trình sanitization của tổ chức/vendor hoặc hủy vật lý khi dữ liệu nhạy cảm.

Nên backup:

- `/etc`
- app config
- app data
- database bằng tool native
- danh sách package
- systemd unit custom
- cron/systemd timer custom

## 6. Restore Checklist

Trước khi restore:

1. Xác định restore point.
2. Kiểm tra checksum hoặc khả năng đọc backup.
3. Chạy restore test trên staging/lab nếu dữ liệu quan trọng.
4. Dừng service ghi dữ liệu nếu cần.
5. Backup trạng thái hiện tại trước khi ghi đè.
6. Restore vào staging path nếu có thể.
7. Kiểm tra ownership, permission, SELinux context.
8. Start service và verify log.

Ví dụ restore `/etc` vào thư mục tạm để inspect:

```bash
mkdir -p /tmp/restore-etc
tar -xzf /backup/etc-2026-05-20.tar.gz -C /tmp/restore-etc
diff -ruN /etc /tmp/restore-etc/etc | less
```

Restore bằng `rsync`:

```bash
sudo rsync -aHAX --numeric-ids /backup/source/ /source/
sudo restorecon -RFv /source 2>/dev/null || true
```

## 7. Disk Full và Capacity Troubleshooting

```bash
df -h
df -ih
lsblk
pvs; vgs; lvs
du -xh / --max-depth=1 2>/dev/null | sort -h
lsof +L1
```

Nguyên nhân thường gặp:

- Log tăng nhanh.
- File deleted nhưng process còn giữ fd.
- Snapshot đầy.
- Inode hết.
- Backup ghi nhầm vào root filesystem vì mount backup chưa lên.

Production notes:

- Không xóa file lạ dưới `/var/lib` nếu chưa biết service owner.
- Với database, dùng purge/retention native thay vì xóa file thủ công.
- Trước khi extend disk/LV, kiểm tra storage backend và backup.
