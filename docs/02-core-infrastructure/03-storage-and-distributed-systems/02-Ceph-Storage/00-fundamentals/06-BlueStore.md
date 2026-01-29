# BlueStore 
## Tổng quan
- BlueStore là backend lưu trữ mặc định cho Ceph OSD kể từ bản Luminous (Ceph 12.2.z). Đây là động cơ lưu trữ ở không gian người dùng, quản lý dữ liệu trực tiếp trên thiết bị khối thô mà không cần hệ thống tệp trung gian. Cách tiếp cận này khắc phục hạn chế của FileStore cũ, như chi phí hiệu suất từ lớp trừu tượng hóa hệ thống tệp và phạt viết kép. 

![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/bluestore-2.png)

- BlueStore tích hợp RocksDB để quản lý metadata, hỗ trợ nén inline và kiểm tra checksum cho tính toàn vẹn dữ liệu, đồng thời cho phép cấu hình đa thiết bị để lưu trữ phân tầng (ví dụ: HDD cho dữ liệu, SSD cho metadata). Nó được tối ưu hóa cho khối lượng công việc hiện đại, bao gồm lưu trữ khối, đối tượng và tệp, với tính năng như copy-on-write cho snapshot và pool mã hóa xóa. 
- BlueStore là backend khuyến nghị trong môi trường sản xuất bởi các nhà cung cấp như Red Hat và IBM, với FileStore đã bị loại bỏ ở các bản mới (ví dụ: Ceph Reef).

### Lý do cần BlueStore
FileStore cũ của Ceph dựa vào hệ thống tệp POSIX (như XFS, EXT4, Btrfs), dẫn đến thách thức tương thích, gánh nặng hiệu suất và vấn đề đáng tin cậy. BlueStore được phát triển để vượt qua bằng cách quản lý thiết bị thô trực tiếp, đơn giản hóa đường dẫn I/O và tối ưu cho lưu trữ hiện đại như SSD và NVMe.


#### **Vấn đề của FileStore**
- **Tương thích và Hack:** Cần hỗ trợ nhiều hệ thống tệp Linux, mỗi cái có hành vi không chuẩn (ví dụ: rename không idempotent), đòi hỏi workaround tùy chỉnh, tăng độ phức tạp phát triển.
- **Chi phí Hiệu suất:** Các tính năng POSIX không cần thiết cho Ceph (như duyệt thư mục nâng cao) thêm overhead. Hệ thống tệp áp đặt journaling riêng, dẫn đến "viết kép" – dữ liệu viết hai lần (journal của Ceph và của hệ thống tệp) – giảm một nửa thông lượng.
- **Không tối ưu cho Phần cứng Hiện đại:** Thiếu tối ưu hóa cho song song SSD/NVMe và CPU đa lõi. Sử dụng LevelDB (sau là RocksDB) cho metadata nhưng vẫn chịu indirection hệ thống tệp, gây tranh chấp queue và giảm hiệu quả.
- **Phóng đại Viết:** Overwrite đòi hỏi journaling cho ACID, phóng đại viết. Với LSM-tree như RocksDB, WAL riêng là thừa vì dữ liệu đã cấu trúc log.

#### **Lợi ích của BlueStore BlueStore**
BlueStore loại bỏ lớp hệ thống tệp, quản lý thiết bị qua allocator và dùng RocksDB cho metadata. Điều này giảm một nửa phóng đại viết, tận dụng song song SSD, và hỗ trợ phân tầng thiết bị linh hoạt (ví dụ: NVM cho WAL). Nó cũng cung cấp checksum dữ liệu đầy đủ và nén, bị hạn chế ở FileStore.

## Kiến trúc Tổng thể của BlueStore
BlueStore chia lưu trữ thành các module logic, quản lý thiết bị khối thô qua các thành phần tùy chỉnh. Ưu tiên đường dẫn viết ngắn để hiệu suất, dùng ngữ nghĩa append-only khi có thể. Dữ liệu lưu trực tiếp trên thiết bị, trong khi metadata (như mapping đối tượng) ở RocksDB, giao tiếp qua BlueFS – hệ thống tệp tối thiểu dành cho RocksDB.

![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/bluestore-1.png)

### Các Thành phần Chính

- RocksDB
   + là kho `key-value` hiệu suất cao nhúng trong BlueStore để quản lý metadata, bao gồm metadata đối tượng, OMAP Ceph, WAL và trạng thái allocator. 
   + Hỗ trợ transaction cho hoạt động ACID trong OSD. 
   + Dữ liệu RocksDB (SST và log) lưu qua BlueFS, cho phép đặt trên thiết bị nhanh hơn.
- BlueFS
    + BlueFS là hệ thống tệp không gian người dùng nhẹ, hỗ trợ RocksDB mà không overhead POSIX. 
    + Xử lý nhu cầu tệp của RocksDB (như WAL, DB, slow DB) với cấu trúc thư mục phẳng, viết append-only và metadata in-memory tải qua replay log khi mount. 
    + Hỗ trợ thu gom rác cho hiệu quả không gian và có thể trải nhiều thiết bị (ví dụ: NVM cho WAL, SSD cho SST nóng, HDD cho dữ liệu lạnh).
- Thiết bị Khối
    + BlueStore truy cập thiết bị vật lý (HDD/SSD/NVMe) trực tiếp dùng Linux AIO ở không gian người dùng.
    + Viết page-aligned và không buffer. Thread nội bộ aio_thread xử lý hoàn thành qua callback. 
    + Thiết bị có thể phân vùng: chính cho dữ liệu, WAL tùy chọn cho journaling, DB cho metadata RocksDB.
- Module Allocator
    + Allocator quản lý phân bổ không gian đĩa dùng bitmap với chỉ mục phân cấp cho hiệu quả. 
    + Theo dõi khối tự do, hỗ trợ extent (logic và vật lý), và giảm sử dụng bộ nhớ (~35MB mỗi 1TB). 
    + Granularity phân bổ cấu hình (mặc định 4KiB), giảm phóng đại không gian cho đối tượng nhỏ.

## Quản lý Thiết bị
- BlueStore hỗ trợ 1-3 thiết bị:
    + Chính (block): Lưu trữ dữ liệu chính.
    + WAL (block.wal): Log viết trước cho overwrite nhỏ; đồng vị nếu không riêng.
    + DB (block.db): Lưu RocksDB; khuyến nghị 1-4% kích thước chính (ví dụ: 40GB cho 1TB chính).

> Cấu hình cho phép phân tầng cho media hỗn hợp, như HDD chính với SSD DB/WAL.

## Quản lý Metadata
Metadata lưu trong RocksDB dưới dạng cặp key-value. Đối tượng đại diện bởi Onodes (tương tự inode), chứa logical extent (lextents) map đến blob. Blob tham chiếu physical extent (pextents) trên đĩa. Với snapshot, Bnodes cho phép chia sẻ dữ liệu qua copy-on-write. Tất cả sửa đổi là transaction trong RocksDB, với sharding (từ Pacific) chia dữ liệu thành column family cho cache và compaction tốt hơn.

- BlueStore tối ưu viết để tránh viết kép:
    + **Phân bổ Mới hoặc Append:** Dữ liệu viết trực tiếp đến không gian tự do dùng AIO; metadata cập nhật transaction RocksDB sau viết. Không cần WAL, vì mất điện giữ metadata không thay đổi.
    + **Overwrite:** Nếu > min_alloc_size (ví dụ: 4KiB), chia thành khối đầy (xử lý như mới) và mảnh (defer đến WAL trong RocksDB, flush không đồng bộ).
    + **Viết Nhỏ:** Hợp nhất vào WAL cho commit viết đơn, sau di chuyển đến vị trí cuối.
    + **Transaction:** Đảm bảo per-PG qua OpSequencer; ACID trong OSD.

> Điều này giải quyết vấn đề `journaling-of-journals` của FileStore, với hầu hết viết xảy ra một lần (dữ liệu đến đĩa + cập nhật metadata).

