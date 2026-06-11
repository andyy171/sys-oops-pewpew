# Tổng quan

- OpenStack là một nền tảng mã nguồn mở dùng để xây dựng và vận hành hệ thống cloud theo mô hình Infrastructure as a Service (IaaS). Nó cho phép tổ chức triển khai một môi trường cloud riêng (private cloud) hoặc hybrid cloud với khả năng quản lý tài nguyên compute, storage và networking thông qua các API và dashboard.
- Về bản chất, OpenStack không phải là một phần mềm đơn lẻ mà là một tập hợp nhiều dịch vụ (services) phối hợp với nhau để tạo thành một hệ thống cloud hoàn chỉnh. Mỗi service đảm nhiệm một vai trò riêng biệt, giao tiếp với nhau thông qua API và message queue.
- OpenStack thường được sử dụng trong các môi trường yêu cầu mức độ kiểm soát cao, tùy biến linh hoạt và tối ưu chi phí hạ tầng ở quy mô lớn.

## Reading Map

- [Core architecture](./01-core-fundamentals/01-architectures.md)
- [Certified OpenStack Administrator knowledge path](./06-certification/certified-openstack-administrator/overview.md)
- [OpenStack API and automation workflow](./02-operations/api-and-automation-workflow.md)
- [OpenStack security](./03-security/overview.md)
- [Common commands](./02-operations/common-commands.md)
- [Kolla-Ansible all-in-one lab](./02-operations/01-deployment/kolla-ansible-all-in-one-lab.md)
- [Client debug](./04-troubleshooting/openstack-client-debug.md)

## Knowledge Base Contract

OpenStack trong vault này được tổ chức theo năng lực vận hành, không theo thứ tự chương sách:

```text
openstack/
├── 01-core-fundamentals/    # architecture, control plane model, core service concepts
├── 02-operations/           # CLI/API workflow, deployment, backup, migration, common commands
├── 03-security/             # security review, config protection, defensive guidance
├── 04-troubleshooting/      # symptom/evidence based debug notes
├── 05-labs/                 # lab setup and hands-on practice
└── 06-certification/        # COA learning path and exam-oriented practice
```

`Certified OpenStack Administrator Study Guide 2nd` được dùng làm blueprint để thiết kế learning path COA và bổ sung kiến thức vào canonical notes. Vault không duy trì source digest, audit hay coverage folder riêng; phần nào có giá trị học/vận hành sẽ được viết lại vào đúng note chính.

## COA-Based Learning Flow

| Năng lực | Nên học ở đâu | Điều cần trả lời được |
|---|---|---|
| API, CLI, Horizon, RC file | `02-operations/api-and-automation-workflow.md`, `06-certification/.../01-lab-cli-horizon-keystone-glance.md` | Request đi qua Keystone token, endpoint và service API như thế nào? |
| Identity | `01-core-fundamentals/services/keystone.md` | Domain, project, user, role, token, catalog và endpoint khác nhau ra sao? |
| Image | `01-core-fundamentals/services/glance.md` | Image lifecycle, backend, metadata và boot source ảnh hưởng VM thế nào? |
| Networking | `01-core-fundamentals/services/neutron.md` | Network, subnet, router, port, floating IP và security group phối hợp thế nào? |
| Compute | `01-core-fundamentals/services/nova.md` | Nova API, scheduler, compute, Placement và hypervisor phối hợp để spawn VM ra sao? |
| Object/block storage | `01-core-fundamentals/services/swift.md`, `01-core-fundamentals/services/cinder.md` | Object/container khác volume/snapshot/backup như thế nào? |
| Troubleshooting | `04-troubleshooting/`, `06-certification/.../03-troubleshooting-heat-and-admin-checklist.md` | Khi lỗi, đọc service status, log, DB, RabbitMQ, network/compute/storage evidence theo thứ tự nào? |

## Kiến trúc tổng thể 
- Một hệ thống OpenStack điển hình bao gồm các thành phần chính:
    - **Controller node:** quản lý control plane, API, scheduler
    - **Compute node:** nơi chạy các máy ảo
    - **Storage node:** cung cấp lưu trữ (block, object)
    - **Network node:**xử lý routing, NAT, load balancing
- Các thành phần này có thể được triển khai tách biệt hoặc theo mô hình hyper-converged tùy theo thiết kế hệ thống.

## Các dịch vụ
### I. Nhóm Dịch Vụ Cốt Lõi (Core Services)
Đây là các dịch vụ bắt buộc phải có để một cụm Cloud có thể vận hành cơ bản.

- **Keystone (Identity Service)**: Quản lý định danh, xác thực (Authentication) và phân quyền (Authorization). Là "cửa ngõ" đầu tiên của mọi yêu cầu.

- **Nova (Compute Service)**: Quản lý vòng đời máy ảo (tạo, xóa, lập lịch). Làm việc trực tiếp với Hypervisor (KVM, VMware...).

- **Neutron (Networking Service)**: Cung cấp kết nối mạng (L2, L3, Floating IP, Security Groups, VPN, LBaaS).

- **Glance (Image Service)**: Lưu trữ và quản lý các bản đóng gói hệ điều hành (Images) để boot máy ảo.

- **Placement (Resource Placement)**: Theo dõi và thống kê việc tiêu thụ tài nguyên (CPU, RAM, Disk) để hỗ trợ Nova lập lịch chính xác.

### II. Nhóm Dịch Vụ Lưu Trữ (Storage Services)
Phân tách rõ ràng giữa lưu trữ dạng khối, dạng tệp và dạng đối tượng.

- **Cinder (Block Storage)**: Cung cấp các ổ đĩa ảo (Volumes) gắn vào máy ảo. Phù hợp cho Database, hiệu năng cao.

- **Swift (Object Storage)**: Lưu trữ dữ liệu phi cấu trúc (giống S3). Khả năng mở rộng cực lớn, phù hợp cho Backup, Media.

- **Manila (Shared File Systems)**: Cung cấp các hệ thống tệp chia sẻ (NFS, CIFS) cho phép nhiều instance truy cập đồng thời.

### III. Nhóm Giao Diện & Điều Phối (Management & Orchestration)
- **Horizon (Dashboard)**: Giao diện Web (UI) để người dùng và quản trị viên thao tác trực quan.

- **Heat (Orchestration)**: Triển khai hạ tầng dưới dạng mã (IaC) thông qua các template YAML.

- **Senlin (Clustering Service)**: Quản lý các nhóm tài nguyên giống nhau và thực hiện tự động co giãn (Autoscaling).

- **Mistral (Workflow Service)**: Thiết kế và vận hành các quy trình công việc (workflows) tự động hóa phức tạp.

### IV. Nhóm Dịch Vụ Bổ Trợ & Nâng Cao (Advanced Services)
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

### V. Nhóm Giám Sát & Cảnh Báo (Monitoring & Telemetry)
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

### VPC
- Trong các nền tảng public cloud, khái niệm VPC (Virtual Private Cloud) đóng vai trò trung tâm trong việc tổ chức hạ tầng. VPC không chỉ là một mạng ảo, mà là một không gian cô lập logic nơi toàn bộ tài nguyên như compute, network và security được định nghĩa và kiểm soát. Khi tiếp cận OpenStack, một sai lầm phổ biến là tìm kiếm một thực thể tương đương trực tiếp với VPC, trong khi thực tế OpenStack không cung cấp một object “VPC” duy nhất mà xây dựng cùng chức năng này thông qua nhiều thành phần kết hợp lại.
- Trong OpenStack, ranh giới cô lập không nằm ở network mà nằm ở Project (tenant). Project là đơn vị tổ chức tài nguyên, nơi tất cả các thành phần như instance, network, volume và security policy được gắn vào. Mỗi project được cô lập với project khác ở cả cấp tài nguyên và quyền truy cập, tạo thành một boundary logic tương đương với VPC trong các hệ thống public cloud. Tuy nhiên, khác với VPC là một abstraction hoàn chỉnh, Project chỉ là lớp cô lập cơ bản; để đạt được đầy đủ chức năng như một VPC, cần kết hợp thêm các thành phần khác trong hệ sinh thái OpenStack.

- Một môi trường tương đương VPC trong OpenStack được hình thành bằng cách kết hợp Project với các thành phần mạng của Neutron. Network trong OpenStack đóng vai trò tương tự subnet, nơi xác định dải IP và phạm vi broadcast. Router chịu trách nhiệm kết nối các network nội bộ với nhau và với external network, đóng vai trò tương tự route table và internet gateway trong public cloud. External network cung cấp khả năng truy cập ra bên ngoài, trong khi security group kiểm soát lưu lượng vào ra ở mức instance. Khi các thành phần này được cấu hình đầy đủ trong phạm vi một Project, hệ thống đạt được một môi trường cô lập hoàn chỉnh với đầy đủ khả năng routing, addressing và security — tương đương với một VPC.

- Điểm khác biệt quan trọng giữa OpenStack và các nền tảng như AWS hoặc GCP nằm ở mức độ abstraction. Trong public cloud, VPC là một đối tượng cấp cao, nơi nhiều chi tiết được ẩn đi và tự động cấu hình. Người dùng chỉ cần định nghĩa subnet, route và security rule là có thể sử dụng ngay. Ngược lại, OpenStack cung cấp các building blocks ở mức thấp hơn, yêu cầu người vận hành phải tự thiết kế và lắp ghép các thành phần này để tạo thành một môi trường hoàn chỉnh. Điều này làm tăng độ phức tạp ban đầu, nhưng đổi lại mang lại khả năng kiểm soát sâu hơn đối với network topology, routing behavior và security policy.

- Cách tiếp cận này phản ánh rõ bản chất của private cloud: thay vì tiêu thụ một dịch vụ đã được chuẩn hoá, người vận hành sở hữu toàn bộ hạ tầng và chịu trách nhiệm thiết kế kiến trúc. Project trong OpenStack vì vậy không chỉ là một đơn vị tổ chức tài nguyên, mà là điểm bắt đầu của mọi quyết định về isolation, multi-tenancy và security. Việc thiết kế hệ thống với nhiều project khác nhau cho phép tách biệt workload, môi trường (dev, staging, production) hoặc tenant, tương tự như việc sử dụng nhiều VPC trong public cloud.

- Tuy nhiên, việc sử dụng Project như một VPC không phải lúc nào cũng đủ cho các hệ thống phức tạp. Trong các môi trường multi-tenant lớn hoặc yêu cầu phân tách nhiều lớp, cần kết hợp thêm các cơ chế như RBAC, domain hoặc network segmentation nâng cao để đạt được mức độ cô lập mong muốn. Điều này cho thấy rằng OpenStack cung cấp nền tảng linh hoạt, nhưng trách nhiệm thiết kế luôn thuộc về người vận hành.

- Một điểm cần lưu ý là sự khác biệt về trải nghiệm vận hành. Public cloud cung cấp một môi trường managed, nơi nhiều vấn đề về network và routing đã được xử lý phía sau. Trong OpenStack, mọi cấu hình đều minh bạch và cần được thiết lập thủ công, từ việc gắn router, cấu hình external network cho đến kiểm soát security group. Điều này khiến việc triển khai ban đầu phức tạp hơn, nhưng đồng thời giúp người vận hành hiểu rõ và kiểm soát toàn bộ luồng dữ liệu trong hệ thống.

> Tóm lại, OpenStack không cung cấp một VPC theo nghĩa truyền thống, nhưng cho phép xây dựng một môi trường tương đương thông qua sự kết hợp giữa Project và các thành phần mạng. Việc hiểu đúng mối quan hệ này giúp chuyển đổi tư duy từ việc “tìm kiếm feature” sang “thiết kế hệ thống”, điều cần thiết khi làm việc với private cloud.
