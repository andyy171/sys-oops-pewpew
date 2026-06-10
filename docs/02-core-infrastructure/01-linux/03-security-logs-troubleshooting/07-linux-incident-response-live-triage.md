# Linux Incident Response Live Triage

## Overview

Live triage là bước thu thập nhanh trạng thái của một Linux host nghi ngờ bị xâm nhập khi máy vẫn đang chạy. Mục tiêu là giữ bằng chứng dễ mất, xác định mức độ ảnh hưởng và quyết định có cần cô lập host hay chuyển sang forensic sâu hơn.

Ưu tiên read-only command. Ghi lại thời gian, hostname, user đang thao tác và mọi lệnh đã chạy. Không reboot, cleanup hoặc xóa file trước khi có quyết định xử lý sự cố rõ ràng.

## Triage Order

Một thứ tự thực tế:

1. Xác định host, thời gian và phạm vi nghi ngờ.
2. Thu user/login/authentication.
3. Thu process/service/scheduled job.
4. Thu network connection/listening port.
5. Thu filesystem thay đổi gần đây.
6. Thu log liên quan và đóng gói evidence.

Quy trình IR nên đi theo vòng lặp có kiểm soát:

```text
preparation -> identification and scoping -> containment -> eradication
-> recovery -> lessons learned
```

Không nhảy thẳng vào cleanup khi chưa scope. Rushing identification có thể làm bỏ sót phạm vi compromise; bỏ containment cho phép attacker pivot; hasty remediation có thể làm mất evidence hoặc khiến attacker đổi tactic.

## Initial Context

```bash
date -Is
hostnamectl
uname -a
cat /etc/os-release
uptime
who
w
id
```

Nếu đang trong incident thật, tạo thư mục evidence có timestamp và giữ permission chặt:

```bash
IR_DIR="/root/ir-$(date +%Y%m%d-%H%M%S)"
sudo mkdir -p "$IR_DIR"
sudo chmod 700 "$IR_DIR"
```

Không đặt evidence trên filesystem sắp đầy hoặc volume nghi có vấn đề.

## User And Authentication

Kiểm tra account, UID đặc biệt và login gần đây:

```bash
getent passwd
getent group sudo
getent group wheel
awk -F: '$3 == 0 {print $1":"$3":"$6":"$7}' /etc/passwd
last -a | head -50
lastlog | head -50
```

Kiểm tra account không có owner file tương ứng hoặc file không thuộc user nào:

```bash
find / -xdev \( -nouser -o -nogroup \) -ls 2>/dev/null
```

Kiểm tra sudoers an toàn:

```bash
sudo visudo -c
sudo grep -R "NOPASSWD\\|ALL=(ALL)" /etc/sudoers /etc/sudoers.d 2>/dev/null
```

Log authentication:

```bash
sudo journalctl --since "24 hours ago" -u ssh -u sshd 2>/dev/null
sudo journalctl --since "24 hours ago" | grep -Ei "sshd|sudo|su|useradd|passwd|authentication"
sudo tail -200 /var/log/auth.log 2>/dev/null
sudo tail -200 /var/log/secure 2>/dev/null
```

## Process And Service

```bash
ps auxww
pstree -ap
top -b -n 1 | head -40
systemctl --type=service --state=running
systemctl --failed
```

Điểm cần chú ý:

- Process chạy từ `/tmp`, `/var/tmp`, `/dev/shm` hoặc home directory.
- Command line chứa URL lạ, encoded payload, token hoặc password.
- Service mới, service failed bất thường hoặc binary path không chuẩn.
- Parent/child process không hợp lý, ví dụ web server spawn shell.

Xem chi tiết process:

```bash
sudo ls -la /proc/<pid>/exe
sudo sh -c "tr '\\0' ' ' < /proc/<pid>/cmdline"
sudo ls -la /proc/<pid>/cwd
sudo lsof -p <pid>
```

## Network Triage

```bash
ip addr
ip route
ip neigh
ss -tulpn
ss -antp
sudo lsof -i -P -n
```

Kiểm tra firewall và NAT:

```bash
sudo nft list ruleset 2>/dev/null
sudo iptables -L -n -v 2>/dev/null
sudo iptables -t nat -L -n -v 2>/dev/null
sudo firewall-cmd --list-all 2>/dev/null
sudo ufw status verbose 2>/dev/null
```

Nếu cần capture ngắn để xác nhận kết nối, giới hạn thời gian và kích thước:

```bash
sudo tcpdump -i <interface> -nn -s 0 -c 200 -w /root/ir-capture.pcap
```

## Persistence Checks

Cron và timer:

```bash
cat /etc/crontab
ls -la /etc/cron.d /etc/cron.hourly /etc/cron.daily /etc/cron.weekly
for user in $(cut -d: -f1 /etc/passwd); do sudo crontab -l -u "$user" 2>/dev/null; done
systemctl list-timers --all
```

Systemd unit:

```bash
systemctl list-unit-files --type=service
find /etc/systemd/system /usr/lib/systemd/system /lib/systemd/system -type f -mtime -14 -ls 2>/dev/null
```

SSH persistence:

```bash
find /home /root -path "*/.ssh/authorized_keys" -type f -ls 2>/dev/null
sudo find /home /root -path "*/.ssh/authorized_keys" -type f -exec sh -c 'echo "### $1"; tail -n +1 "$1"' sh {} \\; 2>/dev/null
```

Không xóa key lạ ngay khi chưa lưu bằng chứng và chưa có quyết định containment.

## Filesystem And Recent Changes

File mới hoặc sửa gần đây:

```bash
find / -xdev -type f -mtime -2 -ls 2>/dev/null
find /tmp /var/tmp /dev/shm -type f -ls 2>/dev/null
```

SUID/SGID/capabilities mới:

```bash
find / -xdev -perm -4000 -type f -ls 2>/dev/null
find / -xdev -perm -2000 -type f -ls 2>/dev/null
getcap -r / 2>/dev/null
```

File lớn bất thường:

```bash
find / -xdev -type f -size +500M -ls 2>/dev/null
```

Artifact hunting nên gom theo nhóm thay vì chỉ chạy một danh sách lệnh:

| Nhóm artifact | Dấu hiệu cần nhìn |
| --- | --- |
| Account | UID 0 lạ, user mới, sudoers thay đổi, group đặc quyền thay đổi |
| SSH | `authorized_keys` mới, key lạ trong `/root/.ssh` hoặc home user |
| Shell history | `.bash_history`, `.zsh_history`, `.viminfo`, `.lesshst` bị xóa, bị truncate hoặc có command lạ |
| Persistence | cron, systemd unit, startup script, binary mới, file ẩn |
| Package manager | package/repo lạ, package cài trong incident window, pre/post-install script đáng ngờ |
| Process | process chạy từ `/tmp`, `/var/tmp`, `/dev/shm`, parent-child bất thường |
| Network | port lạ, connection dài, process không rõ owner đang dùng network |
| Logs | auth/journal/service log bị ngắt quãng, logrotate state bất thường, failed sudo/SSH pattern |
| Rootkit | binary bị thay thế, library hijack, kernel module lạ, bootloader/firmware persistence, memory-only behavior |

Nếu cần tạo timeline forensic, phân biệt `mtime`, `atime`, `ctime` và `btime/crtime` vì mỗi loại timestamp trả lời câu hỏi khác nhau. Timestamp có thể bị thao túng hoặc phụ thuộc filesystem/mount option, nên cần đối chiếu với log và package/process evidence.

Acquisition và forensic tools như `dd`, `dcfldd`, `ewfacquire`, AVML, LiME, UAC hoặc Velociraptor cần quyền cao và có thể ảnh hưởng host. Trong production, ưu tiên policy IR, hash, chain of custody, read-only mount và kênh chuyển evidence đã được phê duyệt.

## Evidence Package

Ví dụ thu evidence text vào thư mục riêng:

```bash
IR_DIR="/root/ir-$(date +%Y%m%d-%H%M%S)"
sudo mkdir -p "$IR_DIR"
sudo chmod 700 "$IR_DIR"
sudo sh -c "date -Is > '$IR_DIR/summary.txt'"
sudo sh -c "hostnamectl >> '$IR_DIR/summary.txt'"
sudo sh -c "ss -tulpn > '$IR_DIR/ss-tulpn.txt'"
sudo sh -c "ps auxww > '$IR_DIR/ps-auxww.txt'"
sudo sh -c "journalctl --since '24 hours ago' > '$IR_DIR/journal-last24h.txt'"
sudo sh -c "sha256sum '$IR_DIR'/* > '$IR_DIR/sha256sums.txt'"
```

Nếu cần chuyển evidence ra ngoài, dùng kênh đã được phê duyệt và giữ hash đi kèm.

## Decision Points

- Nếu có dấu hiệu active compromise: cô lập network ở switch/security group/firewall thay vì tắt máy ngay.
- Nếu có khả năng memory-resident malware: cân nhắc memory capture trước reboot.
- Nếu host chứa dữ liệu nhạy cảm: mở incident theo quy trình compliance.
- Nếu root bị compromise: rebuild từ image sạch thường an toàn hơn cleanup thủ công.

## Related Pages

- [Linux Privilege Escalation Defense](./06-linux-privilege-escalation-defense.md)
- [Logs, journald, rsyslog và logrotate](./01-logs-journald-rsyslog-logrotate.md)
- [Common Linux Troubleshooting Runbooks](./04-common-troubleshooting-runbooks.md)
- [Network Tools And Troubleshooting](../../02-network/Tools%20&%20Troubleshooting/netstat,%20ss,%20tcpdump,%20nmap,%20netcat.md)
