# Data Security And Confidential Computing

Bảo mật dữ liệu trong kiến trúc hạ tầng không chỉ là bật encryption. Cần bảo vệ dữ liệu theo cả vòng đời: data at rest, data in transit và data in use. Confidential computing tập trung vào trạng thái khó nhất: dữ liệu đang được xử lý trong memory.

## Data Lifecycle

| Trạng thái | Rủi ro chính | Control thường dùng |
|---|---|---|
| Data at rest | disk mất, storage backend bị truy cập trái phép | encryption at rest, key management, access control |
| Data in transit | sniffing, MITM, route sai trust boundary | TLS, mTLS, private network, segmentation |
| Data in use | plaintext trong memory, compromised host, privileged insider | TEE, attestation, workload isolation |

Distributed storage, replication hoặc erasure coding giúp durability và availability, nhưng không tự đảm bảo confidentiality. Chúng chỉ là một lớp trong defense in depth.

## Trust Boundary

Kiến trúc dữ liệu nhạy cảm phải trả lời:

- ai được tin ở tầng hardware, OS, hypervisor và platform;
- dữ liệu đi qua network segment nào;
- key nằm ở đâu và ai có quyền dùng key;
- workload nào cần isolation mạnh hơn workload thường;
- control nào vẫn hiệu quả khi một lớp bị compromise.

Nếu toàn bộ trust boundary nằm ngoài tổ chức, ví dụ phụ thuộc hoàn toàn vào provider abstraction, cần đánh giá kỹ compliance, data locality, support model và exit strategy.

## Confidential Computing

Confidential computing dùng Trusted Execution Environment (TEE) để giảm rủi ro data in use. Ý tưởng cốt lõi:

- workload chạy trong vùng thực thi được bảo vệ ở cấp phần cứng;
- memory của workload được mã hóa hoặc cô lập;
- OS/hypervisor không còn là nơi được tin mặc định;
- remote attestation giúp workload hoặc client kiểm chứng trạng thái đáng tin trước khi xử lý dữ liệu.

Confidential computing không phải tính năng "bật lên là xong". Nó cần đi cùng key management, network isolation, workload placement, logging, incident response và policy rõ ràng.

## Architecture Pattern

```text
data classification
  -> trust boundary
  -> storage/network/access controls
  -> workload isolation
  -> TEE / attestation for sensitive execution
  -> audit and incident response
```

Một mô hình defense in depth thường gồm:

- storage layer: encryption at rest, replication, backup, key ownership;
- network layer: segmentation, private path, east-west control;
- identity layer: least privilege, service identity, audit;
- compute layer: VM/container isolation, node pool boundary;
- confidential layer: TEE, attestation, sensitive workload placement.

## Workload Placement

Không phải mọi workload đều cần confidential computing. Nên phân loại:

| Workload | Placement gợi ý |
|---|---|
| dữ liệu ít nhạy cảm, scale biến động | cloud/shared platform với security baseline |
| dữ liệu nhạy cảm nhưng không xử lý plaintext lâu | private path, strong IAM, encryption, segmentation |
| data in use cực nhạy cảm | TEE/confidential computing, attestation, key release có điều kiện |
| latency/I/O nhạy cảm kèm dữ liệu nhạy cảm | dedicated capacity hoặc bare metal nếu abstraction gây rủi ro |

Bare metal có thể giảm hypervisor overhead và noisy neighbor, nhưng đổi lại yêu cầu vận hành phần cứng, patching, monitoring và DR cao hơn. Virtualized confidential computing dễ dùng hơn nhưng vẫn cần hiểu giới hạn abstraction và trust boundary.

## Failure Modes

- Chỉ mã hóa at rest và in transit rồi bỏ quên data in use.
- Tin rằng private cloud tự động an toàn hơn public cloud.
- Dùng TEE nhưng không có attestation hoặc key-release policy rõ.
- Tách network kém khiến workload confidential vẫn bị lateral movement.
- Tăng control bằng bare metal nhưng thiếu patching, backup, monitoring và incident workflow.

## Trang Liên Quan

- [Control Vs Abstraction](../02-tradeoffs/04-control-vs-abstraction.md)
- [Single-Tenant Private Cloud For Data Workloads](./05-single-tenant-private-cloud-for-data-workloads.md)
- [IT Infrastructure Security And Resilience](../04-reliability-and-dr/08-it-infrastructure-security-and-resilience.md)
- [Security And Hardening](../../05-infrastructure-automation/02-security-and-hardening/overview.md)
