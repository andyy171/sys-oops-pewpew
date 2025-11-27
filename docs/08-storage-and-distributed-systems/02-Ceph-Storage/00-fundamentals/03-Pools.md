
- Pool là phân vùng logic để lưu trữ objects trong Ceph cluster. Bạn có thể hiểu Pool giống như một "container" hay "bucket" lớn chứa dữ liệu.

- **Tại sao cần Pools?**
    + **Tách biệt dữ liệu:** Mỗi pool có thể có cấu hình riêng (replication, performance)
    + **Quản lý dễ dàng:** Phân chia workload khác nhau vào các pools khác nhau
    + **Bảo mật:** Có thể set quyền truy cập khác nhau cho từng pool
    + **Linh hoạt:** Mỗi pool có thể dùng storage strategy khác nhau

## Cách pool hoạt động 
```
                Client Application
                       ↓
                Pool (logical partition)
                       ↓
                Placement Groups (PGs)
                       ↓
                OSDs (physical storage)
```
- Khi bạn lưu data:
    + Data được chia thành objects
    + Objects được gán vào một Pool cụ thể
    + Pool phân phối objects qua các PGs
    + PGs được map tới các OSDs theo CRUSH algorithm

## Các loại pools 
Có 2 loại pool chính trong Ceph, mỗi loại phù hợp cho use case khác nhau.

#### Replicated Pools
**Cách hoạt động:** Tạo nhiều bản copy giống hệt nhau của mỗi object.

**Ví dụ minh họa:**
```
Object gốc: 1GB
Size = 3 (3 replicas)
→ Tổng dung lượng dùng: 3GB (lưu 3 bản copy)
```

**Ưu điểm:**

✅ Hiệu suất cao (đọc/ghi nhanh)
✅ Hỗ trợ đầy đủ operations (partial write, omap, etc.)
✅ Đơn giản, dễ hiểu và quản lý
✅ Recovery nhanh khi có lỗi

**Nhược điểm:**

❌ Tốn storage (overhead 200-300%)
❌ Đắt tiền hơn về mặt storage cost

**Khi nào dùng Replicated:**
```
    - Database (MySQL, PostgreSQL)
    - VM images (RBD)
    - Workload cần low latency
    - Hot data (được truy cập thường xuyên)
    - Metadata pools (CephFS metadata, RGW index)
```

**Ví dụ thực tế:**
```bash
## Tạo replicated pool với 3 copies
ceph osd pool create vm-images 128 128 replicated
ceph osd pool set vm-images size 3
ceph osd pool set vm-images min_size 2
```


#### Erasure-coded Pools
**Cách hoạt động:** Chia data thành chunks (k data + m coding), giống RAID 5/6.

**Ví dụ minh họa:**
```
Object gốc: 1GB
Profile: k=4, m=2 (4 data chunks + 2 coding chunks)
→ Mỗi chunk: 256MB
→ Tổng dung lượng dùng: 1.5GB (6 chunks × 256MB)
→ Overhead: 50% (thay vì 200% của replicated)
```

- **Công thức:**

    + Tổng chunks: k + m
    + Overhead: (k + m) / k
    + Chịu lỗi: Có thể mất tối đa m chunks

Các profile phổ biến:

![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/pool-ec-profiles.png)

**Ưu điểm:**

✅ Tiết kiệm storage (overhead thấp hơn)
✅ Phù hợp cold storage
✅ Có thể chịu được nhiều OSD fail (tùy m)

**Nhược điểm:**

❌ Performance thấp hơn (CPU overhead cao)
❌ Không hỗ trợ một số operations (partial write, omap)
❌ Recovery chậm hơn
❌ Phức tạp hơn để troubleshoot

**Khi nào dùng Erasure-coded:**
```
    - Cold storage (backup, archive)
    - Object storage (S3/Swift via RGW)
    - Large files ít thay đổi (images, videos, genomics data)
    - Data pools cho RBD/CephFS (chú ý: metadata phải dùng replicated)
```

> Erasure-coded pools không hỗ trợ omap operations, vì vậy không thể dùng cho metadata pools của RGW hoặc RBD. Chỉ nên dùng cho data pools.
## Pool creation & configuration
- Tạo Replicated Pool
    + Syntax cơ bản:
```bash
ceph osd pool create <pool-name> <pg_num> [pgp_num] [replicated]
```
**Ví dụ thực tế:**
```bash
## Tạo pool cho VM images
ceph osd pool create vm-images 128 128 replicated

## Set replication size
ceph osd pool set vm-images size 3
ceph osd pool set vm-images min_size 2

## Enable application tag
ceph osd pool application enable vm-images rbd

## Initialize pool cho RBD
rbd pool init vm-images
```
- Tạo Erasure-coded Pool

**Bước 1: Tạo erasure profile (nếu chưa có)**
```bash
## Xem profiles hiện có
ceph osd erasure-code-profile ls

## Tạo profile mới
ceph osd erasure-code-profile set my-ec-profile \
    k=4 \
    m=2 \
    crush-failure-domain=host \
    plugin=jerasure \
    technique=reed_sol_van
```

**Bước 2: Tạo pool với profile**
```bash
## Tạo EC pool
ceph osd pool create backup-pool 128 128 erasure my-ec-profile

## Enable application
ceph osd pool application enable backup-pool rgw
```

**Bước 3: Verify**
```bash
## Kiểm tra pool đã tạo
ceph osd pool ls detail | grep backup-pool

## Kiểm tra profile
ceph osd erasure-code-profile get my-ec-profile
```


## Pool-level settings (size, min_size, pg_num)
```
size - Số lượng replicas
```
=> Tổng số copies của mỗi object (bao gồm primary copy).

- Giá trị phổ biến:

    + `size = 2`: `1 primary` + `1 replica` (⚠️ rủi ro cao)
    + `size = 3`: `1 primary` + `2 replicas` (✅ recommend cho production)
    + `size = 4`: `1 primary` + `3 replicas` (dùng cho data critical)

```bash
# Xem size hiện tại
ceph osd pool get vm-images size

# Set size
ceph osd pool set vm-images size 3

# Verify
ceph osd pool ls detail | grep vm-images
```
## Pool quotas
- Quota giúp giới hạn dung lượng hoặc số objects mà một pool có thể chứa, tránh pool nào đó "ăn hết" storage.
- Hai loại quota

    + `max_bytes`: Giới hạn tổng dung lượng (bytes)
    + `max_objects`: Giới hạn số lượng objects

**Set quota:**
```bash
ceph osd pool set-quota <pool-name> [max_objects <obj-count>] [max_bytes <bytes>]

## Ví dụ 
# Giới hạn pool chỉ được dùng 1TB
ceph osd pool set-quota vm-images max_bytes 1099511627776

# Hoặc dùng đơn vị dễ đọc (nếu client hỗ trợ)
# 1TB = 1099511627776 bytes
# 1GB = 1073741824 bytes

# Giới hạn 1 triệu objects
ceph osd pool set-quota vm-images max_objects 1000000

# Set cả hai
ceph osd pool set-quota vm-images max_bytes 1099511627776 max_objects 500000

```

**Xem quota:**
```bash
# Xem quota của pool
ceph osd pool get-quota vm-images

# Output:
# quotas for pool 'vm-images':
#   max objects: 500000 objects
#   max bytes  : 1 TiB

# Xem quota trong context với usage
ceph df detail
```

Sample output 
```
POOLS:
POOL         ID  STORED   OBJECTS  USED     %USED  MAX AVAIL  QUOTA OBJECTS  QUOTA BYTES
vm-images     2   450 GiB   120000  900 GiB  45.00      1 TiB       500000        1 TiB
```


**Remove quota:**
```bash
# Remove quota bằng cách set về 0
ceph osd pool set-quota vm-images max_bytes 0
ceph osd pool set-quota vm-images max_objects 0
```


>- Lưu ý :
>    + Khi pool đạt quota, write operations sẽ bị fail
>    + Quota không "hard block" ngay lập tức, có thể vượt một chút trong khi replication
>    + Quota được tính trên "raw" storage, không phải logical storage
>    + Với replication size=3, 1GB data sẽ tính là 3GB quota


### Quota usecase 
1. Multi-tenant environments: Giới hạn mỗi tenant

```bash   
ceph osd pool set-quota tenant-a-pool max_bytes 10737418240  # 10GB
   ceph osd pool set-quota tenant-b-pool max_bytes 21474836480  # 20GB
```
2. Test/dev pools: Tránh lấy hết storage

```bash   
ceph osd pool set-quota dev-pool max_bytes 107374182400  # 100GB
```

3. Archive pools: Limit growth

```bash   
ceph osd pool set-quota archive-pool max_bytes 10995116277760  # 10TB
```

4. RGW buckets: Quota per user/bucket

```bash   
# Set quota cho bucket trong RGW
   radosgw-admin quota set --quota-scope=bucket --bucket=mybucket --max-size=10737418240
```

5. Monitor quota usage
```bash
# Watch quota usage realtime
watch -n 5 "ceph df detail | grep -A 1 vm-images"

# Script để alert khi gần đầy
#!/bin/bash
POOL="vm-images"
THRESHOLD=90  # 90%

USAGE=$(ceph df detail -f json | jq -r ".pools[] | select(.name==\"$POOL\") | .stats.percent_used")
if (( $(echo "$USAGE > $THRESHOLD" | bc -l) )); then
    echo "WARNING: Pool $POOL is ${USAGE}% full"
    # Send alert
fi
```
## Application tags
- Application tag là label để đánh dấu pool được dùng cho service nào (CephFS, RBD, RGW). Từ Ceph Luminous trở đi, mỗi pool bắt buộc phải có application tag trước khi sử dụng.

- Tại sao cần application tags?

    + Security: Prevent unauthorized applications from using pool
    + Management: Dashboard và tools biết pool dùng cho gì
    + Automation: Tự động áp dụng settings phù hợp
    + Monitoring: Dễ dàng track pool theo application

### Enable application tag
```bash
ceph osd pool application enable <pool-name> <app-name>

##Ví dụ thực tế:
## RBD pool
ceph osd pool application enable vm-images rbd

## CephFS pools
ceph osd pool application enable cephfs_data cephfs
ceph osd pool application enable cephfs_metadata cephfs

## RGW pools
ceph osd pool application enable .rgw.root rgw
ceph osd pool application enable default.rgw.buckets.data rgw
```
### Kiểm tra application tags
```bash
# List all pools with their applications
ceph osd pool ls detail | grep application

# Get application của một pool cụ thể
ceph osd pool application get vm-images

# Output:
# {
#     "rbd": {}
# }
```

### Health warning nếu thiếu tag
Nếu pool chưa có application tag, cluster sẽ hiện HEALTH_WARN:
```bash
$ ceph health
HEALTH_WARN application not enabled on 1 pool(s)

$ ceph health detail
HEALTH_WARN application not enabled on 1 pool(s)
POOL_APP_NOT_ENABLED application not enabled on 1 pool(s)
    application not enabled on pool 'my-pool'
    use 'ceph osd pool application enable <pool-name> <app-name>', 
    where <app-name> is 'cephfs', 'rbd', 'rgw', or freeform for custom applications.
```

### Fix warning
```bash
# Enable application tag
ceph osd pool application enable my-pool rbd

# Check health
ceph health
# HEALTH_OK
```


### Custom application names
Bạn có thể dùng custom name cho applications khác:
```bash
# Application tự định nghĩa
ceph osd pool application enable backup-pool backup
ceph osd pool application enable log-pool logging
ceph osd pool application enable metrics-pool metrics
```

### Application metadata (Advanced)
Có thể set metadata cho application:
```bash
# Set metadata key-value
ceph osd pool application set <pool> <app> <key> <value>

# Ví dụ
ceph osd pool application set vm-images rbd department engineering
ceph osd pool application set vm-images rbd owner john@company.com

# Get metadata
ceph osd pool application get vm-images rbd

# Output:
# {
#     "department": "engineering",
#     "owner": "john@company.com"
# }
```

#### Disable application
```bash
# Remove application tag (cẩn thận!)
ceph osd pool application disable <pool> <app> --yes-i-really-mean-it

# Ví dụ
ceph osd pool application disable old-pool rbd --yes-i-really-mean-it
```

## Best practices

1. Luôn enable tag ngay sau khi tạo pool:

```bash   ceph osd pool create mypool 128
   ceph osd pool application enable mypool rbd  # Ngay lập tức
```
2. RBD pools cần initialize thêm:

```bash   ceph osd pool application enable rbd-pool rbd
   rbd pool init rbd-pool  # Initialize RBD
```
3. Multi-application trên cùng pool (không recommend):

```bash   # Có thể nhưng không nên
   ceph osd pool application enable shared-pool rbd
   ceph osd pool application enable shared-pool rgw

```
4. Workflow tạo pool hoàn chỉnh:

```bash   # Tạo pool
   ceph osd pool create mypool 128 128 replicated
   
   # Config basics
   ceph osd pool set mypool size 3
   ceph osd pool set mypool min_size 2
   
   # Enable application
   ceph osd pool application enable mypool rbd
   
   # Initialize cho RBD
   rbd pool init mypool
   
   # Verify
   ceph osd pool ls detail | grep mypool
```
