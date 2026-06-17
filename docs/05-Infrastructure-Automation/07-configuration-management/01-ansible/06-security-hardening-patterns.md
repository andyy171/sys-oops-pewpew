# Ansible Security Hardening Patterns

## Overview

Ansible phu hop de chuan hoa Linux hardening vi no dua server ve desired state lap lai duoc: package, SSH config, sudoers, firewall, logging, patching va MAC policy. Rui ro chinh la cung mot playbook co the lockout hoac pha service tren nhieu host cung luc, nen hardening playbook phai duoc viet nhu production change, khong nhu script nhanh.

## Atom Routing

| Hardening area | Canonical security note | Ansible action |
|---|---|---|
| SSH | [SSH security, 2FA, bastion host](../../02-security-and-hardening/01-access-control/SSH%20security,%202FA,%20bastion%20host.md) | template/lineinfile, validate, reload canary |
| sudo/PAM/fail2ban | [PAM, auditd, fail2ban](../../02-security-and-hardening/01-access-control/PAM,%20auditd,%20fail2ban.md) | copy/template with validation, serial rollout |
| firewall | [Linux firewall operations](../../../02-core-infrastructure/01-linux/02-storage-networking/07-linux-firewall-iptables-operations.md) | allowlist rules, out-of-band rollback |
| logs/logrotate | [Logs, journald, rsyslog va logrotate](../../../02-core-infrastructure/01-linux/03-security-logs-troubleshooting/01-logs-journald-rsyslog-logrotate.md) | ensure retention, forwarding, disk guard |
| SELinux/AppArmor | [SELinux, AppArmor](../../02-security-and-hardening/02-os-and-network-security/SELinux,%20AppArmor.md) | enforce only after denial review |

## Safe Rollout Workflow

```text
read-only baseline
-> staging/lab run
-> canary host with --limit
-> serial rollout per role
-> validation from outside host
-> monitor auth/app/firewall logs
```

Pre-check:

```bash
ansible-playbook -i inventory.ini hardening.yml --list-hosts
ansible-playbook -i inventory.ini hardening.yml --check --diff --limit node-1
```

Rollout:

```yaml
- name: Harden Linux servers
  hosts: linux
  become: true
  serial: 1
  max_fail_percentage: 0
```

Dung `serial` cho cac thay doi co the cat access: SSH, firewall, sudoers, PAM, SELinux/AppArmor.

## SSH Hardening Pattern

Quan ly SSH bang `template` neu team so huu toan bo file. Neu chi thay vai setting, `lineinfile` can co regexp ro va validate truoc reload.

```yaml
- name: Render sshd_config
  template:
    src: sshd_config.j2
    dest: /etc/ssh/sshd_config
    owner: root
    group: root
    mode: "0600"
    validate: "sshd -t -f %s"
  notify: Reload sshd

handlers:
  - name: Reload sshd
    service:
      name: sshd
      state: reloaded
```

Validation sau rollout:

```bash
ansible linux -i inventory.ini -b -m command -a "sshd -T"
ansible linux -i inventory.ini -b -m command -a "journalctl -u sshd --since '10 minutes ago' --no-pager"
```

Neu doi port, mo firewall/security group port moi truoc khi reload va test session moi truoc khi dong port cu.

## sudoers Pattern

Khong sua `/etc/sudoers` bang text replacement khong validate. Dung `copy` hoac `template` voi `visudo`.

```yaml
- name: Install sudoers rule for deploy group
  copy:
    dest: /etc/sudoers.d/deploy
    content: "%deploy ALL=(ALL) NOPASSWD: /bin/systemctl restart app\n"
    owner: root
    group: root
    mode: "0440"
    validate: "visudo -cf %s"
```

Guardrails:

- Tranh `NOPASSWD: ALL` neu chi can mot tap command cu the.
- Review group membership cua user truoc khi cap sudo.
- Test `sudo -l -U <user>` sau rollout.

## Package Cleanup Va Patch

`state=absent`, `purge=yes`, package upgrade toan he thong va service restart la risky operations. Can co inventory target hep, maintenance window va rollback/snapshot neu host quan trong.

Read-only baseline:

```bash
ansible linux -i inventory.ini -b -m command -a "systemctl --failed"
ansible linux -i inventory.ini -b -m command -a "ss -tulpn"
ansible linux -i inventory.ini -b -m command -a "df -h"
```

Patch guardrails:

- test tren staging/canary;
- khong upgrade tat ca host HA cung luc;
- xac dinh package hold/exclude;
- co reboot plan neu kernel/libc/security update yeu cau;
- validate app health sau patch.

## Firewall Pattern

Firewall playbook phai allow duong quan tri truoc khi default deny.

```text
allow admin source to SSH/new SSH port
-> allow service ports from required source CIDR
-> apply default deny inbound
-> validate from outside host
-> remove obsolete rules
```

Neu host remote khong co console out-of-band, dat rollback tu dong hoac chay canary duy nhat truoc.

## Logging, fail2ban Va SELinux

Hardening khong day du neu khong co detection:

- log auth, sudo, firewall drop va app error phai duoc rotate va monitor;
- fail2ban chi la mitigation, khong thay the SSH key/MFA/bastion;
- SELinux/AppArmor nen duoc sua dung context/boolean/profile thay vi disable.

Sau khi apply, validate:

```bash
ansible linux -i inventory.ini -b -m command -a "journalctl --disk-usage"
ansible linux -i inventory.ini -b -m command -a "fail2ban-client status"
ansible linux -i inventory.ini -b -m command -a "getenforce"
```

## Related Pages

- [Ansible Overview](./overview.md)
- [Playbook Advanced Patterns](./02-playbook-advanced-patterns.md)
- [Linux Hardening Baseline](../../02-security-and-hardening/02-os-and-network-security/linux-hardening-baseline.md)
