# Mục lục 




# Tổng quan 





# Health monitoring
Các lệnh này được sử dụng rộng rãi và không thay đổi:

Kiểm tra sức khỏe cụm:

`ceph health` (hoặc ceph health detail): Xem trạng thái sức khỏe tóm tắt và chi tiết (ví dụ: HEALTH_WARN, HEALTH_OK).

Tổng quan cụm:

`ceph -s` (hoặc `ceph status`): Xem tổng quan nhanh về MON, MGR, OSD, Pool, và PG.

Giám sát dung lượng:

`ceph df`: Xem dung lượng toàn cục (GLOBAL) và chi tiết theo từng Pool (POOLS).

Xem trạng thái Monitor:

`ceph mon stat`: Xem trạng thái các Monitor, số lượng quorum.

`ceph quorum_status`: Xem chi tiết các Monitor đang tham gia quorum.


# Service management (start/stop/restart daemons)



# Quản lý Placement Group (PG)

[Cơ bản về PG](/08-storage-and-distributed-systems/02-Ceph-Storage/01-core-service/OSD.md#pg-placement-group)

1. Thiết lập/Điều chỉnh PG:
```bash
ceph osd pool set [pool-name] pg_num [số_lượng]: Vẫn dùng để tăng số lượng PG.

ceph osd pool set [pool-name] pgp_num [số_lượng]: Bắt buộc phải khớp với pg_num khi thay đổi.
```

2. Xem thông tin PG:
```bash
ceph osd pool get [pool-name] pg_num #Lấy số lượng PG của pool.

ceph pg dump #Xuất thông tin chi tiết của tất cả PG.

ceph pg dump_stuck [trạng thái] #Lấy danh sách các PG bị kẹt ở các trạng thái như inactive, unclean, stale, rất quan trọng cho việc gỡ lỗi.
```

## PG scrubbing schedule

## PG repair commands

## Manual PG manipulation

## PG states troubleshooting


# Pool Management
## Create/delete pools

## Set pool size & min_size

## Pool quotas (max objects, max bytes)

## Application enable/disable

## Pool statistics



# OSD Management
## Adding/removing OSDs


## OSD replacement workflow


## Setting OSD weights


## OSD reweighting


## Marking OSDs out/in


## Purging OSDs


# CRUSH Map Management
- Backup CRUSH map trước khi thực hiện bất kỳ thay đổi :
```bash
ceph osd getcrushmap -o /backup/crushmap-$(date +%Y%m%d).bin
crushtool -d /backup/crushmap-$(date +%Y%m%d).bin -o /backup/crushmap-$(date +%Y%m%d).txt
```

- Test CRUSH changes trước khi thực hiện thay đổi :
```bash
# Compile test crushmap
crushtool -c /tmp/crushmap_new.txt -o /tmp/crushmap_new.bin

# Test với dry-run
crushtool -i /tmp/crushmap_new.bin --test --show-mappings \
    --num-rep 3 --rule 0 > /tmp/crush_test_output.txt

# Analyze: Số PGs mỗi OSD nhận được có cân bằng không?
# Failure domain có được tôn trọng không?
```

- Khi chỉnh sửa weight của OSD , hãy chỉnh sửa từ từ 
```bash
# Thay vì jump từ 0 → 3.0, increase gradually
ceph osd crush reweight osd.X 1.0
# Wait for rebalancing...
ceph osd crush reweight osd.X 2.0  
# Wait...
ceph osd crush reweight osd.X 3.0
```

- Giám sát trong khi rebalancing : 
```bash
watch -n 5 'ceph -s'
ceph osd df tree
ceph pg dump pgs_brief | grep -E 'active\+clean'

# Đặt thresholds để giới hạn ảnh hương lên clients

ceph tell 'osd.*' injectargs '--osd-max-backfills 1'
ceph tell 'osd.*' injectargs '--osd-recovery-max-active 1'
ceph tell 'osd.*' injectargs '--osd-recovery-op-priority 1'
```

# Pool Management 
## Cơ bản
 1. Liệt kê và xem thông tin
```bash
# List pools (simple)
ceph osd lspools

# List với detail
ceph osd pool ls detail

# Pool statistics
ceph df

# Pool statistics với detail
ceph df detail

# Specific pool stats
ceph osd pool stats <pool-name>
```

2. Rename pool
```bash
# Rename pool
ceph osd pool rename <old-name> <new-name>

# Ví dụ
ceph osd pool rename old-vm-pool vm-images
```

3. Snapshot pool
> ⚠️ Không recommend cho RBD pools (dùng RBD snapshots thay thế).
```bash
# Tạo snapshot
ceph osd pool mksnap <pool-name> <snap-name>

# List snapshots
rados -p <pool-name> lssnap

# Remove snapshot
ceph osd pool rmsnap <pool-name> <snap-name>
```

4. Delete pool
> ⚠️ NGUY HIỂM: Xóa pool sẽ mất tất cả data!
> Mặc định, Ceph không cho phép xóa pool để tránh tai nạn.

**Bước 1: Enable pool deletion (trên mon nodes)**
```bash
# Temporary enable (sẽ mất sau khi restart)
ceph tell mon.* injectargs '--mon-allow-pool-delete=true'

# Hoặc persistent (thêm vào ceph.conf)
# [mon]
# mon allow pool delete = true

# Restart monitors để apply
systemctl restart ceph-mon.target
```
**Bước 2: Xóa pool**
```bash
# Phải gõ tên pool 2 lần để confirm
ceph osd pool delete <pool-name> <pool-name> --yes-i-really-really-mean-it

# Ví dụ
ceph osd pool delete old-pool old-pool --yes-i-really-really-mean-it

# Disable pool deletion sau khi xong để an toàn
ceph tell mon.* injectargs '--mon-allow-pool-delete=false'

```

5. Copy pool (Backup)
```bash
# Copy tất cả objects từ pool này sang pool khác
rados cppool <source-pool> <dest-pool>

# Ví dụ: Backup vm-images pool
ceph osd pool create vm-images-backup 128
rados cppool vm-images vm-images-backup

# ⚠️ Lưu ý: Command này có thể mất nhiều thời gian với pool lớn
```

6. Export/Import pool data
```bash
# Export pool data
rados export -p <pool-name> <output-file>

# Ví dụ
rados export -p vm-images /backup/vm-images.export

# Import vào pool mới
ceph osd pool create vm-images-restored 128
rados import -p vm-images-restored /backup/vm-images.export

```

### Các lệnh nhanh hữu dụng 
```bash
# Show all pools with size and usage
ceph df | awk 'NR>1 {print $1, $3, $7}'

# Count objects per pool
for pool in $(ceph osd lspools | awk '{print $2}'); do 
    echo "$pool: $(rados -p $pool ls | wc -l) objects"
done

# Find pools without application tag
ceph osd pool ls detail | grep -B1 "application:" | grep "pool " | grep -v "application"

# Get total raw capacity
ceph df | grep "TOTAL" | awk '{print $2}'

# Quick pool summary
ceph osd pool ls detail | grep -E "pool |size|pg_num|application"

# Check which pools are using most space
ceph df detail | grep "USED" -A 100 | sort -k3 -hr | head -10
```

### Pre-production testing
```bash
# 1. Write test
rados -p test-pool put testobj /tmp/testfile
echo "Write: OK"

# 2. Read test
rados -p test-pool get testobj /tmp/testfile.out
diff /tmp/testfile /tmp/testfile.out
echo "Read: OK"

# 3. Delete test
rados -p test-pool rm testobj
echo "Delete: OK"

# 4. Check pool health
ceph osd pool stats test-pool
echo "Pool health: OK"

# 5. Check PG distribution
ceph pg dump | grep "^[0-9]" | grep test-pool | awk '{print $15}' | sort | uniq -c
echo "PG distribution: OK"

# 6. Performance test (optional)
rados bench -p test-pool 30 write --no-cleanup
rados bench -p test-pool 30 seq
rados bench -p test-pool 30 rand
echo "Performance: OK"

# Cleanup
rados -p test-pool cleanup
```

## Pool creation planning
1. Checklist : 
```
    - Pool type: Replicated hay EC?
    - Size: 3 cho production
    - PG number: Tính toán dựa trên số OSDs
    - CRUSH rule: Host, rack, hay datacenter failure domain?
    - Application: RBD, CephFS, hay RGW?
    - Quota: Có cần giới hạn không?
 ```
**Template mẫu :**
```bash
# Planning document
Pool name: vm-images
Type: Replicated
Size: 3
Min_size: 2
PG_num: 256 (cluster có 20 OSDs)
Application: RBD
Quota: 5TB
Purpose: Store VM disk images
```
2. Recommend naming pattern:
```
<application>-<purpose>-<env>

Ví dụ:
- rbd-vms-prod
- rbd-vms-dev
- cephfs-home-prod
- rgw-backup-prod
- ec-archive-prod

```
Tránh việc sử dụng tên quá ngắn (pool1, data), không mô tả (test, temp) hay sử dụng ký tự đặc biệt

3. Workflow tạo pool
```bash
#!/bin/bash
# create-pool.sh

POOL_NAME="rbd-vms-prod"
PG_NUM=256
POOL_SIZE=3
MIN_SIZE=2
APP="rbd"

# Create pool
echo "Creating pool ${POOL_NAME}..."
ceph osd pool create ${POOL_NAME} ${PG_NUM} ${PG_NUM} replicated

# Set size
echo "Setting replication size to ${POOL_SIZE}..."
ceph osd pool set ${POOL_NAME} size ${POOL_SIZE}
ceph osd pool set ${POOL_NAME} min_size ${MIN_SIZE}

# Enable application
echo "Enabling ${APP} application..."
ceph osd pool application enable ${POOL_NAME} ${APP}

# Initialize RBD
if [ "${APP}" = "rbd" ]; then
    echo "Initializing RBD pool..."
    rbd pool init ${POOL_NAME}
fi

# Verify
echo "Verifying pool creation..."
ceph osd pool ls detail | grep ${POOL_NAME}

echo "Pool ${POOL_NAME} created successfully!"
```

```bash
chmod +x create-pool.sh
./create-pool.sh
```
4. Daily monitoring
```bash
# Quick health check
ceph -s

# Pool usage
ceph df

# Detailed pool stats
ceph osd pool stats

# PG status
ceph pg stat

# Watch realtime
watch -n 5 "ceph df && echo && ceph -s"

```

5. Setup alerts:

```bash
#!/bin/bash
# pool-alert.sh - Check pool usage

THRESHOLD=80  # Alert at 80%

ceph df -f json | jq -r '.pools[] | "\(.name) \(.stats.percent_used)"' | while read pool usage; do
    usage_int=${usage%.*}  # Remove decimal
    if [ $usage_int -gt $THRESHOLD ]; then
        echo "ALERT: Pool $pool is ${usage}% full"
        # Send email/Slack/etc
    fi
done

```
```bash
# Add to crontab
# Check every hour
0 * * * * /usr/local/bin/pool-alert.sh
```

## Common mistakes
❌ Mistake 1: Tạo pool với PG quá ít hoặc quá nhiều
```bash
# Sai: PG quá ít
ceph osd pool create mypool 8  # Too few!

# Đúng: Tính toán theo công thức
# 10 OSDs × 100 PGs per OSD ÷ 3 pools = ~333 → 512 PGs
ceph osd pool create mypool 512
```

❌ Mistake 2: Quên set application tag
```bash
# Sai: Tạo pool nhưng không enable app
ceph osd pool create mypool 128
# → HEALTH_WARN!

# Đúng: Enable ngay
ceph osd pool create mypool 128
ceph osd pool application enable mypool rbd
```

❌ Mistake 3: Size = 2 cho production
```bash
# Sai: Size 2 (không an toàn)
ceph osd pool set prod-pool size 2

# Đúng: Size 3 cho production
ceph osd pool set prod-pool size 3
ceph osd pool set prod-pool min_size 2
```

❌ Mistake 4: Không set quota cho dev/test
```bash
# Sai: Dev pool không quota → có thể lấy hết storage
ceph osd pool create dev-pool 128

# Đúng: Limit dev pool
ceph osd pool create dev-pool 128
ceph osd pool set-quota dev-pool max_bytes 107374182400  # 100GB
```

❌ Mistake 5: Xóa pool mà không backup
```bash
# Sai: Xóa luôn
ceph osd pool delete important-pool important-pool --yes-i-really-really-mean-it
# → Data mất vĩnh viễn!

# Đúng: Export/backup trước
rados export -p important-pool /backup/important-pool.backup
# Verify backup
ls -lh /backup/important-pool.backup
# Rồi mới xóa
```
## Troubleshooting 
```bash
# Check health
ceph health detail

#  Check PG status
ceph pg stat

# List problematic PGs
ceph pg dump | grep -v 'active+clean'

# Query specific PG
ceph pg <pg-id> query

# Common fixes
ceph pg repair <pg-id>
ceph osd pool application enable <pool> <app>

# Check which pool is full
ceph df detail

# Options:
# 1. Add more OSDs
# 2. Delete old data
# 3. Increase quota
ceph osd pool set-quota <pool> max_bytes <new-limit>

# 4. Emergency: Increase full ratio (temporary)
ceph osd set-full-ratio 0.90
ceph osd set-nearfull-ratio 0.85

# Check slow ops
ceph health detail | grep slow

# Find which pool/PG
ceph pg dump | grep slow

# Check OSD performance
ceph osd perf

# Check if rebalancing
ceph -s | grep rebalancing

```

## Chiến lược Backup 
Common script 
```bash
#!/bin/bash
# backup-pools.sh

BACKUP_DIR="/backup/ceph-pools"
DATE=$(date +%Y%m%d)

# List của pools cần backup
POOLS="rbd-vms-prod cephfs-metadata"

for pool in $POOLS; do
    echo "Backing up pool: $pool"
    
    # Export pool
    rados export -p $pool ${BACKUP_DIR}/${pool}-${DATE}.export
    
    # Compress
    gzip ${BACKUP_DIR}/${pool}-${DATE}.export
    
    # Verify
    if [ -f ${BACKUP_DIR}/${pool}-${DATE}.export.gz ]; then
        echo "✓ Pool $pool backed up successfully"
    else
        echo "✗ Backup failed for pool $pool"
    fi
done

# Cleanup old backups (keep 7 days)
find ${BACKUP_DIR} -name "*.export.gz" -mtime +7 -delete

echo "Backup completed!"
```