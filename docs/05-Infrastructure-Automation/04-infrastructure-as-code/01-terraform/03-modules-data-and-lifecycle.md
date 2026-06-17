# Terraform Modules, Data Sources and Lifecycle

## Module Là Gì

Module là cách đóng gói một nhóm resource để tái sử dụng. Mọi thư mục Terraform đều là một module. Root module là nơi chạy Terraform. Child module là module được gọi từ root module.

```hcl
module "network" {
  source = "./modules/network"

  vpc_cidr = "10.10.0.0/16"
  name     = "prod"
}
```

## Cấu Trúc Module Cơ Bản

```text
modules/network
  main.tf
  variables.tf
  outputs.tf
  versions.tf
```

Một module tốt nên:

- Có input rõ ràng và type rõ ràng.
- Có output cần thiết, không output thừa secret.
- Không hardcode environment.
- Không tự quyết định provider credential.
- Có version nếu publish dùng chung.
- Có README mô tả input, output và ví dụ dùng.

Không nên module hóa quá sớm. Nếu hạ tầng còn thay đổi mạnh, module quá sớm có thể làm code cứng và khó sửa. Nên bắt đầu bằng code rõ ràng, sau đó gom thành module khi pattern đã ổn định.

## Root Module, Child Module Và Nested Module

Root module là thư mục nơi chạy `terraform init`, `terraform plan` và `terraform apply`. Root module thường giữ provider/backend config, biến theo environment và lời gọi tới các child module.

Child module là module được gọi từ root hoặc từ module khác:

```hcl
module "networking" {
  source    = "./modules/networking"
  namespace = var.namespace
}

module "database" {
  source    = "./modules/database"
  namespace = var.namespace
  vpc       = module.networking.vpc
  sg        = module.networking.sg
}
```

Nested module là khi child module lại gọi các module con khác, ví dụ module `networking` gọi module VPC và security group. Pattern này hữu ích khi hạ tầng phức tạp, nhưng không nên để hierarchy quá sâu. Nếu người vận hành phải đi qua nhiều lớp output/input mới hiểu một subnet, security group hoặc database endpoint đến từ đâu, module boundary đang quá rối.

Mental model:

```text
terraform.tfvars
-> root module variables
-> root module wires top-level modules
-> child modules create resources or call nested modules
-> outputs bubble up
-> selected values trickle down into dependent modules
```

## Module Data Flow

Data giữa module nên đi qua input/output contract rõ ràng. Một module không nên tự đọc sâu vào implementation detail của module khác; nó chỉ nên nhận output đã được module kia công bố.

Ví dụ database cần VPC/subnet/security group từ networking:

```text
module.vpc/database/security-group output
-> networking module output
-> root module
-> database module input
```

Nguyên tắc production:

- Chỉ output dữ liệu module khác thật sự cần, tránh output cả object lớn nếu không có lý do.
- Không output secret ra root module nếu chỉ một child module khác cần dùng.
- Dùng `object({ ... })` cho input quan trọng thay vì `any` khi contract đã ổn định.
- Tránh module interdependency hai chiều; nó làm dependency graph khó hiểu và dễ tạo cycle.
- Nếu hai module phải truyền quá nhiều dữ liệu qua lại, có thể boundary đang sai và nên gom resource gần nhau hơn.

## Public Registry Module Risk

Module public giúp tiết kiệm thời gian, nhưng cũng là dependency supply chain. Trước khi dùng module từ Terraform Registry hoặc Git repo ngoài:

- Pin version/module source rõ ràng.
- Đọc README, input/output, changelog và issue gần đây.
- Skim source để kiểm tra resource nhạy cảm như IAM, security group, public exposure, lifecycle và provisioner.
- Ưu tiên module có maintainer đáng tin, release đều và cộng đồng sử dụng thực tế.
- Với production quan trọng, cân nhắc fork/internal mirror để tránh source bị xóa hoặc thay đổi ngoài kiểm soát.

Không nên coi module Registry là black box tuyệt đối. Module interface có thể đẹp, nhưng blast radius vẫn là resource thật trong account/subscription/project của mình.

## Data Source

Data source dùng để đọc thông tin có sẵn từ provider mà không tạo resource mới.

Ví dụ đọc AMI mới nhất:

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true

  owners = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}
```

Dùng trong resource:

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
}
```

Dùng data source khi cần tham chiếu resource không do module hiện tại tạo ra, ví dụ VPC có sẵn, DNS zone có sẵn, AMI, secret metadata hoặc output từ remote state.

## Cẩn Thận Với Data Source Thay Đổi

Nếu data source trả về giá trị thay đổi theo thời gian, plan có thể đổi ngoài dự kiến. Ví dụ `most_recent = true` có thể làm instance bị replace khi AMI mới xuất hiện.

Với production, nên cân nhắc pin version hoặc dùng quy trình promotion rõ ràng.

## Lifecycle Block

Lifecycle điều chỉnh cách Terraform xử lý vòng đời resource.

```hcl
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = "t3.micro"

  lifecycle {
    create_before_destroy = true
  }
}
```

### create_before_destroy

Tạo resource mới trước rồi xóa resource cũ sau khi cần replace.

```hcl
lifecycle {
  create_before_destroy = true
}
```

Không phải resource nào cũng an toàn với cách này vì có thể vướng quota, naming unique hoặc conflict.

### prevent_destroy

Ngăn Terraform destroy resource quan trọng.

```hcl
lifecycle {
  prevent_destroy = true
}
```

Phù hợp cho database, bucket dữ liệu quan trọng, KMS key hoặc resource có rủi ro mất dữ liệu.

### ignore_changes

Bỏ qua thay đổi ở một số attribute.

```hcl
lifecycle {
  ignore_changes = [tags]
}
```

Dùng khi attribute bị hệ thống khác cập nhật. Không nên dùng để che drift nghiêm trọng. Nếu lạm dụng, Terraform không còn phản ánh đúng desired state.

