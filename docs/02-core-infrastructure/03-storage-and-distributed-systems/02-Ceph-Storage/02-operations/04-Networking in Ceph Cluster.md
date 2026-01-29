### Networking (Public vs Cluster, MTU, Bonding)
- **Public Network**: Mạng cho client truy cập (read/write).
- **Cluster Network**: Mạng nội bộ cho OSD-MON (heartbeats, replication).
    
    **Cơ chế vận hành**: Tách biệt để tăng bảo mật và hiệu suất; khuyến nghị 10Gbps+.
    
- **MTU (Maximum Transmission Unit)**: Kích thước gói tin tối đa (thường 9000 cho Jumbo frames).
    
    **Cơ chế vận hành**: Tăng MTU giảm overhead CPU, cần cấu hình toàn cluster.
    
- **Bonding**: Gộp nhiều NIC thành một logical interface (modes: active-backup, LACP).
    
    **Cơ chế vận hành**: Tăng băng thông và redundancy.
    
    **Ví dụ**: Public như đường khách, cluster như đường nội bộ; bonding như nhiều làn xe.

