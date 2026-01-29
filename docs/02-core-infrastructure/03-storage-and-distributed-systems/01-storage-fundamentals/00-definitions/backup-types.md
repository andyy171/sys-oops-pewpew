# Các kiểu backup 

## Full Backup (Sao lưu Toàn bộ)
- **Cơ chế:** Sao chép toàn bộ dữ liệu đã chọn trong mỗi lần thực hiện.
- **Ưu điểm:** Khôi phục nhanh chóng và đơn giản nhất vì chỉ cần duy nhất một bản sao lưu.

- **Nhược điểm:** Tốn nhiều thời gian, dung lượng lưu trữ và băng thông nhất.

## Incremental Backup (Sao lưu Gia tăng)

- **Cơ chế:** Chỉ sao chép những dữ liệu đã thay đổi kể từ lần sao lưu gần nhất (bất kể là Full hay Incremental).

- **Ưu điểm:** Tốc độ sao lưu nhanh, tiết kiệm dung lượng lưu trữ tối đa.

- **Nhược điểm:** Quá trình khôi phục phức tạp, cần bản Full Backup ban đầu và tất cả các bản Incremental sau đó theo đúng thứ tự.

## Differential Backup (Sao lưu Khác biệt):

- **Cơ chế:** Sao chép tất cả dữ liệu đã thay đổi kể từ lần Full Backup cuối cùng.

- **Ưu điểm:** Khôi phục nhanh hơn Incremental (chỉ cần bản Full và bản Differential mới nhất), cân bằng giữa Full và Incremental.

- **Nhược điểm:** Dung lượng các bản sao lưu Differential sẽ ngày càng lớn cho đến khi có một bản Full Backup mới được tạo.