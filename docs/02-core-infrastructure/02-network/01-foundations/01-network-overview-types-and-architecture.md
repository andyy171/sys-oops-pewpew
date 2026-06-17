# Network Overview, Types And Architecture

## Overview

Network là tập hợp các thiết bị được kết nối để trao đổi dữ liệu và chia sẻ tài nguyên. Khi học networking, nên tách hai lớp ý tưởng:

- **Physical connection**: dây cáp, wireless, port vật lý, NIC, switch, router, access point.
- **Logical connection**: IP address, MAC address, protocol, port, route, policy và cách dữ liệu đi qua nhiều thiết bị.

Một network hoạt động được khi các thiết bị thống nhất protocol, biết xác định nguồn/đích và có cơ chế phát hiện hoặc xử lý dữ liệu lỗi.

## Vì Sao Network Quan Trọng

Network giúp:

- Kết nối người dùng, server, storage, cloud service và application.
- Chia sẻ tài nguyên như file, printer, database, API và Internet access.
- Tạo nền cho HA, backup, replication, monitoring và remote operation.
- Cho phép áp dụng security policy như segmentation, firewall, VPN và zero trust.

Trong vận hành hạ tầng, hầu hết sự cố application đều cần kiểm tra ít nhất một phần network: DNS, route, firewall, port, TLS, latency hoặc packet loss.

## Network Architecture

### Peer-To-Peer

Trong mô hình peer-to-peer, các máy ngang hàng nhau, không có server trung tâm bắt buộc.

Đặc điểm:

- Dễ dựng cho lab, home network hoặc nhóm nhỏ.
- Mỗi node có thể vừa cung cấp vừa tiêu thụ tài nguyên.
- Khó quản trị tập trung khi số lượng máy tăng.
- Security, backup và access control dễ bị phân tán.

### Client-Server

Trong mô hình client-server, server cung cấp dịch vụ, client gửi request để sử dụng dịch vụ đó.

Đặc điểm:

- Dễ quản trị tập trung user, permission, policy và logging.
- Phù hợp doanh nghiệp, datacenter và cloud.
- Cần thiết kế HA/backup cho server vì server trở thành điểm phụ thuộc quan trọng.

Ví dụ:

```text
Client -> DNS server
Client -> Web server
Client -> Database server
Client -> File server
```

## Network Types By Scope

| Loại | Phạm vi | Ví dụ |
| --- | --- | --- |
| PAN | Rất nhỏ, quanh một người dùng | điện thoại, đồng hồ, tai nghe Bluetooth |
| LAN | Phòng, nhà, văn phòng nhỏ | office network, lab nội bộ |
| WLAN | LAN dùng wireless | Wi-Fi văn phòng |
| CAN | Nhiều LAN trong campus | trường đại học, khu văn phòng |
| MAN | Cấp thành phố/khu vực lớn | metro provider network |
| WAN | Nhiều địa điểm địa lý xa nhau | Internet, MPLS, site-to-site VPN |

Khi thiết kế, đừng chỉ hỏi "network loại gì", hãy hỏi thêm: ai quản lý, latency cần bao nhiêu, traffic đi đâu, failure domain ở đâu và security boundary nằm ở lớp nào.

## Bandwidth, Latency Và Edge

Bandwidth và latency là hai tín hiệu khác nhau:

- **Bandwidth** là dung lượng truyền dữ liệu trong một đơn vị thời gian, ví dụ `100 Mbps` hoặc `10 Gbps`.
- **Latency** là thời gian để dữ liệu đi từ nguồn tới đích và quay lại/được xử lý, thường đo bằng millisecond.
- **Packet loss** và **jitter** có thể làm ứng dụng chậm hoặc timeout dù bandwidth nhìn có vẻ đủ.

Trong thiết kế cloud, tăng bandwidth không tự động giải quyết latency. Workload đặt database ở một region xa người dùng sẽ vẫn chậm vì round-trip time cao, dù đường truyền có dung lượng lớn. Với application nhạy latency, ưu tiên đặt compute/data gần user, dùng CDN/edge cache, tối ưu DNS/routing và đo percentile latency thay vì chỉ nhìn throughput trung bình.

Edge datacenter hoặc CDN node giúp đưa cached content và một phần xử lý ra gần người dùng. Đổi lại, hệ thống phải kiểm soát cache invalidation, consistency, observability, security policy và fallback khi edge path lỗi.

## Topology

Topology mô tả cách thiết bị được nối với nhau.

| Topology | Ý nghĩa | Ghi chú vận hành |
| --- | --- | --- |
| Bus | nhiều thiết bị chung một đường truyền | đơn giản nhưng dễ có collision/failure lan rộng |
| Ring | thiết bị nối thành vòng | có thể dự đoán path nhưng cần cơ chế bảo vệ vòng |
| Star | thiết bị nối về switch trung tâm | phổ biến trong LAN hiện đại |
| Mesh | nhiều đường nối chéo | tăng redundancy nhưng phức tạp |
| Hub-and-spoke | spoke đi qua hub trung tâm | phổ biến trong WAN/VPN/cloud transit |

Trong thực tế, topology vật lý và topology logic có thể khác nhau. Ví dụ server cắm vật lý vào switch, nhưng logic lại nằm trong VLAN, VXLAN hoặc overlay network.

## Thiết Bị Network Cơ Bản

| Thiết bị | Vai trò |
| --- | --- |
| NIC | card mạng của host, có MAC address |
| Hub | lặp tín hiệu ra nhiều port, gần như không dùng trong network hiện đại |
| Switch | forward frame theo MAC, hoạt động chủ yếu ở Layer 2 |
| Router | forward packet giữa các subnet/network, hoạt động ở Layer 3 |
| Wireless AP | bridge client Wi-Fi vào wired network |
| Firewall | enforce security policy theo IP, port, protocol, state hoặc application |
| Modem/ONT | chuyển đổi tín hiệu từ ISP sang Ethernet/IP |
| Media converter | chuyển đổi giữa các loại media như copper và fiber |

## Mental Model Khi Troubleshoot

Khi gặp lỗi kết nối, đi từ câu hỏi đơn giản đến phức tạp:

1. Link vật lý hoặc wireless có up không?
2. Host có IP/MAC đúng không?
3. Host có cùng subnet hay cần gateway?
4. DNS resolve ra IP nào?
5. Route đi qua path nào?
6. Firewall/security group có chặn không?
7. Port/service có listen không?
8. Application có trả response hợp lệ không?

## Related Pages

- [OSI, TCP/IP And Encapsulation](./02-osi-tcpip-and-encapsulation.md)
- [Ethernet, Media, Topologies And Layer 2](../02-ethernet-switching/01-ethernet-media-topologies-and-layer2.md)
- [IPv4 Addressing And Subnetting](../03-ip-routing-subnetting/01-ipv4-addressing-and-subnetting.md)
