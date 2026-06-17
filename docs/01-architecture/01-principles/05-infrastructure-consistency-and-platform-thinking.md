# Infrastructure Consistency

Infrastructure consistency là nguyên tắc giữ cho compute, network, storage, configuration, security control và observability được triển khai theo một chuẩn có thể lặp lại. Mục tiêu không phải làm mọi service giống hệt nhau, mà là giảm drift để hệ thống dễ dự đoán, dễ audit và dễ vận hành khi scale.

## Vì Sao Quan Trọng

Ở giai đoạn đầu, hạ tầng thường đơn giản và tương đối đồng nhất. Khi số team, service và môi trường tăng lên, các thay đổi tạm thời dễ trở thành cấu hình lâu dài. Kết quả là dev, staging và production khác nhau; mỗi service có deployment, monitoring hoặc security policy riêng; incident mất nhiều thời gian hơn vì không còn một baseline chung.

Configuration drift là sai lệch giữa desired state được định nghĩa bằng template, code hoặc runbook và actual state đang chạy. Drift không chỉ gây lỗi cấu hình, mà còn làm mất khả năng so sánh giữa môi trường và làm suy yếu compliance.

## Nguyên Nhân Gây Drift

- Sửa trực tiếp trên server hoặc console để xử lý gấp, nhưng không đưa thay đổi về source of truth.
- Mỗi team tự chọn tool deployment, monitoring, secret hoặc naming convention.
- Dev, staging và production không dùng cùng baseline image, network policy hoặc dependency model.
- Capacity hoặc hardware khác nhau khiến cùng một service có behavior khác nhau giữa node/site.
- Security exception không có expiry, owner hoặc audit trail.

## Nguyên Tắc Thiết Kế

- Dùng blueprint/template chuẩn cho workload, network, storage, identity và observability.
- Đưa hạ tầng về source of truth bằng IaC, image chuẩn, policy-as-code hoặc reconciliation loop.
- Giữ môi trường giống nhau ở phần behavior quan trọng: config shape, dependency, policy, alert, backup và release process.
- Tích hợp security và compliance từ đầu thay vì thêm sau khi production đã chạy.
- Chuẩn hóa metric, log, alert và ownership để incident không phụ thuộc vào trí nhớ của một cá nhân.

## Desired State Vs Actual State

Một platform tốt cần phân biệt rõ:

```text
desired state in source of truth
  -> provisioning / deployment / policy engine
  -> actual runtime state
  -> drift detection / reconciliation / audit
```

Không phải drift nào cũng cần tự động sửa ngay. Với production, cần phân loại:

| Loại drift | Cách xử lý |
|---|---|
| Drift do thao tác khẩn cấp | ghi nhận, backport vào source of truth hoặc rollback |
| Drift do policy exception | owner, expiry, risk acceptance |
| Drift do tool không quản lý được | tạo runbook hoặc đổi boundary quản lý |
| Drift gây rủi ro bảo mật/availability | ưu tiên remediation và post-incident review |

## Dấu Hiệu Áp Dụng Sai

- "Chuẩn hóa" thành một template quá cứng khiến workload hợp lệ phải tìm đường vòng.
- Tất cả service dùng chung một pipeline nhưng không có override an toàn.
- Platform team chỉ enforce policy mà không cung cấp self-service hoặc tài liệu rõ.
- Drift detection tạo alert ồn nhưng không có owner/action.

## Trang Liên Quan

- [Platform Engineering And Infrastructure As Product](./06-platform-engineering-and-infrastructure-as-product.md)
- [Control Vs Abstraction](../02-tradeoffs/04-control-vs-abstraction.md)
- [PoC Evaluation Framework](../02-tradeoffs/05-poc-evaluation-framework.md)
- [Workload Patterns](./04-workload-patterns.md)
- [Single-Tenant Private Cloud For Data Workloads](../03-patterns/05-single-tenant-private-cloud-for-data-workloads.md)
