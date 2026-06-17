# Scripting Automation With Bash, PowerShell And Python

## Overview

Scripting trong vận hành hạ tầng là kỹ năng "glue code": nối command, API, file, log, SSH, Git và scheduler thành workflow lặp lại được. Bash, PowerShell và Python đều làm được automation, nhưng mỗi ngôn ngữ phù hợp với một lớp khác nhau.

Note này chuyển hóa từ tài liệu inbox `Scripting-Automation-with-Bash_-PowerShell_-and-python.docx` ở mức mental model và pattern, không chép nội dung sách.

## Chọn Công Cụ Theo Bài Toán

| Công cụ | Phù hợp | Tránh dùng khi |
|---|---|---|
| Bash | Linux command orchestration, pipeline text, cron job nhỏ, glue quanh CLI | Logic phức tạp, xử lý JSON/XML lớn, cần test/structure tốt |
| PowerShell | Windows/AD/Hyper-V/Azure/Microsoft ecosystem, object pipeline | Môi trường Linux tối giản không có PowerShell hoặc tác vụ cần POSIX shell portable |
| Python | API automation, file processing, report, JSON/YAML/XML, retry/timeout, workflow nhiều bước | Chỉ cần một pipeline shell rất ngắn |

Nguyên tắc: script tốt không phải script dài nhất, mà là script có input/output rõ, lỗi rõ, có dry-run khi thay đổi hệ thống và có log đủ để debug.

## Automation Flow

```text
source of truth / input
  -> validate arguments and environment
  -> collect current state
  -> plan or dry-run
  -> execute scoped change
  -> log result
  -> verify final state
```

Với tác vụ production, nên tách rõ bước quan sát và bước thay đổi. Ví dụ script backup nên kiểm tra disk space, target path, permission và retention trước khi xóa hoặc overwrite dữ liệu cũ.

## Pattern Thường Gặp

- Text processing: grep/sed/awk trong Bash; `Select-String`, object pipeline trong PowerShell; `re`, `csv`, `json`, `pathlib` trong Python.
- Scheduled jobs: cron/systemd timer trên Linux, Task Scheduler trên Windows.
- Remote execution: SSH, WinRM, cloud CLI hoặc API.
- File conversion: JSON/YAML/XML/CSV, report HTML/Markdown.
- Backup script: snapshot/copy/verify/retention/log.
- Git automation: pre-commit hooks, release helper, repository hygiene check.
- VM automation: KVM/libvirt, Hyper-V hoặc cloud API.

## Safety Checklist

- Có `--dry-run` hoặc `-WhatIf` cho thao tác thay đổi dữ liệu/hạ tầng.
- Không hardcode secret; đọc từ secret manager, environment hoặc file được bảo vệ.
- Có timeout/retry cho network/API call.
- Log đủ input, target, action, result; không log token/password.
- Dùng exit code rõ để CI/CD hoặc scheduler phát hiện failure.
- Với script xóa/sửa hàng loạt, bắt đầu bằng list/preview trước khi execute.

## Bash Practices

```bash
set -euo pipefail

log() {
  printf '%s %s\n' "$(date -Is)" "$*"
}
```

Lưu ý:

- Quote biến: `"$var"`.
- Dùng `mktemp` cho file tạm.
- Kiểm tra command tồn tại bằng `command -v`.
- Tránh parse output phức tạp nếu công cụ có JSON/YAML output.

## PowerShell Practices

```powershell
[CmdletBinding(SupportsShouldProcess)]
param(
  [Parameter(Mandatory)]
  [string]$Target
)

if ($PSCmdlet.ShouldProcess($Target, "Apply change")) {
  # scoped action
}
```

PowerShell mạnh vì pipeline truyền object, không chỉ text. Khi automation Windows, nên ưu tiên cmdlet trả object thay vì parse chuỗi nếu có thể.

## Python Practices

```python
from pathlib import Path
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
```

Python phù hợp khi script cần cấu trúc, test, retry, API client, xử lý dữ liệu hoặc report. Dùng `argparse`, `logging`, `pathlib`, `subprocess.run(..., check=True, timeout=...)` và validate input trước khi gọi command hệ thống.

## Trang Liên Quan

- [Python Everyday Automation Patterns For Ops](./01-python-everyday-automation-patterns-for-ops.md)
- [Shell, Basic Commands, Pipe và Redirection](../../02-core-infrastructure/01-linux/04-shell-automation-advanced/01-shell-basic-commands-pipe-redirection.md)
- [Bash Scripting, cron và systemd timer](../../02-core-infrastructure/01-linux/04-shell-automation-advanced/03-bash-scripting-cron-systemd-timer.md)
- [Terraform Project Structure and Conventions](../04-infrastructure-as-code/01-terraform/06-project-structure-and-conventions.md)
