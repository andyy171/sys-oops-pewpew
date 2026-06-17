# Terraform Security, CI/CD and Production Practices

## Secret Trong Terraform

Không hardcode secret trong `.tf`:

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}
```

Nhưng cần nhớ: `sensitive = true` chỉ ẩn output CLI. Giá trị vẫn có thể nằm trong state. Vì vậy state phải được bảo vệ như dữ liệu nhạy cảm.

Góc nhìn kỹ thuật về state nằm ở [State, Backend and Workspace](./02-state-backend-and-workspace.md). File này tập trung vào cách biến hiểu biết đó thành quy trình bảo mật và CI/CD.

## Bảo Vệ State

State phải được bảo vệ bằng:

- Remote backend có encryption.
- IAM phân quyền đọc và ghi state rõ ràng.
- Không commit state vào Git.
- Không để state artifact public.
- Bật locking.
- Backup state có kiểm soát.

## Pin Terraform Và Provider Version

Trong team, nên pin Terraform version:

```hcl
terraform {
  required_version = ">= 1.6.0, < 2.0.0"
}
```

Không để provider tự nhảy major version ngoài kiểm soát:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

## CI/CD Với Terraform

Terraform nên chạy qua pipeline để có kiểm soát:

```text
Pull Request
  -> terraform fmt -check
  -> terraform validate
  -> terraform plan
  -> review plan
  -> approval
  -> terraform apply
```

Một pipeline tối thiểu nên có:

- Format check.
- Validate.
- Security scan nếu có.
- Plan cho pull request.
- Manual approval trước apply production.
- Lock backend.
- Lưu artifact plan/log theo chính sách bảo mật.

## Không Để Credential Trong Code

Credential cloud không được hardcode trong `.tf`. Nên dùng:

- OIDC từ CI/CD sang cloud.
- Secret manager của CI/CD.
- Vault hoặc workload identity.
- Role tạm thời thay vì access key dài hạn.
- AWS IAM role hoặc Azure Managed Identity khi chạy trong môi trường hỗ trợ identity native.

## Provider Authentication Guardrails

Provider authentication nên đi qua cơ chế identity chuẩn của từng môi trường thay vì hardcode credential trong HCL. Với production, ưu tiên:

- role tạm thời hoặc workload identity/OIDC từ CI/CD sang cloud;
- profile/role được cấp theo environment, không dùng chung credential giữa dev và production;
- secret manager hoặc Vault khi bắt buộc cần token/password;
- biến môi trường chỉ dùng trong session/pipeline được kiểm soát, không ghi vào shell history hoặc artifact;
- phân quyền provider theo least privilege, tách quyền plan/read với quyền apply/write khi workflow cho phép.

Các appendix authentication trong source nhắc nhiều tới AWS, Azure và GCP. Điểm reusable cần giữ là cùng một mental model: Terraform chỉ nên nhận credential đủ quyền cho scope đang quản lý, credential phải rotate được, và pipeline log/plan/state phải được xem là nơi có thể rò thông tin nhạy cảm.

## tfvars Và Environment Variable

`terraform.tfvars` thường chứa input theo môi trường. Nếu file có dữ liệu nhạy cảm hoặc khác nhau theo user, không commit vào Git.

Ví dụ input không nhạy cảm:

```hcl
region = "ap-southeast-1"
```

Với biến môi trường, Terraform nhận input qua prefix `TF_VAR_`:

```bash
export TF_VAR_region="ap-southeast-1"
terraform plan
```

Không đặt access key dài hạn trong shell history hoặc file `.env` không được kiểm soát.

Góc nhìn HCL/input variable nằm ở [HCL Language, Types and Expressions](./07-hcl-language-types-and-expressions.md). Ở đây cần nhớ thêm lớp vận hành: input có thể đúng cú pháp nhưng vẫn sai nếu chứa secret không được quản lý an toàn.

## Review Plan Như Review Thay Đổi Production

Plan có thể cho thấy destroy hoặc replace resource. Với production, reviewer phải đọc kỹ:

- Resource nào bị destroy.
- Resource nào bị replace.
- Có thay đổi network hoặc security không.
- Có thay đổi database hoặc storage không.
- Có thay đổi IAM hoặc policy không.

Ký hiệu `-/+` là replace. Replace có thể gây downtime hoặc mất dữ liệu tùy resource.

Khi thấy replace, cần hỏi:

- Vì sao resource bị replace?
- Attribute nào force replacement?
- Có cách update in-place không?
- Có cần maintenance window không?
- Có backup không?

## Sai Lầm Hay Gặp

- Commit state lên Git.
- Hardcode secret trong `.tf`.
- Không pin provider version.
- Apply không đọc plan.
- Dùng workspace production quá tùy tiện.
- Gom toàn bộ hạ tầng vào một state khổng lồ.
- Lạm dụng `ignore_changes` để che drift.
- Tự sửa state file bằng tay.
- Không bật locking cho remote state.
- Module hóa quá sớm hoặc quá phức tạp.

## Tư Duy Vận Hành Production

Terraform không chỉ là công cụ tạo resource. Nó là một phần của quy trình thay đổi hạ tầng.

```text
Code change
  -> Review
  -> Plan
  -> Approval
  -> Apply
  -> Verify
  -> Monitor
```

Câu hỏi quan trọng nhất trước khi apply:

```text
Plan này có đang thay đổi đúng thứ mình muốn, trong đúng phạm vi mình chấp nhận không?
```

## Secrets Có Thể Rò Qua State, Logs Và Provisioner

`sensitive = true` chỉ làm CLI che giá trị ở một số output; nó không biến state thành nơi an toàn để chứa secret. Khi thiết kế Terraform cho production, hãy phân loại nơi secret có thể rò:

- resource/data source/output có thể ghi secret vào state;
- `TF_LOG=trace` có thể lộ request, response, caller identity hoặc signed request;
- `local-exec`, `external` data source và script trong pipeline có thể in credential ra log;
- artifact plan/log/state trong CI có thể bị lưu quá lâu hoặc cấp quyền đọc quá rộng.

Nguyên tắc thực tế:

- truyền secret ID/reference thay vì secret value nếu application có thể đọc runtime secret từ Vault, cloud secret manager hoặc workload identity;
- tắt trace log ngay sau khi debug và xử lý log debug như dữ liệu nhạy cảm;
- tránh `local-exec` cho logic có secret; nếu bắt buộc dùng, kiểm soát stdout/stderr và shell history;
- CI job chạy Terraform phải dùng role tạm thời/OIDC thay vì access key dài hạn;
- plan artifact cũng cần access control vì có thể chứa value nhạy cảm hoặc topology nội bộ.

Nếu nghi state/log đã lộ, không chỉ xóa file. Cần rotate secret, audit access, revoke token tạm thời nếu còn hiệu lực, rồi mới làm sạch backend/log retention.

## Policy Guardrails

Policy-as-code giúp chặn thay đổi nguy hiểm trước apply, nhưng không thay thế review plan. Một bộ guardrail Terraform thường kiểm tra:

- không tạo public bucket/storage nếu không có exception;
- không mở SSH/RDP từ `0.0.0.0/0`;
- bắt buộc tag owner, environment và cost center;
- không destroy database, KMS key hoặc bucket dữ liệu nếu thiếu approval;
- không dùng `local-exec` hoặc external data source trong module production nếu policy của team cấm;
- provider/module version phải được pin.

Policy nên chạy trên plan JSON trong CI/CD hoặc Terraform Cloud/HCP Terraform. Kết quả policy fail phải chỉ rõ resource address và lý do để reviewer xử lý được, tránh tạo noise khiến team bỏ qua cảnh báo.
