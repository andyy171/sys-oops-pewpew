# 5 microservices architecture

Kiến trúc Microservices trên Huawei Cloud
1. Sự Phát triển của Kiến trúc Ứng dụng Doanh nghiệp
Lộ trình phát triển kiến trúc ứng dụng của doanh nghiệp thường trải qua các giai đoạn chính sau, phản ánh nhu cầu ngày càng cao về tính linh hoạt, khả năng mở rộng và tốc độ phát triển.

1.1. Kiến trúc Monolithic (Nguyên khối)
Đặc điểm: Toàn bộ ứng dụng (giao diện người dùng, logic nghiệp vụ, truy cập cơ sở dữ liệu) được xây dựng, đóng gói và triển khai như một đơn vị duy nhất.

Ưu điểm:

Phát triển và triển khai đơn giản cho các ứng dụng nhỏ.

Dễ dàng debug và test.

Nhược điểm:

Tính phức tạp gia tăng: Khi codebase phình to, việc hiểu và sửa đổi ứng dụng trở nên khó khăn.

Khả năng mở rộng kém: Buộc phải mở rộng toàn bộ ứng dụng ngay cả khi chỉ một module nhỏ bị nghẽn.

Ứng dụng công nghệ cứng nhắc: Khó áp dụng các framework và ngôn ngữ mới cho từng phần.

Độ tin cậy: Một lỗi nhỏ trong module có thể làm sập toàn bộ hệ thống.

Tốc độ phát hành chậm: Mọi thay đổi dù nhỏ cũng yêu cầu build và deploy lại cả ứng dụng.

1.2. Kiến trúc SOA (Service-Oriented Architecture - Kiến trúc Hướng dịch vụ)
Đặc điểm: Ứng dụng được chia thành các dịch vụ (service) có thể tái sử dụng, giao tiếp với nhau thông qua các giao thức như SOAP/WS-* và thường sử dụng một Enterprise Service Bus (ESB) làm trung tâm.

Ưu điểm:

Tái sử dụng dịch vụ tốt hơn.

Tích hợp các hệ thống nghiệp vụ khác nhau dễ dàng hơn.

Nhược điểm:

Độ trễ cao: ESB có thể trở thành nút thắt cổ chai.

Phức tạp: Các tiêu chuẩn WS-* nặng nề và phức tạp.

Triển khai và vận hành tốn kém.

1.3. Kiến trúc Microservices
Đặc điểm: Ứng dụng được chia thành tập hợp các dịch vụ rất nhỏ, độc lập và được phân phối.

Mỗi dịch vụ chạy trong một tiến trình riêng biệt và quản lý cơ sở dữ liệu riêng.

Giao tiếp với nhau thông qua các API nhẹ (thường là RESTful API hoặc gRPC).

Được triển khai độc lập và tự động hóa hoàn toàn.

Ưu điểm:

Triển khai độc lập & phát hành nhanh chóng: Mỗi team có thể phát triển, triển khai và mở rộng dịch vụ của mình một cách độc lập.

Tính linh hoạt công nghệ: Mỗi dịch vụ có thể sử dụng ngôn ngữ lập trình, framework và cơ sở dữ liệu phù hợp nhất.

Khả năng mở rộng tốt: Có thể mở rộng từng dịch vụ cụ thể dựa trên nhu cầu thực tế.

Khả năng phục hồi: Lỗi của một dịch vụ được cô lập và không làm sập toàn bộ hệ thống.

Thách thức:

Độ phức tạp trong vận hành: Số lượng service lớn đòi hỏi tự động hóa triển khai, giám sát, khắc phục sự cố (cần DevOps và container).

Theo dõi và giám sát phân tán: Khó khăn trong việc debug và theo dõi luồng request qua nhiều service.

Quản lý dữ liệu phân tán: Giao dịch phân tán (distributed transactions) trở nên phức tạp.

1.4. Kiến trúc Cloud-Native (Sinh ra trên Đám mây)
Đặc điểm: Đây là bước tiến hóa tiếp theo, tận dụng tối đa các lợi thế của mô hình điện toán đám mây. Microservices là nền tảng của kiến trúc Cloud-Native.

Các trụ cột chính:

Container: Đóng gói và cách ly từng dịch vụ (sử dụng Docker, CCE).

Dynamic Orchestration: Điều phối và quản lý vòng đời container tự động (sử dụng Kubernetes).

DevOps & CI/CD: Văn hóa và tập hợp các thực nghiệm giúp tự động hóa quy trình phát triển và vận hành.

Service Mesh: Kiến trúc cho phép quản lý giao tiếp giữa các service (traffic management, security, observability) một cách tách biệt mà không cần sửa code (sử dụng Istio).

2. Các Framework Microservices Điển hình
Có nhiều framework và bộ công cụ được sử dụng để xây dựng và quản lý các ứng dụng microservices.

2.1. Spring Cloud
Mô tả: Một bộ công cụ giúp xây dựng các mẫu pattern phổ biến trong microservices (như configuration management, service discovery, circuit breaker) trên nền tảng Spring Boot.

Ưu điểm:

Hệ sinh thái lớn, cộng đồng hỗ trợ mạnh.

Tích hợp dễ dàng với các ứng dụng Java/Spring hiện có.

Cung cấp giải pháp cho hầu hết các vấn đề phổ biến của microservices.

Các thành phần chính: Spring Cloud Netflix (Eureka, Hystrix, Zuul), Spring Cloud Config, Spring Cloud Gateway, Spring Cloud Sleuth.

2.2. Apache ServiceComb
Mô tả: Một framework microservices mã nguồn mở, ban đầu được phát triển bởi Huawei và sau đó được hiến tặng cho Apache Software Foundation.

Ưu điểm:

Hiệu suất cao, hỗ trợ đa ngôn ngữ (Java, Go).

Cung cấp một bộ công cụ toàn diện từ SDK đến các công cụ vận hành.

Tích hợp mạnh mẽ với hệ sinh thái Huawei Cloud.

Các thành phần chính:

ServiceCenter: Service registry và discovery.

Java/Go Chassis: SDK để phát triển các dịch vụ.

Hỗ trợ sẵn các pattern như circuit breaker, load balancing, distributed tracing.

2.3. Huawei Cloud Microservice Engine (MSE)
Mô tả: Đây không hẳn là một framework mà là một dịch vụ được quản lý hoàn toàn (fully-managed) trên Huawei Cloud, cung cấp các thành phần cốt lõi để vận hành microservices.

Ưu điểm: Không cần tự triển khai và bảo trì các thành phần phức tạp như registry, config center. Huawei Cloud lo phần high availability, scaling, và bảo mật.

Hỗ trợ đa Framework: MSE có thể phục vụ các dịch vụ được phát triển bằng nhiều framework khác nhau:

Spring Cloud: Dịch vụ đăng ký với MSE thay vì chạy Eureka server riêng.

Apache ServiceComb: Dịch vụ đăng ký với ServiceCenter được quản lý bởi MSE.

Dubbo: Một framework RPC nổi tiếng khác của Java.

Service Mesh: MSE cung cấp một control plane cho service mesh dựa trên Istio.

2.4. So sánh và Lựa chọn
Framework / Dịch vụ	Ưu điểm chính	Phù hợp nhất với
Spring Cloud	Hệ sinh thái lớn, phổ biến	Ứng dụng Java/Spring hiện có, team đã quen với Spring.
Apache ServiceComb	Hiệu năng cao, đa ngôn ngữ	Dự án mới, cần hiệu năng tối ưu, tích hợp sâu với Huawei Cloud.
Huawei Cloud MSE	Managed service, không vận hành	Mọi framework, team muốn tập trung vào nghiệp vụ thay vì vận hành middleware.
3. Huawei Cloud ServiceStage
ServiceStage là nền tảng ứng dụng (Application Platform as a Service - aPaaS) toàn diện của Huawei Cloud, được thiết kế đặc biệt để hỗ trợ phát triển, triển khai, vận hành và quản lý vòng đời ứng dụng theo kiến trúc microservices và cloud-native.

3.1. Tổng quan
ServiceStage cung cấp một môi trường thống nhất để tích hợp các dịch vụ IaaS (như CCE, ECS), PaaS (như MSE, RDS, ELB) và các công cụ (như Git, Jenkins) lại với nhau, tạo thành một nền tảng end-to-end cho ứng dụng.

3.2. Các Tính năng & Thành phần Chính
a. Phát triển và Triển khai (Development & Deployment)
Hỗ trợ đa Môi trường: Tạo và quản lý nhiều môi trường (dev, test, staging, prod) một cách dễ dàng.

Triển khai Linh hoạt: Hỗ trợ nhiều hình thức triển khai:

Triển khai dựa trên Container: Từ image trong SWR lên cụm CCE.

Triển khai dựa trên VM: Triển khai ứng dụng lên ECS.

Triển khai Serverless: Triển khai ứng dụng không máy chủ lên CCI.

CI/CD tích hợp: Cung cấp pipeline CI/CD tích hợp sẵn, kết nối với mã nguồn từ Git, build tự động, và triển khai với các chiến lược canary/blue-green.

b. Điều phối và Quản lý Dịch vụ (Service Orchestration & Management)
Service Registry & Discovery: Tích hợp sâu với Microservice Engine (MSE) để cung cấp service discovery cho các ứng dụng Spring Cloud, ServiceComb, Dubbo.

Quản lý Cấu hình Tập trung: Quản lý cấu hình ứng dụng cho tất cả các môi trường, hỗ trợ cập nhật cấu hình động mà không cần khởi động lại ứng dụng.

Quản lý Traffic và Resilience:

Điều phối vi mô (Micro-granularity Traffic Management): Cho phép điều hướng traffic giữa các phiên bản dịch vụ dựa trên tỷ lệ, content,...

Circuit Breaker & Rate Limiting: Tự động ngắt kết nối đến các dịch vụ lỗi và giới hạn tỷ lệ request để bảo vệ hệ thống.

Distributed Tracing: Thu thập và hiển thị chi tiết các log, metric và trace từ tất cả các service, giúp dễ dàng giám sát và debug các vấn đề trong kiến trúc phân tán.

c. Service Mesh
Tích hợp Service Mesh: ServiceStage cung cấp khả năng quản lý service mesh dựa trên Istio thông qua MSE.

Lợi ích:

Tách biệt mối quan tâm: Các vấn đề cross-cutting (như security, observability, traffic control) được tách khỏi code nghiệp vụ.

Hỗ trợ đa ngôn ngữ: Dễ dàng quản lý các dịch vụ được viết bằng nhiều ngôn ngữ khác nhau.

Kiểm soát traffic chi tiết: Cấu hình canary release, A/B testing, fault injection một cách trực quan.

d. Quan sát và Vận hành (Observability & Ops)
Giám sát Tổng thể: Tích hợp với Application Performance Management (APM) của Huawei Cloud để cung cấp cái nhìn toàn diện về hiệu năng ứng dụng (thời gian phản hồi, tỷ lệ lỗi, số lượt gọi).

Cảnh báo Thông minh: Thiết lập các ngưỡng cảnh báo dựa trên metric và log, gửi thông báo qua SMS, email, hoặc tích hợp với các hệ thống khác.

3.3. Lợi ích khi sử dụng ServiceStage
Tăng tốc Time-to-Market: Tự động hóa toàn bộ quy trình từ code đến production.

Giảm độ phức tạp: Quản lý thống nhất tất cả các dịch vụ và thành phần ứng dụng trên một nền tảng duy nhất.

Đảm bảo Độ tin cậy: Các tính năng resilience, scaling tự động và giám sát giúp ứng dụng luôn ổn định.

Tiết kiệm Chi phí: Tối ưu hóa việc sử dụng tài nguyên và giảm thiểu công sức vận hành nhờ các dịch vụ được quản lý hoàn toàn.

3.4. Use Case Điển hình
Một doanh nghiệp muốn chuyển đổi hệ thống core banking monolithic sang kiến trúc microservices:

Phát triển: Các team phát triển các dịch vụ độc lập (ví dụ: user-service, account-service, transaction-service) sử dụng Spring Cloud.

Đăng ký & Quản lý: Tất cả dịch vụ đăng ký và được quản lý bởi Microservice Engine (MSE) trên ServiceStage.

Triển khai: ServiceStage tự động build code từ Git và triển khai các dịch vụ dưới dạng container lên CCE.

Quan sát: APM và distributed tracing của ServiceStage giúp theo dõi hiệu năng của từng giao dịch xuyên suốt các service.

Quản lý Traffic: Khi ra mắt tính năng mới, họ sử dụng tính năng canary release của ServiceStage để đưa traffic một cách từ từ đến phiên bản mới, đảm bảo an toàn.
