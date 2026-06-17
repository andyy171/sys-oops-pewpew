# Security And Hardening

Khu vực này gom các note về security fundamentals, access control, OS/network hardening, container/cloud security, security operations và incident response. Khi nhập note thô mới, ưu tiên tách rõ ba câu hỏi: tài sản nào cần bảo vệ, ai được truy cập, và bằng cơ chế kiểm soát/audit nào.

## Suggested Reading

- [Privacy, Compliance, Cryptography And Data Protection](./00-fundamentals/02-privacy-compliance-cryptography-and-data-protection.md)
- [Threat Actors, Malware And Attack Patterns](./00-fundamentals/03-threat-actors-malware-and-attack-patterns.md)
- [Threat Modeling, Vulnerability Management And Application Security](./00-fundamentals/04-threat-modeling-vulnerability-management-and-application-security.md)
- [Attack Surface Management](./00-fundamentals/05-attack-surface-management.md)
- [Attack Surface Categories And Exposure Patterns](./00-fundamentals/06-attack-surface-categories-and-exposure-patterns.md)
- [Attack Surface Risk Management And Prioritization](./00-fundamentals/07-attack-surface-risk-management-and-prioritization.md)
- [Asset Inventory, Classification, And Discovery For ASM](./00-fundamentals/08-asset-inventory-classification-and-discovery-for-asm.md)
- [Automated Asset Discovery And Visibility Patterns](./00-fundamentals/09-automated-asset-discovery-and-visibility-patterns.md)
- [Asset Prioritization And Crown Jewel Analysis](./00-fundamentals/10-asset-prioritization-and-crown-jewel-analysis.md)
- [Attack Surface Analysis And Mapping](./00-fundamentals/11-attack-surface-analysis-and-mapping.md)
- [ASM Remediation, Validation And Reporting](./00-fundamentals/12-asm-remediation-validation-and-reporting.md)
- [Attack Surface Minimization Strategies](./00-fundamentals/13-attack-surface-minimization-strategies.md)
- [Continuous Monitoring And Adaptive ASM](./00-fundamentals/14-continuous-monitoring-and-adaptive-asm.md)
- [Emerging ASM Risks: AI, Quantum And Edge](./00-fundamentals/15-emerging-asm-risks-ai-quantum-and-edge.md)
- [Identity, Authentication And Authorization](./01-access-control/01-identity-authentication-authorization.md)
- [Linux Hardening Baseline](./02-os-and-network-security/linux-hardening-baseline.md)
- [Teleport HA Access Pattern](./01-access-control/teleport-ha-access.md)
- [SSH security, 2FA, bastion host](./01-access-control/SSH%20security,%202FA,%20bastion%20host.md)
- [PAM, auditd, fail2ban](./01-access-control/PAM,%20auditd,%20fail2ban.md)
- [Key rotation](./01-access-control/Key%20rotation.md)
- [Incident Response Overview](./incident-response-overview.md)
- [Security Monitoring, SIEM And IoC](./04-security-operations/01-security-monitoring-siem-ioc-and-detection.md)
- [Network Monitoring And Packet Analysis](./02-os-and-network-security/network-monitoring-and-packet-analysis.md)
- [Firewall SSL Inspection And Certificates](./02-os-and-network-security/02-firewall-ssl-inspection-and-certificates.md)
- [IDS/IPS](./02-os-and-network-security/IDS-IPS%20%28Snort,%20Suricata%29.md)

## Domain Map

```text
02-security-and-hardening/
├── 00-fundamentals/
├── 01-access-control/
├── 02-os-and-network-security/
├── 03-container-and-cloud-security/
├── 04-security-operations/
└── incident-response-overview.md
```

## Operating Principles

- Không phát tán long-lived secrets nếu có thể dùng certificate/token ngắn hạn.
- Dùng least privilege cho user, service account, CI runner và automation.
- Bật audit log ở lớp identity, OS, cloud API và workload quan trọng.
- Với thay đổi production, luôn có rollback và cách verify quyền truy cập sau khi đổi policy.
