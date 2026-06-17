# Terraform Testing, Refactoring and Provider Development

## Mục Tiêu

Testing và refactoring trong Terraform nhằm thay đổi code hạ tầng mà không vô tình phá resource thật. Provider development là chủ đề nâng cao hơn: viết provider khi API nội bộ hoặc hệ thống riêng chưa có provider phù hợp.

Ba nhóm này liên quan với nhau ở cùng một nguyên tắc vận hành:

```text
code thay đổi
-> plan/test phát hiện tác động
-> state mapping vẫn đúng
-> provider/API thực thi thay đổi
-> validate resource thật
```

## Testing Terraform

Terraform test nên kiểm tra cả cấu trúc code lẫn tác động dự kiến:

- `terraform fmt -check` để giữ format nhất quán.
- `terraform validate` để bắt lỗi cú pháp, provider schema và tham chiếu cơ bản.
- `terraform plan` để review create/update/replace/destroy.
- Static analysis hoặc policy check để bắt public exposure, IAM quá rộng, secret trong code, tag thiếu hoặc resource nguy hiểm.
- Test module bằng fixture nhỏ, input rõ ràng và output có thể assert.

Với module dùng chung, nên có bộ input tối thiểu và input production-like. Không nên test bằng production account thật nếu chưa có quota, isolation, cleanup và cost guardrail.

## Refactor Terraform Code An Toàn

Refactor Terraform không chỉ là đổi file hoặc đổi tên resource. Điều quan trọng là Terraform address trong state phải được chuyển đúng sang address mới.

Các tình huống thường gặp:

- tách resource từ root module vào child module;
- đổi tên resource hoặc module để dễ hiểu hơn;
- chuyển từ resource đơn lẻ sang `for_each`;
- gom logic lặp lại thành module;
- import resource tồn tại sẵn rồi đưa vào code chuẩn.

Workflow an toàn:

```bash
terraform fmt -check
terraform validate
terraform state list
terraform plan
terraform state mv <old-address> <new-address>
terraform plan
```

Với Terraform hiện đại, ưu tiên `moved` block khi refactor có thể mô tả bằng code. `moved` block giúp migration có thể review qua pull request và chạy lại trong pipeline thay vì chỉ là thao tác CLI cục bộ.

## Import Và State Movement

`terraform import` đưa object đã tồn tại ngoài thực tế vào state. Import không tự viết module tốt cho bạn; sau import vẫn cần viết HCL khớp với resource thật.

```bash
terraform import <resource-address> <remote-id>
terraform plan
```

Sau import, plan phải được đọc kỹ. Nếu Terraform muốn replace hoặc update nhiều field ngoài ý muốn, code chưa mô tả đúng trạng thái thật hoặc provider đang normalize attribute khác với kỳ vọng.

Không sửa `terraform.tfstate` trực tiếp bằng editor trừ tình huống khẩn cấp đã có backup state, hiểu rõ JSON state và có phương án rollback. Với production, thao tác `state mv`, `state rm`, import hoặc moved block đều phải đi kèm plan trước/sau.

## Provider Development Mental Model

Terraform provider là lớp chuyển HCL và state thành API call tới hệ thống thật. Một resource provider thường cần ánh xạ:

```text
schema
-> create
-> read
-> update
-> delete
-> import/state mapping
```

Các điểm cần thiết kế cẩn thận:

- Schema phân biệt required, optional, computed và sensitive attribute.
- `Read` phải phản ánh trạng thái thật và xử lý object đã bị xóa ngoài Terraform.
- `Create` và `Update` cần idempotent theo API backend, tránh tạo duplicate khi retry.
- `Delete` cần xử lý eventual consistency và timeout.
- Sensitive field không nên ghi log; nếu provider phải lưu vào state, state phải được bảo vệ như secret.
- Acceptance test nên chạy trên môi trường cô lập, có cleanup và quota/cost guardrail.

Provider tự viết là lựa chọn cuối khi không có provider chính thức hoặc API nội bộ quá đặc thù. Nếu chỉ cần gọi script tạm thời, cân nhắc tách logic sang automation khác thay vì nhét imperative workflow vào Terraform provider/provisioner.

## Rủi Ro Production

- `terraform state mv` sai address có thể làm Terraform mất mapping resource.
- `state rm` làm Terraform quên resource, nhưng không xóa resource thật; lần sau có thể tạo trùng nếu code vẫn tồn tại.
- Import thiếu HCL tương ứng làm plan tiếp theo không ổn định.
- Refactor từ `count` sang `for_each` có thể đổi identity key và gây recreate hàng loạt nếu không map state cẩn thận.
- Provider custom có bug trong `Read` hoặc diff logic có thể tạo drift giả hoặc thay đổi resource ngoài ý muốn.

## Trang Liên Quan

- [State, Backend and Workspace](./02-state-backend-and-workspace.md)
- [Modules, Data Sources and Lifecycle](./03-modules-data-and-lifecycle.md)
- [Operations and Troubleshooting](./04-operations-and-troubleshooting.md)
- [Security, CI/CD and Production Practices](./05-security-cicd-and-production-practices.md)
