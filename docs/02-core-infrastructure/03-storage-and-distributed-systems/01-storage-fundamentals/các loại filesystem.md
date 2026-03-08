## So sánh các Filesystem
### Btrfs (B-tree File System)
- Ưu điểm:

    + Hiệu năng tốt nhất trong ba lựa chọn
    + Hỗ trợ copy-on-write, lý tưởng cho VM provisioning và cloning
    + Writable snapshots tích hợp
    + Transparent compression
    + Pervasive checksums đảm bảo tính toàn vẹn dữ liệu
    + Quản lý multidevice tích hợp trong filesystem
    + XATTRs hiệu quả và inline data cho file nhỏ
    + SSD-aware optimization
    + Online fsck (file system check)

- Nhược điểm:

    + Chưa ổn định cho môi trường production
    + Chỉ phù hợp cho test deployment

### XFS
- Ưu điểm:

    + Filesystem ổn định, tin cậy và được kiểm chứng
    + Khuyến nghị cho Ceph production cluster
    + Được sử dụng rộng rãi nhất trong các triển khai Ceph
    + Hỗ trợ XATTRs tốt hơn ext4

- Nhược điểm:

    + Kém Btrfs về một số tính năng tiên tiến
    + Vấn đề hiệu năng khi mở rộng metadata
    + Là journaling filesystem, tạo overhead khi ghi dữ liệu (ghi vào journal trước, sau đó mới ghi vào filesystem)

### ext4 (Fourth Extended Filesystem)
- Ưu điểm:

    + Hỗ trợ journaling filesystem
    + Tương thích tốt với Ceph OSD

- Nhược điểm:

    + Không thân thiện bằng XFS cho Ceph
    + Hạn chế về XATTRs: số lượng bytes lưu trữ XATTRs bị giới hạn
    + Hiệu năng kém hơn Btrfs và XFS
    + Không phù hợp làm filesystem chính cho OSD

## Extended Attributes (XATTRs)
XATTRs là yếu tố then chốt cho hoạt động của Ceph OSD:

- Lưu trữ metadata và trạng thái của objects
- Cung cấp thông tin nhanh chóng mà không cần đọc toàn bộ object
- Btrfs và XFS hỗ trợ dung lượng XATTRs lớn hơn `ext4` đáng kể
- `ext4` bị hạn chế về số byte có thể lưu trong XATTRs, không đủ cho nhiều trường hợp sử dụng