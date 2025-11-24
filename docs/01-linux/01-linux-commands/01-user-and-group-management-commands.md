# 1. Quản lý người dùng và nhóm 

# Liệt Kê Tất Cả Người Dùng Cục Bộ (Local Users)
Để tìm danh sách các tài khoản người dùng có trên hệ thống, có thể dùng các cách sau:
- Sử dụng tệp `/etc/passwd`: Tệp này chứa thông tin cơ bản của tất cả người dùng. 
![](/01-linux/images/user-and-group-management/linux_user_mgt-1.png)

- Sử dụng lệnh `getent`: Lệnh này truy vấn cơ sở dữ liệu người dùng của hệ thống, bao gồm cả người dùng cục bộ và người dùng từ các dịch vụ mạng (như LDAP). Lệnh này hoạt động trên nhiều hệ thống xác thực khác nhau .

![](/01-linux/images/user-and-group-management/linux_user_mgt-getent.png)

- **Liệt kê người dùng thông thường (Regular Users):** Để loại bỏ các tài khoản hệ thống (system accounts) như `bin`, `daemon`, `sys`

+ Ví dụ : Lọc người dùng có UID (User ID) từ 1000 trở lên, vì các UID thấp hơn được dành cho tài khoản hệ thống.

![](/01-linux/images/user-and-group-management/linux_user_mgt-regular-user.png)

- Sử dụng lệnh compgen được tích hợp sẵn của shel giúp liệt kê tất cả tên người dùng được biết đến trên hệ thống 

![](/01-linux/images/user-and-group-management/linux_user_mgt-shell-builtin.png)


# Quản lý nhóm (Group Management)

## Xác định nhóm của người dùng
- Để xem người dùng là thành viên của những nhóm nào, dùng lệnh `groups <username>`:

![](/01-linux/images/user-and-group-management/group-mgmt-1.png)

> Trong Linux, nhóm users là một nhóm mặc định được thiết kế để bao gồm các tài khoản người dùng thông thường (không phải quản trị viên). Nó đóng vai trò là một cách cơ bản để tổ chức quyền hạn của người dùng và quản lý quyền truy cập vào các tài nguyên được chia sẻ.

Trên một số bản phân phối Linux, các tài khoản người dùng mới được tạo sẽ tự động được thêm vào nhóm users.

Các thành viên của nhóm users có quyền truy cập tiêu chuẩn: họ có thể đọc và ghi tệp trong các thư mục của riêng họ nhưng không thể thực hiện các tác vụ quản trị.

Họ thiếu đặc quyền sudo trừ khi được thêm vào các nhóm như sudo hoặc wheel như được trình bày ở phần dưới.
>

- Để xem tất cả thành viên của một nhóm cụ thể `getent group <groupname>`:

![](/01-linux/images/user-and-group-management/group-mgmt-2.png)

## Thêm/Xóa người dùng khỏi nhóm 
### Thêm người dùng vào nhóm
Ta có  thể sử dụng lệnh `usermod` để thêm người dùng vào group có sẵn trong Linux 

```
# usermod -aG <groupname> <username>

-a: Cờ append (thêm vào).

-G: Chỉ định các groups bổ sung.

Việc sử dụng -aG rất quan trọng, nếu chỉ dùng -G mà không có -a, người dùng sẽ bị xóa khỏi tất cả các nhóm khác.
```
### Xóa người dùng khỏi nhóm

```
# usermod -rG <groupname> <username>

# gpasswd  -d <username> <groupname>
```

# Thêm Người Dùng Mới và Cấp Quyền Admin (sudo)

## Tạo người dùng và đặt mật khẩu
### Tạo tài khoản người dùng mới
```
# sudo useradd -m <username>
Cờ -m (--create-home) sẽ tạo thư mục Home cho người dùng trong /home/<username>.
```


### Xác minh người dùng đã được tạo
```
# sudo id <username>

```

### Đặt mật khẩu cho người dùng mới
```
# sudo passwd <username>
```

Sau bước này, người dùng đã có thể đăng nhập, nhưng chưa thể chạy lệnh `sudo`.

## Cấp quyền Admin (sudo)
Để cho phép người dùng chạy các lệnh với quyền quản trị, cần thêm họ vào một nhóm có quyền sudo.

- Trên Debian/Ubuntu: Nhóm mặc định là `sudo`.

```
# usermod -aG sudo <username>
```

- Trên SUSE Linux Enterprise (và nhiều distro khác): Nhóm mặc định thường là wheel.

```
 # usermod -aG wheel <username>
```
> Lưu ý: Nếu sử dụng nhóm wheel, có thể cần đảm bảo nhóm này đã được kích hoạt trong tệp cấu hình /etc/sudoers.

## Quản lý Quyền `sudo` qua Tệp `sudoers`
- Luôn sử dụng lệnh visudo để chỉnh sửa tệp /etc/sudoers. Lệnh này kiểm tra cú pháp trước khi lưu, tránh khóa quyền sudo của bạn.
~[](/01-linux/images/user-and-group-management/sudo-1.png)
- Kích hoạt nhóm wheel (nếu cần): Dùng `visudo` để bỏ ghi chú dòng sau trong `/etc/sudoers`:

~[](/01-linux/images/user-and-group-management/sudo-2.png)
```
%wheel ALL=(ALL) ALL
```
(Dòng này cho phép thành viên nhóm wheel chạy mọi lệnh, yêu cầu mật khẩu của chính họ).

~[](/01-linux/images/user-and-group-management/sudo-3.png)


- **Không cần mật khẩu (NOPASSWD):** Bạn có thể cấu hình để nhóm hoặc người dùng không cần nhập mật khẩu khi dùng `sudo`:

```
%groupname ALL=(ALL:ALL) NOPASSWD: ALL
```

~[](/01-linux/images/user-and-group-management/sudo-4.png)

**Thêm người dùng trực tiếp vào sudoers:** Thay vì dùng nhóm, có thể cấp quyền trực tiếp cho một người dùng:
```
testuser1 ALL=(ALL) NOPASSWD:ALL
```


- Thay vì sửa đổi `/etc/sudoers` gốc, hãy tạo một tệp mới trong thư mục `/etc/sudoers.d/`. Các tệp trong thư mục này sẽ tự động được đưa vào cấu hình `sudoers`.

~[](/01-linux/images/user-and-group-management/sudo-5.png)
