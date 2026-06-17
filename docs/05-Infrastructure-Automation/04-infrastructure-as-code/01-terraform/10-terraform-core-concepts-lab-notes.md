# Terraform Core Concepts Lab Notes

## Overview

Note này chuyển hóa file thô `Terraform-concepts.md` thành bản ghi nhớ thực hành. Nội dung bổ sung cho các note Terraform canonical về provider, resource, variables, output, module, state, backend, datasource, locking và security.

## Workflow

Terraform đi theo vòng cơ bản:

```text
write HCL -> terraform init -> terraform plan -> terraform apply -> observe state -> change -> plan/apply
```

`plan` là bước rất quan trọng vì nó cho biết Terraform định tạo, sửa hoặc xóa gì trước khi tác động vào hạ tầng thật.

## File Building Blocks

| Block | Vai trò |
|---|---|
| `provider` | cấu hình provider/API mà Terraform sẽ gọi |
| `resource` | tài nguyên Terraform quản lý |
| `variable` | input giúp module/project linh hoạt |
| `locals` | giá trị nội bộ tính toán lại từ input hoặc expression |
| `output` | xuất thông tin sau apply |
| `module` | đóng gói/tái sử dụng một nhóm resource |
| `data` | đọc thông tin có sẵn từ provider hoặc remote state |

Ví dụ rất tối giản:

```hcl
provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

resource "aws_instance" "example" {
  ami           = var.ami_id
  instance_type = "t3.micro"
}

output "instance_id" {
  value = aws_instance.example.id
}
```

## Output

Output dùng để lấy giá trị quan trọng sau khi provisioning, ví dụ instance ID, DNS name, private IP hoặc endpoint.

```bash
terraform output
terraform output -raw instance_id
```

Có thể dùng output trong automation sau Terraform:

```bash
export INSTANCE_ID="$(terraform output -raw instance_id)"
```

Không output secret trừ khi thật sự cần và đã hiểu rằng state có thể lưu giá trị nhạy cảm.

## Module

Module giúp chia nhỏ hạ tầng:

```hcl
module "network" {
  source = "./modules/network"

  vpc_cidr = "10.0.0.0/16"
}
```

Module tốt nên có:

- input rõ ràng;
- output cần thiết;
- version nếu dùng module từ registry/git;
- README hoặc ví dụ tối thiểu;
- không hard-code account/region/secret.

## State

State là bản ghi Terraform dùng để map cấu hình HCL với resource thật.

Điểm quan trọng:

- state có thể chứa dữ liệu nhạy cảm;
- state local không phù hợp cho team;
- remote backend giúp chia sẻ state;
- locking tránh hai người apply cùng lúc;
- không sửa state thủ công nếu chưa hiểu hậu quả.

## Remote Backend

Ví dụ backend S3:

```hcl
terraform {
  backend "s3" {
    bucket = "example-terraform-state"
    key    = "project-a/terraform.tfstate"
    region = "us-east-1"
  }
}
```

Sau khi thêm hoặc đổi backend:

```bash
terraform init
```

Trong production, backend cần encryption, versioning, access control và lock phù hợp. Không commit access key/secret key vào HCL.

## Datasource

Datasource đọc dữ liệu có sẵn từ provider:

```hcl
data "aws_availability_zones" "available" {
  state = "available"
}
```

Dùng datasource khi muốn tham chiếu object đã tồn tại hoặc thông tin động như AMI, AZ, IP range, VPC, subnet.

## Commands

```bash
terraform fmt
terraform init
terraform validate
terraform plan
terraform apply
terraform destroy
terraform state list
terraform state show <address>
```

`destroy` là thao tác phá hủy tài nguyên. Với môi trường thật, cần review plan, backup dữ liệu, xác nhận blast radius và có approval.

## Security Notes

- Không lưu secret trong repo.
- Bảo vệ state backend như dữ liệu nhạy cảm.
- Dùng IAM least privilege cho pipeline Terraform.
- Review `plan` trước `apply`.
- Tách workspace/project/account rõ ràng để giảm blast radius.
- Không dùng state local cho team hoặc production.

## Related Pages

- [Terraform Core Concepts And Workflow](./01-core-concepts-and-workflow.md)
- [Terraform State, Backend And Workspace](./02-state-backend-and-workspace.md)
- [Terraform Modules, Data And Lifecycle](./03-modules-data-and-lifecycle.md)
- [Terraform Security, CI/CD And Production Practices](./05-security-cicd-and-production-practices.md)
