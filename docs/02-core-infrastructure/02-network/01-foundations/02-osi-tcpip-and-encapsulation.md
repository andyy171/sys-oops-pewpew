# OSI, TCP/IP And Encapsulation

## Overview

OSI vÃ  TCP/IP lÃ  hai mÃ´ hÃ¬nh giÃºp chia nhá» network thÃ nh nhiá»u lá»›p. Má»¥c tiÃªu khÃ´ng pháº£i há»c thuá»™c tÃªn lá»›p, mÃ  lÃ  biáº¿t sá»± cá»‘ Ä‘ang náº±m á»Ÿ lá»›p nÃ o vÃ  nÃªn dÃ¹ng cÃ´ng cá»¥ gÃ¬ Ä‘á»ƒ kiá»ƒm tra.

![OSI model visualized](../images/all-networking-concept/osi-model-visualized.png)

## OSI Model

| OSI Layer | ÄÆ¡n vá»‹ dá»¯ liá»‡u | Vai trÃ² chÃ­nh | VÃ­ dá»¥ |
| --- | --- | --- | --- |
| 7. Application | Data | protocol gáº§n application | HTTP, DNS, SSH, SMTP |
| 6. Presentation | Data | format, encode, encryption | TLS, serialization, compression |
| 5. Session | Data | duy trÃ¬ session/connection context | RPC/session handling |
| 4. Transport | Segment/Datagram | end-to-end connection, port, reliability | TCP, UDP |
| 3. Network | Packet | logical addressing vÃ  routing | IP, ICMP |
| 2. Data Link | Frame | MAC addressing, switching, VLAN | Ethernet, ARP context, 802.1Q |
| 1. Physical | Bit | signal, cable, radio, optics | copper, fiber, Wi-Fi PHY |

Má»™t lá»—i "khÃ´ng vÃ o Ä‘Æ°á»£c website" cÃ³ thá»ƒ náº±m á»Ÿ nhiá»u lá»›p: DNS layer 7, TLS layer 6, TCP port layer 4, route layer 3, VLAN layer 2 hoáº·c cable layer 1.

## TCP/IP Model

TCP/IP thÆ°á»ng gom OSI thÃ nh Ã­t lá»›p hÆ¡n:

![OSI TCP/IP side by side](../images/all-networking-concept/osi-tcpip-side-by-side.jpg)

| TCP/IP Layer | Gáº§n tÆ°Æ¡ng á»©ng OSI | VÃ­ dá»¥ |
| --- | --- | --- |
| Application | OSI 5-7 | HTTP, DNS, SSH, SMTP |
| Transport | OSI 4 | TCP, UDP |
| Internet | OSI 3 | IP, ICMP |
| Network Interface | OSI 1-2 | Ethernet, Wi-Fi, VLAN |

Trong váº­n hÃ nh, TCP/IP model thÆ°á»ng thá»±c dá»¥ng hÆ¡n vÃ¬ map gáº§n vá»›i tool:

- `curl`, `dig`, `openssl`: application/TLS/DNS.
- `ss`, `nc`, `tcpdump`: transport.
- `ip route`, `ping`, `traceroute`: internet layer.
- `ip link`, `ethtool`, switch port, VLAN: network interface.

## Encapsulation VÃ  De-Encapsulation

Khi data Ä‘i xuá»‘ng stack, má»—i lá»›p thÃªm header cá»§a nÃ³:

```text
Application data
  -> TCP/UDP segment
  -> IP packet
  -> Ethernet frame
  -> bits on wire
```

Khi nháº­n, host bÃ³c ngÆ°á»£c láº¡i:

```text
bits
  -> frame
  -> packet
  -> segment/datagram
  -> application data
```

Äiá»u nÃ y giáº£i thÃ­ch vÃ¬ sao packet capture cÃ³ nhiá»u lá»›p header. Má»™t gÃ³i HTTP qua TCP/IP/Ethernet khÃ´ng chá»‰ cÃ³ payload HTTP, mÃ  cÃ²n cÃ³ Ethernet header, IP header vÃ  TCP header.

## Troubleshooting Theo Layer

| Triá»‡u chá»©ng | Lá»›p nghi ngá» | Kiá»ƒm tra nhanh |
| --- | --- | --- |
| interface down | L1/L2 | `ip link`, `ethtool`, switch port |
| cÃ¹ng subnet khÃ´ng ping Ä‘Æ°á»£c | L2/L3 | ARP table, VLAN, firewall local |
| ping gateway Ä‘Æ°á»£c nhÆ°ng khÃ´ng ra ngoÃ i | L3 | default route, upstream route, NAT |
| ping IP Ä‘Æ°á»£c nhÆ°ng khÃ´ng resolve domain | L7 DNS | `dig`, `nslookup`, resolver config |
| TCP timeout | L3/L4/security | route, firewall, security group |
| TCP connect Ä‘Æ°á»£c nhÆ°ng HTTP lá»—i | L7 | `curl -v`, app log, proxy log |
| TLS handshake fail | L6/L7 | cert, SNI, cipher, time sync |

## Common Misunderstandings

- OSI khÃ´ng pháº£i lÃ  implementation báº¯t buá»™c; nÃ³ lÃ  mental model.
- TCP/IP khÃ´ng thay tháº¿ hoÃ n toÃ n OSI; nÃ³ lÃ  mÃ´ hÃ¬nh thá»±c dá»¥ng hÆ¡n cho Internet.
- Layer 2 dÃ¹ng MAC Ä‘á»ƒ forward trong má»™t broadcast domain; Layer 3 dÃ¹ng IP Ä‘á»ƒ route giá»¯a network.
- DNS thÃ nh cÃ´ng khÃ´ng chá»©ng minh service sá»‘ng; nÃ³ chá»‰ chá»©ng minh tÃªn Ä‘Ã£ resolve.

## Related Pages

- [Addressing, Ports And Sockets](./03-addressing-ports-and-sockets.md)
- [Common Network Protocols And Ports](../04-protocols-and-services/01-common-network-protocols-and-ports.md)
- [Network Troubleshooting Tools](../07-network-operations-lifecycle/03-network-troubleshooting-tools.md)
