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

Trong script, `grep` cũng là một primitive điều kiện:

- exit code `0`: có match.
- exit code `1`: không có match.
- exit code lớn hơn `1`: lỗi đọc file, pattern sai, hoặc lỗi runtime khác.

Vì vậy không nên gom mọi non-zero thành "không tìm thấy" trong automation production. Nếu chỉ cần kiểm tra có match, dùng `-q` thay vì redirect output thủ công:

```bash
if grep -Eq '^(ERROR|WARN)' app.log; then
  echo "log has error-like entries"
fi
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

## 6. `sed` Addressing Và Command Quan Trọng

`sed` mặc định áp command cho mọi dòng và in kết quả ra `STDOUT`, không sửa file gốc. Muốn giới hạn vùng xử lý, dùng address:

```bash
sed '2s/old/new/' file.txt
sed '2,5s/old/new/g' file.txt
sed '/server_name/s/example.com/example.net/' nginx.conf
sed '2,$s/debug/info/g' app.conf
```

Substitution flags:

| Flag | Ý nghĩa |
|---|---|
| `g` | thay toàn bộ occurrence trên dòng |
| `2` | chỉ thay occurrence thứ 2 trên dòng |
| `p` | print dòng đã thay, thường đi với `-n` |
| `w file` | ghi dòng đã thay hoặc match ra file |

Ví dụ:

```bash
sed -n 's/ERROR/WARN/p' app.log
sed -n '/timeout/w timeout-lines.log' app.log
```

Các command chỉnh dòng:

```bash
sed '/DEBUG/d' app.log
sed '1i\# generated file' config.conf
sed '$a\# end of file' config.conf
sed '/^Port /c\Port 2222' sshd_config
```

Khi thay path hoặc URL, đổi delimiter để dễ đọc:

```bash
sed 's!/var/www/html!/srv/app/current!g' nginx.conf
```

Guardrails:

- Test output không ghi file trước: `sed '...' file | less`.
- Với config production, dùng `sed -i.bak` hoặc ghi ra file mới rồi diff.
- Không chạy `sed 'd' file` nếu chưa có address; output sẽ rỗng.
- Cẩn thận range theo pattern: nếu stop pattern không xuất hiện, `sed` có thể áp dụng đến cuối stream.
- Sau khi sửa config bằng `sed`, chạy validator như `sshd -t`, `nginx -t`, `named-checkconf` trước khi reload service.

## 7. `awk/gawk` Program Model

`awk` xử lý dữ liệu theo mô hình:

```text
BEGIN -> đọc từng dòng -> tách field -> chạy rule/action -> END
```

Các biến built-in hay dùng:

| Biến | Ý nghĩa |
|---|---|
| `$0` | toàn bộ dòng hiện tại |
| `$1`, `$2` | field thứ 1, thứ 2 |
| `FS` | input field separator |
| `OFS` | output field separator |
| `NR` | số dòng đã đọc |
| `NF` | số field của dòng hiện tại |

Ví dụ report có header/footer:

```bash
awk -F: '
BEGIN {
  print "user shell"
}
{
  print $1, $7
}
END {
  print "total users:", NR
}' /etc/passwd
```

Truyền biến từ Bash vào `awk` bằng `-v`:

```bash
threshold=80
df -P | awk -v threshold="$threshold" 'NR > 1 {
  usage=$5
  gsub("%", "", usage)
  if (usage >= threshold) print "WARN", $6, $5
}'
```

Khi dữ liệu có delimiter rõ như `/etc/passwd`, dùng `-F`. Khi dữ liệu là CSV thật có quote/escape, đừng parse bằng `-F,` đơn giản nếu độ chính xác quan trọng; dùng parser phù hợp hơn.

## 8. `cut`, `sort`, `uniq`, `wc`, `head`, `tail`

```bash
cut -d: -f1 /etc/passwd
sort names.txt
sort -n numbers.txt
sort -k2,2 data.txt
sort -t: -k3,3n /etc/passwd
sort -u names.txt
uniq -c sorted.txt
wc -l app.log
head -20 app.log
tail -50 app.log
tail -f app.log
```

Khi file có ký tự ẩn, tab, newline khác thường hoặc line quá dài, dùng lệnh quan sát trước khi sửa:

```bash
cat -A file.txt
cat -v file.txt
od -c file.txt | head
wc -L file.txt
```

`cat -A`/`cat -v` giúp thấy non-printing characters; `od -c` hữu ích khi nghi ngờ encoding hoặc byte lạ; `wc -L` giúp phát hiện dòng dài bất thường sau khi sửa config. Với file lớn, ưu tiên pager và lệnh lấy mẫu thay vì `cat` toàn bộ:

```bash
less /var/log/app.log
head -100 /var/log/app.log
tail -100 /var/log/app.log
journalctl -u app.service -f
```

Top IP trong access log:

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
```

`sort` mặc định so sánh theo chuỗi ký tự, nên `10` có thể đứng trước `2`. Khi dữ liệu là số, dùng `sort -n`; khi dữ liệu có field rõ, dùng `-t` để chọn delimiter và `-k` để chọn key. Nếu muốn ghi kết quả ra file, ưu tiên redirect sang file mới hoặc dùng `sort -o output.txt input.txt` thay vì ghi đè nhầm input.

`uniq` chỉ gom các dòng trùng lặp liền kề. Nếu cần đếm toàn bộ giá trị trùng trong file/log, thường phải `sort` trước rồi mới `uniq -c`; nếu thứ tự gốc là tín hiệu quan trọng, đừng sort trực tiếp trên evidence duy nhất, hãy ghi output sang file phân tích riêng.

Với checksum file, `md5sum` còn hữu ích để phát hiện lỗi truyền tải vô tình nhưng không nên dùng làm bằng chứng chống chỉnh sửa ác ý. Khi cần kiểm tra integrity ở ngữ cảnh bảo mật, ưu tiên `sha256sum` hoặc `sha512sum` và lấy checksum từ kênh tin cậy:

```bash
sha256sum artifact.tar.gz
sha256sum -c artifact.tar.gz.sha256
```

## 9. Regex Cơ Bản

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

Quote regex bằng single quote khi không cần shell expand biến. Shell xử lý glob trước khi chạy command, còn regex do tool như `grep`, `sed`, `awk` diễn giải; ví dụ `*.log` trong shell là danh sách filename, còn trong regex `*` lặp lại token đứng trước nó.

## 10. Vim Cơ Bản Cho Sysadmin

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

## 11. Nano Cơ Bản Cho Sysadmin

`nano` đơn giản hơn `vim` và hữu ích khi cần sửa nhanh file nhỏ trên host không có GUI. Ký hiệu `^X` trong giao diện nano nghĩa là `Ctrl+X`.

```bash
nano /etc/hosts
```

Phím tối thiểu cần nhớ:

| Phím | Ý nghĩa |
| --- | --- |
| `Ctrl+O` | Ghi buffer ra file |
| `Enter` | Xác nhận tên file khi save |
| `Ctrl+X` | Thoát |
| `Ctrl+W` | Tìm kiếm |
| `Ctrl+K` | Cut dòng hiện tại |
| `Ctrl+U` | Paste nội dung đã cut |
| `Ctrl+G` | Mở help |

Với file config quan trọng, thói quen an toàn vẫn giống mọi editor khác: backup trước, sửa ít, validate config, rồi reload service nếu cần.

## 12. Lab Parse Log

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
