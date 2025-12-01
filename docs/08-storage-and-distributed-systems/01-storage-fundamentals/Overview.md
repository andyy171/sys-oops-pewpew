# Tổng quan về Storage
- Hệ thống lưu trữ trong công nghệ thông tin (CNTT) là một thành phần cốt lõi, đảm bảo dữ liệu được lưu trữ, truy cập và quản lý một cách hiệu quả. 
- Nó được tổ chức theo cấu trúc phân cấp (hierarchy), giúp cân bằng giữa tốc độ, dung lượng và chi phí. Cấu trúc này bao gồm các cấp độ từ bộ nhớ nhanh nhất (như RAM) đến lưu trữ chậm hơn nhưng dung lượng lớn (như băng từ). Vai trò của các thành phần chính như sau:

- **Controller:** Là **bộ điều khiển lưu trữ, quản lý giao tiếp giữa hệ thống và thiết bị lưu trữ**. Nó xử lý các lệnh đọc/ghi, quản lý **RAID (Redundant Array of Independent Disks)** để tăng độ tin cậy và hiệu suất, và đôi khi tích hợp cache để tối ưu hóa tốc độ. Ví dụ, trong các hệ thống doanh nghiệp, controller có thể là một card HBA (Host Bus Adapter) hoặc tích hợp trong mainboard.
- **Disk:** **Thiết bị lưu trữ vật lý,** có thể là **HDD (Hard Disk Drive)** với đĩa từ quay cơ học hoặc **SSD (Solid State Drive)** sử dụng chip flash. Disk lưu trữ dữ liệu dưới dạng block (khối), thường là 4KB hoặc 512B mỗi block.
- **Cache:** Là **bộ nhớ tạm thời tốc độ cao** (thường là DRAM hoặc SRAM) để lưu trữ dữ liệu thường xuyên truy cập, giảm thời gian chờ đợi từ disk chậm hơn. Cache có thể nằm ở mức controller, OS, hoặc ứng dụng.

- Quá trình ghi/đọc dữ liệu diễn ra theo chuỗi:     
    1. Ứng dụng yêu cầu dữ liệu qua hệ điều hành (OS).
    2. OS chuyển lệnh đến file system (FS), FS ánh xạ thành block, và block được gửi đến disk qua controller. 
    3. Trong quá trình đọc, nếu dữ liệu có trong cache, nó sẽ được trả về ngay lập tức (cache hit), ngược lại là cache miss và phải đọc từ disk. 
    > Quá trình ghi có thể là write-through (ghi ngay vào disk) hoặc write-back (ghi vào cache trước, sau đó flush vào disk để tăng tốc độ nhưng rủi ro mất dữ liệu nếu hệ thống crash).

> Distributed System là Hệ thống bao gồm nhiều máy độc lập phối hợp để hoạt động như một hệ thống thống nhất.

- Phân biệt các loại lưu trữ
    - **Lưu trữ cục bộ (Local Storage):** **Dữ liệu nằm trực tiếp trên máy tính hoặc server**, như ổ cứng nội bộ. 
    + **Ưu điểm:** Tốc độ cao, latency thấp.
    + **Nhược điểm:** Không chia sẻ dễ dàng, rủi ro mất dữ liệu nếu hardware hỏng.

    - **Lưu trữ mạng (Network Storage):** **Dữ liệu được lưu trữ trên các máy chủ được kết nối với các mạng để có thể truy cập**, như NAS (Network Attached Storage) hoặc SAN (Storage Area Network). NAS dùng giao thức file-level (NFS, SMB), SAN dùng block-level (iSCSI, Fibre Channel). 
    + **Ưu điểm:** Chia sẻ dữ liệu giữa nhiều máy.
    + **Nhược điểm:** Latency cao hơn do mạng.

    - **Lưu trữ phân tán (Distributed Storage):** Dữ liệu được phân bổ trên nhiều node, như trong cloud (AWS S3, Google Cloud Storage) hoặc hệ thống như Ceph, Hadoop HDFS. 
    + **Ưu điểm:** Scale horizontally, fault-tolerant.
    + **Nhược điểm:** Phức tạp quản lý, overhead đồng bộ hóa.

>Lưu ý: Trong thực tế, các loại lưu trữ thường kết hợp, ví dụ hybrid cloud với local cache cho distributed storage để giảm latency.
>

## 1. Lưu trữ phân tán 
- **Các tính chất quan trọng của Lưu trữ phân tán:** 
    - **Persistence (Tính Bền Vững) :** Dữ liệu phải tồn tại sau khi ứng dụng ngừng chạy hoặc hệ thống tắt. Đây là yêu cầu bắt buộc cho mọi nền tảng.
    - **Scalability (Khả năng mở rộng):** Khả năng của hệ thống lưu trữ để xử lý khối lượng dữ liệu hoặc lưu lượng truy cập lớn hơn mà không làm giảm hiệu suất. 
        - Có hai loại:
            - **Vertical Scaling** (thêm tài nguyên vào một server)
            - **Horizontal Scaling** (sharding hoặc partitioning dữ liệu qua nhiều server).
    - **Reliability:** Hệ thống tiếp tục hoạt động đúng khi 1 phần bị lỗi.
    - **Availability (Tính Khả Dụng):** Mức độ mà dữ liệu có thể được truy cập và sử dụng ngay lập tức khi cần. Được đo bằng "nines" (ví dụ: $99.999\%$ - five nines). Đạt được qua redundancy (dự phòng) và failover (chuyển đổi dự phòng).
    - **Efficiency:** 
        - **Latency(Độ Trễ):** Thời gian cần thiết để thực hiện một thao tác đọc hoặc ghi. Thấp là yêu cầu cho các hệ thống giao dịch hoặc tương tác trực tiếp.

        - **Throughput (Thông Lượng):** Số lượng dữ liệu (hoặc giao dịch) có thể được xử lý trong một đơn vị thời gian (ví dụ: IOPS - Input/Output Operations Per Second, MB/s).

### 1.1. Nguyên lý cơ bản 
#### CAP Theorem
- Trong hệ thống phân tán chỉ đảm bảo được 2/3 yếu tố:
    - **Consistency (C)**: mọi node thấy dữ liệu giống nhau.
    - **Availability (A):** mọi request đều nhận phản hồi.
    - **Partition Tolerance (P):** hệ thống vẫn chạy dù network bị chia cắt.

#### Quorum ( write/read quorum) 


### 1.2. Cơ chế lưu trữ phân tán
#### 1.2.1. Replication factor


#### 1.2.2. Sync vs Async replication

### 1.3. Phân vùng dữ liệu Sharding



## 2. Mô hình consistency & guarantees

### 2.1. Strong consistency

### 2.2. Eventual consistency


### 2.3. Causal / Session consistency


### 2.4. Kiến trúc đảm bảo (WAL, MVCC, Two-phase commit)


## 3. Kiến trúc Tiering và Storage Classes
### 3.1. Hot / Warm / Cold tiers


### 3.2. Hierarchical storage management
Latency Hierarchy: RAM < SSD < HDD < Tape

- **RAM:** Latency ~nanoseconds, volatile.
- **SSD:** ~microseconds, non-volatile, flash-based.
- **HDD:** ~milliseconds, cơ học.
- **Tape:** ~seconds, dung lượng lớn, cho archive.
- **Pmem**

>Hierarchy này giúp thiết kế hệ thống tiered storage, nơi dữ liệu hot ở RAM/SSD, cold ở HDD/Tape.


## 4. Thành phần vận hành
### 4.1. Deployment & topology
#### 4.1.1. Single datacenter vs geo-replication


#### 4.1.2. Placement groups / failure domains

### 4.2. Scaling & Rebalancing

### 4.3. Monitoring, Alerting, Telemetry


### 4.4. Backup & Restore, Snapshotting


### 4.5. Upgrade / Rolling update / Maintenance


## 5. Hiệu năng (Performance) & QoS

### 5.1. IOPS, Throughput, Latency


### 5.2. Caching strategies (read cache, write-back)


### 5.3. QoS throttling, throttles & IOPS guarantees

## 6. Data Protection & Reliability
### 6.1. Durability models (replication vs EC)


### 6.2. Data scrubbing, repair, self-healing


### 6.3. Consistency check (fsck-like tools)


## 7. Bảo mật & Tuân thủ (Security & Compliance)
### 7.1. Encryption at rest & in transit


### 7.2. Access control (RBAC, ACLs)


### 7.3. Audit logs, WORM, retention policies


## 8. Tích hợp với hệ sinh thái (Integrations)
### 8.1. Kubernetes (CSI, RWO/RWX semantics)


### 8.2. Virtualization (VM volumes)


### 8.3. Backup systems, Object gateways (S3 compatible)


### 8.4. Analytics / Big Data (HDFS, Spark)

## 9. Troubleshooting checklist
### 9.1. Node failure scenarios

### 9.2. Slow IO diagnosis

### 9.3. Data recovery flow

