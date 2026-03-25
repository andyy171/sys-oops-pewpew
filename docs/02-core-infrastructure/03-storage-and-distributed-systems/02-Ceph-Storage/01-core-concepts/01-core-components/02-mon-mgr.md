# MON và MGR
## MON 
- Theo dõi trạng thái cluster, duy trì cluster map (bản đồ vị trí dữ liệu).
- Nhóm MON (3-5 node) dùng Paxos để đồng bộ

## Paxos consensus algorithm 
- **Paxos**: Thuật toán đồng thuận để MON/MGR/MDS thống nhất trạng thái (như OSD up/down).
    
    **Cơ chế vận hành**: Leader đề xuất, node vote; chịu lỗi nếu <50% hỏng.
    
    **Ví dụ**: Như bỏ phiếu bầu chủ tịch, cần đa số đồng ý.
    
# Monitor quorum 
- **Quorum**: Số node tối thiểu để đưa ra quyết định hợp lệ (thường >50%).
    
    **Cơ chế vận hành**: Ngăn split-brain (cluster chia đôi).
    
    **Ví dụ**: Như tòa án cần đa số thẩm phán để phán quyết.

# Monitor synchronization


# Election process



## MGR


MGR (Manager)
- Cung cấp dashboard, telemetry và tích hợp với hệ thống bên ngoài (như Kubernetes).
- Chạy song song MON, xử lý thống kê và báo cáo.


# MGR modules system


# Built-in modules (balancer, dashboard, prometheus, etc.)


# Active/standby MGR



# RESTful API endpoint

