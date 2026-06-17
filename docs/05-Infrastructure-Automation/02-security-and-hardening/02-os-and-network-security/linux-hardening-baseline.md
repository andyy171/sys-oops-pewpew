# Linux Hardening Baseline

Note này chuyển hóa `_inbox/Mastering-Linux-Security-and-Hardening.docx` thành baseline hardening thực dụng cho Linux server. Nội dung nguồn bao phủ lab security, user account, firewall, SSH/encryption, DAC/ACL, MAC, scanning, auditing và intrusion detection.

## Hardening Mental Model

Linux hardening là giảm attack surface và tăng khả năng phát hiện:

```text
Identity -> Privilege -> Filesystem -> Network -> Service -> Audit -> Detection -> Response
```

Không có một setting đơn lẻ làm hệ thống “an toàn”. Cần nhiều lớp kiểm soát nhỏ, có rollback và kiểm chứng.

## Account And Privilege

Checklist:

- Không dùng root cho thao tác hằng ngày.
- Dùng `sudo` theo role, không chia sẻ account.
- Khóa hoặc xóa user không dùng.
- Enforce password/SSH key policy theo chuẩn nội bộ.
- Review user có shell login.
- Review sudo rule quá rộng.

Command:

```bash
getent passwd
awk -F: '$3 == 0 {print}' /etc/passwd
sudo -l -U <user>
lastlog
faillock --user <user> 2>/dev/null || true
```

## SSH Hardening

Các hướng chính:

- ưu tiên SSH key;
- tắt root login trực tiếp;
- tắt password auth nếu có thể;
- giới hạn user/group được SSH;
- bật MFA/bastion nếu môi trường yêu cầu;
- giữ session cũ khi test config mới.

```bash
sudo sshd -t
sudo systemctl reload sshd
```

Không đóng session hiện tại trước khi mở session mới thành công.

## Firewall Baseline

Mục tiêu: chỉ mở port thật sự cần.

```bash
sudo ss -tulpn
sudo firewall-cmd --list-all 2>/dev/null || true
sudo nft list ruleset 2>/dev/null || true
sudo iptables -S 2>/dev/null || true
```

Nguyên tắc:

- default deny cho inbound nếu phù hợp;
- allow theo source cụ thể, nhất là SSH/admin port;
- document owner của từng port;
- test từ ngoài host, không chỉ nhìn local listen.

## File Permission, SUID/SGID And ACL

DAC là lớp quyền truyền thống: owner, group, mode bit.

```bash
namei -l /path/to/file
getfacl /path/to/file
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
```

Checklist:

- Tránh `chmod 777`.
- Review SUID/SGID binary định kỳ.
- Dùng group/ACL thay vì mở permission toàn cục.
- Kiểm tra directory cha có execute bit phù hợp.
- Với shared directory, hiểu sticky bit và SGID directory.

## Mandatory Access Control

SELinux/AppArmor giảm blast radius khi process bị compromise.

```bash
getenforce 2>/dev/null || true
sestatus 2>/dev/null || true
aa-status 2>/dev/null || true
journalctl -t setroubleshoot --since "1 hour ago" 2>/dev/null || true
```

Rule thực tế:

- Không tắt SELinux/AppArmor vội chỉ vì app lỗi.
- Đọc audit denial để hiểu policy thiếu gì.
- Dùng permissive tạm thời có kiểm soát nếu cần khoanh vùng.
- Ghi lại local policy/module đã thêm.

## Encryption

Phân biệt:

- encryption at rest: disk, filesystem, database, object storage;
- encryption in transit: SSH, TLS, VPN, mTLS;
- key management: ai giữ key, rotate thế nào, backup ra sao.

Checklist:

- TLS certificate còn hạn.
- Private key permission chặt.
- Không lưu key/password trong repo.
- Backup key material theo quy trình an toàn.

## Auditing And Scanning

Audit:

```bash
auditctl -s 2>/dev/null || true
ausearch -m USER_LOGIN -ts recent 2>/dev/null || true
journalctl --since "1 hour ago"
```

Scanning/hardening tools có thể gồm:

- Lynis cho baseline audit.
- OpenSCAP/CIS benchmark nếu tổ chức dùng.
- ClamAV trong file server có client Windows.
- auditd cho event quan trọng.
- IDS/IPS như Snort/Suricata ở network layer.

Điểm quan trọng: scan finding phải đi qua triage. Không apply hardening hàng loạt lên production nếu chưa hiểu impact.

## Intrusion Detection

Tín hiệu nên theo dõi:

- login thất bại nhiều lần;
- user mới hoặc sudo rule mới;
- SUID file mới;
- process lạ listen port;
- outbound connection bất thường;
- file integrity thay đổi ở path nhạy cảm;
- service disable Cloud/Audit agent.

Command nền:

```bash
last
lastb 2>/dev/null || true
ss -tulpn
ps auxf
find /tmp /var/tmp -type f -perm -111 2>/dev/null
```

## Hardening Rollout

Trình tự an toàn:

1. Baseline hiện trạng.
2. Apply trên lab/non-prod.
3. Test access, deploy, backup, monitoring.
4. Rollout từng nhóm host.
5. Theo dõi alert/login/app error.
6. Ghi rollback cho từng control.

## Production Automation Guardrails

Khi hardening bang Ansible hoac automation tuong tu, coi moi control nhu mot production change co blast radius:

- `state=absent`, `purge`, package upgrade toan he thong va restart service can co canary, backup/rollback va validation.
- SSH, sudoers, PAM, firewall va SELinux/AppArmor co the lockout admin; rollout bang `serial` va giu session/console du phong.
- Dung `validate` cho file nhay cam neu module ho tro, vi du `sshd -t` va `visudo -cf`.
- Khong tat GPG signature check de "fix nhanh" package automation; import key tu nguon duoc phe duyet.
- Log auth, sudo, firewall va package change phai ve duoc he thong monitoring/logging tap trung.

Pre-check read-only nen co:

```bash
hostnamectl
systemctl --failed
sudo ss -tulpn
sudo ufw status verbose 2>/dev/null || true
sudo firewall-cmd --list-all 2>/dev/null || true
getenforce 2>/dev/null || true
```

## Source Coverage Matrix

`Mastering-Linux-Security-and-Hardening.docx` da duoc gom theo cac nhom:

| Source topic | Da chuyen hoa vao |
|---|---|
| Security lab/virtual environment, threat landscape | Hardening Mental Model va Hardening Rollout |
| Securing user accounts, root, sudo, password/account policy | Account And Privilege |
| Server firewall utilities | Firewall Baseline |
| Encryption and SSH hardening | SSH Hardening va Encryption |
| Discretionary Access Control, SUID/SGID | File Permission, SUID/SGID And ACL |
| ACL and shared directory management | File Permission, SUID/SGID And ACL |
| Mandatory Access Control with SELinux/AppArmor | Mandatory Access Control |
| Scanning, auditing, hardening | Auditing And Scanning |
| Vulnerability scanning and intrusion detection | Intrusion Detection |
| Security tips and tricks | Hardening Rollout va Operating checklist |

Nhung phan lab/tool output dai trong source khong duoc copy nguyen. Kien thuc ben vung duoc chuyen thanh baseline, command read-only, rollout safety va link sang note chuyen sau.

## Related Pages

- [Security And Hardening Overview](../overview.md)
- [SSH security, 2FA, bastion host](../01-access-control/SSH%20security,%202FA,%20bastion%20host.md)
- [PAM, auditd, fail2ban](../01-access-control/PAM,%20auditd,%20fail2ban.md)
- [SELinux, AppArmor](./SELinux,%20AppArmor.md)
- [FirewallD, iptables rules](./FirewallD,%20iptables%20rules.md)
- [Ansible Security Hardening Patterns](../../07-configuration-management/01-ansible/06-security-hardening-patterns.md)
