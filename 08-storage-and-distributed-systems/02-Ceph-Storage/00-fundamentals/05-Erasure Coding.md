# 


Erasure Coding – Công nghệ Bảo vệ Dữ liệu Tiên tiến Trong Ceph

**Erasure Coding (EC)** là một kỹ thuật bảo vệ dữ liệu giúp tiết kiệm không gian lưu trữ đáng kể so với phương pháp nhân bản (Replication) truyền thống, trong khi vẫn cung cấp khả năng chịu lỗi cao. Nó là xương sống cho các hệ thống lưu trữ phân tán, mạnh mẽ và có khả năng mở rộng đến quy mô exabyte.

**Ví dụ đơn giản:** Thay vì lưu 3 bản sao của một file (tốn 3TB để lưu 1TB dữ liệu), EC "chia nhỏ" dữ liệu và tính toán thêm các phần dự phòng, giúp bạn chỉ cần dung lượng ít hơn (ví dụ: 1.5TB cho 1TB dữ liệu) mà vẫn chịu được lỗi của ổ cứng.

#### Nguyên lý Hoạt động
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/ec-1.png)

Erasure Coding hoạt động dựa trên hai khái niệm chính:

- `k` (Data Chunks): Dữ liệu được chia thành `k` phần bằng nhau.

- `m` (Coding Chunks): Hệ thống tính toán và tạo ra `m` phần dữ liệu mã hóa (parity) từ `k` phần trên.

Cách thức:

1. Khi bạn ghi một object vào Ceph, EC sẽ chia nó thành `k` khối dữ liệu.
2. Từ `k` khối này, nó tính toán ra `m` khối mã hóa.
3. Tất cả `k + m` khối này được phân tán lưu trữ trên các ổ đĩa (OSD) khác nhau trong cluster.

- Khi xảy ra sự cố: Nếu có tối đa `m` ổ đĩa bị lỗi, hệ thống có thể sử dụng bất kỳ k khối nào còn lại (bao gồm cả data chunks và coding chunks) để tính toán và khôi phục lại toàn bộ dữ liệu gốc.

+ Ví dụ: Với cấu hình `k=4, m=2`:
* Dữ liệu được chia thành 4 phần.
* Tạo ra 2 phần parity.
* Tổng cộng 6 phần được lưu trên các OSD khác nhau.
* Hệ thống vẫn hoạt động bình thường ngay cả khi 2 OSD bất kỳ cùng lúc bị lỗi.

#### Tại sao Erasure Coding lại quan trọng?
1. Tiết kiệm chi phí & Không gian
- **Hiệu suất lưu trữ cao:** So với replication (lưu 3 bản sao, overhead 200%), EC có overhead thấp hơn nhiều. Ví dụ, profile k=4, m=2 chỉ có overhead 50% (dùng 1.5GB để lưu 1GB dữ liệu).

- **Giảm TCO (Tổng chi phí sở hữu):** Bạn cần ít ổ cứng hơn để đạt được cùng một mức độ bảo vệ dữ liệu.

2. Khả năng chịu lỗi vượt trội & Mở rộng quy mô
- **Chịu lỗi linh hoạt:** Bạn có thể cấu hình để chịu được lỗi của nhiều hơn 2 ổ đĩa (ví dụ: m=3 chịu được lỗi 3 OSD), điều mà RAID truyền thống khó làm được.

- **Mở rộng đến Exabyte:** Kiến trúc phân tán giúp EC mở rộng dễ dàng, phù hợp với nhu cầu dữ liệu lớn.

3. Kiến trúc "Software-Defined"
- **Không phụ thuộc phần cứng:** EC được thực thi bằng phần mềm trong Ceph, không cần đến các card RAID đắt tiền. Nó có thể chạy trên bất kỳ phần cứng tiêu chuẩn nào.

- **Thông minh với CRUSH:** Thay vì dùng một bảng metadata tập trung để tìm dữ liệu (có thể gây nghẽn cổ chai), EC sử dụng thuật toán CRUSH để tính toán vị trí của các khối dữ liệu. Điều này giúp tăng hiệu năng và độ trễ thấp trong các hệ thống quy mô lớn. CRUSH hiểu rõ cơ sở hạ tầng (ổ đĩa, node, rack, trung tâm dữ liệu) để đảm bảo các khối được phân tán một cách an toàn.

#### So sánh với Replication và RAID

| Đặc điểm | Replication | RAID | Erasure Coding |
|---------|-------------|------|----------------|
| **Chi phí lưu trữ** | Cao (3x dung lượng) | Trung bình | Thấp (1.5x dung lượng) |
| **Khả năng chịu lỗi** | Phụ thuộc số bản sao | RAID 5: 1 lỗi, RAID 6: 2 lỗi | Linh hoạt, cấu hình được |
| **Hiệu năng khôi phục** | Nhanh | Chậm | Nhanh hơn RAID |
| **Kiến trúc** | Phần mềm, đơn giản | Phụ thuộc phần cứng | Phần mềm, phân tán |
| **Khả năng mở rộng** | Hạn chế | Rất hạn chế | Rất tốt |
| **Tính phù hợp** | Dữ liệu nóng, performance cao | Server đơn lẻ | Dữ liệu lớn, cold storage |

#### Cấu hình & Sử dụng trong Ceph

Tạo một Erasure Coded Pool
```bash
# Tạo một pool EC với profile mặc định (k=2, m=1)
ceph osd pool create my_ec_pool erasure

# Tạo pool với profile tùy chỉnh (ví dụ: k=4, m=2)
ceph osd erasure-code-profile set myprofile k=4 m=2 crush-failure-domain=host
ceph osd pool create my_custom_ec_pool erasure myprofile
```

**Lưu ý quan trọng:**
- Không sửa profile sau khi tạo pool: Hãy lên kế hoạch kỹ lưỡng trước khi tạo pool, vì bạn không thể thay đổi profile k và m sau đó.
- Cân nhắc hiệu suất: Ghi dữ liệu vào pool EC thường chậm hơn so với pool replicated vì cần nhiều thao tác tính toán và ghi.
- Một số tính năng mới (Ceph Octopus trở lên):
+ Cho phép ghi một phần (partial writes) để tối ưu hiệu suất.
+ Quá trình recovery được tối ưu, chỉ cần K shards để khôi phục.
+ Lưu ý: Tính năng Cache Tiering cho EC đã bị deprecated kể từ phiên bản Ceph Reef.

> Erasure Coding không chỉ là một sự thay thế cho Replication hay RAID, mà nó là một bước tiến công nghệ, định hình tương lai của lưu trữ phân tán. Với ưu điểm vượt trội về tiết kiệm chi phí, khả năng mở rộng và chịu lỗi linh hoạt, EC là lựa chọn hàng đầu cho các hệ thống lưu trữ đám mây và big data, nơi mà khối lượng dữ liệu tăng lên chóng mặt hàng năm.
>
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/ceph-rep-ec.png)
