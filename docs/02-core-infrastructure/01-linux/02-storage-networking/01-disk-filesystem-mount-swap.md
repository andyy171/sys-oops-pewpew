# Disk, Filesystem, Mount và Swap

## 1. Disk và Partition Overview

Linux nhìn disk như block device trong `/dev`, ví dụ:

- `/dev/sda`, `/dev/sdb`: SATA/SCSI/virtio disk.
- `/dev/nvme0n1`: NVMe disk.
- `/dev/sda1`, `/dev/nvme0n1p1`: partition.

Các lệnh kiểm tra:

```bash
lsblk
lsblk -f
blkid
fdisk -l
parted -l
df -h
findmnt
```

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

Filesystem thường gặp:

| Filesystem | Use case |
| --- | --- |
| `ext4` | Phổ biến, ổn định, dễ vận hành |
| `xfs` | Phổ biến trên RHEL, tốt cho filesystem lớn |
| `btrfs` | Snapshot/subvolume, dùng tùy distro/use case |
| `vfat` | EFI System Partition |

Tạo filesystem:

```bash
sudo mkfs.ext4 /dev/sdb1
sudo mkfs.xfs /dev/sdb1
```

Kiểm tra/sửa lỗi filesystem:

```bash
# ext filesystem, chỉ chạy khi unmount hoặc trong rescue mode
sudo fsck -f /dev/sdb1

# XFS
sudo xfs_repair /dev/sdb1
```

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
```

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
- Không reboot trước khi `mount -a` chạy sạch.

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
du -xh / --max-depth=1 2>/dev/null | sort -h
lsof +L1
journalctl --disk-usage
```

Nếu file đã bị xóa nhưng disk vẫn full, kiểm tra process còn giữ deleted file bằng `lsof +L1`.
