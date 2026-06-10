# Linux Routing, Netfilter Và Policy Routing

## Overview

Linux networking có hai mảng dễ bị trộn lẫn:

- **Routing** quyết định packet đi đâu: interface nào, next-hop nào, routing table nào.
- **Filtering/NAT** quyết định packet có được cho qua, bị sửa header, bị mark, bị drop hay reject không.

`ip route`, `ip rule`, `nftables`, `iptables`, `conntrack` và `tcpdump` nhìn vào các phần khác nhau của cùng packet path. Khi debug, cần tách rõ routing decision và firewall decision.

## Packet Path Mental Model

Packet có thể rơi vào ba nhóm:

| Packet type | Ý nghĩa | Chain/hook thường gặp |
|---|---|---|
| Incoming local | packet từ ngoài vào chính host | `PREROUTING` -> route lookup -> `INPUT` |
| Forwarded | host đóng vai trò router, packet đi xuyên qua host | `PREROUTING` -> route lookup -> `FORWARD` -> `POSTROUTING` |
| Locally generated | process local tạo packet đi ra ngoài | `OUTPUT` -> route lookup -> `POSTROUTING` |

Netfilter hooks thường gặp:

| Hook | Khi nào chạy | Ví dụ xử lý |
|---|---|---|
| `PREROUTING` | packet vừa vào host, trước routing decision | DNAT, mangle mark |
| `INPUT` | packet đích là local host | allow/drop service inbound |
| `FORWARD` | packet được route qua host | firewall router/gateway |
| `OUTPUT` | packet do local process tạo | local egress filtering, mark |
| `POSTROUTING` | trước khi packet rời host | SNAT/MASQUERADE |

## Routing Table Và RPDB

Linux có Routing Policy Database (RPDB). Thay vì chỉ có một routing table, Linux có thể có nhiều table và `ip rule` quyết định table nào được lookup.

Kiểm tra rule và route:

```bash
ip rule show
ip route show
ip route show table main
ip route show table local
ip route get 10.0.0.20
```

Các table phổ biến:

| Table | Ý nghĩa |
|---|---|
| `local` | route local/broadcast do kernel quản lý |
| `main` | routing table chính mà admin thường thấy |
| `default` | ít dùng trong cấu hình thông thường |
| custom table | dùng cho policy routing, multi-homing, VPN split route |

Rule có priority. Rule priority thấp hơn được xét trước. Khi một rule match, kernel lookup routing table tương ứng.

## Policy Based Routing

Policy routing hữu ích khi path không chỉ phụ thuộc destination IP. Ví dụ:

- Traffic từ source subnet A đi gateway A.
- Traffic có `fwmark` từ firewall đi qua VPN table.
- Multi-homed host cần chọn outbound interface theo source IP.

Ví dụ source-based routing:

```bash
sudo ip route add default via 10.0.10.1 dev eth0 table 100
sudo ip rule add from 10.0.10.0/24 table 100 priority 1000
ip route get 8.8.8.8 from 10.0.10.10
```

Ví dụ fwmark:

```bash
sudo iptables -t mangle -A PREROUTING -s 10.0.20.0/24 -j MARK --set-mark 20
sudo ip route add default via 10.0.20.1 dev eth1 table 120
sudo ip rule add fwmark 20 table 120 priority 1020
```

Warning: chỉ dùng ví dụ trên trong lab hoặc change window đã có rollback. Với production, cần lưu trạng thái trước khi đổi rule/route.

## iptables Và nftables

`iptables` là interface legacy rất phổ biến. `nftables` là framework hiện đại hơn. Trên nhiều distro mới, lệnh `iptables` có thể chạy qua compatibility layer dùng backend nftables.

Kiểm tra:

```bash
iptables --version
sudo iptables -S
sudo iptables -L -n -v --line-numbers
sudo nft list ruleset
```

iptables tables thường gặp:

| Table | Dùng để làm gì |
|---|---|
| `filter` | allow/drop/reject packet |
| `nat` | SNAT, DNAT, MASQUERADE |
| `mangle` | chỉnh mark/TOS/TTL hoặc xử lý đặc biệt |
| `raw` | bypass conntrack trong trường hợp đặc biệt |
| `security` | security labeling, ít gặp hơn |

Default chains:

| Chain | Ý nghĩa |
|---|---|
| `INPUT` | inbound tới local host |
| `OUTPUT` | outbound từ local host |
| `FORWARD` | routed packet đi qua host |
| `PREROUTING` | trước routing decision |
| `POSTROUTING` | trước egress |

## Conntrack State

Stateful firewall dựa vào conntrack để biết packet thuộc connection nào.

| State | Ý nghĩa |
|---|---|
| `NEW` | packet mở connection mới |
| `ESTABLISHED` | packet thuộc connection đã có hai chiều |
| `RELATED` | connection phụ liên quan connection đã có |
| `INVALID` | packet không map được vào state hợp lệ |
| `UNTRACKED` | packet được loại khỏi tracking |

Kiểm tra nhanh:

```bash
sudo conntrack -L 2>/dev/null | head
sudo conntrack -S 2>/dev/null
```

Nếu không có `conntrack`, có thể kiểm tra module/rules bằng `iptables -S` hoặc `nft list ruleset` trước.

## NAT: SNAT, DNAT, MASQUERADE

| Kiểu | Thường nằm ở đâu | Ý nghĩa |
|---|---|---|
| DNAT | `PREROUTING` hoặc `OUTPUT` trong table `nat` | đổi destination, dùng cho port forward/load balancer đơn giản |
| SNAT | `POSTROUTING` trong table `nat` | đổi source cố định |
| MASQUERADE | `POSTROUTING` trong table `nat` | SNAT động theo IP interface, hay dùng khi IP WAN thay đổi |

Ví dụ đọc rule:

```bash
sudo iptables -t nat -S
sudo iptables -t nat -L -n -v --line-numbers
```

## Troubleshooting Flow

### 1. Xác định route kernel chọn

```bash
ip addr
ip route
ip rule show
ip route get <destination-ip>
```

Nếu source IP quan trọng:

```bash
ip route get <destination-ip> from <source-ip>
```

### 2. Kiểm tra neighbor và gateway

```bash
ip neigh
ping -c 3 <gateway-ip>
```

### 3. Kiểm tra firewall/ruleset

```bash
sudo nft list ruleset
sudo iptables -S
sudo iptables -L -n -v --line-numbers
sudo iptables -t nat -L -n -v --line-numbers
```

### 4. Bắt packet để chứng minh packet path

```bash
sudo tcpdump -i any -nn host <peer-ip>
sudo tcpdump -i <interface> -nn 'tcp and port 443'
```

Nếu packet đi ra nhưng không quay lại, tập trung vào route return path, firewall phía đích hoặc NAT. Nếu packet không rời host, kiểm tra local route, policy rule, firewall OUTPUT/FORWARD và application binding.

## Change Safety

Trước khi thay đổi routing/firewall production:

1. Có out-of-band access hoặc console.
2. Lưu trạng thái hiện tại.
3. Dùng `tmux`/`screen` khi thao tác remote.
4. Áp dụng rule hẹp trước, kiểm tra counter/log.
5. Có rollback command hoặc config backup.

Lưu trạng thái:

```bash
ip rule show
ip route show table all
sudo iptables-save
sudo nft list ruleset
```

Warning: không flush toàn bộ rule trên server production nếu chưa có console/rollback. Một lệnh flush nhầm có thể cắt SSH, mở firewall quá rộng hoặc làm mất NAT cho workload phía sau.

## Related Pages

- [IP, Route, DNS và Firewall](./04-ip-route-dns-firewall.md)
- [SSH, JumpHost, LLDP, Bridge và Network Namespace](./05-ssh-jumphost-lldp-bridge-netns.md)
- [Networking Interview And Operations Quick Reference](../../02-network/00-networking-interview-operations-quick-reference.md)
- [netstat, ss, tcpdump, nmap, netcat](../../02-network/Tools%20&%20Troubleshooting/netstat,%20ss,%20tcpdump,%20nmap,%20netcat.md)
- [Network Monitoring And Packet Analysis](../../../05-infrastructure-automation/02-security-and-hardening/02-os-and-network-security/network-monitoring-and-packet-analysis.md)
