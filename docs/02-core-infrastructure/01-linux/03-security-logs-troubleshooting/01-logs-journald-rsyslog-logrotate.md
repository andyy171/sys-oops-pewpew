# Logs, journald, rsyslog và logrotate

## 1. Log Locations

Linux log có thể nằm trong journal của `systemd`, file log dưới `/var/log`, hoặc log riêng của application.

Các file/thư mục thường gặp:

| Path | Nội dung |
| --- | --- |
| `/var/log/syslog` | Log tổng trên Debian/Ubuntu |
| `/var/log/messages` | Log tổng trên RHEL/CentOS |
| `/var/log/auth.log` | Authentication log trên Debian/Ubuntu |
| `/var/log/secure` | Authentication log trên RHEL/CentOS |
| `/var/log/kern.log` | Kernel log trên một số distro |
| `/var/log/journal/` | Persistent systemd journal nếu bật |
| `/var/log/nginx/`, `/var/log/httpd/` | Web server log |

Một số log dưới `/var/log` là binary file, không đọc trực tiếp bằng `cat`/`less` như text log:

| File | Tool đọc |
| --- | --- |
| `/var/log/wtmp` | `last` |
| `/var/log/btmp` | `lastb` |
| journal của `systemd` | `journalctl` |

Khi trích log cho RCA, luôn ghi rõ timezone, hostname, service/process và time window. Log line dạng syslog thường có timestamp, hostname, program/PID và message; nếu thiếu một trong các mảnh này thì dễ nhầm host hoặc nhầm thời điểm sự cố.

Syslog phân loại message bằng `facility` và `severity`. Facility cho biết nguồn log như `kern`, `auth`, `authpriv`, `daemon`, `mail`, `cron`, `lpr`, `local0`-`local7`; severity đi từ `emerg`, `alert`, `crit`, `err`, `warning`, `notice`, `info` tới `debug`. Khi viết rule, cần nhớ `*.warning` thường match warning và mức nghiêm trọng hơn; nếu chỉ muốn đúng một mức, dùng dạng `*.=warning`.

## 2. journald và journalctl

`journald` thu thập log từ kernel, service, stdout/stderr của unit và syslog-compatible source.

```bash
# Log boot hiện tại
journalctl -b

# Log service
journalctl -u sshd
journalctl -u nginx -b

# Log theo thời gian
journalctl --since "2026-05-20 10:00" --until "2026-05-20 11:00"

# Warning trở lên
journalctl -p warning -b

# Kernel log
journalctl -k

# Follow realtime
journalctl -fu nginx
```

Persistent journal:

```bash
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald
journalctl --disk-usage
sudo journalctl --vacuum-time=30d
sudo journalctl --sync
sudo journalctl --rotate
```

Giới hạn dung lượng trong `/etc/systemd/journald.conf`:

```ini
SystemMaxUse=1G
RuntimeMaxUse=200M
MaxRetentionSec=30day
```

`journalctl --vacuum-*` chỉ dọn archived journal, không chắc làm active journal co lại ngay. Khi cần copy journal đang active để rescue/RCA, chạy `journalctl --sync` trước để flush queue xuống file.

`Storage=` trong `/etc/systemd/journald.conf` cần hiểu rõ:

| Giá trị | Hành vi |
| --- | --- |
| `auto` | Ghi persistent nếu `/var/log/journal` tồn tại, nếu không ghi volatile dưới `/run/log/journal`. |
| `persistent` | Tạo/ghi journal dưới `/var/log/journal`. |
| `volatile` | Chỉ ghi journal runtime dưới `/run/log/journal`, mất sau reboot. |
| `none` | Không lưu journal local. |

Không restart `systemd-journald` giữa incident nếu chưa cân nhắc evidence. Nếu cần đổi config, ghi lại trạng thái trước:

```bash
journalctl --disk-usage
grep -Ev '^\s*(#|$)' /etc/systemd/journald.conf
```

## 3. rsyslog

`rsyslog` nhận, filter và ghi log ra file hoặc forward log tới log server.

```bash
systemctl status rsyslog
grep -R "auth\\|secure\\|messages\\|syslog" /etc/rsyslog.conf /etc/rsyslog.d/
```

Ví dụ forward log:

```text
*.* @@logserver.example.com:514
*.* @@(z5)logserver.example.com:6514
```

Trong đó:

- `@`: UDP.
- `@@`: TCP.
- `@@(z5)`: TCP kèm compression mức 5 nếu receiver hỗ trợ.

Rsyslog rule có dạng `facility.priority action`. Priority như `crit` thường match `crit` và các mức nghiêm trọng hơn; nếu chỉ muốn đúng một mức, dùng dạng `=crit`.

```text
kern.crit     /var/log/kernel-critical.log
kern.=crit    /var/log/kernel-critical-only.log
local0.notice /var/log/app-deploy.log
```

Sau khi sửa:

```bash
sudo rsyslogd -N1
sudo systemctl restart rsyslog
```

Nếu rsyslog lấy log từ journald, kiểm tra module input thay vì chỉ nhìn file log:

```bash
grep -E 'imjournal|imuxsock' /etc/rsyslog.conf /etc/rsyslog.d/*.conf 2>/dev/null
grep -E '^ForwardToSyslog=' /etc/systemd/journald.conf
```

Journal-client method thường giữ log boot sớm tốt hơn vì rsyslog đọc lại từ journal. Forward-to-syslog qua socket phụ thuộc timing giữa hai service hơn, nên cần test khi hardening logging pipeline.

## 4. logrotate

`logrotate` xoay vòng log để tránh đầy disk.

Config chính:

```bash
cat /etc/logrotate.conf
ls /etc/logrotate.d/
```

Ví dụ:

```text
/var/log/app/*.log {
    daily
    rotate 14
    compress
    missingok
    notifempty
    copytruncate
}
```

Test:

```bash
sudo logrotate -d /etc/logrotate.conf
sudo logrotate -f /etc/logrotate.d/app
cat /var/lib/logrotate/status 2>/dev/null || cat /var/lib/logrotate/logrotate.status 2>/dev/null
```

Notes:

- `copytruncate` tiện cho app không reopen log, nhưng có rủi ro mất một ít log trong lúc copy.
- App tốt nên hỗ trợ reopen log bằng signal hoặc restart/reload.
- `rotate 0` nghĩa là log cũ bị xóa thay vì giữ bản rotated; chỉ dùng khi retention policy cho phép.

## 4.1 Production Retention Guardrails

Log auth, sudo, firewall drop, database slow query, web access/error va cron nen co retention ro rang vi chung thuong la evidence cho incident/RCA.

Monitor dung luong `/var/log` va kich thuoc log bat thuong; log day disk la mot dang outage pho bien. Khi quan ly logrotate bang Ansible, nen template tung file trong `/etc/logrotate.d/`, chay dry-run truoc, va khong force rotate tren production neu chua hieu app co reopen log hay khong.

## 5. Log Investigation Method

Quy trình điều tra log:

1. Xác định service/host bị ảnh hưởng.
2. Xác định time window.
3. Xem journal theo service và boot.
4. Grep log file liên quan trong `/var/log`.
5. Đối chiếu auth, kernel, application log.
6. Kiểm tra logrotate/compress nếu log cũ bị xoay.
7. Ghi lại command và mốc thời gian dùng trong điều tra.

Commands:

```bash
systemctl status <service>
journalctl -u <service> --since "1 hour ago"
journalctl -p warning -b
journalctl -k
journalctl -r -n 100
journalctl _SYSTEMD_UNIT=ssh.service --since today
journalctl _UID=1000 --since "1 hour ago"
grep -Rin "error\\|failed\\|denied" /var/log 2>/dev/null
tail -n 200 /var/log/syslog
zgrep -Hin "error" /var/log/syslog*
```

Production notes:

- Không xóa log trước khi thu thập evidence cho incident/RCA.
- Luôn ghi rõ timezone, time window và host khi trích log.
- Với log đã rotate/compress, kiểm tra cả file `.1`, `.gz` bằng `zgrep`.

Khi cần đọc journal copy từ rescue/live environment hoặc từ host khác:

```bash
journalctl -D /mnt/sysroot/var/log/journal --no-pager
journalctl --file /tmp/system.journal --no-pager
journalctl -D /mnt/sysroot/var/log/journal --merge --since "2026-06-16 10:00"
```

Manual log entry hữu ích để đánh dấu timeline hoặc test pipeline:

```bash
logger -p local0.notice -t deploy "deployment started change_id=CHG-1234"
echo "manual journal marker" | systemd-cat -t maint
```

## 6. Common Patterns

### Authentication Failure

```bash
journalctl _COMM=sshd --since "1 hour ago"
grep -E "Failed password|Accepted publickey|sudo" /var/log/auth.log 2>/dev/null
grep -E "Failed password|Accepted publickey|sudo" /var/log/secure 2>/dev/null
```

### Kernel / Hardware Issue

```bash
journalctl -k -p warning
dmesg -T | tail -200
grep -Rin "I/O error\\|reset\\|oom\\|segfault" /var/log 2>/dev/null
```

### Service Crash

```bash
systemctl status <service>
journalctl -u <service> -b
coredumpctl list <service>
```

## 7. Appendix: Small Log Commands

```bash
# Top IP trong access log
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head

# Lọc theo HTTP status
awk '$9 ~ /^5/ {print}' access.log | head

# Theo dõi log realtime có highlight thô
tail -f /var/log/syslog | grep --line-buffered -Ei "error|failed|denied"
```

Script dài nên đặt ở [Sysadmin Scripts Collection](../04-shell-automation-advanced/08-sysadmin-scripts-collection.md).
