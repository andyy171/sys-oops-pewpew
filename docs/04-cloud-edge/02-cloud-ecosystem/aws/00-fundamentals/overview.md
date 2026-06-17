# AWS Fundamentals

## Overview

Nhóm này chứa các khái niệm nền trước khi đi vào từng service AWS: cloud service model, AWS Global Infrastructure, Region/AZ/Edge Location, resilience scope và shared responsibility.

## Pages

- [Cloud, Global Infrastructure And Resilience](./01-cloud-global-infrastructure-and-resilience.md)
- [AWS Operating Model And Service Scope](./02-aws-operating-model-and-service-scope.md)
- [AWS Interview Service Map](./03-aws-interview-service-map.md)

## Mental Model

- Region là fault domain địa lý lớn.
- Availability Zone là fault domain trong một Region.
- Edge Location phục vụ phân phối nội dung, DNS, acceleration hoặc các tính năng edge khác tùy dịch vụ.
- Một số service có phạm vi global, một số resilient trong Region, một số gắn với AZ.
- Khi thiết kế kiến trúc AWS, luôn hỏi: service này sống ở global, regional hay AZ scope?
