
DNSSEC (Domain Name System Security Extensions) là một tập mở rộng bảo mật cho DNS nhằm bảo đảm tính toàn vẹn và xác thực dữ liệu DNS.
<br>

# Mục tiêu chính

- Ngăn chặn giả mạo DNS (DNS Spoofing / Cache Poisoning)

- Xác thực nguồn dữ liệu DNS (đảm bảo bản ghi đến từ tên miền hợp lệ)

- Đảm bảo dữ liệu không bị sửa đổi trong quá trình truyền.

# Cách hoạt động

- Mỗi bản ghi DNS (như A, MX, TXT, v.v.) được ký bằng chữ ký số (RRSIG).

- Chữ ký này được tạo bằng khóa riêng (Private Key) của vùng DNS.

- Client (resolver) kiểm tra chữ ký bằng khóa công khai (DNSKEY).

- Chuỗi tin cậy (Chain of Trust) được tạo từ Root → TLD → Domain.

# Các bản ghi DNSSEC quan trọng
- **DNSKEY :** Chứa khóa công khai dùng để xác thực
- **RRSIG :** Chữ ký số của bản ghi DNS
- **DS (Delegation Signer) :** Liên kết tin cậy giữa parent và child zone
- **NSEC / NSEC3 :** Chứng minh rằng một tên miền không tồn tại (ngăn tấn công NXDOMAIN spoofing)

## Lợi ích và hạn chế 
Lợi ích : 
- Ngăn tấn công DNS spoofing, cache poisoning
- Cung cấp chuỗi xác thực tin cậy từ root đến domain
- Tăng tính bảo mật cho giao thức DNS

Hạn chế :
- Không mã hóa dữ liệu DNS (chỉ xác thực)
- Cấu hình phức tạp, dễ sai
- Không phải mọi resolver đều hỗ trợ

> DNSSEC = DNS + Chữ ký số → đảm bảo dữ liệu DNS xác thực & toàn vẹn, không bị giả mạo.