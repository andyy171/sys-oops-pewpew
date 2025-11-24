# Switch Layer 3 (Multilayer Switch – MLS)

## 1. Khái Niệm Cơ Bản
**Multilayer Switching (MLS)** là kỹ thuật cho phép một thiết bị **switch** hoạt động đồng thời ở **Layer 2 (chuyển mạch)** và **Layer 3 (định tuyến)**.  
Điều này giúp:
- **Chuyển mạch khung Ethernet** như một switch L2 truyền thống.
- **Định tuyến gói IP** giữa các VLAN/subnet như một router.

💡 **Điểm khác biệt**: MLS không phải là router giả lập trên switch. Nó sử dụng **ASIC phần cứng tốc độ cao** + cơ chế xử lý định tuyến (như **Cisco Express Forwarding – CEF**) để chuyển tiếp gói tin gần như tức thời.

---

## 2. Tại Sao Cần Switch Layer 3?
- **Tốc độ cao hơn router-on-a-stick**: định tuyến nội bộ VLAN xảy ra ngay trong switch, không phải gửi gói lên router ngoài.
- **Giảm độ trễ**: forwarding dựa trên bảng CEF phần cứng, nhanh hơn xử lý phần mềm.
- **Đơn giản hoá thiết kế mạng**: một thiết bị vừa switching vừa routing.
- **Linh hoạt trong mạng campus & data center**: thường dùng ở lớp **Access** hoặc **Distribution** để định tuyến inter-VLAN.

---

## 3. Thành Phần Cốt Lõi Khi Cấu Hình MLS

### 3.1 SVI (Switched Virtual Interface)
- Là **interface logic** trên switch đại diện cho một VLAN.
- Mỗi VLAN có thể có một địa chỉ IP trên SVI đóng vai trò **default gateway** cho các host trong VLAN đó.
- Là **trái tim** của định tuyến nội bộ VLAN.

### 3.2 CEF (Cisco Express Forwarding)
- Cơ chế chuyển tiếp gói ở tốc độ phần cứng.
- Sử dụng **Forwarding Information Base (FIB)** và **Adjacency Table** để tra cứu nhanh địa chỉ đích → MAC → cổng ra.
- Đảm bảo định tuyến nội bộ hầu như không nhận thấy độ trễ.

### 3.3 Bảng CAM (Content Addressable Memory)
- Vẫn hoạt động như switch L2: lưu địa chỉ MAC → cổng vật lý.
- Sau khi gói được định tuyến, CAM xác định chính xác cổng vật lý gửi đi.

---

## 4. Cơ Chế Hoạt Động Ví Dụ
**Mô hình:**
- VLAN10: SVI 10.1.1.1/24 (PC A 10.1.1.2, PC B 10.1.1.3)
- VLAN20: SVI 10.2.2.1/24 (PC C 10.2.2.2)

**Quy trình khi PC A (VLAN10) → PC C (VLAN20):**
1. PC A gửi gói đến **default gateway** 10.1.1.1.
2. Switch L3 tra **bảng định tuyến/FIB**: đích 10.2.2.2 qua SVI 10.2.2.1.
3. Switch tra **ARP/Adjacency Table** lấy MAC đích tương ứng SVI 10.2.2.1.
4. Tra **bảng CAM** để xác định cổng ra.
5. Gói được chuyển tiếp ngay trong switch → tốc độ cao.

---

## 5. Cấu Hình Thực Tế Trên Cisco Switch Layer 3
```bash
interface vlan 10
 ip address 10.1.1.1 255.255.255.0
 no shutdown

interface vlan 20
 ip address 10.2.2.1 255.255.255.0
 no shutdown

interface GigabitEthernet1/0/1
 switchport mode access
 switchport access vlan 10

interface GigabitEthernet1/0/2
 switchport mode access
 switchport access vlan 10

interface GigabitEthernet1/0/3
 switchport mode access
 switchport access vlan 20
```

Kích hoạt IP routing trên switch (nếu yêu cầu):
```bash
ip routing
```

Bây giờ switch có thể định tuyến giữa VLAN10 và VLAN20 mà không cần router ngoài.

## 6. Lưu Ý Quan Trọng Khi Lab

- Phải có SVI và IP routing để switch định tuyến giữa các VLAN.

- CEF phải bật (mặc định trên Catalyst) để có tốc độ cao.

- CAM vẫn dùng cho switching L2 sau khi định tuyến.

- Không nhầm với router-on-a-stick: router-on-a-stick dùng trunk từ switch sang router, còn MLS xử lý ngay bên trong switch.