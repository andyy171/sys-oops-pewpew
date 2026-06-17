# Các điểm đáng chú ý từ phiên bản 16.2.x -> 19.2.x

- Thay đổi lớn nhất chủ yếu xoáy quanh 6 trụ cột chính :
    1. cephadm/orchestration trưởng thành hơn
    2. Filestore bị loại bỏ dần rồi không còn support 
    3. BlueStore/RocksDB tiếp tục được tối ưu mạnh
    4. dashboard và monitoring ngày càng usable hơn
    5. RGW multisite/IAM/SSE cải thiện nhiều
    6. CephFS và RBD có thêm tính năng phục vụ DR, snapshot, clone, backup, sync.

## 1. Các thay đổi bản Quincy (17.2.x)
- Filestore bị deprecate ở Quincy.
- Pool `device_health_metrics` được đổi thành `.mgr` để dùng chung cho các mgr modules.
- `ceph pg dump` có thêm cột mới phục vụ scrub visibility.
- Có health warning nếu `require-osd-release` không được set đúng sau upgrade.
- LevelDB support bị bỏ, monitor/OSD cần ở hướng RocksDB trước khi nâng lên Quincy.
- Với cephadm, `osd_memory_target_autotune` bật mặc định, ratio mặc định là `0.7` RAM tổng; tài liệu cảnh báo giá trị này không phù hợp cho hyperconverged, và gợi ý giảm xuống `0.2` cho mô hình đó.

- **Về vận hành,** Quincy còn mở rộng cephadm khá rõ: SNMP support, colocate daemon, memory autotuning, NFS mgr integration, zap OSD khi remove, cephadm agent để tăng performance/scalability. Nói gọn: từ đây trở đi, nếu bạn đang tư duy cluster theo kiểu thủ công cũ, thì docs bắt đầu ép bạn nhìn cluster như một hệ orchestration chuẩn hơn.

- **Về dashboard/observability,** Quincy thêm Cluster Expansion Wizard, quản lý NFS exports, cải thiện quản lý host/service/daemon, thêm 43 alert mới, hỗ trợ SNMP traps, và cập nhật stack monitoring. Nếu team bạn có dùng dashboard/monitoring nhiều, đây là mốc tài liệu đáng skim nhất sau RHCS 5.

- **Về RADOS,** Quincy đổi một thứ khá đáng nhớ: với BlueStore OSD, mặc định chuyển sang mclock_scheduler để cung cấp QoS; Filestore thì không hỗ trợ mclock. Nếu cluster của bạn có tuning queue/scrub/recovery nhạy cảm, đây là một trong những điểm cần đọc kỹ khi so sánh Pacific với các đời sau.


## 2. Các điểm thay đổi ở bản Reef (18.2.x)
- Reef (18.2.x) là nơi nhiều thứ từ “đang đổi” thành “đã chốt”. Release notes 18.2.0 nêu rõ:
    - FileStore không còn được hỗ trợ nữa.
    - RocksDB nâng lên 7.9.2.
    - Có cải thiện lớn về RocksDB iteration overhead/performance.
    - `perf dump` và `perf schema` bị deprecate, chuyển sang `counter - dump / counter schema`.
    - Cache tiering bị deprecate.
    - Có thêm read balancer để cân bằng primary PG theo pool.
    - RGW cũng có 1 số thay đổi đáng chú ý :
        - Bucket resharding hỗ trợ cho multisite.
        - Multisite replication ổn định và nhất quán hơn.
        - Compression hỗ trợ cho object upload bằng Server-Side Encryption.
- **Về Dashboard,** Reef nâng cấp mạnh về khả năng thao tác: layout mới, quản lý Ceph users, cấu hình RGW SSE-S3/KMS ngay từ lúc tạo bucket, cấu hình RBD snapshot mirroring qua UI, wizard tạo OSD dễ hơn, thêm centralized logging, và monitoring chuyển mạnh sang ceph-exporter trên từng daemon thay vì dồn qua exporter cũ.

- **Về CephFS,** Reef có thay đổi nhỏ nhưng đáng biết: đổi tên một số option phía client/MDS, và hỗ trợ xóa recovered files trong lost+found theo workflow DR. Không quá “đập mặt” như RGW/RADOS, nhưng vẫn đáng note.
> release notes mới của Reef có nêu một known issue khi upgrade từ Pacific lên Reef có thể gây cảnh báo `OSD_UPGRADE_FINISHED` sớm do feature bit deprecated, tức là nếu sau này bạn định nhảy dài, phải đọc kỹ release note hotfix chứ không chỉ đọc 18.2.0.

## 3. Các điểm thay đổi ở bản Squid (19.2.x)
- Squid (19.2.x) là nhánh stable thứ 19, phát hành đầu tiên ngày 2024-09-26, hiện vẫn active và nhận backport. Đây là bộ docs bạn nên xem chính khi test feature mới trên 19.x.
- Các điểm đáng chú ý :
    - RADOS / BlueStore
        - BlueStore được tối ưu tốt hơn cho workload nhiều snapshot.
        - RocksDB LZ4 compression bật mặc định để cải thiện hiệu năng trung bình và tối ưu dùng fast device.
        - Có thêm EC configurations linh hoạt hơn, OpTracker để debug vấn đề mgr module, và scrub scheduling tốt hơn.
    - Dashboard
        - Layout/navigation cải thiện.
        - Quản lý CephFS snapshots, clones, snapshot schedules.
        - Quản lý authorization capabilities cho CephFS.
        - Có helper cho việc mount CephFS volume.
    - RBD
        - diff-iterate có thể chạy local, tăng mạnh hiệu năng cho QEMU live disk sync và backup/sync use cases.
        - Hỗ trợ clone từ non-user type snapshots.
        - rbd-wnbd hỗ trợ multiplex image mappings.

    - RGW
       - Có User Accounts feature mở thêm nhiều AWS-compatible IAMAPIs để tự quản lý users, keys, groups, roles, policies. Đây là một thay đổi rất lớn nếu bên bạn làm S3/RGW nhiều.
    - Crimson/Seastore
        - Có tech preview đầu tiên cho Crimson, hỗ trợ RBD workload trên replicated pools. Đây chưa phải thứ nên đưa thẳng vào prod chỉ vì thấy mới.

    - CephFS

        - Có bộ lệnh subvolume quiesce để pause write I/O và metadata mutation, phục vụ crash-consistent snapshots cho distributed apps.
        - Có lệnh ceph fs swap để swap hai filesystem names/IDs, hữu ích cho DR.
        - `ceph fs authorize` giờ có thể upgrade capabilities idempotent thay vì báo lỗi như trước.
        - `ceph fs rename` có thêm điều kiện bắt buộc filesystem phải offline và set refuse_client_session trước khi đổi tên.

