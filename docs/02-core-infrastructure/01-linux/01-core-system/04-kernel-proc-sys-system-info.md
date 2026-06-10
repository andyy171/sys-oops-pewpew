# Kernel, /proc, /sys và System Information

## 1. Kernel Version và Booted Kernel

Kernel là lớp lõi quản lý process, memory, filesystem, network stack, device driver và system call.

```bash
uname -r
uname -a
cat /proc/version
cat /proc/cmdline
```

Kiểm tra kernel package đã cài:

```bash
# Debian/Ubuntu
dpkg -l 'linux-image*'

# RHEL/CentOS/Fedora
rpm -qa 'kernel*'
```

Lưu ý: kernel package đã cài không đồng nghĩa kernel đang boot. Luôn kiểm tra `uname -r`.

## 2. Kernel Modules

Kernel module là phần mở rộng có thể load/unload để hỗ trợ driver hoặc tính năng kernel.

```bash
lsmod
modinfo <module>
sudo modprobe <module>
sudo modprobe -r <module>
```

Ví dụ:

```bash
lsmod | grep br_netfilter
modinfo overlay
```

Không unload module trên production nếu chưa rõ dependency và tác động tới workload. Trước khi dùng `modprobe -r`, kiểm tra module đang được dùng bởi module khác hay service nào bằng `lsmod`, log kernel và tài liệu của distro/vendor.

Load module khi boot:

```bash
echo br_netfilter | sudo tee /etc/modules-load.d/br_netfilter.conf
```

## 3. `/proc` Filesystem

`/proc` là virtual filesystem do kernel tạo, không phải dữ liệu nằm trên disk. Nó expose thông tin process và kernel runtime state.

Các path thường dùng:

| Path | Ý nghĩa |
| --- | --- |
| `/proc/cpuinfo` | Thông tin CPU |
| `/proc/meminfo` | Thông tin memory |
| `/proc/mounts` | Mount hiện tại |
| `/proc/partitions` | Partition kernel thấy |
| `/proc/uptime` | Uptime |
| `/proc/loadavg` | Load average |
| `/proc/cmdline` | Kernel command line |
| `/proc/<pid>/` | Thông tin process |
| `/proc/sys/` | Kernel tunable dùng bởi `sysctl` |

Ví dụ:

```bash
cat /proc/meminfo
cat /proc/loadavg
cat /proc/mounts
ls -l /proc/1
ls -l /proc/$(pidof sshd | awk '{print $1}')/fd
```

`/proc/<pid>` rất hữu ích khi debug process vì nó cho thấy trạng thái mà kernel đang biết, không phụ thuộc hoàn toàn vào output của application:

| Path | Dùng để kiểm tra |
| --- | --- |
| `/proc/<pid>/cmdline` | Command line thật của process, phân tách bằng byte null |
| `/proc/<pid>/environ` | Environment của process, có thể chứa secret nên chỉ đọc khi cần |
| `/proc/<pid>/cwd` | Working directory hiện tại |
| `/proc/<pid>/exe` | Binary đang chạy |
| `/proc/<pid>/fd/` | File descriptor đang mở: file, socket, pipe, device |
| `/proc/<pid>/maps` | Memory mapping, shared library, heap, stack |
| `/proc/<pid>/status` | State, UID/GID, thread count, memory summary |

Khi incident hoặc troubleshooting, ưu tiên đọc snapshot trước khi restart/kill process vì nhiều thông tin trong `/proc/<pid>` biến mất khi process kết thúc.

## 4. `/sys` Filesystem

`/sys` là virtual filesystem expose kernel object, device, driver và class. Nó thường dùng để kiểm tra hardware/runtime state hoặc tuning một số queue/device parameter.

Các path thường gặp:

| Path | Ý nghĩa |
| --- | --- |
| `/sys/class/net/` | Network interfaces |
| `/sys/block/` | Block devices |
| `/sys/devices/` | Device tree |
| `/sys/module/` | Loaded modules và parameters |

Ví dụ:

```bash
ls /sys/class/net
cat /sys/class/net/eth0/operstate
cat /sys/class/net/eth0/speed
ls /sys/block
cat /sys/block/sda/queue/scheduler
```

Không chỉnh file trong `/sys` nếu chưa hiểu tác động runtime và rollback.

## 5. `/dev` và `/run`

`/dev` chứa device nodes do kernel/udev quản lý:

```bash
ls -l /dev/sda
ls -l /dev/nvme0n1
ls -l /dev/null
udevadm info --query=all --name=/dev/sda
udevadm monitor
```

`/run` chứa runtime state trong một phiên boot:

```bash
ls /run
ls /run/systemd
ls /run/lock
```

`/var/run` trên hệ thống hiện đại thường là symlink tới `/run`.

## 6. debugfs và tracing runtime

`debugfs` là pseudo filesystem cho debugging/tracing của kernel. Nó thường mount dưới `/sys/kernel/debug` và được dùng bởi một số công cụ như `perf`, `ftrace`, dynamic debugging hoặc eBPF/BCC tooling.

Kiểm tra read-only:

```bash
mount | grep debugfs
ls /sys/kernel/debug 2>/dev/null
ls /sys/kernel/tracing 2>/dev/null
```

Mount debugfs hoặc bật tracing có thể làm lộ thông tin runtime nhạy cảm và tạo overhead. Trên production, chỉ bật khi có mục tiêu debug rõ, ghi lại thay đổi và tắt sau khi thu thập xong.

## 7. sysctl

`sysctl` đọc/ghi kernel tunable dưới `/proc/sys`.

```bash
sysctl -a
sysctl net.ipv4.ip_forward
sudo sysctl -w net.ipv4.ip_forward=1
```

Persistent config:

```bash
cat /etc/sysctl.conf
ls /etc/sysctl.d/
sudo sysctl --system
```

Thứ tự áp dụng có thể khác nhẹ theo distro, nhưng thực tế nên coi `/etc/sysctl.conf` và các file trong `/etc/sysctl.d/*.conf` là nguồn cấu hình persistent. Dùng `sysctl --system` để reload toàn bộ và kiểm tra output khi có key bị lỗi.

Ví dụ bật IP forwarding:

```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee /etc/sysctl.d/99-ip-forward.conf
sudo sysctl --system
```

Production notes:

- Ghi lại giá trị cũ trước khi thay đổi.
- Ưu tiên file riêng trong `/etc/sysctl.d/`.
- Kiểm tra tác động security/network trước khi bật forwarding hoặc relax kernel hardening.

## 8. System Information Commands

```bash
# OS, hostname, time
cat /etc/os-release
hostnamectl
timedatectl

# CPU/RAM
lscpu
free -h
cat /proc/cpuinfo
cat /proc/meminfo

# Disk/filesystem
lsblk -f
blkid
df -h
findmnt

# Hardware/device
lspci
lsusb
udevadm info --export-db

# Kernel/runtime
uname -a
dmesg -T | tail -100
journalctl -k
```

## 9. Quick Triage

```bash
uptime
hostnamectl
timedatectl
uname -r
free -h
df -h
lsblk -f
ip addr
ip route
systemctl --failed
dmesg -T | tail -100
journalctl -p warning -b
```

Script health-check dài nên đặt ở [Sysadmin Scripts Collection](../04-shell-automation-advanced/08-sysadmin-scripts-collection.md), không đặt trong note kernel/proc/sys.
