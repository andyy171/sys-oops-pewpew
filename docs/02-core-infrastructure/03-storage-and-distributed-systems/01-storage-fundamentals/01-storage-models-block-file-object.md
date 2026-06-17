# Storage Models: Block, File, Object

## Overview

Storage model mô tả cách hệ thống biểu diễn, định danh và truy cập dữ liệu. Ba mô hình phổ biến nhất là block storage, file storage và object storage. Chúng không chỉ khác nhau ở giao thức truy cập, mà còn khác ở metadata, latency, scaling, cách phân quyền và workload phù hợp.

Luồng đọc/ghi cơ bản có thể hình dung như sau:

```text
application
  -> operating system / client library
  -> filesystem or storage protocol
  -> block/object/file backend
  -> disk/controller/network/distributed placement
```

## Block Storage

Block storage chia dữ liệu thành các block có kích thước cố định hoặc gần cố định. Mỗi block được định danh bằng địa chỉ logic như LBA, còn filesystem hoặc database phía trên chịu trách nhiệm tổ chức file, page, record hoặc metadata.

Đặc điểm chính:

- Truy cập gần với thiết bị lưu trữ, phù hợp với random I/O và latency thấp.
- Metadata ở tầng storage thường tối thiểu; logic cao hơn nằm ở filesystem, volume manager hoặc database.
- Thường dùng cho VM disk, database, raw volume, iSCSI, Fibre Channel, RBD hoặc cloud volume.
- Scaling thường theo dung lượng/performance của volume hoặc backend block bên dưới.

Nhầm lẫn thường gặp: block storage không tự biết "file" là gì. Nếu một VM dùng volume block, filesystem bên trong VM mới là nơi hiểu directory, permission và file layout.

## File Storage

File storage tổ chức dữ liệu theo cây thư mục và file. Mỗi file có metadata như tên, path, kích thước, owner, permission, timestamp và đôi khi ACL hoặc extended attributes.

Đặc điểm chính:

- Truy cập qua path, dễ dùng cho con người và ứng dụng legacy.
- Có mô hình permission ở cấp file/directory.
- Phù hợp với home directory, shared folder, media repository, build artifact share, NFS, SMB/CIFS hoặc CephFS.
- Scale bị ảnh hưởng bởi metadata path, directory size, locking và số client đồng thời.

File storage thường đặt trên block storage ở tầng vật lý, nhưng cung cấp semantic khác hẳn: ứng dụng thao tác với file/path thay vì block address.

## Object Storage

Object storage lưu dữ liệu thành object gồm data, metadata và key. Namespace thường phẳng; dấu `/` trong object key chỉ là convention để mô phỏng thư mục, không phải directory thật như filesystem.

Đặc điểm chính:

- Truy cập qua API, phổ biến nhất là S3-compatible API.
- Metadata linh hoạt hơn file/block storage.
- Scale tốt cho dữ liệu phi cấu trúc, backup, archive, image/video, log, data lake.
- Latency thường cao hơn block storage; không phù hợp cho workload cần update nhỏ, ngẫu nhiên, liên tục như database transaction trực tiếp.
- Consistency, versioning, lifecycle, retention và policy là phần quan trọng của thiết kế.

Object storage mạnh ở capacity và durability, nhưng yêu cầu ứng dụng hiểu API/object key thay vì mount như filesystem truyền thống.

## So Sánh Nhanh

| Tiêu chí | Block storage | File storage | Object storage |
|---|---|---|---|
| Đơn vị truy cập | Block / volume | File / directory | Object / key |
| Metadata | Ít, thường ở tầng trên | File metadata, permission, timestamp | Metadata linh hoạt theo object |
| Workload phù hợp | VM, database, low-latency I/O | Shared file, home directory, collaboration | Backup, archive, media, data lake |
| Giao thức ví dụ | iSCSI, FC, NVMe-oF, RBD | NFS, SMB, CephFS | S3, Swift, RGW |
| Điểm nghẽn hay gặp | IOPS, latency, queue depth | metadata, lock, directory traversal | API latency, bucket/index, object count, network |
| Scaling | Theo volume/backend | Theo metadata + data path | Theo namespace, object count, node/backend |

## DAS, NAS, SAN Và Distributed Storage

- DAS (Direct-Attached Storage): disk gắn trực tiếp vào host. Đơn giản, latency thấp, nhưng khó chia sẻ và dễ thành điểm lỗi đơn nếu không có replication/backup.
- NAS (Network-Attached Storage): storage qua mạng ở cấp file, thường dùng NFS/SMB.
- SAN (Storage Area Network): mạng lưu trữ chuyên dụng hoặc logic chuyên dụng ở cấp block, thường dùng iSCSI/Fibre Channel/NVMe-oF.
- Distributed storage: dữ liệu được phân tán qua nhiều node, có cơ chế placement, replication hoặc erasure coding để tăng durability và availability.

Trong thực tế, các mô hình này có thể chồng lớp lên nhau. Ví dụ một dịch vụ file storage có thể dùng block device bên dưới, còn một nền tảng unified storage như Ceph có thể cung cấp block, file và object trên cùng cluster.

## Chọn Model Theo Workload

- Chọn block storage khi ứng dụng cần latency thấp, random I/O và tự quản lý cấu trúc dữ liệu, ví dụ database hoặc VM disk.
- Chọn file storage khi nhiều client cần chia sẻ file theo path và permission quen thuộc.
- Chọn object storage khi dữ liệu lớn, phi cấu trúc, cần API, lifecycle, scale ngang và durability cao.
- Không dùng replication thay cho backup. Replication giúp availability/durability trước lỗi phần cứng, nhưng bad write hoặc delete nhầm vẫn có thể được replicate.

## Trang Liên Quan

- [Disk And Device Fundamentals](./02-disk-and-device-fundamentals.md)
- [Filesystem Basics](./04-filesystem-basics.md)
- [Backup, Snapshot And Replication](./07-backup-snapshot-replication.md)
- [Storage Performance: IOPS, Throughput, Latency](./08-storage-performance-iops-throughput-latency.md)
