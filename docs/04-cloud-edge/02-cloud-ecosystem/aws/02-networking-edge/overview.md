# AWS Networking And Edge

## Overview

Nhóm này chứa VPC, subnet, route table, Internet Gateway, NAT Gateway, VPC endpoint, hybrid connectivity, Route 53, CloudFront và global traffic design.

## Pages

- [VPC, Subnets, Routing And Endpoints](./01-vpc-subnets-routing-endpoints.md)
- [Route 53, CloudFront And Global Traffic](./02-route53-cloudfront-global-traffic.md)
- [VPC Private Subnets, NAT And Endpoints](./03-vpc-private-subnets-nat-and-endpoints.md)

## Mental Model

- VPC là network boundary cấp Region trong một account.
- Subnet gắn với một AZ.
- Route table quyết định traffic đi đâu.
- Security Group stateful; Network ACL stateless.
- VPC Endpoint giúp private subnet gọi AWS service mà không cần public internet.
- Route 53 và CloudFront là lớp edge/global để tối ưu latency, availability và distribution.
