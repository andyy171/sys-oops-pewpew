# Giao thức LACP 

1. Giới thiệu

Trong hạ tầng mạng hiện đại, nhu cầu tăng băng thông, cân bằng tải và dự phòng khi một liên kết bị lỗi là rất quan trọng, đặc biệt trong môi trường doanh nghiệp hoặc trung tâm dữ liệu. Để đáp ứng yêu cầu đó, kỹ thuật EtherChannel (hay Link Aggregation) được sử dụng. Trong đó, LACP (Link Aggregation Control Protocol) là giao thức tiêu chuẩn do IEEE phát triển (IEEE 802.3ad, nay là IEEE 802.1AX), giúp tự động thương lượng và duy trì kết nối trong EtherChannel.
<img src ="/images/lacp.jpg">
2. LACP là gì?

LACP là giao thức giúp các thiết bị mạng (switch, server) tự động nhóm nhiều liên kết vật lý thành một kênh logic duy nhất, tổng hợp băng thông và cung cấp dự phòng.

Ví dụ: Với 2 cổng 1Gbps, cấu hình LACP sẽ tạo kênh logic 2Gbps. Nếu một cổng lỗi, cổng còn lại vẫn duy trì kết nối.

3. Cách hoạt động của LACP

LACP sử dụng LACPDU (LACP Protocol Data Units) để trao đổi giữa hai thiết bị. Quá trình thương lượng kiểm tra các tiêu chí tương thích:
+ Tốc độ cổng (speed)
+ Chế độ duplex (full/half)
+ VLAN cấu hình
+ MTU (Maximum Transmission Unit)
+ Trunking mode

Chỉ khi tất cả tham số khớp, các cổng mới được gộp vào nhóm.

4. Chế độ hoạt động trong LACP
+ Active: Chủ động gửi LACPDU để khởi tạo thương lượng.
+ Passive: Bị động, chỉ phản hồi LACPDU từ phía kia.

Lưu ý: Ít nhất một bên phải là active. Nếu cả hai đều passive, kênh sẽ không hình thành.

5. Vì sao nên sử dụng LACP?
+ Tăng băng thông: Cộng gộp nhiều liên kết vật lý thành logic.
+ Cân bằng tải: Phân phối dữ liệu đều, tránh tắc nghẽn.
+ Dự phòng tự động: Phục hồi khi liên kết lỗi.
+ Tương thích cao: Chuẩn mở IEEE, hỗ trợ đa nhà sản xuất (Cisco, HP, Juniper...).

6. Hướng dẫn cấu hình LACP trên thiết bị Cisco

- Mô hình ví dụ

Hai switch Cisco kết nối qua cổng `GigabitEthernet0/1` và `GigabitEthernet0/2`. 
Mục tiêu: Gộp thành EtherChannel sử dụng LACP ở chế độ trunk.

- Cấu hình trên Switch1 (Chế độ Active)
```bash
Switch1(config)# interface range GigabitEthernet0/1 - 2
Switch1(config-if-range)# channel-group 1 mode active
Switch1(config-if-range)# exit
Switch1(config)# interface Port-channel 1
Switch1(config-if)# switchport mode trunk
Switch1(config-if)# switchport trunk allowed vlan 10,20  # Ví dụ: Cho phép VLAN 10,20
Switch1(config-if)# exit
```
- Cấu hình trên Switch2 (Chế độ Passive)
```bash
Switch2(config)# interface range GigabitEthernet0/1 - 2
Switch2(config-if-range)# channel-group 1 mode passive
Switch2(config-if-range)# exit
Switch2(config)# interface Port-channel 1
Switch2(config-if)# switchport mode trunk
Switch2(config-if)# switchport trunk allowed vlan 10,20  # Phải khớp với Switch1
Switch2(config-if)# exit
```
- Lưu cấu hình
```bash
Switch1# copy running-config startup-config
Switch2# copy running-config startup-config
```
7. Kiểm tra trạng thái LACP và EtherChannel

- Sử dụng các lệnh sau để xác minh:

1. Lệnh cơ bản
+ `show etherchannel summary`: Hiển thị tổng quan nhóm EtherChannel và trạng thái cổng (P: bundled, I: individual).
```
Example Output:
Number of channel-groups in use: 1
Group  Port-channel  Protocol    Ports
------+-------------+-----------+-----------------------------------------------
1      Po1(SU)       LACP        Gi0/1(P)   Gi0/2(P)
```

+ `show etherchannel 1 detail`: Chi tiết nhóm EtherChannel số 1 (thông tin LACP, timers...).

2. Lệnh nâng cao
`show lacp neighbor`: Kiểm tra thiết bị lân cận tham gia LACP.
```
Example Output:
LACPDU Port  Partner's information
Port    System-ID    Age  Port  Role  State
Gi0/1   0000.0c00.0001  0s   Gi0/1  Actor  Up
```

`show interfaces port-channel 1`: Trạng thái kênh logic (traffic, errors...).

- Mẹo debug:
+ Nếu kênh không hình thành: Kiểm tra chế độ (ít nhất một bên active), tốc độ/duplex khớp, và không có ACL chặn LACPDU.
+ Sử dụng debug lacp all (cẩn thận trong production) để theo dõi trao đổi LACPDU.

8. Troubleshooting phổ biến
- Lỗi: Cổng không bundle (trạng thái "I"):
+ Kiểm tra tốc độ/duplex: show interfaces status.
+ Đảm bảo VLAN trunk khớp hai bên.
- Lỗi: Không thương lượng:
+ Xác nhận ít nhất một bên active: show etherchannel protocol.
- Lỗi cân bằng tải: Kiểm tra thuật toán (default: src-mac): port-channel load-balance src-mac.

9. Kết luận

> LACP là công cụ mạnh mẽ cho EtherChannel, mang lại băng thông cao, dự phòng và tương thích đa nền tảng. Với hướng dẫn trên, người mới có thể cấu hình nhanh chóng trên Cisco. Thực hành trong Packet Tracer hoặc GNS3 để nắm vững. Để học sâu hơn, tham khảo tài liệu Cisco CCNA về Network Access.
