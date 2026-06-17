# AWS Identity, Security And Governance

## Overview

Nhóm này chứa IAM, AWS Organizations, policy, tagging governance, KMS, Secrets Manager, AWS Config và các pattern bảo mật thường xuất hiện trong kiến trúc AWS.

## Pages

- [IAM, Accounts, Organizations And Policy](./01-iam-accounts-organizations-policy.md)
- [Account, IAM, Security Groups And VPC Security](./02-account-iam-security-groups-and-vpc-security.md)
- [Shared Responsibility, Compliance And Threat Protection](./03-shared-responsibility-compliance-and-threat-protection.md)
- [AWS Attack Paths And Defensive Controls](./04-aws-attack-paths-and-defensive-controls.md)

## Placement Notes

- IAM và Organizations là nền tảng identity/governance.
- KMS và Secrets Manager thuộc security controls, nhưng khi đi cùng database/storage thì service note tương ứng nên link lại.
- AWS Config/CloudTrail/CloudWatch nằm ở giao điểm giữa security, observability và operations.
