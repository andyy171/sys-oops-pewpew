---
Hướng dẫn các thao tác tìm kiếm và sửa lỗi 

---
# 
- Xem log "thời gian thực":
`tail -f /var/log/ceph/ceph.log` hoặc `tail -f /var/log/ceph/ceph-osd-3.log`

- Tìm khóa/chuỗi quan trọng:
`grep -i "error\|failed\|warning" /var/log/ceph/ceph.log`

# Common issues & solutions:

## Slow requests


## PGs stuck inactive/unclean


## OSD flapping


## MON clock skew


## Full OSDs


# Log analysis


# Debug commands



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
