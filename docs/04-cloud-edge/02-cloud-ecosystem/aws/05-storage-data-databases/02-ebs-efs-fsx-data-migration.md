# EBS, EFS, FSx And Data Migration

## Overview

AWS có ba kiểu storage chính ngoài object storage: block, file và migration/hybrid storage. Chọn sai kiểu storage là lỗi thiết kế rất phổ biến trong SAA scenario.

## Block vs File

| Service | Type | Khi dùng |
|---|---|---|
| EBS | Block | OS disk, database disk, low latency volume cho một EC2 trong cùng AZ |
| EFS | File/NFS | Shared Linux filesystem nhiều EC2, multi-AZ access |
| FSx for Windows | File/SMB | Windows file share, AD integration |
| FSx for Lustre | File/HPC | HPC/ML workload cần throughput cao, Lustre client |

## EBS Patterns

- EBS volume nằm trong một AZ; EC2 muốn attach volume phải ở cùng AZ.
- Snapshot giúp backup và tạo volume mới, có thể copy cross-region.
- Fast Snapshot Restore hữu ích khi cần volume mới có performance ngay, nhưng cần cân nhắc chi phí.
- Data Lifecycle Manager giúp tự động retention snapshot để tránh snapshot cost tăng mãi.
- Snapshot lock/Object Lock tương tự nên được xem xét khi yêu cầu chống xóa nhầm theo compliance.

EBS là block device độc lập với lifecycle của EC2 hơn instance store, nhưng vẫn là tài nguyên zonal. Volume có thể tồn tại khi instance terminate nếu `DeleteOnTermination` không xóa nó, nên cleanup phải kiểm tra cả orphaned volume lẫn snapshot.

Mental model:

```text
EC2 instance in AZ A
-> attach EBS volume in AZ A
-> OS sees block device
-> partition/filesystem/LVM/database decides how data is written
```

Các điểm vận hành quan trọng:

- Không format volume nếu chưa xác nhận đó là volume mới hoặc đã có backup. `mkfs` là thao tác phá hủy dữ liệu.
- Mount bằng UUID hoặc cấu hình ổn định thay vì tin tuyệt đối vào device name như `/dev/xvdf`, vì tên device có thể khác theo OS/Nitro mapping.
- Với database hoặc filesystem đang ghi, snapshot crash-consistent có thể chưa đủ; cần app-consistent snapshot bằng freeze/flush/quiesce hoặc cơ chế backup của database.
- Khi detach volume, unmount filesystem trước để tránh corruption.
- Volume type, instance type và EBS bandwidth đều ảnh hưởng performance; tăng IOPS volume nhưng instance không đủ EBS bandwidth thì vẫn nghẽn.

Snapshot workflow an toàn:

1. Xác định đúng account, Region, AZ, instance ID, volume ID và mount point.
2. Kiểm tra volume đang chứa loại dữ liệu gì: filesystem thường, database, LVM/RAID hay encrypted volume.
3. Nếu cần consistency, flush/quiesce ứng dụng hoặc tạm freeze filesystem trong thời gian rất ngắn.
4. Tạo snapshot rồi unfreeze ngay sau khi request snapshot được nhận, không chờ snapshot hoàn tất mới unfreeze.
5. Validate snapshot bằng cách tạo volume restore thử ở môi trường an toàn.
6. Gắn tag owner, workload, retention và dùng lifecycle policy cho snapshot.

Các thao tác cần cảnh báo rõ:

```bash
echo "Read-only checks trước khi đụng dữ liệu"
lsblk -f
findmnt
sudo file -s /dev/<device>

echo "DANGEROUS: chỉ chạy mkfs khi chắc chắn volume không chứa dữ liệu cần giữ"
sudo mkfs -t ext4 /dev/<device>
```

`dd` có thể dùng để đo throughput đơn giản, nhưng dễ làm sai và phá dữ liệu nếu đảo `if`/`of`. Với production benchmark, ưu tiên công cụ như `fio`, chạy trên volume test, ghi rõ block size, queue depth, read/write mix và không chạy trên filesystem đang phục vụ workload thật.

## Instance Store

Instance store là block storage gắn với host/instance, thường có latency/throughput tốt cho workload tạm thời, nhưng dữ liệu mất khi instance stop/terminate hoặc host có sự cố. Nó không phải nơi lưu dữ liệu duy nhất cho database primary, file upload hoặc state quan trọng.

Use case phù hợp:

- Cache có thể rebuild.
- Temporary scratch space cho batch/transcode/sort.
- Replicated database/node khi ứng dụng tự replication và chịu được node loss.
- Buffer tạm trước khi flush sang S3/EBS/managed storage.

Guardrails:

- Tài liệu hóa rõ dữ liệu nào trên instance store có thể mất.
- Đẩy log/state quan trọng ra ngoài instance.
- Thiết kế Auto Scaling/replace node như mất disk là tình huống bình thường.
- Không backup instance store bằng cron/rsync như cơ chế chính cho dữ liệu critical; nếu cần backup thường xuyên, xem lại lựa chọn storage.

## Shared File Pattern

Nếu hai EC2 sau ALB cần thấy cùng file upload của user, không dùng hai EBS volume riêng. Chuyển file shared sang EFS hoặc object sang S3 tùy semantics app.

Rule nhanh:

- App cần POSIX/NFS shared file: EFS.
- Windows SMB/AD: FSx for Windows.
- HPC/Lustre: FSx for Lustre.
- Object/static/media/data lake: S3.

Tự dựng NFS trên một EC2 + instance store/EBS backup là pattern legacy/lab, không phải mặc định production. Nó tạo single point of failure, yêu cầu tự patch OS/NFS, tự snapshot/restore, tự xử lý split-brain/lock/performance và dễ mở nhầm NFS port. Nếu bắt buộc dùng NFS tự quản:

- Chỉ allow NFS từ security group client, không mở NFS ra Internet.
- Có backup app-consistent và restore test.
- Có monitoring cho mount latency, stale file handle, disk full, rsync/snapshot failure.
- Có runbook failover hoặc chấp nhận downtime rõ ràng.
- Cân nhắc EFS/FSx trước khi tự vận hành.

## Data Migration

| Requirement | Pattern |
|---|---|
| Dữ liệu lớn, muốn giảm bandwidth internet/VPN | Snowball Edge |
| Sync file/object liên tục hoặc định kỳ | DataSync |
| Extend on-prem file storage ra S3 | S3 File Gateway |
| NFS/SMB file server lên AWS | DataSync hoặc File Gateway tùy use case |

SAA pattern: Nếu dữ liệu rất lớn và đường truyền đang gần full, offline transfer bằng Snowball thường thắng giải pháp online về tổng rủi ro bandwidth, dù có thời gian nhận/trả thiết bị.

## Related Pages

- [S3 Object Storage Patterns](./01-s3-object-storage-patterns.md)
- [EC2, Auto Scaling And Load Balancing](../03-compute-containers-serverless/01-ec2-auto-scaling-load-balancing.md)
