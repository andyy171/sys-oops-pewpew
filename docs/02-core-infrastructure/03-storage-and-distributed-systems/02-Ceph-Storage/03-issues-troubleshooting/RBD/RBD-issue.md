# Các issues liên quan đến RBD

## Glance Image pool bị lỗi 


## Lỗi không thu hồi được dung lượng 
- Mô tả : Sau khi xóa dữ liệu bên trong VM, dung lượng trên cụm Ceph (OSD) không giảm .
- Nguyên nhân dự đoán :
    - Guest OS không gửi lệnh fstrim hoặc không được cấu hình mount với tùy chọn discard.
    - Tính năng alloc_hint của BlueStore đôi khi không hoạt động tối ưu trên các dòng SSD cũ.
- Cách xử lý :
    - Tại Client (VM): Đảm bảo dùng lệnh fstrim -v / định kỳ hoặc thêm discard vào /etc/fstab.
    - Tại RBD Level: Kiểm tra xem image có enable feature object-map và fast-diff chưa: rbd feature enable <pool>/<image> object-map fast-diff.
    - Tại Ceph Level: Kiểm tra thông số bluestore_min_alloc_size. Nếu dùng SSD, hãy đảm bảo giá trị này nhỏ (thường là 4K) để tránh lãng phí dung lượng khi lưu các file nhỏ.

## Lỗi Khóa Độc Quyền & Treo I/O
- Mô tả : Một Client khác cố gắng truy cập vào Image đang bị "khóa" bởi một Client đã chết nhưng chưa hết thời gian timeout (Watcher vẫn còn tồn tại).
- Nguyên nhân dự đoán : Do sự tranh chấp này nên I/O của hệ thống không xử lý được dẫn đến dồn request và bị treoo
- Cách xử lý: 
    - Kiểm tra trạng thái khóa: rbd status <pool>/<image>
    - Xác định Watcher: rbd device list hoặc ceph osd blacklist list.
    - Gỡ khóa thủ công (Cẩn trọng): Nếu chắc chắn Client cũ đã chết, hãy xóa Watcher: rbd lock remove <pool>/<image> <lock-id> <client-id>
    - Tối ưu: Giảm client_mount_timeout trong cấu hình để hệ thống phát hiện Client chết nhanh hơn

## Hiệu Năng Suy Giảm Khi Dùng Snapshot Quá Nhiều
- Mô tả : việc duy trì >50 snapshots trên một image RBD khiến độ trễ (latency) tăng vọt khi thực hiện các tác vụ ghi (Write).
- Nguyên nhân dự đoán : Cơ chế "Copy-on-Write" phải kiểm tra qua quá nhiều lớp snapshot trước khi ghi dữ liệu mới.
- Cách xử lý:
    - Giới hạn Snapshot: Duy trì dưới 15-20 snapshots cho mỗi image.

    - Dùng tính năng Flatten: Nếu clone một image từ snapshot, hãy thực hiện rbd flatten sau khi clone để cắt đứt liên kết với image cha, giúp tăng hiệu năng đọc/ghi độc lập.
    - Lịch trình xóa: Sử dụng các script tự động xóa snapshot cũ thay vì để tích tụ quá lâu.

## Lỗi Đồng Bộ RBD Mirroring
- Mô tả : Hệ thống báo lỗi khi thực hiện tiến trình đồng bộ 
- Nguyên nhân dự đoán : Metadata của image ở site chính và site phụ không khớp do lỗi mạng giữa chừng, hoặc rbd-mirror daemon bị thiếu tài nguyên.
- Cách xử lý:
    - Kiểm tra trạng thái: rbd mirror image status <pool>/<image>

    - Restart Replayer: Thường thì restart daemon rbd-mirror sẽ giải quyết được 80% trường hợp.

    - Resync: Nếu image bị "Split-brain", buộc phải thực hiện resync: rbd mirror image resync <pool>/<image>

    - Tăng Buffer: Tăng rbd_mirroring_replay_delay để cho phép hệ thống có thời gian xử lý các biến động mạng ngắn hạn.

## Lỗi Treo Trong Quá Trình "RBD Migration" (Live Migration)

- Mô tả : Từ bản Pacific, Ceph giới thiệu tính năng Migration cho phép chuyển Image giữa các Pool mà không cần tắt VM. Tuy nhiên trong quá trình prepare hoặc execute, nếu đường truyền mạng chập chờn, trạng thái image có thể bị kẹt ở "merging" hoặc "error". Lúc này, dữ liệu nằm ở cả 2 pool và việc xóa pool cũ sẽ làm mất dữ liệu pool mới.
- Nguyên nhân dự đoán : 

- Cách xử lý: Luôn kiểm tra rbd migration status. Nếu bị kẹt, tuyệt đối không dùng lệnh force. Hãy dùng rbd migration abort để rollback về pool gốc trước khi thử lại.

## Persistent Client-side Cache (PCC) Corruption
- Mô tả : Tính năng cho phép dùng SSD cục bộ trên node Client (như node Compute của OpenStack) để làm cache cho RBD.
- Nguyên nhân dự đoán : Nếu node Client bị mất điện đột ngột, dữ liệu trong PCC chưa kịp flush về Ceph Cluster có thể bị hỏng (corruption), dẫn đến việc filesystem bên trong VM bị lỗi "Read-only".
- Cách xử lý: Trong môi trường không có UPS hoặc nguồn điện không ổn định, hãy set rbd_persistent_cache_mode = writethrough (chỉ cache đọc) thay vì writeback.


## Lỗi CSI Snapshot "Orphan" (Kubernetes Environment)
- Mô tả : Dành cho các hệ thống dùng Ceph làm Storage Class cho K8s. Khi xóa một PVC kèm theo Snapshot, đôi khi Ceph CSI không xóa hết các bản clone ẩn (clone v2), để lại các object "mồ côi" chiếm dung lượng mà không hiển thị trong lệnh rbd ls.
- Nguyên nhân dự đoán 
- Cách xử lý: Sử dụng công cụ rbd du trên toàn pool để tìm các image có tên lạ (thường có prefix của CSI) và dọn dẹp thủ công bằng rbd rm.