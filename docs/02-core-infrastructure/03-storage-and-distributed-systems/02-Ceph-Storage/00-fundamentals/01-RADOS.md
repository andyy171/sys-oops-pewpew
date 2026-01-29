# RADOS 
## Tổng quan 
- RADOS (Reliable Autonomic Distributed Object Store) là lớp lưu trữ cốt lõi và nền tảng của toàn bộ hệ thống Ceph Storage. RADOS cung cấp dịch vụ lưu trữ đối tượng phân tán, đáng tin cậy với khả năng tự quản trị và tự phục hồi. Tất cả các phương thức truy cập Ceph như RBD (RADOS Block Device), CephFS (File System), RADOSGW (Object Gateway) và librados đều được xây dựng trên RADOS layer.

- RADOS là trung tâm của Ceph storage cluster, còn được gọi là Ceph Storage Cluster. Đây là một dịch vụ lưu trữ phân tán, hoạt động dựa trên các storage nodes thông minh có khả năng tự quản lý và tự phục hồi. RADOS không giao tiếp trực tiếp với client mà hoạt động như backend storage layer, nằm bên dưới các client interfaces.

- Kiến trúc Ceph được chia làm 2 phần chính :
    + RADOS Layer (Tầng dưới): Nằm trong Ceph cluster, quản lý việc lưu trữ, phân tán và bảo vệ dữ liệu
    + Client Interface Layer (Tầng trên): Cung cấp các giao diện truy cập như RBD, CephFS, RADOSGW để client tương tác với cluster

![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/rados-1.png)

- Các đặc điểm chính của RADOS :
    + **Reliable (Đáng tin cậy):** RADOS đảm bảo độ tin cậy cao thông qua :
        * **Data Replication:** Tự động sao chép dữ liệu theo replication factor được cấu hình
        * **Erasure Coding:** Hỗ trợ mã hóa xóa để tối ưu không gian lưu trữ
        * **Data Durability:** Đảm bảo dữ liệu không bị mất ngay cả khi có lỗi phần cứng
        * **High Availability:** Duy trì khả năng truy cập dữ liệu ngay cả khi một số nodes bị lỗi
    + **Autonomic (Tự quản trị):** RADOS có khả năng tự động quản lý và vận hành:
        * **Self-managing:** Tự động quản lý việc phân bố dữ liệu, cân bằng tải
        * **Self-healing:** Tự động phát hiện và sửa lỗi khi có sự cố xảy ra
        * **Self-monitoring:** Liên tục giám sát trạng thái của cluster và các components
        * **Autonomic Management:** Giảm thiểu công việc quản trị thủ công, tự động xử lý các tác vụ như rebalancing, recovery
    + **Distributed (Phân tán):** RADOS phân tán dữ liệu trên toàn bộ cluster:
        * **Data Distribution:** Sử dụng thuật toán CRUSH để phân tán dữ liệu đồng đều
        * **No Single Point of Failure:** Không có điểm lỗi đơn lẻ trong kiến trúc
        * **Scale-out Architecture:** Khả năng mở rộng tuyến tính bằng cách thêm nodes
        * **Intelligent Storage Nodes:** Các OSD thông minh, có khả năng ra quyết định phân tán
    + **Object Store:** RADOS lưu trữ dữ liệu dưới dạng objects:
        * **Flat Namespace:** Không gian tên phẳng trong mỗi pool, không có cấu trúc thư mục
        * **Object Structure:** Mỗi object bao gồm identifier, binary data và metadata
        * **Scalability:** Có thể quản lý hàng triệu đến hàng tỷ objects

## Cơ chế Replication
RADOS sử dụng primary-copy replication model bao gồm:
- **Write Process:** 
    1. **Client Request:** Client gửi write request tới Primary OSD của PG
    2. **Validation:** Primary OSD validate request, gán sequence number
    3. **Parallel Replication:** Primary gửi write operation tới tất cả Replica OSDs đồng thời
    4. **Local Write:** Primary cũng write data locally
    5. **Acknowledgment:** Mỗi Replica OSD persist data và gửi ACK về Primary
    6. **Client Confirmation:** Primary chỉ confirm với client sau khi nhận đủ ACK từ min_size OSDs
- **Read Process:** 
    1. Read requests được xử lý tại Primary OSD
    2. Primary có bản copy mới nhất và authoritative của dữ liệu
    3. Giúp đảm bảo strong consistency cho read operations

- RADOS duy trì số lượng replicas theo cấu hình:
    + **Pool Size:** Số lượng copies của mỗi object (thường là 2 hoặc 3)
    + **Min Size:** Số lượng copies tối thiểu cần có để PG hoạt động (thường là 2)
    + **Automatic Replication:** Tự động tạo và duy trì replicas
    + **Different Failure Domains:** Replicas được đặt trên các failure domains khác nhau (host, rack, datacenter)

- Ngoài ra RADOS hỗ trợ **erasure coding** giúp :
    + **Space Efficiency:** Tiết kiệm không gian hơn replication (ví dụ: k=8, m=3 thay vì 3 replicas)
    + **Data Chunks:** Chia data thành k data chunks và m coding chunks
    + **Fault Tolerance:** Có thể phục hồi dữ liệu khi mất tối đa m chunks
    + **Trade-offs:** Tiết kiệm không gian nhưng CPU overhead cao hơn và recovery chậm hơn

[ Erasure Coding](/08-storage-and-distributed-systems/02-Ceph-Storage/00-fundamentals/06-Erasure%20Coding.md)


## Consistency Model
- RADOS cung cấp strong consistency model, tuân theo CP principles trong CAP theorem:

    + Linearizable: Tất cả clients thấy cùng một view của data
    + Synchronous Replication: Write phải được replicate đến min_size OSDs trước khi acknowledge
    + Read-Your-Writes: Client đọc được ngay dữ liệu vừa ghi thành công
    + No Stale Reads: Không có trường hợp đọc dữ liệu cũ sau khi write đã được confirm

- Quy trình đảm bảo consistency cho write operations:

    1. Primary OSD nhận write request
    2. Write đồng thời tới tất cả replicas trong Acting Set
    3. Chỉ acknowledge client sau khi nhận đủ ACKs từ min_size OSDs
    4. Sequence numbers đảm bảo thứ tự operations
    5. Short-term logs giúp recovery nhanh khi có intermittent failures
