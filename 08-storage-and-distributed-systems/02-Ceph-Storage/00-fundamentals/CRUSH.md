# Mục lục




---

# Tổng quan 
- CRUSH là trái tim của Ceph — một **thuật toán ánh xạ dữ liệu phi tập trung**, được đề xuất trong paper “CRUSH: Controlled, Scalable, Decentralized Placement of Replicated Data” (Sage Weil, SC’06).

Nó xác định vị trí lưu trữ dữ liệu mà **không cần bảng metadata trung tâm**, giúp Ceph scale tới hàng nghìn node.

- CRUSH là một cải tiến từ thuật toán RUSH ("Replication Under Scalable Hashing"). Cho phép:
    + Ánh xạ có kiểm soát (controlled mapping): người dùng có thể định nghĩa topology và chính sách replication.
    + Khả năng mở rộng: không cần tra cứu bảng metadata.
    + Tối thiểu di chuyển dữ liệu: khi thêm node mới, chỉ các phần liên quan bị remap.

- **Mục tiêu **:Thuật toán này **phân phối dữ liệu ngẫu nhiên có kiểm soát** (“*controlled pseudo-random*”) nhằm đảm bảo:
    + Dữ liệu trải đều trên toàn cluster.
    + Replica được tách theo failure domain.
    + Khi thêm/xóa node, dữ liệu di chuyển tối thiểu cần thiết.

> CRUSH là nền tảng của Ceph. Tất cả lớp cao hơn (RADOS, CephFS, RGW) đều dựa trên CRUSH để định vị dữ liệu.

> Một CRUSH map được thiết kế tốt = cân bằng dữ liệu, đảm bảo an toàn, phục hồi nhanh và scale mượt mà khi mở rộng cluster.

---

# Kiến trúc CRUSH
## Các thành phần chính
- CRUSH hoạt động dựa trên 2 khối:
    + **CRUSH Algorithm** – hàm ánh xạ xác định vị trí lưu object.
    + **CRUSH Map** – cấu trúc phân cấp mô tả hạ tầng vật lý (root, datacenter, rack, host, osd) và chính sách replication.

## Cơ chế hoạt động căn bản 
Sử dụng hàm hash để ánh xạ dữ liệu vào OSD dựa trên cấu trúc cluster (rack, host). Hỗ trợ replication hoặc erasure coding. Khi thêm/xóa node, CRUSH tự cân bằng dữ liệu.

## Đặc tính Ánh xạ Xác định (Deterministic Mapping)
### Nguyên lý Ánh xạ Xác định
Ánh xạ xác định là thuộc tính đảm bảo rằng với một tập hợp đầu vào cố định, thuật toán CRUSH sẽ luôn sinh ra cùng một kết quả đầu ra. Cụ thể, khi biết:
- Object ID (hoặc Placement Group ID)
- CRUSH Map (mô tả topology cluster và các rule)
- CRUSH Rule (chính sách placement)

bất kỳ client hoặc daemon nào trong hệ thống cũng sẽ tính toán ra chính xác cùng một danh sách OSD đích để lưu trữ hoặc truy xuất dữ liệu.

> Tính chất này được triển khai thông qua một hàm băm (hash function) xác định trong thuật toán CRUSH. Hàm này xử lý các đầu vào nêu trên để tạo ra một chuỗi các lựa chọn OSD một cách nhất quán và có thể dự đoán được.

### Ý nghĩa Kiến trúc
Đặc tính này là **nền tảng cho kiến trúc phi tập trung (decentralized) của Ceph**:

- **Không cần Tra cứu Metadata Trung tâm:** Client có thể xác định chính xác vị trí dữ liệu mà không cần liên hệ với một dịch vụ metadata tập trung. Điều này loại bỏ điểm tắc nghẽn (bottleneck) và điểm lỗi đơn (single point of failure).

- **Nhất quán Toàn cục:** Tất cả các thành phần trong cluster (Client, OSD, Monitor) đều có khả năng độc lập tính toán và đạt được kết quả ánh xạ giống hệt nhau, đảm bảo tính nhất quán của dữ liệu.

### Tối ưu Hiệu suất mở rộng
Ánh xạ xác định trực tiếp dẫn đến hiệu quả trong việc quản lý dữ liệu khi cluster thay đổi:

- **Di chuyển Dữ liệu Tối thiểu (Minimal Remapping):** Khi cluster được mở rộng (thêm OSD) hoặc thu hẹp (xóa OSD), CRUSH Map thay đổi. Khi đó, thuật toán được thiết kế để chỉ những dữ liệu được ánh xạ tới các OSD bị ảnh hưởng trực tiếp bởi sự thay đổi (ví dụ: OSD bị xóa hoặc vùng dữ liệu được phân bổ lại cho OSD mới) mới cần di chuyển.

- **Tiệm cận Lý thuyết:** Lượng dữ liệu di chuyển này được chứng minh là tiệm cận với giới hạn tối thiểu lý thuyết (theoretical minimum) cho bất kỳ thuật toán phân phối dữ liệu nào. Trong thực tế, điều này có nghĩa là khi thêm một OSD mới có trọng số (weight) chiếm 1% tổng dung lượng cluster, thì chỉ có khoảng 1% dữ liệu toàn cluster là cần được di chuyển để tái cân bằng.

> Tính chất deterministic mapping, kết hợp với cấu trúc hierarchy và các bucket algorithm (như Straw2), cho phép CRUSH đạt được sự cân bằng giữa tính ngẫu nhiên để phân phối đều (load balancing) và tính xác định để giảm thiểu di chuyển dữ liệu, từ đó tạo nên một hệ thống lưu trữ phân tán có khả năng mở rộng cao và hiệu quả.

## CRUSH Lookup
CRUSH lookup là quá trình tính toán ánh xạ giữa object (hoặc PG) và danh sách OSD.  Điểm quan trọng là **tất cả client, OSD, MON đều có thể tự tính được cùng một kết quả, miễn cùng CRUSH map.**

### Quy trình thực tế trong Ceph
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/ceph-workflow.png)

1. Client nhận cluster map (từ MON).
2. Khi ghi dữ liệu:
- Object → hash → Placement Group (PG).
- PG ID được đưa vào CRUSH cùng rule tương ứng.
- CRUSH trả về danh sách OSDs (primary + replicas hoặc EC shards).

3. Client gửi trực tiếp tới primary OSD, không cần trung gian.
4. Primary OSD tự đồng bộ sang các replica OSD còn lại.
- Cơ chế phân phối tính toán
- Tất cả phép tính lookup diễn ra ở client/daemon → không gây tải cho MON.
- Lookup là metadata computation distributed, không centralized.
- CRUSH loop chạy trong không gian của client (C++ hoặc librados), cho phép tốc độ lookup microsecond-level.
- Với cùng CRUSH map + input (object, rule), output luôn giống nhau (deterministic mapping).
- Khi thêm hoặc xóa OSD, lượng dữ liệu di chuyển (remap) tiệm cận mức tối thiểu lý thuyết.
- Điểm đặc biệt cho CRUSH Lookup là không phụ thuộc vào hệ thống. Ceph cung cấp tính linh hoạt cho client thực hiện tính toán theo metadata khi cần bằng cách chạy CRUSH loop với tài nguyên của chính client, giảm công việc tại centrel.
- Với các hoạt động tại Ceph cluster, client tương tác với Ceph monitor nhận lại cluster map. Cluster map giúp client biết trạng thái cấu hình Ceph cluster. Data được chuyển thành object với obj và pool name/IDs. Obj sau đối hashed với số vị trí group để sinh ra vị trí group cuối cùng mà không yêu cầu Ceph pool.
- Tính toán ví trị group sẽ thông qua CRUSH lookup để quyết định vị trí primary OSD lưu và lấy lại. Sau tính toán, chiết xuất OSD ID, client liên hệ với OSD trực tiếp, lưu data. Tất các tính toán thực hiện bởi client, do đó nó không ảnh hưởng tới hiệu năng cluster. Khi data ghi tới primary OSD, node tương tự thực hiện hoạt động CRUSH lookup và tính toán vị trí secondary placement groups (vị trí phụ thứ yếu) và OSD, vì thế data được nhân rộng khắp Cluster cho tính HA.

## CRUSH Hierarchy
### Khái niệm về Failure Zones
- CRUSH có khả năng nhận thức hạ tầng, hoàn toàn do user cấu hình. Nó duy trì nested hierarchy (phân cấp lồng nhau) cho tất cả thành phần của hạ tầng.
Các thành phần được biết tới = failure zones hay CRUSH buckets.

### Cấu trúc CRUSH Map
CRUSH Map chứa list các bucket có sẵn tập hợp các thiết bị trong các vị trí vật lý. Đồng thời chứa list rule cho phép CRUSH tính toán nhân bản data trên các Ceph pool khác nhau.
- Cấu trúc CRUSH Map gồm các tầng:
```
root → datacenter → row → rack → host → osd
```
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/crushmap-1.png)

- Mỗi tầng là một **bucket**, có thể chứa bucket con hoặc thiết bị.
- CRUSH sử dụng topology này để phân phối dữ liệu qua các failure zones, đảm bảo an toàn và sẵn sàng.

### Cách CRUSH sử dụng hierarchy
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/hierarchy-replica.png)

#### Phân phối replica
- Khi nhân bản dữ liệu, CRUSH chọn replica ở các bucket khác nhau (ví dụ, 3 host khác rack).
- Nếu một node/rack bị lỗi, các replica còn lại vẫn khả dụng.

#### Lợi ích của cấu trúc hierarchy
Cấu trúc hierarchy giúp CRUSH:
- Đảm bảo tính High Availability (HA).
- Giữ phân phối công bằng dựa trên weight.
- Cho phép tận dụng commodity hardware mà vẫn duy trì độ tin cậy cao.

#### Cơ chế đảm bảo an toàn dữ liệu
- Dựa trên hạ tầng, CRUSH truyền data, nhân bản data trên khắp failure zones khiến data an toàn, có sẵn kể cả khi 1 số thành phần lỗi.
=> Đây là cách CRUSH loại bỏ các thành phần có khả năng lỗi trên hạ tầng lưu trữ, đồng thời nó sử dụng các thiết bị thông thường mà vẫn đảm bảo tính HA (ko phải thiết bị chuyên dụng).


## CRUSH Buckets
CRUSH bucket là các container logic chứa các thiết bị (OSD) hoặc bucket con, sử dụng các thuật toán khác nhau để lựa chọn item khi ánh xạ dữ liệu. Việc lựa chọn loại bucket phù hợp ảnh hưởng trực tiếp đến:
- Hiệu năng ánh xạ dữ liệu

- Mức độ di chuyển dữ liệu khi cluster thay đổi

- Khả năng cân bằng tải

### Các Loại Bucket 
- Uniform bucket: 
    + Sử dụng hash trực tiếp, giả định tất cả items có cùng weight
    + Độ phức tạp: O(1) nên tốc độ cực nhanh => Tốc độ ánh xạ nhanh nhất
    + Phải remap toàn bộ dữ liệu khi thay đổi weight hoặc thêm/xóa item => Nhược điểm
    + Sử dụng cho cluster đồng nhất 100% (rất hiếm trong thực tế)
- List bucket: 
    + Duyệt tuần tự từ đầu đến cuối danh sách
    + Độ phức tạp: O(n) => Tốc độ chậm với danh sách lớn => Thêm item mới dễ dàng
    + Xóa item tốn chi phí, hiệu năng giảm khi số lượng item tăng => Nhược
    + Sử dụng cho Legacy systems, không khuyến nghị cho cluster mới
- Tree bucket: 
    + Sử dụng cây nhị phân cân bằng để tìm kiếm
    + Độ phức tạp: O(log n) - cân bằng tốt => Cân bằng giữa tốc độ chọn và chi phí tái cấu trúc
    + Remap trung bình khi có thay đổi 
    + Sử dụng cho cluster lớn cần cân bằng giữa performance và maintenance

- Straw bucket: 
    + Mỗi item "rút thăm" với độ dài straw tỷ lệ với weight
    + Độ phức tạp: O(n) - nhưng thực tế nhanh hơn List bucket =>  Đảm bảo tính công bằng (fairness) và minimal remap
    + Có bias nhất định khi weight thay đổi

- Straw2 bucket (Mặc định hiện nay): 
    + Phiên bản cải tiến của Straw, sử dụng thuật toán "rút thăm" với xác suất tỷ lệ weight
    + Độ phức tạp: O(n) - tương đương Straw 
    + Giảm bias khi weight thay đổi, đảm bảo minimal remap (di chuyển dữ liệu tối thiểu) và ngẫu nhiên có kiểm soát để cân bằng tải => Ưu điểm cải tiến lớn nhất
    + Nhược điểm: Chậm hơn Uniform và Tree
    + Mặc định dùng cho mọi bucket mới trong Ceph (từ Nautilus).

**So sánh nhanh :**

| Kiểu bucket | Cơ chế | Độ phức tạp | Thêm item | Xóa item | Remap khi đổi weight | Phạm vi sử dụng |
|-------------|---------|-------------|-----------|----------|---------------------|-----------------|
| **Uniform** | Hash trực tiếp | O(1) | Remap toàn bộ | Remap toàn bộ | Remap toàn bộ | Cluster đồng nhất |
| **List** | Duyệt tuần tự | O(n) | Dễ dàng | Tốn kém | Remap ít | Legacy |
| **Tree** | Cây nhị phân | O(log n) | Trung bình | Trung bình | Remap trung bình | Map lớn |
| **Straw** | Rút thăm | O(n) | Nhanh | Nhanh | Remap tối thiểu | Được thay thế bởi Straw2 |
| **Straw2** | Rút thăm cải tiến | O(n) | Nhanh | Nhanh | **Remap tối thiểu** | **Mặc định hiện nay** |

**Khuyến nghị :**
- Cluster mới: Luôn sử dụng Straw2 làm bucket type mặc định

- Cluster đồng nhất tuyệt đối: Cân nhắc Uniform nếu đảm bảo không thay đổi hardware

- Cluster lớn với OSD count cao: Straw2 vẫn là lựa chọn tối ưu

- Legacy migration: Chuyển đổi dần từ List/Tree sang Straw2 để tận dụng minimal remap

## Weight Balancing
### Khái niệm về OSD Weight
Mỗi OSD có trọng số (weight) phản ánh khả năng lưu trữ hoặc hiệu năng.
=> Để làm được điều đó, CRUSH cấp phát weights trên mỗi OSD. Cân năng càng cao trên OSD thì khả năng lưu trữ của chính OSD càng cao.

### Cơ chế phân phối dữ liệu theo weight
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/weight-balancing.png)
- CRUSH ghi nhiều dữ liệu hơn vào OSD có weight cao hơn, từ đó CRUSH ghi nhiều data tới những OSD này, duy trì tính cân bằng trên các thiết bị.
- CRUSH ghi data công bằng trên khắp cluster disk, tăng hiệu năng, tính bảo đảm, đưa tất cả disk vào cluster.
- Nó chắc rằng tất cả cluster disk được sử dụng bằng nhau kể cả khả năng lưu trữ khác nhau.

### Tối ưu hóa khi thay đổi weight
Khi weight thay đổi, thuật toán chỉ dịch chuyển lượng dữ liệu tối thiểu.


## CRUSH Rules & Placement
- CRUSH Rule là định nghĩa cách dữ liệu được phân phối trên cluster.
- Thông thường sẽ có 2 kiểu:

    + Replicated Rules: cho replication pool.
    + Erasure Coded Rules: cho EC pool (giúp tiết kiệm dung lượng).

- Cú pháp 
```
rule replicated_rule {
    step take default
    step chooseleaf firstn 3 type host
    step emit
}
```
- `take`: điểm bắt đầu (root hoặc bucket cụ thể).
- `chooseleaf firstn 3 type host`: chọn 3 OSD trên 3 host khác nhau.
- `emit`: xuất kết quả.

### Replicated pools
CRUSH chọn N OSD khác nhau để lưu N replica.
Các replica nằm ở failure domain tách biệt (host hoặc rack khác nhau).

### Erasure-coded pools
- Cơ chế hoạt động
    + Dữ liệu chia thành k+m shard (k data, m parity).
    + CRUSH chọn OSD cho từng shard dựa theo rank.

- EC rules khác replication rule ở chỗ :
    + Giữ thứ tự strict giữa rank → shard.
    + Dùng lựa chọn `indep` để xử lý placement độc lập.

# Vận hành và tối ưu 

## Cơ chế Recovery (Khôi phục)
### Thời gian chờ và Phát hiện lỗi
- **Cơ chế phát hiện:** Ceph sử dụng heartbeat mechanism để phát hiện OSD `down`. Các OSD liên tục gửi tin nhắn heartbeat cho nhau và báo cáo trạng thái tới Monitor.

- **Thời gian chờ mặc định:** 300 giây trước khi đánh dấu OSD là `down` và bắt đầu recovery.

- **Tùy chỉnh:** Thông qua parameter `mon_osd_down_out_interval` trong cấu hình Ceph Cluster.
```bash
# Ví dụ tùy chỉnh thời gian chờ
mon_osd_down_out_interval = 600  # Tăng lên 600 giây
```

### Quá trình khôi phục
1. Xác định PGs cần khôi phục:

- Monitor xác định các Placement Groups (PGs) bị ảnh hưởng bởi OSD failure

- Đánh dấu PG trạng thái degraded

2. Chọn nguồn khôi phục:

- Primary OSD của PG sẽ chọn replica OSDs còn lại làm nguồn khôi phục

- CRUSH đảm bảo replicas được phân tán trên các failure domain khác nhau

3. Đồng bộ dữ liệu:

- Dữ liệu được sao chép từ replicas còn lại sang OSD thay thế

- Sử dụng versioning để đảm bảo consistency

### Tối ưu hóa di chuyển dữ liệu
- **Parallel Recovery:** Multiple PGs được recovery đồng thời

- **Backfill Recovery:** Recovery không ảnh hưởng đến client I/O

- **Throttling Controls:** Có thể điều chỉnh tốc độ recovery để tránh ảnh hưởng hiệu năng

```bash
# Các tham số tối ưu recovery
osd_recovery_max_active = 3      # Số PGs recovery đồng thời
osd_recovery_max_single_start = 1 # Số operations recovery khởi tạo đồng thời
osd_recovery_sleep = 0           # Thời gian nghỉ giữa các recovery operations
```

## Cơ chế Rebalancing
### Điều kiện kích hoạt Rebalancing
- **Thêm OSD/host mới:** CRUSH tự động tính toán lại data distribution

- **Thay đổi CRUSH Map:** Điều chỉnh weights, rules, hoặc topology

- **OSD failure kéo dài:** Khi OSD bị đánh dấu `out` của cluster

### Quy trình Rebalancing
1. Tính toán data movement:

- CRUSH algorithm tính toán PGs cần di chuyển dựa trên weight changes

- Chỉ những PGs bị ảnh hưởng bởi thay đổi topology mới được remap

2. Backfill process:

- Dữ liệu được di chuyển từ OSDs hiện tại sang OSDs mới

- Quá trình chạy nền, ưu tiên thấp hơn client I/O

3. Parallel execution:

- Nhiều OSDs tham gia đồng thời vào quá trình backfill

- Tự động điều chỉnh tốc độ dựa trên cluster load

### Ví dụ thực tế tính toán lượng dữ liệu di chuyển
**Ví dụ:**
Nếu Ceph cluster chứa 2000 OSDs, 1 hệ thống mới được thêm vào với 20 OSDs mới => 1% data sẽ được chuyển trong quá trình tái cân bằng, tất cả OSDs đã có sẽ làm việc song song khi chuyển data, giữ các hoạt động diễn ra bình thường.

- Công  thức ước tính:
```
Data_movement_percentage = (New_total_weight - Old_total_weight) / Old_total_weight × 100%
```
- Cluster hiện tại: 2000 OSDs, tổng weight = 2000

- Thêm 20 OSDs mới, mỗi OSD weight = 1.0

- Lượng data di chuyển ≈ (2020 - 2000) / 2000 × 100% = 1%

### Best Practices và Khuyến nghị
Chiến lược thêm OSD mới:
```bash
# Bước 1: Thêm OSD với weight = 0
ceph osd crush set osd.<id> 0 root=default

# Bước 2: Tăng weight từ từ
ceph osd crush reweight osd.<id> 0.25
ceph osd crush reweight osd.<id> 0.5
ceph osd crush reweight osd.<id> 0.75
ceph osd crush reweight osd.<id> 1.0
```

Các tham số điều chỉnh rebalancing:
```bash
# Giới hạn tác động đến client I/O
osd_max_backfills = 1           # Số backfills đồng thời mỗi OSD
osd_backfill_full_ratio = 0.85  # Ngừng backfill khi OSD đạt 85% capacity
osd_backfill_retry_interval = 10 # Thời gian chờ retry failed backfills
```

## Cơ chế tái cấu trúc layout
### Nguyên lý Minimal Data Movement
- **Deterministic mapping:** Cùng input (PG + CRUSH Map) → cùng output OSDs

- **Incremental changes:** Chỉ PGs bị ảnh hưởng trực tiếp bởi topology changes mới remap

- **Straw2 algorithm:** Đảm bảo minimal remap khi thay đổi weights

### Quy trình tái ánh xạ
1. Client/OSD computation:

- Mỗi client và OSD tự tính toán mapping mới khi CRUSH Map thay đổi

- Không cần centralized coordination

2. Graceful degradation:

- Trong thời gian remap, hệ thống vẫn phục vụ I/O

- Dữ liệu được đọc từ cả vị trí cũ và mới trong quá trình chuyển đổi

3. Atomic updates:

- PG mappings được cập nhật atomic qua Monitor

- Đảm bảo consistency trên toàn cluster

### Monitoring và Quản lý
```bash
# Kiểm tra recovery status
ceph status
ceph health detail

# Theo dõi PG states
ceph pg stat

# Kiểm tra backfill progress
ceph -s
```

# Các Tính Năng Nâng Cao 
## Device Classes
Phân loại thiết bị theo tốc độ (SSD, HDD, NVMe, slow, fast).

- CRUSH rule có thể target device class cụ thể, ví dụ:
```
step take default class ssd
step chooseleaf firstn 3 type host
```
Điều này giúp pool phân biệt tier dữ liệu mà không cần map thủ công.

## Tunables
CRUSH có sẵn các profile như legacy, hammer, optimal, straw2, ... có thể dùng để đảm bảo tính tương thích khi nâng cấp cluster.

```bash
# Lệnh kiểm tra và áp dụng
ceph osd crush show-tunables
ceph osd crush tunables optimal
```


# Các Thao tác với CRUSH

- Xuất và biên dịch CRUSH map
```bash
# Xuất map
ceph osd getcrushmap -o crushmap.bin
crushtool -d crushmap.bin -o crushmap.txt

# Biên dịch lại map
crushtool -c crushmap.txt -o crushmap_new.bin
ceph osd setcrushmap -i crushmap_new.bin

# Kiểm tra map
crushtool --test --show-utilization crushmap.txt
```

