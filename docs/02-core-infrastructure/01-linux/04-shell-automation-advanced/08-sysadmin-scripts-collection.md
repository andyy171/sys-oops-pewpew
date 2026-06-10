# Sysadmin Scripts Collection

File này chứa script mẫu để tham khảo. Trước khi dùng trong production, cần review, test trên lab, thêm logging/alerting phù hợp và bỏ hardcode secret.

## 1. System Info Snapshot

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "== Host =="
hostnamectl

echo "== Kernel =="
uname -a

echo "== CPU =="
lscpu

echo "== Memory =="
free -h

echo "== Disk =="
lsblk -f
df -h

echo "== Network =="
ip -br addr
ip route

echo "== Failed services =="
systemctl --failed --no-pager
```

## 2. Common Helpers

Logging function:

```bash
log() {
  printf '%s [%s] %s\n' "$(date -Is)" "$$" "$*"
}
```

Lock chống chạy trùng:

```bash
exec 9>/var/lock/myjob.lock
flock -n 9 || exit 0
```

Kiểm tra script:

```bash
shellcheck script.sh
```

## 3. Service Health Check

```bash
#!/usr/bin/env bash
set -euo pipefail

services=("sshd" "nginx")

for service in "${services[@]}"; do
  if systemctl is-active --quiet "$service"; then
    echo "OK: $service"
  else
    echo "FAILED: $service" >&2
    systemctl status "$service" --no-pager || true
  fi
done
```

## 4. Disk Usage Report

```bash
#!/usr/bin/env bash
set -euo pipefail

threshold="${1:-80}"

df -P -h | awk -v threshold="$threshold" '
NR > 1 {
  usage=$5
  gsub("%", "", usage)
  if (usage >= threshold) {
    print "WARN:", $6, "is", $5, "full"
  }
}'
```

## 5. Network Connectivity Check

```bash
#!/usr/bin/env bash
set -euo pipefail

targets=("8.8.8.8" "example.com")

for target in "${targets[@]}"; do
  echo "== $target =="
  ping -c 3 "$target" || true
  getent hosts "$target" || true
done
```

## 6. Log Error Summary

```bash
#!/usr/bin/env bash
set -euo pipefail

log_file="${1:-/var/log/syslog}"

if [[ ! -r "$log_file" ]]; then
  echo "Cannot read $log_file" >&2
  exit 1
fi

grep -Ein "error|failed|denied|timeout" "$log_file" | tail -100
```

## 7. Backup Directory With rsync

```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <source-dir> <destination-dir>" >&2
  exit 2
fi

src="$1"
dst="$2"

if [[ ! -d "$src" ]]; then
  echo "Source is not a directory: $src" >&2
  exit 1
fi

mkdir -p "$dst"
rsync -aHAX --numeric-ids --dry-run --info=progress2 "$src"/ "$dst"/

echo "Dry-run completed. Remove --dry-run after review."
```

Chạy thử với `--dry-run` trước khi backup/restore dữ liệu quan trọng.

## 8. User Audit Snapshot

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "== UID 0 accounts =="
awk -F: '$3 == 0 {print $1}' /etc/passwd

echo "== Users with login shell =="
awk -F: '$7 !~ /(nologin|false)$/ {print $1, $7}' /etc/passwd

echo "== sudo group =="
getent group sudo || true
getent group wheel || true

echo "== Human users =="
awk -F: '$3 >= 1000 && $7 !~ /(nologin|false)$/ {print $1, $3, $7}' /etc/passwd
```

## 9. Safety Notes

- Không chạy script tải từ note này bằng root nếu chưa đọc.
- Thêm `--dry-run` cho script xóa/move/chmod nếu mở rộng.
- Ghi log ra file hoặc journal khi chạy định kỳ.
- Dùng systemd timer cho job quan trọng cần audit tốt hơn cron.
