# OpenStack Security

Phần này gom các ghi chú về security engineering, configuration protection và defensive review cho OpenStack. Nội dung ở đây bổ sung cho deployment/operations, không thay thế các checklist hardening chi tiết theo từng môi trường.

## Reading Order

1. [Secure Development Và Configuration Review](./01-secure-development-and-configuration-review.md)

## Khi Review OpenStack Security Cần Nhìn Theo Boundary

- Dashboard/API: Horizon, custom portal, API endpoint, redirect, XSS, CSRF và session handling.
- Identity: Keystone token, service catalog, role assignment, policy và trust giữa services.
- Network: Neutron isolation, provider network, security group, metadata access và router behavior.
- Storage: Cinder, Glance, Swift, backend như Ceph/RBD và quyền truy cập dữ liệu.
- Compute: Nova, libvirt/qemu, image handling, metadata và tenant isolation.
- Config/secrets: service config, password file, TLS key, Ceph keyring, logs và troubleshooting bundle.

## Trang Liên Quan

- [OpenStack API And Automation Workflow](../02-operations/api-and-automation-workflow.md)
- [OpenStack Operations](../02-operations/operations.md)
- [Keystone](../01-core-fundamentals/services/keystone.md)
- [Horizon](../01-core-fundamentals/services/horizon.md)
- [Neutron](../01-core-fundamentals/services/neutron.md)
- [Cinder](../01-core-fundamentals/services/cinder.md)
- [Glance](../01-core-fundamentals/services/glance.md)
