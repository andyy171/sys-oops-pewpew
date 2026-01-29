# "Các lệnh tham khảo cho System Monitoring"
---

# CPU Monitoring
```bash
#!/bin/bash
# CPU Monitoring Script
THRESHOLD=90
LOG_FILE="/var/log/cpu_monitor.log"

# Lấy CPU usage từ /proc/stat
cpu_usage() {
  awk '/^cpu /{usage=($2+$4)*100/($2+$4+$5); printf "%.0f", usage}' /proc/stat
}

USAGE=$(cpu_usage)

# Ghi log và cảnh báo nếu vượt ngưỡng
echo "$(date '+%Y-%m-%d %H:%M:%S') - CPU Usage: ${USAGE}%" >> "$LOG_FILE"

if [ "$USAGE" -gt "$THRESHOLD" ]; then
  echo "ALERT: High CPU usage detected: ${USAGE}%" >> "$LOG_FILE"
  # Thêm lệnh gửi cảnh báo tại đây (email, slack, etc.)
fi

# Log rotation
tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"

## Save as cpu_monitor.sh
## chmod +x cpu_monitor.sh
## ad to crontab
```
# Memory Monitoring
```bash
#!/bin/bash
# Memory Monitoring Script
THRESHOLD=90
LOG_FILE="/var/log/memory_monitor.log"

# Tính toán memory usage
memory_usage() {
  total_mem=$(awk '/MemTotal:/ {print $2}' /proc/meminfo)
  available_mem=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
  echo $((100 - (100 * available_mem / total_mem)))
}

USAGE=$(memory_usage)

# Ghi log và cảnh báo
echo "$(date '+%Y-%m-%d %H:%M:%S') - Memory Usage: ${USAGE}%" >> "$LOG_FILE"

if [ "$USAGE" -gt "$THRESHOLD" ]; then
  echo "ALERT: High Memory usage detected: ${USAGE}%" >> "$LOG_FILE"
  # Thêm lệnh gửi cảnh báo tại đây
fi

# Log rotation
tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
```
# Disk Monitoring 

```bash
#!/bin/bash
# Disk Monitoring Script
THRESHOLD=90
LOG_FILE="/var/log/disk_monitor.log"

# Lấy disk usage cho partition root
disk_usage() {
  df -P / | awk 'NR==2 {gsub(/%/, ""); print $5}'
}

USAGE=$(disk_usage)

# Ghi log và cảnh báo
echo "$(date '+%Y-%m-%d %H:%M:%S') - Disk Usage: ${USAGE}%" >> "$LOG_FILE"

if [ "$USAGE" -gt "$THRESHOLD" ]; then
  echo "ALERT: High Disk usage detected: ${USAGE}%" >> "$LOG_FILE"
  # Thêm lệnh gửi cảnh báo tại đây
fi

# Log rotation
tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
```
# Process Monitoring

```bash
#!/bin/bash
# Process Monitoring Script
LOG_FILE="/var/log/process_monitor.log"
PROCESS_LIST=("sshd" "nginx" "mysql")

for process in "${PROCESS_LIST[@]}"; do
  if ! pgrep -x "$process" > /dev/null; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - WARNING: Process $process is not running" >> "$LOG_FILE"
    # Thêm lệnh khởi động lại process tại đây
    # systemctl start $process
  fi
done

# Log rotation
tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
```

# System Load Monitoring
Theo dõi tải hệ thống và cảnh báo khi quá cao
```bash
#!/bin/bash
# System Load Monitoring Script
THRESHOLD=$(nproc)  # Sử dụng số core làm ngưỡng
LOG_FILE="/var/log/load_monitor.log"

# Lấy load average 1 phút
load_avg() {
  awk '{print $1}' /proc/loadavg
}

LOAD=$(load_avg)

# Ghi log và cảnh báo
echo "$(date '+%Y-%m-%d %H:%M:%S') - System Load: ${LOAD}" >> "$LOG_FILE"

if [ $(echo "$LOAD > $THRESHOLD" | bc -l) -eq 1 ]; then
  echo "ALERT: High system load detected: ${LOAD}" >> "$LOG_FILE"
  # Thêm lệnh gửi cảnh báo tại đây
fi

# Log rotation
tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
```

# crontab config 
```bash
# Thêm vào crontab -e
# Chạy CPU monitoring mỗi 5 phút
*/5 * * * * /path/to/cpu_monitor.sh

# Chạy Memory monitoring mỗi 5 phút
*/5 * * * * /path/to/memory_monitor.sh

# Chạy Disk monitoring mỗi 30 phút
*/30 * * * * /path/to/disk_monitor.sh

# Chạy Process monitoring mỗi 5 phút
*/5 * * * * /path/to/process_monitor.sh

# Chạy Load monitoring mỗi 5 phút
*/5 * * * * /path/to/load_monitor.sh
```

# Lưu ý 
- Đảm bảo thư mục log tồn tại: Tạo thư mục log nếu chưa có:

```bash
sudo mkdir -p /var/log/
sudo touch /var/log/{cpu,memory,disk,process,load}_monitor.log
sudo chmod 644 /var/log/*_monitor.log
```
- Điều chỉnh ngưỡng cảnh báo: Thay đổi giá trị THRESHOLD trong mỗi script theo nhu cầu