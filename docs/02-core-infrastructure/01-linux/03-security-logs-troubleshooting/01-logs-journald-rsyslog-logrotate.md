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
```

Giới hạn dung lượng trong `/etc/systemd/journald.conf`:

```ini
SystemMaxUse=1G
RuntimeMaxUse=200M
MaxRetentionSec=30day
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
```

Trong đó:

- `@`: UDP.
- `@@`: TCP.

Sau khi sửa:

```bash
sudo rsyslogd -N1
sudo systemctl restart rsyslog
```

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
```

Notes:

- `copytruncate` tiện cho app không reopen log, nhưng có rủi ro mất một ít log trong lúc copy.
- App tốt nên hỗ trợ reopen log bằng signal hoặc restart/reload.

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
grep -Rin "error\\|failed\\|denied" /var/log 2>/dev/null
tail -n 200 /var/log/syslog
zgrep -Hin "error" /var/log/syslog*
```

Production notes:

- Không xóa log trước khi thu thập evidence cho incident/RCA.
- Luôn ghi rõ timezone, time window và host khi trích log.
- Với log đã rotate/compress, kiểm tra cả file `.1`, `.gz` bằng `zgrep`.

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
