# SỰ CỐ MẤT KẾT NỐI SSH TRÊN VM
1. Thông tin chung
Tên máy ảo (VM): new-pg.admin

Địa chỉ IP Public: 103.172.236.32

Địa chỉ IP Private: 10.106.80.163

Hệ điều hành: CentOS Stream 8

Ngày phát hiện: 03/02/2026

2. Tình trạng sự cố
Khách hàng báo cáo không thể truy cập VM qua giao thức SSH.

Kiểm tra thực tế: Không thể ping đến địa chỉ Public IP mặc dù trạng thái trên Portal vẫn là Running và In use.

3. Quá trình kiểm tra & Phân tích
Bước 1: Kiểm tra lớp hạ tầng (Portal/Security Group)
Security Group: Đã được cấu hình mở toàn bộ (Allow All TCP, UDP, ICMP) từ 0.0.0.0/0.

Network Interface: Trạng thái trên Dashboard hiển thị ACTIVE và đã gắn đúng Floating IP.

Snapshot/Storage: Kiểm tra mối liên hệ với đợt dọn dẹp Snapshot trước đó; tuy nhiên, VM vẫn có thể truy cập được qua Web Console, chứng tỏ ổ đĩa (Volume) không bị lỗi I/O.

Bước 2: Kiểm tra trực tiếp qua Web Console (Guest OS)
Qua Console, ghi nhận interface eth0 không có địa chỉ IPv4 (chỉ có IPv6 link-local).

Lệnh ping 8.8.8.8 báo lỗi Network is unreachable.

Dịch vụ network.service báo trạng thái bad (LSB: Bring up/down networking).

4. Nguyên nhân gốc (Root Cause)
Lỗi nội tại OS: Do cấu hình mạng bên trong Hệ điều hành (Guest OS) không tự động nhận lại IP (DHCP) sau khi khởi động hoặc gặp lỗi xung đột giữa các dịch vụ quản lý mạng (network.service và NetworkManager).

Khẳng định: Lỗi không xuất phát từ hạ tầng OpenStack hay quá trình dọn dẹp Snapshot, vì hệ thống vẫn sẵn sàng cấp IP ngay khi OS thực hiện lệnh xin lại.

5. Các bước đã xử lý (Action Taken)
Truy cập vào VM thông qua Web Console.

Thực hiện ngắt và kích hoạt lại card mạng:
```bash
ifdown eth0

ifup eth0
```
Xác nhận card mạng nhận đúng IP 10.106.80.163 từ DHCP Server của hệ thống.

Kiểm tra kết nối SSH từ bên ngoài: Thành công.