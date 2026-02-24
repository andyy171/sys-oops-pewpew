# Giả lập các trường hợp slow ops và quy trình trace mẫu 

## Các thông số cơ sở trước khi giả lập 

- Sức khỏe tổng quan của cụm :


"Tôi đang quản trị cụm Ceph (Cephadm) 3 node, mỗi node có 2 OSD (30GB/OSD). Cụm này tích hợp với OpenStack (Kolla-Ansible). Hãy giúp tôi xây dựng kịch bản chi tiết cho 4 trường hợp Slow Operations theo cấu trúc: Mô phỏng lỗi -> Nhận diện log -> Xử lý lỗi.

Trường hợp 1: Disk I/O Saturation (Quá tải ổ đĩa)
Mô phỏng: Cách dùng lệnh fio hoặc dd trực tiếp lên ổ đĩa vật lý của OSD trên node02 để đẩy %util lên 100%, ép Ceph ghi log slow operation observed.

Nhận diện: Cách xem ceph -s và tìm dòng log _txc_committed_kv trong OSD container.

Xử lý: Cách giới hạn I/O hoặc điều chỉnh osd_disk_thread_timeout.

Trường hợp 2: Network Latency (Nghẽn mạng Cluster)
Mô phỏng: Cách dùng lệnh tc (Traffic Control) trên ceph-node01 để tạo độ trễ 500ms cho card mạng dùng làm Cluster Network (phục vụ replication).

Nhận diện: Cách phát hiện OSD bị heartbeat_timeout và trạng thái Slow Ops do không thể replicate dữ liệu sang node khác.

Xử lý: Kiểm tra MTU, xóa quy tắc tc và tối ưu net_priority.

Trường hợp 3: OpenStack-Ceph Integration Slowdown (Nghẽn từ phía Client)
Mô phỏng: Cách tạo hàng loạt Volume/Snapshot từ OpenStack (Cinder) trong khi OSD đang Rebalance để làm treo I/O của Glance/Cinder.

Nhận diện: Cách đọc log trong container cinder_volume trên node Kolla khi gặp lỗi Request timed out từ Ceph.

Xử lý: Điều chỉnh rbd_cache và các thông số osd_op_threads để ưu tiên Client IO.

Trường hợp 4: Metadata (RocksDB/WAL) Latency
Mô phỏng: Cách lấp đầy dung lượng OSD hoặc ép OSD thực hiện dọn dẹp (Compaction) liên tục bằng cách xóa/ghi hàng triệu object nhỏ.

Nhận diện: Phân tích bảng RocksDB Stats trong log OSD để tìm Stalls.

Xử lý: Cách tối ưu bluestore_rocksdb_options cho môi trường Lab ổ đĩa nhỏ (30GB).

Yêu cầu chung:

Các lệnh mô phỏng phải chạy được trên Ubuntu/CentOS có cài cephadm.

Phải hướng dẫn cách vào ceph shell hoặc docker/podman exec để xem log OSD.

Giải thích tác động của từng lỗi này lên Dashboard của OpenStack (Horizon)."