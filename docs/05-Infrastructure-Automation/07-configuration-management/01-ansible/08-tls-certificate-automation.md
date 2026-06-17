# Ansible TLS Certificate Automation

## Overview

TLS certificate automation gom ba viec rieng nhau:

- tao hoac lay certificate;
- cai certificate/key/chain vao dung service;
- renew/rotate truoc khi het han va validate traffic that.

Ansible phu hop de quan ly workflow nay, nhung private key va reload web server la security-sensitive operation. Playbook phai co pre-check, validation, rollback va secret handling ro rang.

## Certificate Types

| Loai | Dung khi | Guardrail |
|---|---|---|
| Self-signed | lab, dev, internal test, bootstrap tam thoi | client se khong trust mac dinh; khong dung cho public production |
| Internal CA | private service, enterprise PKI, mTLS noi bo | phan phoi CA trust store co kiem soat |
| Public CA / ACME | public website/API | DNS/HTTP validation phai reach duoc; monitor renewal |

Self-signed certificate huu ich de test TLS config, nhung khong nen day user hoac service production vao thoi quen bo qua certificate validation.

## Ansible Workflow

```text
pre-check DNS/firewall/service ownership
-> ensure package/collection dependency
-> create or fetch certificate
-> install key/cert/chain with strict permission
-> render web/proxy config
-> validate config syntax
-> reload service
-> validate HTTPS from client path
-> monitor expiry and renewal
```

Pre-check:

```bash
ansible-playbook -i inventory.ini tls.yml --list-hosts
ansible-playbook -i inventory.ini tls.yml --check --diff --limit node-1
```

## Self-Signed Pattern

Use maintained Ansible crypto modules/collections and pin their versions in the project. Avoid shelling out to `openssl` unless module support is insufficient.

High-level task model:

```text
create private key
-> create CSR with SAN
-> create self-signed certificate
-> install key as 0600 owned by service/root
-> install certificate/chain as readable by service
```

Guardrails:

- Certificate hostname phai co trong SAN; chi CN khong du cho client hien dai.
- Private key khong duoc commit vao Git, in ra log, hoac copy vao artifact.
- Neu rebuild lab sinh cert moi, client co the can xoa trust cache/cert cu.
- Self-signed cert chi nen duoc trust trong pham vi ro rang.

## ACME / Certbot Pattern

ACME/Certbot automation phu hop cho public endpoint khi CA can verify domain ownership. Playbook phai dam bao:

- DNS cua domain tro dung endpoint;
- port validation can thiet duoc mo tu Internet hoac DNS challenge duoc cau hinh dung;
- email/contact cua certificate owner duoc quan ly;
- renewal job/timer ton tai va duoc monitor;
- web server reload sau renewal neu can.

Khong automate hang loat domain/subdomain khi chua hieu rate limit cua CA va chua co staging/test endpoint. Voi production, test renewal path quan trong hon test first-issue path.

## Nginx TLS Termination

Nginx co the terminate TLS va serve static content hoac proxy ve backend HTTP/private service.

Config rollout pattern:

```text
render nginx config
-> nginx -t
-> reload nginx
-> curl -vk https://<host>
-> check access/error log
```

HTTP-to-HTTPS redirect nen duoc cau hinh ro, nhung can tranh loop khi co load balancer/CDN dung `X-Forwarded-Proto` phia truoc.

## HTTPS Reverse Proxy

Pattern:

```text
Client
-> HTTPS reverse proxy / TLS termination
-> backend HTTP service on private network
```

Dung khi app legacy chi noi HTTP nhung endpoint user-facing can HTTPS. Guardrails:

- backend nen nam tren localhost/private network, khong expose public HTTP;
- proxy timeout, header forwarding va body size can phu hop app;
- health check phai kiem tra backend, khong chi Nginx process;
- 502 Bad Gateway thuong nghia la proxy reach duoc config nhung backend khong san sang hoac route sai.

## Validation

Read-only validation:

```bash
curl -vk https://example.com
openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null
systemctl status nginx --no-pager
journalctl -u nginx --since "10 minutes ago" --no-pager
```

Check:

- SAN khop hostname;
- chain day du;
- certificate chua het han;
- private key permission chat;
- HTTP redirect dung;
- backend health dung;
- renewal job/timer dang active.

## Rollback

Truoc khi thay config/cert production:

```bash
sudo cp -a /etc/nginx /etc/nginx.bak.$(date +%F-%H%M%S)
sudo cp -a /etc/letsencrypt /etc/letsencrypt.bak.$(date +%F-%H%M%S)
```

Rollback co the la restore config/cert cu va reload service. Khong xoa cert/key cu ngay sau rotation; giu trong retention ngan va bao ve permission de co rollback.

## Related Pages

- [Ansible Overview](./overview.md)
- [Ansible Security Hardening Patterns](./06-security-hardening-patterns.md)
- [Firewall SSL Inspection And Certificates](../../02-security-and-hardening/02-os-and-network-security/02-firewall-ssl-inspection-and-certificates.md)
- [CA Certificates, GRUB va Boot Security](../../../02-core-infrastructure/01-linux/03-security-logs-troubleshooting/02-ca-certificates-grub-boot-security.md)
- [Proxy, Load Balancer, VPN And Expose Endpoints](../../../02-core-infrastructure/02-network/04-protocols-and-services/03-proxy-load-balancer-vpn-and-expose-endpoints.md)
