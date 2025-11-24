Domain 3: Thiết Kế Các Kiến Trúc Hiệu Năng Cao (Design High-Performing Architectures) - Kỳ Thi AWS SAA-C03

LƯU Ý QUAN TRỌNG: Domain này tập trung vào việc lựa chọn và thiết kế các dịch vụ AWS để đáp ứng các yêu cầu về hiệu suất, khả năng mở rộng (scalability), tính đàn hồi (elasticity), và độ trễ thấp. Không có một câu trả lời chung cho mọi bài toán; giải pháp tối ưu phụ thuộc vào từng ngữ cảnh cụ thể.

Phần 1: Các Giải Pháp Lưu Trữ Hiệu Năng Cao Và Có Khả Năng Mở Rộng (High-Performing and/or Scalable Storage Solutions)
1. Ba Hình Thức Lưu Trữ Chính:

Object Storage (Lưu trữ đối tượng - e.g., Amazon S3): Lý tưởng cho dữ liệu phi cấu trúc, archive, backup, big data. Truy cập qua API.

Các lớp lưu trữ (Storage Classes): Hiểu rõ sự khác biệt giữa S3 Standard, Standard-IA, Glacier về chi phí, hiệu suất truy cập.

Tính Resiliency: Dữ liệu được lưu trong một Region và có thể chịu được lỗi của một Availability Zone (AZ). Có thể sao chép sang các Region khác.

Tối ưu hiệu suất: S3 Transfer Acceleration (upload), CloudFront (download), multi-part uploads.

Block Storage (Lưu trữ khối - e.g., Amazon EBS): Gắn trực tiếp vào EC2 instances, dùng cho file systems, databases. Độ trễ rất thấp.

Các loại Volume: Hiểu hiệu suất của SSD (gp3/io1 - cho IOPS cao) và HDD (st1/sc1 - cho throughput cao).

Scaling: Phải thực hiện thủ công bằng cách thay đổi cấu hình (kích thước, IOPS, throughput). Không tự động scale.

Snapshot: EBS Snapshots được lưu trong S3, giúp dữ liệu trở nên Region resilient.

File Storage (Lưu trữ file - e.g., Amazon EFS, Amazon FSx): Cung cấp hệ thống file chia sẻ qua mạng (network file system).

Amazon EFS: Dành cho Linux instances, sử dụng giao thức NFS. Hỗ trợ hybrid access (VPN/Direct Connect).

Scaling: Tự động scale lên/xuống khi bạn thêm/xóa file.

Cấu hình hiệu suất: General Purpose vs. Max I/O.

Amazon FSx:

FSx for Windows: Dành cho Windows instances, hỗ trợ SMB protocol, NTFS, tích hợp Active Directory.

FSx for Lustre: Dành cho workload High-Performance Computing (HPC) và machine learning trên Linux.

2. Lưu Ý Khi Lựa Chọn:

Access Patterns: Cách thức truy cập dữ liệu (API, block, file).

Khả năng mở rộng: Cần tự động (EFS, S3) hay thủ công (EBS)?

Hiệu suất: Yêu cầu độ trễ thấp nhất (EBS) hay throughput cao (S3)?

Chi phí: Sử dụng Lifecycle Policies (chính sách vòng đời) để tự động chuyển dữ liệu sang lớp lưu trữ rẻ hơn khi ít được truy cập.

Dung lượng tương lai: Hiểu giới hạn dung lượng của từng dịch vụ để lập kế hoạch.

Phần 2: Thiết Kế Các Giải Pháp Điện Toán Hiệu Năng Cao Và Đàn Hồi (High-Performing and Elastic Compute Solutions)
1. Ba Hình Thức Điện Toán Chính:

Instances (Máy ảo - Amazon EC2):

Instance Types & Families: Hiểu sự khác biệt giữa các họ (M - balanced, C - compute optimized, R - memory optimized, etc.) về tỷ lệ CPU/memory/network.

Scaling: EC2 không tự động scalable. Phải sử dụng EC2 Auto Scaling để tự động thêm/bớt instances dựa trên nhu cầu (vd: dựa trên CloudWatch metrics như CPU utilization).

Kết hợp với Elastic Load Balancing (ELB) để phân phối traffic và thực hi health checks.

Containers (Amazon ECS, Amazon EKS):

Amazon ECS: Dịch vụ container managed của AWS.

Chế độ chạy: Fargate (serverless - AWS quản lý hạ tầng) vs. EC2 (bạn tự quản lý cluster EC2).

Amazon EKS: Managed Kubernetes service.

Functions (AWS Lambda):

Serverless: Chỉ trả tiền cho thời gian thực thi, không quản lý server.

Tính đàn hồi: Tự động scale cực cao, xử lý từ 1 đến hàng nghìn request cùng lúc.

Giới hạn: Thời gian thực thi tối đa 15 phút. Dùng Step Functions cho workflow dài hơn.

Lambda@Edge: Chạy Lambda tại các CloudFront Edge Locations để giảm độ trễ.

2. Các Dịch Vụ Hỗ Trợ Scalability & Decoupling:

Amazon SQS (Simple Queue Service): Hàng đợi tin nhắn để tách rời (decouple) các thành phần ứng dụng, cho phép chúng scale độc lập. Hiểu cách xử lý lỗi với Lambda.

Amazon SNS (Simple Notification Service): Dịch vụ pub/sub để gửi thông báo.

Các dịch vụ serverless khác: API Gateway (có thể cấu hình throttling), EventBridge, AWS AppSync (GraphQL interface).

3. Giám Sát & Tự Động Hóa:

Amazon CloudWatch: Là trung tâm để giám sát và tự động hóa.

Metrics: Số liệu về hiệu năng (CPU, Network, custom metrics).

Alarms: Cảnh báo khi metrics vượt ngưỡng, có thể kích hoạt Auto Scaling.

Lưu ý: Một số metrics như Memory Usage không có sẵn mặc định, cần cài đặt CloudWatch Agent.

Phần 3: Các Giải Pháp Cơ Sở Dữ Liệu Hiệu Năng Cao (High-Performing Database Solutions)
1. Các Loại Database & Khi Nào Sử Dụng:

Relational (Quan hệ - Amazon RDS, Aurora): Cho dữ liệu có cấu trúc, cần ACID transactions, complex queries.

NoSQL - Key/Value (Amazon DynamoDB): Cho workload cần độ trễ millisecond ổn định ở mọi scale, schema-less.

In-Memory (Amazon ElastiCache - Redis/Memcached, DAX): Làm cache để giảm tải cho database chính, giảm độ trễ.

2. So Sánh Sâu RDS vs. Aurora:

RDS:

Read Replicas: Chỉ dùng để scale read operations.

Multi-AZ: Chỉ dùng cho high availability (tự động failover sang AZ standby).

Aurora:

Kiến trúc Cluster: Một primary instance và nhiều Aurora Replicas. Các replica này vừa dùng để scale read VỪA có thể dùng cho failover (thay thế Multi-AZ).

Shared Storage: Dữ liệu được lưu trong một cluster volume được chia sẻ với 6 bản sao across 3 AZ, cho hiệu suất và độ sẵn sàng cao hơn.

Aurora Global Database: Mở rộng database across multiple Regions.

Aurora Serverless: Cấu hình auto-scaling tự động (từ 0 ACU) dựa trên nhu cầu, cực kỳ cost-effective cho workload không Predictable.

3. Tối Ưu Hiệu Suất Database:

Caching: Sử dụng ElastiCache (cho RDS/Aurora) hoặc DAX (cho DynamoDB) để giảm độ trễ.

Quản lý kết nối: RDS Proxy duy trì pool kết nối, rất quan trọng cho serverless (Lambda) để tránh làm quá tải database.

Capacity Planning: Chọn đúng instance type/size. DynamoDB có On-Demand (cho workload không Predictable) và Provisioned capacity.

Phần 4: Các Kiến Trúc Mạng Hiệu Năng Cao Và Có Khả Năng Mở Rộng (High-Performing Network Architectures)
1. Xây Dựng VPC (Virtual Private Cloud):

Thành phần & Quy trình: VPC (Regional) -> Subnets (trong AZs) -> Route Tables -> Internet Gateway (IGW) -> Network ACLs (tùy chọn, stateless) -> Security Groups (stateful) -> Resources -> NAT Gateway, VPC Peering, Endpoints.

Tính bảo mật: VPC mặc định là private.

2. Kết Nối Hybrid (On-premise to AWS):

AWS Site-to-Site VPN: Kết nối qua Internet, phù hợp cho lưu lượng vừa và nhỏ.

AWS Direct Connect (DX): Kết nối vật lý chuyên dụng, cung cấp băng thông cao, ổn định, độ trễ thấp. Phù hợp cho lưu lượng lớn.

AWS Transit Gateway: Hub trung tâm để kết nối nhiều VPC và kết nối on-premise (qua VPN/DX) một cách đơn giản.

3. Kết Nối Nội Bộ AWS:

Giữa các VPC: VPC Peering (trực tiếp) hoặc Transit Gateway (qua hub).

Đến AWS Public Services (S3, DynamoDB) từ Private Subnet: Sử dụng VPC Endpoints (Gateway hoặc Interface) để kết nối an toàn mà không cần Internet Gateway/NAT.

Cung cấp dịch vụ riêng tư: AWS PrivateLink cho phép expose dịch vụ của bạn trong VPC cho các VPC khác một cách an toàn.

4. Tối Ưu Hiệu Suất Mạng Toàn Cầu:

Amazon Route 53: DNS service với các Routing Policies (e.g., Latency Routing, Geoproximity Routing) để điều hướng user đến endpoint gần nhất/khỏe mạnh nhất.

Amazon CloudFront: Content Delivery Network (CDN) cache nội dung tĩnh tại Edge Locations, giảm độ trễ và tải cho origin server.

AWS Global Accelerator: Cải thiện hiệu suất bằng cách sử dụng network backbone của AWS, cung cấp IP tĩnh làm entry point.

5. Dịch Vụ Chuyển Dữ Liệu:

AWS DataSync: Tự động hóa và tăng tốc chuyển dữ liệu quy mô lớn đến/đi từ AWS.

AWS Snow Family: Để di chuyển dữ liệu rất lớn (petabyte-scale) khi kết nối mạng không khả thi.

AWS DMS (Database Migration Service): Di chuyển cơ sở dữ liệu.

AWS Transfer Family: Managed service cho các giao thức chuyển file (SFTP, FTP, FTPS).

Phần 5: Các Giải Pháp Thu Nhận Và Chuyển Đổi Dữ Liệu Hiệu Năng Cao (High-Performing Data Ingestion and Transformation Solutions)
1. Các Mẫu Hình Thu Nhận (Ingestion Patterns):

Homogeneous Ingestion: Di chuyển dữ liệu mà không thay đổi định dạng (e.g., dùng DataSync, DMS). Trọng tâm là tốc độ.

Heterogeneous Ingestion: Dữ liệu được chuyển đổi (transform) trong quá trình thu nhận (e.g., dùng AWS Glue, EMR).

2. Xử Lý Dữ Liệu Streaming (Real-time):

Amazon Kinesis Data Streams: Thu nhận và lưu trữ dữ liệu streaming để xử lý real-time linh hoạt.

Amazon Kinesis Data Firehose: Tải dữ liệu streaming trực tiếp vào kho dữ liệu (S3, Redshift, etc.) một cách đơn giản, có thể transform cơ bản.

Amazon Kinesis Data Analytics: Phân tích và biến đổi dữ liệu streaming theo thời gian thực bằng SQL.

So sánh: Dùng Data Streams cho xử lý real-time phức tạp. Dùng Data Firehose để load nhanh vào data stores.

3. Data Lake & Xử Lý Dữ Liệu:

Data Lake: Kho lưu trữ tập trung cho mọi loại dữ liệu (structured/unstructured) trên S3.

AWS Glue: Dịch vụ serverless ETL để discover, prepare, và transform dữ liệu.

Amazon EMR: Managed service cho các framework Big Data (Spark, Hadoop) để xử lý dữ liệu quy mô rất lớn.

Tối ưu hóa: Chuyển đổi dữ liệu sang định dạng Parquet hoặc ORC để tăng hiệu suất truy vấn và giảm dung lượng.

4. Phân Tích & Trực Quan Hóa:

Amazon Athena: Query dữ liệu trực tiếp trên S3 bằng SQL, serverless.

AWS Lake Formation: Giúp thiết lập và quản lý Data Lake an toàn một cách nhanh chóng.

Amazon QuickSight: Dịch vụ trực quan hóa dữ liệu (Business Intelligence).

5. Bảo Mật Cho Dữ Liệu:

IAM Policies & Bucket Policies: Kiểm soát truy cập.

Mã hóa: Sử dụng AWS KMS để quản lý keys mã hóa. Dùng AWS CloudHSM cho yêu cầu tuân thủ và bảo mật cao cấp (e.g., PII data).

Tính năng bảo vệ S3: Versioning, Object Lock, Replication.

Kết Luận cho Domain 3: Domain này kiểm tra khả năng áp dụng kiến thức sâu rộng về các dịch vụ AWS để giải quyết các bài toán về hiệu suất và khả năng mở rộng. Thí sinh cần hiểu rõ nguyên lý hoạt động, điểm mạnh/điểm yếu, và cách tích hợp của từng dịch vụ trong một kiến trúc tổng thể, đồng thời luôn đánh giá các yêu cầu về bảo mật và chi phí.