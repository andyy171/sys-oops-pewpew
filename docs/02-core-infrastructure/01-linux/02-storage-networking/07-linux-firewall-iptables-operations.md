# Linux Firewall, iptables Và nftables Operations

## Overview

Linux firewall dựa trên packet filtering trong kernel. Ở tầng vận hành, bạn có thể gặp `iptables`, `nftables`, `firewalld` hoặc `ufw`. Mục tiêu của note này là đọc ruleset an toàn, hiểu packet path cơ bản, thay đổi rule có rollback và dùng firewall log để hỗ trợ troubleshooting/attack detection.

`iptables` vẫn xuất hiện nhiều ở hệ legacy và lab. `nftables` là framework hiện đại hơn. `firewalld` và `ufw` là frontend giúp quản lý policy dễ hơn trên một số distro.

## Tooling Landscape

| Tool | Vai trò |
|---|---|
| `iptables` | Interface legacy để cấu hình Netfilter table/chain/rule |
| `nft` | CLI cho `nftables`, thay thế dần iptables ở nhiều distro |
| `firewalld` | Dynamic firewall manager, zone/service model |
| `ufw` | Frontend đơn giản cho host firewall, phổ biến trên Ubuntu |
| `conntrack` | Xem state table của connection tracking |
| `tcpdump` | Capture packet để xác nhận traffic thật |

Không trộn nhiều frontend trên cùng host nếu không rõ backend đang được dùng, vì ruleset có thể khó audit.

## Read-Only Inspection

Kiểm tra công cụ và ruleset hiện tại:

```bash
sudo nft list ruleset
sudo iptables -S
sudo iptables -L -n -v
sudo iptables -t nat -L -n -v
sudo firewall-cmd --state 2>/dev/null
sudo firewall-cmd --list-all 2>/dev/null
sudo ufw status verbose 2>/dev/null
```

Kiểm tra port và process:

```bash
sudo ss -tulpn
sudo lsof -i -P -n
ip route
ip addr
```

## iptables Mental Model

iptables tổ chức rule theo table và chain.

| Table | Dùng cho |
|---|---|
| `filter` | Allow/drop traffic, thường gồm `INPUT`, `OUTPUT`, `FORWARD` |
| `nat` | DNAT, SNAT, MASQUERADE |
| `mangle` | Đánh dấu/chỉnh packet nâng cao |
| `raw` | Bỏ qua connection tracking trong trường hợp đặc biệt |

Các chain hay gặp:

- `INPUT`: packet đi vào local host.
- `OUTPUT`: packet đi ra từ local host.
- `FORWARD`: packet được route qua host.
- `PREROUTING`: xử lý trước routing decision, hay dùng DNAT.
- `POSTROUTING`: xử lý sau routing decision, hay dùng SNAT/MASQUERADE.

## Stateful Filtering

Phần lớn host firewall nên dùng state để cho phép reply traffic:

```bash
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate INVALID -j DROP
```

Mẫu policy tối thiểu cần có:

- Default deny cho inbound nếu host không phải router.
- Allow loopback.
- Allow `ESTABLISHED,RELATED`.
- Allow service cần thiết theo source/port cụ thể.
- Log có rate limit trước khi drop nếu cần điều tra.

## Safe Change Workflow

Trước khi thay đổi:

```bash
sudo iptables-save > /root/iptables.backup.$(date +%Y%m%d-%H%M%S)
sudo nft list ruleset > /root/nftables.backup.$(date +%Y%m%d-%H%M%S).txt
```

Nếu đang SSH vào máy từ xa, nên mở một phiên thứ hai hoặc có out-of-band console. Với iptables, có thể đặt rollback bằng `at` hoặc cơ chế orchestration trước khi áp rule mới.

Ví dụ cho phép SSH từ một IP quản trị mẫu:

```bash
sudo iptables -I INPUT 1 -s 203.0.113.10/32 -p tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT
sudo iptables -L INPUT -n -v --line-numbers
```

Ví dụ xóa rule theo line number sau khi kiểm tra:

```bash
sudo iptables -D INPUT <line-number>
```

## NAT Patterns

DNAT chuyển traffic vào service nội bộ:

```bash
sudo iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 10.0.0.10:80
```

MASQUERADE dùng cho outbound NAT khi IP ngoài có thể thay đổi:

```bash
sudo iptables -t nat -A POSTROUTING -o <wan-interface> -j MASQUERADE
```

Khi debug NAT, kiểm tra đủ:

```bash
ip route
sysctl net.ipv4.ip_forward
sudo iptables -t nat -L -n -v
sudo iptables -L FORWARD -n -v
```

## Logging And Detection

Rule log cần rate limit để tránh làm đầy disk:

```bash
sudo iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-drop: " --log-level 4
```

Xem log:

```bash
sudo journalctl -k --since "1 hour ago"
sudo dmesg -T | tail -100
```

Các dấu hiệu cần chú ý:

- Nhiều SYN tới nhiều port khác nhau: có thể là port scan.
- Nhiều attempt tới SSH/RDP/VPN từ source lạ.
- Traffic outbound tới IP/port không thuộc baseline.
- Drop tăng nhanh sau khi deploy app hoặc đổi route.

Một số stack cũ dùng `psad` hoặc `fwsnort` để phân tích iptables log và map rule kiểu IDS. Nếu gặp trong hệ thống legacy, hãy coi chúng là nguồn tín hiệu bổ sung, không thay thế log tập trung/IDS hiện đại.

## Troubleshooting Packet Path

Khi "port không vào được", đi theo thứ tự:

1. App có listen đúng interface/port không.
2. Local firewall host có drop không.
3. Route và reverse route có đúng không.
4. Security group/network ACL/firewall upstream có chặn không.
5. NAT hoặc load balancer có rewrite sai không.

Lệnh kiểm tra:

```bash
sudo ss -tulpn | grep <port>
sudo iptables -L -n -v --line-numbers
sudo nft list ruleset
ip route get <client-ip>
sudo tcpdump -i <interface> -nn host <client-ip> and port <port>
```

Nếu thấy packet vào interface nhưng không thấy app nhận, tập trung vào local firewall/routing/listen address. Nếu không thấy packet vào host, kiểm tra upstream trước.

## Persistence

Rule tạm sẽ mất sau reboot nếu không được persist bằng cơ chế distro:

- RHEL-family thường dùng `firewalld` hoặc `iptables-services`.
- Ubuntu thường dùng `ufw`, `netfilter-persistent` hoặc systemd unit tùy chuẩn nội bộ.
- Với `nftables`, kiểm tra `/etc/nftables.conf` và service liên quan.

Trước khi persist rule, cần có review, backup ruleset cũ và test rollback.

## Related Pages

- [IP, Route, DNS và Firewall](./04-ip-route-dns-firewall.md)
- [Linux Routing, Netfilter Và Policy Routing](./06-linux-routing-netfilter-policy-routing.md)
- [Linux Incident Response Live Triage](../03-security-logs-troubleshooting/07-linux-incident-response-live-triage.md)
- [Network Tools And Troubleshooting](../../02-network/Tools%20&%20Troubleshooting/netstat,%20ss,%20tcpdump,%20nmap,%20netcat.md)
