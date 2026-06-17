# Security Concepts, Port Security, DHCP Snooping And DAI

## Overview

Security trong CCNA Volume 2 bắt đầu từ mental model CIA, sau đó đi vào các control rất thực tế ở access layer: AAA/802.1X, firewall/IPS, Port Security, DHCP Snooping và Dynamic ARP Inspection.

## CIA Triad And Threat Model

Ba mục tiêu nền tảng:

- Confidentiality: chỉ người được phép mới đọc được dữ liệu.
- Integrity: dữ liệu và hệ thống không bị sửa sai hoặc giả mạo.
- Availability: dịch vụ sẵn sàng cho người dùng hợp lệ.

Một threat nên được phân tích theo cả ba hướng. Ví dụ DHCP exhaustion chủ yếu đánh availability, còn ARP poisoning đánh confidentiality và integrity vì attacker có thể đứng giữa luồng traffic.

## Authentication, Authorization And Accounting

AAA tách ba câu hỏi:

- Authentication: bạn là ai?
- Authorization: bạn được làm gì?
- Accounting: bạn đã làm gì?

RADIUS thường dùng UDP và phổ biến trong 802.1X/wireless. TACACS+ thường dùng TCP và hay gặp trong quản trị thiết bị Cisco vì tách authentication với authorization tốt hơn.

## 802.1X

802.1X kiểm soát access port trước khi cho client vào mạng. Các vai trò:

- Supplicant: client xin truy cập.
- Authenticator: switch/AP kiểm soát port.
- Authentication server: thường là RADIUS server.

![802.1X original page](./images/ccna-vol2-page-0177.jpg)

Trước khi xác thực, port chỉ cho traffic 802.1X/EAPOL cần thiết. Sau khi xác thực thành công, switch/AP mở quyền theo policy, có thể gán VLAN hoặc ACL động.

## Firewall And IPS

ACL trên router là stateless filtering cơ bản. Stateful firewall hiểu trạng thái session, vì vậy có thể cho phép return traffic hợp lệ mà không cần mở chiều ngược một cách rộng rãi.

NGFW thường thêm khả năng nhận diện application, user, URL/category, malware và tích hợp threat intelligence. IPS phát hiện và có thể chặn traffic có dấu hiệu exploit.

## Port Security

Port Security giới hạn MAC address được phép học trên access port. Nó giúp giảm rủi ro MAC flooding và cắm thiết bị trái phép.

![Port Security original page](./images/ccna-vol2-page-0185.jpg)

Các chế độ violation:

- protect: drop frame vi phạm, không log/counter rõ ràng.
- restrict: drop frame, tăng counter và có thể log/SNMP.
- shutdown: err-disable port, mặc định phổ biến và dễ nhận biết.

```text
interface FastEthernet0/1
 switchport mode access
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
```

Port Security hợp cho access port. Không bật bừa trên trunk/uplink vì số MAC hợp lệ phía sau uplink có thể rất lớn.

## DHCP Snooping

DHCP Snooping phân biệt trusted port và untrusted port:

- Trusted port: nơi DHCP server hợp lệ hoặc uplink tới server.
- Untrusted port: port người dùng, không được phép gửi DHCP Offer/Ack giả.

Nó cũng tạo DHCP Snooping binding table, map MAC/IP/VLAN/interface/lease. Binding table này là nền cho Dynamic ARP Inspection và IP Source Guard.

```text
ip dhcp snooping
ip dhcp snooping vlan 10,20
interface GigabitEthernet0/1
 ip dhcp snooping trust
interface range FastEthernet0/1 - 24
 ip dhcp snooping limit rate 15
```

## Dynamic ARP Inspection

DAI chặn ARP spoofing/poisoning bằng cách kiểm tra ARP packet với DHCP Snooping binding table.

Luồng suy nghĩ:

1. DHCP Snooping biết MAC nào được cấp IP nào trên port nào.
2. DAI nhìn ARP packet trên untrusted port.
3. Nếu ARP claim không khớp binding, switch drop.
4. Trusted port thường là uplink hoặc port về router/server đáng tin.

```text
ip arp inspection vlan 10,20
interface GigabitEthernet0/1
 ip arp inspection trust
```

DAI cần cẩn thận với host dùng static IP. Nếu không có binding DHCP, cần static ARP ACL hoặc cơ chế tương đương, nếu không host hợp lệ có thể bị drop.

## Troubleshooting Checklist

- AAA fail do credential, RADIUS reachability, shared secret hay policy?
- 802.1X port đang unauthorized, authorized hay guest/auth-fail VLAN?
- Port Security đang secure-up hay err-disabled?
- Sticky MAC có học nhầm MAC cũ không?
- DHCP Snooping trust port đã đặt đúng uplink/server chưa?
- DHCP Snooping binding table có entry cho client không?
- DAI drop do thiếu binding, ARP ACL sai hay trust boundary sai?
- Có đang bật rate limit quá thấp làm drop traffic hợp lệ không?
