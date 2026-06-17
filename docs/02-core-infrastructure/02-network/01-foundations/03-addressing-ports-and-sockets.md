# Addressing, Ports And Sockets

## Overview

Network communication cáº§n nhiá»u loáº¡i Ä‘á»‹a chá»‰ á»Ÿ nhiá»u lá»›p khÃ¡c nhau:

- MAC address Ä‘á»ƒ giao tiáº¿p trong Layer 2 segment.
- IP address Ä‘á»ƒ Ä‘á»‹nh danh host hoáº·c interface á»Ÿ Layer 3.
- Port Ä‘á»ƒ Ä‘á»‹nh danh process/service á»Ÿ Layer 4.
- Protocol Ä‘á»ƒ Ä‘á»‹nh nghÄ©a luáº­t trao Ä‘á»•i dá»¯ liá»‡u.

Hiá»ƒu Ä‘Ãºng cÃ¡c lá»›p nÃ y giÃºp trÃ¡nh nháº§m láº«n giá»¯a "mÃ¡y nÃ o", "network nÃ o", "service nÃ o" vÃ  "application nÃ³i chuyá»‡n kiá»ƒu gÃ¬".

## MAC Address

MAC address lÃ  Ä‘á»‹a chá»‰ Layer 2 gáº¯n vá»›i network interface. Switch dÃ¹ng MAC table Ä‘á»ƒ quyáº¿t Ä‘á»‹nh frame Ä‘i ra port nÃ o.

Äáº·c Ä‘iá»ƒm:

- ThÆ°á»ng dÃ i 48 bit, biá»ƒu diá»…n dáº¡ng hex nhÆ° `00:11:22:aa:bb:cc`.
- CÃ³ Ã½ nghÄ©a trong cÃ¹ng broadcast domain.
- KhÃ´ng dÃ¹ng Ä‘á»ƒ route qua Internet.
- CÃ³ thá»ƒ thay Ä‘á»•i/spoof trong má»™t sá»‘ trÆ°á»ng há»£p.

Kiá»ƒm tra trÃªn Linux:

```bash
ip link
ip neigh
```

## IP Address

IP address lÃ  Ä‘á»‹a chá»‰ Layer 3 dÃ¹ng Ä‘á»ƒ route packet giá»¯a network.

VÃ­ dá»¥ IPv4:

```text
192.168.1.10/24
```

Trong Ä‘Ã³:

- `192.168.1.10` lÃ  Ä‘á»‹a chá»‰ host/interface.
- `/24` lÃ  prefix length, cho biáº¿t pháº§n network dÃ i 24 bit.
- Host cáº§n route/default gateway Ä‘á»ƒ Ä‘i ra ngoÃ i subnet.

### IPv4 Và IPv6

IPv4 dài 32 bit, thường viết bằng 4 octet như `192.0.2.10`. IPv6 dài 128 bit, viết bằng các nhóm hexadecimal như `2001:db8::10`. Trong production hiện đại, IPv4 vẫn rất phổ biến vì legacy system, NAT và private addressing; IPv6 hữu ích khi cần address space lớn, public routability rõ hơn và giảm phụ thuộc NAT, nhưng phải kiểm soát firewall, routing, DNS `AAAA` record và observability tương ứng.

Không nên coi IPv6 là "tự an toàn hơn" hoặc "tự đơn giản hơn". Dual-stack thường làm troubleshooting khó hơn vì cùng một hostname có thể resolve ra cả IPv4 và IPv6, trong khi path/firewall của hai family khác nhau.

## Protocol, Port VÃ  Socket

Protocol Ä‘á»‹nh nghÄ©a cÃ¡ch hai bÃªn giao tiáº¿p. Port giÃºp há»‡ Ä‘iá»u hÃ nh phÃ¢n biá»‡t traffic thuá»™c service nÃ o.

VÃ­ dá»¥:

```text
TCP 10.0.0.10:54321 -> 10.0.0.20:443
```

Má»™t socket thÆ°á»ng Ä‘Æ°á»£c nháº­n diá»‡n báº±ng tá»• há»£p:

```text
source IP + source port + destination IP + destination port + protocol
```

Nhá» port, má»™t server cÃ³ thá»ƒ cháº¡y nhiá»u service:

| Service | Protocol | Port thÆ°á»ng gáº·p |
| --- | --- | --- |
| SSH | TCP | 22 |
| DNS | UDP/TCP | 53 |
| HTTP | TCP | 80 |
| HTTPS | TCP | 443 |
| SMTP | TCP | 25 |
| RDP | TCP/UDP | 3389 |

### TCP Socket Lifecycle

Ở mức application, TCP socket thường đi theo flow:

| Server | Client | Ý nghĩa |
| --- | --- | --- |
| `socket()` | `socket()` | Tạo communication endpoint |
| `bind()` | tùy chọn | Server gắn local IP/port; client thường để OS chọn ephemeral port |
| `listen()` | - | Server khai báo backlog cho pending connection |
| `accept()` | `connect()` | Server block chờ connection; client chủ động mở connection |
| `recv()` / `send()` | `send()` / `recv()` | Hai bên trao đổi byte stream |
| `close()` | `close()` | Đóng connection/socket |

Điểm hay nhầm: socket lắng nghe ban đầu không phải socket dùng cho từng client. Khi `accept()` thành công, OS tạo một connected socket mới cho connection đó; listening socket vẫn tiếp tục nhận connection mới.

Operational checks:

```bash
ss -lntup
ss -tan state established
ss -tan state time-wait
```

Nếu backlog quá nhỏ hoặc application `accept()` chậm, client có thể thấy timeout/reset dù port vẫn listen. Khi tăng backlog, cũng kiểm tra kernel limit, load balancer health check, số worker và thời gian xử lý mỗi request.

## Transmission Types

![Unicast multicast broadcast](../images/all-networking-concept/unicast-multicast-broadcast.jpg)

| Kiá»ƒu truyá»n | Ã nghÄ©a | VÃ­ dá»¥ |
| --- | --- | --- |
| Unicast | má»™t nguá»“n tá»›i má»™t Ä‘Ã­ch | client gá»i web server |
| Multicast | má»™t nguá»“n tá»›i má»™t nhÃ³m receiver | streaming, routing protocol |
| Broadcast | má»™t nguá»“n tá»›i toÃ n bá»™ broadcast domain | ARP request trong IPv4 LAN |

Broadcast cáº§n Ä‘Æ°á»£c kiá»ƒm soÃ¡t vÃ¬ broadcast domain quÃ¡ lá»›n cÃ³ thá»ƒ gÃ¢y nhiá»…u vÃ  lÃ m tÄƒng táº£i trÃªn host/switch.

## Duplex

Duplex mÃ´ táº£ hÆ°á»›ng truyá»n dá»¯ liá»‡u:

- **Half-duplex**: chá»‰ má»™t bÃªn truyá»n táº¡i má»™t thá»i Ä‘iá»ƒm.
- **Full-duplex**: hai bÃªn truyá»n/nháº­n Ä‘á»“ng thá»i.

Trong Ethernet hiá»‡n Ä‘áº¡i, full-duplex lÃ  phá»• biáº¿n. Mismatch duplex giá»¯a hai Ä‘áº§u cÃ³ thá»ƒ gÃ¢y performance issue, CRC/error hoáº·c throughput tháº¥p.

Kiá»ƒm tra:

```bash
ethtool <interface>
```

## Related Pages

- [OSI, TCP/IP And Encapsulation](./02-osi-tcpip-and-encapsulation.md)
- [IPv4 Addressing And Subnetting](../03-ip-routing-subnetting/01-ipv4-addressing-and-subnetting.md)
- [Network Troubleshooting Tools](../07-network-operations-lifecycle/03-network-troubleshooting-tools.md)
