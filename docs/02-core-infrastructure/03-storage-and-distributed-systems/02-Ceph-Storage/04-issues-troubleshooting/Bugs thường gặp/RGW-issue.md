# Các issues liên quan đến RGW
## Lỗi Đồng Bộ Versioned Objects (Multi-site)
- Mô tả : Khi bạn bật tính năng Versioning (lưu nhiều phiên bản của 1 file) và chạy Multi-site (đồng bộ giữa 2 cụm Ceph).
- Nguyên nhân dự đoán : Một số phiên bản cũ của file ở Site A không được đồng bộ sang Site B, hoặc tệ hơn là Site B ghi đè phiên bản mới lên phiên bản cũ của Site A do sai lệch về timestamp.
- Xử lý : bản Reef, Ceph đã cải thiện rgw_sync_log. Nếu gặp lỗi này ở Pacific/Quincy, bạn cần kiểm tra radosgw-admin sync status và đôi khi phải chạy sync error list để tìm các object bị lỗi và "touch" lại chúng để kích hoạt đồng bộ lại.

## Lỗi "LifeCycle Policy" (LC) Stalls
- Mô tả : Tính năng tự động xóa hoặc chuyển vùng dữ liệu (Tiering) sau một số ngày nhất định.
- Nguyên nhân dự đoán : Khi số lượng object lên tới hàng trăm triệu, tiến trình LC (LifeCycle) có thể bị rơi vào vòng lặp vô tận hoặc bỏ sót các bucket lớn. Đặc biệt ở bản Pacific, LC có thể tiêu tốn 100% CPU của Gateway.
- Cách Xử lý: 
    - Tách biệt các Gateway chuyên dụng chỉ để chạy LC (rgw_enable_lc = true chỉ trên 1-2 node).

    - Ở bản Reef/Squid, sử dụng tính năng lc_sharding để chia nhỏ hàng đợi LC, tránh việc một tiến trình duy nhất bị nghẽn.

## Lỗi Tích Hợp SSE-KMS (Mã hóa dữ liệu với Vault)
- Mô tả: RGW hỗ trợ mã hóa dữ liệu đầu cuối bằng khóa từ HashiCorp Vault.
- Nguyên nhân dự đoán : Khi xoay vòng khóa (Key Rotation) trên Vault, RGW đôi khi không cập nhật kịp thời thông tin khóa mới, dẫn đến việc các Object cũ không thể giải mã được (Lỗi 403 hoặc 500).
- Cách xử lý : Đảm bảo cấu hình rgw_crypt_sse_s3_backend = vault và kiểm tra độ trễ mạng giữa RGW và Vault. Trong các bản Squid, việc quản lý token Vault đã được cải thiện để tự động gia hạn (renew) tránh hết hạn giữa chừng.

## Lỗi Hệ Thống "Account" mới
- Mô tả : Ceph Reef giới thiệu hệ thống Account (tương tự AWS Account) để quản lý nhiều User.
- Nguyên nhân dự đoán : Việc phân quyền IAM Policy trở nên cực kỳ phức tạp. Một sai sót nhỏ trong JSON Policy có thể khiến toàn bộ các User trong Account đó mất quyền truy cập (Access Denied) mà không có log rõ ràng.
- Cách xử lý : Sử dụng công cụ radosgw-admin policy để kiểm tra cú pháp trước khi apply. Luôn giữ lại một User có quyền caps cao nhất nằm ngoài hệ thống Account để cứu hộ.

## Lỗi "Multipart Upload" ETag Mismatch
- Mô tả: Khi upload các file lớn (>5GB) được chia nhỏ thành nhiều phần.

- Nguyên nhân dự đoán : Sau khi kết hợp (Complete Multipart), mã ETag trả về không khớp với mã MD5 của file gốc. Điều này gây lỗi cho các ứng dụng kiểm tra tính toàn vẹn khắt khe.

- Cách Xử lý: Lỗi này chủ yếu do cơ chế nén dữ liệu (compression) của RGW. Nếu độ chính xác của ETag là tiên quyết, hãy tắt nén cho các bucket đó: radosgw-admin bucket encryption get và cấu hình nén về none.