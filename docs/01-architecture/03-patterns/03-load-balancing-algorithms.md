# Load Balancing Algorithms

Load balancing phân phối request hoặc connection qua nhiều backend để tăng availability, throughput và fault isolation.

## Round Robin

Gửi request lần lượt đến từng backend.

Ưu điểm:

- Đơn giản.
- Phù hợp khi backend tương đồng.

Nhược điểm:

- Không tính đến request cost.
- Backend chậm vẫn nhận tải nếu health check chưa loại bỏ.

## Weighted Round Robin

Backend có weight cao nhận nhiều request hơn. Phù hợp khi backend khác cấu hình CPU/RAM hoặc muốn canary một phần traffic.

## Least Connections

Gửi request đến backend có ít connection active nhất. Phù hợp với request giữ connection lâu hoặc xử lý không đều.

## Least Response Time

Ưu tiên backend có response time thấp hơn. Hiệu quả hơn round robin nhưng cần metric chính xác, tránh dao động khi đo sai.

## Consistent Hashing

Map key/request vào backend ổn định hơn khi thêm/bớt node. Phù hợp cho cache, session routing hoặc workload cần locality.

## Health Check

Load balancing không chỉ là thuật toán. Health check quyết định backend nào được nhận traffic.

Health check tốt nên phân biệt:

- Process còn sống.
- Service sẵn sàng nhận request.
- Dependency quan trọng còn hoạt động.
- Backend có quá tải không.

## Design Checklist

- Request có state/session không.
- Backend có cấu hình đồng đều không.
- Cần L4 hay L7 balancing.
- Failover cần nhanh đến mức nào.
- Có cần canary/weighted traffic không.
- Health check có làm backend quá tải khi sự cố không.

