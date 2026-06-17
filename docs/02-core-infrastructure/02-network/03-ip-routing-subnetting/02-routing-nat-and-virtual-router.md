# Routing, NAT And Virtual Router

## Overview

Routing quyết định packet đi qua next hop nào. NAT thay đổi địa chỉ/port để private network giao tiếp với public network hoặc publish service nội bộ. Virtual router đưa các chức năng routing, NAT, VPN, firewall và policy vào software để chạy trên hypervisor, cloud hoặc network appliance ảo.

## Route Table Mental Model

Router chọn route theo longest prefix match:

```text
10.10.20.0/24 -> next-hop A
10.10.0.0/16  -> next-hop B
0.0.0.0/0     -> default gateway
```

Nếu destination là `10.10.20.55`, route `/24` thắng `/16` vì cụ thể hơn. Nếu không route nào cụ thể hơn khớp, default route `/0` được dùng.

```bash
ip route
ip route get 10.10.20.55
traceroute 10.10.20.55
```

```text
show ip route
show ip cef <destination>
traceroute <destination>
```

## Packet Life Across Hops

Khi packet đi qua nhiều hop:

- IP packet thường giữ nguyên source/destination IP, trừ khi có NAT hoặc policy đặc biệt.
- Ethernet frame thay đổi ở mỗi hop vì source/destination MAC chỉ có ý nghĩa trên local segment.
- TTL giảm qua mỗi router để tránh loop vô hạn.
- Router decapsulate frame cũ, lookup route, rồi encapsulate packet vào frame mới cho next hop.

## NAT Concepts

| Thuật ngữ | Ý nghĩa |
|---|---|
| inside local | IP private thật của host nội bộ |
| inside global | IP mà bên ngoài nhìn thấy cho host nội bộ |
| outside global | IP thật của host bên ngoài |
| outside local | IP của host bên ngoài theo góc nhìn bên trong, ít gặp hơn |

Các kiểu NAT:

- **Static NAT:** ánh xạ 1:1 cố định, thường dùng khi publish server nội bộ.
- **Dynamic NAT:** ánh xạ từ pool public, không overload port.
- **PAT/NAT overload:** nhiều host dùng chung một hoặc vài IP public bằng cách phân biệt port.

## Static NAT

Static NAT phù hợp khi một service nội bộ cần địa chỉ public ổn định, ví dụ web, mail, VPN endpoint hoặc hệ thống cần allowlist theo public IP.

```text
10.1.1.10 -> 203.0.113.10
10.1.1.20 -> 203.0.113.20
```

Ví dụ Cisco:

```text
interface Ethernet0/0
 ip address 10.1.1.1 255.255.255.0
 ip nat inside

interface Serial0/0
 ip address 203.0.113.1 255.255.255.0
 ip nat outside

ip nat inside source static 10.1.1.10 203.0.113.10
ip nat inside source static 10.1.1.20 203.0.113.20
```

Kiểm tra:

```text
show ip nat translations
show ip nat statistics
```

## PAT / NAT Overload

PAT là kiểu phổ biến cho user/host nội bộ đi Internet:

```text
ip nat inside source list 10 interface GigabitEthernet0/1 overload
access-list 10 permit 10.0.0.0 0.255.255.255
```

Các lỗi NAT thường gặp:

- Chọn sai inside/outside interface.
- ACL NAT không match source thật.
- Route ra Internet có nhưng route chiều về thiếu.
- NAT nhiều lớp làm khó debug.
- Firewall rule chỉ mở port nhưng chưa publish NAT đúng.

## Virtual Router

Virtual router là router chạy bằng software thay vì phần cứng chuyên dụng. Nó có thể chạy trên hypervisor, cloud VM, container hoặc appliance ảo.

Chức năng thường gặp:

- Static/dynamic routing như BGP, OSPF hoặc route table cloud.
- NAT, firewall, VPN, QoS.
- SD-WAN hoặc branch connectivity.
- Automation qua API, Terraform, Ansible hoặc controller.

```text
Branch / user network
        |
        v
VPN / SD-WAN
        |
        v
Virtual router in cloud/VPC
        |
        v
Private workloads
```

Rủi ro vận hành:

- Throughput phụ thuộc CPU, NIC, offload và licensing.
- HA cần thiết kế rõ: active/passive, route failover, health check.
- Nếu virtual router là choke point, lỗi VM/hypervisor có thể ảnh hưởng toàn bộ traffic.

## Troubleshooting Checklist

- `ip route get` hoặc `show ip route` chọn next hop nào?
- Có asymmetric routing làm stateful firewall drop reply không?
- NAT translation có xuất hiện khi test không?
- Firewall policy nằm trước hay sau NAT trong platform đang dùng?
- MTU/tunnel overhead có làm packet bị fragment hoặc blackhole không?
- Virtual router có đủ CPU/session/PPS/throughput cho traffic thực tế không?

## Related Pages

- [IPv4 Addressing And Subnetting](./01-ipv4-addressing-and-subnetting.md)
- [Network Services, NAT And QoS](../06-ccna-advanced-networking-and-security/01-network-services-nat-and-qos.md)
- [Network Troubleshooting Tools](../07-network-operations-lifecycle/03-network-troubleshooting-tools.md)
