# Manila

## Overview

Manila là OpenStack Shared File Systems service. Nếu Cinder cung cấp block volume và Swift cung cấp object storage, Manila cung cấp file share theo các giao thức như NFS hoặc CIFS/SMB thông qua backend storage phù hợp.

Manila hữu ích khi workload cần một filesystem dùng chung giữa nhiều instance hoặc cần mô hình NAS managed trong private cloud.

## Core Concepts

| Khái niệm | Ý nghĩa |
|---|---|
| Share | File share được cấp cho project/user |
| Share type | Policy/capability class cho share, tương tự volume type trong Cinder |
| Share network | Network context để backend export share tới tenant |
| Access rule | Quy tắc cho phép client truy cập share |
| Security service | Tích hợp identity như LDAP/AD/Kerberos tùy backend |

## Components

Các thành phần Manila thường gặp:

| Component | Vai trò |
|---|---|
| `manila-api` | Nhận API request |
| `manila-scheduler` | Chọn backend phù hợp cho share |
| `manila-share` | Điều khiển backend share service |
| `manila-data` | Xử lý data operation dài hoặc có thể block service khác |

Về mặt tư duy, `manila-share` có thể được xem gần giống vai trò của `nova-compute` hoặc `cinder-volume`: nó là service gần backend thực thi nhất.

## Khi Nào Dùng Manila

Dùng Manila khi:

- Nhiều VM cần mount chung một filesystem.
- Ứng dụng cần giao thức file truyền thống như NFS hoặc SMB.
- Tenant cần tự cấp phát file share theo API thay vì chờ storage admin tạo tay.
- Private cloud muốn cung cấp dịch vụ gần với AWS EFS hoặc managed NAS.

Không dùng Manila thay cho Cinder nếu workload cần block device riêng cho một VM. Không dùng Manila thay Swift nếu workload phù hợp object storage và access qua HTTP API.

## Operations Quick Reference

```bash
openstack share service list
openstack share type list
openstack share list
openstack share show <share>
openstack share access list <share>
```

Khi share không mount được:

1. Kiểm tra share status và export location.
2. Kiểm tra access rule đã allow đúng client chưa.
3. Kiểm tra network path từ VM tới backend/export network.
4. Kiểm tra security group/firewall cho NFS/SMB.
5. Kiểm tra log `manila-api`, `manila-scheduler`, `manila-share`.

## Related Pages

- [Cinder](./cinder.md)
- [Swift](./swift.md)
- [Neutron](./neutron.md)
- [OpenStack Common Commands](../../02-operations/common-commands.md)
