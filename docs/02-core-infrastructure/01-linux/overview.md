# Linux

Folder này là nơi tổng hợp kiến thức Linux chính của vault. Khi có note Linux mới, ưu tiên đọc nội dung, xác định đúng domain, rồi merge vào file phù hợp trong cấu trúc hiện tại thay vì tạo bản trùng lặp.

Kiến thức Linux được chia theo 4 nhóm vận hành chính: core system, storage/networking, security/logs/troubleshooting, và shell/automation/advanced.

Nguyên tắc tổ chức: root của folder kiến thức chỉ giữ `overview.md` làm cổng vào. Kiến thức chi tiết, lab, runbook và deep dive phải nằm trong subfolder đúng domain.

## Nguyên tắc vận hành Linux

Sysadmin/SRE giỏi không chỉ nhớ lệnh. Khi vận hành Linux trong production, luôn bắt đầu từ workload, rủi ro thay đổi, khả năng rollback và bằng chứng cần giữ lại.

- Chọn distribution theo workload, support window, ecosystem package, kỹ năng team và yêu cầu compliance; không chọn chỉ vì thói quen cá nhân.
- Release model là ràng buộc vận hành: LTS phù hợp hơn cho server stateful; rolling/rapid release cần automation, test và rollback tốt.
- Patch management phải cân bằng risk của vulnerability với risk của change. Trì hoãn patch quá lâu thường chỉ đổi planned downtime thành unplanned incident.
- Storage phải được đánh giá theo durability, availability, performance, capacity và recovery. RAID không thay thế backup hoặc disaster recovery.
- Documentation nên sống cùng thay đổi: owner, dependency, port, config, backup, restore, runbook và lịch sử quyết định.
- Automation trưởng thành theo bậc: command repeatable -> script -> scheduled task -> config management -> IaC -> rebuild/restore được từ source of truth.
- Backup chỉ được tính là đáng tin khi restore đã được kiểm chứng.
- Troubleshooting cần tách điều tra và sửa lỗi. Restart có thể khôi phục dịch vụ, nhưng cũng có thể làm mất evidence tạm thời.

## Lộ trình học ngắn gọn

1. Bắt đầu với boot, filesystem hierarchy, `systemd`, user/permission, package, process và kernel runtime trong [Core system](./01-core-system/01-linux-overview-boot-systemd.md).
2. Học disk, mount, LVM/RAID, backup, IP/route/DNS/firewall, SSH và network namespace trong [Storage và networking](./02-storage-networking/01-disk-filesystem-mount-swap.md).
3. Học log, audit, hardening, performance troubleshooting, incident response và evidence collection trong [Security, logs và troubleshooting](./03-security-logs-troubleshooting/01-logs-journald-rsyslog-logrotate.md).
4. Học shell, text processing, scripting, cron/systemd timer, Ansible, container/KVM/cgroup/namespace và system programming trong [Shell automation advanced](./04-shell-automation-advanced/01-shell-basic-commands-pipe-redirection.md).

## Review cấu trúc hiện tại

### Điểm tốt

- Cấu trúc 4 nhóm chính hợp lý cho Linux operations: core system, storage/networking, security/logs/troubleshooting, shell/automation/advanced.
- Nội dung đã có nhiều note vận hành thật: boot/systemd, user/permission, package/process/service, kernel `/proc`/`/sys`, disk/LVM/network/firewall, journald/rsyslog/logrotate, hardening, performance, incident response và system programming.
- Các note troubleshooting đã bắt đầu đi theo hướng đọc signal trước: `systemctl`, `journalctl`, `df`, `du`, `ip`, `ss`, `tcpdump`, logs/evidence.

### Chưa tốt

- Một số note còn gom hơi nhiều chủ đề trong một file, ví dụ security + boot, SSH + bridge + netns, storage + networking nằm cùng một tầng. Khi review sâu nên cân nhắc tách thêm nếu file quá dài hoặc khác mục đích.
- Chưa có `overview.md` riêng cho từng subfolder Linux; hiện root overview đang làm cả nhiệm vụ index. Nếu muốn navigation đẹp hơn, bước tiếp theo nên thêm overview ngắn cho từng subfolder.

### Đánh giá nhanh

| Hạng mục | Điểm |
|---|---:|
| Cấu trúc thư mục sau khi dọn root | 820/1000 |
| Mức bao phủ nội dung Linux operations | 850/1000 |
| Độ sạch placement/canonical note | 850/1000 |
| Mức sẵn sàng để học theo lộ trình | 850/1000 |

Điểm tổng quan hiện tại: **842/1000**. Nền kiến thức tốt; bước cải thiện tiếp theo là thêm overview ngắn cho từng subfolder và tách các note đang gom nhiều mục đích khi cần học sâu.

## Cấu trúc

```text
01-linux/
├── overview.md
├── 01-core-system/
├── 02-storage-networking/
├── 03-security-logs-troubleshooting/
└── 04-shell-automation-advanced/
```

## 01-core-system

- [Linux Overview, Boot Process và Systemd](./01-core-system/01-linux-overview-boot-systemd.md)
- [User, Permission và Access Control Cơ Bản](./01-core-system/02-users-permissions-access.md)
- [Package, Process và Service Management](./01-core-system/03-package-process-service.md)
- [Kernel, procfs, sysfs và System Information](./01-core-system/04-kernel-proc-sys-system-info.md)

## 02-storage-networking

- [Disk, Filesystem, Mount và Swap](./02-storage-networking/01-disk-filesystem-mount-swap.md)
- [LVM, RAID, Backup và Restore](./02-storage-networking/02-lvm-raid-backup-restore.md)
- [NFS, SMB/CIFS và iSCSI Network Storage](./02-storage-networking/03-nfs-smb-iscsi-network-storage.md)
- [IP, Route, DNS và Firewall](./02-storage-networking/04-ip-route-dns-firewall.md)
- [SSH, JumpHost, LLDP, Bridge và Network Namespace](./02-storage-networking/05-ssh-jumphost-lldp-bridge-netns.md)
- [Linux Routing, Netfilter Và Policy Routing](./02-storage-networking/06-linux-routing-netfilter-policy-routing.md)
- [Linux Firewall, iptables Và nftables Operations](./02-storage-networking/07-linux-firewall-iptables-operations.md)

## 03-security-logs-troubleshooting

- [Logs, journald, rsyslog và logrotate](./03-security-logs-troubleshooting/01-logs-journald-rsyslog-logrotate.md)
- [CA Certificates, GRUB và Boot Security](./03-security-logs-troubleshooting/02-ca-certificates-grub-boot-security.md)
- [SUID, SGID, SELinux, PAM, auditd và Hardening](./03-security-logs-troubleshooting/03-suid-sgid-selinux-pam-auditd-hardening.md)
- [Common Linux Troubleshooting Runbooks](./03-security-logs-troubleshooting/04-common-troubleshooting-runbooks.md)
- [Performance Troubleshooting Cơ Bản](./03-security-logs-troubleshooting/05-performance-troubleshooting.md)
- [Linux Privilege Escalation Defense](./03-security-logs-troubleshooting/06-linux-privilege-escalation-defense.md)
- [Linux Incident Response Live Triage](./03-security-logs-troubleshooting/07-linux-incident-response-live-triage.md)
- [Linux Server Troubleshooting Playbook](./03-security-logs-troubleshooting/08-linux-server-troubleshooting-playbook.md)
- [Linux Security Policy Baseline](./03-security-logs-troubleshooting/09-linux-security-policy-baseline.md)
- [Recover Lost Partition After Accidental wipefs With TestDisk](./03-security-logs-troubleshooting/10-recover-lost-partition-after-wipefs-testdisk.md)

## 04-shell-automation-advanced

- [Shell, Basic Commands, Pipe và Redirection](./04-shell-automation-advanced/01-shell-basic-commands-pipe-redirection.md)
- [Text Processing: grep, sed, awk, regex và vim](./04-shell-automation-advanced/02-text-processing-grep-sed-awk-regex-vim.md)
- [Bash Scripting, cron và systemd timer](./04-shell-automation-advanced/03-bash-scripting-cron-systemd-timer.md)
- [Ansible và Git cho Sysadmin](./04-shell-automation-advanced/04-ansible-git-for-sysadmin.md)
- [Container, KVM, cgroup và namespace](./04-shell-automation-advanced/05-container-kvm-cgroup-namespace.md)
- [HA Cluster, Pacemaker và Corosync](./04-shell-automation-advanced/06-ha-cluster-pacemaker-corosync.md)
- [Linux Labs và Practices](./04-shell-automation-advanced/07-labs-practices.md)
- [Sysadmin Scripts Collection](./04-shell-automation-advanced/08-sysadmin-scripts-collection.md)
- [Bash System Check, Log And Cron Labs](./04-shell-automation-advanced/09-bash-system-check-log-and-cron-labs.md)
- [Linux System Programming For Ops](./04-shell-automation-advanced/10-linux-system-programming-for-ops.md)
- [Linux Commands For Operations](./04-shell-automation-advanced/11-linux-commands-for-operations.md)

