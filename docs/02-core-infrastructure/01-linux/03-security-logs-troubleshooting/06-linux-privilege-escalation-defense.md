# Linux Privilege Escalation Defense

## Overview

Privilege escalation là quá trình một account hoặc process có quyền thấp giành được quyền cao hơn do lỗi cấu hình, lỗ hổng phần mềm hoặc chính sách phân quyền yếu. Trong vận hành Linux, nên đọc chủ đề này theo góc phòng thủ: hiểu các đường leo quyền phổ biến để audit, harden và phát hiện sớm.

Không dùng checklist này như exploit runbook. Với CVE, kernel exploit hoặc hành vi phiên bản cụ thể, luôn kiểm tra advisory chính thức, môi trường lab và rollback plan trước khi áp dụng vào production.

## Attack Surface Map

| Nhóm rủi ro | Lỗi thường gặp | Tín hiệu cần kiểm tra |
|---|---|---|
| Sudo | User có `NOPASSWD`, được chạy binary quá rộng hoặc giữ biến môi trường nguy hiểm | `sudo -l`, `/etc/sudoers`, `/etc/sudoers.d/` |
| SUID/SGID | Binary owner `root` có SUID/SGID không cần thiết | `find` theo permission bit, so với baseline |
| Linux capabilities | Binary có capability mạnh như `cap_setuid`, `cap_dac_read_search`, `cap_sys_admin` | `getcap -r /` |
| Writable path | Directory/script trong `$PATH`, cron hoặc service file writable bởi user thường | permission, owner, group, ACL |
| Cron/systemd timer | Scheduled job chạy quyền cao nhưng gọi script không kiểm soát | `/etc/crontab`, `/etc/cron.*`, systemd timer |
| NFS | Export cấu hình sai như cho ghi rộng hoặc không squash root | `/etc/exports`, mount option |
| Secret leakage | Token/password nằm trong history, env, config, backup file | shell history, `.env`, config, archive |
| Kernel/package cũ | Kernel hoặc package có lỗ hổng đã biết | inventory, patch level, advisory |

## First Enumeration Signals

Các lệnh dưới đây là read-only và hữu ích cho cả audit lẫn incident response:

```bash
hostname
uname -a
cat /etc/os-release
id
groups
who
w
env
ip addr
ip route
ss -tulpn
ps aux
```

Kiểm tra quyền hiện tại của user:

```bash
sudo -l
getent passwd
getent group
```

Tìm nhanh các điểm cần audit:

```bash
find / -xdev -perm -4000 -type f -ls 2>/dev/null
find / -xdev -perm -2000 -type f -ls 2>/dev/null
getcap -r / 2>/dev/null
find / -xdev -writable -type d 2>/dev/null
```

Với filesystem lớn, chạy theo mount point quan trọng trước để tránh tạo tải không cần thiết.

## Sudo Review

Sudo là đường leo quyền hợp lệ nếu policy quá rộng. Khi review:

- Tránh cấp `ALL=(ALL) NOPASSWD: ALL` cho user thường.
- Hạn chế command theo đường dẫn tuyệt đối, ví dụ `/usr/bin/systemctl restart nginx`.
- Không cho phép editor, shell, interpreter hoặc tool có khả năng spawn shell nếu không thật sự cần.
- Review `env_keep`, đặc biệt với biến như `LD_PRELOAD`, `LD_LIBRARY_PATH`, `PYTHONPATH`.
- Dùng group theo role, không gán quyền trực tiếp cho từng user nếu có thể.

Kiểm tra policy:

```bash
sudo visudo -c
sudo grep -R "NOPASSWD\\|ALL=(ALL)" /etc/sudoers /etc/sudoers.d 2>/dev/null
```

## SUID, SGID Và Capabilities

SUID/SGID cho phép binary chạy với effective UID/GID của owner/group. Đây là cơ chế hợp lệ, nhưng cần baseline rõ.

Audit SUID/SGID:

```bash
find / -xdev -perm -4000 -type f -ls 2>/dev/null
find / -xdev -perm -2000 -type f -ls 2>/dev/null
```

Audit capabilities:

```bash
getcap -r / 2>/dev/null
```

Hướng xử lý:

- So sánh với baseline của distro hoặc golden image.
- Gỡ SUID/SGID khỏi binary tự build nếu không có use case rõ.
- Tránh gán capability rộng; ưu tiên service chạy user riêng và quyền tối thiểu.
- Theo dõi thay đổi permission bằng `auditd`, file integrity monitoring hoặc EDR.

## Cron, PATH Và Writable Script

Cron job, systemd unit và maintenance script thường trở thành điểm yếu khi script chạy quyền cao nhưng nằm ở path writable.

Kiểm tra:

```bash
cat /etc/crontab
ls -la /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.weekly
systemctl list-timers --all
systemctl cat <service>
```

Checklist:

- Script chạy bởi root phải owner là `root:root`.
- Không cho group/world writable trên script, directory cha và file config liên quan.
- Dùng absolute path trong script thay vì phụ thuộc vào `$PATH`.
- Không đặt secret trong command line hoặc crontab plaintext.

## NFS Và Shared Filesystem

Với NFS, quyền client không thể thay thế kiểm soát ở server. Cần review:

```bash
cat /etc/exports
exportfs -v
mount | grep nfs
```

Khuyến nghị:

- Tránh export ghi rộng cho subnet lớn.
- Dùng `root_squash` trừ khi có lý do vận hành rất rõ.
- Giới hạn client theo subnet/host cụ thể.
- Tách share dùng cho app khỏi share dùng cho admin.

## Secret And History Hygiene

Các nguồn hay lộ secret:

- `~/.bash_history`, `~/.zsh_history`.
- File `.env`, backup `.bak`, archive `.tar.gz`, dump database.
- Command line process chứa password/token.
- Config app world-readable.

Kiểm tra có kiểm soát:

```bash
find /home /root -type f \\( -name "*history" -o -name ".env" -o -name "*.bak" \\) -ls 2>/dev/null
ps auxww
```

Không paste secret thật vào ticket, chat hoặc note. Nếu phát hiện credential thật, rotate credential và ghi nhận bằng placeholder.

## Hardening Checklist

- Patch kernel và package theo vòng đời hỗ trợ của distro.
- Bật MFA/SSH key policy cho access quản trị nếu nền tảng hỗ trợ.
- Tắt SSH password login khi có thể; giới hạn user/group được SSH.
- Dùng `sudo` thay vì shared root password.
- Đặt umask phù hợp cho user/service tạo file nhạy cảm.
- Chạy service bằng user riêng, không dùng root nếu không cần.
- Bật audit cho thay đổi sudoers, SUID/SGID, service file và cron.
- Giữ baseline định kỳ cho SUID/SGID/capabilities/listening ports.

## Detection And Evidence

Tín hiệu đáng chú ý:

- User mới, UID `0` bất thường, group `sudo`/`wheel` thay đổi.
- SUID/SGID file mới xuất hiện ngoài baseline.
- Binary có capability mạnh mới được gán.
- Cron hoặc systemd unit lạ.
- Process chạy từ `/tmp`, `/var/tmp`, home directory hoặc path không chuẩn.
- SSH login ngoài giờ hoặc từ nguồn không quen thuộc.

Lệnh kiểm tra nhanh:

```bash
awk -F: '$3 == 0 {print $1":"$3":"$6":"$7}' /etc/passwd
last -a | head -50
journalctl --since "24 hours ago" | grep -Ei "sudo|su|useradd|passwd|sshd"
find / -xdev -perm -4000 -type f -mtime -7 -ls 2>/dev/null
```

## Related Pages

- [User, Permission và Access Control Cơ Bản](../01-core-system/02-users-permissions-access.md)
- [SUID, SGID, SELinux, PAM, auditd và Hardening](./03-suid-sgid-selinux-pam-auditd-hardening.md)
- [Linux Incident Response Live Triage](./07-linux-incident-response-live-triage.md)
- [Logs, journald, rsyslog và logrotate](./01-logs-journald-rsyslog-logrotate.md)
