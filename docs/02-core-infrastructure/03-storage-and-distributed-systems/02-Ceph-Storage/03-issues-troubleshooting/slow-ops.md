# Slow Ops 
- Về bản chất, "Slow ops" nghĩa là các OSD (Object Storage Daemons) không thể hoàn thành một yêu cầu (read/write) trong khoảng thời gian quy định (mặc định là 30 giây).

## Các nguyên nhân chính 
### 1. Vấn Đề Phần Cứng Lưu Trữ
**Hiện tượng:** Một hoặc vài OSD cụ thể thường xuyên báo slow ops.
- Disk latency cao: Các ổ cứng không đạt yêu cầu hiệu năng, đặc biệt là các SSD/NVMe tiêu dùng hoặc HDD spinning disk

- Disk utilization 100%: Khi chạy iostat -xNmy 1, nếu utilization gần 100%, OSD đã đạt giới hạn hiệu năng​

- Apply/Commit latency cao: Đo bằng ceph osd perf, nếu commit latency >50ms hoặc apply latency >100ms cho thấy disk chậm​

- Ổ cứng bị quá tải (Saturation): IOPS vượt quá khả năng vật lý của đĩa (thường gặp khi dùng HDD cho OS/Journal mà không có SSD làm Cache/WAL).

- Ổ cứng (HDD/SSD) bị bad sector hoặc controller bị lỗi, dẫn đến thời gian phản hồi (service time) tăng vọt.
### 2. Vấn đề với Mạng
**Hiện tượng:** Slow ops xuất hiện trên nhiều OSD cùng thuộc một host hoặc một Rack.
- Độ trễ cao giữa các node trong cluster (ceph public/cluster network) hoặc mất gói tin (packet loss) giữa các OSD
- Bandwidth không đủ cho replication traffic
- Cấu hình MTU không nhất quán 
- Kết nối heartbeat bị delay → Slow OSD ping time

### 3. Quá Tải Tài Nguyên Hệ Thống​
Hiện tượng: Cả server chậm chạp, SSH vào cũng lag.
- CPU maxing out:Ít gặp hơn, nhưng nếu CPU quá yếu hoặc bị tranh chấp bởi các process khác (ví dụ chạy Compute chung với Storage - Hyperconverged), OSD thread sẽ không được xử lý kịp. OSD processes không đủ CPU cores để xử lý operations 
- RAM không đủ: Đặc biệt là memory cho BlueStore metadata và RocksDB cache . Ceph OSD ăn RAM rất dữ (đặc biệt khi Recovery). Nếu không đủ RAM, hệ thống dùng đến SWAP. Swap là kẻ thù số 1 của Ceph latency. Chỉ cần đụng vào Swap, slow ops sẽ bắn ra ngay lập tức.
- High I/O wait: Thấy qua iostat, vmstat, hoặc top command ( Số lượng thread/process đạt giới hạn)

- Cluster hoặc pool ở trạng thái NEARFULL/FULL
- Khi near full, các write operations bị sync (thay vì async), làm chậm cluster

### 4. RocksDB Compaction Quá Lâu​
- Leveldb/RocksDB compaction chạy quá lâu, lock OSD threads
- Xảy ra khi có nhiều DELETE operations, gây ra stale data trong OMAP (object map)
- Compaction là single-threaded operation mặc định

### 5. Vấn đề trong việc cấu hình Ceph 
- PGs per OSD không cần bằng : Quá nhiều gây overhead (Tăng memory usage, PG log length, và PG stat updates ) , quá ít lại gây contention 
- Cấu hình Backfilling/Recovery settings quá aggressive: Các tham số như osd_max_backfills, osd_recovery_max_active được cấu hình quá cao
- OSD op queue misconfiguration: Sử dụng sai priority queue settings
- RBD cache bị tắt hoặc cấu hình kém (đặc biệt với OpenStack).
- Pool size/replication factor không phù hợp (vd: size=2 nhưng chỉ có 2 OSD, dẫn đến recovery chậm).
### 6. Tác vụ ngầm trong Ceph​
**Hiện tượng:** Slow ops xảy ra vào các khung giờ cụ thể (thường là đêm hoặc cuối tuần) hoặc ngay sau khi một OSD bị down/up.
- Scrubbing: Deep scrub hoặc regular scrub trên PG lớn ( đồng thời trên nhiều OSD) . Ceph định kỳ đọc dữ liệu để kiểm tra tính toàn vẹn. Việc này tốn I/O. Nếu không giới hạn giờ chạy (time window), nó sẽ tranh chấp I/O với OpenStack VM.

- Recovery/Backfilling: Dữ liệu rebalance khi node down . Khi một OSD chết và sống lại (hoặc thay ổ mới), Ceph sẽ "đổ" dữ liệu về (Backfill). Nếu không giới hạn tốc độ backfill, hệ thống sẽ bị "lụt" I/O.
- Snap trim: Snapshot cleanup operations

### 7. Vấn đề từ phía OpenStack (OpenStack‑side issues)
- Driver Cinder RBD cấu hình không tối ưu (vd: rbd_concurrent_requests quá thấp/cao).
- Glance upload chậm do cấu hình store=rbd nhưng không dùng cache
-  Nova-compute không đủ thread để xử lý nhiều volume cùng lúc.

### 8. Hệ thống chưa được tuning 
- Các tham số sysctl (vm.swappiness, vm.dirty_ratio, vm.dirty_background_ratio) chưa tối ưu.
- NF conntrack table đầy gây drop kết nối.
- Phiên bản kernel/Ceph không tương thích (vd: kernel mới nhưng driver rbd cũ).


## Quy trình Chẩn đoán lỗi 
1. Kiểm tra trạng thái Cluster tổng quát 
```bash
# Xem overview health
ceph -s
# Xem chi tiết vấn đề
ceph health detail
## Xem có cảnh báo slow/block requests không

# Xem performance của từng OSD
ceph osd perf
ceph osd tree

# Xem các slow ops hiện tại
ceph -w | grep slow

```
>  Output sẽ cho thấy OSD nào chậm, số lượng slow ops, và thời gian chờ lâu nhất.
- **Nếu chỉ 1 OSD:** Khả năng cao là lỗi ổ cứng đó.

- **Nếu cả 1 Host (nhiều OSD trên cùng 1 server):** Lỗi Network, CPU, RAM hoặc HBA Card của server đó.

- **Nếu rải rác toàn cụm:** Lỗi Network Switch, hoặc đang diễn ra Recovery diện rộng.
2. Xác Định OSD Bị Ảnh Hưởng và check logs
```bash
# Manual 
# Dump các operations đang chạy trên OSD
ceph daemon osd.{id} dump_ops_in_flight

# Xem lịch sử các operations (để hiểu pattern)
ceph daemon osd.{id} dump_historic_ops

# Xem priority queue state
ceph daemon osd.{id} dump_osd_op_queue


# Cephadm


```
> Output sẽ cho thấy : 
>    - Events column cho thấy operation đã chạy qua những bước nào
>    - "waiting for subops from [X]" → Đang chờ OSD khác replicate dữ liệu
>    - Timing cho thấy thời gian tại mỗi step


- Kiểm tra logs của ceph OSD 
Vào thư mục log (thường là `/var/log/ceph/`).
```bash
tail -f /var/log/ceph/ceph-osd.<id>.log



```
- Tìm các từ khóa: `slow request`, `blocked`, `heartbeat`.
    Nếu thấy log báo `heartbeat_check: no reply from osd.X`: Có thể OSD X hoặc mạng tới OSD X đang bị lag.

3. Kiểm Tra Phần Cứng Disk​
```bash
# Kiểm tra latency của disk theo thời gian thực
iostat -xNmy 1

# Hoặc chi tiết hơn:
iostat -dxm /dev/sda 1

# Chú ý metrics:
# await: Average I/O wait time (ms) - nên <5-10ms
# svctm: Average service time - nên <5ms
# %util: Disk utilization - 100% = bottleneck
```
- nếu chỉ số `await` > 50ms : Disk đang rất chậm
- `%util` = 100% : OSD đạt giới hạn hiệu năng 
- Nếu `await` cao nhưng `%util` thấp -> thường là lỗi về firmware
    - Cột `await` (Average Wait Time): Đây là thời gian trung bình request phải đợi.
        - **SSD Enterprise:** await nên < 5ms.
        - **HDD:** await nên < 20-50ms.
        - Nếu bạn thấy `await` lên tới hàng trăm hoặc hàng nghìn ms: Chắc chắn ổ cứng đó đang gây ra slow ops.
```bash


# Kiểm tra latency qua Ceph metrics
ceph osd perf

# Output format:
# osd.X  commit_latency(ms)  apply_latency(ms)
# Nên < 30ms commit, < 100ms apply
```

4. Kiểm Tra Mạng
Nếu disk ngon lành (`await` thấp), hãy kiểm tra tiếp đến  mạng.
```bash
# Kiểm tra OSD ping time
ceph tell osd.* version

# Hoặc xem trong cluster log:
ceph log last n

# Tìm "OSD_SLOW_PING_TIME_FRONT" hoặc "OSD_SLOW_PING_TIME_BACK"

# Kiểm tra xem có lỗi interface không 


# Kiểm tra băng thông hiện tại
iftop ( phải cài đặt không có sẵn)

sar -n DEV 1
```
- Front (public network) latency > 1000ms
- Back (cluster network) latency > 1000ms
- Nếu cả hai cao: Network issue


```bash
# Kiểm tra kết nối mạng
netstat -a | grep ceph
netstat -s  # xem packet loss

# Kiểm tra MTU
ip link show | grep mtu
# Nên đồng nhất, thường 1500 cho Ethernet

```

5. Kiểm Tra Tài Nguyên CPU/Memory
```bash
# Trên OSD node
top -p $(pgrep -f ceph-osd)

# Hoặc
ps aux | grep ceph-osd

# Kiểm tra memory:
free -h
vmstat 1 5

# Chú ý:
# CPU usage của ceph-osd process
# Memory sử dụng (nên >50% available)
# Context switches (cs column) cao = thread contention

```

6. Kiểm Tra RocksDB/Leveldb Compaction​
```bash
# Xem log OSD để tìm compaction messages
tail -f /var/log/ceph/ceph-osd.*.log | grep -i compact

# Hoặc trực tiếp dump stats
ceph daemon osd.{id} perf dump | grep compaction

# Nếu thấy compaction chạy lâu, có thể force compact:
ceph tell osd.* compact

# HOẶC từng OSD:
ceph daemon osd.0 compact
```

7. Kiểm Tra Ceph Configuration​
```bash
# Xem config hiện tại
ceph config dump | grep osd

# Chú ý các tham số:
ceph config get osd osd_op_complaint_time
ceph config get osd osd_max_backfills
ceph config get osd osd_recovery_max_active
ceph config get osd osd_op_queue
```

8. Kiểm Tra Pool/Cluster Status​
```bash
# Xem cluster capacity
ceph df

# Nếu WARN_FULL hoặc nearfull, đó là vấn đề
# Xem từng pool
ceph osd pool ls
ceph osd pool stats

# Kiểm tra full ratio
ceph osd pool get {pool} full_ratio
ceph osd pool get {pool} nearfull_ratio
```


## Cách Xử Lý Trực Tiếp SLOW_OPS

**Giải Pháp 1:** Khởi Động Lại OSD (Quick Fix - Tạm Thời)​
⚠️ Chỉ sử dụng khi cần restore service ngay lập tức

```bash
# Xác định OSD nào chậm từ ceph health detail

# Gracefully stop OSD (nên restart một lúc, không cùng lúc)
systemctl stop ceph-osd@{id}

# Ceph sẽ rebalance tự động - chờ cluster trở lại HEALTH_OK
ceph -w | grep health

# Khởi động lại
systemctl start ceph-osd@{id}

# Kiểm tra
ceph osd perf | grep osd.{id}
Lưu ý: Đây chỉ là fix tạm thời, vấn đề sẽ tái phát nếu nguyên nhân gốc không được giải quyết.

```

**Giải Pháp 2:** RocksDB Compaction​
Nếu disk latency tăng dần và thấy compaction messages:

```bash
# Nếu chỉ một OSD
ceph daemon osd.{id} compact

# Hoặc tất cả OSD (từng cái một để tránh cluster down)
for osd in $(ceph osd ls); do
    ceph daemon osd.$osd compact &
    sleep 300  # chờ 5 phút trước compaction tiếp theo
done
Hoặc cấu hình auto-compact trên restart:

bash
ceph config set osd leveldb_compact_on_mount true
```
Sau đó restart OSDs.

**Giải Pháp 3:** Tối Ưu Disk I/O - Nếu Disk Chậm​
```bash
# Kiểm tra hiện tại
ceph osd perf

# Nếu disk 100% utilized, tăng OSD threads (cần restart)
ceph config set osd osd_op_threads 8
ceph config set osd osd_disk_threads 4
ceph config set osd ms_async_op_threads 5

# Tắt C-states (nếu BIOS cho phép)
# Thực hiện trên node, không phải ceph command
# Khi boot hoặc modify BIOS:
# - Disable CPU C-states
# - Set CPU to Performance mode
# - Disable CPU power management

# Sau khi thay đổi, restart OSD
systemctl restart ceph-osd@{id}
```

**Giải Pháp 4:** Điều Chỉnh Recovery/Backfill Settings​
Nếu slow ops xảy ra khi cluster recovery:

```bash
# Kiểm tra hiện tại
ceph config get osd osd_max_backfills  # default: 1
ceph config get osd osd_recovery_max_active  # default: 3

# Giảm để ít aggressive hơn (chậm hơn nhưng ít ảnh hưởng client)
ceph config set osd osd_max_backfills 1
ceph config set osd osd_recovery_max_active 3
ceph config set osd osd_recovery_sleep_degraded 0.5

# Hoặc tạm dừng recovery nếu quá khẩn cấp
ceph osd set norebalance
ceph osd set norecovery

# Sau khi xử lý xong:
ceph osd unset norebalance
ceph osd unset norecovery
```


**Giải Pháp 5:** Kiểm Tra & Sửa MTU Network​
```bash
# Xem MTU hiện tại
ip link show

# Đặt MTU (trên mỗi node, cần planned downtime)
ip link set dev {interface} mtu 1500

# Hoặc qua netplan/ifupdown config
# Sau đó restart network hoặc reboot

# Verify
ip link show dev {interface} | grep mtu
```

**Giải Pháp 6:** Tối Ưu RocksDB Settings​
Nếu OMAP-heavy workload (nhiều deletions):

```bash
# Thêm vào ceph.conf và restart OSD:
[osd]
rocksdb_cache_size = 536870912  # 512MB, tùy CPU cores
rocksdb_block_size = 4096
rocksdb_perf_multiplier = 10

# Hoặc runtime (reef+):
ceph config set osd rocksdb_cache_size 536870912
```
**Giải Pháp 7:** Giảm PGs nếu PGs/OSD quá cao​
⚠️ Đây là thao tác nặng, cần planning cẩn thận

```bash
# Kiểm tra PGs per OSD
ceph osd df | head -20

# Nếu >200 PGs/OSD, có thể reduce (cần monitor)
ceph osd pool set {pool} pg_num {new_value}
ceph osd pool set {pool} pgp_num {new_value}

# Chỉ giảm, không tăng
# Ceph sẽ rebalance - chờ HEALTH_OK

```

### Xử lý ổ cứng chậm 
- Nếu `iostat` báo `await` cao và `dmesg` có lỗi: Thay ổ cứng ngay. Đừng cố gắng sửa.

- Trong lúc chờ thay, hãy `ceph osd out <osd_id>` để cluster không ghi thêm dữ liệu vào đó, giảm tải cho nó.

### Tuning Recovery (Giảm tốc độ để cứu latency) và Tối ưu Scrubbing 
- Nếu hệ thống đang recovery mà gây slow ops, hãy giảm tốc độ lại (chấp nhận recovery lâu hơn để VM không bị treo). Set tạm thời các cờ sau:

```bash
# Giảm mức độ ưu tiên của recovery
ceph config set osd osd_recovery_op_priority 1
# Giới hạn số lượng backfill đồng thời (Default thường là 1, nhưng có thể đã bị chỉnh lên cao)
ceph config set osd osd_max_backfills 1
# Giới hạn tốc độ sleep giữa các lần recovery (tăng lên để giảm tải)
ceph config set osd osd_recovery_sleep 0.5

# Chỉ cho phép scrubbing theo giờ thấp điểm 
ceph config set osd osd_scrub_begin_hour 22
ceph config set osd osd_scrub_end_hour 06

# Kiểm soát swap 
- Set vm.swappiness = 1 hoặc 10 trên các node OSD (đừng để mặc định 60).
- Hoặc tốt nhất là disable hẳn swap 
```


