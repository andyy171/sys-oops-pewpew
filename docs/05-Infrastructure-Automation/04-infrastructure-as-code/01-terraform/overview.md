# Terraform Overview

Terraform là công cụ Infrastructure as Code do HashiCorp phát triển. Công cụ này cho phép mô tả hạ tầng bằng HCL, sau đó tạo, cập nhật hoặc xóa resource thông qua API của provider như AWS, Azure, Google Cloud, OpenStack, Kubernetes, GitHub hoặc Cloudflare.

Terraform phù hợp nhất cho provisioning hạ tầng: network, subnet, VM, security group, load balancer, database, Kubernetes cluster, DNS record và các resource nền tảng khác. Với cấu hình bên trong máy chủ, Ansible hoặc công cụ configuration management thường phù hợp hơn.

## Vì Sao Cần IaC

Infrastructure as Code giúp hạ tầng có version, có thể review, có thể lặp lại và giảm sai lệch giữa các môi trường. Khi không dùng IaC, việc quản lý hạ tầng thường phụ thuộc vào thao tác thủ công, script rời rạc hoặc tài liệu không còn khớp với thực tế.

Các vấn đề thường gặp khi quản lý infrastructure bằng tay:

- Khó đảm bảo các component được cấu hình thống nhất.
- Khó giữ cùng một tiêu chuẩn giữa dev, staging và production.
- Provisioning chậm, phụ thuộc nhiều vào người thao tác.
- Dễ phát sinh lỗi như thiếu config, sai region, sai rule hoặc sai thứ tự triển khai.
- Khó tạo tài liệu chính xác vì trạng thái thật thay đổi liên tục.

## Tư Duy Cốt Lõi

Terraform hoạt động theo mô hình declarative. Người vận hành mô tả trạng thái mong muốn, còn Terraform tự tính các bước cần làm thông qua execution plan.

```text
HCL configuration
        |
        v
terraform init
        |
        v
terraform plan
        |
        v
terraform apply
        |
        v
terraform state
```

Điểm trung tâm cần hiểu là `state`. Terraform không chỉ đọc cloud thật, mà còn dựa vào state để biết resource nào đang thuộc quyền quản lý của nó.

## Cách Học Terraform

Không nên học Terraform như một tập lệnh rời rạc. Nên học theo lớp:

1. IaC và declarative workflow.
2. Provider, resource, data source.
3. Variable, local, output.
4. State, backend, locking, workspace.
5. HCL type system, expression, `for_each`, `count` và `dynamic block`.
6. Project structure, file convention và module boundary.
7. Module, Registry và lifecycle.
8. Import, drift, troubleshooting.
9. Testing, refactoring và state migration an toàn.
10. Security, CI/CD, Terraform Cloud và production change management.
11. Cloud patterns như multi-region, serverless, zero-downtime, container infrastructure và multi-cloud.

## Cảnh Báo Lab Và Production

Không chạy `terraform apply` vào tài khoản cloud production nếu chưa đọc kỹ plan, chưa xác nhận đúng backend/workspace/account và chưa hiểu resource nào sẽ được tạo, thay đổi hoặc xóa.

Với lab, nên tạo thư mục riêng:

```bash
mkdir terraform-lab
cd terraform-lab
terraform version
```

## Related Pages

- [Core Concepts and Workflow](./01-core-concepts-and-workflow.md)
- [Terraform Core Concepts Lab Notes](./10-terraform-core-concepts-lab-notes.md)
- [State, Backend and Workspace](./02-state-backend-and-workspace.md)
- [HCL Language, Types and Expressions](./07-hcl-language-types-and-expressions.md)
- [Project Structure and Conventions](./06-project-structure-and-conventions.md)
- [Security, CI/CD and Production Practices](./05-security-cicd-and-production-practices.md)
- [Terraform Cloud and Registry](./08-terraform-cloud-and-registry.md)
- [Cloud Patterns and Advanced Use Cases](./09-cloud-patterns-and-advanced-use-cases.md)
- [Testing, Refactoring and Provider Development](./11-testing-refactoring-and-provider-development.md)
