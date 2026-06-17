# PAM, auditd, fail2ban

## Overview

`PAM`, `auditd` va `fail2ban` nam o lop access control va detection cua Linux host:

- PAM quyet dinh authentication/session policy cho login, SSH, sudo va nhieu service.
- auditd ghi lai su kien bao mat can dieu tra hoac compliance.
- fail2ban doc log, phat hien failed login lap lai va tam chan source nghi ngo.

Ba cong cu nay khong thay the nhau. PAM enforce policy, auditd ghi evidence, fail2ban la mitigation tam thoi cho brute-force/noise.

## PAM Guardrails

PAM co the lock admin khoi server neu sai syntax hoac policy qua chat. Truoc khi thay doi:

```bash
sudo cp -a /etc/pam.d /etc/pam.d.bak.$(date +%F-%H%M%S)
grep -R "pam_faillock\|pam_pwquality\|pam_limits" /etc/pam.d /etc/security 2>/dev/null
```

Production checklist:

- Giu mot root/admin session dang mo.
- Test login bang session moi truoc khi logout session cu.
- Ghi ro service nao bi anh huong: `sshd`, `sudo`, `login`, app PAM rieng.
- Neu dung automation, rollout theo `serial` va co rollback file config.

## auditd Baseline

auditd nen theo doi cac file va event co anh huong identity/privilege:

```text
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers
```

Read-only checks:

```bash
sudo systemctl status auditd --no-pager
sudo auditctl -l
sudo ausearch -m USER_LOGIN,USER_AUTH,USER_ACCT -ts recent
sudo aureport -au
```

Audit log can duoc forward/backup theo policy. Neu attacker co root, local-only log co the bi xoa hoac sua.

## fail2ban

fail2ban doc log va ban source khi vuot nguong failed attempts. No huu ich cho SSH hoac app login public-facing, nhung khong thay the viec tat password SSH, dung MFA/bastion, hoac gioi han source IP.

Read-only checks:

```bash
sudo systemctl status fail2ban --no-pager
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

Config nen nam trong override local, khong sua truc tiep default package file:

```text
/etc/fail2ban/jail.local
/etc/fail2ban/jail.d/*.conf
```

Guardrails:

- Dat `ignoreip` cho subnet quan tri neu policy cho phep.
- Kiem tra firewall backend ma fail2ban dang thao tac.
- Canh bao truoc khi ban/unban tren production vi co the anh huong admin hop le.
- Theo doi log size; login brute force co the lam day disk neu logrotate/retention sai.

## Detection Signals

Can dieu tra khi thay:

- failed SSH login tang dot bien;
- nhieu username khong ton tai;
- sudo failure hoac sudoers thay doi ngoai change window;
- PAM lockout cua admin;
- fail2ban ban nhieu source trong thoi gian ngan;
- auditd mat log hoac service bi stop.

## Ansible Notes

Khi quan ly PAM/auditd/fail2ban bang Ansible:

- dung `copy`/`template` voi `validate` neu tool ho tro;
- dung handler reload/restart co canary;
- khong apply lockout policy moi tren tat ca bastion/admin host cung luc;
- tach variable threshold theo environment;
- log thay doi vao changelog/change ticket.

## Related Pages

- [SSH security, 2FA, bastion host](./SSH%20security,%202FA,%20bastion%20host.md)
- [Identity, Authentication And Authorization](./01-identity-authentication-authorization.md)
- [Linux Incident Response Live Triage](../../../02-core-infrastructure/01-linux/03-security-logs-troubleshooting/07-linux-incident-response-live-triage.md)
- [Logs, journald, rsyslog va logrotate](../../../02-core-infrastructure/01-linux/03-security-logs-troubleshooting/01-logs-journald-rsyslog-logrotate.md)
