# SSH Security, 2FA, Bastion Host

## Mental Model

SSH la control channel quan trong cua Linux server. Bao ve SSH khong chi la doi port, ma la giam kha nang login trai phep va dam bao moi session quan tri co identity, encryption, audit trail va rollback path ro rang.

Luon phan biet:

- host key: dinh danh server ma client dang ket noi toi;
- user key: dinh danh nguoi dung hoac automation account;
- session encryption: kenh ma hoa sau khi client va server da bat tay;
- access policy: user/group/source nao duoc phep SSH.

Telnet, rlogin, rsh va cac protocol plain text khong phu hop cho remote administration tren network hien dai. Neu can test port bang plain TCP, chi dung cho troubleshooting dich vu khong nhay cam; khong gui password/token qua kenh khong ma hoa.

## SSH Daemon Baseline

Trong `/etc/ssh/sshd_config`, baseline production thuong gom:

```text
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowGroups ssh-admins
MaxAuthTries 3
```

`PasswordAuthentication no` chi nen bat sau khi da xac nhan break-glass process va key-based login hoat dong. Neu dung automation nhu Ansible, inventory va bastion config cung phai duoc cap nhat truoc khi reload SSH.

## Safe Change Workflow

Thay doi SSH co rui ro tu khoa minh khoi server. Quy trinh toi thieu:

```bash
sudo cp -a /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%F-%H%M%S)
sudo sshd -t
sudo systemctl reload sshd
```

Validation:

```bash
ssh -o PreferredAuthentications=publickey <user>@<host>
sudo journalctl -u sshd --since "10 minutes ago" --no-pager
```

Guardrails:

- Giu session SSH hien tai dang mo cho toi khi session moi login thanh cong.
- Neu doi SSH port, mo firewall/security group cho port moi truoc.
- Chi dong port cu sau khi da test login qua port moi.
- Co console out-of-band neu thao tac tren host remote quan trong.

## Port Change Va Security Through Obscurity

Doi port SSH co the giam bot noise tu scanner mac dinh port 22, nhung khong thay the duoc key-based auth, least privilege, MFA/bastion va log monitoring. Neu doi port, phai cap nhat:

- inventory automation;
- firewall host;
- security group/NACL/upstream firewall;
- monitoring check;
- runbook break-glass.

## Bastion Va 2FA

Bastion host hoac access gateway phu hop khi can:

- tap trung audit log;
- enforce MFA/SSO;
- gioi han source IP vao private server;
- tranh mo SSH truc tiep tu Internet vao tung host.

Khong dat bastion thanh single point of failure ma khong co HA hoac break-glass path. Log cua bastion phai duoc forward ve logging/SIEM vi no la diem quan sat access quan trong.

## Ansible Notes

Khi dung Ansible de harden SSH:

- dung `template` neu quan ly ca file config;
- dung `lineinfile` chi cho setting nho va co regexp chat che;
- notify handler `reload sshd` sau khi validate config;
- chay canary tren mot host truoc khi rollout ca group;
- dung `serial` de tranh lockout dong loat.

Example pattern:

```yaml
- name: Validate SSH config before reload
  command: sshd -t
  changed_when: false

- name: Reload sshd
  service:
    name: sshd
    state: reloaded
```

## Related Pages

- [Identity, Authentication And Authorization](./01-identity-authentication-authorization.md)
- [Teleport HA Access Pattern](./teleport-ha-access.md)
- [Linux Hardening Baseline](../02-os-and-network-security/linux-hardening-baseline.md)
- [Linux Security Policy Baseline](../../../02-core-infrastructure/01-linux/03-security-logs-troubleshooting/09-linux-security-policy-baseline.md)
