#  —  Xử lý văn bản và Cluster
## 1. Các lệnh xử lý/lọc văn bản
### 1.1. Text Commands
- Linux cung cấp các tiện ích cho thao tác tập tin và văn bản như sau

|Tiện ích|Lệnh|
|---|---|
|Hiển thị nội dung|`cat` và `echo`|
|Chỉnh sửa nội dung|`sed` và `awk`|
|Tìm theo mẫu|`grep`|

### 1.2. Hiển thị nội dung
- Lệnh `# cat` được sử dụng để đọc và in ra nội dung của file `# tac` là ngược lại của `# cat` có chức năng đọc và in ra nội dung file theo chiều ngược lại

- Lệnh `# echo` là lệnh hiển thị text lên màn hình, Ngoài ra, ta có thể in ra giá trị của biến: `# echo $<bien>`

![](./images/cattacecho.png)

### 1.3. Chỉnh sửa nội dung
#### 1.3.1. Lệnh `# sed`
- Là một công cụ lọc văn bản cũng như thực hiện thay thế trong luồng dữ liệu. Dữ liệu từ nguồn được lấy ra và di chuyển vào không gian xử lý. Toàn bộ danh sách, thao tác sửa đổi được áp dụng lên dữ liệu trong không gian xử lý, nội dung cuối cùng được chuyển đến không gian đầu ra
- Ví dụ: Thay đổi nội dung file

![](./images/sed.png)

- Xóa 1 dòng

![](./images/sed-e.png)

#### 1.3.2. Lệnh `# awk`
- Được sử dụng để trích xuất và sau đó in nội dung cụ thể của tệp. Được sử dụng để thao tác với tệp dữ liệu, truy xuất và xử lý văn bản

![](./images/awk.png)

#### 1.3.3. Lệnh `# sort`
- Được sử dụng để sắp xếp lại các dòng của tệp văn bản theo thứ tự tăng dần hoặc giảm dần, theo 1 chuẩn nào đó

![](./images/sort.png)

#### 1.3.4. Lệnh `# uniq`
- Dùng để xóa các dòng trùng lặp trong tệp văn bản. Các đòng trùng lặp nối tiếp bị loại bỏ

![](./images/uniq.png)

#### 1.3.5. Lệnh `# paste`
- Dùng để kết hợp các trường (fields) từ các file khác nhau.

![](./images/paste.png)

#### 1.3.6. Lệnh `# join`
- Dùng để kết hợp 2 file với nhau theo 1 trường chung

![](./images/join.png)

### 1.4. Tìm theo mẫu
#### 1.4.1. Lệnh `# grep`
- Được sử dụng để quét các tập cho các mẫu chỉ định và có thể được sử dụng với các biểu thức thông thường

![](./images/grep.png)

#### 1.4.2. Lệnh `# tr`
- Được sử dụng để dịch các kí tự được chỉ định sang ký tự khác hoặc xóa chúng đi

![](./images/tr.png)

#### 1.4.3. Lệnh `# tee`
- Lệnh này sẽ lấy đầu ra của bất kỳ lệnh nào và trong lúc gửi ra đầu ra tiêu chuẩn, nó sẽ lưu vào 1 file

![](./images/tee.png)

### 1.5. Lệnh `# wc`
- Lệnh này đếm số lượng dòng `-l`, số lượng từ `-w`, số lượng ký tự `-c` trong một tệp hoặc một danh sách tệp

![](./images/wc.png)

### 1.6. Lệnh `# cut`
- Sử dụng để trích xuất các cột trong tệp. Dấu phân cách cột mặc định sẽ là kí tự `tab`

![](./images/cut.png)

### 1.7. Lệnh head
- In ra vài dòng đầu tiên của file (mặc định là 10). Có thể thay đổi qua option `-n <so_dong>`

![](./images/head.png)

### 1.8. Lệnh tail
- In ra vài dòng cuối của file (mặc định là 10). Có thể thay đổi qua option `-n <so_dong>`

![](./images/tail.png)

# 2. Cluster 
- Một cluster (Cụm) là hai hay nhiều máy tính làm việc cùng nhau để thực hiện một tác vụ. Ví dụ như là: cung cấp tính sẵn sàng cao cho một dịch vụ. Các cụm khả dụng cao cung cấp các dịch vụ khả dụng cao bằng cách loại bỏ những điểm bị lỗi và lỗi dịch vụ từ một thành viên của cụm đến những trường hợp khác không hoạt động 
- Thông thường, các dịch vụ trong cụm khả dụng cao, duy trì tính toàn vẹn của dữ liệu 
- Trong Linux, có nhiều công cụ cụm đạt được tính sẵn sàng cao cho tài nguyên. Công cụ được sử dụng nhiều nhất là Pacemaker. 
- Một cụm được định cấu hình với Pacemaker bao gồm các trình nền thành phần riêng biệt theo dõi các thành viên trong cụm, tập lệnh quản lý dịch vụ và các hệ thống con quản lý tài nguyên theo dõi tài nguyên
- Kiến trúc Pacemaker gồm:
	+ **Cluster Information Base (Cụm thông tin cơ sở)**: Trình thông tin Pacemaker phân phối, đồng bộ cấu hình cụm và trạng thái thông tin điều phối được chỉ định (DC) của cụm tới tất cả các thành viên trong cụm. DC là một thành viên cụm được chỉ định để lưu trạng thái cụm 
	+ **Cluster Resource Management Daemon (Quản lý tài nguyên cụm)**: Tài nguyên cụm được quản lí bởi thành phần này có thể được truy vấn bởi hệ thống máy khách, di chuyển, khởi tạo và thay đổi khi cần thiết. Mỗi nút cụm bao gồm một trình nền quản lý tài nguyên cục bộ hoạt động như một giao diện giữa trình nền quản lý tài nguyên cụm và chính tài nguyên đó

## 2. GNU/Unix commands

### ls – Liệt kê file và thư mục
- Xem có những file/thư mục nào trong thư mục hiện tại (hoặc thư mục chỉ định).
- Cách dùng:
```bash
ls               # chỉ hiện tên file/thư mục trong thư mục hiện tại
ls /etc          # xem bên trong thư mục /etc
ls *.txt         # chỉ hiện các file có đuôi .txt
```
- Các options:
	- -l → định dạng dài (long)
	Hiển thị đầy đủ thông tin mỗi file:
	`drwxr-xr-x  2 user user 4096 Nov 30 10:00 Documents`
	**Trong đó:**
		`drwxr-xr-x` = quyền (d = thư mục, rwx = chủ sở hữu được đọc/ghi/thực thi, r-x = nhóm và người khác chỉ đọc/thực thi)
		`2` = số link
		`user` `user` = chủ sở hữu và nhóm
		`4096` = kích thước (byte)
		`Nov 30 10:00` = ngày giờ sửa đổi cuối
		`Documents` = tên
	- `-h` → human-readable (kích thước dễ đọc) → luôn dùng kèm `-l`
	Thay vì 4096 → hiển thị 4.0K, thay vì 1048576 → 1.0M
	- `-a` → all → hiện cả file ẩn (bắt đầu bằng dấu `.`)
	Rất hay dùng vì Linux có rất nhiều file cấu hình ẩn: `.bashrc`, `.ssh`, `.cache`…
	- `-A` → almost all → như -a nhưng không hiện . (thư mục hiện tại) và .. (thư mục cha)
	- `-t` → sắp xếp theo thời gian sửa đổi (mới nhất lên đầu)
	- `-r` → reverse → đảo ngược thứ tự (kèm `-t` thì cũ nhất lên đầu)
	- `-S` → sắp xếp theo kích thước (lớn nhất lên đầu)
	- `-R` → recursive → liệt kê cả tất cả thư mục con (rất sâu)
	- `--color=auto` → tô màu (xanh = thư mục, xanh lá = file thực thi, đỏ = file nén…) → mặc định trên hầu hết distro
### cp – Copy file/thư mục
- Sao chép file hoặc cả thư mục sang nơi khác.
- Cách dùng:
```bash
cp file.txt /backup/          # copy file.txt vào thư mục backup
cp *.jpg /photos/             # copy tất cả file .jpg
```
- Các tùy chọn : 
	- `-r` hoặc `-R `→ copy cả thư mục (recursive)
	Không có `-r` thì chỉ copy được file, không copy được thư mục.
	- `-v` → hiện tiến trình (verbose), thấy đang copy cái gì
	- `-i` → hỏi trước khi ghi đè (an toàn)
	- `-a` → archive: giữ nguyên mọi thứ (quyền, thời gian, symbolic link…) – tốt nhất để backup
	- `-p` → preserve → giữ nguyên quyền, owner, timestamp
	- `-u` → update → chỉ copy khi file nguồn mới hơn file đích

Ví dụ : 
```bash
cp -a /home/user /backup/user_$(date +%F)   # backup đầy đủ, giữ nguyên hết
cp -rv *.txt /dest/                         # copy tất cả .txt, hiện tên từng file
```

### mv – Di chuyển hoặc đổi tên
- Sử dụng để di chuyển file/thư mục đồng thời có thể đổi tên file/thư mục ở vị trí đích di chuyển tới
- Cách dùng:
```bash
mv old.txt new.txt          # đổi tên
mv file.txt /var/www/       # di chuyển vào thư mục khác
mv *.log /logs/             # di chuyển tất cả file .log
```
- Các option:
	- `-i` → hỏi trước khi ghi đè (rất nên bật)
	- `-v` → hiện tiến trình
	- `-u` → chỉ di chuyển khi file nguồn mới hơn
### rm – Xóa file/thư mục
- Xóa vĩnh viễn (không vào thùng rác).
- Cách dùng:
```bash
rm file.txt
rm *.tmp
```

- Các Options :
	- `-r` → xóa cả thư mục và mọi thứ bên trong (recursive)
	- `-f` → force, không hỏi gì cả (nguy hiểm)
	- `-i` → hỏi từng file (an toàn cho người mới)
	- `-I` → hỏi một lần nếu xóa nhiều hơn 3 file hoặc đệ quy (mặc định trên nhiều distro)

- setup alias nhanh vào ~/.bashrc ( không khuyến khích khi prod):
```bash 
alias rm='rm -I'          # tự động hỏi khi xóa nhiều
alias del='trash-cli'     # dùng trash-cli để xóa vào thùng rác (cài bằng apt install trash-cli)
```
### grep – Tìm kiếm text trong file
- Tìm dòng chứa từ/ký tự nào đó trong file hoặc output.
- Cách dùng:
```bash
grep "error" log.txt
grep -i "hello" file.txt    # không phân biệt hoa/thường
```

- Các options:
	- `-i` → ignore case (không phân biệt hoa thường)
	- `-r` / `-R` → tìm đệ quy trong tất cả file con thư mục
	- `-n` → hiện số dòng
	- `-c` → chỉ đếm số dòng khớp
	- `-v` → đảo ngược: hiện dòng KHÔNG chứa từ đó
	- `--color=always` → tô màu từ tìm thấy (rất tiện khi pipe)
	- `-w` → whole word → chỉ khớp cả từ
- Ví dụ : 
```
grep -r "ERROR" /var/log/          # tìm lỗi trong toàn bộ log
dmesg | grep -i nvidia             # xem lỗi driver card màn hình
ps aux | grep -v grep | grep python # xem process python đang chạy
```

### cut – Cắt theo cột
- Lấy một phần của mỗi dòng (theo dấu phân cách hoặc vị trí ký tự).
- Ví dụ :
```
# File /etc/passwd mỗi dòng: user:x:1000:1000::/home:/bin/bash
cut -d: -f1 /etc/passwd    # lấy cột 1 → liệt kê tất cả username
cut -d: -f1,7 /etc/passwd   # lấy username và shell
echo "192.168.1.1" | cut -d. -f4   # lấy số cuối của IP → 1
```
### tar – Đóng gói và giải nén
- Cách dùng :
```bash
tar -cf archive.tar file1 file2 ...      # tạo (create)
tar -xf archive.tar                      # giải nén (extract)
tar -tf archive.tar                      # xem nội dung (table of contents)
```

- Các options:
	- `-v` → hiện từng file đang xử lý
	- `-C` /path → giải nén vào thư mục khác
### find – Tìm file theo mọi điều kiện
- Cách dùng:
```bash
find /etc -name "*.conf          # tìm file có tên chứa "conf" trong /etc
find . -iname "*.txt"            # tìm file .txt, không phân biệt hoa thường
```

- Các điều kiện: 
	- `-type f` → chỉ file thường
	- `-type d` → chỉ thư mục
	- `-size +100M` → lớn hơn 100MB
	- `-size -10k` → nhỏ hơn 10KB
	- `-mtime -7` → sửa trong 7 ngày qua
	- `-mmin -60` → sửa trong 60 phút qua
	- `-user username` → thuộc về user nào
	- `-exec lệnh {} +` → thực thi lệnh trên kết quả
		- ` -exec rm {} +` → xóa tất cả kết quả

## 3. Sử dụng pipe 
- Pipe lấy kết quả của lệnh bên trái, nhét thẳng vào làm đầu vào cho lệnh bên phải.  
Nó giúp bạn kết hợp nhiều lệnh đơn giản thành một "dây chuyền sản xuất" mạnh mẽ.
- **Cú pháp**:
```bash
lệnh1 | lệnh2 | lệnh3 | ...
```
- Các ví dụ :
```bash
# xem danh sách file dài mà cuộn được
ls -lh | less

# Lọc ra chỉ thông tin mình cần
ls -lh | grep ".txt"        # chỉ hiện file .txt
ps aux | grep python        # xem process python (có cả grep chính nó)
ps aux | grep -v grep | grep python   # loại bỏ dòng grep → sạch sẽ

# Top 10 process ngốn CPU nhất
ps aux --sort=-%cpu | head -n 11

# Top 10 process ngốn RAM nhất:
ps aux --sort=-%mem | head -n 11

# Đếm số file theo phần mở rộng:
find . -type f | sed -E 's/.*\.([^\.]+)$/\1/' | sort | uniq -c | sort -nr

# Tìm file lớn nhất trong thư mục hiện tại:
find . -type f -printf '%s %p\n' | sort -nr | head -1

# Xem IP nào kết nối nhiều nhất vào máy:
ss -ant | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head

# Pipe cả lỗi (stderr) lẫn kết quả bình thường:
lệnh 2>&1 | grep something      # cũ
lệnh |& grep something          # mới (bash/zsh)

# Lưu kết quả trung gian mà vẫn tiếp tục pipe:
ls -lh | tee danh_sach.txt | grep ".log"

```
> Dùng `| less -R` để cuộn và giữ màu
> Dùng `| grep --color=always` để giữ màu khi pipe tiếp
> Dùng `| tail -f` để theo dõi log realtime

## 4. vi/vim editor
- Ba chế độ chính quan trọng nhất :
	- **Normal mode**    → chế độ mặc định khi mở file mở (dùng để di chuyển, copy, xóa, tìm kiếm)
	- **Insert mode**   → chế độ soạn thảo (nhấn i để vào)
	- **Visual mode**    → chế độ chọn vùng (nhấn v, V, Ctrl-v)
- Cách thoát khỏi Insert mode → Normal mode: nhấn Esc
### 4.1 Các lệnh quan trọng nhất (Normal mode):

- Di chuyển nhanh (không cần chuột):
	- h j k l          → trái xuống lên phải (như phím mũi tên)
	- w                → nhảy tới đầu từ tiếp theo
	- b                → nhảy lùi về đầu từ trước
	- 0                → đầu dòng
	- ^                → ký tự đầu tiên không phải khoảng trắng
	- $                → cuối dòng
	- gg               → đầu file
	- G                → cuối file
	- 123G             → nhảy đến dòng 123
	- Ctrl+u           → lên nửa trang
	- Ctrl+d           → xuống nửa trang
	- Ctrl+b           → lùi 1 trang
	- Ctrl+f           → tiến 1 trang
### 4.1 Insert mode 
Vào Insert mode (bắt đầu gõ):
- i → chèn trước con trỏ
- I → chèn đầu dòng
- a → chèn sau con trỏ
- A → chèn cuối dòng
- o → mở dòng mới bên dưới
- O → mở dòng mới bên trên
- Copy - Cut - Paste:
	- yy               → copy 1 dòng
	- 3yy              → copy 3 dòng
	- dd               → cut (xóa) 1 dòng
	- 5dd              → cut 5 dòng
	- p                → dán dưới dòng hiện tại
	- P                → dán trên dòng hiện tại
	- x                → xóa 1 ký tự

- Undo - Redo:
	- u                → undo
	- Ctrl+r           → redo
	- .                → lặp lại lệnh cuối cùng (thần thánh)

- Tìm kiếm:
	- /từ_khóa Enter   → tìm xuống
	- ?từ_khóa Enter   → tìm lên
	- n                → tìm tiếp cùng chiều
	- N                → tìm ngược chiều

- Thay thế:
	- :%s/cũ/mới/g      → thay tất cả trong file
	- :%s/cũ/mới/gc     → thay tất cả nhưng hỏi từng cái
	- :10,20s/^/# /g   → comment dòng 10-20 (thêm # đầu dòng)

- Visual block (comment nhiều dòng cực nhanh):
	- Ctrl+v → vào visual block
	- j hoặc k kéo chọn cột đầu dòng
	- I# Esc → tự động thêm # vào tất cả dòng đã chọn

- Lưu & thoát (Command mode – nhấn : ):
	- :w               → lưu
	- :q               → thoát (nếu không thay đổi)
	- :wq hoặc ZZ      → lưu + thoát
	- :q!              → thoát không lưu (buông bỏ thay đổi)
	- :x               → lưu nếu có thay đổi rồi thoát

## 5. Regex - Regular Expressions 