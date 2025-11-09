---
title: "Các lệnh tham khảo cho Log Analysis  "
date: 2025-01-01T00:00:00+07:00
draft: false
---

# Trích xuất và phân tích các dòng lỗi từ log files
```bash
#!/bin/bash
# Log Analyzer Script
LOG_FILE="/path/to/logfile.log"
ERROR_LOG="/var/log/error_analysis.log"
ANALYSIS_DIR="/var/log/analysis"

# Tạo thư mục phân tích nếu chưa tồn tại
mkdir -p "$ANALYSIS_DIR"

# Kiểm tra file log tồn tại
if [ ! -f "$LOG_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Log file $LOG_FILE not found" >> "$ERROR_LOG"
    exit 1
fi

# Tạo timestamp cho output files
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Trích xuất các dòng có chứa "ERROR"
ERROR_OUTPUT="$ANALYSIS_DIR/errors_$TIMESTAMP.txt"
grep -i "ERROR" "$LOG_FILE" > "$ERROR_OUTPUT"

# Trích xuất các dòng có chứa "WARN"
WARN_OUTPUT="$ANALYSIS_DIR/warnings_$TIMESTAMP.txt"
grep -i "WARN" "$LOG_FILE" > "$WARN_OUTPUT"

# Đếm số lượng errors và warnings
ERROR_COUNT=$(wc -l < "$ERROR_OUTPUT")
WARN_COUNT=$(wc -l < "$WARN_OUTPUT")

# Ghi kết quả phân tích
echo "$(date '+%Y-%m-%d %H:%M:%S') - Log analysis completed:" >> "$ERROR_LOG"
echo "  Errors found: $ERROR_COUNT" >> "$ERROR_LOG"
echo "  Warnings found: $WARN_COUNT" >> "$ERROR_LOG"
echo "  Error log: $ERROR_OUTPUT" >> "$ERROR_LOG"
echo "  Warning log: $WARN_OUTPUT" >> "$ERROR_LOG"

# Nếu có nhiều hơn 10 errors, gửi cảnh báo
if [ "$ERROR_COUNT" -gt 10 ]; then
    echo "ALERT: High number of errors ($ERROR_COUNT) detected in $LOG_FILE" >> "$ERROR_LOG"
    # Thêm lệnh gửi cảnh báo tại đây
fi

# Giữ lại 7 ngày log analysis
find "$ANALYSIS_DIR" -name "*.txt" -mtime +7 -delete

# Log rotation cho error log
tail -n 1000 "$ERROR_LOG" > "${ERROR_LOG}.tmp" && mv "${ERROR_LOG}.tmp" "$ERROR_LOG"
```

# Phân tích log web server để thống kê truy cập
```bash
#!/bin/bash
# Web Server Log Analyzer Script
LOG_FILE="/var/log/apache2/access.log"
ANALYSIS_LOG="/var/log/web_analysis.log"
ANALYSIS_DIR="/var/log/web_analysis"

# Tạo thư mục phân tích nếu chưa tồn tại
mkdir -p "$ANALYSIS_DIR"

# Kiểm tra file log tồn tại
if [ ! -f "$LOG_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Web log file $LOG_FILE not found" >> "$ANALYSIS_LOG"
    exit 1
fi

# Tạo timestamp cho output files
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Phân tích địa chỉ IP truy cập
IP_OUTPUT="$ANALYSIS_DIR/ip_analysis_$TIMESTAMP.txt"
awk '{print $1}' "$LOG_FILE" | sort | uniq -c | sort -nr > "$IP_OUTPUT"

# Phân tích các response code
STATUS_OUTPUT="$ANALYSIS_DIR/status_codes_$TIMESTAMP.txt"
awk '{print $9}' "$LOG_FILE" | sort | uniq -c | sort -nr > "$STATUS_OUTPUT"

# Phân tích các URL được truy cập nhiều nhất
URL_OUTPUT="$ANALYSIS_DIR/urls_$TIMESTAMP.txt"
awk '{print $7}' "$LOG_FILE" | sort | uniq -c | sort -nr | head -20 > "$URL_OUTPUT"

# Phân tích user agents
UA_OUTPUT="$ANALYSIS_DIR/user_agents_$TIMESTAMP.txt"
awk -F'"' '{print $6}' "$LOG_FILE" | sort | uniq -c | sort -nr | head -10 > "$UA_OUTPUT"

# Thống kê tổng số requests
TOTAL_REQUESTS=$(wc -l < "$LOG_FILE")
UNIQUE_IPS=$(wc -l < "$IP_OUTPUT")

# Ghi kết quả phân tích
echo "$(date '+%Y-%m-%d %H:%M:%S') - Web server log analysis completed:" >> "$ANALYSIS_LOG"
echo "  Total requests: $TOTAL_REQUESTS" >> "$ANALYSIS_LOG"
echo "  Unique IP addresses: $UNIQUE_IPS" >> "$ANALYSIS_LOG"
echo "  Analysis files created in $ANALYSIS_DIR" >> "$ANALYSIS_LOG"

# Kiểm tra các response code lỗi (4xx, 5xx)
ERROR_CODES=$(awk '$9 ~ /^[45][0-9][0-9]$/ {print $9}' "$LOG_FILE" | wc -l)
if [ "$ERROR_CODES" -gt 0 ]; then
    ERROR_RATE=$((ERROR_CODES * 100 / TOTAL_REQUESTS))
    echo "  Error responses: $ERROR_CODES ($ERROR_RATE%)" >> "$ANALYSIS_LOG"
    
    # Nếu error rate cao hơn 5%, gửi cảnh báo
    if [ "$ERROR_RATE" -gt 5 ]; then
        echo "ALERT: High error rate ($ERROR_RATE%) detected in web server logs" >> "$ANALYSIS_LOG"
        # Thêm lệnh gửi cảnh báo tại đây
    fi
fi

# Giữ lại 7 ngày log analysis
find "$ANALYSIS_DIR" -name "*.txt" -mtime +7 -delete

# Log rotation cho analysis log
tail -n 1000 "$ANALYSIS_LOG" > "${ANALYSIS_LOG}.tmp" && mv "${ANALYSIS_LOG}.tmp" "$ANALYSIS_LOG"
```

# Giám sát log file theo thời gian thực và cảnh báo khi phát hiện lỗi
```bash
#!/bin/bash
# Real-time Log Monitor Script
LOG_FILE="/path/to/logfile.log"
ALERT_LOG="/var/log/realtime_monitor.log"
KEYWORDS=("ERROR" "CRITICAL" "FAILED" "EXCEPTION")

# Kiểm tra file log tồn tại
if [ ! -f "$LOG_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Log file $LOG_FILE not found" >> "$ALERT_LOG"
    exit 1
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting real-time monitoring of $LOG_FILE" >> "$ALERT_LOG"

# Theo dõi log file theo thời gian thực
tail -F "$LOG_FILE" | while read line; do
    for keyword in "${KEYWORDS[@]}"; do
        if echo "$line" | grep -q -i "$keyword"; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - ALERT: Found '$keyword' in log: $line" >> "$ALERT_LOG"
            # Thêm lệnh gửi cảnh báo tại đây
        fi
    done
done
```

## Cấu Hình Crontab Mẫu
```bash
# Phân tích log hàng ngày vào lúc nửa đêm
0 0 * * * /path/to/log_analyzer.sh

# Phân tích web server log hàng ngày vào lúc 1 giờ sáng
0 1 * * * /path/to/web_log_analyzer.sh

# Khởi động real-time monitor khi hệ thống boot
@reboot /path/to/realtime_monitor.sh
```

