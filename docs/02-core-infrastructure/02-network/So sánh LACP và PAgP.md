# So sánh LACP và PAgP trong Cấu hình EtherChannel

1. Giới thiệu

EtherChannel (Link Aggregation) là kỹ thuật kết hợp nhiều liên kết vật lý để tăng băng thông, tạo dự phòng và cân bằng tải trong mạng doanh nghiệp. Hai giao thức chính hỗ trợ cấu hình EtherChannel là:  LACP (Link Aggregation Control Protocol): Chuẩn mở do IEEE phát triển. 
PAgP (Port Aggregation Protocol): Giao thức độc quyền của Cisco.

Bài viết này so sánh chi tiết LACP và PAgP, phân tích ưu/nhược điểm và khi nào nên sử dụng từng giao thức.

2. Khái quát về LACP và PAgP

- LACP – Link Aggregation Control Protocol  
+ Tổ chức phát triển: IEEE 
+ Tên tiêu chuẩn: IEEE 802.3ad (nay là IEEE 802.1AX) 
+ Tính tương thích: Chuẩn mở, hỗ trợ bởi nhiều nhà sản xuất (Cisco, HP, Juniper, Dell, v.v.). 
+ Chế độ hoạt động:  Active: Chủ động gửi bản tin LACPDU để thương lượng. 
+ Passive: Chờ nhận LACPDU để phản hồi.

- PAgP – Port Aggregation Protocol  
+ Tổ chức phát triển: Cisco 
+ Tính tương thích: Độc quyền, chỉ hoạt động trên thiết bị Cisco hoặc thiết bị hỗ trợ Cisco-like. 
+ Chế độ hoạt động:  Desirable: Chủ động gửi bản tin PAgP để thương lượng. 
+ Auto: Bị động, chỉ tham gia khi nhận bản tin từ phía đối diện.
![](/docs/02-network/images/lacp-pagp.jpg)
3. So sánh chi tiết LACP vs PAgP  

Dưới đây là bảng so sánh giữa LACP và PAgP được định dạng trong Markdown:

| Tiêu chí                  | LACP                                                                 | PAgP                                                                 |
|---------------------------|----------------------------------------------------------------------|----------------------------------------------------------------------|
| **Tính mở rộng và tương thích** | Chuẩn mở, hỗ trợ đa nền tảng (Cisco, HP, Juniper, v.v.).               | Độc quyền, chỉ dùng trên thiết bị Cisco.                              |
| **Khả năng tự động thương lượng** | Kiểm tra chặt chẽ tốc độ, chế độ, và các tham số cấu hình để đồng bộ. | Tự động thương lượng, nhưng ít kiểm tra tham số hơn LACP.             |
| **Cấu hình**               | Cú pháp phổ biến trong môi trường hỗn hợp thiết bị.                   | Cú pháp đơn giản hơn trong hệ sinh thái Cisco.                        |
| **Số lượng cổng hỗ trợ**   | Tối đa 16 cổng (8 hoạt động, 8 dự phòng - hot standby).               | Tối đa 8 cổng, không hỗ trợ dự phòng.                                |

4. Ưu điểm và nhược điểm

- **LACP** 
+ **Ưu điểm:**  
* Chuẩn mở, tương thích đa nền tảng. 
* Hỗ trợ nhiều cổng hơn, bao gồm cổng dự phòng. 
* Phát hiện lỗi và bảo trì đường truyền tốt hơn. 
+ **Nhược điểm:** 
* Cần cấu hình đúng chế độ (Active/Passive) để liên kết hoạt động. 
* Có thể phức tạp hơn trong hệ thống thuần Cisco so với PAgP.

- **PAgP**  
+ **Ưu điểm:**  
* Dễ triển khai trong hệ sinh thái Cisco. 
* Tự động xác định các tham số tương thích. 
* Tương thích với thiết bị Cisco cũ. 
+ **Nhược điểm:**  
* Không hỗ trợ đa nền tảng, giới hạn ở thiết bị Cisco. 
* Hạn chế số cổng và không có cơ chế dự phòng. 
* Ít được sử dụng trong các hệ thống mạng hiện đại.

5. Khi nào nên dùng LACP hay PAgP?

- Nên dùng LACP khi:  
+ Kết nối thiết bị từ nhiều nhà sản xuất khác nhau. 
+ Hệ thống yêu cầu khả năng mở rộng cao, nhiều cổng, hoặc cổng dự phòng. 
+ Tuân thủ tiêu chuẩn IEEE (phổ biến trong môi trường chuyên nghiệp). 
+ Làm việc trong data center hoặc mạng campus lớn.

- Nên dùng PAgP khi:  
+ Sử dụng toàn bộ thiết bị Cisco. 
+ Triển khai mạng đơn giản, nhỏ gọn. 
+ Làm việc với hệ thống cũ hoặc yêu cầu tương thích với switch legacy của Cisco.

6. Ví dụ cấu hình cơ bản

- Cấu hình LACP
```bash
interface range GigabitEthernet0/1 - 2
 channel-group 1 mode active
interface Port-channel1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
```
- Cấu hình PAgP
```bash
interface range GigabitEthernet0/1 - 2
 channel-group 1 mode desirable
interface Port-channel1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
```
7. Kết luận  
- **LACP:** Lựa chọn tối ưu cho môi trường đa nhà cung cấp, hệ thống lớn, và yêu cầu dự phòng cao. 
- **PAgP:** Phù hợp cho mạng thuần Cisco, đặc biệt là các hệ thống cũ hoặc đơn giản. 
- Khi cấu hình EtherChannel, hãy kiểm tra thiết bị và yêu cầu mạng để chọn giao thức phù hợp, đảm bảo chế độ (Active/Passive hoặc Desirable/Auto) khớp nhau giữa hai đầu liên kết.