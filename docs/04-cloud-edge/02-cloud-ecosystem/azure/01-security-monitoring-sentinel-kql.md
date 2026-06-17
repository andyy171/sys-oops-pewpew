# Azure Security Monitoring And Sentinel KQL

## Overview

Microsoft Sentinel dùng KQL để truy vấn log bảo mật và vận hành trong Azure. File thô `_inbox/Azure Sentinel KQL Queries.pdf` là một bộ nhiều use case KQL cho Azure AD, Key Vault, AKS, SQL, API Management, Functions, DevOps, Container Registry và các dịch vụ Azure khác. Thay vì chép hàng trăm query rời rạc, note này gom thành mental model để tự viết và review query.

## KQL Mental Model

Một query điều tra thường đi theo flow:

```text
source table -> time window -> filter event/action -> summarize -> join/enrich -> project useful fields -> order by time/risk
```

Ví dụ khung chung:

```kusto
AzureActivity
| where TimeGenerated > ago(24h)
| where ActivityStatusValue in ("Failure", "Failed")
| summarize Count=count() by Caller, OperationNameValue, ResourceGroup, bin(TimeGenerated, 1h)
| order by Count desc
```

## Common Data Sources

| Log source | Dùng để phát hiện |
|---|---|
| `SigninLogs` | sign-in bất thường, MFA failure, location lạ |
| `AuditLogs` | thay đổi user, group, role, app consent |
| `AzureActivity` | thay đổi resource, delete/update operation, policy event |
| `SecurityAlert` | alert từ Defender/Sentinel connector |
| `AzureDiagnostics` | log dịch vụ như Key Vault, Application Gateway, Firewall, AKS tùy cấu hình |
| `ContainerLog` / `Kube*` | workload/container/Kubernetes behavior |

Tên table có thể khác tùy connector và Diagnostic Settings. Khi copy query từ nguồn ngoài, luôn kiểm tra table/field thật trong workspace trước.

## Use Case Groups

| Nhóm | Ví dụ tín hiệu |
|---|---|
| Identity | sign-in thất bại nhiều lần, impossible travel, admin role assignment, consent grant bất thường |
| Key Vault | secret read/list thất bại, secret access spike, policy thay đổi |
| Compute | VM start/stop/delete, extension thay đổi, managed identity thay đổi |
| Kubernetes/Container | AKS operation failure, ACR push/pull bất thường, image hoặc deployment thay đổi |
| Database | SQL Database operation lạ, login failure spike, firewall rule thay đổi |
| Network/Edge | Front Door, API Management, CDN, DNS hoặc public endpoint thay đổi |
| DevOps | pipeline modification, service connection thay đổi, repo access bất thường |
| Data | Data Lake, Storage, Data Factory pipeline run bất thường |

## Query Patterns

### Failed Operation Spike

```kusto
AzureActivity
| where TimeGenerated > ago(24h)
| where ActivityStatusValue has_any ("Failure", "Failed")
| summarize Failures=count() by Caller, OperationNameValue, bin(TimeGenerated, 30m)
| where Failures > 5
| order by Failures desc
```

### Sensitive Resource Change

```kusto
AzureActivity
| where TimeGenerated > ago(7d)
| where OperationNameValue has_any ("Delete", "Write", "Update", "Regenerate")
| where ResourceProviderValue has_any ("MICROSOFT.KEYVAULT", "MICROSOFT.NETWORK", "MICROSOFT.CONTAINERREGISTRY")
| project TimeGenerated, Caller, ResourceProviderValue, OperationNameValue, ResourceGroup, Resource
| order by TimeGenerated desc
```

### Unusual Admin Activity

```kusto
AuditLogs
| where TimeGenerated > ago(7d)
| where OperationName has_any ("Add member to role", "Add app role assignment", "Consent to application")
| project TimeGenerated, OperationName, Result, InitiatedBy, TargetResources
| order by TimeGenerated desc
```

### Suspicious Sign-In Review

```kusto
SigninLogs
| where TimeGenerated > ago(24h)
| where ResultType != 0 or ConditionalAccessStatus in ("failure", "notApplied")
| summarize Attempts=count(), Locations=make_set(Location), Apps=make_set(AppDisplayName) by UserPrincipalName, IPAddress
| order by Attempts desc
```

## Review Checklist

- Query có giới hạn thời gian rõ bằng `TimeGenerated > ago(...)`.
- Không dùng threshold cứng cho production khi chưa biết baseline.
- `summarize` theo đúng entity điều tra: user, IP, resource, operation hoặc workload.
- Giữ lại field đủ để triage: time, actor, action, resource, status, IP/location.
- Với alert, cần mapping entity để Sentinel incident dễ điều tra.
- Với query từ internet/PDF, kiểm tra lại schema workspace trước khi đưa vào scheduled analytics rule.

## Related Pages

- [Azure Overview](./overview.md)
- [Security And Hardening Overview](../../../05-infrastructure-automation/02-security-and-hardening/overview.md)
