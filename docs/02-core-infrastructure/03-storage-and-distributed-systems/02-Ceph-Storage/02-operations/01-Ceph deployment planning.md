# Lưu ý khi chuẩn bị triển khai 1 cụm ceph 
## Yêu cầu phần cứng
- Ceph là software-based storage system, được thiết kế chạy tương thích với các phần cứng chung. Tính năng này của Ceph khiến nó đáp ứng được các yêu cầu về chi phí, tính mở rộng, giải pháp của các nhà cung cấp.

- Cluster hardware config yêu cầu phải có kế hoạch khi xây dựng storage. Loại hardware sử dụng cho thiết kế cluster cần được cân nhắc trước khi khởi tạo project. Kế hoạch càng chi tiết giúp cho thiết kế tránh khởi các vấn đề về nghẽn cổ chai, tính bảo đảm của cluster. Chọn phần cứng dựa trên sự đa dạng của các nhà cung cấp, túi tiền nhưng các yếu tố phải xem xét cẩn trọng là hiệu năng, sức chứa hoặc cả 2, mức chịu lỗi, các phương pháp xử lý.

### Yêu cầu trên OSD
OSD là trái tim của việc lưu trữ và là nơi xảy ra các quá trình tính toán phức tạp (CRUSH, Replication, Recovery). Đây là nơi cần đầu tư tài nguyên đáng kể nhất.

- **CPU và RAM (Rất Quan trọng):**

+ **CPU:** Cần tối thiểu 1 Core CPU vật lý (hoặc logic) cho mỗi OSD daemon. Quá trình phục hồi và tái cân bằng yêu cầu CPU cao để tính toán lại vị trí dữ liệu (CRUSH) và thực hiện các thuật toán Erasure Coding.

+ **RAM:** Khuyến nghị tối thiểu 5 GB RAM/OSD daemon (đã bao gồm phần RAM cho HĐH). Thiếu RAM sẽ làm OSD bị starve (đói tài nguyên), ảnh hưởng nghiêm trọng đến hiệu suất ghi.

- **Lưu trữ Backend (BlueStore):**

+ **Công nghệ Mặc định:** Hiện nay, BlueStore là backend mặc định và được khuyến nghị, lưu trữ trực tiếp trên thiết bị block mà không cần qua hệ thống tệp truyền thống (ext4/XFS).

+ **Tách biệt Metadata:** BlueStore sử dụng SSD/NVMe nhanh để lưu trữ Metadata/WAL (Write Ahead Log) riêng biệt với dữ liệu trên HDD. Việc chia sẻ một SSD cho 2-4 OSD HDD là giải pháp cân bằng chi phí, nhưng cần lưu ý nếu SSD này lỗi, tất cả OSD liên kết sẽ tạm thời dừng hoạt động (vì dữ liệu metadata bị mất, mặc dù dữ liệu object vẫn được nhân bản trên các OSD khác).

### Yêu cầu MDS và Gateways

Các daemon này đại diện cho các giao diện truy cập cấp cao, yêu cầu tài nguyên phụ thuộc vào khối lượng công việc của từng dịch vụ.

- **MDS (Metadata Server cho CephFS):**

+ Yêu cầu CPU và RAM cao (RAM cao để caching metadata). Cần triển khai tối thiểu 2 node (1 Active, 1 Standby) để đảm bảo HA.


### Yêu cầu cho Monitor (MON)
MON chịu trách nhiệm duy trì sự đồng thuận và Cluster Map, yêu cầu tài nguyên không cao nhưng cần đảm bảo tính sẵn sàng cao (HA).

Tính Sẵn sàng (HA): Luôn cần triển khai số lẻ các node MON (tối thiểu 3 hoặc 5) tại các Failure Domain (vùng lỗi, ví dụ: các rack vật lý khác nhau) để đảm bảo Quorum (đa số đồng thuận) và ngăn chặn lỗi phân tách (split-brain).

Tài nguyên: MON chỉ yêu cầu CPU và RAM ở mức cơ bản (vài GB RAM là đủ) vì không lưu trữ dữ liệu người dùng. Tuy nhiên, nó cần ổ đĩa SSD nhỏ để lưu trữ Cluster Map và log.

Network: Khuyến nghị nâng cấp tối thiểu lên 10 Gbps. Khi có sự cố xảy ra trong cluster (nhiều OSD down), MON là nơi tiếp nhận lượng lớn thông tin trạng thái. Tốc độ mạng thấp sẽ làm chậm phản ứng của cả cluster, kéo dài thời gian phục hồi.



+ **Network:** Tối thiểu 10 Gbps nếu CephFS là dịch vụ chính.

- **RGW (RADOS Gateway cho Object Storage S3/Swift):**

+ Yêu cầu CPU mạnh và Network 10 Gbps+ để xử lý các kết nối HTTP/SSL. RGW dễ dàng được mở rộng (scale-out) bằng cách thêm nhiều RGW node phía sau Load Balancer.

- **RBD/iSCSI Gateway:** Cần tài nguyên CPU và Network tốt (10 Gbps+) để xử lý việc mapping block và truyền tải lưu lượng iSCSI.


## Yêu cầu về mạng 
- **Network (Yêu cầu Tối thiểu 10 Gbps):**

+ **Bắt buộc Tách biệt:** Cần ít nhất hai mạng riêng biệt: Public Network (client-cluster) và Cluster Network (OSD-OSD).

+ **Cluster Network:** Cần tối thiểu 10 Gbps cho mạng này. Đây là điểm nghẽn cổ chai quan trọng. Mọi hoạt động nhân bản dữ liệu (Replication) và phục hồi (Recovery/Rebalancing) đều diễn ra trên mạng này. Tốc độ thấp (ví dụ: 1 Gbps) sẽ làm chậm quá trình ghi của client (vì client phải chờ OSD Primary nhân bản dữ liệu trên mạng chậm) và kéo dài thời gian phục hồi.


## Cephadm (container-based, recommended)



