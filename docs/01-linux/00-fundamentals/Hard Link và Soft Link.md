# Inode và Khái niệm File trong Unix-like Systems
- Trong các hệ điều hành **Unix-like**, mọi thứ đều được coi là **file** – từ tệp tin thông thường, thư mục, thiết bị, đến socket. Tuy nhiên, một file không phải là nội dung dữ liệu trực tiếp mà là một liên kết (link) đến một cấu trúc dữ liệu gọi là inode (index node). **Inode** là một khối metadata chứa thông tin về file, bao gồm:

+ Ngày tạo, sửa đổi, và truy cập.
+ Quyền hạn (permissions), chủ sở hữu (owner), và nhóm (group).
+ Số lượng hard link trỏ đến nó (link count).
+ Tham chiếu đến vị trí lưu trữ thực tế của nội dung dữ liệu (payload) trên đĩa cứng.

- **Inode** không chứa tên file gốc hoặc nội dung thực tế; nó chỉ là "bảng chỉ dẫn" giúp hệ thống tìm đến dữ liệu. Mỗi inode có một số duy nhất (inode number) để nhận dạng.

> **Lưu ý quan trọng: Inode** được tạo khi file được tạo, và nó tồn tại độc lập với tên file. Nếu bạn xóa một file, hệ thống chỉ giảm link count của inode; dữ liệu chỉ bị xóa thực sự khi link count về 0. Điều này giải thích tại sao hard link và soft link hoạt động khác nhau.

Để minh họa, hãy tạo một file đơn giản và kiểm tra inode. Bạn có thể sử dụng lệnh cat để tạo file nhanh chóng mà không cần trình soạn thảo:
```bash
cat > file1.txt

# Nhập nội dung (nhấn Enter cho dòng mới), rồi nhấn Ctrl+D để kết thúc và lưu file.

# Để xem inode number, sử dụng lệnh ls -i:
bashls -i file1.txt
```
Kết quả có thể là một số như 921412, đại diện cho inode của file.


# Các Loại File trong Unix
- Theo chuẩn **POSIX**, **Unix-like systems** hỗ trợ **bảy loại file chính**: 
    + regular files (tệp thông thường)
    + directory (thư mục)
    + symbolic link (soft link)
    + FIFO special (pipe)
    + block special (thiết bị khối)
    + character special (thiết bị ký tự)
    + socket. 

Mỗi loại đều là "file" và có inode riêng, nhưng cách chúng tham chiếu dữ liệu khác nhau.

> **Lưu ý quan trọng:** **Thư mục (directory)** cũng là một loại file đặc biệt, **chứa danh sách các liên kết đến inode của các file con**. Tuy nhiên, bạn **không thể tạo hard link cho thư mục để tránh tạo chu kỳ (cycles) dẫn đến lỗi hệ thống file vô tận**. Thay vào đó, sử dụng soft link cho thư mục.

# Hard Link
- Hard link là một liên kết trực tiếp trỏ đến inode của file, nghĩa là nó chia sẻ cùng metadata và nội dung dữ liệu với file gốc. Mỗi file khi tạo đều có ít nhất một hard link (tên file gốc), và hệ thống sử dụng link count để theo dõi số lượng hard link.

+ Không có "file gốc" hay "bản sao"; tất cả hard link đều bình đẳng, vì chúng trỏ cùng inode. Thay đổi nội dung qua bất kỳ hard link nào cũng ảnh hưởng đến tất cả.
+ Hard link chỉ hoạt động trong cùng filesystem (không cross-filesystem), vì inode là duy nhất trong filesystem.

- Để xem link count, sử dụng `ls -l` (cột thứ hai hiển thị số lượng hard link). Ví dụ, thư mục mới tạo có link count là 2: một cho chính nó (.) và một cho thư mục cha (..). Mỗi thư mục con tăng link count của thư mục cha lên 1.

Cách tạo hard link bằng lệnh ln:
```bash
ln file1.txt link_to_file1.txt
ln -v file1.txt link_to_file1.txt  # -v cho verbose mode
ln file1.txt /different/folder/link_to_file1.txt  # Tạo ở thư mục khác, nhưng cùng filesystem
```

**Lưu ý quan trọng:** Để xóa file hoàn toàn, phải xóa tất cả hard link (link count về 0). Xóa một hard link không ảnh hưởng đến các hard link khác. Sử dụng rm hoặc unlink để xóa hard link:.
```
rm link_to_file1.txt
unlink link_to_file1.txt
```


Để tìm tất cả hard link của một file, lấy inode number từ ls -i, rồi dùng find:
```bash
find / -inum 921415  # Tìm toàn hệ thống
```
Điều này liệt kê tất cả đường dẫn trỏ đến cùng inode.
- **Ưu điểm:** Tiết kiệm không gian (không sao chép dữ liệu), bền vững (không bị hỏng nếu đổi tên file). 
- **Nhược điểm:** Không dùng cho thư mục hoặc cross-filesystem.

# Soft Link (Symlink, Symbolic Link)
- **Soft link (hay symlink)** là một file nhỏ chứa đường dẫn (path) đến file hoặc thư mục đích, hoạt động như "shortcut" trong Windows. Không giống hard link, soft link có inode riêng và không trỏ trực tiếp đến dữ liệu; nó chỉ trỏ đến tên file đích.

+ Đường dẫn có thể là relative (`../folder1/file1`) hoặc absolute (`/opt/folder1/file1`).
+ Có thể tạo soft link cho thư mục hoặc cross-filesystem, vượt qua hạn chế của hard link.
+ Trong `ls -l`, soft link hiển thị với chữ 'l' ở đầu permissions, và đường dẫn đích (thường màu cyan trên Ubuntu). Nếu đích bị xóa hoặc di chuyển, soft link bị hỏng (broken, màu đỏ trên Ubuntu).

Cách tạo soft link bằng ln -s:
```bash
ln -s file1.txt symlink_to_file1.txt
ln -vs file1.txt symlink_to_file1.txt  # -v cho verbose
ln -s /source/folder /different/filesystem/symlink_to_folder
```

> Soft link bị hỏng nếu file đích bị xóa hoặc đổi tên/đường dẫn. Ví dụ, nếu đổi tên folder1 thành folder11, symlink cũ sẽ broken. Tạo symlink mới để sửa. Xóa soft link không ảnh hưởng đến file đích.

Xóa soft link bằng rm hoặc unlink (tương tự hard link):
```bash
rm symlink_to_file1.txt
unlink symlink_to_file1.txt
```

Để tìm tất cả soft link trong hệ thống:
```
find / -type l
```

Để tìm soft link trỏ đến file cụ thể:
```bash
find -L /path -xtype l -samefile /opt/file1.txt

-L: Theo dõi symlink.
-xtype l: Chỉ symlink.
-samefile: Trỏ cùng inode.
```

# So sánh và Lưu ý
- Hard link và soft link đều giúp tham chiếu file mà không sao chép dữ liệu, nhưng hard link bền vững hơn (chia sẻ inode), trong khi soft link linh hoạt hơn nhưng dễ hỏng. Sử dụng hard link cho backup hoặc tổ chức file cùng filesystem; soft link cho shortcut hoặc liên kết giữa các đĩa.
> Lưu ý quan trọng: Tránh tạo cycle với soft link (ví dụ: symlink A trỏ B, B trỏ A). Kiểm tra filesystem giới hạn (như ext4 hỗ trợ giới hạn hard link per inode). Trong script, dùng readlink để giải mã symlink: readlink -f symlink_to_file1.txt

## Symbolic Links và Hard Links trong Windows 
- Trong Windows (NTFS), tương đương là **hard link**, **junction** (soft link cho thư mục), và **symbolic link** (soft link cho file/thư mục). Sử dụng lệnh `mklink` để tạo:

+ Hard link: `mklink /H link source`.
+ Symbolic link: `mklink link source`.
+ Junction: `mklink /J link source `(cho thư mục).

Windows hỗ trợ ba loại:** hard link **(tương tự Linux), **junction** (soft link cho thư mục, không cross-volume), và **symbolic link** (linh hoạt hơn, cross-volume).
> Lưu ý quan trọng: Cần quyền admin để tạo symbolic link trong Windows. Tham khảo docs Microsoft để chi tiết.