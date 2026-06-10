# Bash System Check, Log And Cron Labs

## Overview

Note này chuyển hóa nhóm lab Bash cũ trong `_inbox`: biến, điều kiện, vòng lặp, function, xử lý file, phân tích log và cron job. Đây là lớp thực hành bổ sung cho các note Bash canonical, tập trung vào automation nhỏ nhưng dùng được trong vận hành Linux/DevOps.

## Mental Model

Bash mạnh nhất khi dùng để nối các command Linux thành workflow ngắn:

```text
collect data -> filter/parse -> decide -> log/report -> schedule
```

Nếu logic bắt đầu phức tạp, cần nhiều cấu trúc dữ liệu hoặc xử lý lỗi sâu, nên cân nhắc Python. Nhưng với task kiểm tra disk, CPU, log, service, cron và pipeline glue, Bash vẫn rất thực tế.

## Lab 1: System Check Cơ Bản

Script kiểm tra hostname, disk và memory:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Host: $(hostname)"
echo "Time: $(date -Is)"
df -h /
free -h
```

Chạy:

```bash
chmod +x check-system.sh
./check-system.sh
```

Điểm cần nhớ:

- dùng `#!/usr/bin/env bash` để chọn Bash qua `PATH`;
- dùng `set -euo pipefail` cho script nghiêm túc hơn;
- dùng đường dẫn tuyệt đối khi script chạy qua cron.

## Lab 2: Điều Kiện Cảnh Báo Disk

```bash
#!/usr/bin/env bash
set -euo pipefail

threshold="${1:-80}"
usage="$(df -h / | awk 'NR==2 {gsub("%","",$5); print $5}')"

if [ "$usage" -gt "$threshold" ]; then
  echo "WARN disk usage ${usage}% > ${threshold}%"
else
  echo "OK disk usage ${usage}%"
fi
```

Điểm hay lỗi:

- không đặt khoảng trắng quanh `=`;
- luôn quote biến: `"$usage"`;
- kiểm tra input nếu script nhận tham số từ người dùng hoặc CI variable.

## Lab 3: Function Và Logging

```bash
#!/usr/bin/env bash
set -euo pipefail

log_file="/var/log/example-system-check.log"

log() {
  local level="$1"
  local message="$2"
  echo "$(date -Is) [$level] $message" | sudo tee -a "$log_file" >/dev/null
}

check_disk() {
  local usage
  usage="$(df -h / | awk 'NR==2 {gsub("%","",$5); print $5}')"
  if [ "$usage" -gt 80 ]; then
    log "WARN" "disk usage ${usage}%"
  else
    log "INFO" "disk usage ${usage}%"
  fi
}

check_disk
```

Best practice:

- biến trong function nên khai báo `local`;
- log có timestamp;
- không ghi secret vào log;
- dùng exit code rõ ràng nếu script được pipeline gọi.

## Lab 4: Vòng Lặp Kiểm Tra Nhiều Host

```bash
#!/usr/bin/env bash
set -euo pipefail

hosts=("10.0.0.10" "10.0.0.11" "10.0.0.12")

for host in "${hosts[@]}"; do
  if ping -c 1 -W 2 "$host" >/dev/null; then
    echo "OK $host reachable"
  else
    echo "WARN $host unreachable"
  fi
done
```

Không dùng IP thật của production trong note/lab. Khi áp dụng thực tế, thay bằng inventory hoặc DNS nội bộ đã được kiểm soát.

## Lab 5: Phân Tích Log Bằng grep, awk, sed

Ví dụ tìm lỗi HTTP 500 trong access log:

```bash
grep ' 500 ' /var/log/nginx/access.log | tail -n 20
```

Đếm IP gọi lỗi nhiều nhất:

```bash
awk '$9 == 500 {print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head
```

Thử thay text nhưng chưa ghi file:

```bash
sed 's/ERROR/WARN/g' app.log | head
```

Chỉ dùng `sed -i` sau khi đã kiểm tra output. Với file production quan trọng, backup trước hoặc dùng pipeline review.

## Lab 6: Cron Job

Cron format:

```text
* * * * * /absolute/path/to/script.sh
```

Ví dụ chạy mỗi giờ và ghi log:

```text
0 * * * * /opt/scripts/check-system.sh >> /var/log/check-system.log 2>&1
```

Checklist khi cron không chạy:

```bash
crontab -l
systemctl status cron || systemctl status crond
journalctl -u cron --since "1 hour ago" --no-pager
ls -l /opt/scripts/check-system.sh
```

Lỗi phổ biến:

- dùng path tương đối;
- thiếu quyền execute;
- environment trong cron khác shell interactive;
- command cần `PATH` nhưng cron không có;
- script ghi log vào path không có quyền.

## Related Pages

- [Shell Basic Commands, Pipe And Redirection](./01-shell-basic-commands-pipe-redirection.md)
- [Text Processing: grep, sed, awk, regex và vim](./02-text-processing-grep-sed-awk-regex-vim.md)
- [Bash Scripting, cron và systemd timer](./03-bash-scripting-cron-systemd-timer.md)
- [Linux Labs và Practices](./07-labs-practices.md)
