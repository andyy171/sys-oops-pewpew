# VLAN, LACP And Layer 2 Operations

## Overview

Layer 2 operations xoay quanh ba câu hỏi: host đang ở broadcast domain nào, switch forward frame theo MAC ra sao, và uplink có đủ dự phòng/băng thông không. VLAN, trunk, access port, switch L2/L3 và LACP/EtherChannel là các khối chính để trả lời các câu hỏi đó.

Trang này hấp thụ các note lẻ về VLAN, switch L2, switch L3, LACP và so sánh LACP/PAgP vào một nơi vận hành thống nhất.

## VLAN Mental Model

VLAN chia một hạ tầng switch vật lý thành nhiều Layer 2 network logic. Mỗi VLAN là một broadcast domain riêng.

| VLAN | Mục đích |
|---|---|
| VLAN 10 | User hoặc office endpoint |
| VLAN 20 | Voice/IP phone |
| VLAN 30 | Management |
| VLAN 40 | Server, storage hoặc backend |

VLAN giúp giảm broadcast không cần thiết và cô lập logic, nhưng VLAN không thay thế firewall policy. Traffic giữa VLAN vẫn cần Layer 3 gateway và policy rõ ràng.

## Access Port, Trunk Port And Native VLAN

| Loại port | Dùng cho | Điểm cần nhớ |
|---|---|---|
| Access port | PC, printer, camera, server đơn VLAN | Frame đi ra thường untagged và port thuộc một VLAN |
| Trunk port | switch-switch, switch-router, switch-hypervisor | Mang nhiều VLAN bằng 802.1Q tag |
| Native VLAN | VLAN untagged trên trunk | Cần đồng bộ hai đầu để tránh mismatch |

Các lỗi hay gặp:

- Access port đặt sai VLAN.
- Trunk chưa allow VLAN cần thiết.
- Native VLAN mismatch.
- VLAN tồn tại trên switch này nhưng chưa được tạo/allow trên switch khác.
- Port security hoặc STP làm port không forward.

## Switch Layer 2

Switch L2 forward Ethernet frame dựa trên MAC table:

1. Nhận frame trên ingress port.
2. Học `source MAC -> ingress port`.
3. Nếu biết destination MAC, forward ra đúng port.
4. Nếu chưa biết destination MAC, flood trong cùng VLAN.
5. Nếu source và destination nằm cùng port, switch filter frame.

Lệnh kiểm tra trên Cisco:

```text
show mac address-table
show interfaces status
show interfaces trunk
show vlan brief
clear mac address-table dynamic
```

Trên Linux bridge:

```bash
bridge fdb show
bridge link
ip link show
```

## Switch Layer 3 And Inter-VLAN Routing

Switch Layer 3 vừa switch frame ở Layer 2 vừa route packet ở Layer 3. Trong campus hoặc datacenter nhỏ, switch L3 thường làm inter-VLAN gateway bằng SVI.

```text
VLAN 10 hosts -> SVI vlan10
VLAN 20 hosts -> SVI vlan20
SVI/router/firewall routes between VLANs
```

Ví dụ Cisco:

```text
interface vlan 10
 ip address 10.1.10.1 255.255.255.0
 no shutdown

interface vlan 20
 ip address 10.1.20.1 255.255.255.0
 no shutdown

ip routing
```

Điểm cần nhớ:

- SVI cần `up/up`; nếu VLAN không có port active hoặc trunk không mang VLAN đó, SVI có thể down.
- Switch L3 route nhanh nhờ phần cứng/ASIC, nhưng policy east-west vẫn cần ACL hoặc firewall nếu traffic nhạy cảm.
- Không nhầm MLS với router-on-a-stick: router-on-a-stick dùng router ngoài qua trunk, còn MLS xử lý routing ngay trên switch.

## LACP And EtherChannel

LACP gom nhiều link vật lý thành một port-channel logic để tăng tính sẵn sàng và phân phối traffic theo hash. Nó không biến một flow TCP đơn thành tốc độ bằng tổng mọi link; một flow thường vẫn đi qua một member link theo thuật toán hashing.

Điều kiện member link cần khớp:

- Speed và duplex.
- Trunk/access mode.
- Allowed VLAN/native VLAN.
- MTU.
- Channel-group và protocol mode.

LACP mode:

| Mode | Ý nghĩa |
|---|---|
| active | Chủ động gửi LACPDU |
| passive | Chỉ phản hồi LACPDU |

Ít nhất một đầu phải là `active`. Nếu cả hai đầu đều `passive`, port-channel không hình thành.

Ví dụ Cisco:

```text
interface range GigabitEthernet0/1 - 2
 channel-group 1 mode active

interface Port-channel1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
```

Kiểm tra:

```text
show etherchannel summary
show etherchannel 1 detail
show lacp neighbor
show interfaces port-channel 1
```

## LACP Vs PAgP

| Tiêu chí | LACP | PAgP |
|---|---|---|
| Chuẩn | IEEE 802.1AX/802.3ad | Cisco proprietary |
| Môi trường phù hợp | Multi-vendor, production hiện đại | Cisco-only hoặc legacy |
| Mode | active/passive | desirable/auto |
| Khuyến nghị | Ưu tiên mặc định | Chỉ dùng khi có lý do Cisco-specific |

Trong hạ tầng mới, ưu tiên LACP vì tương thích rộng và dễ vận hành hơn trong môi trường nhiều vendor.

## Troubleshooting Checklist

- Port-channel có member ở trạng thái bundled (`P`) hay bị individual/suspended?
- Speed/duplex/MTU/trunk mode hai đầu có khớp không?
- Allowed VLAN trên port-channel và member interface có đồng nhất không?
- Có đang cấu hình trên physical member thay vì port-channel không?
- Hashing có làm một link nóng hơn link khác do traffic cùng flow không?
- Có MAC flapping do loop hoặc do dual-homing sai thiết kế không?

## Best Practices

- Cấu hình VLAN/trunk trên port-channel interface, không cấu hình lệch giữa từng member.
- Giới hạn VLAN được phép đi qua trunk.
- Dùng naming convention rõ cho VLAN, port-channel và mô tả interface.
- Bật STP/RSTP hoặc dùng thiết kế leaf-spine/MLAG/stacking rõ ràng để tránh loop.
- Theo dõi CRC, discard, link flap và MAC move, vì link up không đồng nghĩa path khỏe.

## Related Pages

- [Ethernet, Media, Topologies And Layer 2](./01-ethernet-media-topologies-and-layer2.md)
- [IPv4 Addressing And Subnetting](../03-ip-routing-subnetting/01-ipv4-addressing-and-subnetting.md)
- [Network Troubleshooting Tools](../07-network-operations-lifecycle/03-network-troubleshooting-tools.md)
