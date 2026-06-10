# User, Permission và Access Control Cơ Bản

## 1. User và Group

Linux phân quyền chủ yếu dựa trên user, group và permission của file. Hai nhóm user thường gặp:

- System user: chạy daemon hoặc tác vụ hệ thống, thường không dùng để login trực tiếp.
- Human user: tài khoản người dùng hoặc admin dùng để login.

`root` có UID `0` và có toàn quyền trên hệ thống. Trong vận hành production, nên dùng user thường + `sudo`, hạn chế login trực tiếp bằng `root`.

## 2. Account Files Trong `/etc`

| File | Nội dung | Quyền truy cập |
| --- | --- | --- |
| `/etc/passwd` | Username, UID, GID, home, shell | User thường đọc được |
| `/etc/shadow` | Password hash và password aging | Chỉ root đọc |
| `/etc/group` | Group, GID, member | User thường đọc được |
| `/etc/gshadow` | Group password/admin/member nâng cao | Chỉ root đọc |
| `/etc/sudoers` | Policy `sudo` chính | Sửa bằng `visudo` |
| `/etc/sudoers.d/` | Policy `sudo` tách nhỏ theo file | Sửa bằng `visudo -f` |
| `/etc/login.defs` | Default policy khi tạo account | Root sửa |
| `/etc/skel` | Template copy vào home user mới | Root quản lý |

Ví dụ xem account:

```bash
getent passwd <user>
getent group <group>
id <user>
```

## 3. Quản Lý User

```bash
# Tạo user có home directory
sudo useradd -m -s /bin/bash <username>

# Đặt hoặc đổi mật khẩu
sudo passwd <username>

# Thêm user vào group phụ
sudo usermod -aG <groupname> <username>

# Khóa/mở khóa user
sudo usermod -L <username>
sudo usermod -U <username>

# Xóa user và home directory
sudo userdel -r <username>
```

> Trong production, nếu tài khoản liên quan tới audit, incident hoặc người dùng đã nghỉ, thường nên khóa account trước khi xóa. Việc xóa ngay có thể làm mất ngữ cảnh owner, home directory, SSH key hoặc evidence cần đối chiếu.

Password aging:

```bash
# Xem policy
sudo chage -l <username>

# Bắt đổi mật khẩu ở lần login tiếp theo
sudo chage -d 0 <username>

# Set max age 90 ngày, warning 14 ngày
sudo chage -M 90 -W 14 <username>
```

## 4. Quản Lý Group

```bash
sudo groupadd <groupname>
sudo groupmod -n <newname> <oldname>
sudo groupdel <groupname>
sudo gpasswd -a <username> <groupname>
sudo gpasswd -d <username> <groupname>
```

> Lưu ý: sau khi thêm user vào group, user thường cần logout/login lại để session nhận group mới.

## 5. `su` và `sudo`

`su` chuyển sang user khác, thường là root:

```bash
su -
su - <username>
```

`sudo` cho phép chạy command với quyền cao hơn dựa trên policy:

```bash
sudo -l
sudo -i
sudo systemctl restart nginx
```

Sửa sudo policy bằng `visudo`, không sửa trực tiếp bằng editor thường:

```bash
sudo visudo
sudo visudo -f /etc/sudoers.d/<name>
sudo visudo -c
```

Ví dụ rule:

```text
%admin ALL=(ALL:ALL) ALL
deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart app.service
```

Production notes:

- Cấp quyền theo group thay vì từng user rời rạc.
- Ưu tiên command allowlist cho automation account.
- Tránh `NOPASSWD: ALL` nếu không có lý do rõ.

## 6. File Permission và Ownership

Permission cơ bản gồm `read`, `write`, `execute` cho ba nhóm:

- User/owner
- Group
- Other

Ví dụ output:

```text
-rw-r----- 1 app app 1200 May 20 10:00 config.env
drwxr-x--- 2 app app 4096 May 20 10:00 logs
```

Ký tự đầu tiên là file type:

| Ký tự | Loại |
| --- | --- |
| `-` | Regular file |
| `d` | Directory |
| `l` | Symbolic link |
| `c` | Character device |
| `b` | Block device |
| `p` | FIFO/pipe |
| `s` | Socket |

## 7. `chmod`, `chown`, `chgrp`, `umask`

```bash
# Symbolic mode
chmod u+rwx,g+rx,o-rwx file

# Numeric mode
chmod 640 config.env
chmod 750 scripts/

# Recursive, dùng cẩn thận
chmod -R g+rwX /srv/app

# Đổi owner/group
chown app:app config.env
chown -R app:app /srv/app
chgrp nginx /srv/app/logs
```

`umask` quyết định permission mặc định khi tạo file/directory:

```bash
umask
umask 027
```

Ví dụ `umask 027` thường tạo file `640`, directory `750`.

## 8. SUID, SGID và Sticky Bit

Special permission cần hiểu ở mức concept trong file này. Audit/hardening chi tiết nằm ở [SUID, SGID, SELinux, PAM, auditd và Hardening](../03-security-logs-troubleshooting/03-suid-sgid-selinux-pam-auditd-hardening.md).

| Bit | Áp dụng | Ý nghĩa |
| --- | --- | --- |
| SUID | File executable | Chạy với quyền owner của file |
| SGID | File executable | Chạy với quyền group của file |
| SGID | Directory | File mới kế thừa group của directory |
| Sticky bit | Directory | Chỉ owner/root xóa hoặc rename file bên trong |

```bash
# SUID
chmod u+s /path/to/bin
chmod 4755 /path/to/bin

# SGID
chmod g+s /srv/shared
chmod 2770 /srv/shared

# Sticky bit
chmod +t /srv/tmp
chmod 1777 /srv/tmp

# Kiểm tra
ls -ld /tmp /srv/shared
find / -perm -4000 -type f -xdev 2>/dev/null
```

Rủi ro vận hành:

- SUID root bất thường có thể mở đường leo quyền.
- SGID trên shared directory hữu ích nhưng cần group ownership rõ.
- Sticky bit nên dùng cho thư mục shared write như `/tmp`.

## 9. Inode, Hard Link và Soft Link

Linux filesystem dùng inode để lưu metadata của file. Tên file là entry trong directory trỏ tới inode.

```bash
ls -li file.txt
stat file.txt
```

Hard link:

- Trỏ trực tiếp tới cùng inode.
- Không dùng cross-filesystem.
- Không dùng cho directory trong use case thông thường.

```bash
ln file.txt file-hardlink.txt
ls -li file.txt file-hardlink.txt
```

Soft link/symlink:

- Là file riêng trỏ tới path khác.
- Có thể trỏ cross-filesystem hoặc tới directory.
- Bị broken nếu target bị xóa/đổi path.

```bash
ln -s /opt/app/current app-current
readlink -f app-current
find /path -type l
```

## 10. Troubleshooting Permission Denied

```bash
id
whoami
ls -lah <path>
namei -l <path>
getfacl <path>
sudo -l
mount | grep <mountpoint>
getenforce
```

Các nguyên nhân thường gặp:

- User không thuộc group đúng.
- Directory cha thiếu execute bit.
- File ownership sai sau khi copy/restore.
- ACL hoặc SELinux/AppArmor chặn.
- Filesystem mount read-only hoặc có option giới hạn quyền.
