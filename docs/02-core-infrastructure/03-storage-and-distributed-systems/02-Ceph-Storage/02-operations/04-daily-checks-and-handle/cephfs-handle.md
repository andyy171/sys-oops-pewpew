title : Làm việc với CephFS


# Làm việc với MDS (CephFS)
```bash
ceph fs ls

name: cephfs, metadata pool: cephfs_metadata, data pools: [cephfs_data ]

# Hiển thị trạng thái của mọi thành phần của CephFS
ceph fs status
#Example
cephfs - 0 clients <<-- Containers or hosts attached to cephfs are represented here
======
+------+--------+-----------+---------------+-------+-------+
| Rank | State  |    MDS    |    Activity   |  dns  |  inos |
+------+--------+-----------+---------------+-------+-------+
|  0   | active | ceph-2    | Reqs:    0 /s |  10   |   13  |   <<-- Active server
+------+--------+-----------+---------------+-------+-------+
+-----------------+----------+-------+-------+
|       Pool      |   type   |  used | avail |
+-----------------+----------+-------+-------+
| cephfs_metadata | metadata | 1536k | 13.1G |
|   cephfs_data   |   data   |   0   | 13.1G |  <<-- Where files get stored
+-----------------+----------+-------+-------+
+-------------+
| Standby MDS |
+-------------+
|   ceph-1    |
|   ceph-3    |
+-------------+
MDS version: ceph version 14.2.0-300-gacd2f2b9e1 (acd2f2b9e196222b0350b3b59af9981f91706c7f) nautilus (stable)

```