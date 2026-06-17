# Core Infrastructure

Domain này chứa tầng nền thấp của hạ tầng: Linux, network, storage/distributed systems, database systems, hardware và bare metal operations.

## Chứa Gì

- Host operating system, filesystem, process, package, shell, logs và Linux troubleshooting.
- Network foundation, Ethernet switching, IP routing, subnetting, protocol, DNS, firewall và network troubleshooting.
- Storage model, block/file/object access, filesystem, distributed storage, Ceph, MinIO, Longhorn, vSAN và storage operations.
- Database engine concepts, PostgreSQL/MySQL/MongoDB/Redis, replication, backup/restore, query performance và database operations.
- Server hardware, disk/NIC/firmware, datacenter basics, OS installation checklist và bare metal runbook.
- Windows Server ở mức OS/domain operations như AD, Group Policy, PowerShell và services.

## Không Chứa Gì

- Kubernetes object, scheduler, controller, CNI/CSI và container orchestration; đặt ở [Compute And Orchestration](../03-compute-and-orchestration/overview.md).
- Cloud provider service như EC2, S3, VPC, Keystone, Nova, Cinder; đặt ở [Cloud Edge](../04-cloud-edge/overview.md).
- CI/CD, Terraform, observability pipeline và security program ở tầng tool/process; đặt ở [Infrastructure Automation](../05-infrastructure-automation/overview.md).

## Khi Tạo Note Ở Đây

- Đặt note ở đây khi primary object là host, network device/protocol, disk/storage backend, database engine hoặc hardware.
- Với troubleshooting, ưu tiên một runbook riêng nếu note có triệu chứng, check, log và bước xử lý rõ ràng.
- Với cloud-backed storage/database, ghi phần engine/backend ở đây và link sang cloud provider note nếu có service-specific behavior.

## Learning Path

- [Linux Operations](./01-linux/overview.md)
- [Network](./02-network/Overview.md)
- [Storage And Distributed Systems](./03-storage-and-distributed-systems/overview.md)
- [Database Systems](./04-database-systems/overview.md)
- [Hardware And Bare Metal](./05-hardware-and-baremetal/overview.md)
- [Windows Server](./06-windows-server/overview.md)

## Ghi Chú Refactor

- `02-network` là ưu tiên dọn tiếp theo: gom file lẻ vào foundations, switching, routing/subnetting, protocols/services, security/firewall và tools/troubleshooting.
- Storage fundamentals đã được hợp nhất vào cấu trúc mới; ưu tiên cập nhật các note canonical thay vì tạo lại cấu trúc cũ.
- PostgreSQL nên có skeleton riêng trong relational databases vì đây là engine vận hành phổ biến và cần note backup, replication, performance, locking.
