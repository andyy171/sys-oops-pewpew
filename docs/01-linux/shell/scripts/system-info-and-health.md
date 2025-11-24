# "Các lệnh tham khảo cho System Information and Health  "
---

#  Thu thập và lưu trữ thông tin chi tiết về hệ thống
```bash
#!/bin/bash
# System Information Script
OUTPUT_DIR="/var/log/system_info"
OUTPUT_FILE="$OUTPUT_DIR/system_info_$(date +%Y%m%d_%H%M%S).txt"
LOG_FILE="/var/log/system_info.log"

# Tạo thư mục output nếu chưa tồn tại
mkdir -p "$OUTPUT_DIR"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting system information collection" >> "$LOG_FILE"

# Thu thập thông tin hệ thống
{
    echo "==================== SYSTEM INFORMATION ===================="
    echo "Collection Time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "============================================================"
    echo ""
    
    echo "---------------------- HOST INFORMATION --------------------"
    echo "Hostname: $(hostname)"
    echo "FQDN: $(hostname -f 2>/dev/null || echo "Not available")"
    echo "Domain: $(domainname 2>/dev/null || echo "Not available")"
    echo ""
    
    echo "----------------------- OS INFORMATION ---------------------"
    echo "Kernel: $(uname -srm)"
    if [ -f /etc/os-release ]; then
        echo "OS: $(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '\"')"
        echo "ID: $(grep ^ID= /etc/os-release | cut -d= -f2)"
        echo "Version: $(grep VERSION_ID /etc/os-release | cut -d= -f2 | tr -d '\"')"
    else
        echo "OS: $(uname -o)"
    fi
    echo "Uptime: $(uptime -p)"
    echo ""
    
    echo "---------------------- CPU INFORMATION ---------------------"
    echo "CPU Model: $(grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2 | sed 's/^ *//')"
    echo "CPU Cores: $(nproc)"
    echo "CPU Threads: $(grep -c "processor" /proc/cpuinfo)"
    echo "Architecture: $(arch)"
    echo ""
    
    echo "--------------------- MEMORY INFORMATION -------------------"
    free -h
    echo ""
    echo "Detailed Memory:"
    awk '/MemTotal/ {total=$2/1024/1024; printf "Total: %.2f GB\n", total}
         /MemAvailable/ {avail=$2/1024/1024; printf "Available: %.2f GB\n", avail}
         /SwapTotal/ {swap=$2/1024/1024; printf "Swap: %.2f GB\n", swap}' /proc/meminfo
    echo ""
    
    echo "--------------------- DISK INFORMATION ---------------------"
    echo "Mounted Filesystems:"
    df -hT -x tmpfs -x devtmpfs
    echo ""
    echo "Disk Devices:"
    lsblk 2>/dev/null || echo "lsblk not available"
    echo ""
    
    echo "------------------- NETWORK INFORMATION --------------------"
    echo "IP Addresses:"
    ip addr show | grep -w "inet" | awk '{print $2}' | grep -v "127.0.0.1" | head -5
    echo ""
    echo "Network Interfaces:"
    ip link show | grep "^[0-9]:" | awk -F: '{print $2}' | tr -d ' '
    echo ""
    
    echo "------------------- SYSTEM SERVICES ------------------------"
    echo "Running Services:"
    if command -v systemctl >/dev/null 2>&1; then
        systemctl list-units --type=service --state=running | head -10
    else
        service --status-all | grep "+" | head -10
    fi
    echo ""
    
    echo "------------------- LOGGED-IN USERS -----------------------"
    who
    echo ""
    
    echo "==================== COLLECTION COMPLETE ==================="
} > "$OUTPUT_FILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') - System information saved to $OUTPUT_FILE" >> "$LOG_FILE"

# Giữ lại 30 ngày log
find "$OUTPUT_DIR" -name "system_info_*.txt" -mtime +30 -delete

# Log rotation
tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"

echo "System information saved to $OUTPUT_FILE"
```


#  Kiểm tra tình trạng sức khỏe hệ thống và phát hiện vấn đề
```bash
#!/bin/bash
# System Health Check Script
OUTPUT_DIR="/var/log/system_health"
OUTPUT_FILE="$OUTPUT_DIR/health_check_$(date +%Y%m%d_%H%M%S).txt"
LOG_FILE="/var/log/system_health.log"
WARNING_THRESHOLD=90
CRITICAL_THRESHOLD=95

# Tạo thư mục output nếu chưa tồn tại
mkdir -p "$OUTPUT_DIR"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting system health check" >> "$LOG_FILE"

# Hàm kiểm tra và đánh dấu cảnh báo
check_warning() {
    local value=$1
    local threshold=$2
    local message=$3
    
    if [ "$value" -ge "$CRITICAL_THRESHOLD" ]; then
        echo "[CRITICAL] $message"
    elif [ "$value" -ge "$WARNING_THRESHOLD" ]; then
        echo "[WARNING] $message"
    else
        echo "[OK] $message"
    fi
}

{
    echo "==================== SYSTEM HEALTH CHECK ==================="
    echo "Check Time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "============================================================"
    echo ""
    
    echo "---------------------- SYSTEM UPTIME -----------------------"
    uptime
    echo ""
    
    echo "---------------------- LOAD AVERAGE ------------------------"
    load=$(cat /proc/loadavg)
    echo "Load Average: $load"
    
    # Phân tích load average
    cores=$(nproc)
    load1=$(echo $load | awk '{print $1}')
    load5=$(echo $load | awk '{print $2}')
    load15=$(echo $load | awk '{print $3}')
    
    load_percent1=$(echo "scale=0; $load1 * 100 / $cores" | bc)
    load_percent5=$(echo "scale=0; $load5 * 100 / $cores" | bc)
    load_percent15=$(echo "scale=0; $load15 * 100 / $cores" | bc)
    
    echo "Load 1min: $load1 ($load_percent1% of $cores cores)"
    echo "Load 5min: $load5 ($load_percent5% of $cores cores)"
    echo "Load 15min: $load15 ($load_percent15% of $cores cores)"
    echo ""
    
    echo "--------------------- MEMORY USAGE -------------------------"
    mem_total=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
    mem_available=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
    mem_used=$((mem_total - mem_available))
    mem_usage_percent=$((mem_used * 100 / mem_total))
    
    echo "Memory Usage: $mem_usage_percent%"
    check_warning $mem_usage_percent $WARNING_THRESHOLD "Memory usage"
    free -m
    echo ""
    
    echo "---------------------- SWAP USAGE --------------------------"
    swap_total=$(awk '/SwapTotal/ {print $2}' /proc/meminfo)
    if [ "$swap_total" -gt 0 ]; then
        swap_free=$(awk '/SwapFree/ {print $2}' /proc/meminfo)
        swap_used=$((swap_total - swap_free))
        swap_usage_percent=$((swap_used * 100 / swap_total))
        
        echo "Swap Usage: $swap_usage_percent%"
        check_warning $swap_usage_percent $WARNING_THRESHOLD "Swap usage"
    else
        echo "No swap configured"
    fi
    echo ""
    
    echo "---------------------- DISK USAGE --------------------------"
    echo "Critical Filesystems:"
    df -h | awk -v warning=$WARNING_THRESHOLD -v critical=$CRITICAL_THRESHOLD '
    NR==1 {print}
    NR>1 {
        usage = substr($5, 1, length($5)-1)
        if (usage >= critical) status = "[CRITICAL]"
        else if (usage >= warning) status = "[WARNING]"
        else status = "[OK]"
        printf "%s %s %s\n", status, $0, ""
    }' | grep -E "(CRITICAL|WARNING|/dev/sd|/dev/xvd|/dev/nvme|/)$"
    echo ""
    
    echo "------------------- PROCESS HEALTH -------------------------"
    echo "Critical Processes:"
    critical_processes=("sshd" "nginx" "apache2" "mysql" "postgres" "redis")
    for process in "${critical_processes[@]}"; do
        if pgrep -x "$process" >/dev/null; then
            echo "[OK] $process is running"
        else
            echo "[WARNING] $process is not running"
        fi
    done
    echo ""
    
    echo "------------------- RECENT ERRORS --------------------------"
    echo "Recent system errors (last 30 minutes):"
    journalctl --since "30 minutes ago" -p 3..5 -n 10 2>/dev/null || \
    grep -i "error\|warn\|fail" /var/log/syslog /var/log/messages 2>/dev/null | tail -10 || \
    echo "No recent error logs found or unable to access logs"
    echo ""
    
    echo "==================== CHECK COMPLETE ========================"
} > "$OUTPUT_FILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') - System health check saved to $OUTPUT_FILE" >> "$LOG_FILE"

# Kiểm tra nếu có cảnh báo quan trọng
if grep -q "CRITICAL" "$OUTPUT_FILE"; then
    echo "ALERT: Critical issues found during health check" >> "$LOG_FILE"
    # Thêm lệnh gửi cảnh báo tại đây
fi

# Giữ lại 30 ngày log
find "$OUTPUT_DIR" -name "health_check_*.txt" -mtime +30 -delete

# Log rotation
tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"

echo "System health check saved to $OUTPUT_FILE"
```

# Cấu Hình Crontab Mẫu
```bash
# Thu thập thông tin hệ thống hàng ngày
0 2 * * * /path/to/system_info.sh

# Kiểm tra sức khỏe hệ thống mỗi giờ
0 * * * * /path/to/system_health_check.sh

# Kiểm tra sức khỏe hệ thống chi tiết hàng ngày
0 3 * * * /path/to/system_health_check.sh > /dev/null 2>&1
```

# Ghi Chú Quan Trọng

- Đảm bảo thư mục log tồn tại:

```bash
sudo mkdir -p /var/log/system_info /var/log/system_health
sudo touch /var/log/system_info.log /var/log/system_health.log
sudo chmod 600 /var/log/system_info.log /var/log/system_health.log
```
- Tùy chỉnh ngưỡng cảnh báo:

+ Chỉnh sửa biến WARNING_THRESHOLD và CRITICAL_THRESHOLD trong script health check

+ Mặc định: 90% cho cảnh báo, 95% cho nguy cấp

- Tùy chỉnh process quan trọng:

+ Chỉnh sửa mảng critical_processes trong script health check

+ Thêm các process quan trọng với hệ thống của bạn



