# Text Processing: grep, sed, awk, regex và vim

## 1. Mục Tiêu

Text processing giúp sysadmin đọc log, lọc output command, trích xuất field, sửa config hàng loạt và chuẩn bị dữ liệu cho script.

File này chỉ tập trung vào text processing. Basic command và pipe/redirection nằm ở [Shell, Basic Commands, Pipe và Redirection](./01-shell-basic-commands-pipe-redirection.md).

## 2. Khi Nào Dùng Trong Thực Tế

- Lọc lỗi trong log.
- Đếm IP/request/status code.
- Thay đổi config theo pattern.
- Trích field từ output command.
- Chuẩn bị report nhanh trong incident.

## 3. `grep`

```bash
grep "error" app.log
grep -i "error" app.log
grep -n "error" app.log
grep -R "PermitRootLogin" /etc/ssh
grep -rni "error" /var/log
grep -E "error|failed|denied" app.log
grep -v "healthcheck" access.log
grep --color=always -E "error|failed|denied" app.log | less -R
```

Context:

```bash
grep -A 3 -B 3 "panic" kernel.log
grep -C 5 "Exception" app.log
```

## 4. `sed`

In dòng:

```bash
sed -n '1,20p' file.txt
sed -n '/server {/,/}/p' nginx.conf
```

Replace:

```bash
sed 's/old/new/' file.txt
sed 's/old/new/g' file.txt
```

Edit in-place, nên backup:

```bash
sed -i.bak 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
```

Production note: luôn dùng `sed -i.bak` khi sửa file config quan trọng, rồi validate service config trước khi reload.

```bash
sudo sed -i.bak 's/^#Port 22/Port 2222/' /etc/ssh/sshd_config
sudo sshd -t
sudo systemctl reload sshd
```

Xóa dòng match:

```bash
sed '/^#/d' config.conf
```

## 5. `awk`

In field:

```bash
awk '{print $1}' access.log
awk '{print $1, $9}' access.log
```

Filter:

```bash
awk '$9 >= 500 {print}' access.log
awk '$3 > 80 {print $0}' metrics.txt
```

Delimiter:

```bash
awk -F: '{print $1, $3, $7}' /etc/passwd
```

Aggregate:

```bash
awk '{count[$1]++} END {for (ip in count) print count[ip], ip}' access.log | sort -nr | head
```

Biến built-in hay dùng:

```bash
awk '{print NR, $0}' file.txt
awk '{print NF, $0}' file.txt
awk 'END {print NR}' file.txt
```

## 6. `cut`, `sort`, `uniq`, `wc`, `head`, `tail`

```bash
cut -d: -f1 /etc/passwd
sort names.txt
sort -u names.txt
uniq -c sorted.txt
wc -l app.log
head -20 app.log
tail -50 app.log
tail -f app.log
```

Top IP trong access log:

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
```

## 7. Regex Cơ Bản

| Pattern | Ý nghĩa |
| --- | --- |
| `.` | Một ký tự bất kỳ |
| `*` | Lặp 0 hoặc nhiều lần |
| `+` | Lặp 1 hoặc nhiều lần, dùng với extended regex |
| `?` | Optional, dùng với extended regex |
| `^` | Đầu dòng |
| `$` | Cuối dòng |
| `[abc]` | Một ký tự trong set |
| `[^abc]` | Không thuộc set |
| `[0-9]` | Digit |
| `(a|b)` | a hoặc b, dùng với extended regex |

Ví dụ:

```bash
grep -E '^[0-9]+\.' access.log
grep -E ' 5[0-9]{2} ' access.log
grep -E 'error|failed|timeout' app.log
```

## 8. Vim Cơ Bản Cho Sysadmin

Mở file:

```bash
vim /etc/ssh/sshd_config
```

Phím/lệnh cơ bản:

| Lệnh | Ý nghĩa |
| --- | --- |
| `i` | Insert mode |
| `Esc` | Về normal mode |
| `:w` | Save |
| `:q` | Quit |
| `:wq` | Save and quit |
| `:q!` | Quit không save |
| `/text` | Search |
| `n`, `N` | Next/previous search |
| `:%s/old/new/g` | Replace toàn file |
| `:set number` | Hiện số dòng |

Production note: với file critical như sudoers, dùng tool validate như `visudo` thay vì `vim /etc/sudoers` trực tiếp.

## 9. Lab Parse Log

Giả sử access log có format Nginx/Apache phổ biến.

Top IP:

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
```

Top 5xx:

```bash
awk '$9 ~ /^5/ {print $0}' access.log | head
```

Đếm status code:

```bash
awk '{print $9}' access.log | sort | uniq -c | sort -nr
```

Top URL:

```bash
awk '{print $7}' access.log | sort | uniq -c | sort -nr | head
```
