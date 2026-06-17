# Cloud Edge

Domain này chứa kiến thức về cloud fundamentals, cloud provider, private cloud, edge/cloud architecture và các service map theo vendor.

## Chứa Gì

- Cloud fundamentals: region/AZ, shared responsibility, IAM ở mức cloud, networking, billing/cost và service model.
- Cloud provider-specific notes: AWS, Azure, GCP, Huawei Cloud, Oracle Cloud.
- OpenStack như private cloud/platform layer: Keystone, Nova, Neutron, Cinder, Glance, Octavia, Trove, Swift, Heat và operations.
- Provider operations, migration, troubleshooting và architecture pattern gắn với service cụ thể.
- Edge/cloud architecture khi primary object là provider platform hoặc hybrid/private cloud design.

## Không Chứa Gì

- Ceph/RBD/RGW backend internals, disk, filesystem hoặc storage engine; đặt ở [Core Infrastructure](../02-core-infrastructure/overview.md).
- Kubernetes object và runtime behavior thuần Kubernetes; đặt ở [Compute And Orchestration](../03-compute-and-orchestration/overview.md).
- Terraform module/pipeline/GitOps generic; đặt ở [Infrastructure Automation](../05-infrastructure-automation/overview.md), chỉ link sang đây khi note là service-specific.

## Learning Path

- [Cloud Fundamentals](./01-cloud-fundamentals/overview.md)
- [Cloud Computing Core Mechanisms](./01-cloud-fundamentals/01-cloud-computing-core-mechanisms.md)
- [Cloud Ecosystem](./02-cloud-ecosystem/overview.md)
- [AWS](./02-cloud-ecosystem/aws/_index.md)
- [OpenStack](./02-cloud-ecosystem/openstack/overview.md)
- [Azure](./02-cloud-ecosystem/azure/overview.md)
- [GCP](./02-cloud-ecosystem/gcp/overview.md)

## Ghi Chú Refactor

- AWS hiện còn một số folder numbering trùng do có cả cấu trúc cũ và cấu trúc mới. Chưa nên xóa/rename ngay nếu chưa kiểm tra link; bước tiếp theo nên là lập mapping cũ -> mới rồi merge từng cụm.
- OpenStack nên phát triển theo hướng thực chiến hơn: fundamentals, services, operations, deployment, troubleshooting, integration, labs và certification.
- Azure/GCP/Oracle Cloud có thể giữ skeleton mỏng nhưng nên có overview thống nhất để mở rộng sau này.
