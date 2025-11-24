

Ta có thể đặt lại mật khẩu người dùng root trong Linux bằng cách can thiện vào GRUB 2 Boot Loader. Phương pháp này áp dụng khi bạn có quyền truy cập trực tiếp vào máy tính vật lý hoặc console ảo của máy ảo (qua hypervisor).

![](/01-linux/images/user-and-group-management/Linux_Reset_Password001.png)

>Lưu ý Quan Trọng: Đây là một kỹ thuật khôi phục quyền truy cập. Nó minh họa cho "Định luật Bất biến số 3 của Bảo mật": Nếu kẻ xấu có quyền truy cập vật lý không giới hạn vào máy tính của bạn, thì đó không còn là máy tính của bạn nữa.

# Thay Đổi Tham Số Khởi Động (Boot Parameters)

Quy trình này sẽ yêu cầu hệ thống khởi động trực tiếp vào một môi trường Shell có quyền root, bỏ qua quá trình đăng nhập thông thường.

1. Truy cập Màn hình GRUB:

- Trong màn hình GRUB 2 boot, sử dụng phím mũi tên ↑ và ↓ để đánh dấu mục khởi động (boot entry) mà bạn muốn sửa đổi.

- Nhấn phím E để vào chế độ chỉnh sửa.

2. Tìm và Sửa đổi Dòng `linux`:

- Bạn sẽ được đưa đến một trình soạn thảo hiển thị nội dung của mục khởi động đã chọn.

- Tìm dòng bắt đầu bằng linux (hoặc linuxefi trên một số hệ thống UEFI).
![](/01-linux/images/user-and-group-management/Linux_Reset_Password002.png)
3. Thêm Tham Số Khởi Động:

- Thêm tham số sau vào cuối dòng bắt đầu bằng linux:
```
init=/bin/bash
```
- Mục đích: Tham số này yêu cầu hạt nhân (kernel) sau khi khởi động xong sẽ thực thi `/bin/bash` thay vì chương trình `init` thông thường, đưa bạn trực tiếp vào Bash Shell với quyền root mà không cần mật khẩu.

Trường hợp thay thế: Đôi khi, tùy thuộc vào bản phân phối Linux, bạn có thể cần phải sử dụng Bourne Shell (sh) thay thế:
```
init=/bin/sh
```
4. Khởi động Hệ thống:

Nhấn tổ hợp phím `CTRL + X` hoặc phím `F10` để khởi động hệ thống với các tham số mới đã thêm vào.
![](/01-linux/images/user-and-group-management/Linux_Reset_Password003.png)

![](/01-linux/images/user-and-group-management/Linux_Reset_Password004.png)
# Thực Hiện Thay Đổi Mật Khẩu
Sau khi khởi động, hệ thống sẽ hiển thị Bash Shell với dấu nhắc (prompt) thường là #, xác nhận bạn đang ở quyền root.
![](/01-linux/images/user-and-group-management/Linux_Reset_Password005.png)
1. **Gắn lại Hệ thống Tệp với Quyền Ghi (Remount Filesystem):**

Ban đầu, hệ thống tệp root (`/`) chỉ được gắn ở chế độ chỉ đọc (read-only). Bạn cần gắn lại nó với quyền đọc/ghi (read/write) để có thể thay đổi mật khẩu.
```bash
 mount -o remount,rw /
```
![](/01-linux/images/user-and-group-management/Linux_Reset_Password006.png)
2. **Thay đổi Mật khẩu Root:**

- Sử dụng lệnh `passwd` như bình thường để thay đổi mật khẩu cho người dùng root.
```bash
passwd root
```
- Hệ thống sẽ yêu cầu bạn nhập mật khẩu mới hai lần.
![](/01-linux/images/user-and-group-management/Linux_Reset_Password007.png)
3. Khởi động lại Hệ thống:

Sau khi thay đổi mật khẩu thành công, hãy khởi động lại hệ thống:
```bash
 sudo reboot -f
```
![](/01-linux/images/user-and-group-management/Linux_Reset_Password009.png)
Từ bây giờ, bạn có thể đăng nhập vào hệ thống bằng người dùng root và mật khẩu mới.

> Lưu ý Về Sự Cố: Nếu lần đầu thực hiện, hệ thống không khởi động vào Bash Shell mà bị treo ở màn hình đen hoặc khởi động bình thường, hãy lặp lại quy trình thêm 2-3 lần. Đôi khi sự cố này xảy ra và việc lặp lại thường khắc phục được.

# Bảo Mật GRUB Bằng Mật Khẩu
Để ngăn chặn người dùng trái phép truy cập dễ dàng vào GRUB để sửa đổi tham số khởi động (như cách chúng ta vừa làm), bạn có thể thiết lập mật khẩu GRUB.

>Cảnh báo Bảo mật: Thiết lập mật khẩu GRUB chỉ là một biện pháp bảo vệ cơ bản để ngăn chặn truy cập qua menu GRUB. Những kẻ có quyền truy cập vật lý vẫn có thể truy cập tệp của bạn bằng các phương pháp khác, ví dụ như khởi động từ Live CD/USB.

1. Tạo Mã Băm Mật Khẩu (Password Hash):

- Sử dụng công cụ grub2-mkpasswd-pbkdf2 để tạo mã băm mật khẩu mới:
```bash
grub2-mkpasswd-pbkdf2
```
Công cụ này sẽ trả về một chuỗi mật khẩu đã được mã hóa.

2. Đặt Tên Người Dùng và Mật khẩu vào Tệp Cấu hình:

- Bạn cần đặt tên người dùng được cấp quyền (superuser) và mã băm mật khẩu đã tạo vào một tệp cấu hình GRUB.

- Nên sử dụng tệp `/etc/grub.d/40_custom` để tránh bị ghi đè khi cập nhật gói GRUB.

- Thêm hai dòng sau vào tệp (thay thế `<password hash>` bằng chuỗi bạn đã tạo):
```
set superusers="root"
password_pbkdf2 root <password hash>
```
![](/01-linux/images/user-and-group-management/grub-password-1.png)
*Lưu ý:* Nếu sử dụng tệp tùy chỉnh, không thêm các dòng cat << EOF và EOF.

3. Cập nhật Cấu hình GRUB:

Thực thi lệnh sau để ghi cấu hình mới vào tệp grub.cfg chính:
```bash
 grub2-mkconfig -o /boot/grub2/grub.cfg
```
![](/01-linux/images/user-and-group-management/grub-password-2.png)

Từ giờ trở đi, khi bạn nhấn phím E trong menu GRUB để chỉnh sửa, hệ thống sẽ yêu cầu bạn nhập tên người dùng và mật khẩu (ví dụ: `root` và mật khẩu đã đặt) trước khi cấp quyền truy cập vào trình soạn thảo GRUB.

![](/01-linux/images/user-and-group-management/grub-password-3.png)