# Tổng quan

- OpenStack là một nền tảng mã nguồn mở dùng để xây dựng và vận hành hệ thống cloud theo mô hình Infrastructure as a Service (IaaS). Nó cho phép tổ chức triển khai một môi trường cloud riêng (private cloud) hoặc hybrid cloud với khả năng quản lý tài nguyên compute, storage và networking thông qua các API và dashboard.
- Về bản chất, OpenStack không phải là một phần mềm đơn lẻ mà là một tập hợp nhiều dịch vụ (services) phối hợp với nhau để tạo thành một hệ thống cloud hoàn chỉnh. Mỗi service đảm nhiệm một vai trò riêng biệt, giao tiếp với nhau thông qua API và message queue.
- OpenStack thường được sử dụng trong các môi trường yêu cầu mức độ kiểm soát cao, tùy biến linh hoạt và tối ưu chi phí hạ tầng ở quy mô lớn.


## Kiến trúc tổng thể 
- Một hệ thống OpenStack điển hình bao gồm các thành phần chính:
    - **Controller node:** quản lý control plane, API, scheduler
    - **Compute node:** nơi chạy các máy ảo
    - **Storage node:** cung cấp lưu trữ (block, object)
    - **Network node:**xử lý routing, NAT, load balancing
- Các thành phần này có thể được triển khai tách biệt hoặc theo mô hình hyper-converged tùy theo thiết kế hệ thống.

## I. Nhóm Dịch Vụ Cốt Lõi (Core Services)
Đây là các dịch vụ bắt buộc phải có để một cụm Cloud có thể vận hành cơ bản.

- **Keystone (Identity Service)**: Quản lý định danh, xác thực (Authentication) và phân quyền (Authorization). Là "cửa ngõ" đầu tiên của mọi yêu cầu.

- **Nova (Compute Service)**: Quản lý vòng đời máy ảo (tạo, xóa, lập lịch). Làm việc trực tiếp với Hypervisor (KVM, VMware...).

- **Neutron (Networking Service)**: Cung cấp kết nối mạng (L2, L3, Floating IP, Security Groups, VPN, LBaaS).

- **Glance (Image Service)**: Lưu trữ và quản lý các bản đóng gói hệ điều hành (Images) để boot máy ảo.

- **Placement (Resource Placement)**: Theo dõi và thống kê việc tiêu thụ tài nguyên (CPU, RAM, Disk) để hỗ trợ Nova lập lịch chính xác.

## II. Nhóm Dịch Vụ Lưu Trữ (Storage Services)
Phân tách rõ ràng giữa lưu trữ dạng khối, dạng tệp và dạng đối tượng.

- **Cinder (Block Storage)**: Cung cấp các ổ đĩa ảo (Volumes) gắn vào máy ảo. Phù hợp cho Database, hiệu năng cao.

- **Swift (Object Storage)**: Lưu trữ dữ liệu phi cấu trúc (giống S3). Khả năng mở rộng cực lớn, phù hợp cho Backup, Media.

- **Manila (Shared File Systems)**: Cung cấp các hệ thống tệp chia sẻ (NFS, CIFS) cho phép nhiều instance truy cập đồng thời.

## III. Nhóm Giao Diện & Điều Phối (Management & Orchestration)
- **Horizon (Dashboard)**: Giao diện Web (UI) để người dùng và quản trị viên thao tác trực quan.

- **Heat (Orchestration)**: Triển khai hạ tầng dưới dạng mã (IaC) thông qua các template YAML.

- **Senlin (Clustering Service)**: Quản lý các nhóm tài nguyên giống nhau và thực hiện tự động co giãn (Autoscaling).

- **Mistral (Workflow Service)**: Thiết kế và vận hành các quy trình công việc (workflows) tự động hóa phức tạp.

## IV. Nhóm Dịch Vụ Bổ Trợ & Nâng Cao (Advanced Services)
- **Magnum (Container Infrastructure)**: Cung cấp các công cụ điều phối container như Kubernetes, Swarm, Mesos trên OpenStack.

- **Zun (Container Service)**: Khác với Magnum (tạo cụm K8s), Zun cho phép bạn chạy các Container đơn lẻ trực tiếp như một tài nguyên của OpenStack mà không cần quản lý máy ảo hay cụm orchestration phức tạp.

- Qinling (Function as a Service - FaaS): Cung cấp mô hình Serverless. Bạn chỉ cần upload code (Python, Node.js...), Qinling sẽ tự động thực thi khi có sự kiện kích hoạt.

- **Trove (Database as a Service)**: Cung cấp và quản lý các hệ quản trị CSDL (MySQL, MongoDB, PostgreSQL) tự động.

- **Designate (DNS as a Service)**: Quản lý các bản ghi tên miền (DNS records) tích hợp trong Cloud.

- **Masakari (High Availability Service)**: Đây là dịch vụ cực kỳ quan trọng cho môi trường Production. Nó tự động phát hiện lỗi của máy ảo hoặc host vật lý và thực hiện di trú (evacuate) máy ảo sang node khác để duy trì dịch vụ.

- **Freezer (Backup, Restore & Disaster Recovery)**: Cung cấp giải pháp sao lưu toàn diện cho dữ liệu máy ảo, file system và cả các database của OpenStack.

- **Karbor (Application Data Protection)**: Bảo vệ dữ liệu ở tầng ứng dụng, giúp thiết lập các chính sách backup/restore theo từng project cụ thể.

- **Octavia (Load Balancer as a Service)**: Dịch vụ cân bằng tải chuyên sâu (thay thế cho LBaaS cũ trong Neutron).

- **Sahara (Data Processing)**: Hỗ trợ triển khai nhanh các cụm xử lý dữ liệu lớn như Hadoop hoặc Spark.

- **Ironic (Bare Metal Provisioning)**: Cho phép quản lý và cài đặt trực tiếp lên các máy chủ vật lý thay vì máy ảo.

- **Barbican (Key Management)**: Lưu trữ bảo mật các khóa, chứng chỉ và mật khẩu (Secrets).

## V. Nhóm Giám Sát & Cảnh Báo (Monitoring & Telemetry)
- **Ceilometer (Telemetry)**: Thu thập các thông số sử dụng (metrics) từ toàn bộ hệ thống.

- **Gnocchi (Resource Indexing)**: Lưu trữ và lập chỉ mục dữ liệu chuỗi thời gian (time-series) từ Ceilometer.

- **Aodh (Alarming)**: Thiết lập các quy tắc cảnh báo (Alarms) dựa trên dữ liệu thu thập được để kích hoạt các hành động tự động.

- **Blazar (Resource Reservation Service)**: Cho phép người dùng đặt chỗ trước tài nguyên (CPU, RAM, hoặc cả Bare Metal) cho một khoảng thời gian trong tương lai. Rất hữu ích cho các dự án cần chạy tính toán lớn vào thời điểm xác định.

- **Vitrage (Root Cause Analysis - RCA)**: Dịch vụ phân tích nguyên nhân gốc rễ. Nó tổng hợp dữ liệu từ nhiều nguồn để đưa ra bức tranh toàn cảnh khi hệ thống gặp sự cố (ví dụ: switch hỏng dẫn đến hàng loạt VM mất kết nối).

### VI. Nhóm Khác (Niche Services)
- **Zaqar (Messaging Service)**: Dịch vụ hàng đợi tin nhắn (Messaging Queue) cho các nhà phát triển ứng dụng Cloud.

- **Murano (Application Catalog)**: Một "chợ" ứng dụng giúp người dùng click-to-deploy các phần mềm phức tạp.

- **Cyborg (Accelerator Management)**: Quản lý các tài nguyên phần cứng đặc thù như GPU, FPGA.

- **Searchlight (Indexing and Search)**: Giúp cải thiện tốc độ tìm kiếm tài nguyên trên Dashboard (Horizon) bằng cách đánh chỉ mục (indexing) dữ liệu từ các dịch vụ khác vào Elasticsearch.

- **Cloudkitty (Rating & Billing)**: Nếu bạn muốn xây dựng hệ thống tính cước (Chargeback/Showback) cho khách hàng hoặc các phòng ban dựa trên tài nguyên họ đã dùng, đây là dịch vụ bạn cần.