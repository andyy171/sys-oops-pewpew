# Platform Engineering And Infrastructure As Product

Infrastructure as a product là cách thiết kế platform nội bộ như một sản phẩm phục vụ developer và workload team. Hạ tầng không chỉ là server, network, storage hoặc ticket cấp tài nguyên; nó là một tập service có interface rõ, guardrails rõ và khả năng self-service có kiểm soát.

## Khi Nào Cần

- Nhiều team cùng deploy workload lên một nền tảng chung.
- Ticket thủ công trở thành bottleneck cho release hoặc environment provisioning.
- Mỗi team tự dựng pipeline, secret, monitoring hoặc network policy theo cách riêng.
- Security/compliance cần được áp dụng đồng nhất nhưng không muốn chặn tốc độ phát triển.

## Product Thinking

Platform team nên hoạt động như một product team:

- user chính là developer, SRE, app team hoặc data team;
- service catalog mô tả rõ platform cung cấp gì và không cung cấp gì;
- API, portal, template hoặc pipeline là interface của sản phẩm;
- adoption, lead time, failure rate và developer satisfaction là tín hiệu quan trọng, không chỉ uptime;
- documentation, support path và migration guide là một phần của sản phẩm.

## Guardrails Vs Gatekeeping

Gatekeeping bắt mọi thay đổi đi qua phê duyệt thủ công. Guardrails cho phép self-service nhưng giới hạn rủi ro bằng policy, quota, default, template và audit.

| Cách tiếp cận | Hệ quả |
|---|---|
| Gatekeeping nặng | chậm, tạo shadow IT, phụ thuộc cá nhân |
| Self-service không guardrails | nhanh lúc đầu, dễ drift và khó audit |
| Self-service có guardrails | tốc độ tốt hơn nhưng vẫn giữ chuẩn vận hành |

## Service Catalog

Một service catalog tốt nên nói rõ:

- workload type được hỗ trợ;
- SLO hoặc expectation vận hành;
- request, limit, quota và cost model;
- security baseline và exception path;
- backup/restore hoặc data responsibility;
- owner, escalation và lifecycle policy.

## Failure Modes

- Platform chỉ là tập script rời rạc, không có product owner.
- Developer không hiểu guardrails nên coi platform là rào cản.
- Service catalog quá rộng, team platform không đủ sức vận hành.
- Platform ép một mô hình cho mọi workload, làm mất phù hợp kiến trúc.
- Không có exit strategy, khiến app team bị khóa vào abstraction nội bộ.

## Trang Liên Quan

- [Infrastructure Consistency](./05-infrastructure-consistency-and-platform-thinking.md)
- [Control Vs Abstraction](../02-tradeoffs/04-control-vs-abstraction.md)
- [Scalability Vs Maintainability](../02-tradeoffs/03-scalability-vs-maintainability.md)
- [SRE Concepts](../05-sre-and-operations-principles/01-sre-concepts.md)
