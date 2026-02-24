# Lỗi LARGE_OMAP_OBJECTS trong Ceph RGW - S3
- OMAP (Object Map) là phần metadata được lưu trữ dưới dạng Key-Value trong RocksDB của OSD.Khi một object có quá nhiều keys (mặc định > 200,000) hoặc dung lượng quá lớn, các tiến trình như Deep Scrub, Recovery, hoặc Backfill sẽ gây nghẽn I/O, làm chậm phản hồi OSD, thậm chí gây sập OSD (Timeout).

- Theo Ceph health checks và kinh nghiệm vận hành thực tế, ít nhất 3 nhóm nguyên nhân phổ biến gây cảnh báo large omap object: 
1. **Index bucket quá lớn (RGW bucket index)**:
    Khi một bucket có quá nhiều key/entries trong omap index (ví dụ bucket chứa hàng trăm nghìn object/version) → kích thước omap lớn vượt thresholds. Điều này xảy ra thường khi:
    - Bucket chưa reshard tốt hoặc dynamic resharding không kịp. Bucket đang có quá nhiều object/version gây nên một shard chứa quá nhiều entries. Hoặc một nguyên nhân cũng do shards là số lượng shards thấp khiến mỗi shards chứa lượng entries quá lớn .
    - Bucket có rất nhiều phiên bản (versioning) → mỗi phiên bản tạo dấu entry trong omap → dồn vào 1 shard.

> Đây là nguyên nhân phổ biến trên cả single-site và multisite nếu bucket lớn hoặc versioned 

2. **Versioning / multipart / nhiều bản ghi nhỏ liên tục**
Mỗi version/part dữ liệu lại tạo entry metadata → cộng dồn gây đầy

3. **Tombstones / GC chưa chạy**
Xóa/ Tạo markers chưa được thu gom → giữ nhiều key

4. **Stale bucket index trong môi trường multisite**
- Deleted bucket index vẫn còn tồn tại trong stale instances do sync chưa hoàn tất, không bị xóa tự động.
=> Điều này tạo ra một object .dir.<bucketID>… trong pool rgw.buckets.index có omap rất lớn → deep-scrub sẽ cảnh báo.

> Đặc trưng ở RGW Multisite, nhất là khi delete bucket ở 1 site nhưng chưa sync sạch sang site kia.

5. **Sync/log/usage omap lớn (log pool / usage entries)**
Một số trường hợp large omap có thể xảy ra không phải index pool mà ở:
- pool `rgw.log` do sync error logs chưa được trim.
- pool `rgw.usage` chứa usage statistics.
=> Các trường hợp này cũng gọi là large omap nhưng nguyên nhân khác hoàn toàn với index bucket 

## Xác định nguyên nhân
### Bước 1: Xác đinh các thông tin 
```bash
ceph -s # Trạng thái tổng quan để xác nhận lỗi large omap 
ceph health detail # Xem chi tiết osd bị LARGE OMAP OBJECTS 
grep -i "Large omap object found" /var/log/ceph/ceph.log # Xem thử log

# Map object bị large omap
## nếu object tên chứa bucket-id (.dir.<bucket-id>...), lấy bucket-id
radosgw-admin metadata list --metadata-key bucket.instance | grep <bucket-id>
## hoặc liệt kê bucket instance entries
radosgw-admin metadata list --metadata-key bucket

# bucket stats
radosgw-admin bucket stats --bucket=<bucket-name>
## xem num_objects, size, num_shards, versioning flag

# Đếm keys trong omap object (read)
rados -p <pool-name> listomapkeys <object-name> | wc -l
## hoặc lấy vài dòng đầu để kiểm tra dạng key:
rados -p <pool-name> listomapkeys <object-name> | head -n 20

# Xem PG info 
ceph pg <pgid> query

# Check bilog / reshard queue / sync status
## Multisite 
radosgw-admin sync status và radosgw-admin bucket sync status --bucket=<bucket>.

#Reshard queue 
radosgw-admin reshard list / radosgw-admin reshard status --bucket=<bucket>.
```
Từ đây xác định được :
- Pool nào bị (rgw.buckets.index / rgw.log / rgw.usage)?
- Object name (thường `.dir.<bucket-id>...` cho bucket index) — có thể map về bucket-id? Key count & size lớn cỡ nào?
- PG chứa object (PGID) — để giới hạn scope deep-scrub.
- Kiểm tra xem RGW đang là singlesite hay multisite 

Khi đã xác định được pool type thì có thể giới hạn được vấn đề : 
- Nếu pool là `rgw.buckets.index` → bucket index case. Lỗi do Bucket quá lớn hoặc Versioning quá nhiều. (Chiếm 90% trường hợp).
- Nếu pool là `rgw.log` / `rgw.usage` → xử lý log/usage case. Lỗi do log hệ thống hoặc thống kê sử dụng tích tụ lâu ngày.
- Nếu pool là `rgw.otp` / `rgw.meta` → Lỗi metadata hệ thống

### Bước 2 : Xử lý theo từng trường hợp 
#### 2.1 CASE A — Bucket index quá lớn (single big bucket)
**Dấu hiệu:** object là `.dir.<id>`, `key count >> threshold` (ví dụ >200k hoặc >1GB tuỳ config), bucket stats cho thấy `num_objects` rất lớn, `num_shards` thấp.
- **Kiểm tra thông tin:** 
```bash
# Lấy ID từ tên object tìm được ở Bước 1 và map ra tên bucket
radosgw-admin metadata get bucket.instance:<id> | grep '"bucket":'

# Kiểm tra chỉ số phân mảnh hiện tại
radosgw-admin bucket stats --bucket=<bucket_name> | grep num_shards
```
- **Các bước xử lý gợi ý:**
    - **Bật/khởi chạy dynamic resharding (nếu chưa bật / phiên bản hỗ trợ):** dynamic sẽ tự phân tách index background. Theo docs, dynamic resharding có từ Luminous trở đi. Giám sát queue.

    - **Reshard thủ công (có thể làm online):** thêm reshard task vào queue hoặc chạy `radosgw-admin bucket reshard --bucket=<bucket> --num-shards=<N>` hoặc `radosgw-admin reshard add ...` rồi `radosgw-admin reshard process`. Đây là thao tác metadata nhưng được thiết kế để thực hiện online (không cần dừng RGW). Chọn số shards hợp lý (thường chọn số lớn / prime numbers). Lưu ý là quá trình này sẽ khóa (lock) các thao tác ghi vào bucket trong khi thực hiện. Nên khuyến khích thực hiện vào giờ thấp điểm  

    - **Sau resharding:** chạy deep-scrub chỉ PG bị ảnh hưởng (`ceph osd pg deep-scrub <pgid>`) để clear health warning.

> **Rủi ro / lưu ý:** resharding tạo I/O background; manual reshard vẫn là thay đổi metadata — test trên staging nếu lần đầu. Khi resharding hoàn tất có thể cần chạy `radosgw-admin lc reshard fix` nếu lifecycle policies bị ảnh hưởng (các phiên bản cũ hơn cần)

#### 2.2 CASE B — Tombstones / GC chưa chạy (single-site)
- **Dấu hiệu:** bucket stats cho thấy num_objects nhỏ, nhưng listomapkeys lại trả về con số khổng lồ. Đây là các "dấu vết" (tombstones) chưa được Garbage Collection (GC) quét sạch.`radosgw-admin gc list` c
- **Thông tin cần check:** 
    - Kiểm tra danh sách GC còn tồn đọng: `radosgw-admin gc list --include-all.`
    - Xem log RGW để tìm các lỗi liên quan đến GC bị nghẽn.
- **Các cách xử lý gợi ý:**
    - Chạy GC/expire policies theo cách an toàn (thực hiện từng bước, giới hạn phạm vi nếu tool cho phép).
    - Tăng tốc độ xử lý GC bằng cách điều chỉnh `rgw_gc_max_objs` và `rgw_gc_processor_period`
    - Chạy thủ công tiến trình dọn dẹp nếu cần (cần cẩn trọng với I/O)
> Rủi ro: GC xóa metadata/data — đảm bảo retention policy và backup trước nếu nhạy cảm.

#### 2.3 CASE C — Phình to Log Pool(rgw.usage / rgw.log)
- **Dấu hiệu:** Cảnh báo Large OMAP xuất hiện ở các pool hệ thống (rgw.usage, rgw.log) thay vì pool index dữ liệu.

- **Thông tin cần check:** l
    - Liệt kê object trong pool bị báo lỗi: rados -p rgw.log ls.
    - Đếm key của các object log bị cảnh báo.

- **Các bước xử lý gợi ý:**
    1. Sử dụng lệnh Trim: ví dụ `radosgw-admin usage trim --start-date=YYYY-MM-DD --end-date=YYYY-MM-DD` hoặc `radosgw-admin bilog trim --bucket=...` để prune logs. Sau đó deep-scrub PG.
        - Với log đồng bộ: radosgw-admin log trim --end-date=...
    2. Throttle trim / chạy theo batches để không spike I/O.
> Rủi ro: Trim thay đổi metadata/history; kiểm tra backup/retention.

#### 2.4 CASE D — Lỗi Logic Multisite (Stale Instances / Sync Stuck)
- **Dấu hiệu:** 
    - bucket-id xuất hiện ở stale instances, `radosgw-admin sync status` cho thấy sync stuck; Red Hat paper đề cập `bilogs not trimmed → large omap`.
    - Object .dir.<id> bị báo lỗi nhưng khi tra cứu ID bằng metadata get thì trả về lỗi 404 (không tồn tại bucket).

- **Thông tin cần check:** 
    - `radosgw-admin metadata list --metadata-key bucket.instance`
    - `radosgw-admin bilog list --bucket=<bucket>`
    - `radosgw-admin sync status`.

- **Các bước xử lý gợi ý:**
    1. Không chạy destructive ngay. Trước hết: check why sync stuck (network, credentials, replication policy).
    2. Nếu chắc chắn stale và quyết định cleanup: **trim bilog** via r`adosgw-admin bilog trim --bucket="..." --bucket-id="..."` (dùng cautiously) — Red Hat khuyến nghị các bước trim & sau đó deep-scrub.
    3. Nếu bạn muốn tránh data loss: tạm disable bucket sync (`radosgw-admin bucket sync disable --bucket=<bucket>`) để ngăn thêm thay đổi cross-site trước khi trim — nhưng thao tác này thay đổi sync state (thực hiện cẩn trọng).
> Rủi ro: trim bilog là thao tác chỉnh sửa metadata; sai thao tác có thể làm mất dữ liệu replication state — test trên staging; ideally thực hiện trên một site duy nhất (cleanup stale instances chỉ làm trên single site cluster).

### 2.5 CASE E - Artifacts sau Reshard hoặc lỗi do old verison
- **Dấu hiệu:** 
    - Đã reshard nhưng vẫn có large omap; mailing lists cho biết có trường hợp bilogs/retired shards phải remove thủ công.
    - Bucket đã có số Shard mới, dữ liệu đã chia nhỏ, nhưng OSD vẫn báo lỗi ở các tên Object Shard cũ.
- **Các cách xử lý gợi ý:** 
    - kiểm tra changelog/bugfix cho phiên bản Ceph; nếu cần, áp patch/upgrade (lên phiên bản hỗ trợ dynamic reshard fixes) trong maintenance window.
    - Ép hệ thống quét lại metadata: `ceph osd pg deep-scrub <pg_id>` (cần map các bucket lớn đó với các bucket báo lỗi )
        - Nếu Object bị báo lỗi là Shard cũ (đã được thay thế), hãy xóa nó thủ công sau khi kiểm tra kỹ bằng listomapkeys thấy rỗng hoặc dữ liệu đã cũ.


### Bước 3: Kiểm tra và xác thực 
1. Sau reshard/trim/GC: `ceph health detail` và grep log để kiểm tra message đã biến mất.
2. Chạy `ceph osd pool stats` hoặc `ceph osd df` để xem I/O impact.
3. Kiểm tra RGW bucket stats, và reshard status: `radosgw-admin reshard status --bucket=<bucket>`.

### Tóm tắt các lệnh 

- Kiểm tra và check thông tin 
```bash
grep -i "Large omap object found" /var/log/ceph/ceph.log
rados -p <pool> listomapkeys <object> | wc -l
radosgw-admin metadata list --metadata-key bucket.instance
radosgw-admin bucket stats --bucket=<bucket>
ceph pg <pgid> query
ceph health detail
radosgw-admin sync status
radosgw-admin reshard list
```

- Các lệnh thực thi ( có ảnh hưởng cụm , khuyến nghị test lab hoặc backup trước)
```bash
# Manual immediate reshard (online)
radosgw-admin bucket reshard --bucket=<bucket> --num-shards=<N>
# or schedule and process
radosgw-admin reshard add --bucket=<bucket> --num-shards=<N>
radosgw-admin reshard process
# Trim bilog (multi-site/stale) — rất cẩn trọng
radosgw-admin bilog trim --bucket="<bucket-name>" --bucket-id="<bucket-id>"
# Trim usage (logs)
radosgw-admin usage trim --start-date=YYYY-MM-DD --end-date=YYYY-MM-DD
# Deep-scrub specific PG
ceph osd pg deep-scrub <pgid>
# Disable bucket sync (if needed, impacts replication)
radosgw-admin bucket sync disable --bucket=<bucket>
```