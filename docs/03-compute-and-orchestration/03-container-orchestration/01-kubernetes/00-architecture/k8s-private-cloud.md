# Kubernetes on Private Cloud: Cost & Performance vs Managed (EKS / GKE)

- Trong nhiều năm, các dịch vụ managed Kubernetes như EKS hay GKE được xem là lựa chọn mặc định vì sự tiện lợi và abstraction mà chúng mang lại. Tuy nhiên, khi hệ thống bắt đầu scale, đặc biệt với các workload chạy ổn định và dài hạn, những giả định ban đầu về chi phí và hiệu năng dần bộc lộ vấn đề. Bài viết này cho thấy rằng việc chạy Kubernetes trên private cloud không chỉ là một lựa chọn thay thế, mà trong nhiều trường hợp còn là phương án tối ưu hơn về cả chi phí lẫn hiệu năng.

- Một điểm quan trọng là chi phí của managed Kubernetes không chỉ nằm ở “giá niêm yết”. Ngoài control plane fee cố định, chi phí thực tế còn bị đẩy lên bởi nhiều lớp ẩn như markup của VM, storage bị throttle theo IOPS, và đặc biệt là data egress. Những yếu tố này không đáng kể ở quy mô nhỏ, nhưng sẽ tích lũy nhanh chóng khi cluster mở rộng. Ví dụ, cùng một cấu hình, chi phí VM trên public cloud có thể cao hơn nhiều lần so với private cloud, và tổng chi phí có thể giảm tới ~50% khi chuyển sang mô hình private cloud.

- Song song với chi phí là vấn đề hiệu năng, vốn thường bị đánh giá thấp khi chọn managed service. Trong môi trường multi-tenant, workload của bạn luôn phải chia sẻ tài nguyên với các tenant khác, dẫn đến hiện tượng “noisy neighbor”. Điều này tạo ra sự biến động về CPU, độ trễ I/O và congestion mạng, khiến hệ thống trở nên khó đoán và khó tối ưu. Ngoài ra, storage trong public cloud thường bị giới hạn hoặc throttle để đảm bảo fairness, khiến bạn không thể tối ưu theo đặc tính workload (read-heavy vs write-heavy).

- Private cloud giải quyết trực tiếp hai vấn đề này bằng cách đưa Kubernetes về môi trường single-tenant với hardware dedicated. Khi đó, toàn bộ tài nguyên CPU, memory, storage và network đều thuộc quyền kiểm soát của bạn. Điều này không chỉ loại bỏ hiện tượng resource contention mà còn giúp hệ thống đạt được hiệu năng ổn định và predictable hơn. Đặc biệt, khi kết hợp với distributed storage như Ceph và network nội bộ tốc độ cao, các workload phân tán như database hoặc streaming system có thể đạt throughput và latency tốt hơn đáng kể so với môi trường public cloud.

- Một khác biệt mang tính kiến trúc là mức độ kiểm soát. Trong managed Kubernetes, bạn bị giới hạn bởi abstraction của provider: không có root access đầy đủ, không thể tinh chỉnh kernel, driver hoặc hardware-level parameters. Trong private cloud, bạn có thể tối ưu toàn bộ stack từ OS, network stack cho đến BIOS-level tuning. Điều này đặc biệt quan trọng với các workload yêu cầu latency thấp hoặc tối ưu tài nguyên sâu, nơi mà mỗi lớp abstraction đều tạo thêm overhead.

- Tuy nhiên, lợi thế lớn nhất của private cloud không nằm ở từng yếu tố riêng lẻ mà nằm ở mô hình chi phí. Public cloud vận hành theo usage-based model, nghĩa là chi phí tăng tuyến tính (hoặc tệ hơn) theo tài nguyên sử dụng. Ngược lại, private cloud hoạt động theo fixed-cost model: bạn trả tiền cho hardware, không phải cho từng đơn vị sử dụng. Điều này khiến chi phí trở nên predictable và đặc biệt hiệu quả với các workload có mức sử dụng ổn định. Khi scale đủ lớn, economics sẽ “flip”, và private cloud trở thành lựa chọn rẻ hơn rõ rệt.

- Dù vậy, managed Kubernetes không phải lúc nào cũng là lựa chọn tệ. Với các hệ thống nhỏ, workload không ổn định hoặc cần time-to-market nhanh, EKS/GKE vẫn mang lại lợi thế nhờ giảm gánh nặng vận hành. Vấn đề chỉ xuất hiện khi hệ thống chuyển sang trạng thái steady-state, nơi bạn đang trả tiền liên tục cho một mức tài nguyên gần như không thay đổi.

- Từ góc nhìn kiến trúc, bài này thực chất không phải so sánh Kubernetes platform, mà là so sánh hai mô hình hạ tầng:

    - public cloud → tối ưu cho flexibility và convenience
    - private cloud → tối ưu cho performance, control và cost predictability

Và điều quan trọng nhất là:

>Kubernetes không quyết định chi phí hay hiệu năng, hạ tầng bên dưới Kubernetes mới là thứ quyết định