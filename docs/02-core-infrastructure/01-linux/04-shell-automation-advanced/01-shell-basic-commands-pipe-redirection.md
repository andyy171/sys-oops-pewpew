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

Kiểm tra shell:

```bash
echo "$SHELL"
cat /etc/shells
ps -p $$ -o comm=
```

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
| `~/.bash_profile`, `~/.profile` | User login shell |
| `~/.bashrc` | User interactive non-login shell |
| `/etc/bash.bashrc` hoặc `/etc/bashrc` | Global bashrc tùy distro |

## 5. Basic Navigation và File Commands

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

## 6. Inspect Files và Directories

```bash
file /bin/bash
stat /etc/passwd
du -sh /var/log
df -h
tree -L 2 2>/dev/null
```

Tìm file:

```bash
find /var/log -type f -name "*.log"
find /var/log -type f -mtime -7
find /var/log -type f -size +100M
```

## 7. Archive và Compression

```bash
tar -czf etc-backup.tar.gz /etc
tar -tzf etc-backup.tar.gz | head
tar -xzf etc-backup.tar.gz -C /tmp/restore

gzip file.log
gunzip file.log.gz
zip -r archive.zip directory/
unzip archive.zip
```

## 8. Globbing, Brace Expansion và History

Globbing:

```bash
ls *.log
ls access-2026-05-*.log
rm -i *.tmp
```

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
```

Trong shell interactive, `Ctrl+r` giúp search lại command cũ.

Di chuyển nhanh:

```bash
cd -
pushd /var/log
popd
```

## 9. Pipe

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

## 10. Redirection

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

## 11. `tee`

`tee` vừa hiển thị output vừa ghi file.

```bash
echo "hello" | tee output.txt
echo "more" | tee -a output.txt
echo "net.ipv4.ip_forward = 1" | sudo tee /etc/sysctl.d/99-ip-forward.conf
```

`sudo echo ... > /root/file` thường fail vì redirection chạy bởi shell hiện tại; dùng `sudo tee`.

## 12. `xargs`

`xargs` chuyển stdin thành argument.

```bash
find /tmp -name "*.log" -print0 | xargs -0 ls -lh
printf "%s\n" file1 file2 | xargs -I{} echo "File: {}"
```

Cẩn thận với filename có khoảng trắng; ưu tiên `-print0` và `-0`.

## 13. Command Chaining

```bash
command1 && command2    # command2 chạy nếu command1 thành công
command1 || command2    # command2 chạy nếu command1 fail
command1 ; command2     # chạy tuần tự, không phụ thuộc exit code
```

Ví dụ:

```bash
mkdir -p /backup && tar -czf /backup/etc.tar.gz /etc
systemctl reload nginx || systemctl status nginx
```

## 14. Exit Code

```bash
echo $?
true
echo $?
false
echo $?
```

Trong vận hành:

- `0`: success.
- Khác `0`: lỗi hoặc trạng thái đặc biệt tùy command.

## 15. Shell Safety Notes

- Kiểm tra biến trước khi dùng trong command nguy hiểm.
- Quote biến path: `"$path"`.
- Với `rm`, `mv`, `chmod -R`, đọc lại path trước khi chạy.
- Ưu tiên dry-run nếu tool hỗ trợ.
- Khi chạy command từ tài liệu, hiểu từng option trước khi paste vào production.
