# Terraform State, Backend and Workspace

## State Là Gì

State là dữ liệu Terraform dùng để ánh xạ giữa cấu hình và resource thật ngoài hạ tầng. Mặc định state nằm trong file `terraform.tfstate`.

State trả lời các câu hỏi:

- Resource nào đang do Terraform quản lý?
- ID thật ngoài cloud là gì?
- Thuộc tính hiện tại của resource là gì?
- Lần apply trước Terraform đã biết gì?

Nếu mất state, Terraform có thể không biết resource thật nào tương ứng với code. Khi đó có thể phải import lại hoặc tệ hơn là tạo resource trùng.

## Vì Sao Terraform Cần State

State giúp Terraform ánh xạ resource trong config tới object thật ngoài provider. Terraform kỳ vọng mỗi remote object chỉ tương ứng với một resource instance trong config. Sau khi tạo resource, Terraform ghi lại identity thật của resource đó trong state.

State cũng lưu metadata phục vụ dependency và destroy order. Khi một `aws_internet_gateway` tham chiếu `aws_vpc.main.id`, Terraform hiểu gateway phụ thuộc vào VPC và khi destroy cũng cần tính thứ tự ngược lại.

Với hạ tầng lớn, state còn giúp cache thuộc tính để giảm số lần query provider API. Điều này quan trọng khi provider API chậm, bị rate limit hoặc không hỗ trợ query hàng loạt hiệu quả.

## State Có Thể Chứa Secret

State có thể chứa password, token, private endpoint, connection string hoặc dữ liệu nhạy cảm khác.

Nguyên tắc bắt buộc:

- Không commit `terraform.tfstate` vào Git.
- Không gửi state qua chat hoặc email.
- Dùng remote backend có access control và encryption.
- Bật state locking nếu backend hỗ trợ.
- Backup state có kiểm soát.

Đây là cùng một vấn đề với góc nhìn bảo mật trong [Security, CI/CD and Production Practices](./05-security-cicd-and-production-practices.md): state phải được xem như dữ liệu nhạy cảm, không chỉ là file kỹ thuật của Terraform.

## Lệnh Inspect State

```bash
terraform state list
terraform state show aws_instance.web
terraform show
```

Không sửa trực tiếp file state bằng text editor. Nếu cần thao tác state, dùng nhóm lệnh `terraform state`.

```bash
terraform state mv aws_instance.old aws_instance.new
terraform state rm aws_instance.web
```

## Backend

Backend quyết định Terraform lưu state ở đâu. Local backend phù hợp lab cá nhân. Với team hoặc production, nên dùng remote backend.

Các backend thường gặp:

- `local`: lưu state ở local file, là backend mặc định.
- `s3`: lưu state trên Amazon S3, thường kết hợp DynamoDB để locking.
- `azurerm`, `gcs`, `consul` hoặc Terraform Cloud/HCP Terraform tùy môi trường.

Ví dụ S3 backend:

```hcl
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "prod/network/terraform.tfstate"
    region         = "ap-southeast-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

Sau khi thêm hoặc đổi backend, chạy:

```bash
terraform init
```

Terraform có thể hỏi có muốn migrate state từ local lên remote không.

Khi cần migrate state giữa backend, dùng:

```bash
terraform init -migrate-state
```

### S3 Backend Production Pattern

Một S3 backend dùng cho team thường không chỉ là một bucket. Pattern tối thiểu nên có:

- S3 bucket để lưu state, bật versioning và encryption.
- DynamoDB table hoặc cơ chế lock tương đương để tránh hai apply ghi cùng state.
- KMS key hoặc encryption policy phù hợp với tiêu chuẩn bảo mật của tổ chức.
- IAM role/policy least privilege cho người dùng hoặc CI runner cần đọc/ghi state.
- Quy ước `key` theo domain/environment, ví dụ `prod/network/terraform.tfstate`.

Backend config được đọc rất sớm trong `terraform init`, nên không thể phụ thuộc vào variable Terraform thông thường theo cách resource argument phụ thuộc variable. Với nhiều environment, thường dùng file backend config riêng hoặc sinh config từ pipeline có kiểm soát.

Không commit credential backend. Nếu CI/CD assume role để truy cập state, role đó chỉ nên có quyền với bucket/key/table cần thiết, không dùng quyền cloud admin chung.

## State Locking

Locking ngăn hai người hoặc hai pipeline apply cùng lúc vào cùng một state.

Không có locking, rủi ro production rất lớn:

```text
Người A đang apply network
Người B cùng lúc apply security group
State bị ghi đè hoặc mất update
Plan sau đó không còn chính xác
```

Chỉ dùng `force-unlock` khi chắc chắn không còn process Terraform nào đang chạy:

```bash
terraform force-unlock <LOCK_ID>
```

Force unlock sai thời điểm có thể làm hai apply chạy đồng thời vào cùng state.

## Chia State Theo Domain

Không nên gom toàn bộ hạ tầng vào một state quá lớn. Nên chia theo domain hoặc blast radius:

```text
network/prod
security/prod
platform/prod
database/prod
application/prod
```

Chia nhỏ giúp giảm thời gian plan/apply và giới hạn phạm vi sự cố. Không nên chia quá nhỏ đến mức dependency phức tạp và phải truyền remote state khắp nơi.

Về cách đặt thư mục và tách environment, xem thêm: [Project Structure and Conventions](./06-project-structure-and-conventions.md).

## Workspace

Workspace cho phép nhiều state cùng dùng một root module. Mặc định luôn có workspace `default`.

```bash
terraform workspace list
terraform workspace new dev
terraform workspace select dev
terraform workspace show
terraform workspace delete dev
```

Workspace phù hợp cho lab hoặc nhiều môi trường giống nhau với khác biệt nhỏ.

Có thể dùng workspace trong code:

```hcl
resource "aws_instance" "example" {
  count         = terraform.workspace == "production" ? 5 : 1
  ami           = var.ami_id
  instance_type = "t3.micro"

  tags = {
    Name = "example-${terraform.workspace}"
  }
}
```

`default` workspace được tạo tự động và không thể xóa.

Không nên dùng workspace để thay thế phân tách production phức tạp nếu mỗi môi trường cần:

- Backend khác nhau.
- Credential khác nhau.
- Quy trình approval khác nhau.
- Blast radius tách biệt rõ.

Với production, thường nên tách thư mục hoặc root module theo environment:

```text
environments/dev
environments/staging
environments/prod
modules/network
modules/compute
```

## Refactor Mà Không Recreate Resource

Khi đổi cấu trúc Terraform code, mục tiêu là đổi resource address trong state mà không vô tình destroy/recreate object thật. Các tình huống thường gặp:

- chuyển resource từ root module vào child module;
- đổi tên resource cho rõ nghĩa hơn;
- chuyển từ resource rời sang `for_each`;
- import resource đã tồn tại ngoài Terraform vào code.

Workflow an toàn:

```bash
terraform state list
terraform plan
terraform state mv <old-address> <new-address>
terraform plan
```

`terraform state mv` chỉ nên chạy khi đã biết chắc source address và destination address. Sau khi move, plan phải xác nhận resource quan trọng không còn bị `destroy` hoặc `replace` ngoài ý muốn.

Nếu resource đang tồn tại ngoài Terraform, dùng import theo hướng:

```bash
terraform import <resource-address> <remote-id>
terraform plan
```

Không sửa trực tiếp `terraform.tfstate` bằng editor trừ trường hợp rất đặc biệt và đã backup state. Với Terraform version hiện đại, ưu tiên `moved` block khi refactor trong code để migration state có thể review và repeat trong pipeline.
