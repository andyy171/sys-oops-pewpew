---
title : OSD 

---
# Kiến trúc và cơ chế hoạt động
Ceph Object Storage Device (OSD) là thành phần cốt lõi trong kiến trúc Ceph storage cluster, đóng vai trò lưu trữ dữ liệu thực tế trên các ổ đĩa lưu trữ vật lý dưới dạng objects. OSD daemon chịu trách nhiệm phần lớn các hoạt động xử lý dữ liệu bên trong Ceph cluster, bao gồm lưu trữ, nhân bản, khôi phục và đảm bảo tính nhất quán của dữ liệu.
- OSD báo cáo trạng thái (up/down) cho cluster, xử lý replication và kiểm tra lỗi (scrubbing).
- Điểm đặc biệt trong kiến trúc Ceph là client không cần thông qua các lớp trung gian khi truy xuất dữ liệu. Sau khi nhận cluster map từ monitors, client tương tác trực tiếp với OSD để thực hiện các thao tác đọc/ghi, giúp tăng tốc độ xử lý đáng kể so với các hệ thống storage truyền thống.
## Cơ chế lưu trữ và truy xuất dữ liệu

Ceph OSD lưu trữ tất cả dữ liệu của client dưới dạng objects và trực tiếp đáp ứng các yêu cầu truy xuất. Quy trình hoạt động diễn ra như sau:
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/osd-1.png)

1.  Client request tới monitors để lấy cluster maps
2. Client tương tác trực tiếp với OSD để đọc/ghi dữ liệu
3. Dữ liệu được ghi trực tiếp vào OSD mà không qua các lớp xử lý trung gian

=> Cơ chế này tạo nên sự khác biệt cơ bản giữa Ceph và các giải pháp storage khác, giúp tối ưu hiệu năng và giảm độ trễ.

## Replication và High Availability
Dựa trên cấu hình replication size, Ceph đảm bảo tính sẵn sàng cao bằng cách:

- Nhân bản mỗi object tới nhiều cluster nodes khác nhau
- Mỗi object có một bản chính (primary copy) và các bản phụ (replica) nằm trên các OSD khác
- Mỗi OSD vừa lưu trữ bản chính của một số objects, vừa lưu bản phụ của các objects khác

> Cơ chế phân tán này không chỉ đảm bảo tính HA mà còn cho phép hệ thống chịu lỗi tốt, duy trì hoạt động ngay cả khi có sự cố xảy ra.

## Khôi phục tự động

Khi xảy ra lỗi disk, Ceph OSD daemon tự động kích hoạt quy trình recovery:

1. OSD daemon so sánh trạng thái giữa các OSD để xác định dữ liệu cần khôi phục
2. OSD chứa bản sao được tự động thăng cấp thành bản chính
3. Hệ thống tạo bản sao mới và phân phối tới OSD khác
4. Quá trình diễn ra trong suốt, không gián đoạn dịch vụ

# OSD lifecycle (up/down, in/out)



# Heartbeat mechanism


# Primary OSD selection


# Scrubbing (shallow & deep)


# Cấu hình OSD
## Tỷ lệ OSD trên Physical Hardware
Theo mặc định, Ceph cluster tạo một OSD daemon cho mỗi disk vật lý. Tuy nhiên, hệ thống hỗ trợ các cấu hình linh hoạt:

- **One OSD per disk (khuyến nghị):** Phổ biến nhất trong môi trường JBOD
- **One OSD per host:** Sử dụng trong các trường hợp đặc biệt
- **One OSD per RAID volume:** Áp dụng khi có RAID hardware

> Đối với hầu hết các triển khai production, việc sử dụng một OSD daemon trên mỗi disk vật lý là lựa chọn tối ưu về hiệu năng và quản lý.

### Lưu ý về RAID
Không nên sử dụng RAID với Ceph vì những lý do sau:

- **Nhân bản kép:** Chạy RAID và replication của Ceph đồng thời gây lãng phí tài nguyên, dữ liệu được nhân bản 2 lần
- **Hiệu năng giảm:** Đặc biệt với RAID 5/6 do tính chất random I/O của Ceph
- **Redundancy thừa:** Ceph tự quản lý bảo vệ dữ liệu hiệu quả hơn RAID truyền thống

=> Nếu bắt buộc phải sử dụng RAID, chỉ nên dùng RAID 0 để tận dụng throughput mà không tạo redundancy thừa.


# Filesystem cho Ceph OSD
## Vai trò của Linux Filesystem
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/osd-2.png)

Ceph OSD hoạt động dựa trên ba tầng:

1. Ceph OSD service (tầng trên cùng)
2. Linux filesystem (tầng giữa)
3. Physical disk với partition (tầng dưới)

Linux filesystem đóng vai trò quan trọng thông qua việc hỗ trợ Extended Attributes (XATTRs), cung cấp:

- Thông tin về trạng thái nội bộ của object
- Metadata của objects
- Snapshot information
- Access Control Lists (ACL)

XATTRs lưu trữ thông tin mở rộng dạng cặp xattr_name và xattr_value, cho phép OSD daemon quản lý dữ liệu hiệu quả.


Lựa chọn phổ biến nhất và ổn định nhất cho OSD trong production thường là XFS 

# Ceph OSD Journal
Journal là một thành phần quan trọng trong kiến trúc OSD, hoạt động như buffer để tối ưu hiệu năng ghi. Trước khi dữ liệu được ghi vào backing store chính, Ceph ghi dữ liệu vào journal trước.

- Đặc điểm của Journal:

    + Là partition nhỏ, buffer-sized, được cách biệt
    + Có thể nằm trên spinning disk cùng với OSD
    + Có thể nằm trên SSD disk hoặc partition riêng (khuyến nghị)
    + Có thể là một file trên filesystem

> **Kích thước khuyến nghị:** 10GB là size cơ bản, có thể lớn hơn tùy theo workload.

## Cơ chế hoạt động
Journal giúp tăng tốc độ và tính bảo đảm thông qua quy trình:

![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/osd-3.png)

1. Ghi vào Journal trước: Tất cả write operations được ghi vào journal dưới dạng sequential pattern
2. Flush sang Backing Store: Sau đó dữ liệu được đẩy từ journal sang filesystem chính
3. Random Write → Sequential Write: Journal chuyển đổi random writes thành sequential writes, tối ưu cho cả HDD và SSD

=> Cơ chế này cho phép filesystem có đủ thời gian để tổ chức và gộp các write operations xuống disk một cách hiệu quả.

## Tối ưu với SSD Journal
Sử dụng SSD cho journal mang lại lợi ích đáng kể:
- Ưu điểm:

    + Client write operations được xử lý cực nhanh trên SSD
    + Dữ liệu sau đó được flush từ SSD xuống spinning disk
    + OSD có thể xử lý khối lượng công việc lớn hơn nhiều

- Khuyến nghị cấu hình:

    + Tối đa 4-5 OSDs trên mỗi SSD journal
    + Vượt quá tỷ lệ này sẽ tạo bottleneck
    + Journal chậm hơn backing store sẽ hạn chế hiệu năng toàn bộ cluster

> **Lưu ý quan trọng:** Nếu journal disk chậm hơn backing store, nó sẽ trở thành điểm nghẽn cổ chai cho toàn bộ cluster.

## Bảo vệ dữ liệu với Journal
Trường hợp lỗi Journal
- **Với Btrfs:**

    + Giảm thiểu mất mát dữ liệu nhờ copy-on-write
    + Khi content block thay đổi, ghi diễn ra ở vị trí mới
    + Dữ liệu cũ vẫn tồn tại nếu journal gặp lỗi

- **Với XFS/ext4:**

    + Rủi ro mất dữ liệu cao hơn khi journal fail
    + Cần backup và monitoring chặt chẽ

## Best Practices
- Vị trí Journal:

    + Ưu tiên SSD cho journal trong production
    + Tách biệt journal khỏi OSD data disk
    + Sử dụng enterprise-grade SSD với endurance cao


- Sizing:

    + Bắt đầu với 10GB
    + Tăng lên nếu workload có burst writes lớn
    + Monitor journal utilization thường xuyên


- Redundancy:

    + Không dùng single SSD cho nhiều OSD critical
    + Cân nhắc RAID 1 cho journal SSD trong môi trường quan trọng
    + Backup journal configuration

# Crimson OSD 
- Crimson OSD là phiên bản mới, cải tiến của Ceph OSD (một phần mềm quản lý lưu trữ dữ liệu trong hệ thống Ceph). Nó được thiết kế đặc biệt để hoạt động tốt hơn trên các ổ đĩa tốc độ cao như NVMe (một loại ổ SSD siêu nhanh). Dự án này nhằm viết lại OSD để nó chạy hiệu quả hơn, có thể mở rộng lớn hơn, mà vẫn tương thích với các phần mềm cũ của Ceph.
- Ceph được tạo ra hơn 10 năm trước, lúc đó chủ yếu dựa vào sức mạnh của một lõi CPU duy nhất. Điều này làm nó không tận dụng hết khả năng của các thiết bị lưu trữ hiện đại. Ví dụ, OSD cũ sử dụng nhiều luồng (threads) để xử lý dữ liệu, nhưng điều này gây chậm trễ vì các luồng phải "nói chuyện" với nhau giữa các lõi CPU.

- Với CPU tốc độ 3 GHz, mỗi lần đọc/ghi dữ liệu (I/O) tốn khoảng:
    + 20 triệu chu kỳ cho ổ cứng HDD cũ.
    + 300 nghìn chu kỳ cho SSD cũ.
    + Chỉ 6 nghìn chu kỳ cho NVMe mới – nghĩa là rất nhanh, nhưng OSD cũ không theo kịp.

- Các đặc điểm chính bao gồm:
    + **Kernel Bypass:** Cho phép giao tiếp trực tiếp với thiết bị mạng hoặc lưu trữ mà không qua hệ điều hành, giúp nhanh hơn (nhờ chế độ polling – liên tục kiểm tra thay vì chờ đợi).
    + **Kiến trúc Shared-Nothing:** Mỗi phần chạy độc lập, giảm tranh chấp (lock contention) giữa các lõi CPU.
    + **Hiệu quả tính toán:** Cân bằng tải công việc trên nhiều lõi CPU.

> Crimson OSD tương thích hoàn toàn với OSD cũ, nên bạn có thể nâng cấp mà không làm gián đoạn hệ thống. Nó hỗ trợ giao thức librados (một cách giao tiếp dữ liệu) và làm việc được với các client cũ.

## Giới hạn hiện tại
Crimson vẫn đang được phát triển mạnh mẽ, nên chưa đầy đủ tính năng như phiên bản cũ. Hiện tại, nó chưa hỗ trợ chạy trên nhiều lõi CPU thực sự (đa nhân), nhưng bạn có thể "giả lập" bằng cách chạy nhiều bản Crimson riêng lẻ trên cùng một thiết bị.

## Testing và CI/CD
- Có bộ kiểm tra tên `crimson-rados` đang được xây dựng, dùng để kiểm tra các thay đổi mới (PR) và tránh lỗi cũ quay lại.
- Ngoài ra, có các bài kiểm tra hiệu năng (performance test) chạy bằng công cụ CBT, khoảng 2 lần mỗi tuần.

=> Hệ thống CI/CD của Ceph tự động xây dựng các container (gói phần mềm) thay thế OSD cũ bằng Crimson OSD. Phiên bản chính (nhánh main) được build hàng ngày, và bạn có thể tải images từ kho lưu trữ Quay.

## Cấu hình và triển khai
- Crimson không bật mặc định. Để bật, khi build Ceph, bạn dùng lệnh: `WITH_CRIMSON=true ./install-deps.sh` và `./do_cmake.sh -DWITH_CRIMSON=ON`.
- Các luồng xử lý I/O thường được gắn cố định vào một lõi CPU cụ thể để tối ưu. Có cơ chế "Alien threads" trong Seastar (một framework Crimson dùng) để hỗ trợ các tác vụ cũ (blocking tasks) mà không làm chậm hệ thống.
- Trước khi triển khai OSD, bạn cần cấu hình Ceph:
```bash
ceph config set global 'enable_experimental_unrecoverable_data_corrupting_features' crimson
```
Sau đó, bật flag `allow_crimson` và thiết lập các pool (nhóm lưu trữ) mặc định dùng Crimson.

### Hiệu năng
- Lý tưởng nhất, Crimson loại bỏ hoàn toàn các khóa (lock) và chuyển ngữ cảnh (context-switch) không cần thiết. Mỗi nhiệm vụ chạy liên tục trên CPU đến khi xong hoặc nhường quyền một cách chủ động. Nếu không cần giao tiếp giữa các phần khác nhau, hiệu năng sẽ tăng tuyến tính theo số lõi CPU – nghĩa là thêm lõi là nhanh hơn, cho đến khi thiết bị lưu trữ đạt giới hạn.
- Hiệu năng của Crimson phụ thuộc trực tiếp vào CPU, vì nó có thể dùng hết sức mạnh của từng lõi.

## Kế hoạch phát triển
Crimson được thiết kế để thay thế trực tiếp cho ceph-osd cũ (drop-in replacement). Tuy nhiên, vì cách lập trình hoàn toàn khác biệt, nó thực chất là một phiên bản viết lại từ đầu của OSD.


# Bluestore 
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

- RocksDB - Lưu metadata của object giúp mapping object đến các offset trên disk
   + là kho `key-value` hiệu suất cao nhúng trong BlueStore để quản lý metadata, bao gồm metadata đối tượng, OMAP Ceph, WAL và trạng thái allocator. 
   + Hỗ trợ transaction cho hoạt động ACID trong OSD. 
   + Dữ liệu RocksDB (SST và log) lưu qua BlueFS, cho phép đặt trên thiết bị nhanh hơn.
- BlueFS
    + BlueFS là hệ thống tệp không gian người dùng nhẹ, hỗ trợ RocksDB mà không overhead POSIX. 
    + Xử lý nhu cầu tệp của RocksDB (như WAL, DB, slow DB) với cấu trúc thư mục phẳng, viết append-only và metadata in-memory tải qua replay log khi mount. 
    + Hỗ trợ thu gom rác cho hiệu quả không gian và có thể trải nhiều thiết bị (ví dụ: NVM cho WAL, SSD cho SST nóng, HDD cho dữ liệu lạnh).
- Block device chính - Lưu object data thực tế : 
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
    + WAL - Write Ahead Log (block.wal): Log viết trước cho overwrite nhỏ; đồng vị nếu không riêng.
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

**Kiến trúc BlueStore**

```
            ┌─────────────────────────────────────────┐
            │         Ceph OSD Daemon                 │
            ├─────────────────────────────────────────┤
            │         BlueStore Engine                │
            │  ┌──────────────┬───────────────────┐   │
            │  │   Object     │    Metadata       │   │
            │  │   Data       │    (RocksDB)      │   │
            │  └──────────────┴───────────────────┘   │
            ├──────────┬──────────────────┬───────────┤
            │  block   │    block.db      │ block.wal │
            │  (data)  │   (metadata)     │   (WAL)   │
            └──────────┴──────────────────┴───────────┘
                │              │                │
                ▼              ▼                ▼
                HDD          SSD/NVMe           NVMe

```

**BlueStore chia làm ba phần:**
- **block (data):** Chứa object data, thường trên HDD cho capacity
- **block.db:** Chứa RocksDB database (metadata: object names, checksums, allocation map). Rất IOPS-intensive, nên đặt trên SSD/NVMe
- **block.wal:** Write-Ahead Log, chứa journal của transactions. Write-intensive, tốt nhất là NVMe

#### BlueStore Tiering Strategy
Best practice cho production:

Scenario 1: All-HDD (budget constraint)
```bash
# Block, block.db, block.wal cùng trên HDD
ceph-volume lvm create --data /dev/sdb
```
- **Performance:** Thấp nhất nhưng cost thấp
- **Use case:** Archive, backup, cold storage

Scenario 2: HDD + SSD hybrid (khuyến nghị cho most workloads)
```bash
# Data trên HDD, metadata+WAL trên SSD partition
ceph-volume lvm create \
    --data /dev/sdb \
    --block.db /dev/nvme0n1p1 \
    --block.wal /dev/nvme0n1p2
```
- **Performance:** Tăng 30-50% so với all-HDD
- **Cost:** Chấp nhận được (chỉ cần 1-5% capacity của data device cho db/wal)
- **Sizing guideline:**

    + `block.db`: 1-4% của block size. Ví dụ: 12TB HDD → 120-480GB db
    + `block.wal`: 512MB - 2GB là đủ (default 512MB)`

Scenario 3:  All-NVMe (high performance)

```bash
ceph-volume lvm create --data /dev/nvme0n1
```
- **Performance:** Tốt nhất, latency sub-millisecond
- **Cost:** Cao nhất
- **Use case:** Database, VMs, high-IOPS workloads

### Tại sao BlueStore làm Cache Tiering trở nên "không cần thiết"?

- Trước BlueStore (khi dùng FileStore), toàn bộ metadata và data đều trên HDD → chậm. Cache Tiering ra đời để:
    + Tạo một pool SSD làm "cache" trước pool HDD
    + Hot data được promote lên cache pool
    + Cold data được flush xuống backing pool (HDD)
- Nhưng Cache Tiering có nhiều vấn đề:
    + Complexity: Khó tune parameters (hit_set, target_max_bytes, flush/evict ratios)
    + Performance unpredictability:
        * Cache miss → latency spike lớn
        * Flush/promote/evict storms → cluster load tăng đột biến
    + Consistency issues: Edge cases khi promote/flush/evict đồng thời

=> Với BlueStore + hybrid setup (HDD+SSD), metadata đã ở trên SSD rồi, performance đã tốt mà không cần độ phức tạp của cache tiering. 


>- Khuyến nghị chính thức từ Ceph community và Red Hat:
>    + Không dùng Cache Tiering cho deployments mới
>    + Thay vào đó: Dùng device class + BlueStore hybrid
>    + Nếu cần hot/cold separation: Dùng separate pools (hot pool = all-SSD, cold pool = HDD+SSD hybrid) và di chuyển data giữa pools bằng application logic 
 

## BlueStore cache tuning
