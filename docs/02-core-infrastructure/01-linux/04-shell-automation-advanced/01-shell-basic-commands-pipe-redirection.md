# Shell, Basic Commands, Pipe và Redirection

## 1. Mục Tiêu

File này giúp nắm các thao tác CLI nền tảng khi làm việc trên Linux server: di chuyển thư mục, xem file, tìm file, pipe, redirection, exit code và các lưu ý an toàn khi chạy lệnh.

## 2. Khi Dùng Trong Thực Tế

- Làm việc qua SSH trên server.
- Kiểm tra file, log, dung lượng và trạng thái nhanh.
- Chain command khi troubleshoot.
- Ghi output ra file hoặc bỏ stdout/stderr có kiểm soát.

## 3. Shell Overview

Shell là command interpreter giữa user và hệ điều hành. Shell phổ biến nhất trên Linux server là `bash`, ngoài ra có `sh`, `zsh`, `fish`.

Không nên giả định mọi host đều chạy cùng shell. Trên nhiều distro, `/bin/sh` có thể trỏ tới `dash`, `bash` ở POSIX mode hoặc shell tối giản khác; script gọi bằng `sh script.sh` có thể fail nếu bên trong dùng Bash-only feature như array, `[[ ... ]]`, brace expansion phức tạp hoặc process substitution. Với automation production, shebang phải nói rõ runtime thật sự cần dùng:

```bash
#!/usr/bin/env bash
```

Nếu script chỉ cần POSIX shell, viết theo POSIX và test bằng `/bin/sh`. Nếu cần Bash feature, dùng shebang Bash và tránh chạy qua `sh`. Các shell như `zsh`, `ksh`, `tcsh` hữu ích trong môi trường interactive hoặc legacy riêng, nhưng không nên dùng làm runtime mặc định cho runbook nếu fleet không chuẩn hóa shell đó.

Kiểm tra shell:

```bash
echo "$SHELL"
cat /etc/shells
ps -p $$ -o comm=
```

### Quoting Và Shell Metacharacter

Shell xử lý metacharacter trước khi command thật nhận argument. Vì vậy cùng một chuỗi text có thể trở thành biến, glob, pipe, redirection hoặc command separator nếu quote sai. Các ký tự cần chú ý gồm `$`, `*`, `?`, `[ ]`, `;`, `&`, `|`, `<`, `>`, `(`, `)`, backslash và quote.

```bash
echo "cost is \$1.00"
printf '%s\n' '*.log'
grep 'error|failed' app.log
grep -E 'error|failed' app.log
```

Quy tắc thực dụng:

- Dùng single quote khi muốn giữ literal và không cần expand biến.
- Dùng double quote khi cần expand biến nhưng vẫn muốn giữ khoảng trắng trong một argument.
- Dùng backslash cho một ký tự đặc biệt đơn lẻ.
- Với regex, nhớ phân biệt shell glob với regex của tool. Quote pattern để shell không expand trước khi `grep`, `sed` hoặc `awk` chạy.

Trên console local hoặc VM console, Linux có thể cung cấp nhiều **virtual console**. Người dùng có thể chuyển giữa các TTY bằng tổ hợp như `Ctrl+Alt+F2`, `Ctrl+Alt+F3` tùy distro/desktop. Trên server headless, hầu hết thao tác hằng ngày đi qua SSH, nhưng hiểu virtual console vẫn hữu ích khi debug boot, network hoặc display manager.

Prompt shell thường cho biết user, host, working directory và quyền hiện tại:

```text
user@host:/path$
root@host:/path#
```

Ký tự `$` thường là user thường; `#` thường là root. Đừng chỉ nhìn prompt để kết luận quyền thật, vì prompt có thể tùy biến bằng `PS1`; khi thao tác rủi ro, kiểm tra bằng `id`, `whoami`, `hostnamectl` và `pwd`.

## 4. Interactive, Non-interactive, Login và Non-login Shell

| Loại | Mô tả |
| --- | --- |
| Interactive shell | User gõ lệnh trực tiếp |
| Non-interactive shell | Chạy script |
| Login shell | Shell đầu tiên sau login |
| Non-login shell | Shell mở thêm trong session |

Startup files thường gặp:

| File | Vai trò |
| --- | --- |
| `/etc/profile` | Global login shell |
| `/etc/profile.d/*.sh` | Hook thường được `/etc/profile` gọi để package hoặc team thêm biến môi trường |
| `~/.bash_profile`, `~/.profile` | User login shell |
| `~/.bashrc` | User interactive non-login shell |
| `/etc/bash.bashrc` hoặc `/etc/bashrc` | Global bashrc tùy distro |

Với Bash login shell, thứ tự thực tế thường là `/etc/profile`, sau đó Bash tìm file user đầu tiên tồn tại trong nhóm `~/.bash_profile`, `~/.bash_login`, `~/.profile`. Interactive non-login shell thường đọc `~/.bashrc`, nhưng không đọc `/etc/profile`. Non-interactive shell dùng để chạy script thường không load các file trên; nếu biến `BASH_ENV` được set, Bash sẽ đọc file mà biến này trỏ tới trước khi chạy script.

Guardrails:

- Không đặt logic production bắt buộc chỉ trong `.bashrc`; cron, systemd và script non-interactive thường không có môi trường giống terminal của user.
- Khi debug khác biệt giữa SSH interactive và cron/systemd, in ra `env`, `id`, `pwd`, `umask`, `PATH`, `SHELL` và command lookup bằng `type -a <command>`.
- `BASH_ENV` có thể làm script non-interactive chạy thêm code ngoài mong đợi. Chỉ dùng khi được kiểm soát rõ owner, permission và nội dung file.

## 5. Manual Pages Và Command Discovery

Manual page là nguồn tra cứu offline quan trọng trên Linux server:

```bash
man ls
man 5 passwd
whatis passwd
apropos "copy file"
man -k network
info coreutils
ls /usr/share/doc/
type cd
help cd
```

Man page thường có các phần như `NAME`, `SYNOPSIS`, `DESCRIPTION`, `OPTIONS`, `EXAMPLES`, `FILES`, `SEE ALSO`. Khi đọc `SYNOPSIS`, dấu `[]` thường biểu thị phần tùy chọn; dấu `...` biểu thị có thể lặp lại nhiều argument.

Một số section hay gặp:

| Section | Nội dung |
| --- | --- |
| `1` | User command |
| `5` | File format/config format |
| `8` | System administration command |

Ví dụ `passwd` có thể là command đổi mật khẩu hoặc file `/etc/passwd`, nên dùng section để tránh nhầm:

```bash
man 1 passwd
man 5 passwd
```

Khi command là shell builtin như `cd`, man page riêng có thể không tồn tại hoặc không phải nguồn chính xác nhất. Dùng `type <command>` để biết shell sẽ chạy builtin, alias, function hay executable ngoài; dùng `help <builtin>` để xem trợ giúp của builtin trong `bash`.

Ngoài `man`, nhiều package còn có tài liệu trong `/usr/share/doc/<package>/`, changelog, README hoặc ví dụ cấu hình. `info` hữu ích với một số GNU tool vì tài liệu có thể chi tiết hơn man page, nhưng trong vận hành server thường bắt đầu bằng `man`, `--help`, `type`, `whatis` và `apropos`.

## 6. Basic Navigation và File Commands

```bash
pwd
ls -lah
cd /var/log
mkdir -p /tmp/demo
touch file.txt
cp file.txt file.bak
mv file.bak file.old
rm file.old
rmdir /tmp/demo
```

An toàn hơn khi xóa:

```bash
rm -i file.txt
rm -rI directory/
```

Phân biệt path:

| Kiểu path | Ví dụ | Ghi chú |
| --- | --- | --- |
| Absolute path | `/var/log/messages` | Bắt đầu từ root `/`, ít phụ thuộc working directory |
| Relative path | `../app/config.yml` | Tính từ working directory hiện tại |
| Home shortcut | `~/.bashrc` | Trỏ về home của user hiện tại |

Tên file Linux phân biệt hoa/thường. Filename có space hoặc ký tự đặc biệt cần quote:

```bash
ls -l "file with space.txt"
rm -i -- "-strange-name"
```

## 7. Inspect Files và Directories

```bash
file /bin/bash
stat /etc/passwd
du -sh /var/log
df -h
tree -L 2 2>/dev/null
```

`ls -l` trên directory hiển thị metadata của chính directory entry, không phải tổng dung lượng toàn bộ cây con. Khi cần biết directory đang chiếm bao nhiêu disk, dùng `du`:

```bash
du -sh /var/log
du -xh --max-depth=1 /var | sort -h
```

Tìm file:

```bash
find /var/log -type f -name "*.log"
find /var/log -type f -mtime -7
find /var/log -type f -size +100M
locate nginx.conf
locate -b '\nginx.conf'
```

`locate` đọc từ database index nên rất nhanh nhưng có thể stale nếu file vừa tạo/xóa hoặc `updatedb` chưa chạy. Pattern của `locate` có thể match rộng hơn dự kiến; dùng `-b` để chỉ match basename và quote pattern nếu cần tìm đúng tên file. `find` chậm hơn nhưng quét trạng thái filesystem thật tại thời điểm chạy.

Linux định danh file bằng inode trong filesystem, không phải chỉ bằng filename. Filename là directory entry trỏ tới inode. Vì vậy hard link có thể tạo nhiều tên cùng trỏ tới một inode, còn symbolic link là file riêng trỏ tới path khác.

```bash
ls -li file.txt
ln file.txt hard-link.txt
ln -s file.txt symlink.txt
stat file.txt hard-link.txt symlink.txt
```

| Loại link | Đặc điểm |
| --- | --- |
| Hard link | Cùng inode, thường không cross filesystem, không dùng cho directory thông thường |
| Symbolic link | File riêng chứa path đích, có thể trỏ cross filesystem, có thể bị broken nếu target đổi/xóa |

## 8. Archive và Compression

```bash
tar -czf etc-backup.tar.gz /etc
tar -tzf etc-backup.tar.gz | head
tar -xzf etc-backup.tar.gz -C /tmp/restore

gzip file.log
gunzip file.log.gz
zip -r archive.zip directory/
unzip archive.zip
```

Xem nội dung file nén mà chưa bung ra:

```bash
zcat app.log.gz | head
bzcat app.log.bz2 | head
xzcat app.log.xz | head
file unknown-archive
```

Trước khi extract archive lạ, xem nội dung trước để tránh ghi đè file không mong muốn:

```bash
tar -tf archive.tar
tar -tzf archive.tar.gz | head
unzip -l archive.zip
```

Trong production, xem archive là artifact cần kiểm soát chứ không phải backup hoàn chỉnh nếu chưa có checksum, metadata, vị trí lưu độc lập và restore test. Khi restore hoặc nhận archive từ nguồn khác, ưu tiên extract vào thư mục tạm rồi kiểm tra:

```bash
mkdir -p /tmp/restore-check
tar -xzf app-release.tar.gz -C /tmp/restore-check
```

Tránh dùng hoặc extract archive có absolute path nếu chưa review kỹ. Với `tar`, option như `-P` giữ đường dẫn tuyệt đối và có thể ghi đè file hệ thống khi chạy bằng quyền cao; mặc định nên để archive dùng relative path. Với nén dữ liệu, `gzip`, `bzip2`, `xz` thường đánh đổi CPU/thời gian để lấy dung lượng nhỏ hơn; không nên chạy mức nén quá nặng trên host đang xử lý sự cố nếu I/O và CPU đang căng.

## 9. Globbing, Brace Expansion và History

Globbing:

```bash
ls *.log
ls access-2026-05-*.log
rm -i *.tmp
printf '%s\n' ./*.tmp
```

Globbing là shell expansion, không phải regex. Trên Linux, match tên file thường phân biệt hoa/thường; bracket range như `[a-z]` có thể chịu ảnh hưởng locale/collation. Khi cần kết quả nhất quán trong script hoặc runbook, quote pattern truyền cho tool regex, hoặc test danh sách target bằng `printf '%s\n' pattern`/`find ... -print` trước khi chạy lệnh có tác động.

Brace expansion:

```bash
cp file{,.bak}
mkdir -p /data/{app,log,tmp}
mv app.conf{,.old}
```

History và command recall:

```bash
history
!!
!123
history 20
history -c
```

Trong shell interactive, `Ctrl+r` giúp search lại command cũ.

Di chuyển nhanh:

```bash
cd -
pushd /var/log
popd
```

Command completion bằng `Tab` giúp giảm gõ sai tên lệnh, path, option hoặc service name. Nếu completion không hoạt động như mong muốn, kiểm tra package completion của shell/distro và nhớ rằng completion không thay thế việc hiểu option.

## 10. Pipe

Pipe đưa stdout của command trước vào stdin của command sau.

```bash
ps aux | grep nginx
journalctl -u nginx | tail -100
cat access.log | awk '{print $1}' | sort | uniq -c | sort -nr | head
```

Khi command có thể đọc file trực tiếp, không cần `cat`:

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
```

## 11. Redirection

| Cú pháp | Ý nghĩa |
| --- | --- |
| `>` | Ghi stdout, overwrite |
| `>>` | Ghi stdout, append |
| `2>` | Ghi stderr |
| `&>` | Ghi stdout + stderr trong bash |
| `<` | Đọc stdin từ file |
| `/dev/null` | Bỏ output |

Ví dụ:

```bash
command > output.txt
command >> output.txt
command 2> error.log
command > output.txt 2> error.log
command &> all.log
command >/dev/null 2>&1
```

## 12. `tee`

`tee` vừa hiển thị output vừa ghi file.

```bash
echo "hello" | tee output.txt
echo "more" | tee -a output.txt
echo "net.ipv4.ip_forward = 1" | sudo tee /etc/sysctl.d/99-ip-forward.conf
```

`sudo echo ... > /root/file` thường fail vì redirection chạy bởi shell hiện tại; dùng `sudo tee`.

## 13. File Descriptor Và Logging Luồng I/O

Mỗi process Linux có ba file descriptor chuẩn:

| FD | Stream | Dùng cho |
|---:|---|---|
| `0` | `STDIN` | input, thường là keyboard hoặc file |
| `1` | `STDOUT` | output bình thường |
| `2` | `STDERR` | lỗi, warning, diagnostic |

Tách `STDOUT` và `STDERR` giúp script dễ debug hơn:

```bash
command > output.log 2> error.log
command >> combined.log 2>&1
```

Trong script, nên gửi message lỗi tự viết vào `stderr`:

```bash
usage() {
  echo "Usage: $(basename "$0") <file>" >&2
}
```

Redirect toàn bộ output từ một điểm trở đi bằng `exec`:

```bash
LOG_FILE="./script.log"
exec >> "$LOG_FILE" 2>&1
echo "[$(date '+%F %T')] started"
```

Có thể tự mở descriptor phụ khi cần tách log:

```bash
exec 3>>info.log
exec 4>>audit.log

echo "normal info" >&3
echo "audit event" >&4

exec 3>&-
exec 4>&-
```

Nếu cần đổi `STDOUT` tạm thời rồi khôi phục:

```bash
exec 3>&1
exec > output.log
echo "goes to file"
exec 1>&3
echo "back to terminal"
exec 3>&-
```

Guardrails:

- Dùng `>>` cho log chạy định kỳ để tránh ghi đè.
- Không redirect tất cả vào `/dev/null` khi còn cần evidence điều tra.
- Với cron/background job, luôn log rõ `stdout` và `stderr`.
- Đóng FD tự mở khi không dùng nữa để tránh leak descriptor trong script dài.

## 14. Heredoc, Command Substitution Và Arithmetic

`heredoc` dùng để cấp nhiều dòng input cho command:

```bash
cat > config.txt <<'CONFIG'
server=app01
port=8080
mode=production
CONFIG
```

Dùng delimiter có quote như `<<'CONFIG'` khi muốn giữ nội dung literal, không expand biến trong heredoc.

Command substitution lấy output command gán vào biến:

```bash
today="$(date +%F)"
log_file="job-${today}.log"
```

Ưu tiên `$()` thay vì backtick vì dễ đọc và dễ lồng nhau hơn. Lưu ý command substitution chạy trong subshell; thay đổi directory hoặc biến bên trong không tự quay lại shell cha.

Bash arithmetic mặc định chỉ xử lý integer:

```bash
total=$(( used + free ))
percent=$(( used * 100 / total ))
```

Khi cần số thập phân, dùng `bc` hoặc `awk`:

```bash
ratio="$(echo "scale=2; $used / $total * 100" | bc)"
```

## 15. Exit Status Và Command Chaining

Mỗi command trả exit status. Quy ước chung:

| Exit code | Ý nghĩa thường gặp |
|---:|---|
| `0` | success |
| `1` | lỗi chung |
| `2` | dùng sai command/script |
| `126` | command tồn tại nhưng không execute được |
| `127` | command not found |
| `128+n` | process kết thúc do signal `n` |

`$?` chỉ giữ status của command gần nhất, nên lưu lại ngay nếu cần:

```bash
some_command
rc=$?
echo "exit_code=$rc"
```

Chaining thường dùng:

```bash
mkdir -p /backup && tar -czf /backup/etc.tar.gz /etc
systemctl reload nginx || systemctl status nginx --no-pager
```

Với pipeline, nếu cần fail khi bất kỳ command nào trong pipeline fail, xem phần Bash scripting về `set -o pipefail`.

## 16. `xargs`

`xargs` chuyển stdin thành argument.

```bash
find /tmp -name "*.log" -print0 | xargs -0 ls -lh
printf "%s\n" file1 file2 | xargs -I{} echo "File: {}"
```

Cẩn thận với filename có khoảng trắng; ưu tiên `-print0` và `-0`.

## 17. Environment Variables Và User-defined Variables

Environment variable là key/value được process truyền cho child process. Biến shell local chỉ tồn tại trong shell hiện tại nếu chưa `export`.

```bash
env
printenv
echo "$PATH"
echo "$HOME"
echo "$USER"
echo "$SHELL"

APP_ENV=dev
bash -c 'echo "$APP_ENV"'

export APP_ENV=dev
bash -c 'echo "$APP_ENV"'
```

Một số biến thường gặp:

| Biến | Ý nghĩa |
| --- | --- |
| `PATH` | Danh sách directory để tìm executable |
| `HOME` | Home directory của user |
| `USER` | Username hiện tại |
| `SHELL` | Login shell mặc định |
| `PWD` | Working directory hiện tại |
| `PS1` | Prompt string cho interactive shell |

Tùy biến prompt bằng `PS1` hữu ích trong lab, nhưng trên production không nên làm prompt gây hiểu nhầm environment hoặc quyền hiện tại.

`PATH` được đọc theo thứ tự từ trái sang phải; executable đầu tiên khớp tên sẽ được chạy. Khi debug command lookup, dùng:

```bash
type -a <command>
command -v <command>
echo "$PATH"
```

Không thêm directory writable bởi nhiều user vào đầu `PATH` của account đặc quyền. Nếu cần chạy script nằm ngoài path chuẩn, ưu tiên gọi bằng absolute path hoặc quản lý location/permission rõ ràng.

## 18. Shell Safety Notes

- Kiểm tra biến trước khi dùng trong command nguy hiểm.
- Quote biến path: `"$path"`.
- Với `rm`, `mv`, `cp`, `chmod -R`, đọc lại path trước khi chạy.
- Ưu tiên dry-run nếu tool hỗ trợ.
- Khi chạy command từ tài liệu, hiểu từng option trước khi paste vào production.
- `>` ghi đè file đích; dùng `>>` khi muốn append log, hoặc backup file trước khi redirect vào config quan trọng.
- `cp` và `mv` có thể ghi đè file đích. Dùng `-i` khi cần prompt, `-n` khi muốn no-clobber, và `cp -a` khi cần giữ mode/owner/timestamp/symlink trong backup hoặc copy cấu hình.
- Shell mở rộng glob như `*`, `?`, `[]` trước khi command thật chạy. Với thao tác phá hủy, kiểm tra bằng `printf '%s\n' pattern`, `ls -ld pattern` hoặc `find ... -print` trước khi đổi sang `rm`, `mv`, `chmod` hay `chown`.
- `rm -r` áp dụng đệ quy cho toàn bộ cây con. Trên production, tránh chạy với path quá rộng như `/`, `/*`, biến rỗng hoặc pattern chưa xác nhận; ưu tiên `rm -rI`/`rm -ri` cho thao tác thủ công và backup/rollback khi dữ liệu có giá trị.
