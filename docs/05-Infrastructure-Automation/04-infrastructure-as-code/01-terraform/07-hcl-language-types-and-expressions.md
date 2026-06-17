# Terraform HCL Language, Types and Expressions

## Overview

Terraform dùng HCL để mô tả resource, input, output, expression và logic lặp. Với production code, hiểu type system và các construct như `for_each`, `count`, `dynamic block` giúp module rõ hơn, ít lỗi hơn và dễ review plan hơn.

## Kiểu Dữ Liệu Cơ Bản

Các kiểu cơ bản thường dùng:

- `string`: chuỗi.
- `number`: số.
- `bool`: giá trị đúng/sai.

```hcl
variable "str_ex" {
  type    = string
  default = "str_val"
}

variable "num_ex" {
  type    = number
  default = 99
}

variable "bool_ex" {
  type    = bool
  default = true
}
```

## Kiểu Dữ Liệu Phức Tạp

Các kiểu phức tạp thường dùng:

- `list(type)`: danh sách có thứ tự, các phần tử cùng kiểu.
- `set(type)`: tập giá trị không trùng lặp, không nên dựa vào thứ tự.
- `map(type)`: key/value, các value cùng kiểu.
- `object({...})`: key/value với schema rõ ràng cho từng field.
- `tuple([...])`: danh sách có số phần tử và kiểu phần tử cố định.

```hcl
variable "servers" {
  type = map(object({
    instance_type = string
    subnet_id      = string
  }))
}
```

Trong module dùng chung, nên khai báo type cụ thể thay vì dùng `any` quá rộng. Type rõ giúp `terraform validate` phát hiện lỗi sớm hơn.

### Type Coercion Và Validation

Terraform có thể tự ép kiểu primitive sang string trong một số ngữ cảnh, đặc biệt khi nội suy chuỗi. Ví dụ `true`, `false` hoặc `17` có thể trở thành `"true"`, `"false"` hoặc `"17"` khi đi qua string template. Điều này tiện cho rendering, nhưng dễ làm điều kiện review sai nếu người viết nhầm giữa number/bool và string.

Nguyên tắc an toàn:

- Khai báo `type` rõ ràng cho input variable.
- Dùng `validation` để chặn input không hợp lệ càng sớm càng tốt.
- Dùng `tostring()`, `tonumber()`, `toset()`, `tolist()` khi cần cast rõ ràng thay vì dựa vào ép kiểu ngầm.

Ví dụ validation:

```hcl
variable "allowed_cidrs" {
  type        = list(string)
  description = "CIDR ranges allowed to access the service."

  validation {
    condition     = length(var.allowed_cidrs) > 0
    error_message = "At least one CIDR must be provided."
  }
}
```

Trong production module, validation nên mô tả điều kiện vận hành thật: danh sách không rỗng, region nằm trong allowlist, port nằm trong khoảng hợp lệ, hoặc mode chỉ nhận các giá trị được hỗ trợ.

## Truyền Biến Qua tfvars Và Environment

File `terraform.tfvars` hoặc `*.tfvars` thường dùng để truyền input theo môi trường.

```hcl
region        = "ap-southeast-1"
instance_type = "t3.micro"
```

Không commit file chứa secret hoặc credential thật. Với file có dữ liệu nhạy cảm, thêm vào `.gitignore` và dùng secret manager hoặc cơ chế inject an toàn trong CI/CD.

Terraform cũng hỗ trợ input qua biến môi trường có prefix `TF_VAR_`:

```bash
export TF_VAR_instance_type="t3.small"
terraform plan
```

Về quy trình bảo vệ secret, credential và tfvars trong team, xem thêm: [Security, CI/CD and Production Practices](./05-security-cicd-and-production-practices.md).

## Locals Và Expression

`locals` dùng để đặt tên cho kết quả của expression. Nên dùng local khi một expression được dùng nhiều lần hoặc khi đặt tên giúp plan/code dễ đọc hơn.

```hcl
locals {
  normalized_tags = merge(var.common_tags, {
    Environment = var.environment
    ManagedBy   = "terraform"
  })
}

resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = var.instance_type
  tags          = local.normalized_tags
}
```

Input variable giống tham số truyền vào module, local giống biến tạm có tên, còn output giống giá trị trả ra cho người dùng hoặc module khác. Không nên biến `locals` thành nơi giấu toàn bộ business logic phức tạp; nếu expression cần nhiều tầng `for`, `merge`, `flatten`, `lookup`, hãy cân nhắc tách nhỏ thành nhiều local có tên rõ.

## Functions Và Templatefile

Terraform function biến đổi input thành output trong expression. Terraform không có user-defined function theo nghĩa của ngôn ngữ lập trình tổng quát; nếu cần mở rộng hành vi tương tác với hệ thống ngoài, hướng đúng thường là provider hoặc external data source có kiểm soát.

`templatefile(path, vars)` render file template bằng map biến truyền vào:

```hcl
locals {
  user_data = templatefile("${path.module}/templates/user-data.sh", {
    hostname = var.hostname
    packages = var.packages
  })
}
```

Chỉ các biến trong map thứ hai mới nằm trong scope của template. Template không tự thấy toàn bộ `var`, `local` hoặc resource của module. Với template cho script/cloud-init, nên dùng extension đúng với nội dung thật như `.sh`, `.yaml` hoặc `.cloud-config` thay vì đặt tên mơ hồ.

Các helper liên quan file hay gặp:

```hcl
locals {
  template_files = tolist(fileset(path.module, "templates/*.yaml"))
  selected_file  = element(local.template_files, var.index)
}
```

- `path.module`: thư mục chứa module hiện tại.
- `fileset()`: trả về set path khớp pattern, thường cần `tolist()` nếu cần list.
- `element()`: lấy phần tử theo index và có hành vi vòng tròn; tiện cho lab, nhưng trong production cần cẩn thận vì có thể che lỗi index ngoài mong đợi.

## for_each

`for_each` dùng để tạo nhiều resource instance từ `map` hoặc `set`. Ưu điểm chính là mỗi instance có key ổn định, dễ đọc trong state và plan.

```hcl
variable "security_groups" {
  type = map(object({
    name        = string
    description = string
  }))
}

resource "aws_security_group" "example" {
  for_each = var.security_groups

  name        = each.value.name
  description = each.value.description
  vpc_id      = aws_vpc.main.id
}
```

Resource address sẽ có dạng:

```text
aws_security_group.example["web"]
aws_security_group.example["ssh"]
```

## count

`count` dùng để tạo nhiều instance dựa trên số lượng.

```hcl
resource "aws_instance" "example" {
  count         = length(var.instances)
  ami           = var.instances[count.index].ami
  instance_type = var.instances[count.index].instance_type
}
```

`count` phù hợp khi các instance gần như giống nhau và không cần key có ý nghĩa. Nếu danh sách bị sắp xếp lại, address theo index có thể thay đổi và làm plan khó đọc hơn.

## for_each So Với count

Nên ưu tiên `for_each` khi:

- Mỗi instance có tên hoặc key tự nhiên.
- Cần lifecycle ổn định khi thêm/xóa một phần tử.
- Muốn plan/state dễ đọc hơn.

`count` phù hợp khi:

- Chỉ cần bật/tắt resource bằng `count = var.enabled ? 1 : 0`.
- Các instance thật sự đồng nhất và không cần định danh riêng.

Khi dùng `count`, resource address trở thành dạng index:

```text
aws_instance.example[0]
aws_instance.example[1]
```

Index làm state dễ bị xáo trộn nếu list đầu vào thay đổi thứ tự. Với resource có identity quan trọng, `for_each` thường an toàn hơn vì key ổn định hơn index.

## For Expression

`for` expression dùng để biến đổi collection này thành collection khác. Dấu ngoặc quyết định output type:

```hcl
locals {
  upper_names = [for name in var.names : upper(name)]
  subnet_host = { for name, cidr in var.subnets : name => cidrhost(cidr, 10) }
}
```

Có thể thêm `if` để lọc phần tử:

```hcl
locals {
  public_subnets = {
    for name, subnet in var.subnets : name => subnet
    if subnet.public
  }
}
```

`for` expression mạnh nhưng rất dễ làm module khó review. Với production code, ưu tiên expression ngắn, có tên qua `locals`, và tránh lồng nhiều tầng nếu người review plan không thể đoán resource cuối cùng sẽ được tạo như thế nào.

## Splat Expression Và String Template Directive

Splat expression là cú pháp ngắn để lấy cùng một field từ nhiều object:

```hcl
locals {
  instance_ids = aws_instance.web[*].id
}
```

Nó tương đương mental model:

```hcl
locals {
  instance_ids = [for instance in aws_instance.web : instance.id]
}
```

Splat giúp code gọn trong output hoặc module wiring đơn giản. Với logic phức tạp, `for` expression có tên trong `locals` thường dễ review hơn.

String template directive dùng `%{ ... }` để lặp hoặc điều kiện bên trong chuỗi/template:

```hcl
%{ for ip in var.backend_ips ~}
server ${ip}
%{ endfor ~}
```

Dùng directive cho file cấu hình render bằng `templatefile()` thì hợp lý. Không nên nhồi quá nhiều control flow vào string template trong resource argument vì plan sẽ khó đọc và khó test.

## Conditional Expression Và Randomness

Conditional expression có dạng:

```hcl
condition ? value_if_true : value_if_false
```

Use case phổ biến là bật/tắt resource:

```hcl
resource "aws_cloudwatch_metric_alarm" "latency" {
  count = var.enable_alarm ? 1 : 0
}
```

Không nên dùng conditional để thay thế `validation` khi mục tiêu là chặn input sai. Conditional lồng nhiều tầng làm plan khó đọc và dễ tạo khác biệt giữa môi trường.

Terraform function nên hội tụ về cùng kết quả với cùng input. Các function tạo giá trị thay đổi theo thời gian hoặc ngẫu nhiên như `timestamp()` và `uuid()` có thể làm plan không ổn định nếu dùng trực tiếp trong resource argument. Nếu cần random value, dùng Random provider và nhớ rằng giá trị random có thể nằm trong state/plan; với secret, state/backend phải được bảo vệ như dữ liệu nhạy cảm.

## Dynamic Block

`dynamic block` dùng để sinh nested block lặp lại, ví dụ nhiều rule `ingress`.

```hcl
variable "ingress_rules" {
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
  }))
}

resource "aws_security_group" "example" {
  name   = "example"
  vpc_id = aws_vpc.main.id

  dynamic "ingress" {
    for_each = var.ingress_rules

    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

Không nên lạm dụng `dynamic block`. Nếu module có quá nhiều dynamic logic, plan sẽ khó đọc và người vận hành khó đoán được resource thật sẽ trông như thế nào.

## Best Practices

- Khai báo type rõ ràng cho variable.
- Ưu tiên `object` cho input phức tạp thay vì nhiều biến rời rạc.
- Dùng `for_each` cho collection có key ổn định.
- Tránh biến module thành framework quá thông minh.
- Với production, code dễ đọc quan trọng hơn việc giảm vài dòng HCL.
