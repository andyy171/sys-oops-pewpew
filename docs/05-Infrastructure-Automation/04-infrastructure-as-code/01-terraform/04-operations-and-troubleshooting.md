# Terraform Operations and Troubleshooting

## Khi Nào Dùng Lệnh Nào

Phần này gom các lệnh theo tình huống vận hành. Các lệnh như `init`, `plan`, `apply` là workflow cơ bản; các lệnh như `import`, `replace`, `refresh-only`, `force-unlock` chỉ nên dùng khi đã hiểu tác động tới state và hạ tầng thật.

### init

`terraform init` khởi tạo working directory, tải provider, tải module và cấu hình backend.

```bash
terraform init
terraform init -backend-config=backend.hcl
terraform init -backend-config="key=prod/network/terraform.tfstate"
```

### plan

`terraform plan` tạo execution plan để xem Terraform sẽ tạo, cập nhật, replace hoặc xóa resource nào.

```bash
terraform plan
terraform plan -out=tfplan
```

### apply

`terraform apply` áp dụng thay đổi vào hạ tầng.

```bash
terraform apply
terraform apply tfplan
```

Không nên dùng `apply` trên production nếu chưa review plan. Nếu config `.tf` rỗng nhưng state vẫn có resource, Terraform có thể plan destroy các resource đang được quản lý.

### destroy

`terraform destroy` xóa resource đang được quản lý bởi root module hiện tại.

```bash
terraform destroy
```

`terraform destroy -auto-approve` bỏ qua xác nhận thủ công, rất nguy hiểm nếu dùng sai môi trường.

### Import Resource

`terraform import` đưa resource đã tồn tại ngoài thực tế vào Terraform state.

```bash
terraform import aws_instance.web i-0123456789abcdef0
```

Import không tự sinh đầy đủ file `.tf`. Sau khi import, vẫn phải viết cấu hình tương ứng trong code. Nếu chỉ import state mà không có config đúng, lần plan tiếp theo có thể báo drift hoặc muốn thay đổi resource.

### Replace Resource

`terraform taint` từng được dùng để đánh dấu resource cần recreate. Cách hiện đại hơn là dùng `terraform apply -replace`.

```bash
terraform apply -replace=aws_instance.web
```

Lệnh này yêu cầu Terraform thay thế resource cụ thể trong lần apply.

### Refresh Only

Refresh-only cập nhật state theo trạng thái thật ngoài hạ tầng mà chưa muốn thay đổi hạ tầng.

```bash
terraform plan -refresh-only
terraform apply -refresh-only
```

`terraform refresh` kiểu cũ đã bị thay bằng workflow `plan/apply -refresh-only` trong thực hành hiện đại.

### fmt, output Và graph

```bash
terraform fmt
terraform fmt -recursive
terraform output
terraform graph
```

`terraform graph` xuất dependency graph ở định dạng DOT, hữu ích khi muốn hiểu dependency phức tạp.

## Provisioning Parallelism Và Provisioner

Terraform có thể thực hiện nhiều thao tác song song. Mặc định thường là 10 thao tác đồng thời, có thể điều chỉnh bằng `-parallelism`.

```bash
terraform apply -parallelism=20
```

Không phải tăng parallelism là tốt hơn. Cần cân nhắc provider API rate limit, dependency thật và khả năng rollback thủ công nếu apply một phần thành công.

Provisioner như `remote-exec` và `local-exec` có thể chạy script hoặc command trong quá trình tạo resource.

```hcl
resource "aws_instance" "example" {
  ami           = var.ami_id
  instance_type = "t3.micro"

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y nginx"
    ]
  }
}
```

Provisioner chỉ nên dùng khi thật cần, ví dụ bootstrapping tạm thời. Với cấu hình OS hoặc application lâu dài, nên ưu tiên cloud-init, image baking, Ansible hoặc một pipeline cấu hình riêng.

Nếu mục tiêu là chuẩn hóa cấu hình sau khi resource đã được tạo, xem thêm các note Linux/configuration management thay vì dồn toàn bộ logic vào Terraform provisioner.

## Debug Terraform

### Validate

```bash
terraform validate
```

Lệnh này kiểm tra cấu hình có hợp lệ về cú pháp và cấu trúc không. Nó không đảm bảo apply thành công vì apply còn phụ thuộc API, permission, quota và trạng thái thật.

### Console

`terraform console` giúp thử expression:

```bash
terraform console
```

Ví dụ:

```hcl
length(["a", "b", "c"])
toset(["dev", "prod"])
```

### Bật Log Debug

```bash
export TF_LOG=DEBUG
terraform plan
```

Ghi log ra file:

```bash
export TF_LOG=DEBUG
export TF_LOG_PATH=terraform-debug.log
terraform plan
```

Không bật debug lâu trong môi trường có secret vì log có thể chứa thông tin nhạy cảm.

Các log level thường gặp:

- `TRACE`
- `DEBUG`
- `INFO`
- `WARN`
- `ERROR`

## Lỗi Thường Gặp

Các nhóm lỗi phổ biến:

- Sai provider credential.
- Sai region, project hoặc tenant.
- Resource name bị trùng.
- Thiếu permission IAM.
- State lock chưa được giải phóng.
- Drift ngoài Terraform.
- Provider version thay đổi làm behavior khác.
- Variable type không khớp.

## Plan Hoặc Apply Chậm

Terraform có thể chậm do:

- State quá lớn.
- Quá nhiều resource trong một root module.
- Provider API chậm hoặc bị rate limit.
- Data source đọc quá nhiều.
- Dependency graph bị serialize quá mức.
- Module thiết kế quá rộng hoặc quá nhiều logic.

Hướng xử lý:

- Chia state theo domain vừa đủ.
- Giảm data source không cần thiết.
- Pin giá trị ít thay đổi qua variable nếu phù hợp.
- Kiểm tra dependency có đang làm graph bị tuần tự hóa không.
- Không tăng `parallelism` tùy tiện nếu provider bị rate limit.

```bash
terraform apply -parallelism=20
```

Khi state quá lớn làm plan/apply chậm, xem thêm: [State, Backend and Workspace](./02-state-backend-and-workspace.md).

## Checklist Trước Khi Apply Production

Trước khi apply production, kiểm tra:

- Đúng workspace hoặc backend chưa.
- Đúng cloud account, project hoặc tenant chưa.
- Provider version có thay đổi không.
- Có resource nào bị destroy hoặc replace không.
- State có lock không.
- Có backup hoặc rollback plan không.
- Có approval chưa.
- Có ai khác đang apply không.

## Lệnh Cần Nhớ

```bash
terraform version
terraform init
terraform fmt
terraform validate
terraform plan
terraform plan -out=tfplan
terraform apply tfplan
terraform output
terraform state list
terraform state show <ADDRESS>
terraform import <ADDRESS> <ID>
terraform apply -replace=<ADDRESS>
terraform destroy
terraform workspace list
terraform workspace select <NAME>
```

## Flag Vận Hành Hay Gặp

Các ảnh note trong `_inbox` nhắc nhiều tới flag Terraform. Khi ghi vào note vận hành, nên nhớ theo nhóm tác động thay vì học thuộc rời rạc:

| Flag | Dùng với | Ý nghĩa / lưu ý |
|---|---|---|
| `-out=tfplan` | `plan` | Lưu execution plan để apply đúng plan đã review |
| `-input=false` | `init`, `plan`, `apply` | Tắt prompt tương tác, hữu ích trong CI/CD |
| `-no-color` | nhiều lệnh | Log dễ đọc hơn trong CI/CD |
| `-json` | `show`, `plan`, `output` | Xuất JSON cho automation hoặc policy check |
| `-var` / `-var-file` | `plan`, `apply` | Truyền biến; tránh đưa secret vào command history |
| `-lock-timeout` | `plan`, `apply`, `import`, state commands | Chờ state lock thay vì fail ngay |
| `-parallelism` | `plan`, `apply`, `destroy` | Điều chỉnh số thao tác song song; cẩn thận provider rate limit |
| `-state` | state/debug commands | Dùng state file thay thế; chỉ nên dùng khi hiểu rõ rủi ro |
| `-target` | `plan`, `apply`, `destroy` | Chỉ target resource cụ thể; không dùng như workflow thường ngày |
| `-auto-approve` | `apply`, `destroy` | Bỏ qua xác nhận; nguy hiểm trên production |

Trong production, thứ tự an toàn thường là:

```bash
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
```
