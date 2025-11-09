Domain 4: Design Cost-Optimized Architectures
I. Nguyên Tắc Chung Về Tối Ưu Chi Phí
Mô Hình Chi Phí Biến Đổi (Variable Cost Model): AWS hoạt động theo mô hình "chỉ trả cho những gì bạn sử dụng". Đây là lợi thế lớn để liên tục tối ưu hóa chi phí.

Quy Trình Lặp Lại (Iterative Process): Tối ưu chi phí không phải là một lần, mà là một hành trình liên tục. Hàng tháng, bạn có thể xem xét từng mảng (compute, storage, database, network) để tìm cơ hội cắt giảm.

Đo Lường và Giám Sát (Monitoring & Measurement): Bạn không thể quản lý cái bạn không thể đo lường. Phải thiết lập hệ thống giám sát để hiểu rõ việc sử dụng tài nguyên và chi phí.

Gắn Nhãn (Tagging): Một chiến lược gắn nhãn (tag) rõ ràng là CỰC KỲ QUAN TRỌNG để phân bổ chi phí chính xác cho từng dự án, phòng ban, môi trường (prod/dev/test) thông qua các công cụ như Cost Explorer.

II. Tối Ưu Chi Phí Storage (Lưu Trữ)
1. Chọn Đúng Dịch Vụ Cho Đúng Nhu Cầu:

Block Storage (EBS): Cho dữ liệu cần truy cập ở cấp độ khối (block-level) như ổ đĩa OS, databases.

Object Storage (S3): Cho dữ liệu phi cấu trúc, dung lượng lớn (images, backups, logs).

File Storage (EFS): Cho hệ thống file chia sẻ giữa nhiều EC2 instances.

Ephemeral Storage: Lưu trữ tạm thời đi kèm EC2. Rẻ nhất nhưng dữ liệu sẽ mất khi instance dừng.

2. Amazon S3 Cost Optimization:

S3 Storage Classes: Hiểu rõ sự đánh đổi giữa chi phí lưu trữ và chi phí truy xuất của từng lớp.

Standard: Truy cập thường xuyên.

Standard-IA & One Zone-IA: Truy cập không thường xuyên.

Intelligent-Tiering: Tự động chuyển đổi lớp cho dữ liệu có pattern truy cập không thể đoán trước. Tối ưu chi phí nhất khi không chắc chắn về access pattern.

Glacier & Deep Archive: Lưu trữ archive, thời gian truy xuất lâu.

Vòng Đời Dữ Liệu (Lifecycle Policies): Tự động chuyển đổi giữa các storage class hoặc xóa dữ liệu dựa trên rules (ví dụ: chuyển sang Glacier sau 90 ngày, xóa sau 365 ngày).

Requester Pays: Cấu hình bucket để người request (thay vì chủ bucket) chịu phí request và data download.

3. Amazon EBS Cost Optimization:

Right-Sizing: Chọn đúng dung lượng và IOPS (Input/Output Operations Per Second) cần thiết. Tránh over-provisioning.

Chọn Đúng Volume Type:

gp3/gp2: General Purpose, cân bằng giữa chi phí và hiệu năng.

io1/io2: Provisioned IOPS, hiệu năng cao, đắt tiền. Chỉ dùng khi thực sự cần.

Quản Lý Snapshot:

Sử dụng Amazon Data Lifecycle Manager để tự động xóa các snapshot cũ, không cần thiết.

Trusted Advisor có thể phát hiện các EBS volumes không được gắn (unattached) – hãy xóa chúng để tiết kiệm chi phí.

III. Tối Ưu Chi Phí Compute (Máy Chủ)
1. Right-Sizing EC2 Instances:

Là bước đầu tiên và quan trọng nhất. Chọn instance type và size phù hợp với nhu cầu thực tế của workload (dựa trên metrics từ CloudWatch: CPU, RAM, Network...).

Hiểu các instance families:

General Purpose (M): Cân bằng, cho ứng dụng thông thường.

Compute Optimized (C): Cho workload cần CPU cao (batch processing, gaming).

Memory Optimized (R): Cho workload cần nhi RAM (databases, big data processing).

2. Chọn Đúng Pricing Model:

On-Demand: Linh hoạt nhất, không cam kết. Đắt nhất.

Savings Plans: Cam kết mức chi tiêu ($/giờ) để nhận discount lớn. Linh hoạt (áp dụng cho EC2, Fargate, Lambda).

Reserved Instances: Cam kết trước với một loại instance cụ thể để nhận discount. Ít linh hoạt hơn Savings Plans.

Spot Instances: Tận dụng capacity dư thừa, giá rẻ nhất (có thể giảm tới 90%). Có thể bị thu hồi với cảnh báo 2 phút. Chỉ dùng cho workload chấp nhận gián đoạn (batch processing, stateless web servers, HPC).

3. Tăng Tính Co Giãn (Increase Elasticity):

Sử dụng AWS Auto Scaling & EC2 Auto Scaling để tự động thêm/bớt instance dựa trên demand. Chỉ trả tiền khi cần.

Kết hợp với Elastic Load Balancing (ELB) để phân phối traffic đồng đều.

4. Chọn Đúng Dịch Vụ Compute:

AWS Lambda: Tối ưu bằng cách viết function chạy nhanh, sử dụng ít bộ nhớ.

AWS Fargate: Serverless cho containers. Không phải quản lý EC2 instances, chỉ trả cho tài nguyên container sử dụng.

Dịch vụ được quản lý (Managed Services): Sử dụng các dịch vụ như RDS, DynamoDB để giảm chi phí vận hành và quản lý.

IV. Tối Ưu Chi Phí Database (Cơ Sở Dữ Liệu)
1. Chọn Đúng Công Cụ Cho Đúng Dữ Liệu (Polyglot Persistence):

RDS/Aurora: Cho dữ liệu quan hệ, transactional.

DynamoDB: Cho dữ liệu NoSQL, access patterns có thể dự đoán.

S3: Lưu trữ các đối tượng lớn (large objects) để giảm tải cho database chính.

2. Scaling Strategies:

Scale Out (Horizontal) thay vì Scale Up (Vertical):

Sử dụng Read Replicas để phân tải truy vấn đọc, thay vì nâng cấp instance đắt tiền.

Sử dụng Caching (Amazon ElastiCache) để lưu trữ kết quả truy vấn thường dùng, giảm tải trực tiếp lên database.

3. Tận Dụng Managed Services & Cấu Hình:

Aurora Serverless: Tự động co giãn. Tối ưu chi phí cho workload không liên tục, khó dự đoán.

Quản Lý Backup: Thiết lập chính sách retention để tự động xóa các snapshot cũ, vượt quá nhu cầu.

V. Tối Ưu Chi Phí Network (Mạng)
1. Hiểu Và Kiểm Soát Data Transfer Costs: Đây là khoản phí ẩn quan trọng nhất.

Data Transfer OUT từ AWS ra Internet luôn tốn phí.

Data Transfer BETWEEN Availability Zones (AZs) thường tốn phí.

Data Transfer BETWEEN Regions luôn tốn phí đáng kể.

Chiến lược: Ưu tiên giữ lưu lượng truy cập trong cùng một AZ và Region bất cứ khi nào có thể.

2. Chọn Đúng Công Cụ Kết Nối:

Site-to-Site VPN: Kết nối qua Internet. Chi phí thấp, thiết lập nhanh.

AWS Direct Connect: Kết nối riêng tư, vật lý. Hiệu năng cao, chi phí cao. Dùng VPN làm failover cho Direct Connect để tiết kiệm chi phí.

VPC Peering vs. Transit Gateway: VPC Peering thường có chi phí data transfer thấp hơn Transit Gateway.

3. Sử Dụng Các Dịch Vụ Giảm Data Transfer:

VPC Endpoints: Cho phép kết nối private đến các dịch vụ AWS (như S3, DynamoDB) mà không cần đi qua Internet/NAT Gateway và không phát sinh phí data transfer trong cùng Region.

Amazon CloudFront (CDN):

Cache dữ liệu ở edge locations, giảm số request trực tiếp đến origin (S3, EC2, ALB).

KHÔNG tính phí data transfer từ Origin tới CloudFront Edge Locations. Chỉ tính phí data transfer từ CloudFront ra end-user.

Giảm tải đáng kể cho origin server, có thể cho phép sử dụng instance nhỏ hơn, rẻ hơn.

4. Tối Ưu Các Dịch Vụ Mạng Khác:

NAT Gateway: Có phí theo giờ + phí data processing. Trong môi trường dev/test, có thể dùng chung một NAT Gateway cho nhiều AZ để tiết kiệm chi phí.

API Gateway: Sử dụng Usage Plans và API Keys để thiết lập throttle và quota, kiểm soát lượng request và tránh chi phí phát sinh ngoài ý muốn.

VI. Công Cụ Quản Lý Chi Phí
AWS Cost Explorer: Phân tích và dự báo xu hướng chi phí, có thể lọc theo service, tag, v.v.

AWS Budgets: Đặt ngân sách và nhận cảnh báo khi chi phí vượt ngưỡng.

Cost and Usage Report (CAR): Báo cáo chi tiết nhất, cung cấp dữ liệu raw để phân tích.

AWS Trusted Advisor: Cung cấp recommendations thực tế, như phát hiện các EBS volumes không dùng, idle load balancers, v.v.

VII. Tư Duy Làm Bài Thi
Bước 1: Đáp Ứng Yêu Cầu Kỹ Thuật. Đầu tiên, luôn chọn giải pháp đáp ứng đủ các yêu cầu về tính năng, hiệu năng, bảo mật, độ tin cậy.

Bước 2: Tối Ưu Chi Phí Trong Các Phương Án Khả Thi. Khi nhiều lựa chọn đều thỏa mãn yêu cầu kỹ thuật, hãy chọn phương án TIẾT KIỆM CHI PHÍ NHẤT dựa trên các nguyên tắc trên (ví dụ: chọn Spot Instances thay On-Demand nếu workload cho phép, chọn S3 Intelligent-Tiering thay vì Standard, sử dụng VPC Endpoints để tránh data transfer cost).