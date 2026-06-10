# SUID, SGID, SELinux, PAM, auditd và Hardening

## 1. Privilege Boundary

Linux security không chỉ là file permission. Một server an toàn cần kiểm soát privilege boundary:

- Ai được login.
- Ai được `sudo`.
- Binary nào có SUID/SGID.
- Mandatory Access Control như SELinux/AppArmor.
- Authentication policy qua PAM.
- Audit trail qua auditd/journald.

## 2. SUID, SGID và Sticky Bit

| Bit | Ví dụ hiển thị | Ý nghĩa |
| --- | --- | --- |
| SUID | `-rwsr-xr-x` | File chạy với quyền owner |
| SGID | `-rwxr-sr-x` | File chạy với quyền group hoặc directory kế thừa group |
| Sticky | `drwxrwxrwt` | Directory chỉ owner/root được xóa file |

Ví dụ hợp lệ thường gặp:

```bash
ls -l /usr/bin/passwd
ls -ld /tmp
```

Set bit:

```bash
chmod u+s /path/to/bin
chmod g+s /srv/shared
chmod +t /srv/tmp
```

## 3. Audit SUID/SGID

```bash
# SUID root trong filesystem hiện tại
find / -xdev -perm -4000 -type f -ls 2>/dev/null

# SGID
find / -xdev -perm -2000 -type f -ls 2>/dev/null

# World-writable directory không có sticky bit
find / -xdev -type d -perm -0002 ! -perm -1000 -ls 2>/dev/null
```

Baseline nên lưu theo host role:

```bash
find / -xdev -perm -4000 -type f -print 2>/dev/null | sort | sudo tee /root/suid-baseline.txt
```

SUID bất thường khi:

- Nằm trong `/tmp`, `/var/tmp`, home user, app upload directory.
- Owner là root nhưng binary không thuộc package.
- Mới xuất hiện sau incident/change không rõ.
- Permission hoặc checksum khác baseline/package database.

Kiểm tra package owner:

```bash
# Debian/Ubuntu
dpkg -S /usr/bin/passwd
debsums -s passwd 2>/dev/null

# RHEL/CentOS/Fedora
rpm -qf /usr/bin/passwd
rpm -V passwd
```

Không remove SUID/SGID bừa theo kết quả `find`. Baseline hợp lệ khác nhau theo distro, package set và role của host; cần đối chiếu package database/change history trước khi xử lý.

## 4. SELinux

SELinux là Mandatory Access Control phổ biến trên RHEL-family.

Mode:

```bash
getenforce
sestatus
```

| Mode | Ý nghĩa |
| --- | --- |
| Enforcing | Chặn vi phạm policy |
| Permissive | Log vi phạm nhưng không chặn |
| Disabled | Tắt SELinux |

Context:

```bash
ls -Z /var/www/html
ps -eZ | grep httpd
```

Restore context:

```bash
sudo restorecon -RFv /var/www/html
```

Quản lý fcontext:

```bash
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/www(/.*)?'
sudo restorecon -RFv /srv/www
```

Điều tra deny:

```bash
sudo ausearch -m AVC,USER_AVC -ts recent
sudo audit2why -a
sudo audit2allow -a
```

Notes:

- Không tắt SELinux vĩnh viễn chỉ vì lỗi permission.
- Ưu tiên sửa context/boolean/policy đúng.
- `audit2allow` cần review kỹ trước khi áp dụng.

## 5. AppArmor Overview

AppArmor phổ biến trên Ubuntu/Debian.

```bash
aa-status
sudo aa-complain <profile>
sudo aa-enforce <profile>
```

Profile thường nằm dưới:

```text
/etc/apparmor.d/
```

## 6. PAM

PAM quản lý authentication policy cho login, SSH, sudo và nhiều service.

Path:

```text
/etc/pam.d/
```

Ví dụ file:

```bash
cat /etc/pam.d/sshd
cat /etc/pam.d/sudo
```

Use case thường gặp:

- Password quality: `pam_pwquality`.
- Login failure lockout: `pam_faillock`.
- Giới hạn resource/session: `pam_limits`.

Ví dụ kiểm tra policy liên quan:

```bash
grep -R "pam_pwquality\\|pam_faillock" /etc/pam.d/ /etc/security/ 2>/dev/null
cat /etc/security/pwquality.conf 2>/dev/null
faillock --user <username> 2>/dev/null
```

Production notes:

- Backup file PAM trước khi sửa.
- Giữ root session đang mở.
- Test login bằng session mới trước khi logout session cũ.
- Lỗi PAM có thể lock admin khỏi server.

## 7. auditd

`auditd` ghi nhận sự kiện bảo mật ở mức kernel/user-space.

```bash
sudo systemctl status auditd
sudo auditctl -l
sudo ausearch -m USER_LOGIN,USER_AUTH,USER_ACCT
sudo aureport -au
```

Rule runtime:

```bash
sudo auditctl -w /etc/passwd -p wa -k identity
sudo auditctl -w /etc/sudoers -p wa -k sudoers
```

Persistent rules:

```text
/etc/audit/rules.d/*.rules
```

Ví dụ:

```text
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers
```

Apply:

```bash
sudo augenrules --load
sudo auditctl -l
```

Search:

```bash
sudo ausearch -k identity
sudo ausearch -f /etc/passwd
sudo aureport -f
```

## 8. SSH Hardening Checklist

`/etc/ssh/sshd_config`:

```text
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowGroups ssh-admins
MaxAuthTries 3
```

Validate:

```bash
sudo sshd -t
sudo systemctl reload sshd
```

Safety:

- Test login bằng session mới.
- Không đóng session hiện tại trước khi xác nhận.
- Với bastion, log đầy đủ auth events.

## 9. Basic Hardening Checklist

- Patch OS/package định kỳ.
- Tắt service không dùng.
- Dùng firewall allowlist.
- Quản lý sudo theo group và command.
- Audit SUID/SGID định kỳ.
- Bật SELinux/AppArmor nếu distro hỗ trợ.
- Bật audit log cho file nhạy cảm.
- Quản lý SSH key lifecycle.
- Đồng bộ thời gian bằng NTP/chrony.
- Gửi log quan trọng về log server nếu có.
