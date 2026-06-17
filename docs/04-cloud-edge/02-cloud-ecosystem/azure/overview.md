# Azure Overview

## Azure Resource Hierarchy

Azure tổ chức resource theo nhiều lớp để quản lý access, policy, billing và governance.

```text
Management Group
└── Child Management Group
    └── Subscription
        └── Resource Group
            └── Resources
```

## Các Lớp Chính

| Layer | Vai trò | Ghi chú vận hành |
|---|---|---|
| Management Group | Cấp cao nhất để tổ chức nhiều subscription | Dùng để áp policy, RBAC và governance ở phạm vi tổ chức |
| Child Management Group | Nhóm con theo department, team hoặc business unit | Kế thừa policy và permission từ parent |
| Subscription | Boundary cho billing, quota và access | Nên tách theo môi trường, team hoặc workload quan trọng |
| Resource Group | Logical container cho resource liên quan | Resource trong cùng RG thường được quản lý, deploy và xóa cùng nhau |
| Resource | Dịch vụ Azure thật như VM, Storage Account, SQL Database, VNet, Load Balancer | Đây là đối tượng tiêu thụ quota/chi phí và cần tagging/governance |

## Mental Model

Từ trên xuống dưới, scope nhỏ dần và quyền kiểm soát cụ thể hơn:

```text
Organization governance -> Billing/access boundary -> Application/resource lifecycle
```

Ví dụ:

- Management Group áp baseline policy cho toàn công ty.
- Subscription tách `dev`, `staging`, `prod` hoặc từng business unit.
- Resource Group gom tài nguyên của một ứng dụng như VM, VNet, Storage Account, Load Balancer và Key Vault.

## Best Practices

- Dùng management group cho governance cấp tổ chức, không cho từng workload nhỏ.
- Tách subscription khi cần boundary rõ về billing, quota, risk hoặc permission.
- Đặt Resource Group theo vòng đời deploy/xóa của ứng dụng.
- Dùng tag để theo dõi owner, environment, cost center và workload.
- Không nhầm Resource Group với security boundary tuyệt đối; access vẫn phải quản lý bằng RBAC và policy.

## Related Pages

- [Azure Security Monitoring And Sentinel KQL](./01-security-monitoring-sentinel-kql.md)
- [Cloud Ecosystem Overview](../overview.md)
- [Cloud Fundamentals](../../01-cloud-fundamentals/overview.md)
