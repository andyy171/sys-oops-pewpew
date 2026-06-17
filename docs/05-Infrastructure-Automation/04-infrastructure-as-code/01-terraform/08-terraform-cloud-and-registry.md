# Terraform Cloud and Registry

## Overview

Terraform Cloud, HCP Terraform và Terraform Registry nằm ở lớp cộng tác, quản trị module, policy và workflow quanh Terraform. Đây không phải kiến thức bắt buộc để chạy Terraform local, nhưng rất quan trọng khi nhiều người cùng quản lý hạ tầng production.

## Terraform Cloud Workspace

Workspace trong Terraform Cloud không giống hoàn toàn `terraform workspace` trong CLI. Trong Terraform Cloud, workspace thường đại diện cho một working directory hoặc một stack hạ tầng có state, variable, run history và workflow riêng.

Tên workspace nên có convention rõ ràng, ví dụ:

```text
network-prod
eks-staging
openstack-shared-services
```

Không nên dùng chung một workspace cho quá nhiều domain hạ tầng vì blast radius lớn và plan/apply khó review.

## Authentication

`terraform login` dùng API token từ Terraform Cloud/HCP Terraform để CLI xác thực với platform.

Không commit token vào Git. Token cá nhân nên có phạm vi quyền tối thiểu và được rotate khi cần.

## Variables Và Secure Variables

Terraform Cloud có thể lưu variable cho workspace. Với giá trị nhạy cảm như password, token, access key hoặc private endpoint, dùng chế độ sensitive/secure variable.

Sensitive variable giúp giảm rủi ro lộ trên UI/log, nhưng vẫn cần kiểm soát quyền truy cập workspace và run output.

## VCS-Driven Workflow

VCS-driven workflow liên kết workspace với GitHub, GitLab, Bitbucket hoặc hệ thống VCS khác.

Luồng phổ biến:

```text
Pull Request
  -> Terraform Cloud speculative plan
  -> Review
  -> Merge
  -> Terraform Cloud plan/apply
```

Với workspace đã chọn VCS-driven workflow, nên xem Git repo là source of truth. Không nên apply production từ CLI riêng lẻ nếu quy trình team yêu cầu mọi thay đổi đi qua VCS.

## Automated Plan And Apply Workflow

Khi tự động hóa Terraform, tách rõ speculative plan, approved plan và apply:

```text
pull request
-> fmt/validate/security scan
-> speculative plan
-> human review
-> merge
-> plan chính thức
-> approval/policy
-> apply
-> post-apply verification
```

Plan dùng để review không nên bị thay bằng một plan khác mà không ai đọc. Nếu pipeline lưu `tfplan`, artifact đó phải có access control vì có thể chứa topology hoặc value nhạy cảm. Với Terraform Cloud/HCP Terraform, run history, variable set, policy result và workspace permission là một phần của audit trail.

Các guardrail vận hành:

- không chạy nhiều apply song song vào cùng workspace/state;
- dùng lock và timeout hợp lý;
- tách workspace theo domain/environment để blast radius nhỏ;
- apply production cần approval rõ ràng, đặc biệt khi plan có destroy/replace;
- post-apply phải có bước verify ngoài Terraform, ví dụ health check, dashboard hoặc smoke test.

## Private Registry

Private registry lưu và version module nội bộ để nhiều team dùng chung. Đây là cách tốt hơn so với copy module giữa nhiều repo.

Một module publish tốt nên có:

- `main.tf`
- `variables.tf`
- `outputs.tf`
- `README.md`
- Ví dụ sử dụng.
- Version rõ ràng.

Về cấu trúc module trước khi publish, xem thêm: [Project Structure and Conventions](./06-project-structure-and-conventions.md).

## Public Terraform Registry

Terraform Registry là nơi phân phối provider, module, policy và run task. Khi publish module public, repository thường cần theo format:

```text
terraform-<PROVIDER>-<NAME>
```

Ví dụ:

```text
terraform-aws-vpc
terraform-google-network
```

Module nên dùng semantic versioning:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Documentation tối thiểu nên có mô tả, hướng dẫn sử dụng, input, output và ví dụ.

## Sentinel Policy

Sentinel là policy-as-code trong hệ sinh thái Terraform. Policy thường chạy sau plan và trước apply để kiểm tra thay đổi có vi phạm rule không.

Các mức policy thường gặp:

- Advisory: policy fail chỉ cảnh báo.
- Soft mandatory: fail nhưng có thể override nếu có quyền.
- Hard mandatory: bắt buộc pass, không cho override.

Ví dụ rule có thể kiểm tra:

- Không tạo public S3 bucket.
- Không mở security group `0.0.0.0/0` vào SSH.
- Bắt buộc tag cost center.
- Không cho destroy database nếu chưa có approval.

## Agents

Terraform Cloud Agent cho phép Terraform Cloud điều phối plan/apply nhưng thực thi trong network nội bộ. Mô hình này hữu ích khi hạ tầng không expose API ra Internet hoặc cần truy cập private endpoint.

Agent thường:

- Nhận job plan/apply từ Terraform Cloud.
- Chạy Terraform trong môi trường nội bộ.
- Truy cập provider API/private network theo quyền được cấp.
- Trả kết quả run về Terraform Cloud.

## Best Practices

- Tách workspace theo domain và environment.
- Dùng VCS-driven workflow cho production.
- Dùng private registry cho module dùng chung.
- Version module rõ ràng, tránh dùng branch mutable cho production.
- Giới hạn quyền token và workspace.
- Dùng policy-as-code cho guardrail quan trọng, nhưng không thay thế review của con người.
