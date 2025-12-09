# OSD 
Ceph Object Storage Device (OSD) là thành phần cốt lõi trong kiến trúc Ceph storage cluster, đóng vai trò lưu trữ dữ liệu thực tế trên các ổ đĩa lưu trữ vật lý dưới dạng objects. OSD daemon chịu trách nhiệm phần lớn các hoạt động xử lý dữ liệu bên trong Ceph cluster, bao gồm lưu trữ, nhân bản, khôi phục và đảm bảo tính nhất quán của dữ liệu.
- OSD báo cáo trạng thái (up/down) cho cluster, xử lý replication và kiểm tra lỗi (scrubbing).
- Điểm đặc biệt trong kiến trúc Ceph là client không cần thông qua các lớp trung gian khi truy xuất dữ liệu. Sau khi nhận cluster map từ monitors, client tương tác trực tiếp với OSD để thực hiện các thao tác đọc/ghi, giúp tăng tốc độ xử lý đáng kể so với các hệ thống storage truyền thống.

## Kiến trúc và cơ chế hoạt động
### Cơ chế lưu trữ và truy xuất dữ liệu

Ceph OSD lưu trữ tất cả dữ liệu của client dưới dạng objects và trực tiếp đáp ứng các yêu cầu truy xuất. Quy trình hoạt động diễn ra như sau:
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/osd-1.png)

1.  Client request tới monitors để lấy cluster maps
2. Client tương tác trực tiếp với OSD để đọc/ghi dữ liệu
3. Dữ liệu được ghi trực tiếp vào OSD mà không qua các lớp xử lý trung gian

=> Cơ chế này tạo nên sự khác biệt cơ bản giữa Ceph và các giải pháp storage khác, giúp tối ưu hiệu năng và giảm độ trễ.

### Replication và High Availability
Dựa trên cấu hình replication size, Ceph đảm bảo tính sẵn sàng cao bằng cách:

- Nhân bản mỗi object tới nhiều cluster nodes khác nhau
- Mỗi object có một bản chính (primary copy) và các bản phụ (replica) nằm trên các OSD khác
- Mỗi OSD vừa lưu trữ bản chính của một số objects, vừa lưu bản phụ của các objects khác

> Cơ chế phân tán này không chỉ đảm bảo tính HA mà còn cho phép hệ thống chịu lỗi tốt, duy trì hoạt động ngay cả khi có sự cố xảy ra.

### Khôi phục tự động

Khi xảy ra lỗi disk, Ceph OSD daemon tự động kích hoạt quy trình recovery:

1. OSD daemon so sánh trạng thái giữa các OSD để xác định dữ liệu cần khôi phục
2. OSD chứa bản sao được tự động thăng cấp thành bản chính
3. Hệ thống tạo bản sao mới và phân phối tới OSD khác
4. Quá trình diễn ra trong suốt, không gián đoạn dịch vụ

## OSD lifecycle (up/down, in/out)



## Heartbeat mechanism


## Primary OSD selection


## Scrubbing (shallow & deep)




## Cấu hình OSD
### Tỷ lệ OSD trên Physical Hardware
Theo mặc định, Ceph cluster tạo một OSD daemon cho mỗi disk vật lý. Tuy nhiên, hệ thống hỗ trợ các cấu hình linh hoạt:

- **One OSD per disk (khuyến nghị):** Phổ biến nhất trong môi trường JBOD
- **One OSD per host:** Sử dụng trong các trường hợp đặc biệt
- **One OSD per RAID volume:** Áp dụng khi có RAID hardware

> Đối với hầu hết các triển khai production, việc sử dụng một OSD daemon trên mỗi disk vật lý là lựa chọn tối ưu về hiệu năng và quản lý.

#### Lưu ý về RAID
Không nên sử dụng RAID với Ceph vì những lý do sau:

- **Nhân bản kép:** Chạy RAID và replication của Ceph đồng thời gây lãng phí tài nguyên, dữ liệu được nhân bản 2 lần
- **Hiệu năng giảm:** Đặc biệt với RAID 5/6 do tính chất random I/O của Ceph
- **Redundancy thừa:** Ceph tự quản lý bảo vệ dữ liệu hiệu quả hơn RAID truyền thống

=> Nếu bắt buộc phải sử dụng RAID, chỉ nên dùng RAID 0 để tận dụng throughput mà không tạo redundancy thừa.


## Filesystem cho Ceph OSD
### Vai trò của Linux Filesystem
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

### So sánh các Filesystem
#### Btrfs (B-tree File System)
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

#### XFS
- Ưu điểm:

    + Filesystem ổn định, tin cậy và được kiểm chứng
    + Khuyến nghị cho Ceph production cluster
    + Được sử dụng rộng rãi nhất trong các triển khai Ceph
    + Hỗ trợ XATTRs tốt hơn ext4

- Nhược điểm:

    + Kém Btrfs về một số tính năng tiên tiến
    + Vấn đề hiệu năng khi mở rộng metadata
    + Là journaling filesystem, tạo overhead khi ghi dữ liệu (ghi vào journal trước, sau đó mới ghi vào filesystem)

> Lựa chọn phổ biến nhất và ổn định nhất cho OSD trong production.
#### ext4 (Fourth Extended Filesystem)
- Ưu điểm:

    + Hỗ trợ journaling filesystem
    + Tương thích tốt với Ceph OSD

- Nhược điểm:

    + Không thân thiện bằng XFS cho Ceph
    + Hạn chế về XATTRs: số lượng bytes lưu trữ XATTRs bị giới hạn
    + Hiệu năng kém hơn Btrfs và XFS
    + Không phù hợp làm filesystem chính cho OSD

### Extended Attributes (XATTRs)
XATTRs là yếu tố then chốt cho hoạt động của Ceph OSD:

- Lưu trữ metadata và trạng thái của objects
- Cung cấp thông tin nhanh chóng mà không cần đọc toàn bộ object
- Btrfs và XFS hỗ trợ dung lượng XATTRs lớn hơn `ext4` đáng kể
- `ext4` bị hạn chế về số byte có thể lưu trong XATTRs, không đủ cho nhiều trường hợp sử dụng

## Ceph OSD Journal
Journal là một thành phần quan trọng trong kiến trúc OSD, hoạt động như buffer để tối ưu hiệu năng ghi. Trước khi dữ liệu được ghi vào backing store chính, Ceph ghi dữ liệu vào journal trước.

- Đặc điểm của Journal:

    + Là partition nhỏ, buffer-sized, được cách biệt
    + Có thể nằm trên spinning disk cùng với OSD
    + Có thể nằm trên SSD disk hoặc partition riêng (khuyến nghị)
    + Có thể là một file trên filesystem

> **Kích thước khuyến nghị:** 10GB là size cơ bản, có thể lớn hơn tùy theo workload.

### Cơ chế hoạt động
Journal giúp tăng tốc độ và tính bảo đảm thông qua quy trình:

![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/osd-3.png)

1. Ghi vào Journal trước: Tất cả write operations được ghi vào journal dưới dạng sequential pattern
2. Flush sang Backing Store: Sau đó dữ liệu được đẩy từ journal sang filesystem chính
3. Random Write → Sequential Write: Journal chuyển đổi random writes thành sequential writes, tối ưu cho cả HDD và SSD

=> Cơ chế này cho phép filesystem có đủ thời gian để tổ chức và gộp các write operations xuống disk một cách hiệu quả.

### Tối ưu với SSD Journal
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

### Bảo vệ dữ liệu với Journal
Trường hợp lỗi Journal
- **Với Btrfs:**

    + Giảm thiểu mất mát dữ liệu nhờ copy-on-write
    + Khi content block thay đổi, ghi diễn ra ở vị trí mới
    + Dữ liệu cũ vẫn tồn tại nếu journal gặp lỗi

- **Với XFS/ext4:**

    + Rủi ro mất dữ liệu cao hơn khi journal fail
    + Cần backup và monitoring chặt chẽ

### Best Practices
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



### PG (Placement Group)
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/pg.png)

- Khi Ceph cluster nhận yêu cầu từ data storage, nó sẽ chia thành nhiều phẩn đc gọi là placement groups (PG). Tuy nhiên, CRUSH data đầu tiên được chia nhỏ thành tập các Obj, dựa trên hoạt động hash trên tên obj , mức nhân bản, tổng các placement groups trong hệ thông, placement groups IDs được sinh ra tương ứng.

- Placement groups là tập logical (logical collection) các obj được nhân bản trên các OSDs để nâng cao tính bảo đảm trong storage system. Dựa trên mức nhân bản của Ceph pool, mỗi placement group sẽ được nhân bản, phân tán trên nhiều hơn 1 OSD tại Ceph cluster. Ta có thể cân nhắc placement group như logical container giữ nhiều obj = logical container is mapped to multiple OSDs. Placement groups (vị trí nhóm) được thiết kế đáp ứng khả năng mở rộng, hiệu suất cao trong Ceph storage system.

![](/08-storage-and-distributed-systems/02-Ceph-Storage//images/theory/ceph-in-4.png")

- Nếu không có placement groups, nó sẽ khó cho việc quản trị, theo dõi các obj được nhân bản (hảng triệu obj được nhân bản) tới hàng trăm các OSD khác nhau. Thay vì quản lý tất cả obj riêng biệt, hệ thông cần quản lý placement group với numerous objects (số lượng nhiều các obj). Nó khiến ceph dễ quản lý và giảm bớt sự phức tạp. Mỗi placement group yêu cầu tài nguyên hệ thống, CPU và Memo vì chúng cần quản lý nhiều obj.

- Số lượng placement group trong cluster cần được tính toán tỉ mỉ. Thông thường, tăng số lượng placement groups trong cluster sẽ giảm bớt gánh nặng trên mỗi OSD, nhưng cần xem xét theo quy chuẩn. 50-100 placement groups trên mỗi OSD được khuyến cáo. Nó tránh tiêu tốn quá nhiều tài nguyên trên mỗi OSD node. Khi data tăng lên, ta cần mở rộng cluster cùng với nhiều chỉnh số lượng placement groups. Khi thiệt bị được thêm, xóa khởi cluster, các placement group sẽ vẫn tồn tại – CRUSH sẽ quản lý việc tài cấp pháp placement groups trên toàn cluster.

> PGP is the total number of placement groups for placement purposes. This should be equal to the total number of placement groups.

<details>

<summary> Tính toán số PG cần thiết - Calculating PG numbers</summary>

Quyết đinh PG là bước cần thiết khi xây dựng nên tảng Ceph storage cluster cho doanh nghiệp. Placement group có thể tăng hoặc làm ảnh hưởng tới hiệu năng storge.
Công thức tính tổng placement group cho Ceph cluster:
```
Total PGs = (Total_number_of_OSD * 100) / max_replication_count

Kết quả có thể làm tròn gần nhất theo 2 ^ đơn vị.
```
__Ví dụ thực tế__
```
Tổng OSDs = 160, mức nhận bản = 3, tổng pool = 3 => Tông PGs = 1777.7 => kết quả tính theo 2^.. = 2048 PGs trên mỗi pool.
```

> Việc cân bẳng tông PGs/pool với số PGs/OSD rất quan trọng, nó ảnh hưởng tới hđ OSD, giảm tiển trình khôi phục.

</details>

## Crimson OSD 
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

### Giới hạn hiện tại
Crimson vẫn đang được phát triển mạnh mẽ, nên chưa đầy đủ tính năng như phiên bản cũ. Hiện tại, nó chưa hỗ trợ chạy trên nhiều lõi CPU thực sự (đa nhân), nhưng bạn có thể "giả lập" bằng cách chạy nhiều bản Crimson riêng lẻ trên cùng một thiết bị.

### Testing và CI/CD
- Có bộ kiểm tra tên `crimson-rados` đang được xây dựng, dùng để kiểm tra các thay đổi mới (PR) và tránh lỗi cũ quay lại.
- Ngoài ra, có các bài kiểm tra hiệu năng (performance test) chạy bằng công cụ CBT, khoảng 2 lần mỗi tuần.

=> Hệ thống CI/CD của Ceph tự động xây dựng các container (gói phần mềm) thay thế OSD cũ bằng Crimson OSD. Phiên bản chính (nhánh main) được build hàng ngày, và bạn có thể tải images từ kho lưu trữ Quay.

### Cấu hình và triển khai
- Crimson không bật mặc định. Để bật, khi build Ceph, bạn dùng lệnh: `WITH_CRIMSON=true ./install-deps.sh` và `./do_cmake.sh -DWITH_CRIMSON=ON`.
- Các luồng xử lý I/O thường được gắn cố định vào một lõi CPU cụ thể để tối ưu. Có cơ chế "Alien threads" trong Seastar (một framework Crimson dùng) để hỗ trợ các tác vụ cũ (blocking tasks) mà không làm chậm hệ thống.
- Trước khi triển khai OSD, bạn cần cấu hình Ceph:
```bash
ceph config set global 'enable_experimental_unrecoverable_data_corrupting_features' crimson
```
Sau đó, bật flag `allow_crimson` và thiết lập các pool (nhóm lưu trữ) mặc định dùng Crimson.

#### Hiệu năng
- Lý tưởng nhất, Crimson loại bỏ hoàn toàn các khóa (lock) và chuyển ngữ cảnh (context-switch) không cần thiết. Mỗi nhiệm vụ chạy liên tục trên CPU đến khi xong hoặc nhường quyền một cách chủ động. Nếu không cần giao tiếp giữa các phần khác nhau, hiệu năng sẽ tăng tuyến tính theo số lõi CPU – nghĩa là thêm lõi là nhanh hơn, cho đến khi thiết bị lưu trữ đạt giới hạn.
- Hiệu năng của Crimson phụ thuộc trực tiếp vào CPU, vì nó có thể dùng hết sức mạnh của từng lõi.

### Kế hoạch phát triển
Crimson được thiết kế để thay thế trực tiếp cho ceph-osd cũ (drop-in replacement). Tuy nhiên, vì cách lập trình hoàn toàn khác biệt, nó thực chất là một phiên bản viết lại từ đầu của OSD.
