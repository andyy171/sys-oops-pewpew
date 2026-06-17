# Network Fundamentals, Devices, Media, Models And IOS

## Overview

Phần đầu của CCNA xây nền cho toàn bộ phần sau: network là tập hợp thiết bị trao đổi dữ liệu theo protocol; mỗi thiết bị có vai trò khác nhau; dữ liệu đi qua nhiều lớp đóng gói; và khi vào thiết bị Cisco, CLI là giao diện chính để xem, cấu hình và kiểm tra trạng thái.

## Network Devices

Các thiết bị cần phân biệt bằng chức năng, không chỉ bằng tên:

- Client tạo request, ví dụ laptop, điện thoại, máy người dùng.
- Server cung cấp dịch vụ, ví dụ web, DNS, DHCP, file server.
- Switch nối các thiết bị trong LAN và forward frame dựa trên MAC address.
- Router nối các network khác subnet và forward packet dựa trên IP route.
- Firewall kiểm soát traffic theo policy, thường xét IP, port, state và application.
- Wireless AP nối client không dây vào wired network.

Một lỗi học networking rất phổ biến là nghĩ switch "chỉ nối dây" còn router "chỉ ra internet". Đúng hơn: switch chủ yếu xử lý Layer 2 broadcast domain, router xử lý Layer 3 boundary giữa subnet.

## Cables, Connectors And Ports

Media vật lý quyết định tốc độ, khoảng cách, khả năng chống nhiễu và loại transceiver/port.

- UTP copper phổ biến trong LAN, dùng RJ-45, có giới hạn khoảng cách điển hình 100m cho Ethernet copper.
- Fiber dùng ánh sáng, hợp khoảng cách xa hơn, uplink/datacenter, chống nhiễu điện tốt hơn.
- Straight-through/crossover từng quan trọng khi nối thiết bị cùng/khác loại; hiện nay auto-MDI/MDIX làm việc này ít cần nhớ thủ công hơn.
- Interface speed/duplex mismatch vẫn là nguyên nhân kinh điển gây throughput thấp, CRC, collision hoặc late collision trên môi trường legacy.

## OSI And TCP/IP Model

OSI là mô hình học và troubleshooting; TCP/IP là mô hình gần với triển khai thực tế hơn. Khi debug, điều quan trọng là biết dấu hiệu lỗi nằm ở layer nào.

| Layer | Câu hỏi cần hỏi | Ví dụ |
|---|---|---|
| Physical | Link có lên không? | cable, optic, speed, duplex |
| Data Link | Frame có đi đúng VLAN/MAC không? | Ethernet, switch, ARP, STP |
| Network | IP có route tới đích không? | IPv4/IPv6, routing table, ICMP |
| Transport | Port có mở và session có ổn không? | TCP, UDP, ACL theo port |
| Application | Service có phản hồi đúng không? | DNS, HTTP, SSH, app log |

Encapsulation là quá trình mỗi layer thêm header/trailer của mình. Khi host gửi dữ liệu qua Ethernet LAN, dữ liệu thường đi theo chuỗi:

```text
Application data
-> TCP/UDP segment
-> IP packet
-> Ethernet frame
-> bits on wire
```

## Ethernet Switching Basics

Switch học MAC address từ source MAC của frame đi vào port. Sau đó nó dùng MAC address table để quyết định:

- known unicast: forward ra port đã học;
- unknown unicast: flood trong VLAN;
- broadcast: flood trong VLAN;
- multicast: flood hoặc xử lý theo cơ chế multicast snooping nếu có.

ARP nối IPv4 address với MAC address trong cùng LAN. Nếu host muốn gửi packet đến IP cùng subnet, nó ARP trực tiếp IP đích. Nếu IP khác subnet, nó ARP MAC của default gateway.

## Cisco IOS CLI

IOS CLI có nhiều mode. Cần phân biệt để không nhập lệnh sai ngữ cảnh:

```text
Router>                 user EXEC
Router#                 privileged EXEC
Router(config)#         global configuration
Router(config-if)#      interface configuration
Router(config-line)#    line configuration
```

Các lệnh nền tảng:

```text
show running-config
show startup-config
show interfaces
show ip interface brief
show version
copy running-config startup-config
```

## Interface Configuration

Một interface production nên có mô tả, trạng thái rõ ràng và kiểm tra speed/duplex khi có sự cố.

```text
interface GigabitEthernet0/1
 description uplink-to-sw01
 ip address 10.0.0.1 255.255.255.0
 no shutdown
```

Với switchport access:

```text
interface GigabitEthernet0/10
 description user-port
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
```

## Troubleshooting Checklist

- Link LED/interface status có up/up không?
- Speed/duplex có bị mismatch không?
- MAC address có được học đúng port/VLAN không?
- ARP có resolve được next hop không?
- Default gateway của host có đúng subnet không?
- IOS config đang nằm trong running-config hay đã save vào startup-config?
