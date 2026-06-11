# OpenStack All-In-One Lab

## Overview

All-in-one lab là môi trường OpenStack chạy trên một VM hoặc một host để học kiến trúc, CLI, Horizon, service flow và troubleshooting cơ bản. Đây không phải blueprint production: failure domain, HA, storage durability và network isolation đều bị đơn giản hoá.

Mục tiêu của lab:

- Hiểu request đi qua Keystone, catalog, API service, scheduler/agent và backend như thế nào.
- Thực hành tạo image, flavor, network, subnet, router, security group, instance, volume và floating IP.
- Có môi trường an toàn để đọc log, kiểm service status, thử lỗi quota/network/storage.

## Chọn Công Cụ Lab

| Công cụ | Khi nên dùng | Điểm mạnh | Giới hạn |
|---|---|---|---|
| DevStack | Học API/service internals hoặc phát triển OpenStack. | Cài nhanh, bám sát upstream, dễ bật/tắt service khi dev. | Không phải deployment tool production; dễ vỡ khi OS/package thay đổi. |
| PackStack/RDO | Học lab kiểu RPM/CentOS/RHEL và mô hình answer file. | Dễ dựng all-in-one hoặc thêm compute node trong lab. | Chủ yếu phục vụ test/lab, không phải hướng production hiện đại. |
| MicroStack | Muốn lab rất nhanh trên Ubuntu/snap. | Ít bước, nhanh có Keystone/Glance/Nova/Neutron/Horizon. | Không phù hợp nếu cần đầy đủ Cinder/Swift/Heat labs hoặc debug sâu nhiều backend. |
| Kolla-Ansible AIO | Muốn gần với deployment containerized hiện đại hơn. | Có precheck/reconfigure, dễ quan sát container service, gần workflow vận hành. | Cần hiểu Docker, Ansible, network interface và version matrix. |

Trong vault này, runbook chi tiết ưu tiên Kolla-Ansible AIO vì nó gần với cách vận hành OpenStack hiện đại hơn DevStack/MicroStack.

PackStack/RDO caveats khi dùng để học:

- Dùng answer file thay vì chỉ `packstack --allinone` để còn biết service nào được bật, backend nào được dùng và password/NTP/network host đang cấu hình ra sao.
- NTP/time sync rất quan trọng; clock lệch gây lỗi Keystone token và service coordination khó hiểu.
- Một số môi trường RPM cũ có caveat với NetworkManager/SELinux; xử lý theo tài liệu đúng version thay vì tắt bừa trong production.
- Cinder/Swift lab có thể dùng loopback file để giả lập storage. Cách này chỉ phục vụ lab, không phản ánh durability/performance production.

## Lab Topology Tối Thiểu

```text
Laptop / Hypervisor host
  -> VM OpenStack AIO
      -> management/NAT NIC: SSH, API, Horizon
      -> external/provider NIC: Neutron external bridge
      -> optional extra disk: Cinder LVM backend
```

Khuyến nghị tối thiểu:

| Thành phần | Khuyến nghị |
|---|---|
| CPU | 4 vCPU trở lên; bật nested virtualization nếu muốn dùng KVM thật trong VM lab. |
| RAM | 8 GB trở lên cho lab nhỏ; nhiều service hơn cần RAM cao hơn. |
| Disk | OS disk riêng, thêm disk nếu thử Cinder LVM. |
| NIC | Ít nhất 2 NIC: management và external/provider. |
| Time sync | Bắt buộc kiểm tra vì Keystone token và service coordination nhạy với clock skew. |

## KVM Và Nested Virtualization Check

OpenStack không bị buộc vào một hypervisor duy nhất, nhưng Nova thường được học và triển khai phổ biến với KVM/libvirt. Nếu lab chạy bên trong VM, cần phân biệt:

- Host vật lý hỗ trợ VT-x/AMD-V.
- Hypervisor bên ngoài có bật nested virtualization.
- VM lab nhìn thấy `/dev/kvm` và kernel module KVM.
- Nếu không có KVM, lab có thể dùng QEMU software emulation nhưng VM sẽ chậm hơn.

Read-only checks trong VM lab:

```bash
grep -E 'vmx|svm' /proc/cpuinfo
lsmod | grep kvm
test -e /dev/kvm && echo "KVM device exists"
```

Nếu không có `vmx`/`svm` hoặc `/dev/kvm`, kiểm tra BIOS/UEFI của host vật lý và cấu hình nested virtualization của VirtualBox/VMware/KVM trước khi debug Nova.

## Flow Sau Khi Deploy

Sau khi control plane chạy, đừng tạo VM ngay. Kiểm theo thứ tự:

```bash
source <openrc-file>
openstack token issue
openstack service list
openstack endpoint list
openstack compute service list
openstack network agent list
openstack image list
```

Sau đó mới tạo resource nền:

```text
image -> flavor -> network/subnet -> router/external gateway
  -> security group/keypair -> instance -> floating IP
```

Với Cinder lab:

```text
extra disk -> PV/VG -> cinder-volume backend -> volume type
  -> volume create -> attach to server
```

## Khi Lab Lỗi

| Triệu chứng | Kiểm tra trước |
|---|---|
| CLI `401/403` | RC file, domain/project, Keystone token, time sync. |
| Horizon vào được nhưng tạo VM fail | Nova/Neutron/Cinder log theo request ID, quota, image, network. |
| Instance stuck `BUILD` | `nova-scheduler`, `nova-compute`, Placement inventory, Neutron port, Glance image. |
| Không SSH được instance | Security group, floating IP, router gateway, provider bridge, external network. |
| Volume fail | `openstack volume service list`, `cinder-volume`, backend VG/Ceph/NFS, quota. |
| Network external không hoạt động | NIC external có bị đặt IP trên host không, Neutron bridge/provider mapping, upstream route. |

## Related Pages

- [Kolla-Ansible All-In-One Lab](../02-operations/01-deployment/kolla-ansible-all-in-one-lab.md)
- [OpenStack Common Commands](../02-operations/common-commands.md)
- [OpenStack Client Debug](../04-troubleshooting/openstack-client-debug.md)
- [Nova](../01-core-fundamentals/services/nova.md)
- [Neutron](../01-core-fundamentals/services/neutron.md)
- [Cinder](../01-core-fundamentals/services/cinder.md)
