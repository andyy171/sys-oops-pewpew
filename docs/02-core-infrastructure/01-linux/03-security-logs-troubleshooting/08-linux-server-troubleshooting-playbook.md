# Linux Server Troubleshooting Playbook

Note này chuyển hóa `_inbox/DevOps-Troubleshooting-Linux-Server-Best-Practices.docx` thành playbook điều tra sự cố Linux server. Nội dung nguồn bao phủ troubleshooting method, CPU/RAM/I/O, boot, disk, network, DNS, email, web, database và hardware.

## Tư Duy Troubleshooting

Troubleshooting tốt không bắt đầu bằng command, mà bắt đầu bằng scope:

1. Sự cố bắt đầu lúc nào?
2. Ảnh hưởng user/service nào?
3. Có thay đổi/deploy/maintenance gần đó không?
4. Lỗi tái hiện được không?
5. Có workaround giảm impact trước khi root cause không?
6. Dữ liệu nào cần thu thập trước khi restart/kill process?

Khi phối hợp nhóm:

- thống nhất một kênh incident chính;
- ghi timeline;
- phân vai người điều phối, người thao tác, người ghi log;
- không để nhiều người cùng sửa một hệ thống mà không thông báo.

## Server Slow: CPU, Memory, Disk I/O

Luồng triage:

```bash
uptime
top
free -h
vmstat 1
iostat -xz 1
pidstat 1
dmesg -T | tail -100
```

Diễn giải nhanh:

| Dấu hiệu | Nghi ngờ |
|---|---|
| CPU user/system cao | process tính toán, loop, thread quá nhiều |
| memory available thấp, swap tăng | memory pressure hoặc leak |
| OOM log | kernel đã kill process |
| iowait cao | disk/storage/network filesystem chậm |
| load cao nhưng CPU không cao | nhiều task stuck I/O hoặc state `D` |

Sysstat hữu ích để xem lịch sử:

```bash
sar -u
sar -r
sar -b
sar -n DEV
```

## Boot Problem

Boot failure nên đi theo chuỗi:

```text
Firmware/BIOS/UEFI -> bootloader -> kernel/initramfs -> root filesystem -> init/systemd -> services
```

Checklist:

- máy có thấy disk boot không;
- GRUB có prompt/menu không;
- kernel parameter `root=` đúng không;
- initramfs có driver storage/filesystem không;
- `/etc/fstab` có entry làm boot vào emergency không;
- root filesystem có corrupt hoặc full không.

Command khi vào rescue/emergency:

```bash
lsblk -f
blkid
mount
journalctl -xb
findmnt --verify
```

Trước khi sửa GRUB/fstab, backup file cấu hình nếu filesystem còn ghi được.

## Disk Full, Filesystem Corrupt, Read-Only

Triệu chứng:

- app không ghi log/data;
- package manager fail;
- database stop;
- filesystem bị remount read-only.

Triage:

```bash
df -h
df -ih
du -xh /var --max-depth=1 2>/dev/null | sort -h
lsof +L1
mount | grep ' ro,'
dmesg -T | grep -i -E 'i/o error|ext4|xfs|read-only|corrupt'
```

Điểm hay bị bỏ qua:

- inode đầy dù dung lượng còn;
- file log đã xóa nhưng process vẫn giữ fd;
- reserved block trên filesystem;
- snapshot/backup sinh file lớn;
- filesystem read-only vì lỗi I/O.

Không chạy repair filesystem trên mounted filesystem đang ghi. Với production, cần backup/snapshot và maintenance window.

## Network Problem

Đi theo layer:

```bash
ip addr
ip route
ip route get <target-ip>
ss -tulpn
ss -s
ping -c 5 <gateway-or-target>
tracepath <target>
nc -vz <host> <port>
```

Phân biệt:

- `connection refused`: tới được host nhưng service không listen hoặc firewall reject.
- timeout: route/firewall/security group/service path có thể drop.
- ping được IP nhưng hostname không được: DNS.
- một chiều được một chiều không: route bất đối xứng hoặc firewall state.

## DNS Problem

DNS dễ gây hiểu nhầm vì app thường chỉ báo timeout hoặc cannot connect.

```bash
resolvectl status
cat /etc/resolv.conf
getent hosts example.com
dig example.com
dig @<dns-server> example.com
```

Checklist:

- resolver local đang dùng DNS server nào;
- DNS server có reachable không;
- search domain có làm query sai không;
- cache DNS có stale không;
- split-horizon/internal DNS có khác public DNS không;
- record TTL có làm rollout chậm không.

## Email Problem

Với server gửi mail, kiểm tra theo chuỗi:

```text
app -> local MUA/MDA -> local MTA -> queue -> DNS/MX -> remote SMTP -> spam/filtering -> inbox
```

Mental model nhanh:

| Thành phần | Vai trò |
|---|---|
| MUA | User-facing client đọc/gửi mail, ví dụ `mail`, `mailx`, webmail hoặc app client. |
| MDA | Giao mail vào mailbox local, ví dụ mail spool dưới `/var/spool/mail` hoặc `/var/mail`. |
| MTA | Chuyển mail local/remote, ví dụ Postfix, Sendmail, Exim. |

Command:

```bash
mail -s "test message" <local-user>
mailq 2>/dev/null || postqueue -p 2>/dev/null
sendmail -bp 2>/dev/null || true
journalctl -u postfix --since "1 hour ago" 2>/dev/null
grep -Rin "deferred\\|bounced\\|reject\\|warning" /var/log/mail* /var/log/maillog 2>/dev/null
dig MX example.com
nc -vz <smtp-host> 25
```

Điểm cần xem:

- queue có backlog không;
- DNS MX/SPF/DKIM/DMARC;
- port 25 outbound có bị cloud/provider chặn không;
- remote SMTP trả mã lỗi gì.
- local account có mailbox đúng path không;
- username case-sensitive/case-normalization có làm Postfix/local delivery fail không;
- alias hoặc forward có redirect mail sang người nhận khác không.

Alias và forward:

```bash
grep '^support:' /etc/aliases
sudoedit /etc/aliases
sudo newaliases
test -f ~/.forward && ls -l ~/.forward
```

`/etc/aliases` cần chạy `newaliases` sau khi sửa để cập nhật database alias. `.forward` là per-user forwarding, thường cần permission không quá mở, ví dụ `0644`, và có thể làm người dùng tưởng mail bị mất vì mail đã được chuyển sang mailbox khác.

Không xóa file queue thô trong `/var/spool` để "dọn nhanh" nếu chưa snapshot/ghi lại Queue ID và hiểu MTA đang dùng. Ưu tiên hold/defer/requeue/delete bằng tool của MTA tương ứng và giữ evidence nếu đang điều tra incident hoặc data leakage.

## Web Server Problem

```bash
curl -v http://127.0.0.1/
curl -vk https://example.com/
ss -tulpn | grep -E ':80|:443'
systemctl status nginx apache2 httpd
tail -f /var/log/nginx/error.log 2>/dev/null
tail -f /var/log/httpd/error_log 2>/dev/null
```

Khoanh vùng:

- DNS trỏ đúng IP không;
- load balancer/ingress có healthy target không;
- web server listen port đúng không;
- certificate TLS còn hạn không;
- backend upstream còn sống không;
- disk/log full không.

## Database Slow

Tư duy:

- database slow có thể do query, index, lock, connection pool, disk I/O hoặc network.
- Đừng restart database trước khi thu thập trạng thái nếu chưa cần giảm impact khẩn cấp.

Checklist chung:

```bash
top
iostat -xz 1
ss -tan | grep <db-port> | wc -l
journalctl -u <db-service> --since "1 hour ago"
```

Trong DB:

- xem slow query;
- xem connection count;
- xem lock/wait;
- xem replication lag nếu có;
- kiểm tra disk free và fsync latency.

## Hardware Fault

Dấu hiệu:

- kernel log có I/O error, reset bus, ECC, NIC flap;
- disk SMART báo lỗi;
- node tự reboot;
- performance giảm không giải thích được.

Command:

```bash
dmesg -T | grep -i -E 'error|fail|reset|timeout|mce|edac|nvme|scsi'
journalctl -k --since "24 hours ago"
smartctl -a /dev/<disk> 2>/dev/null
ip -s link
```

Với VM/cloud, hardware fault có thể hiện thành lỗi hypervisor, storage backend, noisy neighbor hoặc underlying host issue. Cần đối chiếu metric cloud/provider.

## Sau Incident

Ghi lại:

- symptom và impact;
- timeline;
- command/log đã dùng;
- root cause hoặc contributing factors;
- workaround/fix;
- preventive action;
- runbook cần cập nhật.

## Source Coverage Matrix

`DevOps-Troubleshooting-Linux-Server-Best-Practices.docx` da duoc chuyen hoa theo cac nhom:

| Source topic | Da chuyen hoa vao |
|---|---|
| Troubleshooting best practices, communication, backup communication | Tu Duy Troubleshooting |
| Server slow: CPU, RAM, disk I/O, top, sysstat, sar | Server Slow |
| Boot problem: BIOS, GRUB, kernel, initrd, init, rescue | Boot Problem |
| Disk full/corrupt: reserved blocks, largest dirs, read-only | Disk Full, Filesystem Corrupt, Read-Only |
| Network problem: client/server, tcpdump, iftop, bandwidth | Network Problem |
| DNS problem: resolver/recursive name server issues | DNS Problem |
| Email problem: outbound mail, destination SMTP, queue | Email Problem |
| Web problem: sluggish/unavailable web, HTTP 5xx, Apache metrics | Web Server Problem |
| Database slow: active threads, metrics, query/resource pressure | Database Slow |
| Hardware fault: disk/NIC/kernel hardware signals | Hardware Fault |

Cong cu nhu `tcpdump`, `iftop`, Apache status va database-specific metrics duoc giu o muc playbook. Neu can lab sau nay, nen tach thanh runbook rieng theo tung service.

## Related Pages

- [Common Linux Troubleshooting Runbooks](./04-common-troubleshooting-runbooks.md)
- [Performance Troubleshooting](./05-performance-troubleshooting.md)
- [Logs, journald, rsyslog và logrotate](./01-logs-journald-rsyslog-logrotate.md)
