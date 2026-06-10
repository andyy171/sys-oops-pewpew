# Linux Overview, Boot Process và systemd

## 1. Linux System Overview

Linux là hệ điều hành Unix-like, thường dùng cho server, cloud, container host, network appliance và embedded system. Một hệ thống Linux vận hành quanh các lớp chính:

- Kernel: quản lý process, memory, filesystem, network stack, device driver và system call.
- User space: shell, core utilities, package manager, daemon, service và ứng dụng.
- Filesystem hierarchy: tổ chức file cấu hình, binary, log, runtime data và dữ liệu người dùng.
- Init/service manager: khởi động hệ thống và quản lý daemon. Trên distro hiện đại, phần này thường là `systemd`.

## 2. Khi Dùng Trong Thực Tế

File này dùng như bản đồ tổng quan khi cần:

- Hiểu Linux boot qua các lớp firmware, bootloader, kernel và `systemd`.
- Xác định service đang được `systemd` quản lý như thế nào.
- Kiểm tra nhanh lỗi boot, target, unit hoặc service failed.
- Đọc các path hệ thống quan trọng trước khi đi sâu vào storage, security hoặc troubleshooting.

## 3. Filesystem Hierarchy Standard

Các thư mục quan trọng cần nắm khi vận hành Linux:

| Path | Vai trò |
| --- | --- |
| `/` | Root filesystem, điểm bắt đầu của toàn bộ cây thư mục |
| `/boot` | Kernel, initramfs, GRUB config; hệ UEFI có thêm `/boot/efi` |
| `/etc` | Cấu hình tĩnh của hệ thống và service |
| `/bin`, `/usr/bin` | Lệnh cho user |
| `/sbin`, `/usr/sbin` | Lệnh quản trị hệ thống |
| `/lib`, `/usr/lib` | Library và kernel modules |
| `/dev` | Device nodes do kernel/udev quản lý |
| `/proc` | Virtual filesystem expose process và kernel runtime state |
| `/sys` | Virtual filesystem expose device, driver và kernel object |
| `/run` | Runtime state trong một phiên boot |
| `/var` | Log, cache, spool, state data thường xuyên thay đổi |
| `/home` | Dữ liệu người dùng |
| `/root` | Home directory của `root` |
| `/mnt`, `/media` | Mount point tạm hoặc removable media |
| `/opt` | Third-party/self-contained software |
| `/srv` | Dữ liệu phục vụ bởi service như web, ftp, nfs |

Không nên biến note FHS thành note storage chi tiết. Các thao tác disk, partition, mount, fstab và swap nằm ở [Disk, Filesystem, Mount và Swap](../02-storage-networking/01-disk-filesystem-mount-swap.md).

## 4. Boot Flow: BIOS/UEFI -> GRUB -> Kernel -> init/systemd

Luồng boot cơ bản:

1. Firmware chạy POST và tìm boot device.
2. BIOS đọc boot loader từ MBR, hoặc UEFI đọc boot entry từ EFI System Partition.
3. GRUB hiển thị menu, nạp kernel và initramfs.
4. Kernel khởi tạo hardware, mount root filesystem ban đầu và chạy PID 1.
5. PID 1, thường là `systemd`, khởi động target, service, mount, socket và timer.
6. Hệ thống vào trạng thái login hoặc workload service.

### BIOS và MBR

BIOS thường tìm boot code trong sector đầu tiên của disk. MBR có kích thước 512 byte, chứa boot loader stage đầu, partition table kiểu legacy và magic number.

### UEFI

UEFI dùng EFI System Partition, thường mount tại `/boot/efi`. Boot entry được quản lý bởi firmware và có thể kiểm tra bằng:

```bash
efibootmgr -v
```

### GRUB

GRUB chịu trách nhiệm chọn kernel, initramfs và kernel parameter.

```bash
grep ^menuentry /boot/grub/grub.cfg
cat /proc/cmdline
```

Đường dẫn config có thể khác nhau theo distro:

- Debian/Ubuntu: thường dùng `update-grub`.
- RHEL/CentOS BIOS: thường ghi vào `/boot/grub2/grub.cfg`.
- RHEL/CentOS UEFI: có thể nằm dưới `/boot/efi/EFI/<vendor>/grub.cfg`.

## 5. systemd, Unit, Service và Target

`systemd` là init system và service manager phổ biến trên Linux hiện đại. Nó chạy với PID 1 và quản lý service thông qua unit.

Các unit thường gặp:

| Unit | Ý nghĩa |
| --- | --- |
| `.service` | Daemon hoặc service |
| `.socket` | Socket activation |
| `.mount` | Mount point |
| `.automount` | Automount |
| `.timer` | Lịch chạy thay cho cron trong nhiều use case |
| `.target` | Nhóm trạng thái hệ thống |
| `.path` | Kích hoạt theo thay đổi path |
| `.device` | Device unit |

Target thay thế runlevel truyền thống:

| SysV runlevel | systemd target | Ý nghĩa |
| --- | --- | --- |
| 0 | `poweroff.target` | Tắt máy |
| 1 | `rescue.target` | Rescue/single-user |
| 3 | `multi-user.target` | Multi-user CLI |
| 5 | `graphical.target` | GUI |
| 6 | `reboot.target` | Reboot |

## 6. Common Commands

```bash
# Xem init system và PID 1
ps -p 1 -o pid,comm,args

# Xem default target
systemctl get-default
systemctl set-default multi-user.target
systemctl set-default graphical.target

# Chuyển target tạm thời
systemctl isolate multi-user.target
systemctl isolate graphical.target

# Quản lý service
systemctl status ssh
systemctl start ssh
systemctl stop ssh
systemctl restart ssh
systemctl reload ssh
systemctl enable ssh
systemctl disable ssh

# Xem unit
systemctl list-units --type=service
systemctl list-unit-files
systemctl cat ssh.service

# Log theo service
journalctl -u ssh
journalctl -u ssh -b
journalctl -u ssh -xe
```

## 7. Troubleshooting Quick Checks

Khi hệ thống không boot hoặc service không lên:

```bash
# Boot/kernel message
journalctl -xb
dmesg -T | tail -100

# Service failure
systemctl --failed
systemctl status <service>
journalctl -u <service> -xe

# Mount lỗi trong boot
findmnt
systemctl status local-fs.target
mount -a

# Target hiện tại
systemctl get-default
systemctl list-dependencies multi-user.target
```

## 8. Production Notes

- Không sửa GRUB hoặc kernel parameter trên production nếu chưa có console/out-of-band access và rollback plan.
- Trước khi reboot sau khi sửa boot config, `systemd` unit hoặc `/etc/fstab`, giữ một session root đang mở nếu có thể.
- Với service quan trọng, validate config trước khi `restart` hoặc `reload`, ví dụ `nginx -t`, `sshd -t`, `named-checkconf`.
- Không reboot để “thử may mắn” khi chưa kiểm tra log boot, fstab, disk và service dependency.
