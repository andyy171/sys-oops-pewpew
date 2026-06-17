# Filesystem Basics

## Overview

Filesystem là lớp biến block device thành không gian file/directory có tên, metadata, permission và quy tắc truy cập. Nếu không có filesystem, dữ liệu chỉ là các block rời rạc; OS hoặc ứng dụng sẽ không biết file bắt đầu/kết thúc ở đâu, ai sở hữu, quyền gì và block nào còn trống.

```text
application
  -> VFS / syscall
  -> filesystem implementation
  -> block allocation / inode / metadata
  -> block device
```

## Logical, Virtual Và Physical Filesystem

- Logical filesystem: xử lý API cấp file như open, close, read, write, permission, directory operation.
- VFS (Virtual File System): lớp trừu tượng trong Linux cho phép nhiều filesystem cùng tồn tại, ví dụ ext4, XFS, Btrfs, tmpfs, NFS.
- Physical filesystem: triển khai cụ thể cách layout metadata/data block trên disk và tương tác với block layer.

VFS giúp ứng dụng dùng cùng syscall dù backend là local disk, network filesystem hay pseudo filesystem như `/proc`.

## Mount Và Namespace

Mount là thao tác gắn một filesystem vào cây thư mục. Kernel đọc metadata quan trọng như superblock, tạo cấu trúc in-memory cho mounted volume, rồi VFS chuyển lời gọi file đến implementation phù hợp.

Lệnh quan sát an toàn:

```bash
findmnt
mount | column -t
df -hT
lsblk -f
```

## On-Disk Structures

Nhiều filesystem dùng các cấu trúc tương tự:

- Superblock: metadata cấp filesystem như block size, số block, trạng thái.
- Block group hoặc allocation group: chia filesystem thành vùng quản lý nhỏ hơn.
- Bitmap/free-space map: theo dõi block hoặc inode còn trống.
- Inode hoặc File Control Block: metadata của file.
- Data block: nơi chứa nội dung file hoặc directory entries.

Trong Unix/Linux, inode thường chứa owner, permission, size, timestamp, link count và pointer đến data blocks. Tên file nằm trong directory entry, trỏ đến inode.

## Inode, Directory Và Link

Directory có thể hiểu là bảng ánh xạ tên sang inode. Vì vậy:

- Hard link là nhiều tên cùng trỏ đến một inode. File thật chỉ bị xóa khi link count về 0 và không còn process giữ file mở.
- Symbolic link là một file đặc biệt chứa path đến mục tiêu. Nếu mục tiêu bị xóa, symlink có thể trở thành dangling link.
- Xóa file đang được process mở có thể làm `df` và `du` lệch nhau vì block chỉ được giải phóng khi file descriptor cuối cùng đóng.

## File Access Methods

- Sequential access: đọc/ghi theo thứ tự, phù hợp log, stream, editor, compiler.
- Direct/random access: đọc/ghi theo offset hoặc record, quan trọng với database và VM image.
- Indexed access: dùng index để tìm record/block nhanh hơn, đổi lại cần metadata/index bổ sung.

## Allocation Methods

| Phương pháp | Cách hoạt động | Ưu điểm | Nhược điểm |
|---|---|---|---|
| Contiguous allocation | File dùng các block liền kề | Đọc tuần tự nhanh | Khó mở rộng, dễ external fragmentation |
| Linked allocation | Mỗi block trỏ đến block kế tiếp | Linh hoạt, ít cần biết trước size | Random access kém, mất pointer có thể mất chuỗi sau |
| Indexed allocation | Index block/inode giữ danh sách block | Hỗ trợ random access tốt | Tốn metadata, cần cache/index hiệu quả |
| Extent-based | Gom các range block liên tiếp thành extent | Giảm metadata cho file lớn | Vẫn cần quản lý fragmentation |

## Common Linux Filesystems

| Filesystem | Điểm mạnh | Lưu ý |
|---|---|---|
| ext4 | Ổn định, phổ biến, phù hợp general-purpose | Ít tính năng advanced hơn Btrfs/ZFS |
| XFS | Tốt cho file lớn, parallel I/O, production server | Không shrink online theo cách đơn giản như một số FS khác |
| Btrfs | Copy-on-write, snapshot, checksum, compression | Cần hiểu profile/RAID mode và maturity theo distro/use case |
| ZFS | Pool, snapshot, checksum, self-healing khi có redundancy | Licensing/module packaging trên Linux cần lưu ý |
| tmpfs | Dữ liệu nằm trong memory/swap | Mất khi reboot, phù hợp temporary runtime data |
| NFS/SMB | Network file access | Bị ảnh hưởng bởi network, lock, server availability |

## FUSE

FUSE (Filesystem in Userspace) cho phép triển khai filesystem ở user space thay vì viết kernel module. Nó hữu ích cho filesystem ảo, object storage mount, encrypted view hoặc tool tích hợp đặc biệt.

Trade-off: FUSE dễ phát triển và an toàn hơn kernel module, nhưng có thể có overhead và failure mode ở process user-space.

## Access Control

Filesystem access thường kết hợp:

- Owner/group/other permission bits.
- ACL cho quyền chi tiết hơn.
- Extended attributes cho metadata bổ sung.
- SELinux/AppArmor hoặc policy ở lớp OS.

Khi troubleshooting permission, cần kiểm tra cả path traversal permission trên thư mục cha, ownership, ACL, mount option và security policy.

## Recovery

Filesystem có thể mất consistency nếu crash khi metadata/data còn nằm trong cache. Các cơ chế phổ biến:

- `fsck`: scan metadata và sửa inconsistency. Có thể lâu với filesystem lớn.
- Journaling: ghi transaction metadata vào journal để replay/rollback nhanh hơn sau crash.
- Copy-on-write: ghi phiên bản mới thay vì overwrite trực tiếp, giúp snapshot/checksum tốt hơn ở một số filesystem.

Không chạy repair destructive khi chưa có backup hoặc snapshot phù hợp.

## Trang Liên Quan

- [Disk And Device Fundamentals](./02-disk-and-device-fundamentals.md)
- [Cache, Buffer, WAL And Journal](./05-cache-buffer-wal-journal.md)
- [Data Integrity, Checksum And Hashing](./06-data-integrity-checksum-hashing.md)
