## DoH (DNS over HTTPS)

**Khái niệm:**  
DoH là giao thức gửi truy vấn DNS thông qua **HTTPS (port 443)** thay vì UDP/TCP port 53.  
Mục tiêu: **Bảo mật và riêng tư** cho các truy vấn DNS.

---

### 🔹 Cách hoạt động
- Trình duyệt / hệ thống gửi truy vấn DNS → qua **HTTPS** đến máy chủ DoH.
- Dữ liệu DNS được **mã hóa TLS**, không thể bị chặn hay đọc trộm.
- Máy chủ DoH giải mã, truy vấn DNS bình thường, sau đó trả kết quả qua HTTPS.

---

### 🔹 Ưu điểm
- 🛡️ **Bảo mật:** tránh nghe lén và giả mạo DNS.
- 🔒 **Riêng tư:** ISP không thấy website bạn truy cập.
- 🌍 **Hoạt động qua firewall dễ dàng** (vì dùng port 443).

---

### 🔹 Nhược điểm
- ⚙️ Tăng độ trễ (vì có lớp HTTPS).
- ❌ Có thể **làm giảm khả năng giám sát DNS nội bộ** của doanh nghiệp.
- 📉 Không tự động tích hợp với mọi ứng dụng (nhiều app vẫn dùng DNS cũ).

---

### 🔹 So sánh nhanh
| Tiêu chí | DNS thường | DoT (DNS over TLS) | DoH (DNS over HTTPS) |
|-----------|-------------|--------------------|----------------------|
| Cổng | 53 | 853 | 443 |
| Mã hóa | ❌ Không | ✅ TLS | ✅ HTTPS |
| Che giấu lưu lượng | ❌ | 🔸 Một phần | ✅ Hoàn toàn |
| Dễ vượt tường lửa | ❌ | ❌ | ✅ |

---

> **DoH = DNS + HTTPS** → bảo mật, riêng tư hơn, nhưng phức tạp và có thể ảnh hưởng đến quản trị mạng.
