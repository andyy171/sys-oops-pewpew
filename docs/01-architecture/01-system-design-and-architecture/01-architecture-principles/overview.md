# Tổng quan



## Infrastructure Consistency (Tính đồng nhất hạ tầng)
- Infrastructure Consistency là nguyên tắc đảm bảo rằng toàn bộ hạ tầng hệ thống (compute, network, storage, cấu hình, công cụ vận hành) được triển khai và vận hành theo một chuẩn thống nhất, thay vì bị phân mảnh theo từng team hoặc từng giai đoạn phát triển.
- Trong giai đoạn đầu của một hệ thống SaaS, hạ tầng thường đơn giản và đồng nhất. Tuy nhiên, khi hệ thống mở rộng, áp lực phát triển nhanh và sự gia tăng số lượng dịch vụ khiến hạ tầng dần bị “drift”, dẫn đến tình trạng mỗi service hoặc mỗi môi trường có cấu hình và cách vận hành khác nhau.
> Configuration Drift là sự sai lệch giữa trạng thái thực tế của tài nguyên (Actual State) và trạng thái được định nghĩa trong code (Desired State). Sự không đồng nhất này có thể dẫn đến các vấn đề về hiệu năng, bảo mật và khả năng vận hành khi hệ thống phát triển đến quy mô lớn. 
> Giải pháp thương được áp dụng là sử dụng các công cụ có tính năng Reconciliation Loop (như Kubernetes hoặc Terraform Cloud/Drift Detection) để tự động phát hiện và đưa hạ tầng về trạng thái chuẩn.

- Sự không đồng nhất này không xảy ra ngay lập tức mà tích lũy theo thời gian, thường xuất phát từ các thay đổi nhỏ như chỉnh sửa cấu hình tạm thời, sử dụng công cụ khác nhau giữa các team hoặc triển khai môi trường không nhất quán giữa dev, staging và production.
### Nguyên nhân gây mất tính đồng nhất
- Áp lực phát triển và release nhanh khiến các thay đổi được thực hiện theo hướng “tạm thời nhưng tồn tại lâu dài”, làm lệch khỏi chuẩn ban đầu của hệ thống.
- Sự khác biệt giữa các môi trường (development, staging, production) dẫn đến tình trạng hành vi hệ thống không nhất quán, gây khó khăn trong việc dự đoán và kiểm thử.
- Việc sử dụng nhiều công cụ khác nhau cho deployment, monitoring hoặc security khiến hệ thống thiếu một tiêu chuẩn chung để quản lý.
- Hạn chế từ hạ tầng (ví dụ như resource không đồng đều hoặc cấu hình khác nhau giữa các instance) cũng góp phần làm tăng sự không nhất quán.
### Hệ quả trong môi trường production
- Hệ thống trở nên khó dự đoán về hiệu năng, đặc biệt khi có sự gia tăng đột biến về tải. Một số thành phần hoạt động ổn định trong khi các thành phần khác có thể trở thành điểm nghẽn do khác biệt về cấu hình.
- Các vấn đề về bảo mật có thể xuất hiện do không áp dụng đồng đều các chính sách security trên toàn hệ thống, tạo ra những điểm yếu khó phát hiện.
- Việc troubleshooting và vận hành trở nên phức tạp hơn do mỗi service có cách cấu hình và giám sát khác nhau, làm tăng thời gian xử lý sự cố.
- Quá trình audit và compliance gặp khó khăn do phải kiểm tra nhiều cấu hình khác nhau thay vì một chuẩn chung.
### Nguyên tắc đảm bảo Infrastructure Consistency
- Hạ tầng cần được chuẩn hóa thông qua các template hoặc blueprint chung, đảm bảo các service được triển khai theo cùng một mô hình ngay từ đầu.

> Ví dụ : Thay vì sửa lỗi trực tiếp trên một server đang chạy (Patching), chúng ta sẽ hủy nó đi và triển khai một bản mới hoàn toàn từ Image/Template chuẩn. Điều này triệt tiêu hoàn toàn sự khác biệt giữa các instance do thao tác tay.

- Các môi trường (dev, staging, production) cần được thiết kế sao cho càng giống nhau càng tốt, giảm thiểu sự khác biệt về hành vi khi triển khai thực tế.
- Security và compliance nên được tích hợp trực tiếp vào hạ tầng (built-in), thay vì bổ sung sau khi hệ thống đã vận hành.
- Monitoring và alerting cần được chuẩn hóa, sử dụng cùng một hệ thống metric và quy tắc cảnh báo để đảm bảo khả năng quan sát và xử lý sự cố hiệu quả.
- Infrastructure as Code cần được sử dụng theo các pattern thống nhất, tránh việc mỗi team triển khai theo cách riêng dẫn đến phân mảnh hệ thống.
### Vai trò trong kiến trúc hệ thống
- Infrastructure Consistency không phải là một công cụ hay công nghệ cụ thể, mà là một nguyên tắc thiết kế và vận hành hệ thống ở quy mô lớn.
- Nguyên tắc này đóng vai trò nền tảng trong việc đảm bảo khả năng mở rộng (scalability), tính ổn định (reliability) và khả năng vận hành (operability) của hệ thống.
- Trong các hệ thống hiện đại, đặc biệt là SaaS và cloud-native, việc duy trì tính đồng nhất của hạ tầng là điều kiện cần để kiểm soát độ phức tạp khi hệ thống phát triển.


## Infrastructure as a Product (Tư duy sản phẩm hóa hạ tầng)
- Infrastructure as a Product là cách tiếp cận trong đó hạ tầng không còn được xem là một tập hợp tài nguyên cần quản lý (server, network, storage), mà được thiết kế và vận hành như một “sản phẩm nội bộ” phục vụ cho developer.
- Trong mô hình truyền thống, hạ tầng thường được cung cấp thông qua quy trình ticket-based, nơi các team phải phụ thuộc vào bộ phận vận hành để cấp phát tài nguyên hoặc triển khai môi trường. Cách tiếp cận này tạo ra bottleneck, làm chậm quá trình phát triển và khiến hạ tầng trở thành điểm nghẽn thay vì là nền tảng hỗ trợ.
- Khi hệ thống phát triển theo hướng cloud-native và DevOps, nhu cầu về tốc độ và khả năng tự phục vụ (self-service) tăng cao. Điều này dẫn đến sự chuyển dịch từ mô hình IT Operations truyền thống sang Platform Engineering, nơi hạ tầng được đóng gói thành các dịch vụ tiêu chuẩn hóa và cung cấp thông qua API hoặc portal.

### Đặc trưng của Infrastructure as a Product
- Hạ tầng được thiết kế theo hướng self-service, cho phép developer chủ động tạo và quản lý tài nguyên mà không cần thông qua quy trình thủ công.
- Các thành phần hạ tầng (compute, storage, network, CI/CD, monitoring) được chuẩn hóa thành các service có thể tái sử dụng, thay vì mỗi team tự triển khai theo cách riêng.
- API-first là nguyên tắc cốt lõi, đảm bảo mọi thao tác với hạ tầng đều có thể tự động hóa và tích hợp vào pipeline.
- Security, monitoring và compliance được tích hợp sẵn (built-in) vào platform, thay vì bổ sung sau.
### Nguyên nhân thúc đẩy mô hình này
- Áp lực giảm time-to-market khiến việc phụ thuộc vào quy trình thủ công trở nên không còn phù hợp.
- Sự phân mảnh hạ tầng giữa các team làm giảm khả năng kiểm soát và tăng chi phí vận hành.
- Sự phát triển của cloud và container platform cho phép trừu tượng hóa hạ tầng ở mức cao hơn.
### Hệ quả nếu không áp dụng
- Developer tìm cách “lách” quy trình (shadow IT), sử dụng tài nguyên bên ngoài hệ thống kiểm soát.
- Hạ tầng trở thành bottleneck, làm giảm tốc độ release và khả năng cạnh tranh.
- Tăng rủi ro về bảo mật và chi phí do thiếu tiêu chuẩn chung.
### Nguyên tắc triển khai
- Xây dựng platform team với vai trò như một product team nội bộ, trong đó developer là “khách hàng”.
- Cung cấp service catalog rõ ràng, bao gồm các dịch vụ hạ tầng chuẩn hóa.
- Thiết kế theo mô hình guardrails thay vì kiểm soát chặt, cho phép linh hoạt nhưng vẫn đảm bảo tiêu chuẩn.
- Đo lường hiệu quả dựa trên developer productivity và adoption, thay vì chỉ dựa trên uptime hoặc resource utilization.
### Vai trò trong kiến trúc hệ thống
- Infrastructure as a Product là bước tiến tiếp theo của Infrastructure Consistency, giúp không chỉ đảm bảo tính đồng nhất mà còn nâng cao trải nghiệm sử dụng hạ tầng.
- Nguyên tắc này đặc biệt quan trọng trong các hệ thống lớn, nơi số lượng team và service tăng nhanh, đòi hỏi một nền tảng chung để giảm độ phức tạp.
- Đây là nền tảng của Platform Engineering, giúp cân bằng giữa tốc độ phát triển, khả năng kiểm soát và chi phí vận hành trong dài hạn.

## Full Control Infrastructure (Toàn quyền kiểm soát hạ tầng)
- Full Control Infrastructure là nguyên tắc trong đó đội ngũ DevOps có toàn quyền kiểm soát hệ thống ở mọi tầng, từ phần cứng, hệ điều hành đến network và security, thay vì bị giới hạn bởi abstraction hoặc policy của cloud provider.
- Trong các môi trường cloud truyền thống, đặc biệt là public cloud, hạ tầng thường bị giới hạn bởi các lớp abstraction và cơ chế kiểm soát của nhà cung cấp. Điều này giúp đơn giản hóa việc sử dụng, nhưng đồng thời làm giảm khả năng tùy biến và kiểm soát sâu đối với hệ thống.
- Khi hệ thống phát triển đến mức cần tối ưu hiệu năng, bảo mật hoặc triển khai các workload đặc thù (high-performance, low-latency, custom kernel, security hardening), các giới hạn này trở thành rào cản kỹ thuật thực sự.
### Root Access và ý nghĩa thực tế
- Root access đại diện cho mức quyền cao nhất trên hệ thống, cho phép thay đổi mọi thành phần từ cấu hình OS, network, firewall đến cài đặt phần mềm và tuning hệ thống.
- Đối với DevOps, điều này không chỉ là “quyền truy cập”, mà là khả năng:
    - triển khai và tùy chỉnh toàn bộ stack (OS → middleware → application)
    - tối ưu hiệu năng theo workload cụ thể
    - triển khai các cơ chế bảo mật tùy chỉnh
- Trong môi trường không có root access, các thao tác này thường phải thông qua quy trình trung gian (ticket, approval), gây gián đoạn workflow và làm chậm tốc độ phát triển.
### Vấn đề của mô hình bị giới hạn quyền
- Hạ tầng trở thành “black box”, khó debug và khó tối ưu.
- DevOps mất khả năng tự chủ, phụ thuộc vào provider hoặc team khác để thực hiện các thay đổi ở mức hệ thống.
- Một số use case không thể triển khai:
    - custom kernel / driver
    - hardware-level tuning
    - security control đặc thù
- Tốc độ phát triển bị ảnh hưởng do các thao tác đơn giản cũng cần qua nhiều bước trung gian.
### Private Cloud và Bare Metal như một giải pháp
- Private cloud trên nền bare metal cung cấp:
    - toàn quyền kiểm soát phần cứng và phần mềm
    - khả năng cấu hình mạng, storage và compute theo nhu cầu
    - môi trường không bị giới hạn bởi multi-tenant abstraction
- Điều này cho phép DevOps triển khai hạ tầng “theo đúng cách họ muốn”, thay vì phải thích nghi với giới hạn của nền tảng.
### Kết hợp với Automation và IaC
- Full control không mâu thuẫn với automation, mà ngược lại là điều kiện để automation hoạt động hiệu quả:
    - Infrastructure as Code có thể quản lý toàn bộ stack
    - CI/CD có thể provision và teardown môi trường hoàn toàn tự động
    - Có thể tích hợp sâu với tooling như Ansible, Terraform
- Việc có quyền đầy đủ giúp loại bỏ các giới hạn permission trong pipeline và giảm độ phức tạp khi thiết kế automation.
### Cân bằng giữa Control và Security
- Full control không đồng nghĩa với mất an toàn, mà yêu cầu:
    - kiểm soát truy cập chặt chẽ (RBAC, MFA)
    - audit và logging đầy đủ
    - nguyên tắc “provision → harden → restrict”
- Security chuyển từ “bị áp đặt bởi provider” sang “do hệ thống tự định nghĩa”.
### Vai trò trong kiến trúc hệ thống
- Full Control Infrastructure là nền tảng cho các hệ thống cần:
    - hiệu năng cao
    - khả năng tùy biến sâu
    - kiểm soát bảo mật nghiêm ngặt
- Nguyên tắc này đặc biệt quan trọng khi:
    - xây dựng platform nội bộ
    - vận hành private cloud
    - triển khai hybrid hoặc multi-cloud
> Đây là yếu tố bổ sung cho Infrastructure as a Product, đảm bảo rằng platform không chỉ dễ dùng mà còn đủ mạnh và linh hoạt để đáp ứng các yêu cầu phức tạp.

## Cách đánh giá một PoC
- **Proof of Concept (PoC)** không chỉ là việc thử nghiệm một giải pháp để xem “có chạy được hay không”, mà là quá trình kiểm chứng một giả thuyết cụ thể về hệ thống, nhằm đánh giá liệu giải pháp đó có thực sự giải quyết được vấn đề trong môi trường production hay không.
- Một PoC hiệu quả cần được thiết kế với mục tiêu rõ ràng và tiêu chí đánh giá cụ thể. Nếu không, kết quả PoC sẽ mang tính cảm tính và không thể dùng làm cơ sở ra quyết định.
- Nguyên tắc cốt lõi
    - PoC phải bắt đầu từ một giả thuyết rõ ràng, ví dụ như cải thiện hiệu năng, giảm chi phí hoặc tăng khả năng vận hành. Việc xác định rõ giả thuyết giúp định hướng toàn bộ quá trình thử nghiệm.
    - Thành công của PoC cần được đo lường bằng các chỉ số cụ thể thay vì cảm nhận. Các metric như latency (p95, p99), throughput, thời gian deploy hoặc chi phí vận hành cần được xác định trước khi bắt đầu.
    - Việc thiết lập baseline là bắt buộc. Nếu không có dữ liệu của hệ thống hiện tại, không thể xác định liệu giải pháp mới có thực sự mang lại cải thiện hay không.
### Đánh giá theo vòng đời hệ thống

- PoC không nên chỉ tập trung vào giai đoạn triển khai ban đầu (Day 1), mà cần đánh giá cả khả năng vận hành (Day 2). Một hệ thống có thể dễ deploy nhưng khó vận hành sẽ không phù hợp cho production.
    - Các yếu tố cần kiểm tra bao gồm khả năng tự động hóa, khả năng tích hợp với hệ thống hiện tại, quy trình backup/restore và khả năng xử lý sự cố.

### Tính tương thích và tích hợp 
- Giải pháp cần được kiểm tra khả năng tương thích với các công cụ hiện có như CI/CD, monitoring, logging và hệ thống quản lý cấu hình.
- Một PoC tốt không chỉ chứng minh giải pháp hoạt động độc lập, mà còn chứng minh nó có thể hoạt động hiệu quả trong hệ sinh thái hiện tại.

### Đánh giá chi phí (Cost Predictability)
- Chi phí không nên được đánh giá dựa trên giá niêm yết mà cần dựa trên hành vi thực tế của hệ thống.
- PoC cần mô phỏng workload thực tế để xác định chi phí vận hành trong các kịch bản khác nhau, đặc biệt là khi hệ thống scale.
- Khả năng dự đoán chi phí theo thời gian là yếu tố quan trọng trong việc lựa chọn giải pháp hạ tầng.

### Đánh giá vận hành và con người
- Khả năng vận hành của hệ thống phụ thuộc không chỉ vào công nghệ mà còn vào đội ngũ kỹ thuật và hệ thống hỗ trợ.
- Cần đánh giá mức độ phức tạp khi vận hành, thời gian xử lý sự cố và chất lượng hỗ trợ từ nhà cung cấp hoặc cộng đồng.

### Exit Strategy (Khả năng thoát khỏi hệ thống)
- Một tiêu chí quan trọng của PoC là khả năng thoát khỏi giải pháp mà không bị khóa chặt (vendor lock-in).
- Cần kiểm tra khả năng export dữ liệu, tính tương thích định dạng và khả năng di chuyển workload sang hệ thống khác.

### Vai trò trong kiến trúc hệ thống
PoC evaluation là một nguyên tắc quan trọng trong quá trình thiết kế và lựa chọn kiến trúc, giúp giảm rủi ro khi đưa ra quyết định về công nghệ.
> Việc đánh giá PoC một cách có hệ thống giúp đảm bảo rằng các lựa chọn hạ tầng không chỉ phù hợp về mặt kỹ thuật mà còn phù hợp với vận hành và chi phí trong dài hạn.


## Single-Tenant Private Cloud for High-Volume Data Collection
- High-volume data collection là kiểu workload mà giá trị cốt lõi không nằm ở việc hệ thống chỉ "chạy được", mà nằm ở việc hệ thống có thể ingest, xử lý và lưu trữ dữ liệu với hiệu năng ổn định, dự đoán được và chi phí có thể kiểm soát.
> Trong các môi trường multi-tenant, vấn đề lớn nhất không chỉ là cạnh tranh tài nguyên, mà là sự thiếu ổn định của tài nguyên khi nhiều tenant cùng chia sẻ CPU, memory, storage I/O và network. Đây là nguyên nhân trực tiếp dẫn đến hiện tượng noisy neighbor và làm hiệu năng hệ thống dao động khó đoán.

### Vấn đề của multi-tenant đối với data collection
- Với các workload dữ liệu lớn, tính ổn định quan trọng hơn việc đạt một con số performance cao trong một thời điểm ngắn. Một pipeline ingest có thể chạy rất tốt trong một khoảng thời gian, rồi đột ngột giảm throughput chỉ vì một tenant khác trên cùng hạ tầng đang chạy tác vụ nặng.
- Đặc biệt với các hệ thống write-heavy như ingestion pipeline, Kafka, batch processing hoặc real-time analytics, storage I/O contention là một trong những nguyên nhân gây ra độ trễ và sai lệch hiệu năng rõ nhất.
- Khi hạ tầng bị ảnh hưởng bởi noisy neighbor, hệ thống không chỉ chậm hơn mà còn mất tính dự đoán. Và với data system, mất tính dự đoán thường nguy hiểm hơn mất hiệu năng tuyệt đối.

### Lợi thế của single-tenant private cloud
- Single-tenant private cloud cấp phát tài nguyên vật lý riêng cho một tổ chức, thay vì chia sẻ hạ tầng với nhiều tenant khác. Điều này loại bỏ lớp tranh chấp tài nguyên ở mức phần cứng, từ đó tạo ra môi trường vận hành ổn định hơn cho các workload dữ liệu lớn.
- Lợi ích lớn nhất của mô hình này không chỉ là performance cao hơn, mà là performance ổn định hơn. Khi CPU, disk và network không bị can thiệp bởi workload của tenant khác, hệ thống ingest và xử lý dữ liệu có thể vận hành theo hành vi nhất quán hơn.
- Với các workload dữ liệu lớn, sự ổn định này trực tiếp giúp giảm rủi ro vi phạm SLA, giảm thời gian debug và làm cho toàn bộ chuỗi xử lý dữ liệu trở nên dễ dự đoán hơn.

### Predictable performance, predictable cost
- Với các hệ thống data collection liên tục, chi phí cloud không chỉ đến từ compute và storage mà còn từ việc hệ thống mở rộng khó đoán, traffic tăng khó kiểm soát và tài nguyên bị ảnh hưởng bởi mô hình chia sẻ.
- Private cloud single-tenant giúp chi phí dễ dự đoán hơn vì tài nguyên được cấp phát cố định và hành vi hệ thống không bị dao động bởi tenant khác. Điều này đặc biệt quan trọng với các tổ chức có workload ổn định, ingest liên tục và không có nhiều thời gian idle để tối ưu bằng cách scale down.
- Trong thực tế, chi phí hạ tầng tốt không phải là chi phí thấp nhất trên giấy, mà là chi phí có thể mô hình hóa được và không tạo ra bất ngờ trong production.

### Storage architecture cho data collection
- Với hệ thống dữ liệu lớn, storage không chỉ là nơi lưu dữ liệu mà là một phần của đường đi dữ liệu. Nếu storage không đủ ổn định, toàn bộ pipeline ingest, queue, processing và persistence đều có thể bị ảnh hưởng.
- Các hệ thống single-tenant private cloud phù hợp với workload cần I/O ổn định, độ trễ thấp và throughput nhất quán. Đây là nền tảng tốt cho các thành phần như Kafka, Spark, database analytics và các pipeline thu thập dữ liệu theo thời gian thực.
- Khi storage được vận hành trên hạ tầng riêng, khả năng kiểm soát hiệu năng, bố trí tài nguyên và tối ưu kiến trúc sẽ tốt hơn nhiều so với môi trường chia sẻ.

### Monitoring và observability ở quy mô lớn
- Monitoring chỉ thật sự có ý nghĩa khi hạ tầng đủ ổn định để metric phản ánh đúng trạng thái hệ thống. Nếu tài nguyên dao động liên tục vì noisy neighbor, metric trở nên khó phân biệt giữa lỗi ứng dụng và nhiễu hạ tầng.
- Single-tenant infrastructure giúp observability rõ hơn vì biến số hạ tầng giảm xuống. Khi đó, các tín hiệu về throughput, latency, queue lag và storage pressure trở nên đáng tin cậy hơn để ra quyết định vận hành.

### Khi nào nên chọn single-tenant private cloud
- Mô hình này phù hợp nhất với các hệ thống có khối lượng dữ liệu lớn, ingest liên tục, yêu cầu SLA rõ ràng và cần hiệu năng có thể dự đoán được.
- Nó đặc biệt phù hợp với các use case như IoT data collection, real-time analytics, logging pipeline, media processing, telemetry system và các hệ thống data platform phục vụ nhiều nhóm người dùng nội bộ.
- Ngược lại, nếu workload nhỏ, biến động mạnh hoặc chỉ chạy theo từng đợt ngắn, việc dùng hạ tầng single-tenant có thể không đem lại lợi ích kinh tế tương xứng.


## Workload Pattern và kiến trúc hệ thống
- Workload pattern là cách thức mà một hệ thống sử dụng tài nguyên để thực hiện các tác vụ cụ thể, và nó có ảnh hưởng trực tiếp đến việc thiết kế kiến trúc hệ thống.
- Việc hiểu rõ workload pattern giúp kiến trúc sư lựa chọn đúng loại hạ tầng, công nghệ và mô hình triển khai phù hợp, từ đó tối ưu hiệu năng, chi phí và khả năng vận hành của hệ thống.
- Các workload pattern phổ biến bao gồm:
    - Steady-state workload : Workload có khối lượng ổn định, thường xuyên và có thể dự đoán được. Ví dụ: hệ thống thu thập dữ liệu liên tục, dịch vụ API với traffic ổn định.
    - Spiky workload : Workload có khối lượng biến động mạnh, thường xuyên có những đợt tăng đột biến. Ví dụ: hệ thống bán hàng trong dịp khuyến mãi, dịch vụ streaming trong giờ cao điểm.
    - Batch workload : Workload thực hiện các tác vụ theo lô, thường chạy vào ban đêm hoặc vào thời điểm có ít người dùng. Ví dụ: hệ thống ETL, báo cáo hàng ngày.
    - Real-time workload : Workload yêu cầu xử lý dữ liệu ngay lập tức, với độ trễ thấp. Ví dụ: hệ thống giám sát, dịch vụ chat, xử lý giao dịch tài chính.
- Mỗi loại workload pattern sẽ yêu cầu một kiến trúc hệ thống khác nhau để tối ưu hóa hiệu năng và chi phí. Ví dụ, steady-state workload có thể phù hợp với hạ tầng single-tenant để đảm bảo ổn định, trong khi spiky workload có thể tận dụng lợi thế của cloud để scale linh hoạt.
- Việc lựa chọn kiến trúc hệ thống dựa trên workload pattern cũng giúp đảm bảo rằng hệ thống có thể đáp ứng được các yêu cầu về SLA, khả năng mở rộng và chi phí vận hành trong dài hạn.