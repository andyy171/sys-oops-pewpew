# Linux Security Policy Baseline

## Overview

Linux security policy là tập quy tắc vận hành để giảm rủi ro từ account, permission, storage, automation, network, software supply chain và incident response. Note này chuyển hóa phần reusable từ `_inbox/Linux-cyber.docx` theo hướng phòng thủ và vận hành production.

Không dùng note này như exploit guide. Với hardening production, luôn test trên môi trường lab/staging, có rollback, và giữ session quản trị dự phòng trước khi thay đổi authentication/firewall/PAM.

## Policy Areas

| Mảng | Mục tiêu | Note liên quan |
| --- | --- | --- |
| Account security | kiểm soát user, group, sudo, password/key policy | [Users, permissions and access](../01-core-system/02-users-permissions-access.md) |
| File permission | owner/group/mode, SUID/SGID/sticky bit, ACL | [SUID, SGID, SELinux, PAM, auditd](./03-suid-sgid-selinux-pam-auditd-hardening.md) |
| Storage security | mount option, encryption, backup, network storage permission | [Disk, filesystem, mount and swap](../02-storage-networking/01-disk-filesystem-mount-swap.md) |
| Automation security | cron, systemd timer, script owner, secret handling | [Bash scripting, cron and systemd timer](../04-shell-automation-advanced/03-bash-scripting-cron-systemd-timer.md) |
| Network security | SSH, firewall, exposed services, listening ports | [IP, route, DNS and firewall](../02-storage-networking/04-ip-route-dns-firewall.md) |
| Software management | repository trust, patching, package inventory | [Package, process and service management](../01-core-system/03-package-process-service.md) |
| Detection/response | logs, audit, triage, evidence handling | [Linux incident response live triage](./07-linux-incident-response-live-triage.md) |

## Account Security Baseline

Checklist:

- Không dùng shared account cho vận hành hằng ngày.
- Admin dùng user riêng, elevate qua `sudo`.
- Review group `sudo` hoặc `wheel` định kỳ.
- Không để UID `0` ngoài account root trừ khi có lý do rất đặc biệt.
- Khóa hoặc xóa account không còn owner.
- Tắt password SSH nếu policy và break-glass process cho phép.
- Dùng key-based login, passphrase, MFA hoặc bastion nếu hạ tầng hỗ trợ.

Read-only checks:

```bash
getent passwd
getent group sudo
getent group wheel
awk -F: '$3 == 0 {print $1":"$3":"$6":"$7}' /etc/passwd
last -a | head -50
lastlog | head -50
sudo -l
```

## File And Permission Baseline

Permission policy phải trả lời:

- File/directory thuộc user/group nào?
- Service chạy bằng user nào?
- Directory nào được ghi bởi application?
- File nào có SUID/SGID/capability đặc biệt?
- Sticky bit có được dùng cho shared temp directory không?

Audit nhanh:

```bash
find / -xdev -perm -4000 -type f -ls 2>/dev/null
find / -xdev -perm -2000 -type f -ls 2>/dev/null
getcap -r / 2>/dev/null
find / -xdev -type d -perm -0002 ! -perm -1000 -ls 2>/dev/null
```

Không sửa bằng `chmod 777` để "chạy cho được". Hãy sửa owner, group, mode, ACL hoặc service user đúng với mô hình quyền.

## Storage Security Baseline

Storage security không chỉ là disk encryption. Với server Linux, cần kiểm soát:

- Mount option như `nodev`, `nosuid`, `noexec` cho filesystem phù hợp.
- Permission của backup, dump, archive và log.
- NFS/SMB export/mount option.
- Dữ liệu nhạy cảm trong `/tmp`, `/var/tmp`, `/dev/shm`.
- Snapshot/backup retention và quyền truy cập backup.

Checks:

```bash
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
df -h
lsblk -f
cat /etc/fstab
find /tmp /var/tmp /dev/shm -type f -ls 2>/dev/null
```

Với network storage, kiểm tra cả client mount option và server export/share permission.

## Automation Security Baseline

Cron, systemd timer và script automation thường chạy quyền cao. Rủi ro lớn nhất là script hoặc directory cha writable bởi user không đáng tin.

Checklist:

- Script chạy bởi root phải thuộc `root:root` và không world/group writable.
- Dùng absolute path trong script.
- Không để password/token trong crontab, command line hoặc shell history.
- Có log, exit code rõ và lock chống chạy trùng nếu job có thể overlap.
- Dùng systemd timer nếu cần dependency, retry, logging và trạng thái rõ hơn cron.

Checks:

```bash
cat /etc/crontab
ls -la /etc/cron.d /etc/cron.hourly /etc/cron.daily /etc/cron.weekly
systemctl list-timers --all
find /etc/systemd/system -type f -mtime -14 -ls 2>/dev/null
```

## Network Security Baseline

Mục tiêu là biết host đang expose gì, ai được truy cập, firewall nào enforce policy, và log ở đâu.

Checks:

```bash
ip addr
ip route
sudo ss -tulpn
sudo nft list ruleset 2>/dev/null
sudo iptables -L -n -v 2>/dev/null
sudo firewall-cmd --list-all 2>/dev/null
sudo ufw status verbose 2>/dev/null
```

SSH baseline:

- Chỉ cho user/group cần thiết.
- Không cho root login trực tiếp nếu không bắt buộc.
- Ưu tiên key-based auth.
- Giới hạn source IP bằng firewall/security group nếu có thể.
- Log authentication phải được giữ đủ lâu để điều tra.

## Software Management Baseline

Package policy cần kiểm soát nguồn cài và vòng đời patch:

- Dùng repository được phê duyệt.
- Ghi lại repository thêm thủ công.
- Không import GPG key không rõ nguồn.
- Có maintenance window cho upgrade production.
- Biết package nào sở hữu file quan trọng.
- Có rollback/snapshot/backup cho thay đổi lớn.

Checks:

```bash
cat /etc/os-release
apt policy 2>/dev/null
dnf repolist 2>/dev/null
rpm -qa 2>/dev/null | sort | head
dpkg -l 2>/dev/null | head
```

## Footprinting And Exposure Review

Footprinting là bước hiểu bề mặt hệ thống trước khi hardening hoặc incident response. Ở góc phòng thủ, nó giúp phát hiện service lạ, port lạ, account lạ hoặc rule firewall không còn owner.

Read-only baseline:

```bash
hostnamectl
uname -a
uptime
sudo ss -tulpn
systemctl --type=service --state=running
systemctl --failed
ip addr
ip route
```

Nếu dùng scanner như `nmap`, chỉ scan phạm vi đã được phép. Không scan mạng production rộng khi chưa có phê duyệt.

## Intrusion Detection Signals

Tín hiệu cần điều tra:

- Login SSH thất bại tăng mạnh.
- User mới hoặc sudoers thay đổi ngoài change window.
- SUID/SGID/capability mới xuất hiện.
- Process chạy từ `/tmp`, `/var/tmp`, `/dev/shm` hoặc home user.
- Port listen mới không có owner.
- Cron/systemd unit mới.
- Outbound connection tới IP/port không thuộc baseline.

Checks:

```bash
journalctl --since "24 hours ago" | grep -Ei "sshd|sudo|su|useradd|passwd|authentication"
find / -xdev -perm -4000 -type f -mtime -7 -ls 2>/dev/null
find /etc/systemd/system /etc/cron.d -type f -mtime -14 -ls 2>/dev/null
sudo ss -antp
```

## Change Safety

Các thay đổi có rủi ro lockout hoặc outage:

- PAM.
- SSH daemon config.
- Firewall inbound policy.
- SELinux/AppArmor enforce mode.
- Sudoers.
- fstab/mount option.

Quy trình an toàn:

1. Backup file config.
2. Validate syntax nếu tool hỗ trợ.
3. Giữ session quản trị đang mở.
4. Test bằng session mới.
5. Có rollback command hoặc console out-of-band.
6. Ghi lại thay đổi và owner.

## Related Pages

- [Linux Privilege Escalation Defense](./06-linux-privilege-escalation-defense.md)
- [Linux Incident Response Live Triage](./07-linux-incident-response-live-triage.md)
- [SUID, SGID, SELinux, PAM, auditd và Hardening](./03-suid-sgid-selinux-pam-auditd-hardening.md)
- [Linux Firewall, iptables và nftables Operations](../02-storage-networking/07-linux-firewall-iptables-operations.md)
