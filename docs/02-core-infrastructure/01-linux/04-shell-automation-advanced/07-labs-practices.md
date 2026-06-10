# Linux Labs và Practices

File này là mục lục lab, không copy lại toàn bộ runbook. Nội dung chi tiết nằm ở file domain chính để tránh trùng lặp.

## 1. Storage Labs

- Move `/home` to dedicated partition: [Disk, Filesystem, Mount và Swap](../02-storage-networking/01-disk-filesystem-mount-swap.md)
- Create and extend LVM logical volume: [LVM, RAID, Backup và Restore](../02-storage-networking/02-lvm-raid-backup-restore.md)
- Create RAID1 with `mdadm`: [LVM, RAID, Backup và Restore](../02-storage-networking/02-lvm-raid-backup-restore.md)
- Backup and restore `/etc`: [LVM, RAID, Backup và Restore](../02-storage-networking/02-lvm-raid-backup-restore.md)

## 2. Network Storage Labs

- Mount NFS share: [NFS, SMB/CIFS và iSCSI Network Storage](../02-storage-networking/03-nfs-smb-iscsi-network-storage.md)
- Mount SMB/CIFS share with credential file: [NFS, SMB/CIFS và iSCSI Network Storage](../02-storage-networking/03-nfs-smb-iscsi-network-storage.md)
- Connect iSCSI initiator to target: [NFS, SMB/CIFS và iSCSI Network Storage](../02-storage-networking/03-nfs-smb-iscsi-network-storage.md)

## 3. Network Labs

- Static IP and route checks: [IP, Route, DNS và Firewall](../02-storage-networking/04-ip-route-dns-firewall.md)
- DNS troubleshooting with `dig`, `getent`, `resolvectl`: [IP, Route, DNS và Firewall](../02-storage-networking/04-ip-route-dns-firewall.md)
- Firewall rule inspection: [IP, Route, DNS và Firewall](../02-storage-networking/04-ip-route-dns-firewall.md)
- Network namespace lab: [SSH, JumpHost, LLDP, Bridge và Network Namespace](../02-storage-networking/05-ssh-jumphost-lldp-bridge-netns.md)

## 4. Remote Access Labs

- SSH key login: [SSH, JumpHost, LLDP, Bridge và Network Namespace](../02-storage-networking/05-ssh-jumphost-lldp-bridge-netns.md)
- SSH through JumpHost with `ProxyJump`: [SSH, JumpHost, LLDP, Bridge và Network Namespace](../02-storage-networking/05-ssh-jumphost-lldp-bridge-netns.md)
- LLDP neighbor discovery: [SSH, JumpHost, LLDP, Bridge và Network Namespace](../02-storage-networking/05-ssh-jumphost-lldp-bridge-netns.md)

## 5. Security Labs

- Install internal Root CA: [CA Certificates, GRUB và Boot Security](../03-security-logs-troubleshooting/02-ca-certificates-grub-boot-security.md)
- Reset root password using GRUB rescue flow: [CA Certificates, GRUB và Boot Security](../03-security-logs-troubleshooting/02-ca-certificates-grub-boot-security.md)
- Audit SUID/SGID files: [SUID, SGID, SELinux, PAM, auditd và Hardening](../03-security-logs-troubleshooting/03-suid-sgid-selinux-pam-auditd-hardening.md)
- Add auditd rule for sensitive files: [SUID, SGID, SELinux, PAM, auditd và Hardening](../03-security-logs-troubleshooting/03-suid-sgid-selinux-pam-auditd-hardening.md)

## 6. Troubleshooting Labs

- Service failed runbook: [Common Linux Troubleshooting Runbooks](../03-security-logs-troubleshooting/04-common-troubleshooting-runbooks.md)
- Mount/fstab failure: [Common Linux Troubleshooting Runbooks](../03-security-logs-troubleshooting/04-common-troubleshooting-runbooks.md)
- Disk full incident: [Common Linux Troubleshooting Runbooks](../03-security-logs-troubleshooting/04-common-troubleshooting-runbooks.md)
- High CPU / high memory triage: [Performance Troubleshooting](../03-security-logs-troubleshooting/05-performance-troubleshooting.md)

## 7. Shell Labs

- Bash system check, log parsing and cron lab: [Bash System Check, Log And Cron Labs](./09-bash-system-check-log-and-cron-labs.md)
- Parse access log with `awk`, `sort`, `uniq`: [Text Processing: grep, sed, awk, regex và vim](./02-text-processing-grep-sed-awk-regex-vim.md)
- Write backup script: [Bash Scripting, cron và systemd timer](./03-bash-scripting-cron-systemd-timer.md)
- Create systemd timer: [Bash Scripting, cron và systemd timer](./03-bash-scripting-cron-systemd-timer.md)
- Use sample sysadmin scripts: [Sysadmin Scripts Collection](./08-sysadmin-scripts-collection.md)

## 8. Automation Labs

- Git rollback practice: [Git và Ansible cho Sysadmin](./04-ansible-git-for-sysadmin.md)
- Run Ansible ad-hoc command: [Git và Ansible cho Sysadmin](./04-ansible-git-for-sysadmin.md)
- Run Ansible playbook in check mode: [Git và Ansible cho Sysadmin](./04-ansible-git-for-sysadmin.md)

## 9. Advanced Labs

- Inspect namespaces with `lsns`: [Container, KVM, cgroup và namespace](./05-container-kvm-cgroup-namespace.md)
- Check cgroup resource usage: [Container, KVM, cgroup và namespace](./05-container-kvm-cgroup-namespace.md)
- Inspect libvirt network: [Container, KVM, cgroup và namespace](./05-container-kvm-cgroup-namespace.md)
- Pacemaker resource status check: [HA Cluster, Pacemaker và Corosync](./06-ha-cluster-pacemaker-corosync.md)
