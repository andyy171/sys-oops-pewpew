# RBD - Rados Block Device
RBD (Rados Block Device) là một giao diện lưu trữ block phân tán, hiệu năng cao và chịu lỗi vượt trội của Ceph Storage Cluster. RBD được thiết kế để đáp ứng nhu cầu lưu trữ phân tán, mở rộng cao, hỗ trợ dung lượng lên tới exabyte và tương thích hoàn hảo với các nền tảng ảo hóa như KVM, VMware, OpenStack hay CloudStack. RBD chia block thành nhiều object và phân tán chúng toàn bộ cluster, mang lại tính bảo đảm và hiệu năng cao. Nó hỗ trợ image size lên tới 16EB, tích hợp chặt chẽ với Linux kernel driver và cung cấp nhiều tính năng quan trọng như snapshot tốc độ cao, copy-on-write cloning, thin provisioning cùng dynamic resize. Ngoài ra RBD còn hỗ trợ in-memory caching để nâng cao hiệu năng đáng kể.



## Vận hành RBD 
```bash
rbd -p POOL_NAME ls -l #Liệt kê các block device của pool cụ thể 
rbd create -p POOL_NAME VOLUME_NAME -size SIZE # Tạo 1 block device 
rbd showmapped # Xem mapping của các device
```

## RBD Configuration
### Ceph RBD Mirroring cho Disaster Recovery
- Ceph RBD mirroring là cơ chế nhân bản các block device image giữa hai cụm Ceph để phục vụ disaster recovery, với mục tiêu chính là giảm downtime và giảm data loss khi site chính gặp sự cố. Điểm đáng nhớ ở đây là nó không chỉ nói về “sao chép dữ liệu”, mà nói về cách xây dựng một lớp DR thực sự cho private cloud, nơi RTO và RPO được xem như chỉ số vận hành cốt lõi chứ không phải chỉ là khái niệm lý thuyết. Ceph RBD mirroring có hai kiểu replication chính: one-way theo mô hình active-passive và two-way theo mô hình active-active; đồng thời có hai cách đồng bộ là journal-based cho near real-time replication và snapshot-based cho việc đồng bộ theo chu kỳ.
- Điều kiện tiên quyết đầu tiên là phải có ít nhất hai cụm Ceph khỏe mạnh, đặt ở hai data center khác nhau và nối với nhau bằng đường truyền có băng thông cao, ổn định. 
    - daemon rbd-mirror phải kết nối được đồng thời tới cả local và remote cluster, nên network giữa hai site không thể coi là phụ trợ mà phải được thiết kế như một phần của DR architecture. 
    - [Ceph documentation](https://docs.ceph.com/en/mimic/rbd/rbd-mirroring/) cũng yêu cầu băng thông đủ lớn cho mirroring workload,  khuyến nghị tối thiểu nên có kết nối 10 Gbps.
        - Ví dụ 1 TB qua 1 Gbps mất khoảng 3 giờ, trong khi 10 Gbps rút xuống khoảng 20 phút. Với synchronous stretch cluster thì RTT giữa hai site không nên vượt quá 10 ms, còn asynchronous mirroring thì chịu latency tốt hơn và phù hợp hơn cho triển khai địa lý xa.

- Ở tầng cấu hình, RBD mirroring không thể bật “cho xong” mà phải đồng bộ đúng feature và pool giữa hai cluster. Các pool cần có tên tương ứng trên cả hai bên; nếu dùng journal-based mirroring thì journaling phải được bật, và image cần có exclusive-lock cùng journaling để đảm bảo chỉ một client ghi tại một thời điểm và replica luôn crash-consistent. 
    - Một điểm rất thực tế là journaling có thể làm write latency tăng gần gấp đôi, nên đây là trade-off giữa consistency và hiệu năng chứ không phải cấu hình miễn phí. 
    - Chúng ta cũng cần phân biệt rõ pool mode và image mode: pool mode áp dụng cho toàn bộ image trong pool, còn image mode cho phép chọn lọc từng image; riêng khi tích hợp với OpenStack Cinder thì cần cấu hình ở image mode.

- Quy trình triển khai thông thường theo các bước tham khảo sau :
    - Trước tiên là bật mirroring ở cấp pool bằng `rbd mirror pool enable`
        Trên cả hai cluster (hoặc cluster primary tùy mode), bật mirroring:
        ```bash
        rbd mirror pool enable <pool-name> pool
        ```
        Nếu muốn kiểm soát chi tiết từng image:
        ```bash
        rbd mirror pool enable <pool-name> image
        ```
        > `pool` mode → áp dụng cho toàn bộ image
        > `image` mode → chọn lọc (bắt buộc khi dùng với Cinder)
        Nếu dùng journal-based mirroring thì phải bật journaling cho images trong pool:
        ```bash
        rbd feature enable <pool-name>/<image-name> exclusive-lock,journaling
        ```
        => Đây là điều kiện bắt buộc để journal-based mirroring hoạt động.
    - Sau đó ta cần cấu hình peer cluster đơn giản bằng `rbd mirror peer add` để thiết lập trust và kết nối giữa hai cluster, đảm bảo rằng daemon rbd-mirror có thể giao tiếp với cả hai bên.
        Trên cluster A:
        ```bash
        rbd mirror pool peer add <pool-name> client.<user>@<remote-cluster>
        ```
        Hoặc dùng bootstrap token (cách phổ biến hơn):
        ```bash
        rbd mirror pool peer bootstrap create <pool-name> > token.txt
        ```
        Sau đó import vào cluster B:
        ```bash
        rbd mirror pool peer bootstrap import <pool-name> token.txt
        ```
        > Việc này thiết lập trust và kết nối giữa hai cluster, đảm bảo rằng daemon rbd-mirror có thể giao tiếp với cả hai bên.
    - Tiếp đó ta  triển khai rbd-mirror daemon để xử lý replication giữa hai cluster. 
        Trên node chạy mirroring:
        ```bash
        ceph orch apply rbd-mirror
        ```
        Hoặc nếu chạy thủ công:
        ```bash
        rbd-mirror --cluster <cluster-name>
        ```
        Với one-way mirroring, daemon chỉ cần đặt ở cluster secondary ( cluster B); với two-way mirroring thì phải có ở cả hai bên.

        > Việc tương thích phiên bản là rất quan trọng: không nên trộn các phiên bản Ceph server/client khác nhau một cách tùy tiện, và với Red Hat Ceph Storage 5 thì chỉ hỗ trợ containerized daemons.

    - Cuối sùng ta kiểm tra trạng thái mirroring 
        ```bash
        rbd mirror pool status <pool-name>
        rbd mirror image status <pool-name>/<image-name>
        ceph -s
        ```
        > Các chỉ số quan trọng cần theo dõi gồm replication lag (thời gian trễ giữa hai site), journal utilization (nếu dùng journal-based), network throughput giữa hai site, mirror image health, daemon connectivity và peer cluster availability.
    - Phần cuối cùng nhưng không kém phần quan trọng là failover và failback. Mirroring chỉ có ý nghĩa khi failover thực sự hoạt động khi site chính gặp sự cố. 
        Với planned failover, trình tự đúng là demote image ở site A rồi mới promote image ở site B để tránh split-brain. 
        ```bash
        rbd mirror image demote <pool>/<image>   # tại site A
        rbd mirror image promote <pool>/<image>  # tại site B
        ```
        
        Với emergency failover, có thể dùng --force khi promote, nhưng cách này có nguy cơ mất một phần dữ liệu tùy vào replication lag tại thời điểm sự cố. Sau khi promote xong, không chỉ kiểm tra image mà còn phải boot VM/container và xác minh ứng dụng hoạt động bình thường. Khi test, nên theo dõi ceph status, ceph -w, rbd mirror image status, rồi đo cả failover time lẫn failback time.
        ```bash
        rbd mirror image promote <pool>/<image> --force
        ```

        Failback sau khi site chính đã khôi phục thì phải đảm bảo rằng dữ liệu trên site phụ đã được đồng bộ hoàn toàn trước khi chuyển workload trở lại, tránh việc promote một image chưa kịp sync về site chính.
        ```bash
        rbd mirror image demote <pool>/<image>   # tại site B
        rbd mirror image promote <pool>/<image>  # tại site A
        ```
- Các lưu ý khi vận hành mirroring quan trọng giúp chuyển từ “có chạy” sang “chạy bền”. 
    - Ceph RBD mirroring cần được tune theo throughput thực tế của workload: 
        Network là bottleneck lớn nhất khi replication, nên network bandwidth phải lớn hơn hoặc ít nhất là bằng tổng write throughtout theo công thức 
        `network ≥ N × X + 20–30% buffer` 
        trong đó N là số image và X là write throughput trung bình của mỗi image, rồi cộng thêm khoảng 20–30% buffer để tránh nghẽn khi replication, client request và recovery traffic chồng lên nhau.

        Nếu không đáp ứng ít nhất theo công thức thì replication lag có thể tăng dựa trên độ lớn của image và tốc độ ghi, dẫn đến RPO tăng và nguy cơ mất dữ liệu cao hơn khi failover. 
        
    Hai cluster được khuyến nghị nên có capacity và performance tương đương, journaling cần được cân đối giữa độ lớn journal và mức memory dùng, còn nhiều image hoặc write throughput cao thì nên phân bổ nhiều rbd-mirror daemon trên nhiều node để chia tải. Khi hệ thống mở rộng, CRUSH rules cũng cần được rà soát để tránh hotspot và giữ placement group phân bố đều.

    - Giám sát là phần không thể bỏ qua. Nếu sử dụng Ceph thì có thể dùng dùng Ceph Dashboard kết hợp Prometheus, Grafana và Alertmanager, bật Prometheus module trong ceph-mgr, cài node-exporter trên từng node để có cả metric của Ceph lẫn metric hạ tầng. Các chỉ số cần theo dõi gồm replication lag, **journal utilization**, network throughput giữa hai site, **mirror image health**, **daemon connectivity** và **peer cluster availability**. Điểm rất thực tế là alert nên được gắn với ngưỡng RPO, tức là nếu replication chậm vượt quá mức chấp nhận được thì phải báo ngay.

- Phần test DR mới là chỗ giúp biến mirroring thành một cơ chế đáng tin chứ không phải chỉ là replication trên giấy. Khuyến nghị trước khi failover thử nghiệm thì nên sync luôn VM và container configuration sang site phụ, chẳng hạn bằng rsync, để khi image được promote lên thì workload thực sự boot được. Với planned failover, trình tự đúng là demote image ở site A rồi mới promote image ở site B để tránh split-brain. Với emergency failover, có thể dùng --force khi promote, nhưng cách này có nguy cơ mất một phần dữ liệu tùy vào replication lag tại thời điểm sự cố. Sau khi promote xong, không chỉ kiểm tra image mà còn phải boot VM/container và xác minh ứng dụng hoạt động bình thường. Khi test, nên theo dõi ceph status, ceph -w, rbd mirror image status, rồi đo cả failover time lẫn failback time.

> RBD mirroring là một nền tảng tốt cho disaster recovery trong private OpenStack cloud, nhưng không thay thế hoàn toàn các lớp bảo vệ khác. Với workload cực kỳ quan trọng, nên bổ sung off-site backups để giảm thêm rủi ro dữ liệu. Nghĩa là mirroring nên được xem như một lớp DR chính, còn backup là lớp an toàn bổ sung cho các tình huống đặc biệt.

- Những ý cốt lõi cần nắm
    - Ceph RBD mirroring là cơ chế replicate block images giữa hai cluster để làm disaster recovery. Tuy nhiên Mirroing khác hoàn toàn với backup, nó tập trung vào RTO và RPO thấp hơn là chỉ sao chép dữ liệu.
    - Có hai mode chính: **one-way active-passive** và **two-way active-active**.
    - Có hai phương pháp: **journal-based** và **snapshot-based**, mỗi cách có trade-off riêng về độ tươi của dữ liệu và latency.
    - DR đúng nghĩa cần hai cluster khỏe, network mạnh, latency phù hợp, và monitoring liên tục.
    - Failover phải được test định kỳ, vì replication mà không kiểm thử thì chưa phải DR hoàn chỉnh.

## RBD Troubleshooting
### Glance Image pool bị lỗi 


### Lỗi không thu hồi được dung lượng 
- Mô tả : Sau khi xóa dữ liệu bên trong VM, dung lượng trên cụm Ceph (OSD) không giảm .
- Nguyên nhân dự đoán :
    - Guest OS không gửi lệnh fstrim hoặc không được cấu hình mount với tùy chọn discard.
    - Tính năng alloc_hint của BlueStore đôi khi không hoạt động tối ưu trên các dòng SSD cũ.
- Cách xử lý :
    - Tại Client (VM): Đảm bảo dùng lệnh fstrim -v / định kỳ hoặc thêm discard vào /etc/fstab.
    - Tại RBD Level: Kiểm tra xem image có enable feature object-map và fast-diff chưa: rbd feature enable <pool>/<image> object-map fast-diff.
    - Tại Ceph Level: Kiểm tra thông số bluestore_min_alloc_size. Nếu dùng SSD, hãy đảm bảo giá trị này nhỏ (thường là 4K) để tránh lãng phí dung lượng khi lưu các file nhỏ.

### Lỗi Khóa Độc Quyền & Treo I/O
- Mô tả : Một Client khác cố gắng truy cập vào Image đang bị "khóa" bởi một Client đã chết nhưng chưa hết thời gian timeout (Watcher vẫn còn tồn tại).
- Nguyên nhân dự đoán : Do sự tranh chấp này nên I/O của hệ thống không xử lý được dẫn đến dồn request và bị treoo
- Cách xử lý: 
    - Kiểm tra trạng thái khóa: rbd status <pool>/<image>
    - Xác định Watcher: rbd device list hoặc ceph osd blacklist list.
    - Gỡ khóa thủ công (Cẩn trọng): Nếu chắc chắn Client cũ đã chết, hãy xóa Watcher: rbd lock remove <pool>/<image> <lock-id> <client-id>
    - Tối ưu: Giảm client_mount_timeout trong cấu hình để hệ thống phát hiện Client chết nhanh hơn

### Hiệu Năng Suy Giảm Khi Dùng Snapshot Quá Nhiều
- Mô tả : việc duy trì >50 snapshots trên một image RBD khiến độ trễ (latency) tăng vọt khi thực hiện các tác vụ ghi (Write).
- Nguyên nhân dự đoán : Cơ chế "Copy-on-Write" phải kiểm tra qua quá nhiều lớp snapshot trước khi ghi dữ liệu mới.
- Cách xử lý:
    - Giới hạn Snapshot: Duy trì dưới 15-20 snapshots cho mỗi image.

    - Dùng tính năng Flatten: Nếu clone một image từ snapshot, hãy thực hiện rbd flatten sau khi clone để cắt đứt liên kết với image cha, giúp tăng hiệu năng đọc/ghi độc lập.
    - Lịch trình xóa: Sử dụng các script tự động xóa snapshot cũ thay vì để tích tụ quá lâu.

### Lỗi Đồng Bộ RBD Mirroring
- Mô tả : Hệ thống báo lỗi khi thực hiện tiến trình đồng bộ 
- Nguyên nhân dự đoán : Metadata của image ở site chính và site phụ không khớp do lỗi mạng giữa chừng, hoặc rbd-mirror daemon bị thiếu tài nguyên.
- Cách xử lý:
    - Kiểm tra trạng thái: rbd mirror image status <pool>/<image>

    - Restart Replayer: Thường thì restart daemon rbd-mirror sẽ giải quyết được 80% trường hợp.

    - Resync: Nếu image bị "Split-brain", buộc phải thực hiện resync: rbd mirror image resync <pool>/<image>

    - Tăng Buffer: Tăng rbd_mirroring_replay_delay để cho phép hệ thống có thời gian xử lý các biến động mạng ngắn hạn.

### Lỗi Treo Trong Quá Trình "RBD Migration" (Live Migration)

- Mô tả : Từ bản Pacific, Ceph giới thiệu tính năng Migration cho phép chuyển Image giữa các Pool mà không cần tắt VM. Tuy nhiên trong quá trình prepare hoặc execute, nếu đường truyền mạng chập chờn, trạng thái image có thể bị kẹt ở "merging" hoặc "error". Lúc này, dữ liệu nằm ở cả 2 pool và việc xóa pool cũ sẽ làm mất dữ liệu pool mới.
- Nguyên nhân dự đoán : 

- Cách xử lý: Luôn kiểm tra rbd migration status. Nếu bị kẹt, tuyệt đối không dùng lệnh force. Hãy dùng rbd migration abort để rollback về pool gốc trước khi thử lại.

### Persistent Client-side Cache (PCC) Corruption
- Mô tả : Tính năng cho phép dùng SSD cục bộ trên node Client (như node Compute của OpenStack) để làm cache cho RBD.
- Nguyên nhân dự đoán : Nếu node Client bị mất điện đột ngột, dữ liệu trong PCC chưa kịp flush về Ceph Cluster có thể bị hỏng (corruption), dẫn đến việc filesystem bên trong VM bị lỗi "Read-only".
- Cách xử lý: Trong môi trường không có UPS hoặc nguồn điện không ổn định, hãy set rbd_persistent_cache_mode = writethrough (chỉ cache đọc) thay vì writeback.


### Lỗi CSI Snapshot "Orphan" (Kubernetes Environment)
- Mô tả : Dành cho các hệ thống dùng Ceph làm Storage Class cho K8s. Khi xóa một PVC kèm theo Snapshot, đôi khi Ceph CSI không xóa hết các bản clone ẩn (clone v2), để lại các object "mồ côi" chiếm dung lượng mà không hiển thị trong lệnh rbd ls.
- Nguyên nhân dự đoán 
- Cách xử lý: Sử dụng công cụ rbd du trên toàn pool để tìm các image có tên lạ (thường có prefix của CSI) và dọn dẹp thủ công bằng rbd rm.