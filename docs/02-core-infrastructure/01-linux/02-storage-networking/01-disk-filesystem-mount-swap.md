# Disk, Filesystem, Mount và Swap

## 1. Disk và Partition Overview

Linux nhìn disk như block device trong `/dev`, ví dụ:

- `/dev/sda`, `/dev/sdb`: SATA/SCSI/virtio disk.
- `/dev/nvme0n1`: NVMe disk.
- `/dev/mmcblk0`: eMMC/SD card hoặc một số removable media.
- `/dev/sda1`, `/dev/nvme0n1p1`: partition.
- `/dev/mmcblk0p1`: partition trên thiết bị kiểu `mmcblk`.

Trên disk MBR legacy, primary partition thường được đánh số 1-4; logical partition trong extended partition thường bắt đầu từ 5. Với GPT, không cần extended partition và số partition chỉ là định danh logic. Trên NVMe/eMMC, ký tự `p` được thêm vào trước số partition để tránh nhầm tên disk với số partition, ví dụ `/dev/nvme0n1p1`.

Các lệnh kiểm tra:

```bash
lsblk
lsblk -f
blkid
fdisk -l
parted -l
df -h
df -ih
findmnt
cat /proc/partitions
```

Luồng mental model khi thêm storage mới:

```text
physical/virtual disk
-> kernel block device trong /dev
-> partition
-> filesystem hoặc swap
-> mount point
-> application/user I/O
```

Trong production, phải phân biệt rõ disk như `/dev/sdb`, partition như `/dev/sdb1`, LVM LV như `/dev/vg_data/lv_app`, filesystem và mount point. Nhầm một lớp là lỗi phổ biến nhất dẫn tới `mkfs`, `fsck` hoặc `mount` sai device.

Partition chỉ là cách chia logic trên cùng block device. Hai partition nằm trên cùng một disk không tạo fault tolerance; nếu disk vật lý hoặc volume backend hỏng thì cả hai partition đều có thể mất. Nếu cần redundancy, dùng RAID, replication, snapshot/backup độc lập hoặc cơ chế HA của storage backend.

## 1.1 Thiết Kế Layout Filesystem

Khi thiết kế layout cho server, câu hỏi chính không phải là "chia được bao nhiêu partition", mà là thư mục nào có vòng đời, rủi ro đầy disk, yêu cầu backup/restore và profile IO khác nhau.

| Mount point | Khi nên tách riêng | Lý do vận hành |
| --- | --- | --- |
| `/boot` | Host có encryption/compression/root filesystem mà bootloader khó đọc, hoặc cần vùng boot tách khỏi root | Giữ kernel, initramfs và GRUB file ở vùng đơn giản, dễ rescue |
| `/boot/efi` | Host boot UEFI | ESP thường là FAT và được firmware đọc trực tiếp |
| `/home` | Multi-user, workstation, jump host, server có dữ liệu user đáng giữ khi reinstall | Tách dữ liệu user khỏi OS lifecycle |
| `/var` | Server ghi log/cache/spool/database/web data nhiều | Tránh log/cache hoặc application data làm đầy root filesystem |
| `/var/log` | Host yêu cầu retention/evidence rõ hoặc log volume lớn | Giảm rủi ro log flood làm đầy `/var` hoặc `/` |
| `/srv`, `/data`, `/opt/<app>` | Application data có backup/restore/IO policy riêng | Tách workload data khỏi OS package/config |
| swap | Host cần swap partition/file hoặc hibernate | Swap sizing phụ thuộc workload; hibernate thường cần đủ cho RAM image |

Không tách partition chỉ vì checklist. Tách quá nhiều mà không có monitoring và resize workflow sẽ tạo outage kiểu "partition A đầy trong khi partition B còn trống". Với cloud VM hoặc LVM-backed server, ưu tiên layout có thể mở rộng được, dùng `UUID`/`LABEL`, và ghi rõ ownership của từng mount trong runbook.

Pre-check trước khi thay layout production:

```bash
lsblk -f
findmnt
df -hT
df -ih
swapon --show
cat /etc/fstab
```

Guardrails:

- Backup `/etc/fstab` và dữ liệu trước khi thay mount.
- Không format/mkfs partition đang chứa dữ liệu nếu chưa xác minh serial/WWN/size/mountpoint.
- Với `/boot` và ESP, giữ ít nhất một kernel/initramfs/GRUB entry boot được để rollback.
- Với `/var`, kiểm tra logrotate/journald retention và workload ghi dữ liệu như database, queue, web upload.
- Với swap, không dùng quy tắc "gấp đôi RAM" một cách máy móc; sizing phải dựa vào memory pressure, hibernate requirement và policy của workload/vendor.

## 2. MBR và GPT

| Kiểu partition table | Ghi chú |
| --- | --- |
| MBR | Legacy, giới hạn 2 TiB, tối đa 4 primary partition |
| GPT | Hiện đại, hỗ trợ disk lớn, dùng phổ biến với UEFI |

Kiểm tra partition table:

```bash
sudo parted /dev/sdb print
sudo fdisk -l /dev/sdb
```

## 3. Tạo Partition

Ví dụ dùng `parted` tạo GPT và một partition:

```bash
sudo parted /dev/sdb
mklabel gpt
mkpart primary ext4 1MiB 100%
quit
```

Reload partition table:

```bash
sudo partprobe /dev/sdb
lsblk /dev/sdb
```

Production notes:

- Xác nhận đúng disk bằng `lsblk`, serial, size, mountpoint.
- Không thao tác trên disk đang chứa dữ liệu nếu chưa backup.
- Với VM/cloud volume mới attach, nên ghi rõ mapping device trước khi format.

## 4. Filesystem

Kernel không cần mỗi application tự hiểu từng loại filesystem. Linux dùng **Virtual File System - VFS** làm lớp interface chung: application gọi `open`, `read`, `write`, `stat`; kernel chuyển thao tác đó tới driver/filesystem backend phù hợp như ext4, XFS, btrfs, NFS, SMB hoặc pseudo filesystem.

Filesystem thường gặp:

| Filesystem | Use case |
| --- | --- |
| `ext2` | Legacy extended filesystem, không journaling |
| `ext3` | Legacy ext filesystem có journaling |
| `ext4` | Phổ biến, ổn định, dễ vận hành |
| `xfs` | Phổ biến trên RHEL, tốt cho filesystem lớn |
| `btrfs` | Snapshot/subvolume, dùng tùy distro/use case |
| `nfs` | Network filesystem cho Linux/Unix share |
| `smb` | SMB/CIFS share, thường dùng khi tích hợp Windows/Samba |
| `ntfs` | Filesystem Windows NT, thường gặp khi mount disk từ Windows |
| `vfat` | EFI System Partition |
| `exfat` | Removable media hiện đại như USB/SD card |
| `iso9660` | CD/DVD image |
| `proc`, `sysfs` | Pseudo filesystem expose kernel/process/device runtime state |

Điểm cần nhớ: `proc` và `sysfs` là runtime view do kernel tạo, không phải dữ liệu persistent trên disk. Không xử lý chúng như filesystem lưu file thông thường.

Phân biệt nhanh:

| Khái niệm | Ý nghĩa |
| --- | --- |
| Block device | Thiết bị hoặc logical device để đọc/ghi block, ví dụ `/dev/sdb` |
| Partition | Vùng chia trên block device, ví dụ `/dev/sdb1` |
| Filesystem | Cấu trúc dữ liệu được format trên partition/LV để lưu file |
| Mount point | Thư mục nơi filesystem được gắn vào cây `/` |

Tạo filesystem:

```bash
sudo mkfs.ext4 /dev/sdb1
sudo mkfs.xfs /dev/sdb1
```

`mkfs.*` là thao tác phá hủy dữ liệu trên target device. Trước khi format, kiểm tra read-only bằng `lsblk -f`, `blkid`, `findmnt`, serial/WWN và mountpoint; với server remote nên có backup hoặc xác nhận volume mới attach từ cloud/storage backend.

Kiểm tra/sửa lỗi filesystem:

```bash
# ext filesystem, chỉ chạy khi unmount hoặc trong rescue mode
sudo fsck -f /dev/sdb1

# XFS
sudo xfs_repair /dev/sdb1
```

Không chạy `fsck` trên filesystem đang được mount read-write. Với root filesystem hoặc mount chứa dữ liệu quan trọng, cần boot vào rescue/live environment hoặc maintenance window, backup/snapshot trước, ghi lại output sửa lỗi và chỉ mount lại sau khi kiểm tra sạch. Nếu lỗi filesystem lặp lại sau khi repair, kiểm tra thêm SMART/storage backend/controller vì nguyên nhân có thể nằm dưới filesystem.

Resize filesystem sau khi tăng disk/LV:

```bash
# ext4
sudo resize2fs /dev/vg_data/lv_app

# XFS, chạy trên mountpoint
sudo xfs_growfs /data/app
```

## 5. Mount và Umount

```bash
sudo mkdir -p /data
sudo mount /dev/sdb1 /data
findmnt /data
df -h /data
sudo umount /data
```

Nếu filesystem đang bận:

```bash
sudo lsof +f -- /data
sudo fuser -vm /data
```

## 6. `/etc/fstab`, UUID và Label

Không nên dùng device name như `/dev/sdb1` trong `fstab` cho server lâu dài vì thứ tự device có thể đổi. Ưu tiên `UUID` hoặc `LABEL`.

```bash
blkid /dev/sdb1
sudo e2label /dev/sdb1 DATA
ls -l /dev/disk/by-uuid/
ls -l /dev/disk/by-id/
ls -l /dev/disk/by-label/
ls -l /dev/disk/by-path/
```

Các symlink dưới `/dev/disk/` do `udev` tạo và ổn định hơn `/dev/sdX`:

| Path | Khi hữu ích |
| --- | --- |
| `/dev/disk/by-uuid/` | Mount filesystem hoặc swap theo UUID trong `fstab` |
| `/dev/disk/by-label/` | Dễ đọc với volume ít và label được quản lý chặt |
| `/dev/disk/by-id/` | Nhận diện disk/LUN theo serial, WWN hoặc vendor ID |
| `/dev/disk/by-path/` | Debug đường đi qua bus/controller/port; có thể đổi khi thay topology |

Ví dụ `/etc/fstab`:

```text
UUID=<uuid> /data ext4 defaults,nofail 0 2
```

Checklist trước khi sửa `/etc/fstab`:

```bash
sudo cp /etc/fstab /etc/fstab.bak.$(date +%F-%H%M)
sudo findmnt --verify
sudo mount -a
findmnt /data
```

Production notes:

- Backup `/etc/fstab` trước khi sửa và ưu tiên dùng `UUID` thay vì `/dev/sdX`.
- Giữ một root shell đang mở khi sửa mount quan trọng.
- Với mount không bắt buộc cho boot, cân nhắc `nofail`.
- Không reboot trước khi `findmnt --verify` và `mount -a` chạy sạch.
- Với mount network hoặc storage chậm, cân nhắc `x-systemd.automount`/timeout phù hợp để tránh boot bị kẹt; chỉ dùng sau khi đã test trên môi trường tương đương.

## 7. Swap

Kiểm tra swap:

```bash
swapon --show
free -h
cat /proc/swaps
```

Tạo swap file:

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
swapon --show
```

Thêm vào `/etc/fstab`:

```text
/swapfile none swap sw 0 0
```

Swappiness:

```bash
cat /proc/sys/vm/swappiness
sudo sysctl vm.swappiness=10
echo 'vm.swappiness = 10' | sudo tee /etc/sysctl.d/99-swappiness.conf
```

## 8. Di Chuyển Thư Mục `/home` Sang Partition Riêng

Use case: tách dữ liệu user khỏi root filesystem để dễ reinstall OS hoặc cô lập dung lượng.

High-level workflow:

1. Backup dữ liệu `/home`.
2. Tạo partition/filesystem mới.
3. Mount tạm vào `/mnt/newhome`.
4. Copy dữ liệu bằng `rsync -aHAX`.
5. Đổi tên `/home` cũ để rollback.
6. Mount filesystem mới vào `/home`.
7. Cập nhật `/etc/fstab` bằng UUID.
8. Test login/user data.

Ví dụ:

```bash
sudo mkdir -p /mnt/newhome
sudo mount /dev/sdb1 /mnt/newhome
sudo rsync -aHAX --numeric-ids /home/ /mnt/newhome/
sudo mv /home /home.old
sudo mkdir /home
sudo mount /dev/sdb1 /home
sudo restorecon -RFv /home 2>/dev/null || true
```

`fstab`:

```text
UUID=<uuid> /home ext4 defaults 0 2
```

Cảnh báo production:

- Cần maintenance window.
- User nên logout, service dùng `/home` nên dừng.
- Luôn có backup và rollback path `/home.old`.
- Kiểm tra SELinux context nếu dùng RHEL/CentOS.

## 9. Troubleshooting

### Mount Failed

```bash
mount -a
journalctl -xe
dmesg -T | tail -100
blkid
findmnt --verify
```

Nguyên nhân thường gặp:

- UUID sai.
- Filesystem type sai.
- Mountpoint không tồn tại.
- Filesystem lỗi.
- Device chưa attach.

### Disk Full

```bash
df -h
df -ih
du -xh / --max-depth=1 2>/dev/null | sort -h
lsof +L1
journalctl --disk-usage
```

Nếu file đã bị xóa nhưng disk vẫn full, kiểm tra process còn giữ deleted file bằng `lsof +L1`.

Nếu `df -h` vẫn còn dung lượng nhưng ứng dụng không tạo được file mới, kiểm tra inode bằng `df -ih`. Workload nhiều file nhỏ, log nhỏ hoặc cache nhỏ có thể làm inode hết trước khi block space hết.
