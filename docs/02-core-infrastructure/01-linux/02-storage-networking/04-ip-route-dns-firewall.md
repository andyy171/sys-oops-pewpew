# IP, Route, DNS và Firewall

## 1. Network Interface Overview

Kiểm tra interface:

```bash
ip link
ip addr
nmcli device status
ethtool <interface>
```

State thường gặp:

- `UP`: interface đang bật ở layer 2.
- `LOWER_UP`: có carrier/link vật lý.
- `DOWN`: interface tắt hoặc chưa có link.

## 2. IP Address

Xem IP:

```bash
ip addr show
ip -br addr
```

Gán IP tạm thời:

```bash
sudo ip addr add 10.0.0.10/24 dev eth0
sudo ip link set eth0 up
```

Xóa IP tạm thời:

```bash
sudo ip addr del 10.0.0.10/24 dev eth0
```

Các thay đổi bằng `ip addr`, `ip route` và `ip link` thường là runtime state, mất sau reboot hoặc khi network manager apply lại config. Trên server remote, đổi IP/route có thể làm mất SSH; cần console/OOB, maintenance window hoặc rollback command đã chuẩn bị sẵn.

IPv4 dùng địa chỉ 32-bit và subnet/CIDR để tách network part với host part. Các private range thường gặp là `10.0.0.0/8`, `172.16.0.0/12` và `192.168.0.0/16`; chúng không route trực tiếp trên Internet nếu không đi qua NAT, proxy, VPN hoặc route riêng.

IPv6 dùng địa chỉ 128-bit, có thể rút gọn bằng `::` một lần trong địa chỉ. Link-local address bắt đầu bằng `fe80::` chỉ có ý nghĩa trên local link; khi ping link-local thường phải chỉ interface zone.

```bash
ip -6 addr show
ping -c 3 fe80::1%eth0
```

Persistent config phụ thuộc distro/network stack:

- NetworkManager: `nmcli`.
- Netplan: Ubuntu server mới.
- `/etc/sysconfig/network-scripts/`: RHEL/CentOS cũ.
- systemd-networkd: một số server/minimal image.

Ví dụ với NetworkManager:

```bash
nmcli connection show
nmcli device status
sudo nmcli connection modify <connection> ipv4.addresses 10.0.0.10/24 ipv4.gateway 10.0.0.1 ipv4.method manual
sudo nmcli connection up <connection>
```

Với Ubuntu Server dùng Netplan, thay đổi thường nằm trong `/etc/netplan/*.yaml` và backend có thể là `systemd-networkd` hoặc NetworkManager. YAML sai indentation có thể làm cấu hình không apply được, nên kiểm tra qua console/OOB khi đổi IP trên server remote.

```bash
sudo netplan try
sudo netplan apply
networkctl status 2>/dev/null || nmcli device status
```

Với RHEL-family dùng NetworkManager, ưu tiên `nmcli`/`nmtui` thay vì sửa file thủ công nếu distro đang quản lý connection bằng NetworkManager.

Tạo connection mới bằng `nmcli` nên làm có kiểm soát, vì đặt sai `ifname`, gateway hoặc `ipv4.method` có thể làm host mất network sau khi `connection up`:

```bash
nmcli connection show
nmcli device status
sudo nmcli connection add type ethernet con-name <conn-name> ifname <interface> ipv4.addresses 10.0.0.10/24 ipv4.gateway 10.0.0.1 ipv4.method manual
sudo nmcli connection up <conn-name>
```

Trước khi đổi persistent network config trên host remote, ghi lại state hiện tại:

```bash
ip -br addr
ip route
resolvectl status 2>/dev/null || cat /etc/resolv.conf
nmcli connection show 2>/dev/null || true
```

## 3. Route

```bash
ip route
ip route get 8.8.8.8
```

Thêm default route tạm thời:

```bash
sudo ip route add default via 10.0.0.1 dev eth0
```

Thêm route tạm thời:

```bash
sudo ip route add 10.20.0.0/16 via 10.0.0.254 dev eth0
```

NAT/PAT/masquerade giúp nhiều host private đi ra ngoài qua một địa chỉ public hoặc địa chỉ upstream, nhưng NAT không phải firewall. Vẫn cần policy rõ cho inbound, outbound, stateful rule, security group hoặc firewall rule ở đúng lớp.

Troubleshooting route:

```bash
ip addr
ip route
ip neigh
ping -c 3 <gateway>
tracepath <target>
```

## 4. DNS Resolver

Kiểm tra resolver:

```bash
cat /etc/resolv.conf
resolvectl status
getent hosts example.com
dig example.com
nslookup example.com
```

Phân biệt:

- `dig` kiểm tra DNS query trực tiếp.
- `getent hosts` dùng NSS stack, gần với cách app resolve hostname.
- `resolvectl` hữu ích khi dùng `systemd-resolved`.

Flush cache:

```bash
sudo resolvectl flush-caches
```

## 5. Hostname và Domain

```bash
hostname
hostnamectl
sudo hostnamectl set-hostname node-1.example.com
```

`/etc/hosts` dùng mapping local:

```text
10.0.0.10 node-1.example.com node-1
```

Trên nhiều distro, NSS thường kiểm tra `/etc/hosts` trước DNS theo `/etc/nsswitch.conf`. Vì vậy một entry cũ trong `/etc/hosts` có thể làm `dig` đúng nhưng application vẫn resolve sai. Không dùng `/etc/hosts` để che lỗi DNS lâu dài nếu hệ thống cần scale.

`/etc/resolv.conf` có thể là file thật hoặc symlink do NetworkManager, systemd-resolved, netplan hoặc DHCP client quản lý. Trước khi sửa tay, kiểm tra owner/backend:

```bash
ls -l /etc/resolv.conf
readlink -f /etc/resolv.conf
resolvectl status 2>/dev/null || true
nmcli dev show 2>/dev/null | grep -E 'DNS|DOMAIN'
```

Sửa trực tiếp file do backend quản lý thường bị ghi đè sau DHCP renew, reboot hoặc network reload.

### DNS, NSS Và Split-Horizon Troubleshooting

Không phải mọi lỗi "DNS sai" đều nằm ở DNS server. Linux application thường resolve name qua NSS stack, nên kết quả có thể đến từ `/etc/hosts`, mDNS, LDAP/SSSD hoặc DNS tùy `/etc/nsswitch.conf`. Vì vậy `dig` đúng nhưng app vẫn sai thường là dấu hiệu cần kiểm tra NSS hoặc local override.

Checklist nhanh:

```bash
getent hosts app.example.com
dig app.example.com
cat /etc/nsswitch.conf
grep -n "app.example.com" /etc/hosts
resolvectl status 2>/dev/null || true
```

Với split-horizon DNS qua VPN hoặc nhiều search domain, kiểm tra resolver theo interface và domain route thay vì chỉ nhìn một dòng `nameserver`:

```bash
resolvectl domain
resolvectl dns
nmcli dev show 2>/dev/null | grep -E 'DNS|DOMAIN'
```

Nếu chỉ một subnet hoặc chỉ khi bật VPN mới lỗi, kiểm tra route tới DNS server, search domain, policy routing, firewall outbound `53/udp`, `53/tcp` và proxy policy của tổ chức. Không sửa `/etc/hosts` dài hạn để che lỗi DNS nội bộ trừ khi đó là break-glass tạm thời đã ghi vào ticket.

## 6. Connectivity Tools

```bash
ping -c 3 8.8.8.8
tracepath example.com
traceroute example.com
ss -tulpn
ss -s
curl -vk https://example.com
nc -vz <host> <port>
```

`ss -tulpn` giúp xem process đang listen port nào:

```bash
sudo ss -tulpn
```

Chọn tool theo tình huống:

| Tình huống | Tool nên dùng | Ghi chú |
| --- | --- | --- |
| Interface/IP | `ip addr`, `ip link`, `nmcli device status`, `hostnamectl` | `ifconfig` là tool cũ; ưu tiên `ip` trên hệ hiện đại |
| Routing | `ip route`, `ip route get <ip>`, `tracepath`, `mtr` | kiểm tra cả route đi và khả năng reverse path khi cần |
| DNS | `getent hosts`, `dig`, `host`, `resolvectl status` | `getent` gần với cách application resolve hostname hơn vì đi qua NSS |
| Socket/port | `ss -tulpn`, `ss -s`, `lsof -i -P -n`, `nc -vz` | phân biệt listen local và connectivity từ xa |
| Packet capture | `tcpdump -i <iface> -nn` | luôn giới hạn filter, count hoặc thời gian khi chạy production |
| Throughput/traffic | `iftop`, `nload`, `iperf3` | dùng khi cần phân biệt bandwidth, latency và packet loss |
| Firewall/NAT | `nft list ruleset`, `iptables -L -n -v`, `firewall-cmd --list-all`, `ufw status` | xác định frontend nào đang quản lý ruleset trước khi sửa |

Legacy tools như `ifconfig`, `route`, `iwconfig`, `iwlist` vẫn gặp trên hệ cũ hoặc tài liệu cũ, nhưng hệ hiện đại nên ưu tiên `ip`, `ss`, `nmcli`, `resolvectl` và tool của network backend hiện tại. Không paste wireless key thật vào shell history bằng `iwconfig ... key s:<password>` trên máy dùng chung; ưu tiên NetworkManager profile, secret storage hoặc automation secret backend.

## 7. Firewall Overview

Linux firewall có nhiều lớp/tool:

| Tool | Ghi chú |
| --- | --- |
| `iptables` | Legacy interface, vẫn gặp nhiều |
| `nftables` | Backend/firewall framework mới |
| `firewalld` | Dynamic firewall manager, phổ biến trên RHEL-family |
| `ufw` | Simple firewall frontend, phổ biến trên Ubuntu |

Ghi nhớ thực tế:

- RHEL/Fedora thường dùng `firewalld`.
- Ubuntu server thường gặp `ufw`, nhưng vẫn có thể dùng raw `nftables`.
- `nftables` là framework hiện đại; `iptables` vẫn xuất hiện trong nhiều hệ legacy hoặc compatibility layer.

### firewalld

```bash
sudo firewall-cmd --state
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --list-all
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload
```

### nftables

```bash
sudo nft list ruleset
```

### iptables

```bash
sudo iptables -S
sudo iptables -L -n -v
```

### ufw

```bash
sudo ufw status verbose
sudo ufw allow 22/tcp
sudo ufw enable
```

## 7.1 Bonding Checklist

Bonding gom nhiều NIC thành interface logic như `bond0` để tăng HA hoặc bandwidth. Mode `active-backup` thường an toàn hơn cho HA đơn giản; mode `802.3ad` cần switch cấu hình LACP tương ứng.

Chọn mode theo mục tiêu:

| Mode | Khi cân nhắc | Lưu ý |
| --- | --- | --- |
| `active-backup` / mode 1 | HA đơn giản, một link active một link standby | Thường ít yêu cầu switch nhất, phù hợp server production phổ thông. |
| `802.3ad` / mode 4 | Aggregate bandwidth theo flow và HA qua LACP | Switch phải cấu hình LACP/port-channel đúng; một flow đơn lẻ thường không dùng tổng bandwidth của mọi link. |
| `balance-rr` / mode 0 | Lab hoặc môi trường kiểm soát rất rõ | Có thể gây reorder packet nếu switch/path không hỗ trợ đúng; thận trọng trong production. |

```bash
cat /proc/net/bonding/bond0
ip -d link show bond0
ethtool <slave-interface>
```

Production notes:

- Không giả định cấu hình Linux là đủ; phía switch phải khớp mode, VLAN/trunk và LACP.
- Khi troubleshoot, đi theo thứ tự: physical link -> bond slave state -> VLAN/subinterface -> IP/route -> firewall/service.
- Thay đổi bond/VLAN trên remote host có thể làm mất SSH; cần console/OOB hoặc rollback window.

## 7.2 Layered Network Troubleshooting Flow

Khi sự cố network không rõ nguyên nhân, đi từ lớp thấp lên lớp cao để tránh nhảy thẳng vào firewall hoặc DNS:

1. **Link**: interface có `LOWER_UP`, speed/duplex đúng và không có error/drop bất thường không?
2. **Address**: IP, prefix, VLAN/subinterface và duplicate address có đúng không?
3. **Gateway/neighbor**: ARP/NDP tới gateway có resolve không?
4. **Route**: `ip route get <target>` chọn đúng source IP, interface và table không?
5. **Name resolution**: `getent hosts` và `dig` có thống nhất không?
6. **Socket/service**: service có listen đúng IP/port không, client có reach được port không?
7. **Policy**: local firewall, security group, ACL, proxy, VPN split route hoặc upstream firewall có chặn không?

```bash
ip -br link
ip -br addr
ip neigh
ip route get <target-ip>
getent hosts <name>
sudo ss -tulpn
nc -vz <host> <port>
```

## 8. Troubleshooting Checklist

### Không ping được gateway

```bash
ip link
ip addr
ip route
ip neigh
ethtool <interface>
```

Nguyên nhân thường gặp:

- Interface down.
- VLAN/network mapping sai.
- IP/subnet sai.
- Gateway sai hoặc ARP không resolve.

### Resolve DNS lỗi

```bash
cat /etc/resolv.conf
resolvectl status
dig example.com
getent hosts example.com
```

Nguyên nhân thường gặp:

- DNS server không reachable.
- Search domain sai.
- Split DNS/VPN.
- `/etc/hosts` override.

### Port không truy cập được

```bash
sudo ss -tulpn | grep <port>
sudo firewall-cmd --list-all 2>/dev/null
sudo nft list ruleset 2>/dev/null
sudo iptables -L -n -v 2>/dev/null
nc -vz <host> <port>
```

Kiểm tra theo thứ tự: app listen, local firewall, route, remote firewall/security group, service log.
