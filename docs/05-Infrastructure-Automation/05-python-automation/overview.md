# Python Automation

## Overview

Folder này gom các pattern dùng Python để tự động hóa công việc vận hành, xử lý file, báo cáo, kiểm tra định kỳ, notification, web/API polling và các script hỗ trợ workflow.

Không nên xem Python automation chỉ là tập script lẻ. Với hạ tầng, một script tốt cần có cấu hình rõ ràng, logging, dry-run, error handling, timeout, retry, idempotency và cách rollback/khôi phục nếu nó thay đổi dữ liệu.

## Notes

- [Python Everyday Automation Patterns For Ops](./01-python-everyday-automation-patterns-for-ops.md)
- [Scripting Automation With Bash, PowerShell And Python](./02-scripting-automation-bash-powershell-python.md)

## Placement Rules

- Đưa script liên quan trực tiếp tới Linux host vào Linux shell/automation nếu nó chủ yếu là shell/sysadmin.
- Đưa script liên quan CI/CD vào CI/CD section nếu nó là pipeline logic.
- Đưa pattern Python tổng quát, file/data/report/API/notification vào folder này.
