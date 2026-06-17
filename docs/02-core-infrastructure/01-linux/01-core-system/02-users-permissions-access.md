# User, Permission và Access Control Cơ Bản

## 1. User và Group

Linux phân quyền chủ yếu dựa trên user, group và permission của file. Hai nhóm user thường gặp:

- System user: chạy daemon hoặc tác vụ hệ thống, thường không dùng để login trực tiếp.
- Human user: tài khoản người dùng hoặc admin dùng để login.

`root` có UID `0` và có toàn quyền trên hệ thống. Trong vận hành production, nên dùng user thường + `sudo`, hạn chế login trực tiếp bằng `root`.

Không nên hard-code rằng mọi distro đều dùng cùng một ngưỡng UID/GID cho human user, system user hoặc service account. Dùng `getent`, `id`, shell login và owner của process để xác nhận account đang phục vụ mục đích gì. Service account thường không cần interactive shell; nếu chỉ dùng để chạy daemon, đặt shell như `/usr/sbin/nologin` hoặc `/sbin/nologin` giúp giảm bề mặt login.

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
sudo getent shadow <user>
getent group <group>
sudo getent gshadow <group>
id <user>
```

`/etc/passwd` và `/etc/group` dùng field phân tách bằng dấu `:`. Trường password trong `/etc/passwd` thường là `x`, nghĩa là password hash nằm trong `/etc/shadow`; không phải password thật. Khi kiểm tra production, ưu tiên `getent` thay vì chỉ `grep /etc/passwd` để không bỏ sót account đến từ NSS backend như LDAP/SSSD.

Một record `/etc/passwd` có 7 field chính: username, password placeholder, UID, primary GID, comment/GECOS, home directory và login shell. Một record `/etc/shadow` có password hash/lock marker, ngày đổi password gần nhất, minimum/maximum age, warning, inactive period và account expiration. Không đọc trực tiếp `/etc/shadow` vào ticket/chat nếu có hash thật; chỉ ghi trạng thái cần thiết như locked/expired/aging policy.

Trước khi tạo account hàng loạt, kiểm tra default của distro:

```bash
grep -E '^(UID_MIN|UID_MAX|SYS_UID_MIN|SYS_UID_MAX|GID_MIN|GID_MAX|CREATE_HOME|UMASK|ENCRYPT_METHOD|PASS_)' /etc/login.defs
useradd -D
ls -la /etc/skel
```

`useradd -D` đọc default từ `/etc/default/useradd` và cũng có thể thay đổi default này. Với production, ưu tiên quản lý default account bằng configuration management thay vì sửa thủ công từng host; nếu sửa `/etc/skel`, nhớ rằng thay đổi chỉ áp dụng cho user tạo sau đó, không tự migrate vào home user hiện có.

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

Pre-check trước khi tạo hoặc xóa account:

```bash
getent passwd <username>
getent group <groupname>
id <username>
sudo find / -xdev -user <username> -ls 2>/dev/null
```

`useradd` chịu ảnh hưởng bởi default trong `/etc/login.defs`, `/etc/default/useradd` và nội dung `/etc/skel`. Khi tạo home directory, các dotfile/template trong `/etc/skel` được copy sang home mới, nên không đặt secret hoặc token cá nhân vào skeleton. Account mới có thể chưa login được cho đến khi password hoặc phương thức SSH key/authentication phù hợp được cấu hình.

`userdel -r` có blast radius vì xóa home directory và mail spool của user. Với account production, rollback thường là khôi phục từ backup/home snapshot và tạo lại UID/GID đúng; vì vậy hãy ghi lại UID/GID, group membership và owner của dữ liệu trước khi xóa.

Password aging:

```bash
# Xem policy
sudo chage -l <username>
sudo passwd -S <username>

# Bắt đổi mật khẩu ở lần login tiếp theo
sudo chage -d 0 <username>
sudo passwd -e <username>

# Set max age 90 ngày, warning 14 ngày
sudo chage -M 90 -W 14 <username>
```

`passwd -l`/`usermod -L` thường thêm `!` trước password hash trong `/etc/shadow`, chặn password login nhưng không nhất thiết vô hiệu hóa mọi cơ chế như SSH key, cron hoặc process đang chạy. Khi offboard user, cần kết hợp lock/expire account, thu hồi SSH key/token, dừng session/process nếu policy yêu cầu và lưu evidence trước khi xóa.

## 4. Quản Lý Group

```bash
sudo groupadd <groupname>
sudo groupmod -n <newname> <oldname>
sudo groupdel <groupname>
sudo gpasswd -a <username> <groupname>
sudo gpasswd -d <username> <groupname>
getent group <groupname>
```

> Lưu ý: sau khi thêm user vào group, user thường cần logout/login lại để session nhận group mới.

Nếu cần đổi primary group tạm thời trong phiên hiện tại, dùng `newgrp <groupname>` sau khi xác nhận user là member của group đó. Cách này hữu ích cho thao tác thủ công ngắn hạn, nhưng không thay thế việc kiểm soát group membership và service user cố định trong production.

Không dùng group password trong `/etc/gshadow` cho production. Group password thường bị chia sẻ giữa nhiều người, làm mất accountability. Cấp quyền bằng group membership rõ ràng, qua `usermod -aG` hoặc `gpasswd -a`, và audit bằng `id`, `groups`, `getent group`.

Trước khi xóa hoặc đổi GID của group, ghi lại GID cũ và tìm file còn gắn với GID đó:

```bash
old_gid=$(getent group <groupname> | cut -d: -f3)
sudo find / -xdev -gid "$old_gid" -ls 2>/dev/null
```

`groupdel` xóa group database entry, nhưng file đã tồn tại có thể còn numeric GID cũ. Nếu GID được tái sử dụng sau này, dữ liệu cũ có thể vô tình thuộc về group mới.

## 5. `su` và `sudo`

`su` chuyển sang user khác, thường là root:

```bash
su -
su - <username>
```

Ưu tiên `su -` thay vì `su` trần khi thật sự phải chuyển user, vì login shell nạp environment của target user. Dùng lại environment của user cũ trong phiên root có thể gây lỗi `PATH`, `HOME`, config tool hoặc ghi file nhầm owner. Trong production hiện đại, `su` cũng làm tăng rủi ro chia sẻ root password; `sudo` thường dễ audit và phân quyền hơn.

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
- Nhớ rằng `sudo` thường cache xác thực trong một khoảng ngắn; khi rời terminal shared/bastion, dùng `sudo -k` để hủy timestamp nếu cần.
- Sudo giúp non-repudiation tốt hơn shared root password vì log thường ghi user gốc, TTY, working directory, target user và command. Cần forward log auth/sudo về log server nếu host quan trọng.
- Cấu hình rule mới trong `/etc/sudoers.d/` bằng `visudo -f`, kiểm tra bằng `visudo -c`, rồi test `sudo -l -U <user>` trước khi giao quyền.

Audit access hiện tại:

```bash
who
w
last -a | head -50
lastlog | head -50
journalctl --since "24 hours ago" | grep -Ei "sudo|su|sshd|authentication"
```

Nếu cần chặn login user thường trong tình huống khẩn cấp, `/etc/nologin` có thể được dùng như một guardrail tạm thời. Đây là thao tác ảnh hưởng rộng: ghi rõ message, giữ console/root session, thông báo owner và xóa file sau khi incident/change kết thúc.

```bash
printf '%s\n' "Temporary maintenance, contact platform team." | sudo tee /etc/nologin
ls -l /etc/nologin
sudo rm -i /etc/nologin
```

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

Ý nghĩa permission trên directory khác file thường:

| Bit | File thường | Directory |
| --- | --- | --- |
| `r` | Đọc nội dung file | Liệt kê tên entry trong directory |
| `w` | Ghi/truncate nội dung file | Tạo, xóa hoặc rename entry nếu có quyền execute trên directory |
| `x` | Execute file | Traverse/search directory để đi qua path hoặc truy cập entry đã biết tên |

Một lỗi phổ biến: có quyền ghi trên file nhưng không có quyền execute trên directory cha thì vẫn không truy cập được path; có quyền ghi trên directory có thể xóa/rename entry ngay cả khi không có quyền ghi vào nội dung file, trừ khi sticky bit hoặc policy khác chặn.

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
chown :nginx /srv/app/logs
chown -R app:app /srv/app
chgrp nginx /srv/app/logs
```

`chown user:group path` đổi cả owner và group. `chown :group path` chỉ đổi group, tương đương nhiều tình huống dùng `chgrp`, nhưng vẫn cần quyền phù hợp và phải xác nhận group tồn tại bằng `getent group <groupname>`.

`umask` quyết định permission mặc định khi tạo file/directory:

```bash
umask
umask 027
```

Ví dụ `umask 027` thường tạo file `640`, directory `750`.

Guardrails:

- Dùng symbolic mode khi chỉ muốn thêm/bớt một bit, ví dụ `chmod u+x script.sh`.
- Dùng numeric mode khi muốn đặt trạng thái chính xác, ví dụ `chmod 0640 config.env`.
- Với recursive change, chạy kiểm tra trước bằng `find <path> -ls` hoặc giới hạn scope rõ; tránh `chmod -R 777` vì phá vỡ ownership boundary và audit expectation.
- `X` trong `chmod g+rwX` chỉ thêm execute cho directory hoặc file đã có execute bit, an toàn hơn `x` khi xử lý cây thư mục có cả file dữ liệu và script.

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

Temporary directory cần phân biệt:

| Path | Hành vi vận hành |
| --- | --- |
| `/tmp` | Scratch ngắn hạn; có thể bị dọn khi reboot hoặc theo policy cleanup |
| `/var/tmp` | Temporary nhưng thường được giữ qua reboot lâu hơn `/tmp` |
| `/run` | Runtime state của phiên boot hiện tại, như PID/socket; phải coi là volatile |

Không lưu state quan trọng, secret dài hạn hoặc file duy nhất vào các path này. Với directory shared writable, sticky bit là guardrail bắt buộc để user không xóa/rename file của user khác.

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
- Relative target được resolve tương đối theo vị trí của symlink, không phải working directory hiện tại của người dùng.
- Mode thường hiển thị `lrwxrwxrwx`, nhưng quyền truy cập khi dereference phụ thuộc vào target và directory cha, không phải mode hiển thị của symlink.

```bash
ln -s /opt/app/current app-current
readlink -f app-current
find /path -type l
```

Khi di chuyển symlink, kiểm tra lại bằng `readlink` hoặc `readlink -f`. Symlink relative có thể trỏ sang file khác cùng tên ở vị trí mới hoặc trở thành broken link; symlink absolute bền hơn khi di chuyển link nhưng kém portable hơn khi di chuyển cả cây thư mục.

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
