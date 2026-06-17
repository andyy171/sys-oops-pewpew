# Storage Systems

Folder này chứa các storage system cụ thể sau khi đã nắm storage fundamentals, protocol và distributed-system concepts.

## Suggested Reading

- [Ceph](./01-ceph/overview.md)
- [MinIO](./02-minio/overview.md)
- [Longhorn](./03-longhorn/overview.md)
- [vSAN](./04-vsan/overview.md)
- [Curve](./05-curve/overview.md)
- [GlusterFS](./06-glusterfs/overview.md)
- [Ceph vs MinIO](./comparison/02-ceph-vs-minio.md)

## Placement Notes

- Đặt note vendor/system-specific ở đây khi trọng tâm là Ceph, MinIO, Longhorn, vSAN, Curve hoặc hệ storage cụ thể.
- Nếu note chỉ giải thích block/file/object, RAID, filesystem, backup hoặc performance chung, đặt ở `../01-storage-fundamentals/`.
- Nếu note chủ yếu là protocol như NFS, SMB, iSCSI, NVMe-oF hoặc S3 API ở mức protocol, đặt ở `../02-storage-protocols-and-access/` nếu section đó có canonical note phù hợp.
