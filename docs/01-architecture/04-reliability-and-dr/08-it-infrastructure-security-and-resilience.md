# IT Infrastructure Security And Resilience

## Overview

Infrastructure resilience là khả năng hệ thống tiếp tục cung cấp dịch vụ ở mức chấp nhận được khi có lỗi kỹ thuật, lỗi vận hành, sự cố bảo mật hoặc mất một phần hạ tầng. Security và resilience không tách rời: một kiến trúc không chống chịu được tấn công hoặc thao tác sai thì cũng không thật sự reliable.

## Layered Mental Model

```text
facility / power / cooling
  -> hardware / virtualization
  -> network
  -> storage / backup
  -> platform / cloud services
  -> identity / access / security controls
  -> operations / support / incident response
```

Mỗi lớp có failure mode riêng. Thiết kế resilience cần tránh chỉ tập trung vào software HA mà bỏ qua facility, power, cooling, network, backup hoặc support process.

## Cloud And Data Center Service Model

Khi đánh giá cloud hoặc data center service, cần tách:

- Service model: IaaS, PaaS, SaaS, managed service, support service.
- Deployment model: private, public, hybrid, edge.
- Responsibility boundary: provider chịu trách nhiệm phần nào, team vận hành chịu trách nhiệm phần nào.
- Operational dependency: identity, network, DNS, backup, monitoring, support channel.

Một service "managed" không loại bỏ trách nhiệm kiến trúc của người dùng. Nó chỉ chuyển một phần vận hành sang provider.

## Facility Resilience

Các yếu tố facility ảnh hưởng trực tiếp availability:

- physical space, rack layout, cabling
- power feed, UPS, generator, PDU
- cooling, airflow, temperature/humidity
- physical access control
- fire detection/suppression
- spare capacity và maintenance window

Với hệ thống critical, cần biết dependency thật: hai server chạy khác rack nhưng có cùng PDU hoặc cùng uplink switch vẫn có chung failure domain.

## Compute, Storage And Network

Compute resilience cần capacity dự phòng, host failure handling và virtualization/cluster policy rõ ràng.

Storage resilience cần phân biệt:

- replication vs backup
- snapshot vs restore point
- durability vs availability
- local failure domain vs site failure domain

Network resilience cần kiểm tra:

- redundant uplink/switch/router/firewall
- routing/failover convergence
- DNS dependency
- DDoS/security control
- segmentation và blast radius

## Security By Design

Security by design nghĩa là control được đặt trong kiến trúc từ đầu, không chỉ thêm firewall hoặc agent sau cùng.

Các nguyên tắc:

- least privilege cho user, service account và automation
- segmentation theo trust boundary
- secure defaults và hardening baseline
- audit log ở identity, network, OS, platform và application
- backup/restore được bảo vệ khỏi cùng credential compromise
- incident response workflow có owner và evidence retention

## DR Và Support Process

DR không chỉ là replication kỹ thuật. Nó cần:

- RTO/RPO theo từng service
- runbook failover/failback
- restore test định kỳ
- communication path khi incident
- help desk/service desk route rõ ràng
- post-incident review và corrective action

Support service cũng là một phần resilience. Nếu không biết ai nhận alert, ai có quyền thay đổi, ai liên hệ provider và ai quyết định failover, hệ thống sẽ chậm phục hồi dù kỹ thuật có HA.

## Design Checklist

- Xác định business-critical service và dependency map.
- Vẽ failure domain: rack, power, network, storage, identity, region/site.
- Gắn RTO/RPO cho từng workload.
- Tách HA, DR và backup thành ba capability riêng.
- Kiểm tra security control có làm tăng single point of failure không.
- Diễn tập restore/failover, không chỉ đọc tài liệu.
- Đưa monitoring, alerting và support escalation vào thiết kế ban đầu.

## Trang Liên Quan

- [HA And Failover Patterns](./01-ha-and-failover-patterns.md)
- [Replication Strategies](./05-replication-strategies.md)
- [RTO/RPO Design](./07-rto-rpo-design.md)
- [Data Security And Confidential Computing](../03-patterns/04-data-security-and-confidential-computing.md)
- [Security And Hardening](../../05-infrastructure-automation/02-security-and-hardening/overview.md)
