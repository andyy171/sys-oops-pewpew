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

Khi test script trong thư mục hiện tại, chạy bằng `./script.sh`; shell không tự tìm command trong current directory nếu `.` không nằm trong `PATH`. Không thêm `.` hoặc thư mục user-writable vào đầu `PATH` của account có quyền cao; nếu script cần dùng chung, cài vào path được kiểm soát như `/usr/local/bin`.

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

So sánh đúng kiểu dữ liệu:

```bash
name="${1:-}"
count="${2:-0}"

if [[ "$name" == "admin" ]]; then
  echo "reserved name" >&2
fi

if [[ "$count" =~ ^[0-9]+$ ]] && (( count > 10 )); then
  echo "large batch"
fi
```

Trong Bash, `==` trong `[[ ... ]]` là so sánh chuỗi; so sánh số nên dùng arithmetic `(( ... ))` sau khi đã validate input là số. Với script cần portable POSIX `sh`, dùng test operator như `-eq`, `-gt`, nhưng vẫn phải quote biến và xử lý giá trị rỗng.

## 5. Script Interface: Arguments, Options Và `read`

Script vận hành nên có interface rõ: required arguments, options, default value, usage và exit code.

Positional parameters:

```bash
if [[ $# -lt 1 ]]; then
  echo "Usage: $(basename "$0") <target>" >&2
  exit 2
fi

target="$1"
```

Khi loop qua argument, dùng `"$@"` thay vì `$*` để giữ từng argument riêng:

```bash
for arg in "$@"; do
  printf 'arg=%s\n' "$arg"
done
```

Dạng `"$@"` giữ nguyên từng argument, kể cả khi có khoảng trắng. Tránh loop trên `$@` hoặc `$*` không quote vì shell sẽ word-splitting và glob expansion trước khi script xử lý.

Với options, ưu tiên `getopts` cho Bash script:

```bash
verbose=0
force=0
input_file=""

usage() {
  echo "Usage: $(basename "$0") [-v] [-y] -f INPUT" >&2
}

while getopts ":vyf:h" opt; do
  case "$opt" in
    v) verbose=1 ;;
    y) force=1 ;;
    f) input_file="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) usage; exit 2 ;;
  esac
done

shift "$((OPTIND - 1))"
```

Interactive input bằng `read` chỉ nên dùng khi script thật sự chạy bởi người dùng:

```bash
read -r -p "Input file: " input_file
read -r -s -p "Password: " password
echo
```

Khi script không được phép chờ vô hạn, thêm timeout và xử lý exit status của `read`:

```bash
if read -r -t 10 -p "Confirm action [y/N]: " answer; then
  case "$answer" in
    y|Y) confirmed=1 ;;
    *) confirmed=0 ;;
  esac
else
  echo "timeout waiting for confirmation" >&2
  exit 2
fi
```

Khi chỉ cần một ký tự, dùng `-n 1` nhưng vẫn phải có default an toàn:

```bash
read -r -n 1 -p "Continue [y/N]? " answer
echo
case "$answer" in
  y|Y) ;;
  *) exit 2 ;;
esac
```

Guardrails:

- Không echo password/token ra màn hình hoặc log.
- Với automation/cron/systemd, tránh prompt vô hạn; nếu cần thì dùng `read -t` và default fail-closed.
- Action có rủi ro overwrite/delete nên có `--dry-run`, `--yes` hoặc confirm rõ.
- Dùng `--` để tách options khỏi positional arguments khi tự parse thủ công.
- Nếu không truyền tên biến cho `read`, Bash ghi vào biến `REPLY`; trong script production nên ưu tiên biến đặt tên rõ để dễ audit.

## 6. Conditions, `case` Và File Tests

Trong Bash, `if` kiểm tra exit status:

```bash
if systemctl is-active --quiet nginx; then
  echo "running"
else
  echo "not running"
fi
```

Nhóm file test rất quan trọng cho script admin:

```bash
[[ -e "$path" ]]   # exists
[[ -f "$path" ]]   # regular file
[[ -d "$path" ]]   # directory
[[ -r "$path" ]]   # readable
[[ -w "$path" ]]   # writable
[[ -x "$path" ]]   # executable
[[ -s "$path" ]]   # non-empty
```

`case` phù hợp khi script nhận action/subcommand:

```bash
case "${1:-}" in
  start|stop|restart|status)
    systemctl "$1" nginx
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status}" >&2
    exit 2
    ;;
esac
```

Guardrails:

- Quote biến chứa path: `"$path"`.
- Check tồn tại và loại object trước khi `cd`, copy, move, chmod hoặc xóa.
- Với so sánh file `-nt`/`-ot`, kiểm tra cả hai file tồn tại trước để tránh kết quả gây hiểu nhầm.
- Trong `[[ ]]`, pattern matching như `[[ "$env" == prod-* ]]` tiện nhưng là Bash-specific, không portable sang POSIX `sh`.

## 7. Loops Và Batch Guardrails

Chọn loop theo dữ liệu:

| Nhu cầu | Pattern |
|---|---|
| list có sẵn | `for item in "${items[@]}"` |
| counter | `for ((i=0; i<max; i++))` |
| đọc file theo dòng | `while IFS= read -r line` |
| chờ điều kiện | `until command; do sleep 5; done` |

Đọc file line-by-line an toàn:

```bash
while IFS= read -r line; do
  printf '%s\n' "$line"
done < "$input_file"
```

Loop qua file:

```bash
for file in /var/log/*.log; do
  [[ -f "$file" ]] || continue
  echo "$file"
done
```

Guardrails:

- Tránh parse CSV thật bằng `IFS=,` nếu có quote/escape phức tạp.
- Nếu đổi `IFS`, lưu và restore hoặc giới hạn trong subshell/block nhỏ.
- Với `while`, đảm bảo biến điều kiện được update trước mọi nhánh `continue`.
- Nested loop có thể nhân số call rất lớn; tính trước số lần gọi SSH/API/kubectl.
- Với batch destructive, thêm dry-run và in danh sách target trước khi chạy thật.

Ví dụ backup file theo pattern trong một thư mục, có validation và tránh ghi đè:

```bash
dir="${1:-}"

if [[ ! -d "$dir" ]]; then
  echo "usage: $0 <directory>" >&2
  exit 2
fi

shopt -s nullglob
for file in "$dir"/*.txt; do
  [[ -f "$file" ]] || continue
  cp -n -- "$file" "$file.bak"
done
```

`cp -n --` giúp tránh overwrite file backup đã có và ngăn filename bắt đầu bằng `-` bị hiểu nhầm là option. Nếu backup là operation quan trọng, thêm bước verify checksum hoặc restore thử trên mẫu nhỏ trước khi chạy hàng loạt.

## 8. Functions Và Reusable Helpers

Function nên dùng để gom logic có tên, giảm lặp và chuẩn hóa error handling:

```bash
log() {
  printf '%s [%s] %s\n' "$(date -Is)" "$$" "$*" >&2
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    log "missing command: $cmd"
    return 1
  fi
}
```

Quy ước:

- `return` dùng cho status `0..255`, không dùng để trả data.
- Muốn trả data, ghi ra `stdout` và caller capture bằng command substitution.
- Log/debug nên ghi ra `stderr` để không lẫn với data output.
- Biến nội bộ function nên khai báo `local`.
- Function cần được define hoặc source trước khi gọi.
- `$?` chỉ là exit status của command/function vừa chạy ngay trước đó; nếu cần dùng sau nhiều bước, lưu vào biến `rc=$?` ngay lập tức.

Tách helper dùng chung thành library:

```bash
LIB_FILE="/opt/myapp/lib/common.sh"
if [[ ! -r "$LIB_FILE" ]]; then
  echo "Cannot read library: $LIB_FILE" >&2
  exit 1
fi

. "$LIB_FILE"
```

Không phụ thuộc vào function trong `.bashrc` cho script production, vì cron/systemd/non-interactive shell thường không load cùng môi trường interactive.

## 9. Signals, Background Jobs Và Priority

Script cũng là Linux process: có PID, parent, file descriptors và có thể nhận signal.

Signals cần nhớ:

| Signal | Ý nghĩa |
|---|---|
| `SIGINT` | thường do `Ctrl+C` |
| `SIGTERM` | yêu cầu terminate có kiểm soát |
| `SIGHUP` | terminal/session đóng |
| `SIGKILL` | kill cưỡng bức, không trap được |
| `SIGTSTP` | stop do `Ctrl+Z` |

Cleanup bằng `trap`:

```bash
tmpdir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmpdir"
}
trap cleanup EXIT
trap 'echo "interrupted" >&2; exit 130' SIGINT
trap 'echo "terminated" >&2; exit 143' SIGTERM
```

`rm -rf "$tmpdir"` chỉ an toàn khi `tmpdir` được tạo bởi `mktemp -d`, được quote, và không rỗng. Không dùng pattern này với path tính toán từ input nếu chưa validate.

Background job:

```bash
nohup ./long-script.sh > long-script.log 2>&1 &
jobs -l
```

`&` chỉ đưa process ra background của shell hiện tại, không tự detach khỏi terminal. Muốn chạy bền hơn nên dùng `nohup`, `systemd-run`, service hoặc timer tùy use case.

`Ctrl+C` gửi `SIGINT` cho foreground job, còn `Ctrl+Z` gửi `SIGTSTP` để stop job nhưng vẫn giữ process trong memory. Dùng `jobs -l` để xem job number và PID, `bg %<job>` để chạy tiếp ở background, `fg %<job>` để kéo về foreground.

`nohup` mặc định ghi output vào `nohup.out` trong thư mục hiện tại nếu không redirect rõ. Với production, luôn đặt log path cụ thể để tránh nhiều job append chung vào một file khó audit:

```bash
nohup /usr/local/bin/reindex.sh >> /var/log/reindex.log 2>&1 &
```

Priority:

```bash
nice -n 10 ./heavy-script.sh > heavy.log 2>&1 &
renice -n 10 -p <PID>
```

Guardrails:

- Ưu tiên `kill <PID>` (`SIGTERM`) trước `kill -9 <PID>`.
- `kill -9` có thể làm mất cleanup, lock file hoặc state tạm.
- Trước khi kill job, xác nhận PID, command line, user và working directory bằng `ps -fp <PID>` hoặc `ps -o pid,ppid,user,stat,lstart,cmd -p <PID>`.
- Background script phải redirect output; output rơi vào terminal làm khó audit.
- Job quan trọng nên chạy qua systemd service/timer để có journal, restart policy và dependency rõ hơn shell job control.

## 10. One-shot Và Periodic Scheduling

`at` dùng cho job chạy một lần trong tương lai:

```bash
at -M -f /opt/scripts/cleanup.sh now + 10 minutes
atq
atrm <job_id>
```

`at` thường chạy qua daemon `atd` và queue trong `/var/spool/at`. Output của job có thể được gửi qua local mail nếu không redirect; trên server không cấu hình mail nội bộ, output có thể bị bỏ sót.

`cron` dùng cho recurring job. `anacron` giúp không bỏ lỡ daily/weekly/monthly job trên máy không chạy 24/7.

Với job cần audit tốt, dependency rõ, retry và log tập trung, ưu tiên systemd timer thay vì cron thuần.

Guardrails:

- Kiểm tra daemon tồn tại và đang chạy trước khi tin job sẽ được kích hoạt: `systemctl status atd` hoặc package/service tương ứng theo distro.
- Dùng `atq` trước khi submit nhiều job và dùng `atrm <job_id>` để rollback job chưa chạy.
- Với one-shot job có tác động dữ liệu, redirect `stdout`/`stderr` vào log path rõ và ghi lại command/job id trong ticket hoặc change record.

## 11. cron

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
- Cron không tự đọc `.bashrc` như terminal interactive; set `PATH`, `SHELL`, `MAILTO` hoặc biến ứng dụng trực tiếp trong crontab khi cần.
- `%` trong command crontab có ý nghĩa đặc biệt với stdin của cron trên nhiều implementation; escape hoặc đưa logic vào script riêng nếu command phức tạp.

Ví dụ:

```text
*/10 * * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
```

## 12. systemd Timer

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

## 13. ShellCheck

`shellcheck` giúp phát hiện lỗi quote biến, command substitution, test condition và portability.

```bash
shellcheck script.sh
```

Ví dụ lỗi ShellCheck thường bắt được:

- Dùng biến không quote.
- So sánh string/number sai cú pháp.
- Command substitution không an toàn.
- Biến được gán nhưng không dùng.

## 14. Lock Chống Chạy Trùng

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

## 15. Script Placement

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

## 16. Safety Checklist

- Có `usage` rõ nếu script cần argument.
- Quote biến.
- Không hardcode secret.
- Log ra file hoặc journal.
- Có dry-run cho thao tác nguy hiểm nếu có thể.
- Có backup trước khi sửa file quan trọng.
- Test trên lab/staging trước production.

Script mẫu dài nằm ở [Sysadmin Scripts Collection](./08-sysadmin-scripts-collection.md).
