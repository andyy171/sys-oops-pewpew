# Hiệu năng Firewall 

## 🛡️ 1. Các chỉ số hiệu năng quan trọng của Firewall
1) Throughput – Băng thông xử lý tối đa
Đây là chỉ số phổ biến nhất. Có 3 loại throughput:
Firewall Throughput (Raw throughput)
→ Tốc độ tối đa khi không bật tính năng bảo mật (IPS/AV/SSL…)
→ Hãng thường công bố rất cao, nhưng thực tế ít khi đạt vì không ai tắt security.
Threat Protection Throughput
→ Tốc độ khi bật IPS/AV/Anti-malware
→ Đây mới là giá trị sát thực tế khi vận hành.
SSL Inspection Throughput
→ Tốc độ khi firewall giải mã SSL/TLS (https inspection)
→ Đây là tác vụ rất nặng → tốc độ giảm mạnh (thường giảm 50–80%).
👉 Khi tính hiệu năng thực tế, người ta thường lấy Threat Protection hoặc SSL Throughput.
## 🧮 2. Cách tính hiệu năng cần thiết cho hệ thống
Công thức 1 – Dựa trên băng thông Internet
Hiệu năng FW cần thiết = (Băng thông thực tế * Hệ số bảo vệ)
Hệ số bảo vệ thường từ 1.5 – 3 lần, vì khi bật tính năng bảo mật hiệu năng giảm.
Ví dụ:
Đường truyền doanh nghiệp: 500 Mbps
Bật IPS + AV + SSL
→ Firewall nên chọn hiệu năng thực tế ≥ 1–1.5 Gbps
Công thức 2 – Dựa trên số concurrent users / sessions
Firewall có giới hạn về:
Concurrent sessions (tổng số phiên)
New session per second (SPS)
Ví dụ:
300 users → trung bình ~1.000–3.000 sessions/user
→ 300.000 – 900.000 sessions
→ Firewall phải support tối thiểu 1 triệu concurrent sessions.
Công thức 3 – Dựa trên gói tin (packets per second – PPS)
Firewall xử lý theo pps, không chỉ Mbps.
PPS ≈ (Mbps * 1000) / (kích thước gói tin trung bình)
Thường dùng gói tin 512 byte hoặc 1500 byte tùy mô hình.
Ví dụ:
1 Gbps, gói tin 512 bytes
→ PPS ≈ 1,000,000 / 0.512 = ~1.95 triệu pps
Firewall phải đáp ứng ≥ 2 triệu pps.
## ⚠️ 3. Những yếu tố làm giảm hiệu năng Firewall
Bật SSL Inspection (giảm 50–80%)
Bật IPS / Anti-malware / App Control
Nhiều policy phức tạp
NAT nhiều lớp
Traffic nhỏ, burst cao
CPU đơn nhân yếu (vấn đề ở FW đời cũ)