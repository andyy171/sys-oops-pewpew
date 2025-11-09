# Overview 

NAT tĩnh (Static NAT) là kỹ thuật ánh xạ 1-1 giữa địa chỉ IP nội bộ (Inside Local) và địa chỉ IP công cộng (Inside Global). Đây là giải pháp ổn định, dễ kiểm soát, thường được dùng để cho phép các server nội bộ (như Web Server, Mail Server) truy cập từ Internet.

## Kịch bản thực tế

Giả sử một công ty có:
- Web Server: `10.1.1.1`
- Mail Server: `10.1.1.2`
- IP công cộng được cấp:
+ `200.1.1.1` (cho Web Server)
+ `200.1.1.2` (cho Mail Server)

Ánh xạ NAT tĩnh:

`10.1.1.1` → `200.1.1.1`
`10.1.1.2 `→ `200.1.1.2`

## Cấu hình trên router Cisco

1. Định danh cổng bên trong (mạng nội bộ)
```bash
interface Ethernet0/0
 ip address 10.1.1.3 255.255.255.0
 ip nat inside
```
2. Định danh cổng bên ngoài (nối với Internet)
```bash
interface Serial0/0
 ip address 200.1.1.251 255.255.255.0
 ip nat outside
```
3. Khai báo ánh xạ NAT tĩnh
```bash
ip nat inside source static 10.1.1.1 200.1.1.1
ip nat inside source static 10.1.1.2 200.1.1.2
```
## Kiểm tra NAT

Sử dụng lệnh:
```bash
show ip nat translations
```
Kết quả:
```
Pro Inside Global Inside Local Outside Local Outside Global
--- 200.1.1.1     10.1.1.1     ---          ---
--- 200.1.1.2     10.1.1.2     ---          ---
```
### Diễn giải hoạt động NAT tĩnh
- Khi gói tin từ 10.1.1.1 được gửi ra Internet, router thay đổi địa chỉ nguồn thành 200.1.1.1.
- Khi gói tin phản hồi quay lại, router ánh xạ ngược từ 200.1.1.1 về 10.1.1.1.
- Có thể kết hợp NAT tĩnh với firewall để mở cổng dịch vụ (HTTP - 80, SMTP - 25) cho phép truy cập từ Internet.

### Khi nào nên dùng NAT tĩnh?
✅ Public các dịch vụ cố định từ nội bộ ra Internet (Web, Mail, VPN...).
✅ Cấu hình firewall rules chi tiết theo IP công cộng.
✅ Kiểm soát 100% luồng truy cập.

### Ứng dụng thực tế trong doanh nghiệp

NAT tĩnh được sử dụng cho:
+ Mail Server: SMTP, IMAP
+ Web Server: HTTP/HTTPS
+ Remote Access: VPN, SSH

> Giúp hệ thống dễ nhận diện, bảo trì, và giảm thiểu lỗi do thay đổi IP.