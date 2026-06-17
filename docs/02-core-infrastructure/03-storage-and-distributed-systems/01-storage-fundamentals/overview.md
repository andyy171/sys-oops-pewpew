# Storage Fundamentals

Folder này chứa nền tảng storage trước khi đi vào filesystem, protocol, distributed storage hoặc storage system cụ thể như Ceph, MinIO, Longhorn và vSAN.

## Suggested Reading

- [Storage Models: Block, File, Object](./01-storage-models-block-file-object.md)
- [Disk And Device Fundamentals](./02-disk-and-device-fundamentals.md)
- [RAID, LVM And Multipath](./03-raid-lvm-multipath.md)
- [Filesystem Basics](./04-filesystem-basics.md)
- [Cache, Buffer, WAL And Journal](./05-cache-buffer-wal-journal.md)
- [Data Integrity, Checksum And Hashing](./06-data-integrity-checksum-hashing.md)
- [Backup, Snapshot And Replication](./07-backup-snapshot-replication.md)
- [Storage Performance: IOPS, Throughput, Latency](./08-storage-performance-iops-throughput-latency.md)

## Placement Notes

- Đặt ở đây khi note giải thích khái niệm storage chung, chưa phụ thuộc vendor/tool cụ thể.
- Nếu note nói về NFS/iSCSI/NVMe-oF/S3 protocol, đặt ở `02-storage-protocols-and-access`.
- Nếu note nói về Ceph/MinIO/Longhorn/vSAN/Curve, đặt ở `05-storage-systems`.
- Cấu trúc cũ đã được hợp nhất vào các note canonical trong folder này; không tạo lại bản trùng nếu kiến thức đã có ở các trang trên.
