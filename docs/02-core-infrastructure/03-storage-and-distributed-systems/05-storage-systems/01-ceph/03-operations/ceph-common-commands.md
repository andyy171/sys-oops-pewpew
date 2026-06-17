# Tổng hợp câu lệnh ceph thông dụng với 
- Quy ước mức độ ảnh hưởng của lệnh
    - `R`	 : Chỉ đọc trạng thái, không đổi cluster
    - `S1` : Đổi nhẹ, thường an toàn nếu hiểu rõ tác dụng, có thể đảo ngược
    - `S2` : Ảnh hưởng dịch vụ hoặc hành vi recovery/backfill, cần cân nhắc
    - `D`	 : Phá hủy, xóa dữ liệu hoặc khó đảo ngược

- Lưu ý : 
    - `ceph daemon` thường dùng khi bạn đang đứng đúng node chứa daemon và có quyền truy cập admin socket của daemon đó.
    - `ceph tell` gửi lệnh tới daemon qua cluster control plane, thường tiện hơn khi thao tác từ host quản trị.
    - Trước mọi lệnh xóa OSD, luôn kiểm tra `ceph osd safe-to-destroy` trước. `ceph osd purge` là lệnh mạnh, vì nó kết hợp cả destroy, rm và crush remove.
## Nguyên tắc vận hành 
- Hai nguyên tắc vận hành nên chèn vào đầu file

- Nguyên tắc 1: Trước mọi lệnh thay đổi dữ liệu hoặc topology, luôn chạy một lệnh đọc trạng thái tiền đề trước, ví dụ:

    - ceph -s
    - ceph health detail
    - ceph osd tree
    - ceph osd safe-to-destroy
    - ceph pg stat

Làm vậy giúp bạn tránh chạy lệnh đúng cú pháp nhưng trên một cluster đang ở trạng thái rất xấu.

- Nguyên tắc 2: Mọi lệnh có thể đổi placement hoặc làm cluster ngừng tự chữa lành như:

    - ceph osd out
    - ceph osd set noout
    - ceph osd set norecover
    - ceph osd set nobackfill
    - ceph osd reweight
    - ceph osd crush reweight
đều phải có kế hoạch rollback hoặc unset tương ứng.

## 1. Kiểm tra trạng thái
- Các lệnh dưới đây là nhóm lệnh đọc trạng thái cơ bản nhất, an toàn để dùng hằng ngày.
```bash
ceph -s
# R | Tóm tắt nhanh health, MON, MGR, OSD, PG, IO

ceph health
# R | Tóm tắt health hiện tại

ceph health detail
# R | Chi tiết cảnh báo, PG lỗi, OSD lỗi, vấn đề cấu hình

ceph -w
# R | Theo dõi sự kiện cluster theo thời gian thực

ceph report
# R | Xuất báo cáo đầy đủ của cluster ở dạng lớn, hữu ích khi debug / lưu evidence

ceph versions
# R | Xem version của từng nhóm daemon

ceph features
# R | Xem feature bits của client / daemon

ceph quorum_status
# R | Chi tiết quorum monitor ở dạng JSON

ceph mon stat
# R | Xem monitor quorum ngắn gọn

ceph mgr stat
# R | Xem manager active/standby

ceph osd stat
# R | Tóm tắt số OSD up/in

ceph osd status
# R | Trạng thái, độ trễ, tải của từng OSD

ceph osd tree
# R | Cây CRUSH: root > rack > host > osd

ceph osd df
# R | Dung lượng và độ lệch sử dụng theo OSD

ceph osd df tree
# R | Kết hợp thông tin dung lượng với cây CRUSH

ceph df
# R | Dung lượng toàn cluster và theo pool

ceph df detail
# R | Chi tiết dung lượng từng pool

rados df
# R | Thống kê object và dung lượng logic theo pool

ceph pg stat
# R | Tóm tắt tình trạng PG toàn cluster

ceph osd perf
# R | Độ trễ commit/apply của OSD

ceph osd blocklist ls
# R | Xem danh sách client/address đang bị chặn

ceph osd blocklist add <addr> [<expire>]
# S2 | Chặn một địa chỉ client hoặc daemon trong khoảng thời gian chỉ định

ceph osd blocklist rm <addr>
# S1 | Gỡ blocklist cho địa chỉ
```
## 2. Quản lý monitor và quorum
Nhóm lệnh này liên quan đến MON, monmap và quorum. Phần lớn là lệnh đọc; thêm/xóa monitor là thao tác ảnh hưởng control plane, cần rất cẩn thận.
```bash
ceph mon dump
# R | Xem monmap hiện tại: fsid, members, epoch

ceph mon getmap -o monmap.bin
# R | Trích monmap ra file

monmaptool --print monmap.bin
# R | In nội dung monmap từ file

ceph mon add <mon-id> <ip:port>
# S2 | Thêm monitor vào cluster

ceph mon remove <mon-id>
# S2 | Gỡ monitor khỏi cluster

ceph quorum_status --format json-pretty
# R | Chi tiết quorum để debug election / split-brain
```

## 3. OSD: kiểm tra, đánh dấu trạng thái, xóa, thay thế
- Đây là nhóm lệnh dễ gây ảnh hưởng nhất trong vận hành thường ngày. Cần phân biệt rất rõ:
    - `in/out`: có còn tham gia placement không
    - `up/down`: daemon còn sống hay không
    - `reweight`: chỉnh phân phối dữ liệu
    - `destroy / purge`: thao tác thay thế hoặc xóa hẳn OSD
```bash
ceph osd tree
# R | Xem OSD nằm ở host/rack nào, trạng thái up/down, in/out

ceph osd find osd.<id>
# R | Vị trí của OSD trong CRUSH + địa chỉ mạng

ceph osd metadata <id>
# R | Metadata OSD: hostname, backend, device class, v.v.

ceph tell osd.<id> version
# R | Xem version một OSD cụ thể

ceph osd in <id>
# S1 | Đưa OSD quay lại placement

ceph osd out <id>
# S2 | Đưa OSD ra khỏi placement, cluster sẽ bắt đầu backfill/recovery

ceph osd down <id>
# S2 | Đánh dấu OSD down thủ công

ceph osd safe-to-destroy <id> [<id>...]
# R | Kiểm tra đã an toàn để destroy/purge chưa

ceph osd destroy <id> --yes-i-really-mean-it
# D | Hủy OSD ID để thay thế; thường dùng trước khi tái dùng cùng ID trong luồng thay ổ

ceph osd purge <id> --yes-i-really-really-mean-it
# D | Xóa OSD khỏi CRUSH, auth, OSD map; dùng khi bỏ hẳn OSD

ceph osd crush remove osd.<id>
# D | Gỡ OSD khỏi CRUSH map; thường là một phần của luồng xóa thủ công cũ

ceph auth del osd.<id>
# D | Xóa auth key của OSD; thường là một phần của luồng xóa thủ công cũ

ceph osd rm <id>
# D | Xóa OSD khỏi OSD map; thường là một phần của luồng xóa thủ công cũ
```
- Reweight: có hai loại rất dễ nhầm là reweight trong OSD map và reweight trong CRUSH. Cả 2 đều là đổi placement nhưng ý nghĩa khác nhau:
    - `ceph osd reweight <id> <weight>`: chỉnh lại trọng số của OSD trong OSD map, ảnh hưởng trực tiếp đến phân phối dữ liệu trên OSD đó. Thường dùng khi OSD có vấn đề về hiệu năng hoặc dung lượng.
    - `ceph osd crush reweight osd.<id> <weight>`: chỉnh lại trọng số của OSD trong CRUSH map, ảnh hưởng đến cách CRUSH chọn OSD cho placement. Thường dùng khi muốn tạm thời giảm tải cho OSD mà không muốn đưa nó ra khỏi placement hoàn toàn. 
```bash
ceph osd reweight <id> <0.0-1.0>
# S2 | Reweight tạm thời ở mức OSD map; hay dùng để giảm tải OSD đầy / lệch

ceph osd crush reweight osd.<id> <weight>
# S2 | Đổi trọng số CRUSH lâu dài, phản ánh dung lượng / vai trò thật của OSD

ceph osd reweight-by-utilization [<threshold>]
# S2 | Tự động chỉnh reweight dựa trên lệch sử dụng

ceph osd test-reweight-by-utilization [<threshold>]
# R | Dry-run cho reweight-by-utilization

```
> ceph osd reweight = chỉnh tạm thời / tactical
> ceph osd crush reweight = chỉnh cấu trúc placement / strategic

## 4. Cờ toàn cluster của OSD
- Các cờ này cực kỳ hữu ích khi bảo trì, nhưng cũng rất dễ bị lạm dụng. Chúng thay đổi hành vi tự chữa lành của cluster.

```bash
ceph osd set noout
# S2 | Không tự mark out OSD down; hay dùng khi reboot node ngắn hạn

ceph osd unset noout
# S1 | Bỏ noout

ceph osd set norebalance
# S2 | Ngăn rebalance

ceph osd unset norebalance
# S1 | Bỏ norebalance

ceph osd set nobackfill
# S2 | Ngăn backfill

ceph osd unset nobackfill
# S1 | Bỏ nobackfill

ceph osd set norecover
# S2 | Ngăn recovery

ceph osd unset norecover
# S1 | Bỏ norecover

ceph osd set noscrub
# S2 | Tắt scrub

ceph osd unset noscrub
# S1 | Bật lại scrub

ceph osd set nodeep-scrub
# S2 | Tắt deep-scrub

ceph osd unset nodeep-scrub
# S1 | Bật lại deep-scrub
```
> `noout`, `norecover`, `nobackfill`, `norebalance` rất hữu ích khi bảo trì ngắn, nhưng nếu quên bỏ cờ thì cluster có thể “trông yên ổn” trong khi không còn tự chữa lành đúng nghĩa.

## 5. Pool: tạo, xem, chỉnh, quota, xóa
- Pool là nơi gắn application tag, quota và durability policy.
```bash
ceph osd pool ls
# R | Liệt kê tên pool

ceph osd pool ls detail
# R | Liệt kê pool kèm chi tiết

ceph osd pool create <pool> <pg_num> [<pgp_num>] replicated [<crush_rule>] [<expected_num_objects>]
# S2 | Tạo replicated pool

ceph osd pool create <pool> <pg_num> [<pgp_num>] erasure <ec_profile> [<crush_rule>] [<expected_num_objects>] [--autoscale-mode=on|off|warn]
# S2 | Tạo erasure-coded pool

ceph osd pool get <pool> all
# R | Xem toàn bộ thuộc tính pool

ceph osd pool get <pool> <key>
# R | Xem một thuộc tính cụ thể

ceph osd pool set <pool> size <n>
# S2 | Đặt số replica cho replicated pool

ceph osd pool set <pool> min_size <n>
# S2 | Đặt số replica/chunk tối thiểu để còn cho phép ghi

ceph osd pool set <pool> recovery_priority <n>
# S2 | Ưu tiên recovery/backfill của pool

ceph osd pool application enable <pool> <rbd|cephfs|rgw|...>
# S1 | Gắn application tag cho pool

ceph osd pool application get <pool>
# R | Xem application tag

ceph osd pool set-quota <pool> max_bytes <bytes>
# S1 | Đặt quota dung lượng

ceph osd pool set-quota <pool> max_objects <count>
# S1 | Đặt quota số object

ceph osd pool rename <old> <new>
# S2 | Đổi tên pool

ceph osd pool delete <pool> <pool> --yes-i-really-really-mean-it
# D | Xóa pool
```
> Để xóa pool, monitor phải cho phép mon_allow_pool_delete=true; nếu không, lệnh sẽ bị từ chối. Đây là cơ chế bảo vệ mặc định của Ceph.

- Tạo pool dùng cho RBD 
```bash
ceph osd pool create vm-images 128 128 replicated
ceph osd pool set vm-images size 3
ceph osd pool set vm-images min_size 2
ceph osd pool application enable vm-images rbd
rbd pool init vm-images
```
## 6. Erasure Coding profile và CRUSH rule
```bash
ceph osd erasure-code-profile ls
# R | Liệt kê profile EC

ceph osd erasure-code-profile get <profile>
# R | Xem nội dung profile EC

ceph osd erasure-code-profile set <profile> k=4 m=2 crush-failure-domain=host plugin=jerasure technique=reed_sol_van
# S2 | Tạo profile EC

ceph osd crush rule ls
# R | Liệt kê CRUSH rules

ceph osd crush rule dump
# R | Xem chi tiết CRUSH rules

ceph osd crush rule create-replicated <rule> <root> <failure-domain> [<class>]
# S2 | Tạo replicated CRUSH rule, ví dụ theo host/rack và device class

ceph osd crush tree
# R | Xem cây CRUSH

ceph osd crush add-bucket <name> <type>
# S2 | Thêm bucket vào CRUSH

ceph osd crush move <name> <type>=<parent>
# S2 | Di chuyển host/bucket trong CRUSH hierarchy
```

## 7. PG: kiểm tra, truy vết, scrub, repair, ưu tiên recovery
- Nhóm lệnh này bám theo trang Placement Groups của Ceph. Đây là nhóm lệnh rất mạnh cho điều tra sự cố. Các lệnh `force-recovery`, `force-backfill`, `repair`, `mark_unfound_lost` có thể ảnh hưởng thực sự tới dữ liệu hoặc thứ tự recovery, nên phải phân biệt mức độ ảnh hưởng.
```bash
ceph pg stat
# R | Tóm tắt PG toàn cluster

ceph pg dump
# R | Dump trạng thái PG

ceph pg dump_stuck inactive
ceph pg dump_stuck unclean
ceph pg dump_stuck stale
ceph pg dump_stuck undersized
ceph pg dump_stuck degraded
# R | Liệt kê PG bị kẹt theo trạng thái

ceph pg map <pgid>
# R | Xem PG đang map tới up/acting set nào

ceph pg <pgid> query
# R | Xem chi tiết rất sâu về PG

ceph pg <pgid> list_missing
# R | Xem object missing của PG

ceph pg scrub <pgid>
# S1 | Chủ động scrub PG

ceph pg deep-scrub <pgid>
# S2 | Chủ động deep-scrub PG; nặng hơn scrub thường

ceph pg repair <pgid>
# S2 | Yêu cầu repair PG; dùng khi đã xác định inconsistent

ceph pg force-recovery <pgid> [<pgid>...]
# S2 | Ưu tiên recovery cho PG chỉ định

ceph pg cancel-force-recovery <pgid> [<pgid>...]
# S1 | Bỏ ưu tiên recovery

ceph pg force-backfill <pgid> [<pgid>...]
# S2 | Ưu tiên backfill cho PG chỉ định

ceph pg cancel-force-backfill <pgid> [<pgid>...]
# S1 | Bỏ ưu tiên backfill

ceph pg <pgid> mark_unfound_lost revert
# D | Đánh dấu object unfound là lost và revert; có thể làm mất dữ liệu logic

ceph pg <pgid> mark_unfound_lost delete
# D | Đánh dấu object unfound là lost và xóa; cực kỳ nguy hiểm

ceph pg ls
# R | Liệt kê PG theo view mặc định

ceph pg ls-by-pool <pool>
# R | Liệt kê PG thuộc một pool

ceph pg ls-by-primary <osd-id>
# R | Liệt kê PG mà một OSD đang làm primary

ceph pg ls-by-osd <osd-id>
# R | Liệt kê PG có liên quan tới một OSD

ceph pg map <pgid>
# R | Xem up/acting set của PG

ceph pg dump pgs_brief
# R | Dump PG ở chế độ ngắn gọn

ceph pg dump pools
# R | Dump PG theo góc nhìn pool
```
>> `ls-by-primary` và `ls-by-osd` rất hữu ích khi một OSD có biểu hiện bất thường nhưng bạn muốn biết nó đang ảnh hưởng đến những PG nào mà không cần tự lọc JSON dài.

> query = lệnh điều tra sâu nhất cho một PG
> scrub/deep-scrub = kiểm tra tính nhất quán
> repair = chỉ dùng khi đã biết vấn đề và chấp nhận can thiệp
> mark_unfound_lost = lệnh cuối cùng khi không còn đường phục hồi an toàn
## 8. Xác thực và phân quyền
- Nhóm lệnh này liên quan đến quản lý keyring và phân quyền. Thao tác với auth có thể ảnh hưởng đến khả năng client hoặc daemon kết nối, nên cần cẩn thận.
```bash
ceph auth list
# R | Liệt kê toàn bộ user/entity và caps

ceph auth get client.admin
# R | Xem key + caps của một entity

ceph auth export client.admin -o client.admin.keyring
# R | Xuất keyring

ceph auth get-or-create client.rbd mon 'allow r' osd 'allow rw pool=rbd'
# S1 | Tạo user và caps; nếu đã tồn tại thì trả lại

ceph auth get-or-create-key client.libvirt mon 'allow r' osd 'allow rw pool=vms' -o client.libvirt.key
# S1 | Tạo user và chỉ in key

ceph auth caps client.rbd mon 'allow r' osd 'allow rw pool=rbd'
# S2 | Ghi đè caps hiện tại của user

ceph auth del client.rbd
# D | Xóa user/auth entity

ceph auth print-key client.libvirt
# R | In riêng secret key
```
> ceph auth caps là thao tác ghi đè caps hiện tại. Muốn thêm quyền mà không làm mất quyền cũ, cần đọc caps cũ trước rồi đặt lại đầy đủ.

## 9. Làm việc trực tiếp với object bằng rados
- Đây là nhóm lệnh ở tầng object trực tiếp, không qua RBD hoặc CephFS. Rất hữu ích để debug hoặc thao tác thủ công với object.
```bash
rados lspools
# R | Liệt kê pool

rados df
# R | Thống kê số object và dung lượng logic

rados -p <pool> ls
# R | Liệt kê object trong pool

rados -p <pool> stat <object>
# R | Xem size / mtime của object

rados -p <pool> put <object> <file>
# S1 | Ghi file thành object

rados -p <pool> get <object> <file>
# R | Đọc object ra file

rados -p <pool> rm <object>
# D | Xóa object

rados -p <pool> listwatchers <object>
# R | Xem watcher trên object

rados list-inconsistent-pg <pool>
# R | Liệt kê PG inconsistent trong pool | Dùng khi health báo inconsistent, cần biết pool nào có PG lỗi

rados list-inconsistent-obj <pgid>
# R | Liệt kê object inconsistent trong PG | Dùng khi cần truy tới object inconsistent cụ thể

rados list-inconsistent-snapset <pgid>
# R | Liệt kê snapset inconsistent | Dùng khi nghi lỗi liên quan snapshot metadata/object set

rados export <file> -p <pool>
# R/S2 | Xuất toàn bộ nội dung pool để forensic/migration; có thể rất nặng

rados import <file> -p <pool>
# S2 | Nhập object vào pool; cần cực kỳ cẩn thận

rados bench -p <pool> 60 write
rados bench -p <pool> 60 seq
rados bench -p <pool> 60 rand
# S2 | Benchmark object IO; chỉ chạy khi hiểu tác động

rados cleanup --run-name <name>
# S1 | Dọn object benchmark
```


## 10. RBD: quản lý block images
- Nhóm lệnh này liên quan đến quản lý RBD images, snapshots và clones. Thao tác với RBD có thể ảnh hưởng đến VM hoặc ứng dụng đang sử dụng image, nên cần cẩn thận.
```bash
rbd ls -p <pool>
# R | Liệt kê image trong pool

rbd info <pool>/<image>
# R | Xem thông tin image

rbd du <pool>/<image>
# R | Xem dung lượng thực tế đã dùng ở mức object

rbd create <pool>/<image> --size <size-in-MiB>
# S1 | Tạo image

rbd resize <pool>/<image> --size <size-in-MiB>
# S2 | Mở rộng / thu nhỏ image (thu nhỏ cần cực kỳ cẩn thận)

rbd rm <pool>/<image>
# D | Xóa image

rbd map <pool>/<image>
# S1 | Map image vào host Linux hiện tại

rbd unmap /dev/rbdX
# S1 | Unmap image

rbd snap ls <pool>/<image>
# R | Liệt kê snapshot

rbd snap create <pool>/<image>@<snap>
# S1 | Tạo snapshot

rbd snap rm <pool>/<image>@<snap>
# D | Xóa snapshot

rbd export <pool>/<image> <file>
# R/S2 | Xuất image ra file, có thể rất nặng

rbd import <file> <pool>/<image>
# S2 | Nhập image từ file

rbd showmapped
# R | Xem các image đang được map trên host hiện tại

rbd du <pool>/<image>
# R | Xem dung lượng thực đã dùng ở mức object

rbd children <pool>/<image>@<snap>
# R | Xem clone nào đang phụ thuộc snapshot này

rbd snap protect <pool>/<image>@<snap>
# S1 | Bảo vệ snapshot để có thể clone

rbd snap unprotect <pool>/<image>@<snap>
# S1 | Bỏ bảo vệ snapshot

rbd clone <pool>/<image>@<snap> <pool>/<clone-image>
# S2 | Tạo clone từ snapshot

rbd flatten <pool>/<clone-image>
# S2 | Gỡ phụ thuộc clone khỏi parent snapshot

rbd export-diff <pool>/<image>@<snap> <file>
# R/S2 | Xuất delta giữa image và snapshot

rbd import-diff <file> <pool>/<image>
# S2 | Nhập delta vào image
```
## 11. CephFS
- Nhóm lệnh này liên quan đến quản lý CephFS, bao gồm tạo filesystem, quản lý metadata pool và data pool. Thao tác với CephFS có thể ảnh hưởng đến ứng dụng đang sử dụng filesystem, nên cần cẩn thận.
```bash
ceph fs ls
# R | Liệt kê CephFS

ceph fs status
# R | Trạng thái CephFS

ceph fs dump
# R | Chi tiết CephFS map

ceph mds stat
# R | Trạng thái MDS

ceph fs new <fs_name> <metadata_pool> <data_pool>
# S2 | Tạo CephFS

ceph fs get <fs_name>
# R | Xem cấu hình một CephFS

ceph fs set <fs_name> max_mds <n>
# S2 | Tăng/giảm số MDS active mong muốn

ceph mds fail <who>
# S2 | Đánh dấu fail một MDS để trigger failover
```

## 12. RGW (Rados Gateway)
- Nhóm lệnh này liên quan đến quản lý Rados Gateway, bao gồm tạo realm, zonegroup và zone. Thao tác với RGW có thể ảnh hưởng đến ứng dụng đang sử dụng gateway, nên cần cẩn thận.
```bash
ceph rgw zonegroup ls
# R | Liệt kê zonegroup

ceph rgw zonegroup get <zonegroup>
# R | Xem cấu hình zonegroup

ceph rgw zone ls
# R | Liệt kê zone

ceph rgw zone get <zone>
# R | Xem cấu hình zone

ceph rgw realm ls
# R | Liệt kê realm

ceph rgw realm get <realm>
# R | Xem cấu hình realm
```

## 13. cephadm / orchestrator (ceph orch *)
- Nhóm này chỉ dùng nếu **cluster 16.2.x của bạn là cluster cephadm / orchestrator-managed**. RHCS 5 Operations Guide và Ceph Pacific cephadm docs xác nhận các lệnh như `ceph orch host ls`, `ceph orch ps`, `ceph orch ls`, `ceph orch apply osd --all-available-devices` đều thuộc mô hình quản trị này.
```bash
ceph orch status
# R | Tình trạng orchestrator backend

ceph orch host ls
# R | Liệt kê host được orchestrator quản lý

ceph orch ps
# R | Liệt kê daemon/container đang chạy

ceph orch ls
# R | Liệt kê service spec

ceph orch ls --export
# R | Export service spec ra YAML

ceph orch device ls
# R | Liệt kê thiết bị có thể dùng để triển khai OSD

ceph orch host add <host> <ip>
# S2 | Thêm host vào cluster cephadm

ceph orch host rm <host>
# S2 | Gỡ host khỏi cluster cephadm (chỉ khi host đã sạch daemon phù hợp)

ceph orch apply osd --all-available-devices
# S2 | Tạo OSD trên toàn bộ ổ còn trống; hợp cho lab/cluster nhỏ hơn

ceph orch daemon add osd <host>:<device>
# S2 | Tạo OSD trên một thiết bị cụ thể

ceph orch apply -i <service_spec.yaml>
# S2 | Áp service spec

ceph orch redeploy <service-or-daemon>
# S2 | Redeploy service/daemon

ceph orch restart <service-or-daemon>
# S2 | Restart service/daemon

ceph orch ps --daemon_type osd
# R | Lọc daemon theo loại

ceph orch ps <host>
# R | Xem daemon trên một host

ceph orch ls --export
# R | Export service spec ra YAML

ceph orch apply -i service.yaml
# S2 | Áp lại service spec từ file

ceph orch daemon add osd <host>:/dev/sdX
# S2 | Tạo OSD trên thiết bị cụ thể

ceph orch host label add <host> <label>
# S1 | Gắn nhãn host để dùng trong placement

ceph orch host label rm <host> <label>
# S1 | Gỡ nhãn host
```
> docs nêu rõ `ceph orch apply osd --all-available-devices` thường phù hợp hơn với cluster nhỏ; với cluster lớn nên cân nhắc sử dụng file service spec . Red Hat cũng lưu ý lệnh này tạo WAL/DB colocated mặc định; nếu muốn tách block.db / block.wal, không nên dùng nó một cách mù quáng.

## 14. `ceph-volume` và `ceph device` kiểm tra thiết bị 
- Nhóm lệnh này chỉ dùng nếu bạn đang quản lý OSD theo cách thủ công, không qua cephadm. `ceph-volume` là công cụ để tạo OSD trên các thiết bị vật lý hoặc LVM, thường dùng trong cluster non-cephadm hoặc khi cần kiểm soát chi tiết hơn.
```bash
ceph-volume lvm list
# R | Liệt kê LV/device gắn với OSD

ceph-volume lvm prepare --data /dev/sdX
# S2 | Chuẩn bị device cho OSD nhưng chưa activate/start

ceph-volume lvm activate <osd_id> <osd_fsid>
# S2 | Activate OSD đã prepare

ceph-volume lvm create --data /dev/sdX
# S2 | Prepare + activate một bước

ceph-volume lvm batch --bluestore /dev/sdb /dev/sdc
# S2 | Tạo nhiều OSD tự động theo batch logic

ceph-volume lvm zap /dev/sdX --destroy
# D | Xóa chữ ký/LVM trên thiết bị; rất nguy hiểm

ceph-volume lvm batch --bluestore /dev/sdb /dev/sdc
# S2 | Chuẩn bị nhiều OSD theo batch logic

ceph-volume lvm prepare --data /dev/sdX
# S2 | Chỉ prepare, chưa activate daemon

ceph-volume lvm create --data /dev/sdX
# S2 | Prepare + activate trong một bước

ceph-volume lvm zap /dev/sdX --destroy
# D | Xóa chữ ký / VG / LV liên quan trên thiết bị

ceph device ls
# R | Liệt kê thiết bị mà cluster biết tới

ceph device info <devid>
# R | Xem thông tin chi tiết một thiết bị

ceph device ls-by-daemon
# R | Liệt kê mapping thiết bị ↔ daemon

ceph device check-health
# S1 | Yêu cầu cập nhật/đánh giá tình trạng thiết bị

ceph device scrape-health-metrics <devid>
# S1 | Thu thập health metrics cho thiết bị chỉ định

ceph device predict-life-expectancy <devid>
# R | Ước lượng tuổi thọ còn lại nếu backend hỗ trợ

ceph device predict-life-expectancy <devid> from <date>
# R | Ước lượng từ mốc thời gian chỉ định
```
- ceph device ls và ceph device info vẫn rất hữu ích để nối:
    - OSD nào đang dùng thiết bị nào
    - model/serial nào đang liên quan đến sự cố
    - thiết bị có cảnh báo SMART hay không

## 15. `ceph tell` và `ceph daemon`
- Dùng để hỏi sâu trạng thái daemon hoặc gọi lệnh admin nội bộ. Cần hiểu rõ khác nhau:
    - `ceph tell` gửi lệnh tới daemon qua cluster control plane
    - `ceph daemon` làm việc với admin socket cục bộ của daemon
```bash
ceph tell osd.<id> version
# R | Xem version daemon

ceph tell osd.<id> flush_pg_stats
# S1 | Yêu cầu OSD đẩy lại PG stats

ceph daemon osd.<id> perf dump
# R | Xem counters/perf của OSD (chạy trên đúng host có admin socket)

ceph daemon osd.<id> dump_ops_in_flight
# R | Xem các ops đang treo / đang xử lý

ceph daemon mon.<id> mon_status
# R | Xem mon status sâu từ admin socket

ceph daemon osd.<id> dump_ops_in_flight
# R | Xem các operation đang treo trên OSD đó

ceph daemon osd.<id> perf dump
# R | Xem counters/perf nội bộ của OSD

ceph daemon osd.<id> status
# R | Xem trạng thái chi tiết của OSD

ceph daemon mon.<id> mon_status
# R | Xem trạng thái monitor ở mức sâu từ admin socket

ceph daemon <daemon> help
# R | Liệt kê các lệnh admin socket mà daemon đó hỗ trợ
```

## 16. Quản lý config và log
```bash
ceph config dump
# R | Xem toàn bộ cấu hình đang được lưu trong config database của cluster

ceph config get <who> <key>
# R | Xem giá trị một cấu hình cụ thể cho một entity, ví dụ:
# ceph config get osd.12 debug_osd

ceph config show <who>
# R | Hiển thị cấu hình hiệu lực nhìn từ một daemon/entity cụ thể

ceph config set <who> <key> <value>
# S2 | Ghi cấu hình vào config database, có hiệu lực runtime hoặc gần-runtime tùy option

ceph config rm <who> <key>
# S1 | Xóa override của cấu hình trong config database

ceph config assimilate-conf -i /etc/ceph/ceph.conf
# S2 | Đưa nội dung file ceph.conf vào config database tập trung

ceph config generate-minimal-conf
# R | Sinh file conf tối thiểu từ cluster hiện tại
```
- Ví dụ với 1 osd 
```bash
ceph config get osd.12 debug_osd
# R | Kiểm tra giá trị hiện tại trước khi đổi

ceph config set osd.12 debug_osd 5/5
# S2 | Tăng log debug cho một OSD cụ thể

ceph config set osd osd_max_backfills 1
# S2 | Giảm số backfill đồng thời toàn bộ OSD

ceph config set mon mon_max_pg_per_osd 300
# S2 | Điều chỉnh ngưỡng monitor cho PG/OSD

ceph config rm osd.12 debug_osd
# S1 | Gỡ cấu hình override đã set trước đó
```


```bash
ceph log last 100
# R | Xem 100 dòng log cuối của cluster

ceph log last 100 osd.<id>
# R | Xem 100 dòng log cuối của OSD

ceph log last 100 mon.<id>
# R | Xem 100 dòng log cuối của MDS

ceph log last [<n>]
# R | Xem các bản ghi sự kiện gần nhất của cluster log

ceph crash ls
# R | Liệt kê các crash đã ghi nhận

ceph crash info <crash-id>
# R | Xem chi tiết một crash

ceph crash archive <crash-id>
# S1 | Đánh dấu một crash là đã xử lý

ceph crash archive-all
# S1 | Đánh dấu toàn bộ crash hiện có là đã xử lý

ceph crash prune <days>
# S1 | Xóa các bản ghi crash cũ hơn số ngày chỉ định
```