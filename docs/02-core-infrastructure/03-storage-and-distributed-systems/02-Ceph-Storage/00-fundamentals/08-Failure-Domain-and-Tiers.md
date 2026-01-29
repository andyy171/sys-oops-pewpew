# Failure Domain và Storage Tiers
## Tổng quan
- Trong kiến trúc lưu trữ phân tán Ceph, việc đảm bảo dữ liệu không bị mất và luôn sẵn sàng truy cập là yêu cầu tối quan trọng. Hai khái niệm cốt lõi đạt được mục tiêu này là **Failure Domain** (Phân Vùng Lỗi) và **Storage Tiers** (Phân Cấp Lưu Trữ).
- **Failure Domain** giúp Ceph hiểu về cấu trúc vật lý của cơ sở hạ tầng để phân phối dữ liệu sao cho khi một thành phần bị lỗi (disk, server, rack, thậm chí cả datacenter), dữ liệu vẫn có thể được truy cập từ các bản sao hoặc các mảnh dữ liệu còn lại trên các phân vùng lỗi khác. **Storage Tiers** cho phép tận dụng các loại thiết bị lưu trữ khác nhau **(HDD, SSD, NVMe)** để tối ưu hóa hiệu năng và chi phí.


## Failure Domain (Phân Vùng Lỗi)
Failure Domain (FD) là bất kỳ thành phần nào trong cơ sở hạ tầng có thể gặp lỗi đồng thời và ảnh hưởng đến tất cả các thiết bị con bên trong nó. Hiểu đơn giản, Failure Domain là ranh giới mà khi một sự cố xảy ra (mất điện, hỏng phần cứng, lỗi mạng), tất cả các tài nguyên trong ranh giới đó sẽ không khả dụng cùng lúc.

**Các cấp độ Failure Domain phổ biến**
- Ceph hỗ trợ nhiều cấp độ phân vùng lỗi, được định nghĩa trong CRUSH map dưới dạng các "`bucket types`" hay bucket level:
    + `osd`: Cấp độ thấp nhất - một thiết bị lưu trữ đơn lẻ. Khi một OSD lỗi, chỉ dữ liệu trên thiết bị đó bị ảnh hưởng.
    + `host`: Một máy chủ vật lý. Khi máy chủ lỗi (hỏng mainboard, RAM, mất nguồn local), tất cả các OSD trên máy đó đều mất.
    + `chassis`: Khung máy chứa nhiều node (phổ biến trong blade servers). Một chassis lỗi có thể làm mất nhiều host.
    + `rack`: Tủ rack chứa nhiều máy chủ. Sự cố tại rack (mất nguồn từ PDU, lỗi switch mạng rack) ảnh hưởng tất cả các host trong rack đó.
    + `row`: Dãy rack trong datacenter.
    + `pdu`: Thanh nguồn (Power Distribution Unit). Nhiều rack có thể chia sẻ cùng PDU.
    + `room`: Phòng máy chủ. Sự cố như hỏng điều hòa, cháy có thể làm mất cả phòng.
    + `datacenter`: Trung tâm dữ liệu. Thiên tai, mất kết nối Internet, mất điện diện rộng ảnh hưởng toàn bộ datacenter.
    + `root`: Gốc của cây phân cấp, thường đại diện cho toàn bộ cluster.

**Tầm quan trọng của Failure Domain**
Không khai báo đúng Failure Domain là một trong những sai lầm phổ biến nhất khi triển khai Ceph. Nếu không cấu hình, Ceph có thể ngẫu nhiên đặt cả 3 bản sao (replicas) của một đối tượng lên 3 OSD nằm trên cùng một máy chủ, hoặc tệ hơn, 3 máy chủ trong cùng một rack. Khi đó:

- **Máy chủ lỗi:** Nếu 3 replicas trên cùng host, dữ liệu hoàn toàn mất khả năng truy cập cho đến khi máy phục hồi.
- **Rack mất điện:** Nếu 3 replicas phân bố trên 3 host nhưng cả 3 host đều trong cùng rack, khi rack mất nguồn, dữ liệu cũng không thể truy cập.

>**Nguyên tắc quan trọng:** Failure Domain phải được thiết lập ở cấp độ cao nhất mà cluster có thể chấp nhận mất mà vẫn duy trì dữ liệu khả dụng. Với cluster nhỏ (3-10 nodes), thường dùng `host` làm failure domain. Với cluster lớn hơn, nên dùng `rack` hoặc thậm chí `datacenter` cho stretch clusters.


#### Vai trò của Failure Domain trong CRUSH Map
CRUSH (Controlled Replication Under Scalable Hashing) là thuật toán độc đáo giúp Ceph xác định chính xác nơi lưu trữ và truy xuất dữ liệu mà không cần tra cứu bảng metadata tập trung. Đây là một trong những lý do chính khiến Ceph có khả năng mở rộng gần như vô hạn.

Khi một client muốn đọc/ghi một object, thay vì hỏi một server trung tâm "object X nằm ở đâu?", client tự tính toán vị trí bằng cách:
1. Hash tên object và pool ID
2. Ánh xạ hash value vào một Placement Group (PG)
3. Áp dụng CRUSH algorithm với CRUSH map để xác định tập OSDs chịu trách nhiệm cho PG đó

### CRUSH Map và Failure Domain
CRUSH Map chứa ba thành phần chính:

Devices: Danh sách các OSD (leaf nodes)
Buckets: Cấu trúc phân cấp nhóm các OSD theo topology vật lý
Rules: Các quy tắc chỉ định cách CRUSH chọn OSD cho từng pool

Failure Domain được nhúng vào Buckets hierarchy. Khi tạo CRUSH rule, chúng ta chỉ định failure domain type và CRUSH đảm bảo các replicas/shards được phân tán qua các bucket của type đó.

**Ví dụ minh họa:** Một cluster có cấu trúc:
```
root default
├── rack rack1
│   ├── host node1 (osd.0, osd.1)
│   └── host node2 (osd.2, osd.3)
└── rack rack2
    ├── host node3 (osd.4, osd.5)
    └── host node4 (osd.6, osd.7)
```

- Nếu CRUSH rule có failure domain = host, với 3 replicas, CRUSH sẽ chọn 3 OSD từ 3 host khác nhau (ví dụ: osd.0, osd.2, osd.4).
- Nếu CRUSH rule có failure domain = rack, với 3 replicas, CRUSH sẽ:

    + Chọn 1 OSD từ rack1 (giả sử osd.1 từ node1)
    + Chọn 1 OSD từ rack2 (giả sử osd.5 từ node3)
    + Chọn 1 OSD thứ 3... và gặp vấn đề vì chỉ có 2 racks!

→ Lưu ý quan trọng: Số lượng failure domains phải >= số replicas. Nếu cluster chỉ có 2 racks mà dùng failure domain = rack với size = 3, một số PG sẽ không đủ replicas (degraded) hoặc không thể tạo được (inconsistent).

[**==> Kiến thức cần nắm về cây CRUSH**](/08-storage-and-distributed-systems/02-Ceph-Storage/00-fundamentals/03-CRUSH.md#crush-hierarchy)

## Storage Tiers (Phân Cấp Lưu Trữ)
### Device Class
Trước đây (pre-Luminous), để tạo storage tiers, admin phải tạo nhiều CRUSH hierarchies song song (một tree cho HDDs, một tree cho SSDs) trong cùng một CRUSH map. Điều này phức tạp, dễ lỗi và khó bảo trì.

Từ Luminous (12.2.x) trở đi, Ceph giới thiệu Device Class - một cách elegant hơn để phân loại OSDs theo loại phần cứng.

- Device Class là một thuộc tính được gán cho mỗi OSD, chỉ định loại thiết bị vật lý mà OSD đó chạy trên. Ceph tự động phát hiện và gán device class khi OSD khởi động, dựa trên thông tin từ kernel Linux.

- Ba device classes mặc định:

    + `hdd`: Traditional spinning disks (HDD)
    + `ssd`: Solid State Drives (SATA/SAS SSD)
    + `nvme`: NVMe SSDs (PCIe SSD)

#### Auto-detection
Khi một OSD daemon khởi động lần đầu, nó kiểm tra thiết bị vật lý (qua `/sys/block/<device>/queue/rotational`, SMART data, etc.) và tự động set device class:
```bash
# Xem device class của các OSDs
ceph osd tree

# Output:
ID  CLASS  WEIGHT   TYPE NAME       STATUS  REWEIGHT  PRI-AFF
-1         36.0000  root default
-3         12.0000      host node1
 0    hdd   3.0000          osd.0     up    1.00000  1.00000
 1    hdd   3.0000          osd.1     up    1.00000  1.00000
 2    ssd   1.0000          osd.2     up    1.00000  1.00000
 3    nvme  0.5000          osd.3     up    1.00000  1.00000
```

#### Manual Override
Đôi khi auto-detection không chính xác (ví dụ: VM sử dụng virtual disks), ta có thể set thủ công:

```bash
# Set device class cho OSD
ceph osd crush set-device-class <class> <osd-id...>

# Ví dụ: Đặt osd.5 và osd.6 thành ssd
ceph osd crush set-device-class ssd osd.5 osd.6

# Nếu OSD đã có class, phải remove trước
ceph osd crush rm-device-class osd.5
ceph osd crush set-device-class ssd osd.5

# Tạo custom device class (ví dụ: nvme-ultra-fast)
ceph osd crush set-device-class nvme-ultra-fast osd.10
```

#### Shadow CRUSH Hierarchy
Khi device classes được sử dụng, Ceph tự động tạo "shadow hierarchy" cho mỗi class. Đây là các bản copy ảo của CRUSH tree, mỗi bản chỉ chứa OSDs của một class cụ thể.

- Ví dụ, nếu có root `default`, Ceph tạo:

+ `default~hdd`: Shadow tree chỉ chứa HDD OSDs
+ `default~ssd`: Shadow tree chỉ chứa SSD OSDs
+ `default~nvme`: Shadow tree chỉ chứa NVMe OSDs

> User không cần (và không nên) tạo/quản lý shadow trees này thủ công. Chúng được quản lý tự động bởi Ceph.


### Áp dụng Storage Tiers bằng Device Class
#### Tạo Pools cho các Tiers khác nhau

Giả sử ta muốn:

- Hot tier (high IOPS): Dùng NVMe cho RBD images của VMs quan trọng
- Warm tier (balanced): Dùng SSD cho CephFS metadata và RGW index pools
- Cold tier (high capacity): Dùng HDD cho CephFS data và RGW data pools

**Bước 1:** Tạo CRUSH rules cho từng tier
```bash
# Hot tier - NVMe, failure domain = host
ceph osd crush rule create-replicated hot_tier default host nvme

# Warm tier - SSD, failure domain = rack  
ceph osd crush rule create-replicated warm_tier default rack ssd

# Cold tier - HDD, failure domain = rack
ceph osd crush rule create-replicated cold_tier default rack hdd
```

**Bước 2:** Tạo pools và gán rules
```bash
# Hot tier pool
ceph osd pool create rbd_hot 128 128 replicated hot_tier
ceph osd pool set rbd_hot size 2  # NVMe đắt, chỉ cần 2 replicas
ceph osd pool application enable rbd_hot rbd

# Warm tier pool  
ceph osd pool create cephfs_metadata 64 64 replicated warm_tier
ceph osd pool set cephfs_metadata size 3
ceph osd pool application enable cephfs_metadata cephfs

# Cold tier pool
ceph osd pool create cephfs_data 512 512 replicated cold_tier  
ceph osd pool set cephfs_data size 3
ceph osd pool application enable cephfs_data cephfs
```

**Bước 3:** Cấu hình CephFS để sử dụng hai pools
```bash
ceph fs new mycephfs cephfs_metadata cephfs_data
```

**Kết quả:** CephFS metadata (inodes, dentries) được lưu trên SSDs (warm_tier) để đảm bảo latency thấp cho operations như `ls`, `stat`. File data được lưu trên HDDs (cold_tier) để tiết kiệm chi phí.


### Ví dụ thực tế với Erasure Coding
Thường dùng erasure coding cho cold storage để tối ưu dung lượng:

```bash
# Tạo erasure code profile: 8 data chunks + 3 parity chunks
# Yêu cầu ít nhất 11 racks (hoặc 11 hosts nếu dùng host failure domain)
ceph osd erasure-code-profile set ec_cold \
    k=8 m=3 \
    crush-failure-domain=rack \
    crush-device-class=hdd

# Tạo pool
ceph osd pool create ec_archive erasure ec_cold
ceph osd pool application enable ec_archive rgw

# Cấu hình RGW data pool
radosgw-admin zone placement modify \
    --rgw-zone=default \
    --placement-id=default-placement \
    --data-pool=ec_archive
```
=> **Lợi ích:** Với k=8, m=3, overhead chỉ là 37.5% (so với 200% của replication size=3), tiết kiệm được 62.5% dung lượng!

### Mixed Device Classes trong cùng một Pool
Một use case thú vị là kết hợp nhiều device classes trong cùng một CRUSH rule để tối ưu performance và cost.

#### Primary OSD trên SSD, Replicas trên HDD
Đối với workloads write-heavy, ta có thể đặt primary replica trên SSD (để ghi nhanh) và secondary replicas trên HDD:

```bash
# Manual edit CRUSH map (chưa có CLI command cho này)
ceph osd getcrushmap -o /tmp/crushmap.bin
crushtool -d /tmp/crushmap.bin -o /tmp/crushmap.txt

# Edit crushmap.txt, thêm rule:
# rule mixed_replicated {
#     id 10
#     type replicated
#     step take default class ssd
#     step chooseleaf firstn 1 type host
#     step emit
#     step take default class hdd  
#     step chooseleaf firstn -1 type host
#     step emit
# }

crushtool -c /tmp/crushmap.txt -o /tmp/crushmap_new.bin
ceph osd setcrushmap -i /tmp/crushmap_new.bin

# Apply to pool
ceph osd pool create mixed_pool 128 128
ceph osd pool set mixed_pool crush_rule mixed_replicated
ceph osd pool set mixed_pool size 3
```

**Lưu ý:** Cách này có trade-offs:

- **Ưu điểm:** Write latency thấp (vào SSD trước), cost tiết kiệm hơn all-SSD
- **Nhược điểm:**
    + Khi primary SSD OSD fail, một HDD OSD sẽ lên làm primary tạm thời → performance drop
    + Read performance không ổn định (có thể hit HDD replicas)
    + Tăng độ phức tạp quản lý


- **Best practice:** Thường chỉ dùng trong trường hợp rất đặc biệt.Thay vào đó, nên:
    + Dùng pure SSD pools cho hot data
    + Dùng pure HDD pools cho cold data
    + Dùng tiering/replication giữa pools (nếu cần)

###  BlueStore và vai trò trong Storage Tiers
Từ Luminous, BlueStore là storage backend mặc định, thay thế FileStore legacy. BlueStore viết trực tiếp lên raw block device, không qua filesystem trung gian (như XFS trong FileStore).

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

#### Tại sao BlueStore làm Cache Tiering trở nên "không cần thiết"?

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
 

### Cache Tiering (Legacy) - Tại sao không còn được khuyến nghị

Cache Tiering được giới thiệu từ Firefly (0.80), cho phép tạo một "cache pool" (thường là SSD) phía trước một "backing pool" (thường là HDD). 

Architecture:
```
Client → Cache Pool (SSD, fast) → Backing Pool (HDD, slow)
```
Operations:

- **Promote:** Copy object từ backing pool lên cache pool khi accessed
- **Flush:** Ghi dirty objects từ cache pool xuống backing pool
- **Evict:** Xóa clean objects khỏi cache pool để giải phóng không gian

Cấu hình Cache Tiering (chỉ để tham khảo, KHÔNG nên dùng)
```bash
# Tạo backing pool (HDD)
ceph osd pool create cold_pool 128 128

# Tạo cache pool (SSD)  
ceph osd pool create hot_pool 64 64

# Set cache pool cho backing pool
ceph osd tier add cold_pool hot_pool
ceph osd tier cache-mode hot_pool writeback  # hoặc readonly, readproxy

# Set cache pool là tier overlay
ceph osd tier set-overlay cold_pool hot_pool

# Cấu hình cache parameters (rất khó tune đúng!)
ceph osd pool set hot_pool hit_set_type bloom
ceph osd pool set hot_pool hit_set_count 12
ceph osd pool set hot_pool hit_set_period 14400
ceph osd pool set hot_pool target_max_bytes 1099511627776  # 1TB
ceph osd pool set hot_pool min_read_recency_for_promote 2
ceph osd pool set hot_pool min_write_recency_for_promote 2
ceph osd pool set hot_pool cache_target_dirty_ratio 0.4
ceph osd pool set hot_pool cache_target_full_ratio 0.8

```

**Các vấn đề thực tế với Cache Tiering**
1. **Flush storms:** Khi cache đầy, agent bắt đầu flush hàng loạt objects → backing pool quá tải
2. **Promote/evict thrashing:** Objects bị promote lên và evict xuống liên tục → waste I/O
3. **Hit ratio unpredictable:** Khó đạt được hit ratio cao với workloads không đều
4. **Agent overhead:** Cache tier agent chạy trên MON, tiêu tốn CPU/RAM
5. **Difficult troubleshooting:** Khi có vấn đề, rất khó debug (log phức tạp, state machine phức tạp)

#### Migration từ Cache Tiering sang Device Class
Nếu đang dùng cache tiering và muốn migrate:
```bash
# Bước 1: Set cache mode sang forward (stop promoting)
ceph osd tier cache-mode hot_pool forward

# Bước 2: Đợi cache pool rỗng (flush hết)
rados -p hot_pool ls
ceph osd tier cache-mode hot_pool none

# Bước 3: Remove cache tier
ceph osd tier remove-overlay cold_pool
ceph osd tier remove cold_pool hot_pool

# Bước 4: Migrate data sang pools mới dùng device class
# (Dùng tools như rbd export/import, rados cppool, hoặc application-level migration)

# Bước 5: Delete old pools
ceph osd pool delete hot_pool hot_pool --yes-i-really-really-mean-it
ceph osd pool delete cold_pool cold_pool --yes-i-really-really-mean-it

```
> **Thời gian downtime:** Có thể từ vài giờ đến vài ngày tùy data size. Cần lập kế hoạch cẩn thận.


## Best Practices và Khuyến nghị
###  Thiết kế Failure Domain

Quy tắc chọn Failure Domain

1. Đánh giá rủi ro thực tế:

    - Có bao nhiêu racks? Nguồn điện mỗi rack có độc lập không?
    - Switches mạng top-of-rack có SPOF (single point of failure) không?
    - Datacenter có multi-zone/multi-room không?


2. So sánh với replica count:

    - Size 3, min_size 2: Cần ít nhất 3 failure domains
    - EC k=4 m=2: Cần ít nhất 6 failure domains


3. Trade-off giữa availability và performance:

    - Failure domain càng lớn (rack, datacenter) → availability càng cao nhưng latency có thể tăng (cross-rack, cross-DC network)
    - Failure domain càng nhỏ (host) → latency thấp nhưng dễ bị outage
  
Ví dụ Decision Tree
```
Cluster size < 3 nodes?
├─ Yes → KHÔNG nên chạy production Ceph (không đủ HA)
└─ No
    │
    Cluster 3-10 nodes, same rack?
    ├─ Yes → failure_domain = host (chấp nhận risk rack failure)
    └─ No
        │
        Cluster 10+ nodes, multiple racks?
        ├─ Yes → failure_domain = rack (khuyến nghị)
        └─ No
            │
            Cluster multi-datacenter?
            └─ Yes → failure_domain = datacenter (stretch cluster)
```


#### Stretch Clusters (Multi-site)
Đặc biệt với stretch clusters (cụm trải qua nhiều DC), cần:

- **3 sites:** 2 sites chính + 1 arbitrator site (chỉ chứa MON, không chứa data)
- Network latency < 5ms giữa các sites (khuyến nghị < 2ms)
- Failure domain = datacenter
- `min_size` phải được set cẩn thận để tránh *split-brain*

### Device Class Best Practices
1. Luôn verify device class sau khi deploy OSDs
```bash
# Sau khi deploy, check ngay
ceph osd tree | grep -E 'hdd|ssd|nvme'

# Nếu sai, fix ngay
ceph osd crush rm-device-class osd.X
ceph osd crush set-device-class ssd osd.X
```
2. Consistent device class trong cùng host 
Tránh mix HDD và SSD trong cùng một failure domain (host) khi dùng host-level failure domain. Lý do: CRUSH sẽ ưu tiên chọn OSDs từ cùng một host nếu weights tương đương → không đạt được isolation mong muốn.

3. Custom device classes cho special hardware
Nếu có hardware đặc biệt (ví dụ: Intel Optane, NVMe-oF, high-endurance SSD), tạo custom class:
```bash
ceph osd crush set-device-class optane osd.20 osd.21
ceph osd crush rule create-replicated optane_pool default host optane
```

4. Document device class mapping
Tạo inventory rõ ràng:

```
Host         OSD IDs      Device Class    Hardware
---------------------------------------------------------
node1       0-11         hdd             12x HGST 8TB 7200rpm
node1       12-13        ssd             2x Samsung 883 1.92TB
node2       14-25        hdd             12x HGST 8TB 7200rpm
node2       26-27        nvme            2x Samsung 983 960GB
```
[CRUSH Map Management](/08-storage-and-distributed-systems/02-Ceph-Storage/02-operations/03-Cluster-Operations.md#crush-map-management)


###  Monitoring và Alerting

- Key metrics for failure domains

```bash
# OSDs distribution per failure domain
ceph osd tree | awk '/rack/ {print $4, $5}'

# PGs per OSD (should be balanced)
ceph osd df tree | sort -k7 -n

# Placement groups stuck (sign of CRUSH issues)
ceph pg dump pgs_brief | grep -v 'active+clean'

# CRUSH rule usage
ceph osd pool ls detail | grep crush_rule

```
- Alerting rules (Prometheus example)
```yaml
groups:
  - name: ceph_failure_domain
    rules:
      - alert: CephUnbalancedPGs
        expr: |
          stddev(ceph_osd_numpg) / avg(ceph_osd_numpg) > 0.3
        annotations:
          summary: "Ceph PGs distribution is unbalanced"
          
      - alert: CephOSDsInSameFailureDomain
        expr: |
          count(ceph_osd_metadata{failure_domain_name="rack1"}) == 3
          and on() ceph_pool_metadata{size="3"}
        annotations:
          summary: "All replicas might be in same failure domain"

```

## Troubleshooting Common Issues

### "Insufficient replicas" / "Inconsistent" PGs
**Dấu hiệu :**
```bash
ceph health detail
HEALTH_WARN Reduced data availability: X pgs inactive
```
**Nguyên nhân:** Không đủ failure domains để đáp ứng CRUSH rule.
**Ví dụ:** Pool có size=3, failure_domain=rack, nhưng cluster chỉ có 2 racks.

**Giải pháp:**
```
# Option 1: Giảm pool size (không khuyến nghị cho production)
ceph osd pool set <pool> size 2

# Option 2: Thay đổi failure domain trong CRUSH rule
ceph osd crush rule create-replicated new_rule default host  # Thay rack → host
ceph osd pool set <pool> crush_rule new_rule

# Option 3: Add more racks (đúng hướng)
```

### OSDs với device class sai
**Dấu hiệu :** Pool dùng rule ssd nhưng performance vẫn chậm như HDD.
```bash
ceph osd tree
# Thấy OSD mong muốn là ssd nhưng lại hiển thị hdd hoặc không có class
```
**Nguyên nhân:** Auto-detection fail, hoặc OSD created trước khi device class được introduced (pre-Luminous upgrade).


**Giải pháp:**
```bash
# Remove wrong class
ceph osd crush rm-device-class osd.X

# Set correct class
ceph osd crush set-device-class ssd osd.X

# Verify
ceph osd tree | grep osd.X
```

### CRUSH map corruption
**Dấu hiệu :** Cluster không thể start MON, hoặc PGs endless "`activating`".
```bash
ceph osd getcrushmap -o /tmp/current.bin
crushtool -d /tmp/current.bin -o /tmp/current.txt
cat /tmp/current.txt | grep -E 'rule|step'
```
**Nguyên nhân:** 
    + Rule được áp dụng cho bucket không tồn tại
    + Bucket ID bị confilicts
    + Thiếu `step emit`
    + Sai thuật toán ( straw thay vì straw2)
**Giải pháp:**
```bash
# Edit CRUSH map manually
vi /tmp/current.txt

# Test before applying
crushtool -c /tmp/current.txt -o /tmp/fixed.bin
crushtool -i /tmp/fixed.bin --test --show-mappings --num-rep 3

# Apply if test passed
ceph osd setcrushmap -i /tmp/fixed.bin
```

### Rebalancing không kết thúc 
**Dấu hiệu :** Sau khi thay đổi CRUSH, cluster rebalance hoài không xong, PG count misplaced cao.
```bash
ceph -w  # Observe recovery rate
ceph osd pool ls detail | grep pg_num  # PG autoscaler?
ceph config dump | grep -E 'backfill|recovery'  # Limits quá thấp?
```
**Giải pháp:**
```bash
# Increase recovery priority (careful - impact production)
ceph tell 'osd.*' injectargs '--osd-max-backfills 2'
ceph tell 'osd.*' injectargs '--osd-recovery-max-active 3'

# Or pause rebalancing temporarily
ceph osd set nobackfill
ceph osd set norecover
# ... maintenance window ...
ceph osd unset nobackfill
ceph osd unset norecover
``` 
