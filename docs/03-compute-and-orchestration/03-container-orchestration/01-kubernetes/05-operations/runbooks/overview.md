# Kubernetes Operations Runbooks

Folder này chứa các thao tác vận hành cần mở nhanh khi có sự cố hoặc maintenance. Mỗi runbook nên tập trung vào một tình huống cụ thể, có precheck, thao tác, validation và rollback rõ ràng.

## Runbooks

- [Renew kubeadm control-plane certificates](./01-renew-kubeadm-certificates.md)

## Rule Khi Viết Runbook

- Bắt đầu bằng triệu chứng và phạm vi áp dụng.
- Có precheck read-only trước khi thay đổi.
- Có backup hoặc rollback nếu thao tác có rủi ro.
- Command phải có language tag.
- Không dùng giá trị thật như token, kubeconfig, private key hoặc IP nội bộ nhạy cảm.
- Với cluster HA, nêu rõ thao tác tuần tự từng node nếu có rủi ro quorum/control plane.
