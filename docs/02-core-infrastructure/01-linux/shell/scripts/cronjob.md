# Các lệnh tham khảo cho Service and Task Management 

## Lập lịch chạy script/task tự động với cron
```bash
#!/bin/bash
# Task Scheduler Script
SCRIPT_PATH="/path/to/your_script.sh"
CRON_SCHEDULE="0 2 * * *"
CRON_FILE="/etc/cron.d/custom_tasks"

# Kiểm tra script tồn tại
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "ERROR: Script $SCRIPT_PATH not found"
    exit 1
fi

# Đảm bảo script có quyền thực thi
chmod +x "$SCRIPT_PATH"

# Thêm task vào cron
echo "$CRON_SCHEDULE root $SCRIPT_PATH" | sudo tee -a "$CRON_FILE" > /dev/null

# Kiểm tra cron job đã được thêm
if sudo grep -q "$SCRIPT_PATH" "$CRON_FILE"; then
    echo "Task scheduled successfully: $CRON_SCHEDULE $SCRIPT_PATH"
else
    echo "ERROR: Failed to schedule task"
    exit 1
fi
```

## Khởi động lại service và kiểm tra trạng thái
```bash
#!/bin/bash
# Service Restart Script
SERVICE_NAME="nginx"
MAX_RETRIES=3
WAIT_TIME=5

# Kiểm tra service có tồn tại không
if ! systemctl list-unit-files | grep -q "^$SERVICE_NAME.service"; then
    echo "ERROR: Service $SERVICE_NAME does not exist"
    exit 1
fi

# Khởi động lại service
echo "Restarting $SERVICE_NAME..."
sudo systemctl restart "$SERVICE_NAME"

# Kiểm tra trạng thái sau khi restart
for ((i=1; i<=$MAX_RETRIES; i++)); do
    sleep $WAIT_TIME
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "✓ $SERVICE_NAME restarted successfully"
        exit 0
    fi
    echo "Attempt $i: Waiting for $SERVICE_NAME to start..."
done

echo "ERROR: Failed to restart $SERVICE_NAME after $MAX_RETRIES attempts"
exit 1
```

## Giám sát trạng thái các service quan trọng
```bash
#!/bin/bash
# Service Status Monitor
SERVICES=("nginx" "mysql" "ssh" "apache2")
LOG_FILE="/var/log/service_status.log"

for service in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "$(date): ✓ $service is running" >> "$LOG_FILE"
    else
        echo "$(date): ✗ $service is NOT running" >> "$LOG_FILE"
        # Tự động khởi động lại service không hoạt động
        sudo systemctl start "$service"
    fi
done
```

###  Quản lý nhiều services cùng lúc
```bash
#!/bin/bash
# Multiple Services Manager
ACTION="${1:-status}"  # start, stop, restart, status
SERVICES=("nginx" "mysql" "redis")

for service in "${SERVICES[@]}"; do
    echo "Service: $service - Action: $ACTION"
    sudo systemctl "$ACTION" "$service"
    echo "----------------------------------------"
done
```
chmod +x service_manager.sh
./service_manager.sh status    # Kiểm tra trạng thái
./service_manager.sh restart   # Khởi động lại tất cả
./service_manager.sh stop      # Dừng tất cả services

## Cron Job Management
```bash
#!/bin/bash
# Cron Job Management
ACTION="${1:-list}"  # list, add, remove

case $ACTION in
    list)
        echo "Current cron jobs:"
        crontab -l
        ;;
    add)
        echo "Adding new cron job"
        read -p "Schedule (e.g., 0 2 * * *): " schedule
        read -p "Command to execute: " command
        (crontab -l; echo "$schedule $command") | crontab -
        ;;
    remove)
        echo "Removing cron job"
        crontab -l
        read -p "Enter the line number to remove: " line_num
        crontab -l | sed "${line_num}d" | crontab -
        ;;
    *)
        echo "Usage: $0 [list|add|remove]"
        ;;
esac
```

chmod +x cron_manager.sh
./cron_manager.sh list    # Xem cron jobs
./cron_manager.sh add     # Thêm cron job mới
./cron_manager.sh remove  # Xóa cron job


## Cấu Hình Crontab Mẫu
Thêm vào crontab (crontab -e) để tự động hóa:

```bash
# Kiểm tra service mỗi 5 phút
*/5 * * * * /path/to/service_monitor.sh

# Khởi động lại service hàng ngày lúc 3 giờ sáng
0 3 * * * /path/to/restart_service.sh

# Backup dữ liệu hàng ngày lúc 2 giờ sáng
0 2 * * * /path/to/backup_script.sh
```