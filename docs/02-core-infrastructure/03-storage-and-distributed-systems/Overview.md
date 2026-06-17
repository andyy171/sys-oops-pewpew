# Storage And Distributed Systems

Domain này gom kiến thức về storage nền tảng, filesystem, RAID, replication, distributed storage và Ceph.

## Suggested Reading

- [Storage Fundamentals](./01-storage-fundamentals/overview.md)
- [Ceph Architecture Overview](./02-ceph-storage/01-foundations/01-architecture-overview.md)
- [Ceph Core Concepts](./02-ceph-storage/01-foundations/02-core-concepts.md)
- [Ceph Service Overview](./02-ceph-storage/02-services/00-service-overview.md)
- [Ceph Common Commands](./02-ceph-storage/03-operations/ceph-common-commands.md)

## Ghi Chú Tổ Chức

- Dùng `01-storage-fundamentals/` cho kiến thức storage chung: disk, filesystem, RAID, backup, replication và các khái niệm nền.
- Dùng `02-ceph-storage/` cho Ceph: kiến trúc RADOS, MON/MGR/OSD/MDS/RGW, data placement, operations, troubleshooting và lab.
- Các note vận hành production nên tách rõ giữa thao tác đọc/kiểm tra, thao tác có rủi ro, rollback và bước xác minh sau thay đổi.
