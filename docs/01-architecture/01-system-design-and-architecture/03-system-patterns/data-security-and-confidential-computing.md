# Data Security & Confidential Workloads trong Distributed Systems

- Trong các hệ thống hạ tầng hiện đại, đặc biệt là cloud và distributed storage, bảo mật dữ liệu không thể được hiểu đơn giản là “có mã hóa hay không”.

- Thay vào đó, đây là bài toán kiểm soát toàn bộ vòng đời của dữ liệu, bao gồm:
    - dữ liệu lưu trữ trên đĩa (data at rest)
    - dữ liệu truyền qua mạng (data in transit)
    - dữ liệu đang được xử lý trong bộ nhớ (data in use)

> Một hệ thống chỉ thực sự an toàn khi cả ba trạng thái này đều được bảo vệ. Nếu bỏ sót bất kỳ trạng thái nào, phần đó sẽ trở thành điểm yếu mang tính hệ thống.

Trong các nền tảng như Ceph hoặc các distributed storage khác, dữ liệu được phân tán trên nhiều node nhằm đảm bảo durability và scalability, đồng thời cũng giúp giảm blast radius khi có sự cố. Tuy nhiên, việc phân tán này không tự động đồng nghĩa với bảo mật — nó chỉ là một phần của tổng thể kiến trúc.

## Giới hạn của mô hình bảo mật truyền thống
- Encryption truyền thống tập trung vào hai trạng thái:
    - at rest (disk encryption)
    - in transit (TLS, secure channel)
- Đây là baseline bắt buộc, nhưng tồn tại một điểm yếu cốt lõi:

*Khi dữ liệu được đưa vào xử lý (data in use), nó phải được giải mã trong bộ nhớ.*

- Tại thời điểm này:
    - dữ liệu trở thành plaintext
    - có thể bị truy cập bởi:
        - OS
        - hypervisor
        - privileged insider
        - các thành phần không hoàn toàn tin cậy trong môi trường multi-tenant
→ Đây chính là “lỗ hổng cuối cùng” trong mô hình bảo mật truyền thống.

## Confidential Computing: bảo vệ dữ liệu ngay cả khi đang xử lý
Confidential computing ra đời để giải quyết trực tiếp vấn đề data in use.

- Cốt lõi của mô hình này là:
    - dữ liệu luôn ở trạng thái mã hóa
    - chỉ được giải mã bên trong một vùng thực thi tin cậy (TEE – Trusted Execution Environment)
    - vùng này được bảo vệ ở cấp độ phần cứng (CPU)
- Điểm quan trọng:
    - ngay cả OS hoặc hypervisor cũng không thể truy cập dữ liệu
    - giảm thiểu rủi ro từ insider hoặc compromised host

→ Đây là bước tiến từ:
“protect data storage” → “protect data execution”

## Vấn đề thực tế: hạ tầng cloud chưa đủ để đảm bảo trust

- Public cloud cung cấp:

    - scalability
    - managed services
    - abstraction

- Nhưng tồn tại các hạn chế quan trọng:

    - shared infrastructure → rủi ro multi-tenant
    - thiếu kiểm soát tuyệt đối về data locality
    - phụ thuộc vào trust với provider
    - khó đáp ứng các yêu cầu compliance nghiêm ngặt

Ngay cả khi có encryption và IAM tốt, trust boundary vẫn nằm ngoài tổ chức.

## Private Cloud + Distributed Storage: kiểm soát nhưng chưa đủ
- Private cloud (ví dụ OpenStack) kết hợp với distributed storage (Ceph) giúp:

    - kiểm soát hoàn toàn hạ tầng
    - data sovereignty rõ ràng
    - network isolation tốt
    - tích hợp encryption at rest & in transit
    - giảm attack surface khi thiết kế hợp lý

- Tuy nhiên:

    - vẫn chưa giải quyết triệt để data in use
    - OS / hypervisor vẫn là attack vector tiềm năng

→ Nghĩa là:
**đã kiểm soát tốt “where data is” nhưng chưa kiểm soát hoàn toàn “how data is processed”**

### Private Cloud for Confidential Computing: Controlled Environment cho Sensitive Data
- **Confidential computing** (*Điện toán bảo mật*) thường được nhắc đến như một cách bảo vệ data in use, tức là bảo vệ dữ liệu ngay cả khi nó đang được xử lý trong bộ nhớ. Tuy nhiên, nếu nhìn sâu hơn thì bản chất của nó không chỉ nằm ở việc có TEE hay không, mà nằm ở toàn bộ môi trường hạ tầng xung quanh. Một workload nhạy cảm chỉ thật sự “confidential” khi cả phần cứng, mạng, cơ chế xác thực và trust boundary đều được kiểm soát rõ ràng. Nói cách khác, TEE(*Trusted Execution Environment - Môi trường thực thi đáng tin cậy*) là lõi, nhưng môi trường triển khai mới là thứ quyết định mức độ an toàn thực tế.

- Private cloud xuất hiện như một nền tảng phù hợp cho mô hình này vì nó cho phép giữ quyền kiểm soát gần như toàn bộ stack. Khi không phải dùng shared infrastructure như public cloud, bạn loại bỏ được nhiều rủi ro gắn với multi-tenancy, noisy neighbor và các dạng side-channel phụ thuộc vào môi trường dùng chung. Quan trọng hơn, private cloud cho phép bạn chủ động quyết định dữ liệu nằm ở đâu, đi qua đâu và ai có quyền chạm vào nó. Với những workload nhạy cảm như tài chính, healthcare, AI training hay xử lý dữ liệu có tính pháp lý cao, sự kiểm soát này đôi khi quan trọng không kém bản thân cơ chế mã hóa.

- Điểm đáng chú ý trong bài viết là cách nó đặt confidential computing vào đúng góc nhìn kiến trúc. Intel TDX, chẳng hạn, không chỉ tạo ra một lớp VM isolation mạnh hơn, mà còn biến isolation đó thành cryptographic isolation, nghĩa là ngay cả hypervisor hay hệ điều hành cũng không còn là nơi đáng tin mặc định. Điều này rất quan trọng, vì nó thay đổi cách ta nghĩ về trust boundary: thay vì tin toàn bộ máy chủ ảo hóa, ta chỉ tin vào vùng thực thi đã được đo lường và chứng thực. Khi kết hợp với remote attestation, hệ thống không chỉ “được bảo vệ” mà còn “chứng minh được là đang ở trạng thái đáng tin”.

- Một điểm khác cũng rất quan trọng là network không còn chỉ là đường truyền, mà trở thành một phần của security model. Trong private cloud, việc tách riêng private network, kiểm soát east-west traffic, giới hạn truy cập bằng VLAN, firewall hay VPN giúp giảm đáng kể bề mặt tấn công và kiểm soát tốt luồng dữ liệu. Điều này đặc biệt hữu ích với các workload phân tán, nơi traffic nội bộ giữa các node hoặc service có thể còn nhạy cảm hơn cả traffic đi ra ngoài. Nói ngắn gọn, nếu data cần được bảo vệ lúc in use thì network cũng phải được xem như một vùng cần bảo vệ chứ không chỉ là hạ tầng phụ trợ.

=> Vì vậy, confidential computing không nên được hiểu như một tính năng đơn lẻ có thể “bật lên là xong”. Nó là kết quả của một kiến trúc được thiết kế có chủ đích, trong đó private cloud cung cấp controlled environment, TEE cung cấp lớp bảo vệ khi xử lý, còn attestation và network isolation cung cấp niềm tin và ranh giới vận hành. Đây là kiểu bài toán mà public cloud có thể hỗ trợ một phần, nhưng private cloud thường phù hợp hơn nếu mục tiêu là kiểm soát toàn diện và giảm phụ thuộc vào trust bên ngoài.


### Bare Metal Confidential Computing: Dedicated Hardware vs Virtualized Enclaves

- Confidential computing về bản chất nhằm bảo vệ data in use, nhưng cách triển khai nó quyết định trực tiếp đến hiệu quả thực tế. Một điểm quan trọng mà bài này nhấn mạnh là: cùng là TEE, nhưng chạy trên virtualized environment hay bare metal sẽ tạo ra hai hệ thống có đặc tính hoàn toàn khác nhau. Sự khác biệt không nằm ở khái niệm bảo mật, mà nằm ở cách tài nguyên phần cứng được truy cập và kiểm soát.

- Trong mô hình phổ biến hiện nay, confidential computing thường được triển khai dưới dạng virtualized enclaves trên public cloud. Cách tiếp cận này mang lại sự tiện lợi vì không cần quản lý hạ tầng, nhưng nó tạo ra một lớp abstraction bổ sung giữa workload và hardware. Lớp hypervisor này không chỉ là một thành phần trung gian, mà còn là nguồn gốc của nhiều vấn đề: độ trễ tăng lên theo từng lần truy cập tài nguyên, chi phí CPU/memory bị đội lên, và quan trọng nhất là sự không ổn định do resource contention giữa các tenant. Những overhead này không phải lúc nào cũng thấy rõ ở mức nhỏ, nhưng sẽ tích lũy đáng kể trong các workload nặng hoặc latency-sensitive.

- Một hạn chế khác của virtualized enclaves là việc truy cập phần cứng bị giới hạn. Các enclave thường bị constrain bởi:

    - dung lượng memory khả dụng
    - khả năng sử dụng GPU hoặc hardware accelerator
    - giới hạn trong I/O path

- Điều này khiến nhiều workload thực tế, đặc biệt là AI training hoặc xử lý dữ liệu lớn, khó tận dụng đầy đủ lợi ích của confidential computing khi chạy trong môi trường ảo hóa.

- Ngược lại, khi confidential computing được triển khai trên bare metal, toàn bộ mô hình thay đổi. Workload có thể truy cập trực tiếp vào CPU, memory và I/O mà không phải đi qua hypervisor layer. Điều này không chỉ loại bỏ overhead mà còn làm cho hiệu năng trở nên ổn định và dễ dự đoán hơn. Với các công nghệ như Intel TDX, bare metal cho phép tận dụng đầy đủ trust domain ở cấp phần cứng, nơi việc mã hóa memory và bảo vệ CPU state được thực hiện trực tiếp mà không phụ thuộc vào lớp ảo hóa.

- Một hệ quả quan trọng là sự khác biệt về tính “deterministic” của hệ thống. Trong môi trường virtualized:

    - latency có thể biến động
    - throughput không ổn định
    - performance bị ảnh hưởng bởi tenant khác

- Trong khi đó, bare metal mang lại:

    - hiệu năng ổn định
    - không có noisy neighbor
    - predictable latency

- Điều này đặc biệt quan trọng với các hệ thống như trading, blockchain hoặc real-time processing, nơi sự biến động nhỏ cũng có thể gây ra hậu quả lớn.

- Ngoài performance, yếu tố chi phí cũng là một điểm đáng chú ý. Virtualized confidential computing trong public cloud thường đi kèm mô hình billing phức tạp (instance, network egress, storage I/O), khiến chi phí khó dự đoán và dễ tăng đột biến khi workload tăng. Trong khi đó, bare metal thường theo mô hình fixed cost theo server, cho phép tận dụng toàn bộ tài nguyên phần cứng mà không bị tính phí theo từng lớp abstraction.

- Từ góc nhìn kiến trúc, insight quan trọng nhất của bài này là:
confidential computing không chỉ là câu chuyện “có TEE hay không”, mà là câu chuyện TEE chạy trên loại hạ tầng nào. Nếu chạy trên hạ tầng chia sẻ, bạn vẫn đang mang theo các vấn đề của multi-tenancy và virtualization. Nếu chạy trên bare metal, bạn đưa trust boundary xuống sát hardware, nơi mô hình bảo mật thực sự phát huy tác dụng.

## Kiến trúc hoàn chỉnh: Defense in Depth + Workload Placement

Để đạt mức bảo mật cao thực sự, cần kết hợp nhiều lớp:

- **Lớp 1: Storage & Data Layer**
    - distributed storage (Ceph)
    - replication / erasure coding
    - encryption at rest
- **Lớp 2: Network Layer**
    - network isolation (public / cluster / backend)
    - tách biệt traffic storage, replication, client
    - giảm khả năng lateral movement
- **Lớp 3: Access Control**
    - IAM, RBAC
    - authentication, authorization
- **Lớp 4: Compute & Execution Layer**
    - container / VM isolation
    - workload segmentation
- **Lớp 5: Confidential Computing**
    - TEE (SGX, TDX)
    - bảo vệ data in use

→ Đây là mô hình defense in depth, trong đó mỗi lớp giảm thiểu rủi ro nếu lớp khác bị phá vỡ.

## Hybrid Architecture: OpenStack + Bare Metal Confidential Computing

- Một kiến trúc thực tế và hiệu quả là hybrid:

- OpenStack (private cloud):
    - orchestration
    - networking
    - storage integration
    - multi-tenant control
- Bare metal với TEE:
    - xử lý workload nhạy cảm
    - AI/ML training
    - financial computation
    - dữ liệu yêu cầu bảo mật cao
### Nguyên tắc quan trọng: workload placement

> Không phải tất cả workload đều cần confidential computing.

- Phân loại:

    - sensitive workloads → chạy trên TEE (bare metal)
    - non-sensitive workloads → chạy trên cloud layer

→ Đây là bài toán kiến trúc, không phải chỉ là công nghệ.

## Giảm attack surface & kiểm soát kiến trúc

Một insight quan trọng trong thiết kế:

- Mỗi thành phần thêm vào hệ thống → tăng attack surface
- Một nền tảng lưu trữ thống nhất (như Ceph) giúp:
    - giảm số hệ thống cần quản lý
    - giảm điểm tấn công tiềm năng

- Kết hợp với:

    - network isolation
    - segmentation
    - minimal exposure

→ giúp hệ thống vừa secure vừa maintainable

## Vai trò trong thiết kế hệ thống hiện đại

- Bảo mật dữ liệu, đặc biệt là data in use, không còn là optional enhancement mà là:

    - một phần của system architecture
    - cần được thiết kế ngay từ đầu
    - ảnh hưởng trực tiếp đến:
        - workload placement
        - hạ tầng compute
        - topology mạng
        - lựa chọn platform (cloud vs bare metal vs hybrid)

- Các use case như:

    - healthcare (PHI)
    - finance
    - AI/ML
    - blockchain

→ đều yêu cầu mô hình này ở mức độ khác nhau.