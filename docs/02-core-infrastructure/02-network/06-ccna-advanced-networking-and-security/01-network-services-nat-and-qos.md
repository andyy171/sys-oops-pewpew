# Network Services, NAT And QoS

## Overview

Network services là lớp làm cho network vận hành được trong thực tế: thiết bị biết hàng xóm là ai, đồng bộ thời gian, resolve tên miền, cấp IP động, quản trị từ xa, gửi log, backup file cấu hình, dịch địa chỉ IPv4 và ưu tiên traffic quan trọng khi nghẽn.

## CDP And LLDP

CDP và LLDP là Layer 2 discovery protocol. Chúng không thay thế documentation, nhưng rất hữu ích khi tài liệu mạng không cập nhật.

- CDP là Cisco proprietary, thường bật sẵn trên thiết bị Cisco.
- LLDP là open standard, dùng tốt trong môi trường multi-vendor.
- Cả hai gửi thông tin như hostname, local/remote interface, platform, capabilities và management address.
- Vì chúng tiết lộ topology, nên tắt trên port không tin cậy hoặc boundary với bên ngoài.

```text
show cdp neighbors
show cdp neighbors detail
show lldp neighbors
show lldp neighbors detail
```

## NTP

NTP làm cho thời gian trên thiết bị nhất quán. Nếu time lệch, log correlation, certificate validation, AAA, Kerberos, SIEM và incident timeline đều dễ sai.

Mental model:

- stratum 0 là reference clock;
- stratum 1 sync trực tiếp với stratum 0;
- thiết bị càng xa nguồn chuẩn thì stratum càng cao;
- stratum 16 nghĩa là nguồn thời gian không đáng tin.

![NTP hierarchy original page](./images/ccna-vol2-page-0039.jpg)

```text
ntp server 10.0.0.10 prefer
ntp source Loopback0
show ntp associations
show ntp status
```

Trong production, nên dùng NTP server nội bộ đáng tin, source từ loopback nếu thiết bị có nhiều uplink, và cấu hình timezone/DST thống nhất để log dễ đọc.

## DNS

DNS chuyển tên thành địa chỉ. Với network engineer, DNS không chỉ là `A record`. Cần hiểu:

- URL gồm scheme, authority, path và các phần bổ sung như query/fragment.
- DNS hierarchy đi từ root, TLD, domain, subdomain.
- Recursive resolver đi hỏi thay client; authoritative server giữ câu trả lời chính thức cho zone.
- Record phổ biến: `A`, `AAAA`, `CNAME`, `MX`, `NS`, `PTR`, `TXT`.
- TTL ảnh hưởng thời gian cache và propagation.

Cisco IOS có thể làm DNS client hoặc DNS server cơ bản, nhưng trong môi trường lớn nên dùng DNS service chuyên dụng.

## DHCP

DHCP tự động cấp IP, mask, gateway, DNS và các option khác cho client. DORA là flow nền tảng:

1. Discover.
2. Offer.
3. Request.
4. Acknowledge.

![DHCP DORA original page](./images/ccna-vol2-page-0063.jpg)

DHCP relay cần thiết khi client và DHCP server nằm khác subnet. Trên router/L3 interface gần client:

```text
interface vlan 10
 ip helper-address 10.0.0.20
```

Lỗi hay gặp:

- đặt `ip helper-address` sai interface;
- DHCP pool thiếu default gateway hoặc DNS;
- excluded address không đủ;
- relay bị ACL/firewall chặn UDP 67/68;
- DHCP Snooping chưa trust port uplink về DHCP server.

## SSH, SNMP And Syslog

SSH là baseline cho remote management. Telnet gửi plaintext nên không nên dùng.

```text
ip domain-name example.com
crypto key generate rsa
username admin privilege 15 secret <PASSWORD>
line vty 0 15
 login local
 transport input ssh
```

SNMP dùng cho monitoring. SNMPv1/v2c dựa vào community string, yếu hơn SNMPv3. Nếu có thể, dùng SNMPv3 với authentication và privacy.

Syslog gửi event từ thiết bị về collector. Cần nhớ severity từ emergency đến debugging, và luôn đồng bộ NTP để timestamp có giá trị.

## TFTP And FTP

TFTP đơn giản, dùng UDP, không authentication mạnh, thường gặp trong lab hoặc copy image/config nội bộ. FTP có authentication nhưng vẫn không nên xem là secure nếu không có lớp bảo vệ phù hợp. Với production, ưu tiên SCP/SFTP/HTTPS nếu thiết bị hỗ trợ.

## NAT

NAT giải quyết bài toán IPv4 private address cần đi ra mạng public hoặc cần publish service nội bộ.

Các khái niệm Cisco cần tách rõ:

- inside local: địa chỉ private của host nội bộ.
- inside global: địa chỉ mà bên ngoài nhìn thấy cho host nội bộ.
- outside global: địa chỉ thật của host bên ngoài.
- outside local: địa chỉ của host bên ngoài theo góc nhìn bên trong, ít gặp hơn.

![NAT original page](./images/ccna-vol2-page-0127.jpg)

Các dạng chính:

- Static NAT: ánh xạ 1:1 cố định.
- Dynamic NAT: ánh xạ từ pool public, không dùng port để overload.
- PAT/NAT overload: nhiều inside local dùng chung một hoặc vài inside global bằng cách phân biệt port.

```text
ip nat inside source list 10 interface GigabitEthernet0/1 overload
access-list 10 permit 10.0.0.0 0.255.255.255
interface GigabitEthernet0/0
 ip nat inside
interface GigabitEthernet0/1
 ip nat outside
```

## QoS

QoS không tạo thêm bandwidth. QoS quyết định traffic nào được ưu tiên khi có congestion.

Các khái niệm:

- bandwidth: dung lượng đường truyền;
- delay: độ trễ;
- jitter: biến thiên độ trễ;
- loss: mất gói;
- classification: phân loại traffic;
- marking: đánh dấu traffic bằng DSCP/CoS/PCP;
- queuing/scheduling: xếp hàng và chọn gói nào đi trước;
- policing: vượt ngưỡng thì drop/remark;
- shaping: buffer để làm mượt tốc độ.

![QoS policing and shaping original page](./images/ccna-vol2-page-0159.jpg)

Voice/video cần delay và jitter thấp. Trust boundary nên đặt ở nơi bạn tin marking: thường tin IP phone, không tin PC người dùng nếu chưa có policy.

## Troubleshooting Checklist

- CDP/LLDP có đang bật trên interface cần discovery không?
- Thiết bị có sync NTP không, stratum có hợp lý không?
- DNS lỗi do resolver, authoritative, cache hay record?
- DHCP lỗi ở DORA bước nào?
- SSH lỗi do key/domain name/user/VTY/ACL?
- SNMP collector có đúng version, credential và ACL không?
- Syslog có timestamp đúng timezone/NTP không?
- NAT có đúng inside/outside interface và ACL match source không?
- QoS có congestion thật không, hay chỉ là nhầm lẫn về bandwidth?
