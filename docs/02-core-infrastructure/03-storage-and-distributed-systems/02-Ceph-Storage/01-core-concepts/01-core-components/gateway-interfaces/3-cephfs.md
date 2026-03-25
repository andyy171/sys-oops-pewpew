# CephFS - Giao Diện Lưu Trữ File
CephFS là hệ thống file POSIX-compliant phân tán, cho phép nhiều client truy cập đồng thời vào cùng một không gian lưu trữ. CephFS rất phù hợp với các workload truyền thống như home directories, shared storage, kho lưu trữ hoặc các ứng dụng HPC cần filesystem dùng chung. CephFS lưu dữ liệu và metadata riêng biệt (data pool và metadata pool) để tối ưu hiệu năng và độ tin cậy. Client có thể mount CephFS thông qua Linux kernel driver hoặc ceph-fuse (filesystem in user space). Ngoài ra còn có thể sử dụng phần mềm thứ ba như Ganesha cho NFS và Samba cho SMB/CIFS. CephFS cũng tích hợp tốt với Hadoop (HDFS) thông qua libcephfs.
Thành phần quan trọng nhất của CephFS là MDS (Metadata Server) – chịu trách nhiệm quản lý metadata như cấu trúc thư mục và quyền truy cập. CephFS hỗ trợ multiple MDS theo mô hình active/standby để tăng khả năng chịu lỗi và scale. Các tính năng chính của CephFS gồm snapshots, multiple filesystems support cùng sự phân biệt rõ ràng giữa data pool và metadata pool. CephFS cũng hỗ trợ các tính năng như POSIX ACLs, extended attributes, và tích hợp với các công cụ quản lý dữ liệu như Hadoop. CephFS là giải pháp lý tưởng cho các ứng dụng cần filesystem dùng chung với khả năng mở rộng cao và độ tin cậy vượt trội.


## Vận hành CephFS
```bash
ceph fs ls

name: cephfs, metadata pool: cephfs_metadata, data pools: [cephfs_data ]

# Hiển thị trạng thái của mọi thành phần của CephFS
ceph fs status
#Example
cephfs - 0 clients <<-- Containers or hosts attached to cephfs are represented here
======
+------+--------+-----------+---------------+-------+-------+
| Rank | State  |    MDS    |    Activity   |  dns  |  inos |
+------+--------+-----------+---------------+-------+-------+
|  0   | active | ceph-2    | Reqs:    0 /s |  10   |   13  |   <<-- Active server
+------+--------+-----------+---------------+-------+-------+
+-----------------+----------+-------+-------+
|       Pool      |   type   |  used | avail |
+-----------------+----------+-------+-------+
| cephfs_metadata | metadata | 1536k | 13.1G |
|   cephfs_data   |   data   |   0   | 13.1G |  <<-- Where files get stored
+-----------------+----------+-------+-------+
+-------------+
| Standby MDS |
+-------------+
|   ceph-1    |
|   ceph-3    |
+-------------+
MDS version: ceph version 14.2.0-300-gacd2f2b9e1 (acd2f2b9e196222b0350b3b59af9981f91706c7f) nautilus (stable)

```





## CephFS Troubleshooting
### Lỗi MDS kẹt ở trạng thái Replaying hoặc Starting vô thời hạn
- Mô tả lỗi: Một trong những kịch bản gây ám ảnh nhất cho người vận hành CephFS là khi Metadata Server (MDS) chính gặp sự cố và tiến trình dự phòng (Standby) nhảy lên thay thế nhưng lại bị kẹt ở trạng thái "replaying" trong nhiều giờ, thậm chí nhiều ngày. Trong thời gian này, toàn bộ hệ thống tệp bị đóng băng, mọi yêu cầu I/O từ phía Client đều bị treo (hang) và lệnh `ceph -s` sẽ báo cáo lỗi `mds ... is stuck`. Lỗi này đặc biệt phổ biến trong các cụm Pacific và Quincy khi hệ thống tệp chứa hàng chục triệu tệp tin nhỏ hoặc cấu trúc thư mục cực kỳ sâu.

- Nguyên nhân dự đoán: Căn nguyên của vấn đề thường nằm ở sự phình to bất thường của Metadata Journal (nhật ký siêu dữ liệu). Khi MDS thực hiện ghi các thay đổi, nó lưu vào journal trước khi flush xuống đĩa. Nếu cụm OSD lưu trữ Metadata Pool gặp độ trễ lớn hoặc nếu có quá nhiều thao tác xóa tệp tin đồng thời, journal sẽ chứa một lượng lớn các phân đoạn (segments) chưa được dọn dẹp. Khi MDS khởi động lại, nó phải đọc và tái hiện lại toàn bộ nhật ký này vào RAM. Nếu nhật ký bị hỏng một vài bit do lỗi đĩa hoặc nếu dung lượng RAM cấp cho MDS không đủ để chứa cấu trúc dữ liệu đang tái hiện, tiến trình sẽ rơi vào vòng lặp vô tận hoặc crash liên tục.

- Cách xử lý: Để giải quyết triệt để, người quản trị cần sử dụng công cụ cephfs-journal-tool để kiểm tra tính toàn vẹn của nhật ký. Trong trường hợp journal bị hỏng, có thể buộc phải cắt bỏ phần lỗi bằng lệnh event rollback hoặc journal reset, mặc dù điều này có rủi ro mất một phần dữ liệu siêu dữ liệu gần nhất. Để phòng ngừa cho môi trường Production, cần giới hạn kích thước nhật ký thông qua tham số mds_log_max_segments và đảm bảo Metadata Pool luôn nằm trên các ổ đĩa NVMe có chỉ số IOPS cực cao. Ngoài ra, việc duy trì ít nhất hai MDS ở trạng thái Standby-Replay (luôn đọc journal song song với MDS chính) sẽ giúp quá trình chuyển giao (failover) diễn ra gần như tức thì.


### Trì trệ thu hồi Capability (Caps) và hiện tượng Client bị trục xuất (Eviction)
- Mô tả lỗi: Trong các phiên bản từ Pacific đến Reef, cộng đồng thường xuyên báo cáo về lỗi MDS chuyên trách báo cáo: "client is failing to respond to cache pressure". Lúc này, hiệu năng của Client bị giảm sút nghiêm trọng, các thao tác mở file hoặc liệt kê thư mục mất vài chục giây để phản hồi. Nếu tình trạng này kéo dài, MDS sẽ tự động trục xuất (evict) Client đó để bảo vệ sự ổn định của cụm, dẫn đến việc các ứng dụng đang chạy trên Client bị lỗi "Input/Output error" và mất kết nối hoàn toàn với mount point.
- Nguyên nhân dự đoán: Lỗi này xuất phát từ cơ chế quản lý quyền hạn (Capabilities) giữa MDS và Client. Khi một Client mở quá nhiều file, MDS sẽ cấp cho nó các "caps" để cache thông tin tại địa phương. Khi RAM của MDS chạm ngưỡng giới hạn, nó sẽ yêu cầu Client trả lại các caps không dùng đến. Tuy nhiên, nếu Client đang bận xử lý tác vụ nặng hoặc do lỗi mạng khiến gói tin thu hồi bị thất lạc, MDS sẽ coi Client đó là "không phản hồi". Trên các bản Quincy và Reef, lỗi này còn bị trầm trọng hóa bởi cơ chế "Lazy Cap Wanted" khi Client không giải phóng inode kịp thời khỏi bộ nhớ đệm của hệ điều hành.
- Cách xử lý: Cách xử lý nhanh nhất là thực hiện thủ công lệnh `ceph tell mds.<id> session evict` đối với Client gây nghẽn để giải phóng tài nguyên cho các Client khác. Tuy nhiên, về lâu dài, cần điều chỉnh tham số `mds_cache_memory_limit` lên mức đủ lớn (tối thiểu 8GB-16GB cho mỗi 1 triệu file active) và tinh chỉnh `mds_recall_max_caps` để kiểm soát tốc độ thu hồi quyền hạn một cách từ từ thay vì dồn dập. Việc nâng cấp lên Squid (19.x) cũng là một giải pháp vì bản này đã cải thiện đáng kể thuật toán thu hồi caps, giúp giảm bớt sự xung đột giữa MDS và các Client có kết nối mạng kém ổn định.
    
### Hiện tượng tràn Cache MDS và lỗi OOM Killer trong môi trường Multi-Active
- Mô tả lỗi: Khi triển khai cấu hình Multi-Active MDS (nhiều MDS cùng chạy để chia tải), người dùng thường gặp hiện tượng một MDS chiếm dụng RAM vượt xa giới hạn cấu hình, trong khi các MDS khác lại khá rảnh rỗi. Khi RAM vật lý bị cạn kiệt, hệ điều hành sẽ kích hoạt OOM Killer để tiêu diệt tiến trình MDS, gây ra chuỗi lỗi dây chuyền và làm gián đoạn toàn bộ dịch vụ file system. Lỗi này cực kỳ khó chịu vì nó không xuất hiện ngay lập tức mà tích lũy dần theo thời gian vận hành.
- Nguyên nhân dự đoán: Nguyên nhân chủ yếu nằm ở sự phân mảnh Metadata và cơ chế cân bằng tải thư mục (Balancing). Trong phiên bản Pacific và Quincy, trình cân bằng tải đôi khi gặp khó khăn trong việc di chuyển các thư mục bận rộn (hot directories) từ MDS này sang MDS khác, dẫn đến một MDS phải quản lý quá nhiều "dentry" và "inode" trong cache. Hơn nữa, việc giải phóng RAM của MDS không diễn ra ngay lập tức khi tệp tin đóng lại; nó phụ thuộc vào cơ chế dọn dẹp của thư viện `tcmalloc`. Nếu `tcmalloc` không trả lại RAM cho hệ thống kịp thời, dung lượng bộ nhớ ảo của MDS sẽ tăng liên tục cho đến khi sập nguồn.
- Cách xử lý: Để đảm bảo ổn định cho Production, người quản trị nên sử dụng tính năng "Directory Pinning" để chủ động gán các thư mục con có tải lượng lớn vào các MDS cụ thể, thay vì để hệ thống tự cân bằng. Ngoài ra, việc thiết lập tham số môi trường `TCMALLOC_RELEASE_RATE` lên giá trị cao hơn sẽ buộc MDS trả lại RAM cho hệ điều hành nhanh hơn. Trên phiên bản Reef và Squid, cộng đồng khuyến nghị sử dụng lệnh `ceph config set mds mds_cache_trim_threshold 256` để thúc đẩy việc dọn dẹp cache quyết liệt hơn khi MDS bắt đầu cảm thấy áp lực về bộ nhớ.
### Lỗi Snap-trimming đình trệ gây cạn kiệt dung lượng Metadata Pool
- Mô tả lỗi: CephFS hỗ trợ tính năng snapshot (bản ghi nhanh) rất mạnh mẽ, nhưng việc xóa snapshot thường dẫn đến một "cơn ác mộng" về hiệu năng. Sau khi xóa một snapshot lớn, người dùng thấy dung lượng không được thu hồi ngay, đồng thời hiệu năng ghi của toàn bộ cụm giảm xuống mức tối thiểu. Trong một số trường hợp báo cáo từ bản Pacific đến Reef, tiến trình xóa snapshot (snap-trimming) thậm chí bị kẹt hoàn toàn, khiến Metadata Pool bị đầy và ngăn cản mọi thao tác tạo file mới trên hệ thống.
- Nguyên nhân dự đoán: Quá trình snap-trimming trong CephFS cực kỳ tiêu tốn tài nguyên vì nó phải quét qua hàng triệu đối tượng để tìm các khối dữ liệu không còn được tham chiếu bởi bất kỳ snapshot nào khác. Lỗi đình trệ thường xảy ra khi có sự không nhất quán giữa bảng Snapshot (SnapRealm) và dữ liệu thực tế trên OSD. Nếu Metadata Pool và Data Pool có sự chênh lệch lớn về hiệu năng (ví dụ Metadata trên NVMe còn Data trên HDD), việc ghi nhật ký xóa sẽ bị nghẽn cổ chai tại các ổ HDD, làm cho hàng đợi snap-trimming phình to và chặn đứng các tiến trình metadata khác.
- Cách xử lý: Giải pháp hiệu quả nhất cho môi trường Prod là thực hiện điều tiết (throttling) quá trình xóa thông qua tham số `osd_pg_max_concurrent_snap_trims`. Việc giảm số lượng tiến trình xóa đồng thời sẽ giúp giữ lại băng thông cho các tác vụ I/O của người dùng. Nếu tiến trình bị kẹt hoàn toàn, người quản trị cần sử dụng lệnh `ceph mds scrub` để rà soát và sửa lỗi cấu trúc snapshot. Đặc biệt lưu ý từ phiên bản Reef trở đi, nên kích hoạt tính năng `snap_schedule` để việc tạo và xóa snapshot diễn ra theo các cửa sổ thời gian thấp điểm, tránh gây xung đột tài nguyên vào giờ cao điểm của hệ thống.