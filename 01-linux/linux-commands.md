# Các lệnh chung 

- pwd : Tìm path của thư mục làm việc hiện tại 
- cd : điều hướng qua Linux files hoặc thư mục - ls : liệt kê nội dung thu mục 
- cat : tạo file mới 
- cp : copy file từ thư mục hiện tại đến thư mục đích - mv : di chuyển file 
- mkdir : tạo thư mục mới 
- rmdir : xóa thư mục và mọi nội dung nó chứa - locate : định vị một file 
- giống lệnh Search Windows 
- sudo : thực hiện task cần quyền root/administratives 
- head : xem dòng đầu của mọi văn bản 
- ssh : kết nối từ xa tới một máy sử dụng giao thức SSH 
- grep : Tìm một chuỗi trong 1 file 
- top : Hiển thị tài nguyên hệ thống sử dụng và các tiến trình đang chạy 
- find : Tìm kiếm file hoặc thư mục - wget : Tải file từ web 
- chmod : Thay đổi quyền đối với file/Thư mục 
- tar : Đóng gói files hay thư mục thành 1 file duy nhất 
- chown : Thay đổi quyền sở hữu của file 
- gzip : Nén file

## Network 
- ping : Kiểm tra kết nối mạng giữa 2 thiết bị 
- traceroute / tracepath : Xác định đường đi của gói tin qua các router trung gian. 
- ssh : Kết nối từ xa an toàn đến máy chủ Linux. ssh <tên-người-dùng>@<địa-chỉ-IP-hoặc-tên-miền> 
- wget / curl : Tải file từ Internet qua HTTP/HTTPS/FTP. wget <URL> curl -O <URL> 
- ip : Quản lý cấu hình mạng.
```bash
ip a        # Hiển thị thông tin giao diện mạng (địa chỉ IP, trạng thái)
ip route    # Xem bảng định tuyến
ip link set eth0 up   # Kích hoạt giao diện eth0
```
- netstat / ss : Liệt kê kết nối mạng, cổng đang lắng nghe.
```bash
netstat -tuln    # Liệt kê cổng TCP/UDP đang mở
ss -tuln         # Tương tự như netstat nhưng nhanh hơn
netstat -r       # Hiển thị bảng định tuyến
```
- sftp : Kết nối SFTP