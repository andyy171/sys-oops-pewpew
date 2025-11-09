# Overview 

**Switch Layer 2** hoạt động ở tầng liên kết dữ liệu (Data Link Layer - OSI Layer 2) và chuyển tiếp frame dựa trên địa chỉ MAC. Các host (như PC1, PC2) không cần biết sự tồn tại của switch, chỉ cần biết địa chỉ MAC đích của nhau. Switch không thay đổi nội dung frame, không định tuyến, mà chỉ chuyển frame "nguyên xi" từ port này sang port khác.

<img src ="/images/ForwardFrameSwitch.png">

## Cơ chế hoạt động chi tiết

1. Học (Learning)
- Khi PC1 gửi frame, frame mang địa chỉ MAC nguồn (MAC_PC1).
- Switch nhận frame tại port nối với PC1, ghi nhận MAC_PC1 vào bảng địa chỉ MAC, ánh xạ với port tương ứng.
2. Chuyển tiếp (Forwarding)
- Switch đọc địa chỉ MAC đích trong frame (ví dụ: MAC_PC2) và tra trong bảng MAC.
- Nếu đã biết: Chuyển frame đến đúng port chứa MAC_PC2.
- Nếu chưa biết: Flood frame (gửi bản sao đến tất cả các port, trừ port nhận) để tìm host đích và học địa chỉ MAC mới.

3. Lọc (Filtering)
Nếu MAC nguồn và MAC đích nằm trên cùng một port, switch lọc bỏ frame, không chuyển tiếp.

### Switch có “tham gia” không?
- Kỹ thuật: Có, switch là thiết bị trung gian truyền thông tin.
- Logic: Không, switch trong suốt với các host. Nó không can thiệp nội dung frame, không yêu cầu đàm phán, không thay đổi địa chỉ IP/MAC, và không cần cấu hình từ PC1/PC2.
- **Ví dụ thực tế:** Giống như gửi thư nội bộ trong công ty – bạn chỉ cần ghi tên người nhận, nhân viên chuyển thư (switch) sẽ lo phần còn lại mà bạn không cần biết cách họ làm.

## Lệnh quan trọng
-Kiểm tra bảng MAC:
```bash
show mac address-table
```
- Xóa bảng MAC để debug:
```bash
clear mac address-table
```
### Mẹo debug mạng LAN
- Khi mất kết nối trong mạng LAN, đừng vội kiểm tra IP. Hãy:
+ Kiểm tra bảng MAC của switch (show mac address-table).
+ Xác minh hành vi học MAC và chuyển tiếp frame.
+ Đảm bảo không có lỗi port (ví dụ: port bị shutdown hoặc cấu hình sai VLAN).

### Kết luận

Switch Layer 2 là nền tảng của mạng LAN hiện đại, hoạt động dựa trên địa chỉ MAC và học động. Hiểu cơ chế học, chuyển tiếp, và lọc của switch giúp bạn debug và quản lý mạng hiệu quả.