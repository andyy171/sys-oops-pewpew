# Layer 2, VLAN, STP, RSTP And EtherChannel

## Overview

Layer 2 trong CCNA xoay quanh câu hỏi: làm sao chia LAN thành nhiều broadcast domain, nối switch với nhau mà không loop, và tăng băng thông/redundancy giữa switch mà vẫn giữ topology ổn định.

## VLAN

VLAN chia một switch vật lý thành nhiều broadcast domain logic. Host trong VLAN khác nhau không nói chuyện trực tiếp ở Layer 2; muốn giao tiếp cần Layer 3 routing.

```text
VLAN 10 -> users
VLAN 20 -> servers
VLAN 30 -> management
```

Access port thuộc một VLAN duy nhất:

```text
vlan 10
 name USERS
interface GigabitEthernet0/10
 switchport mode access
 switchport access vlan 10
```

Trunk port mang nhiều VLAN giữa switch/router/firewall/hypervisor. IEEE 802.1Q thêm tag VLAN vào Ethernet frame, trừ native VLAN nếu cấu hình theo kiểu mặc định Cisco.

```text
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
```

## Inter-VLAN Routing

Vì VLAN là các subnet riêng, cần routing để đi qua nhau:

- Router-on-a-stick: router dùng subinterface với 802.1Q tag.
- Multilayer switch: switch Layer 3 tạo SVI cho từng VLAN.

```text
interface vlan 10
 ip address 10.10.10.1 255.255.255.0
 no shutdown
```

## DTP And VTP

DTP tự thương lượng trunk trên một số switch Cisco. Trong môi trường production, nên cấu hình mode rõ ràng và tắt negotiation khi không cần để giảm hành vi bất ngờ.

VTP đồng bộ VLAN database giữa switch. Nó tiện trong lab hoặc môi trường được kiểm soát, nhưng có rủi ro lớn nếu switch sai revision/domain làm thay đổi VLAN ngoài ý muốn. Với nhiều hệ thống hiện đại, cấu hình VLAN rõ ràng qua automation thường dễ kiểm soát hơn.

## STP

Ethernet không có TTL như IP. Nếu Layer 2 loop xảy ra, broadcast/unknown unicast có thể quay vòng và làm sập LAN. STP tạo topology không loop bằng cách block một số port dự phòng.

STP bầu chọn:

1. Root bridge có Bridge ID thấp nhất.
2. Mỗi non-root switch chọn root port tốt nhất về root.
3. Mỗi segment chọn designated port.
4. Port còn lại có thể bị block để phá loop.

Bridge ID gồm priority và MAC address. Vì vậy nên cấu hình root bridge chủ động, không để switch ngẫu nhiên thắng do MAC thấp.

```text
spanning-tree vlan 10 root primary
spanning-tree vlan 20 root secondary
```

## PortFast And BPDU Guard

PortFast cho access port đi nhanh vào forwarding, phù hợp cho endpoint. Không dùng PortFast trên trunk/uplink giữa switch nếu không hiểu rõ rủi ro.

BPDU Guard tắt port nếu nhận BPDU trên port đáng lẽ là endpoint. Đây là lớp bảo vệ quan trọng khi người dùng cắm nhầm switch nhỏ vào port access.

```text
interface GigabitEthernet0/10
 spanning-tree portfast
 spanning-tree bpduguard enable
```

## RSTP

RSTP cải thiện thời gian hội tụ so với STP cổ điển. Cần hiểu các thay đổi chính:

- port role rõ hơn: root, designated, alternate, backup;
- port state gọn hơn: discarding, learning, forwarding;
- edge port tương tự PortFast;
- link type point-to-point giúp hội tụ nhanh hơn.

Các guard cần biết:

- Root Guard ngăn port trở thành đường tới root bridge không mong muốn.
- Loop Guard giảm rủi ro loop khi BPDU bị mất một chiều.
- BPDU Filter chặn gửi/nhận BPDU, cần cực kỳ cẩn thận vì có thể che mất tín hiệu STP.

## EtherChannel

EtherChannel gộp nhiều physical link thành một logical link. Lợi ích:

- tăng tổng băng thông giữa switch;
- redundancy nếu một member link hỏng;
- STP nhìn cả bundle như một link logic, tránh block từng link riêng lẻ.

Các mode:

- LACP: chuẩn mở, thường nên ưu tiên.
- PAgP: Cisco proprietary.
- Static `on`: không negotiation, dễ sai nếu hai đầu lệch cấu hình.

```text
interface range GigabitEthernet0/1 - 2
 channel-group 1 mode active
interface Port-channel1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
```

Điều kiện member link nên đồng nhất: speed, duplex, trunk/access mode, native VLAN, allowed VLAN và Layer 2/Layer 3 mode.

## Troubleshooting Checklist

- VLAN có tồn tại trên switch không?
- Access port có đúng VLAN không?
- Trunk có allow VLAN cần đi qua không?
- Native VLAN hai đầu trunk có mismatch không?
- Root bridge có đúng switch mong muốn không?
- Port bị STP blocking hay err-disabled do BPDU Guard?
- EtherChannel member có bị suspended vì lệch cấu hình không?
- Load balancing EtherChannel có thể làm một flow chỉ dùng một member; đừng kỳ vọng một TCP flow tự chia đều qua mọi link.
