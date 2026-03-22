# Migration từ  VMware lên OpenStack

- Storage migration không chỉ là quá trình di chuyển dữ liệu từ hệ thống này sang hệ thống khác, mà là quá trình chuyển đổi toàn bộ hành vi lưu trữ của workload, bao gồm cách dữ liệu được truy cập, xử lý và đáp ứng về hiệu năng.
- Trong bối cảnh chuyển từ VMware sang OpenStack, sự khác biệt về kiến trúc storage (ví dụ như vSAN/VMFS so với Ceph/Cinder) dẫn đến việc cùng một workload có thể có hành vi hoàn toàn khác về latency, throughput và IOPS sau khi migrate.
- Do đó, migration không thể được xem như một thao tác “lift-and-shift” đơn thuần, mà cần được đánh giá như một quá trình thay đổi hệ thống ở mức nền tảng.

- Nguyên tắc cốt lõi
    - Migration cần được bắt đầu từ việc hiểu rõ workload, đặc biệt là các đặc điểm về I/O như pattern truy cập, độ nhạy với latency và yêu cầu về throughput.
    - Việc kiểm chứng hiệu năng phải được thực hiện bằng workload thực tế thay vì chỉ dựa trên các công cụ benchmark tổng hợp, vì các chỉ số benchmark không phản ánh đầy đủ hành vi trong môi trường production.
    - Thành công của storage migration không chỉ được đánh giá bằng việc dữ liệu được chuyển thành công, mà còn phải đảm bảo hệ thống sau migration đáp ứng được các yêu cầu về hiệu năng và độ ổn định.

## Rủi ro và thách thức
- Storage là thành phần có rủi ro cao nhất trong quá trình migration do khối lượng dữ liệu lớn, yêu cầu về tính toàn vẹn và khó khăn trong việc rollback.
- Sự khác biệt về mô hình lưu trữ có thể dẫn đến các vấn đề về hiệu năng sau migration, ngay cả khi hệ thống hoạt động bình thường về mặt chức năng.
- Migration strategy ảnh hưởng trực tiếp đến downtime và rủi ro, do đó cần cân nhắc giữa các phương pháp như cold migration, warm migration và live migration dựa trên yêu cầu của business.

## Chiến lược thực hiện
- Migration nên được thực hiện theo từng giai đoạn (phased migration), bắt đầu từ các workload nhỏ hoặc ít quan trọng, sau đó mở rộng dần khi đã xác nhận được tính ổn định.
- Cần thiết lập quy trình kiểm thử và validation rõ ràng sau mỗi giai đoạn để đảm bảo hệ thống hoạt động đúng kỳ vọng trước khi tiếp tục.
- Việc chuẩn bị hệ thống đích (OpenStack) cần bao gồm cả việc tuning storage (ví dụ Ceph) để phù hợp với workload dự kiến.


## Vận hành và con người
- Thành công của migration không chỉ phụ thuộc vào công nghệ mà còn phụ thuộc vào khả năng vận hành của đội ngũ kỹ thuật, bao gồm việc hiểu rõ hệ thống storage mới và khả năng xử lý sự cố.
- Các quy trình vận hành, monitoring và troubleshooting cần được thiết lập trước khi migration để giảm thiểu rủi ro trong quá trình chuyển đổi.

## Vai trò trong kiến trúc hệ thống 
- Storage migration là một phần quan trọng trong quá trình chuyển đổi hạ tầng, đặc biệt trong các dự án cloud migration hoặc modernize hệ thống.
- Đây là một bài toán liên quan đến dữ liệu nhiều hơn là hạ tầng, do đó yêu cầu cách tiếp cận thận trọng và có kế hoạch dài hạn.

> Trong hạ tầng, compute có thể được tái tạo, network có thể được cấu hình lại, nhưng dữ liệu là thứ khó di chuyển và khó thay thế nhất. Vì vậy, mọi quyết định liên quan đến storage migration đều cần được đánh giá với mức độ cẩn trọng cao nhất.