# 4 huawei cloud container services

Huawei Cloud Container Services
1. Huawei Cloud Full-stack Container Services
Huawei Cloud cung cấp một bộ đầy đủ các dịch vụ container (Full-stack) để đáp ứng mọi nhu cầu từ phát triển ứng dụng, triển khai, vận hành đến quản lý vòng đời trên nền tảng đám mây. Kiến trúc này cho phép khách hàng lựa chọn mô hình phù hợp nhất với trạng thái hiện tại của ứng dụng và kỹ năng của đội ngũ.

1.1. Cloud Container Engine (CCE)
Cloud Container Engine (CCE) là dịch vụ quản lý container hóa doanh nghiệp hoàn toàn được quản lý, cung cấp nền tảng Kubernetes (K8s) có khả năng mở rộng cao và hiệu suất cao.

Tổng quan: CCE cho phép bạn dễ dàng triển khai và quản lý các cụm Kubernetes. Nó tự động hóa việc cung cấp, nâng cấp và mở rộng cụm, giúp bạn tập trung vào ứng dụng thay vì quản lý hạ tầng.

Tính năng chính:

High-Performance Networking: Sử dụng công nghệ Yangtse (dựa trên SR-IOV) cung cấp hiệu năng mạng gần như bare-metal cho container, độ trễ thấp và băng thông cao.

High-Performance Autoscaling: Hỗ trợ Cluster Autoscaler (CA), Horizontal Pod Autoscaler (HPA), và Vertical Pod Autoscaler (VPA) để tự động mở rộng/quy mô hạ tầng dựa trên tải.

Enhanced Kubernetes: Bổ sung nhiều operator và plugin mở rộng để quản lý stateful applications, network policies, và service mesh tích hợp.

Multi-AZ & High Availability: Hỗ trợ triển khai cụm across Multiple Availability Zones để đảm bảo tính sẵn sàng cao và khả năng chịu lỗi.

Hybrid & Multi-Cloud Management: Có thể quản lý các cụm Kubernetes on-premise hoặc trên các đám mây khác thông qua Karmada (một dự án open-source multi-cloud orchestration do Huawei khởi xướng).

Các Chế độ Triển khai:

CCE Standard: Cung cấp toàn quyền kiểm soát cụm worker nodes (ECS). Phù hợp cho các ứng dụng yêu cầu tùy chỉnh cao.

CCE Turbo: Tận dụng CCI (xem bên dưới) làm resource pool, cung cấp trải nghiệm serverless cho Pods với hiệu năng mạng vượt trội. Người dùng chỉ quản lý Pods, không cần quan tâm đến Nodes.

Use Cases: Ứng dụng microservices, ứng dụng AI/ML, web services, batch processing.

1.2. Cloud Container Instance (CCI)
Cloud Container Instance (CCI) là dịch vụ container serverless. Nó cho phép chạy container mà không cần phải quản lý server hay cụm Kubernetes, trả tiền theo giây cho mỗi container chạy.

Tổng quan: CCI loại bỏ hoàn toàn nhu cầu về cấu hình và bảo trì hạ tầng. Bạn chỉ cần đưa ra image container và cấu hình tài nguyên (CPU, memory), CCI sẽ chạy nó ngay lập tức.

Tính năng chính:

Serverless: Không có server để quản lý, không cần quan tâm đến capacity planning.

Pay-per-Use: Thanh toán chi tiết theo giây dựa trên lượng CPU và bộ nhớ thực tế mà container của bạn sử dụng.

Security Isolation: Sử dụng công nghệ Kata Containers để cung cấp sự cô lập mạnh mẽ cấp VM nhưng vẫn có trải nghiệm khởi động nhanh như container.

Native Kubernetes API Compatibility: Có thể được sử dụng như một resource pool cho CCE Turbo, cho phép một cụm CCE chạy cả Pod trên ECS và Pod serverless trên CCI.

Use Cases: Xử lý sự kiện (event-driven), batch jobs, tasks xử lý dữ liệu không liên tục, mở rộng quy mô nhanh chóng để xử lý traffic đột biến.

1.3. Software Repository for Container (SWR)
Software Repository for Container (SWR) là dịch vụ quản lý image container được quản lý toàn phần, cung cấp khả năng lưu trữ image an toàn và hiệu năng cao với các tính năng như đồng bộ và bảo mật.

Tổng quan: SWR hoạt động như một private registry cho các image Docker, tương thích hoàn toàn với Docker Registry API.

Tính năng chính:

Security Scanning: Tự động quét image để phát hiện lỗ hổng bảo mật (CVE) và cung cấp báo cáo chi tiết.

Image Sync: Hỗ trợ đồng bộ image across regions và từ public registry (như Docker Hub) về private registry của bạn.

High Availability & Performance: Được xây dựng trên kiến trúc phân tán, đảm bảo tính sẵn sàng cao và tốc độ push/pull image nhanh chóng.

Fine-Grained Access Control: Quản lý quyền truy cập chi tiết thông qua IAM và namespace.

Use Cases: Lưu trữ và quản lý image container cho tất cả các dịch vụ container khác (CCE, CCI), thiết lập CI/CD pipeline.

1.4. Các Dịch vụ Liên quan và Hệ sinh thái
ServiceStage: Dịch vụ nền tảng ứng dụng (aPaaS) để triển khai, vận hành và quản lý vòng đời ứng dụng microservice một cách end-to-end. Nó tích hợp sâu với CCE và CCI.

Application Orchestration Service (AOS): Dịch vụ orchestration cấp ứng dụng, cho phép mô hình hóa hạ tầng và ứng dụng bằng template để triển khai một cách nhất quán và tự động.

Cloud Native Service Mesh: Cung cấp khả năng quản lý lưu lượng traffic, bảo mật và quan sát cho các ứng dụng microservice dựa trên Istio.

2. Huawei Cloud Container Infrastructure Services
Đây là các dịch vụ và công nghệ nền tảng cung cấp sức mạnh và khả năng cho các dịch vụ container cấp cao hơn.

2.1. CCE Turbo
Như đã đề cập, CCE Turbo không chỉ là một chế độ triển khai mà còn là một nền tảng hạ tầng kết hợp sức mạnh của CCE và CCI.

Kiến trúc Mạng: Sử dụng Yangtse Network để cung cấp cho container một NIC ảo độc lập (elastic network interface - ENI) với hiệu năng cực cao, vượt trội so với mạng overlay truyền thống.

Kiến trúc Lưu trữ: Cung cấp Everest, một plugin CSI (Container Storage Interface) để cung cấp storage cao cấp (như EVS, SFS, OBS) cho container một cách liền mạch với hiệu năng cao.

Lợi ích: Hiệu suất Bare-metal, tính năng bảo mật cao, và mô hình serverless.

2.2. Volcano
Volcano là một hệ thống batch scheduling platform dành riêng cho các workload tính toán quy mô lớn như AI, Machine Learning, Big Data và HPC. Nó mở rộng Kubernetes để trở thành "batch scheduler" mạnh mẽ.

Tổng quan: Được khởi xướng bởi Huawei và nay là một dự án CNCF Sandbox.

Tính năng chính:

Batch Scheduling: Hỗ trợ các cơ chế scheduling nâng cao như Gang Scheduling (đảm bảo tất cả các task của một job được chạy cùng lúc hoặc không chạy task nào), Fair-Sharing, Queue, Reclaim.

Tối ưu hóa cho AI/ML: Hỗ trợ native scheduling cho các framework như TensorFlow, PyTorch, Spark.

Enhanced Job Management: Cung cấp các CRD (Custom Resource Definition) mở rộng để quản lý job phức tạp.

Tích hợp: Volcano được tích hợp sẵn và là scheduler mặc định cho các workload AI/ML trên CCE.

2.3. Các Dịch vụ Hạ tầng Khác
Elastic Cloud Server (ECS): Dịch vụ máy ảo, đóng vai trò là worker nodes cho CCE Standard.

Elastic Volume Service (EVS): Block storage, được dùng làm persistent volumes cho container thông qua plugin Everest.

Elastic Load Balance (ELB): Cung cấp khả năng cân bằng tải cho các service Kubernetes (Service type: LoadBalancer).

Virtual Private Cloud (VPC): Cung cấp mạng riêng ảo, là nền tảng networking cho tất cả các dịch vụ container.

Object Storage Service (OBS): Dịch vụ lưu trữ object, có thể được gắn (mount) trực tiếp vào container để lưu trữ dữ liệu phi cấu trúc.

3. Container-based Cloud Migration Solution
Huawei Cloud cung cấp một lộ trình và bộ công cụ toàn diện để di chuyển ứng dụng lên cloud bằng cách sử dụng công nghệ container.

3.1. Tổng quan về Giải pháp
Giải pháp này tập trung vào việc "container hóa" (containerization) các ứng dụng hiện có (thường chạy trên máy vật lý hoặc VM on-premise) và di chuyển chúng lên các dịch vụ container của Huawei Cloud (chủ yếu là CCE). Quá trình này giúp hiện đại hóa ứng dụng, tăng tính linh hoạt và tối ưu hóa chi phí.

3.2. Quy trình Di chuyển (Migration Process)
Bước 1: Đánh giá và Phân tích (Assessment & Analysis)
Mục tiêu: Hiểu rõ ứng dụng và phụ thuộc.

Hoạt động:

Sử dụng công cụ CTS (Cloud Transfer Service) hoặc các tool third-party để khám phá và đánh giá ứng dụng trên môi trường nguồn.

Phân tích các phụ thuộc (dependency) giữa các ứng dụng, thành phần.

Xác định ứng dụng nào phù hợp để container hóa (ví dụ: ứng dụng stateless thường phù hợp hơn ứng dụng stateful phức tạp).

Lập kế hoạch kiến trúc mạng, lưu trữ và bảo mật trên cloud.

Bước 2: Đóng gói và Container hóa (Containerization)
Mục tiêu: Tạo Docker image từ ứng dụng.

Hoạt động:

Với ứng dụng đã có source code: Viết Dockerfile để build image.

Với ứng dụng không có source code (legacy): Sử dụng công cụ KubeOS (của Huawei) hoặc Craft để phân tích ứng dụng đang chạy trên VM và tự động tạo ra Docker image. Đây là bước then chốt để số hóa ứng dụng legacy.

Bước 3: Di chuyển Dữ liệu (Data Migration)
Mục tiêu: Di chuyển dữ liệu ứng dụng sang cloud một cách an toàn.

Hoạt động:

Sử dụng dịch vụ OBS + Data Ingestion Toolkit để transfer lượng lớn dữ liệu qua internet hoặc dịch vụ DES (Disk Export Service) để chuyển dữ liệu bằng ổ cứng vật lý.

Đối với cơ sở dữ liệu, sử dụng dịch vụ Data Replication Service (DRS) để đồng bộ hóa liên tục từ on-premise database sang cloud database (như RDS) với downtime tối thiểu.

Bước 4: Triển khai và Kiểm thử (Deployment & Validation)
Mục tiêu: Chạy ứng dụng trên Huawei Cloud và đảm bảo nó hoạt động chính xác.

Hoạt động:

Đẩy image lên SWR.

Viết file cấu hình Kubernetes (YAML) để triển khai ứng dụng trên CCE (tạo Deployment, Service, Ingress, v.v.).

Cấu hình ELB và VPC.

Thiết lập persistent storage từ EVS hoặc SFS.

Chạy kiểm thử kỹ lưỡng về chức năng, hiệu năng và bảo mật.

Bước 5: Cắt chuyển và Tối ưu hóa (Cut-over & Optimization)
Mục tiêu: Chuyển hướng traffic sang môi trường mới và tối ưu.

Hoạt động:

Cập nhật cấu hình DNS để trỏ đến ELB của Huawei Cloud.

Giám sát chặt chẽ ứng dụng sau cắt chuyển.

Thiết lập các chính sách HPA để tự động mở rộng quy mô ứng dụng.

Tối ưu hóa cấu hình tài nguyên (CPU, memory) cho container để giảm chi phí.

3.3. Các Công cụ và Dịch vụ Hỗ trợ
Cloud Transfer Service (CTS): Công cụ đánh giá và di chuyển.

KubeOS/Craft: Công cụ container hóa ứng dụng tự động.

Data Replication Service (DRS): Đồng bộ cơ sở dữ liệu.

Object Storage Service (OBS) & Data Ingestion Toolkit: Di chuyển dữ liệu số lượng lớn.

Cloud Enterprise Network (CEN) & Direct Connect (DC): Thiết lập kết nối mạng riêng tốc độ cao, độ trễ thấp giữa datacenter on-premise và Huawei Cloud, rất quan trọng cho quá trình di chuyển.

3.4. Lợi ích
Tăng tốc Time-to-Market: Triển khai ứng dụng nhanh hơn với container.

Giảm chi phí: Tối ưu hóa việc sử dụng tài nguyên với tự động scaling và mô hình pay-as-you-go.

Tính linh hoạt và Khả năng mở rộng: Dễ dàng mở rộng quy mô ứng dụng để đáp ứng nhu cầu kinh doanh.

Hiện đại hóa ứng dụng: Đặt nền móng cho việc chuyển đổi sang kiến trúc microservices và các công nghệ cloud-native khác.

