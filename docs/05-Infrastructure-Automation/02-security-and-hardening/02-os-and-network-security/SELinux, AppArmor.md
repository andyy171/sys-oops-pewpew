# SELinux, AppArmor

## Overview

SELinux va AppArmor la Mandatory Access Control. Chung giam blast radius khi process bi compromise bang cach gioi han process duoc doc/ghi/execute path nao, bind port nao, hoac dung capability nao.

Khac voi Unix permission truyen thong, access chi thanh cong khi ca hai lop deu cho phep:

```text
DAC owner/group/mode/ACL allows
AND
MAC policy allows
```

Vi vay loi `permission denied` khong phai luc nao cung sua bang `chmod` hoac `chown`.

## SELinux Mental Model

SELinux pho bien tren RHEL-family. Cac mode chinh:

| Mode | Y nghia |
|---|---|
| `Enforcing` | Chan hanh vi vi pham policy |
| `Permissive` | Log vi pham nhung khong chan |
| `Disabled` | Tat SELinux |

Read-only checks:

```bash
getenforce
sestatus
ls -Z /var/www/html
ps -eZ | grep httpd
sudo ausearch -m AVC,USER_AVC -ts recent
```

## Common Fix Path

Troubleshoot denial theo thu tu:

1. Xac nhan service user, file path that va symlink/bind mount.
2. Kiem tra DAC permission bang `namei -l`, `ls -l`, `getfacl`.
3. Kiem tra context bang `ls -Z` va process context.
4. Kiem tra boolean lien quan bang `getsebool`.
5. Restore context hoac them fcontext neu path dung nhung label sai.
6. Chi tao custom policy sau khi da review denial.

```bash
sudo restorecon -RFv /srv/www
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/www(/.*)?'
sudo restorecon -RFv /srv/www
```

Boolean example:

```bash
sudo getsebool -a | grep httpd
sudo setsebool -P httpd_can_network_connect on
```

`setsebool -P` ghi persistent policy, can review nhu change production.

## AppArmor Mental Model

AppArmor pho bien tren Ubuntu/Debian va gan policy theo profile path/name.

Read-only checks:

```bash
sudo aa-status
sudo journalctl --since "1 hour ago" | grep -i apparmor
```

Mode thao tac:

```bash
sudo aa-complain <profile>
sudo aa-enforce <profile>
```

`complain` huu ich de khoanh vung denial nhung khong nen de lau tren production neu profile do bao ve workload nhay cam.

## Container Runtime Notes

Container chia se kernel voi host, nen SELinux/AppArmor la lop giam blast radius quan trong khi process trong container bi compromise. Docker/Kubernetes co the gan profile/label rieng cho workload, nhung policy phai duoc test nhu mot thay doi production.

Safe workflow khi tao hoac sua policy cho container:

1. Chay workload trong staging/canary voi profile hien tai.
2. Thu thap denial bang `ausearch`, `journalctl` hoac tool audit cua distro.
3. Xac minh denial co phai hanh vi hop le cua app khong, vi denial bat ngo co the la signal compromise hoac config sai.
4. Sua context/boolean/profile/policy nho nhat co the.
5. Enforce lai tren canary, theo doi app log va audit log.
6. Rollout dan dan, co rollback ve policy truoc hoac mode permissive/complain co time-box.

Vi du Docker gan AppArmor profile:

```bash
docker run --rm \
  --security-opt apparmor=<profile-name> \
  <image>:<tag>
```

Vi du Docker gan SELinux label type da duoc policy cho phep:

```bash
docker run --rm \
  --security-opt label:type:<selinux_type_t> \
  <image>:<tag>
```

Guardrail: khong apply output `audit2allow` mot cach mu quang. Tool co the sinh policy cho phep dung hanh vi vua bi log, nhung khong biet hanh vi do co dung intent bao mat hay khong.

## Production Guardrails

- Khong tat SELinux/AppArmor vinh vien chi de app chay.
- Neu can permissive/complain tam thoi, gioi han host, time window va ghi rollback.
- Luu audit denial truoc khi sua de co evidence.
- Review output `audit2allow`; khong apply blind policy sinh tu log.
- Sau khi sua, validate app behavior va xac nhan khong con denial moi.

## Ansible Notes

Ansible co the quan ly SELinux mode, boolean va file context, nhung phai rollout than trong:

```yaml
- name: Ensure SELinux is enforcing
  selinux:
    policy: targeted
    state: enforcing

- name: Allow httpd network connections when required
  seboolean:
    name: httpd_can_network_connect
    state: true
    persistent: true
```

Truoc khi dua host tu `Permissive` sang `Enforcing`, can:

- review AVC denial gan day;
- test tren staging/canary;
- co rollback ve `Permissive` neu app bi chan;
- theo doi app log va audit log sau rollout.

## Related Pages

- [Linux Hardening Baseline](./linux-hardening-baseline.md)
- [SUID, SGID, SELinux, PAM, auditd va Hardening](../../../02-core-infrastructure/01-linux/03-security-logs-troubleshooting/03-suid-sgid-selinux-pam-auditd-hardening.md)
- [PAM, auditd, fail2ban](../01-access-control/PAM,%20auditd,%20fail2ban.md)
