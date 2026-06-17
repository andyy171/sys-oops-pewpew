# Infrastructure as Code

Infrastructure as Code (IaC) là nhóm kiến thức về cách mô tả, review, triển khai và vận hành hạ tầng bằng code thay vì thao tác thủ công trên console hoặc CLI rời rạc.

Trong vault này, khu vực này dùng cho các công cụ và workflow quản lý hạ tầng như Terraform, OpenTofu, Pulumi, CloudFormation hoặc các pattern liên quan đến plan, apply, state, policy, module và pipeline hạ tầng.

## Khi đặt note vào khu vực này

Đặt note ở đây khi nội dung nói về:

- Mô hình IaC và declarative infrastructure.
- Terraform/OpenTofu provider, resource, state, backend, module, workspace.
- Quy trình `plan`, `apply`, review, approval và rollback hạ tầng.
- Chia state, remote backend, locking, drift và import resource.
- Tích hợp IaC với CI/CD, policy, security scan và secret handling.

Không đặt vào đây nếu note chủ yếu nói về:

- Cấu hình bên trong OS hoặc service sau khi VM đã được tạo. Nội dung đó thường hợp với Linux hoặc configuration management.
- Kiến trúc cloud provider cụ thể như OpenStack, AWS, Huawei Cloud. Nội dung đó thuộc `04-cloud-edge/`.
- Pipeline build/deploy ứng dụng thuần túy. Nội dung đó thuộc `03-cicd-devops-integration/`.

## Suggested Reading Order

1. [Terraform Overview](./01-terraform/overview.md)
2. [Terraform Core Concepts and Workflow](./01-terraform/01-core-concepts-and-workflow.md)
3. [Terraform State, Backend and Workspace](./01-terraform/02-state-backend-and-workspace.md)
4. [Terraform HCL Language, Types and Expressions](./01-terraform/07-hcl-language-types-and-expressions.md)
5. [Terraform Project Structure and Conventions](./01-terraform/06-project-structure-and-conventions.md)
6. [Terraform Modules, Data Sources and Lifecycle](./01-terraform/03-modules-data-and-lifecycle.md)
7. [Terraform Operations and Troubleshooting](./01-terraform/04-operations-and-troubleshooting.md)
8. [Terraform Testing, Refactoring and Provider Development](./01-terraform/11-testing-refactoring-and-provider-development.md)
9. [Terraform Security, CI/CD and Production Practices](./01-terraform/05-security-cicd-and-production-practices.md)
10. [Terraform Cloud and Registry](./01-terraform/08-terraform-cloud-and-registry.md)
11. [Terraform Cloud Patterns and Advanced Use Cases](./01-terraform/09-cloud-patterns-and-advanced-use-cases.md)
