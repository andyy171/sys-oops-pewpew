
# Giới thiệu về sudo và File sudoers
- Sudo là một chương trình phổ biến trên các hệ thống Unix-like, cho phép người dùng chạy lệnh với quyền hạn của người dùng khác, mặc định là **superuser** (root). Tên sudo ban đầu nghĩa là "superuser do", nhưng nay được hiểu rộng hơn là "substitute user do", vì nó có thể chạy lệnh dưới bất kỳ người dùng nào. Ví dụ, một người dùng thông thường có thể sử dụng sudo để cài đặt phần mềm mà không cần chuyển hẳn sang tài khoản root, giảm rủi ro bảo mật.

- File `/etc/sudoers` là nơi lưu trữ các quy tắc này. Nó chứa danh sách người dùng hoặc nhóm được phép chạy các lệnh cụ thể với quyền hạn nâng cao. File này có thể yêu cầu mật khẩu để xác thực, hoặc cấu hình để bỏ qua mật khẩu trong một số trường hợp. Chỉ người dùng được liệt kê trong file mới có thể sử dụng sudo, và file này phải được chỉnh sửa cẩn thận để tránh khóa hệ thống.

> **Lưu ý quan trọng:** Không bao giờ chỉnh sửa trực tiếp file `/etc/sudoers` bằng trình soạn thảo thông thường, vì lỗi cú pháp có thể khiến bạn mất quyền truy cập `sudo`. Thay vào đó, luôn sử dụng lệnh `visudo`, công cụ này khóa file trong quá trình chỉnh sửa và kiểm tra cú pháp trước khi lưu. Ví dụ, chạy `sudo visudo` để mở file an toàn.

---
# Kiểm tra Quyền hạn sudo
Trước khi cấu hình, bạn cần kiểm tra ai có quyền sudo. Dưới đây là các lệnh hữu ích để xác định thành viên của nhóm sudo hoặc các nhóm khác.

- Để liệt kê thành viên của nhóm sudo: Sử dụng lệnh `getent group sudo`. Lệnh này sẽ hiển thị tất cả người dùng trong nhóm, ví dụ: `sudo:x:27:user1,user2`.
![](/01-linux/images/commands/sudoer-01.png)
- Để xem tất cả nhóm mà một người dùng thuộc về: Chạy `groups <username>`. Đối với người dùng hiện tại, chỉ cần `groups`.
- Kiểm tra trực tiếp file sudoers: Xem nội dung bằng `sudo cat /etc/sudoers`, nhưng chỉ đọc thôi, không chỉnh sửa thủ công.
![](/01-linux/images/commands/sudoer-02.png)
> Những lệnh này giúp xác nhận quyền hạn trước khi thay đổi, tránh tình trạng mất quyền truy cập.

---

# Cú pháp và Cấu hình Cơ bản trong File sudoers
- File **sudoers** sử dụng cú pháp đơn giản nhưng mạnh mẽ để định nghĩa quyền hạn. Mỗi dòng quy tắc thường có dạng: `who where = (as_whom) what`, nơi:

+ **who:** Người dùng hoặc nhóm (nhóm dùng tiền tố % như %sudo).
+ **where:** Máy chủ (thường là ALL cho mọi máy).
+ **(as_whom):** Chạy lệnh dưới quyền của ai (ví dụ: (ALL:ALL) nghĩa là dưới bất kỳ người dùng và nhóm nào).
+ **what:** Lệnh được phép (ALL cho tất cả lệnh).

- Dưới đây là giải thích các dòng phổ biến trong file sudoers.

+ **root ALL=(ALL:ALL) ALL:** Người dùng root có thể chạy tất cả lệnh trên mọi máy dưới bất kỳ quyền hạn nào. Root thường không cần sudo, nhưng dòng này cho phép nhân bản người dùng (impersonation).
+ **%admin ALL=(ALL) ALL:** Nhóm admin (đã lỗi thời từ Ubuntu 12.04, chỉ giữ cho tương thích ngược) được cấp quyền chạy tất cả lệnh.
+ **%sudo ALL=(ALL:ALL) ALL:** Nhóm sudo được cấp quyền tương tự, nghĩa là thành viên có thể chạy bất kỳ lệnh nào dưới bất kỳ người dùng hoặc nhóm.
+ **%google-sudoers ALL=(ALL:ALL) NOPASSWD:ALL:** Nhóm **google-sudoers** (thường thấy trên Google Cloud VM) được cấp quyền mà không cần mật khẩu (NOPASSWD). Điều này tiện lợi cho tự động hóa nhưng tăng rủi ro nếu nhóm bị xâm phạm.

Ngoài ra, file **sudoers** có thể bao gồm các chỉ thị `@include` hoặc `@includedir` để nhập quy tắc từ file khác, thường là thư mục `/etc/sudoers.d.` Ví dụ: `@includedir /etc/sudoers.d` sẽ tải tất cả file trong thư mục đó (trừ file ẩn hoặc kết thúc bằng ~). Điều này giúp tổ chức quy tắc riêng lẻ, như một file dành cho nhóm cụ thể.
![](/01-linux/images/commands/sudoer-03.png)
> **Lưu ý quan trọng:** Các file trong /etc/sudoers.d phải có quyền 0440 (chỉ đọc bởi root và nhóm), và không được chứa lỗi cú pháp. Luôn kiểm tra bằng visudo -c để xác thực toàn bộ cấu hình.

# Ví dụ Thực tiễn từ Google Cloud Linux VM 
- Trên các instance Google Cloud, cấu hình sudoers thường được tối ưu cho quản lý đám mây. Thay vì thêm người dùng trực tiếp vào nhóm sudo trong file chính, Google sử dụng file riêng trong /etc/sudoers.d, ví dụ file google_sudoers với nội dung: `%google_sudoers ALL=(ALL:ALL) NOPASSWD:ALL`.
![](/01-linux/images/commands/sudoer-04.png)
+ Người dùng thuộc nhóm google_sudoers có thể chạy sudo mà không cần mật khẩu, tiện cho script tự động.
+ Kiểm tra thành viên nhóm bằng `getent group google_sudoers`.

- Điều này tách biệt quy tắc đám mây khỏi cấu hình hệ thống mặc định, dễ quản lý qua công cụ như Google Cloud IAM.

> **Lưu ý quan trọng:** Trong môi trường đám mây, tránh cấp NOPASSWD cho nhóm lớn để giảm rủi ro tấn công.

---

# Các Cấu hình Nâng cao và Lưu ý Bảo mật
File **sudoers** hỗ trợ nhiều tùy chọn nâng cao để tinh chỉnh quyền hạn.

- `Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"`: Đặt đường dẫn an toàn để tránh chạy lệnh độc hại từ thư mục người dùng.
- **Defaults requiretty:** Yêu cầu sudo chỉ chạy từ terminal thực (TTY), ngăn chặn chạy từ script không tương tác.
- `Defaults logfile="/var/log/sudo.log"`: Ghi log mọi lệnh sudo để kiểm toán.
- Giới hạn lệnh cụ thể: Ví dụ, `user ALL=(ALL) /bin/ls`, `/usr/bin/apt-get` chỉ cho phép chạy `ls` và `apt-get`.

Lưu ý quan trọng:

Sử dụng **User_Alias**, **Host_Alias**, **Cmnd_Alias** để nhóm quy tắc phức tạp, làm file dễ đọc hơn.
Tránh cấp **ALL** cho mọi người; tuân thủ nguyên tắc least privilege (quyền hạn tối thiểu cần thiết).
Kiểm tra cấu hình bằng `sudo -l` để xem quyền hạn của người dùng hiện tại.


# Phân biệt Privileges và Permissions
- **Permissions** **gắn liền với tài nguyên (như file, thư mục)**, định nghĩa **hành động nào (đọc, ghi, thực thi) được phép trên tài nguyên đó**. Chúng được thiết lập qua chmod hoặc ACL, và kiểm tra bởi kernel.

- **Privileges** là **quyền hạn được cấp cho người dùng hoặc nhóm**, **cho phép họ thực hiện hành động trên tài nguyên**. Sudo cấp **privileges tạm thời để vượt qua permissions thông thường**.

T
> Tóm lại, **permissions là thuộc tính của đối tượng**, còn **privileges là khả năng của chủ thể để tương tác với đối tượng đó**. Hiểu rõ sự khác biệt giúp quản lý bảo mật hiệu quả hơn.