# AI Storage Pipeline on Ceph
- Khi làm việc với AI workload một thời gian, một điều trở nên rất rõ: bottleneck của hệ thống không còn nằm ở compute như mọi người thường nghĩ, mà thường nằm ở storage. GPU có thể rất mạnh, nhưng nếu không được cấp dữ liệu đủ nhanh và ổn định, toàn bộ pipeline sẽ bị kéo chậm lại. Điều này làm thay đổi cách nhìn về storage — nó không còn là nơi “lưu dữ liệu”, mà trở thành một phần trực tiếp của execution path.

> Storage trong AI không phải backend, mà là một phần của pipeline execution

- Điểm quan trọng nhất rút ra là AI không phải là một workload đồng nhất, mà là một pipeline gồm nhiều giai đoạn với pattern truy cập dữ liệu hoàn toàn khác nhau. Dataset ingestion cần throughput lớn và khả năng truy cập song song; training lại cần latency ổn định và I/O có tính tuần tự cao; còn giai đoạn chia sẻ model hoặc phối hợp giữa nhiều job lại giống một bài toán file system. Nếu dùng một loại storage duy nhất cho tất cả, hệ thống gần như chắc chắn sẽ bị lệch ở ít nhất một giai đoạn.

> Mỗi phase của AI workload có pattern truy cập khác nhau → cần map đúng storage interface

- Ceph trở nên phù hợp không phải vì nó “scale tốt”, mà vì nó cung cấp nhiều interface storage trên cùng một nền tảng. Object storage phù hợp cho ingest và lưu dataset lớn, block storage phù hợp cho training workload cần hiệu năng ổn định, còn file system hỗ trợ các use case chia sẻ dữ liệu giữa nhiều node hoặc nhiều người. Khi nhìn theo cách này, Ceph không còn là một storage system đơn lẻ, mà là một lớp abstraction cho phép map từng phase của AI pipeline vào đúng kiểu storage phù hợp.

> Ceph phù hợp vì cung cấp object, block và file trên cùng một nền tảng
- Một insight quan trọng khác là performance trong AI không chỉ phụ thuộc vào loại storage, mà phụ thuộc rất nhiều vào cách tổ chức tầng dưới. Hybrid storage (NVMe + HDD) cho thấy rõ điều này: NVMe không cần thay thế hoàn toàn HDD, mà đóng vai trò cache để hấp thụ read/write hot path, trong khi HDD đảm nhận dung lượng lớn. Cách kết hợp này cân bằng giữa cost và performance tốt hơn rất nhiều so với việc chỉ dùng một loại media. Điều tương tự cũng xảy ra với network: khi east-west traffic (replication, training distribution) không được tách biệt, nó sẽ trực tiếp ảnh hưởng đến latency của workload.

> Performance đến từ tổ chức hệ thống (cache, network, layout) hơn là chỉ chọn công nghệ

- Khi hệ thống bắt đầu scale, một vấn đề khác xuất hiện: không chỉ là “có scale được hay không”, mà là “scale có giữ được tính ổn định không”. Ceph giải quyết điều này bằng cách phân tán dữ liệu thông qua CRUSH, loại bỏ dependency vào một metadata layer tập trung. Điều này giúp việc thêm node không làm thay đổi cách dữ liệu được truy cập, từ đó giữ được tính tuyến tính trong cả capacity lẫn performance. Đây là một khác biệt rất lớn so với nhiều hệ thống storage truyền thống, nơi scale thường kéo theo rebalancing phức tạp hoặc downtime.

>Scale không chỉ là thêm node, mà là giữ được tính ổn định khi scale

- Một điều dễ bị đánh giá thấp là cost model của AI storage. Ở giai đoạn thử nghiệm, public cloud có vẻ hợp lý vì không cần đầu tư ban đầu. Nhưng khi chuyển sang production, đặc biệt với inference hoặc training lặp lại, chi phí trở nên khó kiểm soát do phụ thuộc vào usage (compute, storage, network). Khi đó, private cloud với Ceph bắt đầu có lợi thế: chi phí gắn với hardware, không phải từng lần truy cập dữ liệu. Điều này khiến hệ thống trở nên predictable hơn, và khi scale đủ lớn, tổng chi phí thường thấp hơn đáng kể.

> Cost của AI phụ thuộc mạnh vào storage + data movement, không chỉ compute
