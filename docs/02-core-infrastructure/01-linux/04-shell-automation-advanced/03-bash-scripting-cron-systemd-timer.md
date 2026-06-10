# Bash Scripting, cron và systemd timer

## 1. Bash Scripting Foundation

Một script bash nên có shebang, strict mode phù hợp, biến rõ ràng và exit code có kiểm soát.

```bash
#!/usr/bin/env bash
set -euo pipefail

main() {
  echo "Hello from script"
}

main "$@"
```

Notes:

- `set -e`: thoát khi command fail.
- `set -u`: lỗi khi dùng biến chưa set.
- `set -o pipefail`: pipeline fail nếu command bên trong fail.

Không phải script nào cũng nên dùng strict mode tuyệt đối; cân nhắc khi có command được phép fail.

## 2. Variables, Condition, Loop, Function

Variables:

```bash
name="node-1"
echo "$name"
```

Condition:

```bash
if systemctl is-active --quiet nginx; then
  echo "nginx is running"
else
  echo "nginx is not running"
fi
```

Loop:

```bash
for service in nginx sshd cron; do
  systemctl status "$service" --no-pager
done
```

Function:

```bash
log() {
  printf '%s %s\n' "$(date -Is)" "$*"
}
```

## 3. Exit Code, Logging và Trap

```bash
if ! cp config.conf config.conf.bak; then
  echo "backup failed" >&2
  exit 1
fi
```

Trap cleanup:

```bash
tmpdir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmpdir"
}
trap cleanup EXIT
```

Log function:

```bash
log() {
  printf '%s [%s] %s\n' "$(date -Is)" "$$" "$*"
}
```

## 4. Input, Arguments và Quoting

```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <path>" >&2
  exit 2
fi

path="$1"

if [[ ! -e "$path" ]]; then
  echo "not found: $path" >&2
  exit 1
fi
```

Luôn quote biến path:

```bash
rm -i "$path"
```

## 5. cron

User crontab:

```bash
crontab -e
crontab -l
```

System cron:

```text
/etc/crontab
/etc/cron.d/
/etc/cron.daily/
```

Format:

```text
# minute hour day-of-month month day-of-week command
*/5 * * * * /usr/local/bin/check-service.sh
```

Production notes:

- Dùng absolute path trong cron.
- Redirect log rõ ràng.
- Cron có environment tối thiểu, không giống interactive shell.

Ví dụ:

```text
*/10 * * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
```

## 6. systemd Timer

systemd timer phù hợp cho scheduled job cần logging, dependency, retry và quản lý bằng `systemctl`.

Đường dẫn thường dùng:

```text
/etc/systemd/system/backup.service
/etc/systemd/system/backup.timer
```

Service unit:

```ini
[Unit]
Description=Run backup job

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
```

Timer unit:

```ini
[Unit]
Description=Run backup job daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now backup.timer
systemctl list-timers
systemctl cat backup.service
systemctl status backup.timer
journalctl -u backup.service
```

## 7. ShellCheck

`shellcheck` giúp phát hiện lỗi quote biến, command substitution, test condition và portability.

```bash
shellcheck script.sh
```

Ví dụ lỗi ShellCheck thường bắt được:

- Dùng biến không quote.
- So sánh string/number sai cú pháp.
- Command substitution không an toàn.
- Biến được gán nhưng không dùng.

## 8. Lock Chống Chạy Trùng

Cron hoặc timer có thể chạy trùng nếu job trước chưa xong. Dùng `flock` để tránh overlap.

Chạy trực tiếp:

```bash
flock -n /var/lock/backup.lock /usr/local/bin/backup.sh
```

Trong script:

```bash
exec 9>/var/lock/myjob.lock
flock -n 9 || exit 0
```

## 9. Script Placement

Khuyến nghị:

| Path | Use case |
| --- | --- |
| `/usr/local/bin/` | Script admin local |
| `/opt/<app>/bin/` | Script thuộc app |
| `/etc/cron.d/` | Lịch system cron |
| `/etc/systemd/system/` | Custom service/timer |

Set permission:

```bash
sudo install -m 0755 script.sh /usr/local/bin/script-name
```

## 10. Safety Checklist

- Có `usage` rõ nếu script cần argument.
- Quote biến.
- Không hardcode secret.
- Log ra file hoặc journal.
- Có dry-run cho thao tác nguy hiểm nếu có thể.
- Có backup trước khi sửa file quan trọng.
- Test trên lab/staging trước production.

Script mẫu dài nằm ở [Sysadmin Scripts Collection](./08-sysadmin-scripts-collection.md).
