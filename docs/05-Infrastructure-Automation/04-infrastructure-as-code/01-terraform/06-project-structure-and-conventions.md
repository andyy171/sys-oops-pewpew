# Terraform Project Structure and Conventions

## Overview

Project structure là kiến thức nền nên học trước các cloud pattern nâng cao. Một cấu trúc rõ giúp tách environment, module, backend, variable và ownership tốt hơn, từ đó giảm rủi ro khi nhiều người cùng vận hành Terraform.

## Cấu Trúc Project Cho Lab

Với lab hoặc bài học nhỏ, có thể bắt đầu đơn giản:

```text
terraform-lab
  main.tf
  variables.tf
  outputs.tf
  versions.tf
  terraform.tfvars
```

Không cần tách quá nhiều file từ đầu. Mục tiêu của lab là hiểu workflow `init`, `plan`, `apply`, `state` và cách resource thay đổi.

## Cấu Trúc Cho Nhiều Môi Trường

Với hạ tầng nhiều môi trường, nên tách environment rõ ràng:

```text
terraform-infra
  environments
    dev
      main.tf
      backend.tf
      variables.tf
      terraform.tfvars
    staging
      main.tf
      backend.tf
      variables.tf
      terraform.tfvars
    prod
      main.tf
      backend.tf
      variables.tf
      terraform.tfvars
  modules
    network
      main.tf
      variables.tf
      outputs.tf
    compute
      main.tf
      variables.tf
      outputs.tf
```

Cách tách này thường rõ hơn việc dùng workspace cho production phức tạp, vì mỗi environment có thể có backend, credential, approval và blast radius riêng.

Xem thêm: [State, Backend and Workspace](./02-state-backend-and-workspace.md).

## Nguyên Tắc Đặt File

Không bắt buộc Terraform phải có `main.tf`, `variables.tf`, `outputs.tf`, nhưng đây là convention dễ đọc.

- `versions.tf`: `required_version` và `required_providers`.
- `providers.tf`: cấu hình provider.
- `backend.tf`: cấu hình backend.
- `variables.tf`: input variables.
- `outputs.tf`: outputs.
- `locals.tf`: local values.
- `main.tf`: resource hoặc module chính.

Với module lớn, có thể tách file theo domain như `network.tf`, `security-group.tf`, `iam.tf`, nhưng không nên tách vụn đến mức người đọc phải mở quá nhiều file để hiểu một resource graph.

## Module Directory

Module dùng chung nên có cấu trúc tối thiểu:

```text
modules/network
  main.tf
  variables.tf
  outputs.tf
  versions.tf
  README.md
```

Một module tốt nên có input/output rõ ràng, không hardcode environment và có ví dụ sử dụng. Khi module được publish nội bộ hoặc public, cần version rõ ràng.

Xem thêm: [Modules, Data Sources and Lifecycle](./03-modules-data-and-lifecycle.md) và [Terraform Cloud and Registry](./08-terraform-cloud-and-registry.md).

## Flat Module Và Nested Module

Flat module là cách tổ chức nhiều file `.tf` trong cùng một module, ví dụ `main.tf`, `iam.tf`, `network.tf`, `outputs.tf`. Nested module là cách tách từng component thành child module riêng rồi gọi từ root/module cha.

Flat module phù hợp khi:

- codebase nhỏ hoặc trung bình;
- các component gần nhau về ownership;
- tách file giúp đọc dễ hơn nhưng chưa đủ lý do tạo module riêng;
- input/output contract giữa các phần chưa ổn định.

Nested module phù hợp khi:

- component được dùng lại ở nhiều nơi;
- cần interface rõ qua input/output;
- mỗi module có ownership, test hoặc version riêng;
- dependency graph phức tạp và cần boundary để giảm coupling.

Rủi ro của flat module là dễ biến nhiều file `.tf` thành một khối global state khó lần theo. Rủi ro của nested module là tạo quá nhiều boilerplate và output/input dây chuyền. Với production, chọn boundary theo blast radius và khả năng review plan, không chọn chỉ vì muốn code trông "gọn".

## tfvars Convention

`terraform.tfvars` hoặc `*.tfvars` giúp truyền input theo môi trường, nhưng không nên dùng để lưu credential thật.

```hcl
region        = "ap-southeast-1"
instance_type = "t3.micro"
```

Nếu file chứa secret, không commit vào Git và nên thay bằng secret manager, CI/CD secret hoặc workload identity.

Xem thêm: [Security, CI/CD and Production Practices](./05-security-cicd-and-production-practices.md).

## Practical Rules

- Tách environment theo thư mục khi production có backend, credential hoặc approval khác nhau.
- Tách state theo domain có blast radius riêng như network, security, platform, database.
- Giữ module đủ nhỏ để tái sử dụng, nhưng không module hóa quá sớm.
- Commit `.terraform.lock.hcl` để khóa provider version cho team.
- Không commit `.terraform/`, state local, plan binary hoặc file tfvars chứa secret.

## Multi-Cloud Project Structure

Với repository quản lý nhiều cloud provider, nên tách rõ hai lớp:

- `modules/`: module tái sử dụng, không gắn chặt vào environment cụ thể.
- `envs/` hoặc `environments/`: cấu hình gọi module theo từng môi trường và từng provider, có backend/provider/tfvars riêng.

Ví dụ layout:

```text
multi-cloud-terraform
  modules
    aws
      storage
        main.tf
        variables.tf
        outputs.tf
    azure
      compute
        main.tf
        variables.tf
        outputs.tf
  envs
    dev
      aws
        backend.tf
        providers.tf
        terraform.tfvars
      azure
        backend.tf
        providers.tf
        terraform.tfvars
    test
      aws
        backend.tf
        providers.tf
        terraform.tfvars
      azure
        backend.tf
        providers.tf
        terraform.tfvars
    prod
      aws
        backend.tf
        providers.tf
        terraform.tfvars
```

Nguyên tắc vận hành:

- Không dùng chung state giữa AWS và Azure nếu resource lifecycle và quyền quản trị khác nhau.
- Tách backend theo environment để giảm blast radius khi chạy `plan` hoặc `apply`.
- Provider config nên nằm ở environment layer, module chỉ nhận input và trả output.
- Không commit credential trong `terraform.tfvars`; dùng secret manager, CI/CD secret hoặc workload identity.
- Với production, chạy `terraform plan` trên đúng account/subscription/project trước khi apply.
