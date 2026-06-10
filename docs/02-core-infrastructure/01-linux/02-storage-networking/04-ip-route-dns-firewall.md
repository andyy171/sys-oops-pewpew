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

Không dùng `/etc/hosts` để che lỗi DNS lâu dài nếu hệ thống cần scale.

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
