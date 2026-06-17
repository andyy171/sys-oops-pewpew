# Image Scanning, Vulnerability Gate Và Supply Chain

## Overview

Image scanning giúp phát hiện CVE, malware, package lỗi thời và cấu hình nguy hiểm trước khi image đi vào production. Nó không đảm bảo image an toàn tuyệt đối, nhưng là một lớp quan trọng trong defense in depth: source repo, build pipeline, registry, admission policy và runtime monitoring phải phối hợp với nhau.

## Mental Model

```text
source code -> build image -> scan -> sign/provenance -> push registry -> admission policy -> runtime monitoring
```

Scan nên chạy ít nhất ở hai điểm:

- CI/CD: fail sớm trước khi push/promote image.
- Registry/admission: chặn image đã biết không đạt policy trước khi deploy.

## Trivy, Clair Và Registry Scanner

Các tool như Trivy, Clair hoặc scanner tích hợp trong registry có thể phát hiện vulnerability dựa trên OS packages, language dependencies và metadata image. Kết quả scan thường noisy, nên policy phải phân biệt:

- severity: Critical/High/Medium/Low;
- exploitability: có exploit/path runtime thật không;
- fix availability: đã có package fix chưa;
- workload exposure: internet-facing, privileged, internal batch;
- exception owner và expiry.

Không nên biến mọi CVE thành deploy blocker vĩnh viễn. Một gate tốt chặn rủi ro cao có fix rõ, đồng thời cho phép exception có thời hạn và audit.

Scanner không phải magic bullet. Static image scanning thường giỏi phát hiện package đã biết, nhưng yếu hơn với:

- binary tự build không có metadata package rõ ràng;
- dependency được tải động khi runtime;
- malware/backdoor logic nằm trong code ứng dụng;
- container gọi outbound đến endpoint lạ sau khi chạy;
- cấu hình runtime như privileged mode, host mount, capability, seccomp/AppArmor/SELinux.

Vì vậy scanner nên được dùng cùng runtime control: policy admission, egress control, syscall/capability hardening, audit event và monitoring hành vi. Với production gate, phân biệt rõ scan đồng bộ chặn release và scan bất đồng bộ để cảnh báo image đã deploy khi CVE mới xuất hiện.

### Đánh Giá Scanner Bằng Fixture Có Chủ Ý

Một scanner tốt không chỉ là tool báo nhiều CVE nhất. Cần kiểm tra scanner bằng image fixture có chủ ý chứa nhiều dạng vấn đề:

- package OS có CVE rõ;
- dependency ngôn ngữ như npm, pip, gem;
- binary tự build hoặc đặt ở path bất thường;
- file secret giả để kiểm tra secret scanning;
- package tồn tại trong image nhưng không nằm trên runtime path.

Mục tiêu là biết scanner nhìn thấy gì và bỏ sót gì, không phải tạo image độc hại để dùng lại. Fixture này chỉ nên nằm trong lab/private registry, tag rõ `known-bad`, có owner và không được deploy. Khi so sánh scanner, đánh giá theo khả năng giải thích exploitability, fix availability, package path, false positive và policy integration, không chỉ theo số lượng finding.

## Third-Party Image Intake

Third-party image là dependency có blast radius lớn vì nó mang filesystem, entrypoint, package, user, exposed port và đôi khi cả behavior runtime không rõ nguồn gốc. Cấm tuyệt đối mọi third-party image thường không thực tế, nhưng allow tự do cũng không phù hợp production.

Quy trình intake nên gồm:

1. Xác minh nguồn: publisher, repository, tag policy, release cadence và support model.
2. Pull theo digest hoặc immutable tag, không dùng `latest`.
3. Scan image, tạo SBOM/provenance nếu platform hỗ trợ.
4. Chạy sandbox để quan sát process, port, file write, outbound network và privilege requirement.
5. Rebuild hoặc wrap lại từ artifact/source tin cậy khi image cần trở thành dependency lâu dài.
6. Gán owner nội bộ chịu trách nhiệm patch, exception, rollback và deprecation.

Guardrail quan trọng: image do bên thứ ba cung cấp không tự động trở thành "trusted" chỉ vì nó phổ biến. Nếu workload xử lý dữ liệu nhạy cảm, cần thêm network policy/egress allowlist, read-only filesystem, non-root user, secret scope hẹp và log/audit đủ để điều tra incident.

## Policy Gate

Ví dụ policy tư duy:

```text
deny deploy nếu image có Critical CVE có fix
warn nếu High CVE chưa có fix
allow exception bằng annotation/ticket có expiry
```

Admission controller hoặc policy engine có thể kiểm tra image digest, registry allowlist, signature hoặc vulnerability status. Với production, policy phải có message rõ để developer biết cần sửa base image, rebuild dependency hay xin exception.

## Non-Root Và Minimal Base Image

Hai quick wins:

- chạy process bằng non-root user trong Dockerfile hoặc `securityContext`;
- dùng base image tối giản như slim, distroless hoặc scratch khi team đã có debug/observability thay thế shell trong container.

Distroless/scratch giảm attack surface nhưng làm incident response khó hơn nếu runbook vẫn phụ thuộc `sh`, `curl`, package manager hoặc debug tool bên trong container. Cần chuẩn bị logs, metrics, traces, ephemeral container hoặc debug sidecar.

## Provenance, SLSA Và OpenSSF Scorecard

Image security không chỉ là scan binary cuối:

- SLSA giúp tăng mức minh bạch và integrity của build pipeline, artifact và provenance.
- OpenSSF Scorecard giúp đánh giá hygiene của dependency/source repo, ví dụ branch protection, pinned dependencies, fuzzing, token permissions.
- Image signing/provenance giúp admission policy biết image đến từ pipeline tin cậy, không chỉ từ registry tin cậy.

## Troubleshooting

| Symptom | Kiểm tra |
|---|---|
| Scan fail vì CVE trong base image | base image digest, upstream fix, rebuild cache |
| Kết quả scan khác nhau giữa CI và registry | database version của scanner, image digest có giống nhau không |
| Admission chặn image đã fix | image tag mutable, controller cache, digest chưa đổi |
| Quá nhiều false positive | policy severity, fix availability, exception process |
| Distroless khó debug | ephemeral container, debug image, logs/traces/metrics |

## Best Practices

- Deploy bằng digest hoặc immutable tag, không dựa vào `latest`.
- Scan trong CI và registry/admission nếu có thể.
- Không copy secret vào image hoặc bake secret vào layer.
- Rebuild định kỳ để nhận patch từ base image.
- Ký image hoặc lưu provenance cho workload quan trọng.
- Duy trì exception có owner, reason và expiry.
- Theo dõi CVE mới sau khi image đã deploy; scan một lần trước deploy là chưa đủ.

## Related Pages

- [Image Layer Và Dockerfile Best Practices](./Image layer, Dockerfile best practices.md)
- [Least Privilege & Rootless Container](./Least privilege & rootless container.md)
- [Private Registry, Nexus, Harbor](./Private registry, NexusHarbor.md)
- [Kubernetes RBAC, Pod Security Và Admission](../03-container-orchestration/01-kubernetes/04-security/01-rbac-pod-security-and-admission.md)
