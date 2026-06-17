# Tổng quan về Cloud Computing ( Điện toán đám mây)
- Cloud Computing là một mô hình cho phép truy cập mạng mọi lúc, mọi nơi, thuận tiện và theo nhu cầu vào một kho tài nguyên điện toán chung có thể cấu hình được (ví dụ: mạng, máy chủ, lưu trữ, ứng dụng và dịch vụ). Những tài nguyên này có thể được thiết lập nhanh chóng và giải phóng với tối thiểu nỗ lực quản lý hoặc sự tương tác với nhà cung cấp dịch vụ.
- Các đặc điểm chính :
    - On-demand self-service (Tự phục vụ theo nhu cầu): Người dùng có thể tự thiết lập tài nguyên (như giờ chạy server, dung lượng lưu trữ) mà không cần gọi điện nhờ nhân viên kỹ thuật của nhà cung cấp can thiệp.
    - Broad network access (Truy cập mạng rộng rãi): Tài nguyên phải luôn sẵn sàng thông qua mạng Internet và sử dụng được trên nhiều thiết bị khác nhau (điện thoại, laptop, máy tính bảng).
    - Resource pooling (Dùng chung tài nguyên): Tài nguyên của nhà cung cấp được gom lại để phục vụ nhiều người dùng khác nhau. Bạn không biết chính xác dữ liệu mình nằm ở cái máy chủ vật lý nào, nhưng nó vẫn luôn ở đó cho bạn.
    - Rapid elasticity (Khả năng co giãn nhanh chóng): Có thể tăng hoặc giảm tài nguyên ngay lập tức tùy theo nhu cầu. Hệ thống có vẻ như "vô hạn" đối với người dùng.
    - Measured service (Dịch vụ định lượng): Việc sử dụng tài nguyên được giám sát, kiểm soát và báo cáo minh bạch. Bạn dùng bao nhiêu, hệ thống đo lường và tính tiền bấy nhiêu (giống như hóa đơn điện).

## Các mô hình dịch vụ
1. IaaS 
- Cung cấp cơ sở hạ tầng mạng, lưu trữ và máy chủ ảo. Khách hàng có toàn quyền kiểm soát và quản lý hệ điều hành, ứng dụng và dữ liệu của họ.

2. PaaS 
- Cung cấp một nền tảng để phát triển, chạy và quản lý ứng dụng mà không cần quản lý cơ sở hạ tầng.
> Khách hàng sử dụng nền tàng để có thể lập trình và chạy ứng dụng, nhà cung cấp không chỉ quản lý mã nguồn mà còn cả dữ liệu của ứng dụng 

3. SaaS 
- Cung cấp các ứng dụng phần mềm sẵn có thông qua internet, chẳng hạn như email hoặc CRM, cho phép người dùng truy cập và sử dụng mà không cần cài đặt hay quản lý. 
> Khách hàng chỉ sử dụng phần mềm , không cần quản lý kỹ thuật

## Các mô hình triển khai 

### 1. Public Cloud 
- Dịch vụ đám mây được cung cấp bởi bên thứ ba và chia sẻ cho nhiều người dùng qua internet.
- Ưu điểm lớn là triển khai nhanh, dễ scale và không cần đầu tư ban đầu.
- Tuy nhiên, khi hệ thống phát triển, public cloud có thể gặp các vấn đề như chi phí tăng cao do tính theo usage, khó dự đoán ngân sách, và hiệu năng không ổn định do môi trường multi-tenant.

### 2. Private Cloud 
- Dịch vụ đám mây dành riêng cho một tổ chức và được quản lý nội bộ hoặc bởi bên thứ ba.
- Cho phép kiểm soát hoàn toàn hạ tầng (compute, storage, network), tối ưu theo workload cụ thể và đảm bảo tốt hơn về bảo mật, tuân thủ.
- Private cloud thường trở nên hiệu quả hơn về chi phí khi hệ thống đạt quy mô đủ lớn và có workload ổn định.
- Nhược điểm truyền thống là chi phí đầu tư ban đầu cao và yêu cầu vận hành phức tạp, tuy nhiên các mô hình private cloud on-demand hiện đại đang giảm đáng kể rào cản này.

### 3. Hybird Cloud 
- Kết hợp giữa đám mây công cộng và đám mây riêng, cho phép dữ liệu và ứng dụng được chia sẻ giữa chúng.
=> Đây là mô hình thực tế phổ biến, tận dụng public cloud cho các workload linh hoạt và private cloud cho các workload ổn định hoặc nhạy cảm.
#### Edge Computing (Điện toán biên)
- Edge Computing là mô hình đưa tài nguyên tính toán (compute, storage, networking) đến gần nơi dữ liệu được tạo ra hoặc nơi người dùng truy cập, thay vì xử lý hoàn toàn tại các data center tập trung như trong mô hình cloud truyền thống.
- Về bản chất, edge computing không phải là một mô hình thay thế cloud mà là sự mở rộng của kiến trúc cloud, nhằm giải quyết các hạn chế như độ trễ cao (latency) và sự phụ thuộc hoàn toàn vào kết nối mạng. Bằng cách xử lý dữ liệu tại “biên” (edge), hệ thống có thể phản hồi nhanh hơn và vẫn hoạt động ngay cả khi kết nối đến cloud trung tâm bị gián đoạn.
- Edge computing thường được xem là một phần của kiến trúc hybrid cloud, trong đó hệ thống được phân tán thành nhiều lớp:
    - Cloud trung tâm (centralized cloud) để xử lý và lưu trữ quy mô lớn
    - Edge nodes đặt gần người dùng hoặc thiết bị để xử lý nhanh
    - Hạ tầng on-premise phục vụ các nhu cầu nội bộ hoặc đặc thù
- Một điểm quan trọng là các nhà cung cấp cloud lớn cũng đang đưa mô hình edge vào sản phẩm của mình, bằng cách triển khai hạ tầng cloud ngay tại on-premise của khách hàng. Điều này cho thấy xu hướng “đưa cloud đến gần người dùng” thay vì chỉ tập trung tại các data center lớn.
- Tuy nhiên, edge computing không phù hợp với mọi hệ thống. Việc triển khai edge đòi hỏi hệ thống đã có mức độ trưởng thành nhất định, như đã container hóa ứng dụng, có CI/CD, tự động hóa và khả năng quản lý hạ tầng phân tán. Nếu không, edge có thể làm tăng độ phức tạp thay vì mang lại lợi ích.
- Edge computing đặc biệt phù hợp trong các trường hợp yêu cầu độ trễ thấp, xử lý dữ liệu tại chỗ (data locality), hoặc các hệ thống không thể phụ thuộc hoàn toàn vào kết nối internet. Ngược lại, với các hệ thống đơn giản hoặc chưa có yêu cầu rõ ràng, việc sử dụng edge chỉ vì xu hướng có thể dẫn đến lãng phí và khó vận hành.
- Có thể hiểu một cách tổng quát:
    - Cloud tập trung vào tính linh hoạt và mở rộng
    - Private cloud tập trung vào kiểm soát và tối ưu
    - Edge computing tập trung vào việc đặt tài nguyên đúng vị trí để đạt hiệu quả tốt nhất
### 4. Community Cloud
- Hạ tầng đám mây được chia sẻ giữa nhiều tổ chức có cùng mối quan tâm chung như yêu cầu về bảo mật, tuân thủ, hoặc lĩnh vực hoạt động

### Xu hướng thực tế hiện tại 
- Một xu hướng đáng chú ý là việc các doanh nghiệp chuyển workload từ public cloud về private cloud sau một thời gian sử dụng.
- Nguyên nhân chính bao gồm chi phí tăng theo scale, khó kiểm soát billing, yêu cầu cao về bảo mật và nhu cầu tối ưu hiệu năng cho workload cụ thể.
- Điều này không có nghĩa public cloud kém, mà phản ánh việc mỗi mô hình phù hợp với từng giai đoạn phát triển khác nhau của hệ thống. Ban đầu, public cloud rất phù hợp để thử nghiệm, phát triển và chạy các workload linh hoạt. Khi hệ thống trưởng thành và có nhu cầu ổn định hơn, private cloud có thể mang lại lợi ích về chi phí và hiệu năng tốt hơn.

## Các domain chính
### Compute 
- Compute là thành phần đại diện cho năng lực xử lý của toàn bộ hệ thống, đóng vai trò như bộ não thực hiện các phép tính và chạy logic của ứng dụng. Trong môi trường đám mây, Compute không đơn thuần là một chiếc máy chủ vật lý mà là một tập hợp các tài nguyên được ảo hóa linh hoạt.
- Khi bạn khởi tạo một thực thể tính toán, nhà cung cấp sẽ sử dụng công nghệ ảo hóa (Hypervisor) để phân tách một phần tài nguyên CPU và RAM từ các cụm máy chủ vật lý khổng lồ.
- Trong public cloud, compute thường được tối ưu cho tính linh hoạt và khả năng scale nhanh, trong khi private cloud cho phép tối ưu sâu hơn về hiệu năng và chi phí cho các workload ổn định.

### Storage
- Storage là thành phần chịu trách nhiệm lưu trữ dữ liệu của hệ thống, bao gồm dữ liệu ứng dụng, file, backup và các đối tượng khác.
- Trong môi trường cloud, storage thường được trừu tượng hóa thành các dịch vụ như block storage, object storage và file storage.
- Với public cloud, storage có ưu điểm là gần như không giới hạn và dễ mở rộng, nhưng chi phí có thể tăng đáng kể theo dung lượng và băng thông sử dụng.
- Trong private cloud, storage có thể được tối ưu theo nhu cầu cụ thể (ví dụ: dùng distributed storage như Ceph), giúp kiểm soát chi phí tốt hơn khi hệ thống lớn.

### Database 
- Database là lớp lưu trữ dữ liệu có cấu trúc, phục vụ cho việc truy vấn và xử lý nghiệp vụ của ứng dụng.
- Cloud cung cấp cả database managed (trong PaaS/SaaS) và self-managed (trong IaaS).
- Managed database giúp giảm gánh nặng vận hành nhưng đi kèm với chi phí cao và ít kiểm soát hơn.
- Với các hệ thống lớn hoặc yêu cầu đặc thù, doanh nghiệp có xu hướng chuyển sang self-hosted database trên private cloud để tối ưu hiệu năng và chi phí.

### Networking
- Networking là nền tảng kết nối toàn bộ các thành phần trong hệ thống cloud, bao gồm routing, load balancing, firewall và các cơ chế bảo mật.
- Public cloud cung cấp networking linh hoạt và dễ cấu hình, nhưng thường tính phí cao cho data transfer, đặc biệt là traffic outbound.
- Trong private cloud, doanh nghiệp có thể kiểm soát hoàn toàn network topology và tối ưu chi phí, đặc biệt với các hệ thống có lưu lượng nội bộ lớn.

## Distributed System Fundamentals

### Stateless vs stateful services
### Horizontal scaling
### Service decoupling
### Failure domains
### Eventual consistency
### Idempotent operations
### Retry & backoff strategies
### Leader election (concept)
### Partition tolerance

---

## API-Driven Architecture

### RESTful API principles
### Service endpoints & versioning
### Idempotency in API calls
### Request/response lifecycle
### Microversion concept
### API extension mechanism
### API rate limiting (concept)

---

## Control Plane vs Data Plane

### Definition of control plane
### Definition of data plane
### Interaction between planes
### Isolation between planes
### Failure impact per plane

---

## Multi-Tenancy

### Tenant / project isolation
### Resource quotas
### Security isolation boundaries
### Network isolation (concept)
### Storage isolation (concept)
### Identity isolation

---

## Networking Fundamentals

### L2 vs L3 networking
### Network, subnet, port abstraction
### MAC vs IP addressing
### DHCP concept
### Routing & NAT (SNAT / DNAT)
### Security groups vs firewall
### Overlay vs underlay network
### East-West vs North-South traffic
### Virtual networking concept

---

## Storage Concepts

### Block storage vs object storage vs file storage
### Volume abstraction
### Snapshot concept
### Clone vs copy
### Backend abstraction
### Thin vs thick provisioning
### Consistency groups (concept)
### Data durability & replication (concept)

---

## Image Management Concepts

### Image vs volume
### Image formats (qcow2, raw… - concept only)
### Copy-on-write
### Image caching
### Metadata & properties

---

## Compute Virtualization Concepts

### Hypervisor role
### VM lifecycle (high-level)
### Flavor abstraction
### Ephemeral vs persistent disk
### Live migration (concept)
### Cold migration (concept)
### Resize concept

---

## State & Lifecycle Management

### Resource lifecycle (create → update → delete)
### Desired state vs actual state
### State transitions
### Reconciliation concept
### Orphaned resources

---

## Observability & Telemetry

### Metrics vs logs vs traces
### Monitoring vs alerting
### Health checks
### Audit logs
### Event tracking
### Usage metering (concept)

---

## Security Fundamentals

### Authentication vs authorization
### Identity security
### API security
### Encryption in transit vs at rest
### Secret management (concept)
### Least privilege principle
### Attack surface in distributed systems

---

## Fault Tolerance & High Availability

### Redundancy
### Active-active vs active-passive
### Failure detection
### Failover concept
### Split-brain (concept)
### Graceful degradation

---

## Upgrade & Compatibility Concepts

### API backward compatibility
### Rolling upgrade concept
### Database migration strategy
### Deprecation lifecycle
### Version skew

---

## Resource Abstraction & Virtualization

### Abstracting physical resources
### Pooling resources
### Logical vs physical mapping
### Elasticity concept
### Capacity planning (concept)

---

## Orchestration & Automation

### Declarative vs imperative model
### Desired state management
### Stack concept
### Dependency resolution
### Idempotent automation

---

## Naming, Identification & Metadata

### UUID usage
### Naming conventions
### Resource identification
### Metadata vs tags
### Labeling strategies

---

## Limits, Quotas & Governance

### Resource limits
### Quota enforcement
### Soft vs hard limits
### Policy enforcement
### Governance model

---

## Performance & Scalability Concepts

### Bottlenecks (CPU / network / IO)
### Horizontal vs vertical scaling
### Caching strategies
### Load distribution
### Latency vs throughput tradeoff
