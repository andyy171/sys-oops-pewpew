# IPv4 Addressing And Subnetting

## Overview

IPv4 addressing giÃºp xÃ¡c Ä‘á»‹nh host náº±m trong network nÃ o vÃ  cáº§n route ra sao. Subnetting lÃ  ká»¹ thuáº­t chia má»™t network lá»›n thÃ nh nhiá»u network nhá» hÆ¡n Ä‘á»ƒ quáº£n lÃ½ broadcast domain, routing, security boundary vÃ  capacity.

![IPv4 address anatomy](../images/all-networking-concept/ipv4-address-anatomy.jpg)

## IPv4 Anatomy

IPv4 dÃ i 32 bit, thÆ°á»ng viáº¿t thÃ nh 4 octet:

```text
192.168.1.131
```

Má»—i octet cÃ³ 8 bit. CIDR notation cho biáº¿t prefix network dÃ i bao nhiÃªu bit:

```text
192.168.1.131/24
```

Vá»›i `/24`:

- Network portion: 24 bit.
- Host portion: 8 bit.
- Network thÆ°á»ng lÃ  `192.168.1.0`.
- Broadcast thÆ°á»ng lÃ  `192.168.1.255`.
- Usable host thÆ°á»ng tá»« `192.168.1.1` Ä‘áº¿n `192.168.1.254`.

## Public, Private VÃ  Loopback

Private IPv4 ranges:

| Range | CIDR |
| --- | --- |
| 10.0.0.0 - 10.255.255.255 | `10.0.0.0/8` |
| 172.16.0.0 - 172.31.255.255 | `172.16.0.0/12` |
| 192.168.0.0 - 192.168.255.255 | `192.168.0.0/16` |

Loopback:

```text
127.0.0.0/8
```

`127.0.0.1` luÃ´n trá» vá» chÃ­nh host local, khÃ´ng Ä‘i ra network card tháº­t.

### Public/Private Và Static/Dynamic

Public IPv4 là địa chỉ có thể route trên Internet public. Private IPv4 chỉ có ý nghĩa trong network nội bộ hoặc VPC/VNet/project network và thường cần NAT, proxy, VPN hoặc private interconnect để nói chuyện ra ngoài.

Static IP là địa chỉ được giữ ổn định cho một host/service, phù hợp với endpoint cần allowlist, DNS record cố định, VPN gateway, load balancer frontend hoặc hệ thống legacy. Dynamic IP được cấp theo lease hoặc theo lifecycle resource, phù hợp cho client, ephemeral VM, container node hoặc môi trường autoscaling.

Nhầm lẫn phổ biến trong cloud là coi private IP đồng nghĩa với "an toàn". Private IP giảm exposure trực tiếp từ Internet, nhưng service vẫn có thể bị truy cập qua VPN, peering, bastion, load balancer, NAT rule, compromised workload hoặc route sai. Security boundary vẫn cần IAM, firewall/security group, routing control và logging.

## Subnet Mask VÃ  CIDR

| CIDR | Subnet mask | Host bits | Usable hosts |
| --- | --- | ---: | ---: |
| `/24` | `255.255.255.0` | 8 | 254 |
| `/25` | `255.255.255.128` | 7 | 126 |
| `/26` | `255.255.255.192` | 6 | 62 |
| `/27` | `255.255.255.224` | 5 | 30 |
| `/28` | `255.255.255.240` | 4 | 14 |
| `/29` | `255.255.255.248` | 3 | 6 |
| `/30` | `255.255.255.252` | 2 | 2 |

CÃ´ng thá»©c nhanh:

```text
Number of addresses = 2 ^ host_bits
Usable hosts = 2 ^ host_bits - 2
```

Trá»« 2 vÃ¬ IPv4 subnet truyá»n thá»‘ng dÃ nh má»™t Ä‘á»‹a chá»‰ cho network vÃ  má»™t Ä‘á»‹a chá»‰ cho broadcast.

## CÃ¡ch NghÄ© Khi Chia Subnet

1. XÃ¡c Ä‘á»‹nh network gá»‘c, vÃ­ dá»¥ `192.168.1.0/24`.
2. XÃ¡c Ä‘á»‹nh cáº§n bao nhiÃªu subnet hoáº·c má»—i subnet cáº§n bao nhiÃªu host.
3. Chá»n prefix phÃ¹ há»£p.
4. TÃ­nh block size.
5. Liá»‡t kÃª network address, usable range vÃ  broadcast.
6. GÃ¡n subnet theo chá»©c nÄƒng: user, server, storage, management, DMZ, transit.

VÃ­ dá»¥ chia `192.168.1.0/24` thÃ nh cÃ¡c subnet `/26`:

| Subnet | Usable range | Broadcast |
| --- | --- | --- |
| `192.168.1.0/26` | `192.168.1.1 - 192.168.1.62` | `192.168.1.63` |
| `192.168.1.64/26` | `192.168.1.65 - 192.168.1.126` | `192.168.1.127` |
| `192.168.1.128/26` | `192.168.1.129 - 192.168.1.190` | `192.168.1.191` |
| `192.168.1.192/26` | `192.168.1.193 - 192.168.1.254` | `192.168.1.255` |

## Routing Mental Model

Host quyáº¿t Ä‘á»‹nh gá»­i packet nhÆ° sau:

1. Náº¿u destination thuá»™c cÃ¹ng subnet, gá»­i trá»±c tiáº¿p qua Layer 2 báº±ng ARP.
2. Náº¿u destination khÃ¡c subnet, gá»­i tá»›i default gateway.
3. Router nhÃ¬n routing table Ä‘á»ƒ chá»n next hop.
4. Náº¿u khÃ´ng cÃ³ route, packet bá»‹ drop hoáº·c tráº£ ICMP unreachable tÃ¹y thiáº¿t bá»‹/policy.

Kiá»ƒm tra trÃªn Linux:

```bash
ip addr
ip route
ip route get <destination-ip>
ping <gateway-ip>
traceroute <destination-ip>
```

## Common Mistakes

- Nháº§m `/24` lÃ  "class C" cá»‘ Ä‘á»‹nh. CIDR khÃ´ng phá»¥ thuá»™c classful thinking cÅ©.
- GÃ¡n IP host trÃ¹ng network address hoáº·c broadcast address.
- QuÃªn default gateway.
- Subnet overlap giá»¯a site-to-site VPN, VPC, Kubernetes pod CIDR hoáº·c service CIDR.
- NhÃ¬n `kubectl top`/dashboard rá»“i káº¿t luáº­n network cÃ²n "ráº£nh"; routing vÃ  subnet khÃ´ng hoáº¡t Ä‘á»™ng theo cÃ¡ch Ä‘Ã³.

## Related Pages

- [Routing, NAT And Virtual Router](./02-routing-nat-and-virtual-router.md)
- [VLAN, LACP And Layer 2 Operations](../02-ethernet-switching/02-vlan-lacp-and-layer2-operations.md)
- [Network Troubleshooting Tools](../07-network-operations-lifecycle/03-network-troubleshooting-tools.md)
