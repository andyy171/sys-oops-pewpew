# Tổng hợp command ceph thông dụng với 

## 1. Kiểm tra trạng thái

```bash
ceph -s               # Hiển thị tóm tắt nhanh trạng thái toàn bộ cluster (health, OSD, PG, IO)
ceph health detail    # Hiển thị chi tiết các cảnh báo và lỗi đang ảnh hưởng đến health cluster
ceph osd status       # Hiển thị trạng thái hoạt động, dung lượng và tải của từng OSD
ceph osd tree         # Hiển thị cấu trúc CRUSH tree (OSD → host → rack…)
ceph df               # Hiển thị dung lượng sử dụng của toàn cluster và theo từng pool (đã tính replica/EC)
rados df              # Hiển thị thống kê dung lượng và số object ở mức pool/object (logical data)
ceph pg stat          # Hiển thị tổng quan trạng thái Placement Group (PG) trong cluster
ceph auth list        # Liệt kê tất cả user/keyring và quyền (caps) trong cluster
ceph mon stat         # Hiển thị trạng thái quorum và số lượng monitor
ceph osd pool ls      # Liệt kê danh sách các pool hiện có trong cluster
ceph quorum_status    # Hiển thị chi tiết thông tin quorum của monitor (leader, thành viên quorum)
ceph -w               # Theo dõi log sự kiện và thay đổi trạng thái cluster theo thời gian thực
ceph features         # Hiển thị các tính năng (feature bits) mà client/daemon đang hỗ trợ
ceph versions         # Hiển thị phiên bản Ceph của từng loại daemon trong cluster
```
## 2. Quản lý Cluster 
```bash
ceph orch ls                                    # Liệt kê tất cả các dịch vụ đang chạy.
ceph orch status
ceph orch host ls
ceph orch ps                                    # Kiểm tra trạng thái các daemon (tiến trình) cụ thể trên các node.
ceph orch device ls                             # Liệt kê các ổ đĩa có sẵn trên các host để làm OSD.
ceph orch host add <hostname> <ip>              # Thêm một node mới vào cụm.
ceph orch host ls                               # Xem danh sách các máy chủ trong cụm.
ceph orch host rm <hostname>                    # Xóa host khỏi cụm.
ceph orch apply osd --all-available-devices
ceph orch apply mds <fs_name> --placement="2 <host1> <host2>"                      # Triển khai Metadata Server cho CephFS.
ceph orch apply rgw <realm> <zone> --placement="num_instances"                                              # Triển khai Rados Gateway.
ceph config dump
ceph config set <entity> <key> <value>
## ceph config set osd.12 debug_osd 5/5 - Tăng mức log để debug 
## ceph config set osd osd_max_backfills 1
## ceph config set mon mon_max_pg_per_osd 300
ceph report
ceph log
```


## 3. Làm việc với Pools và OSDs 
```bash
#======== OSD ============# 
ceph osd tree                                                               # Liệt kê các host, OSD của chúng, trạng thái hoạt động (up/down), trọng số OSD, và reweight cục bộ.
ceph osd df tree                                                            # Hiển thị cây sử dụng đĩa liên kết với cây CRUSH.
ceph osd stat                                                               # In ra bản tóm tắt của bản đồ OSD (OSD map).
ceph osd pool create <poolname> <pg_num>
ceph osd pool delete <poolname> <poolname> --yes-i-really-really-mean-it
ceph osd crush reweight osd.<id> <weight>
ceph osd deep-scrub osd.<id>
ceph tell osd.<id> version
ceph osd find osd.<id>                                                      # Hiển thị vị trí của một OSD cụ thể (tên host, cổng, và chi tiết CRUSH).
ceph osd map pool object                                                    # Định vị một đối tượng từ một pool. Hiển thị các nhóm vị trí chính và bản sao cho đối tượng đó.
ceph osd metadata <id>

ceph osd out <id>
ceph osd purge <id> --yes-i-really-mean-it
ceph tell osd.<id> flush_pg_stats
ceph osd blocked-by
ceph osd blacklist ls
ceph osd blacklist add <ip>
ceph daemon <daemon> config show


#======== POOL ============# 
ceph osd pool create <pool-name> <pg-number> <pgs-number>   # Tạo một pool nhân bản mới với số lượng nhóm vị trí (PG) nhất định.
ceph osd pool get <pool> all 
## ceph osd pool get rbd all
ceph osd pool ls detail                                     # Liệt kê các pool và chi tiết của các pool đó.
ceph osd pool set <parameter> <value>
## ceph osd pool set default.rgw.buckets.index recovery_priority 5
## ceph osd erasure-code-profile set Erasure-D3F2 crush-failure-domain=osd k=3 m=2 plugin=jerasure technique=reed_sol_van crush-device-class=hdd

ceph osd pool rename <oldname> <newname>
ceph osd reweight <id> <weight>
ceph osd reweight-by-utilization <percent>
ceph osd scrub osd.<id>
ceph osd test-reweight-by-utilization <percent>
ceph osd pool get <poolname> <key>
ceph osd set <flag> 
## ceph osd set noout
## ceph osd set norebalance

ceph osd pool set-quota <poolname> max_bytes <bytes>
ceph osd pool set-quota <poolname> max_objects <num>

ceph osd crush rule ls
ceph osd destroy <osd-id>
ceph osd perf
ceph osd crush rule create-replicated
#===========CRUSH MAP ================#
ceph osd crush tree
ceph osd crush add-bucket <name> <type>
ceph osd crush move <node_name> <type>=<parent_name>
ceph osd crush reweight osd.<id> <weight>

#================ Quota ==============#
# Multi-tenant environments: Giới hạn quota mỗi tenant

ceph osd pool set-quota tenant-a-pool max_bytes 10737418240  # 10GB
   ceph osd pool set-quota tenant-b-pool max_bytes 21474836480  # 20GB

# Test/dev pools: Tránh lấy hết storage
ceph osd pool set-quota dev-pool max_bytes 107374182400  # 100GB

# Archive pools: Limit growth 
ceph osd pool set-quota archive-pool max_bytes 10995116277760  # 10TB

# RGW buckets: Quota per user/bucket
## Set quota cho bucket trong RGW
   radosgw-admin quota set --quota-scope=bucket --bucket=mybucket --max-size=10737418240

# Monitor quota usage
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

#================Pool creation & configuration==============#
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
- Tạo Erasure-coded Pool

# Bước 1: Tạo erasure profile (nếu chưa có)**
## Xem profiles hiện có
ceph osd erasure-code-profile ls

## Tạo profile mới
ceph osd erasure-code-profile set my-ec-profile \
    k=4 \
    m=2 \
    crush-failure-domain=host \
    plugin=jerasure \
    technique=reed_sol_van

# Bước 2: Tạo pool với profile**
## Tạo EC pool
ceph osd pool create backup-pool 128 128 erasure my-ec-profile

## Enable application
ceph osd pool application enable backup-pool rgw

# Bước 3: Verify**
## Kiểm tra pool đã tạo
ceph osd pool ls detail | grep backup-pool

## Kiểm tra profile
ceph osd erasure-code-profile get my-ec-profile

```

## 4. Quản lý Monitor
```bash
ceph mon dump
ceph mon getmap -o monmap
ceph mon add <mon-id> <ip:port>
ceph mon remove <mon-id>
```

## 5. Làm việc với Nhóm Vị trí (PGs)
```bash
ceph pg pg-id query
ceph pg 1.c query
ceph pg pg-id list_missing
ceph pg 1.c list_missing
ceph pg dump [--format]
ceph pg dump
ceph pg dump_stuck inactive unclean stale undersized degraded
ceph pg dump_stuck unclean
ceph pg scrub pg-id
Khởi tạo quy trình scrub trên nội dung của các nhóm vị trí.
ceph pg scrub 3.0
ceph pg deep-scrub pg-id
ceph pg deep-scrub 3.0
ceph pg repair {pg-id}
ceph pg repair 3.0
ceph pg force-recovery <pg-id>
ceph pg deep-scrub <pg-id>
ceph pg ls <state>
instructing pg 3.0 on osd.1 to repair
```
## 6. Tương tác với Daemons 
```bash
ceph daemon <osd.id> dump_ops_in_flight
ceph daemon osd.0 dump_ops_in_flight
ceph daemon <daemon-name> help
## ceph daemon osd.0 help
ceph daemon <daemon-name> mon_status
ceph daemon mon.ceph1 mon_status
ceph daemon osd.<id> status
ceph daemon osd.<id> status
ceph daemon <daemon-name> perf dump
ceph daemon client.radosgw.primary perf dump
ceph orch redeploy
## ceph orch redeploy mds --dry-run xem thử kết quả trước khi chạy
```

## 7. Xác thực và Ủy quyền 
```bash
ceph auth list
ceph auth get-or-create client.rbd mon
'allow r' osd 'allow rw pool=rbd'
ceph auth delete
ceph auth caps
ceph auth get-key client.<id>
ceph auth add client.<id> <caps>
ceph auth del client.<id>
ceph auth caps client.<id> <caps>
ceph auth import
ceph auth get-or-create <entity>
```
## 8. Làm việc với Object
```bash
rados lspools                                                 # Liệt kê các object pool trong cluster
rados df                                                      # Hiển thị thống kê sử dụng dung lượng và object toàn hệ thống và theo pool
rados list-inconsistent-pg <pool>                             # Liệt kê các PG không nhất quán trong pool chỉ định
rados list-inconsistent-obj <pgid> [--format=json-pretty]     # Liệt kê object không nhất quán trong PG chỉ định
rados list-inconsistent-snapset <pgid>                        # Liệt kê snapset không nhất quán trong PG chỉ định

rados put <name> <infile> [--offset <offset>]                 # Ghi object từ infile với offset (default: 0)
##Lưu ý: Tạo object đơn lẻ kích thước bằng infile; khuyến nghị dùng RGW/CephFS/RBD cho objects lớn.
## rados -p foo put myobject blah.txt
rados -p pool ls
rados get <name> <outfile>                                    # Đọc object và ghi vào outfile
## rados -p foo get myobject blah.txt.old -s mysnap
rados -p pool rm object
rados -p pool listwatchers object
rados bench seconds mode [-b object-size] 
## rados bench -p rbd 120 write

rados get <name> <outfile> [-p <pool>] [-N <namespace>] [--object-locator <locator>] [-s <snap>] [--striper]                    # Đọc object và ghi vào outfile từ pool
rados put <name> <infile> [--offset <offset>] [-p <pool>] [-N <namespace>] [--object-locator <locator>] [--striper]             # Ghi object từ infile vào pool với offset tùy chọn
rados append <name> <infile> [-p <pool>] [-N <namespace>] [--object-locator <locator>] [--striper]                              # Thêm nội dung infile vào object hiện có
rados rm [--force-full] <name> ... [-p <pool>] [-N <namespace>] [--object-locator <locator>] [--striper]                        # Xóa object(s), force-full để xóa dù cluster đầy
rados listwatchers <name> [-p <pool>] [-N <namespace>] [--object-locator <locator>]                                             # Liệt kê watchers của object
rados ls <outfile> [-p <pool>] [--pgid <pgid>] [--all] [--default] [--striper]                                                  # Liệt kê object trong pool và ghi vào outfile hoặc stdout
rados lssnap [-p <pool>]                                                                                                        # Liệt kê snapshots của pool
rados mksnap <snap-name> [-p <pool>]                                                                                            # Tạo snapshot cho pool
rados rmsnap <snap-name> [-p <pool>]                                                                                            # Xóa snapshot của pool
rados bench <seconds> <mode> [-b <objsize>] [-t <threads>] [--no-cleanup] [--run-name <label>] [--show-time] [--no-verify] [--write-object] [--write-omap] [--write-xattr]                                                                                                                 # Benchmark IO trong seconds với mode (write/seq/rand)
rados cleanup [--run-name <run_name>] [--prefix <prefix>]                                                                       # Dọn dẹp object sau benchmark
rados listxattr <name> [-p <pool>] [-N <namespace>] [--object-locator <locator>] [--striper]                                    # Liệt kê extended attributes của object
rados getxattr <name> <attr> [-p <pool>] [-N <namespace>] [--object-locator <locator>] [--striper]                              # Lấy giá trị extended attribute
rados setxattr <name> <attr> <value> [-p <pool>] [-N <namespace>] [--object-locator <locator>] [--striper]                      # Đặt giá trị extended attribute
rados rmxattr <name> <attr> [-p <pool>] [-N <namespace>] [--object-locator <locator>] [--striper]                               # Xóa extended attribute
rados stat <name> [-p <pool>] [-N <namespace>] [--object-locator <locator>] [--striper]                                         # Lấy thông tin stat (mtime, size) của object
rados stat2 <name> [-p <pool>] [-N <namespace>] [--object-locator <locator>] [--striper]                                        # Lấy stat với thời gian chính xác cao
rados listomapkeys <name> [-p <pool>] [-N <namespace>] [--object-locator <locator>]                                             # Liệt kê keys trong object map
rados listomapvals <name> [-p <pool>] [-N <namespace>] [--object-locator <locator>]                                             # Liệt kê key/value pairs trong object map (hex)
rados getomapval [--omap-key-file <file>] <name> <key> [<out-file>] [-p <pool>] [-N <namespace>] [--object-locator <locator>]   # Lấy giá trị hex của key trong object map
rados setomapval [--omap-key-file <file>] <name> <key> [<value>] [-p <pool>] [-N <namespace>] [--object-locator <locator>]      # Đặt giá trị key trong object map
rados rmomapkey [--omap-key-file <file>] <name> <key> [-p <pool>] [-N <namespace>] [--object-locator <locator>]                 # Xóa key từ object map
rados getomapheader <name> [-p <pool>] [-N <namespace>] [--object-locator <locator>]                                            # Lấy hex giá trị object map header
rados setomapheader <name> <value> [-p <pool>] [-N <namespace>] [--object-locator <locator>]                                    # Đặt object map header
rados export <filename> [-p <pool>]                                                                                             # Serialize pool contents ra file hoặc stdout
rados import [--dry-run] [--no-overwrite] <filename | -> [-p <pool>] [--target-pool <pool>]                                     # Load pool contents từ file hoặc stdin
```

## 9. Làm việc với Block 
```bash
rbd create <pool>/<image> --size <size>
rbd ls <pool>
rbd info <pool>/<image>
rbd rm <pool>/<image>
rbd map <pool>/<image>
rbd unmap <pool>/<image>
rbd resize <pool>/<image> --size <size>
rbd snap create <pool>/<image>@<snap>
```


## 10. CephFS
```bash
ceph mds stat
ceph fs ls
ceph fs new <fs_name> <metadata_pool> <data_pool>
```
## 11. ceph device
```bash

```

## 12. ceph-volume

```bash

ceph-volume lvm list
ceph-volume lvm prepare --data /dev/sdX
ceph-volume lvm activate <osd_id> <osd_fsid>
ceph-volume lvm create --data /dev/sdX
ceph-volume lvm zap /dev/sdX

```

