# Python Everyday Automation Patterns For Ops

## Overview

Tài liệu `_inbox/50-EVERYDAY-TASKS-TO-AUTOMATE-WITH-PYTHON.docx` là một cookbook rất rộng: backup, image resize, email, scraping, data analysis, PDF/document conversion, scheduler, report, password manager, remote desktop, speech, chatbot và nhiều tool cá nhân khác.

Với vault hạ tầng, giá trị tái sử dụng nằm ở pattern, không phải copy từng script. Note này gom các nhóm automation có ích cho vận hành và các guardrail để biến một script Python thành tool đáng tin hơn.

## Nhóm Automation Hữu Ích Cho Ops

| Nhóm | Ví dụ task | Library thường gặp | Lưu ý vận hành |
|---|---|---|---|
| File và backup | backup folder, file organizer, PDF merge, document convert | `pathlib`, `shutil`, `zipfile`, `PyPDF2`, `pypandoc` | cần dry-run, checksum, overwrite policy |
| Data/report | data cleaning, survey analysis, report generator, chart | `pandas`, `csv`, `matplotlib`, `reportlab` | validate schema, không ghi đè raw data |
| Notification | email automation, alert, weather/news reminder | `smtplib`, `email`, `requests`, `feedparser` | quản lý secret, rate limit, retry |
| Web/API polling | price checker, SEO monitor, content scraper, exchange rate | `requests`, `BeautifulSoup` | timeout, user-agent, robots/policy, backoff |
| Scheduling | recurring task, reminder, time tracker | `schedule`, `datetime`, `cron`, systemd timer | tránh chạy trùng, log rõ exit code |
| Inventory/state | inventory tool, expense tracker, meeting scheduler | `sqlite3`, `json`, `csv` | backup DB, migration đơn giản |
| Network check | network speed test, endpoint check | `socket`, `requests`, `speedtest-cli` | phân biệt app latency và network latency |

## Guardrail Cho Script Production-Like

Một script dùng trong vận hành nên có:

- `--dry-run` cho thao tác ghi/xóa/sửa.
- `--config` hoặc environment variables cho cấu hình.
- Logging có timestamp, level và context.
- Timeout cho network call.
- Retry có giới hạn và backoff.
- Exit code rõ để cron/systemd/CI biết thành công hay lỗi.
- Không hard-code secret trong code.
- Validate input path, file type, schema hoặc response.
- Không ghi đè dữ liệu nếu chưa backup hoặc chưa bật flag rõ ràng.
- Test nhỏ cho logic quan trọng.

## Skeleton Cơ Bản

```python
import argparse
import logging
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    source = Path(args.source)
    destination = Path(args.destination)

    if not source.exists():
        raise SystemExit(f"source does not exist: {source}")

    logging.info("source=%s destination=%s dry_run=%s", source, destination, args.dry_run)

    if args.dry_run:
        logging.info("dry-run only; no changes were made")
        return

    destination.mkdir(parents=True, exist_ok=True)
    # Thực hiện thao tác thật ở đây.


if __name__ == "__main__":
    main()
```

## Pattern: Backup File/Folder

Backup script nên có:

- Timestamp hoặc versioned directory.
- Loại trừ file tạm/cache nếu cần.
- Checksum hoặc ít nhất là count/size summary.
- Retention policy rõ ràng.
- Log vị trí backup.
- Restore test định kỳ.

Không nên chỉ có "copy thành công" rồi xem là đủ. Backup không được test restore thì mới là hy vọng, chưa phải năng lực khôi phục.

## Pattern: Web/API Monitor

Khi viết script gọi web/API:

```python
import requests

response = requests.get("https://example.com/health", timeout=10)
response.raise_for_status()
```

Checklist:

- Luôn đặt `timeout`.
- Kiểm tra HTTP status bằng `raise_for_status()` hoặc logic tương đương.
- Có retry/backoff cho lỗi tạm thời.
- Không log token/header nhạy cảm.
- Tôn trọng rate limit và policy của site/API.
- Với scraping, ưu tiên API chính thức nếu có.

## Pattern: Email Và Notification

Không hard-code password SMTP trong script. Dùng secret manager, environment variable hoặc file config được giới hạn quyền.

```text
SMTP_USERNAME=<user>
SMTP_PASSWORD=<PASSWORD>
```

Nếu script gửi alert:

- Alert phải có tên hệ thống, môi trường, severity và hành động gợi ý.
- Có chống spam hoặc cooldown.
- Có log để audit vì sao alert được gửi.

## Pattern: Data Processing

Với `pandas`/CSV/report:

- Giữ raw input bất biến.
- Ghi output vào path mới hoặc yêu cầu `--overwrite`.
- Validate cột bắt buộc trước khi xử lý.
- Ghi summary: số row đọc, số row bỏ qua, số row ghi.
- Nếu dữ liệu nhạy cảm, không đưa full sample vào log.

## Pattern: Password Manager Và Remote Desktop

Các task như password manager, remote desktop controller, social media bot hoặc voice assistant có rủi ro cao hơn script file/report bình thường.

Chỉ đưa vào vận hành khi có:

- Threat model rõ ràng.
- Secret encryption và key management đúng.
- Authentication/authorization.
- Audit log.
- Network exposure được giới hạn.
- Review bảo mật trước khi dùng thật.

Với vault này, các task đó nên được xem là ý tưởng học tập, không phải runbook production.

## Scheduling

Có thể chạy script bằng cron hoặc systemd timer.

Cron phù hợp cho task đơn giản:

```bash
crontab -e
```

systemd timer phù hợp hơn khi cần log, dependency, restart policy và quản lý service rõ:

```bash
systemctl list-timers
journalctl -u <service-name> --since "1 hour ago"
```

Tránh để hai instance chạy chồng lên nhau. Có thể dùng lock file hoặc systemd service behavior phù hợp.

## Related Pages

- [Bash Scripting, cron và systemd timer](../../02-core-infrastructure/01-linux/04-shell-automation-advanced/03-bash-scripting-cron-systemd-timer.md)
- [Sysadmin Scripts Collection](../../02-core-infrastructure/01-linux/04-shell-automation-advanced/08-sysadmin-scripts-collection.md)
- [Pipeline stages build, test, deploy](../03-cicd-devops-integration/01-continuous-integration/02-Pipeline%20stages%20build,%20test,%20deploy.md)
