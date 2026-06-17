# Network Troubleshooting Tools

## Overview

Network troubleshooting cần bằng chứng theo layer, không chỉ đoán từ error message. Bộ công cụ cơ bản gồm `ip`, `ping`, `traceroute`, `dig`, `ss`, `tcpdump`, `nc`, `nmap`, `ethtool` và log từ firewall/proxy/load balancer.

## Layered Flow

Đi theo thứ tự:

```text
interface -> VLAN/L2 -> IP -> route -> DNS -> port -> TLS -> HTTP/application
```

Lệnh kiểm tra nhanh:

```bash
ip addr show
ip link show
ip route
ping -c 4 10.0.0.1
traceroute 10.0.0.1
dig example.com
ss -lntp
nc -vz example.com 443
curl -Iv https://example.com
```

## Interface And Link Tools

```bash
ip link show
ip addr show
ethtool <interface>
ethtool -S <interface>
```

Kiểm tra:

- Interface up/down.
- Speed/duplex.
- MTU.
- RX/TX error, drop, CRC.
- IP/prefix đúng không.
- Default route có tồn tại không.

## Reachability Tools

```bash
ping -c 4 <ip>
ping -c 4 fe80::1%<interface>
traceroute <ip-or-host>
tracepath <ip-or-host>
```

Diễn giải nhanh:

- `network unreachable`: local route/interface/gateway.
- Ping gateway fail: L2/VLAN/IP local hoặc firewall local.
- Ping IP được nhưng hostname fail: DNS.
- Traceroute dừng ở một hop: firewall, route, ACL hoặc thiết bị không trả ICMP.
- IPv6 link-local cần zone/interface như `%eth0`; thiếu interface có thể làm test sai dù địa chỉ đúng.
- `tracepath` thường dùng UDP và không cần quyền root, hữu ích khi `traceroute` ICMP bị chặn hoặc cần xem MTU/path MTU.

## DNS Tools

```bash
dig example.com
dig @10.0.0.53 example.com
dig +trace example.com
nslookup example.com
host example.com
getent hosts example.com
resolvectl status
```

Tách lỗi DNS:

- Resolver local cấu hình sai.
- Recursive resolver không reachable.
- Authoritative zone sai record.
- TTL/cache giữ record cũ.
- Search domain làm query lệch tên.
- DoH/browser resolver bypass DNS nội bộ.
- `/etc/hosts` hoặc NSS làm application resolve khác với `dig`; dùng `getent hosts` để kiểm gần hơn với cách libc/app resolve.

## Socket And Port Tools

`ss` thay thế tốt cho `netstat` trên Linux hiện đại:

```bash
ss -tulpn
ss -tan state established
ss -lntp
ss -s
```

Điểm hay gặp: service chỉ listen trên `127.0.0.1`, vì vậy local curl được nhưng host khác không connect được.

`netstat` vẫn hữu ích trên hệ legacy nhưng thường đến từ package `net-tools`. Khi có cả hai, ưu tiên `ss` cho socket/process state hiện tại.

Kiểm tra TCP connect:

```bash
nc -vz <host> <port>
```

Netcat có thể dựng listener tạm để test path, nhưng không để listener mở lâu trên production host:

```bash
nc -l 2000
nc <host> 2000
```

Chỉ dùng trên port test đã được phép, dừng ngay sau khi xác nhận, và không truyền secret qua phiên netcat plaintext.

Kiểm tra HTTP/TLS:

```bash
curl -v http://example.com
curl -vk https://example.com
openssl s_client -connect example.com:443 -servername example.com
```

## Packet Capture With tcpdump

```bash
sudo tcpdump -D
sudo tcpdump -i any -nn
sudo tcpdump -i eth0 -nn host 10.0.0.10
sudo tcpdump -i eth0 -nn port 443
sudo tcpdump -i eth0 -c 100 -w capture.pcap
sudo tcpdump -r capture.pcap -nn -vv
```

Filter hữu dụng:

```bash
sudo tcpdump -i any -nn 'host 10.0.0.10 and host 10.0.0.20'
sudo tcpdump -i any -nn 'udp port 53 or tcp port 53'
sudo tcpdump -i any -nn icmp
sudo tcpdump -i any -nn 'tcp[tcpflags] & tcp-syn != 0'
sudo tcpdump -i any -nn 'not port 22'
```

Đọc nhanh TCP:

- Chỉ thấy SYN đi ra, không thấy SYN/ACK: route, firewall, security group hoặc service đích.
- Thấy SYN/SYN-ACK/ACK đủ nhưng app lỗi: TLS, HTTP, proxy hoặc application.
- Không thấy packet: DNS/route/client path trước đó.

Không chia sẻ file `.pcap` thô nếu có thể chứa dữ liệu nhạy cảm.

## nmap

Dùng `nmap` có phạm vi rõ ràng:

```bash
nmap -Pn 10.0.0.10
nmap -Pn -p 22,80,443 10.0.0.10
nmap -sV -p 443 10.0.0.10
```

Không scan rộng/aggressive vào production khi chưa có approval.

## Reproduce And Validate

Tái hiện lỗi từ nhiều vị trí:

- node chạy app;
- node cùng subnet/VPC;
- bastion/jumphost;
- client/user path;
- bên ngoài Internet nếu service public.

Sau khi sửa, xác nhận bằng đúng cách đã reproduce:

```bash
dig <hostname>
nc -vz <host> <port>
curl -Iv https://example.com
```

Đừng chỉ dựa vào việc alert im lặng; cần thấy request thật đi qua đúng path và log/metric phục hồi.

## Related Pages

- [OSI, TCP/IP And Encapsulation](../01-foundations/02-osi-tcpip-and-encapsulation.md)
- [Routing, NAT And Virtual Router](../03-ip-routing-subnetting/02-routing-nat-and-virtual-router.md)
- [Proxy, Load Balancer, VPN And Expose Endpoints](../04-protocols-and-services/03-proxy-load-balancer-vpn-and-expose-endpoints.md)
