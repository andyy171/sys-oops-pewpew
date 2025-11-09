---
title: "Các lệnh tham khảo cho Database Management  "
date: 2025-01-01T00:00:00+07:00
draft: false
---

# Tạo backup tự động cho database với xử lý lỗi và logging
```bash
#!/bin/bash
# Database Backup Script
BACKUP_DIR="/var/backups/databases"
LOG_FILE="/var/log/db_backup.log"
CONFIG_FILE="/etc/db_backup.conf"
RETENTION_DAYS=7

# Tạo thư mục backup nếu chưa tồn tại
mkdir -p "$BACKUP_DIR"

# Đọc cấu hình từ file nếu tồn tại
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    # Thiết lập mặc định nếu không có file cấu hình
    DB_HOST="localhost"
    DB_USER="root"
    DB_PASS=""
    DATABASES=("all")  # "all" để backup tất cả databases
fi

# Hàm log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Hàm backup database
backup_database() {
    local db_name=$1
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/${db_name}_${timestamp}.sql.gz"
    
    log_message "Starting backup for database: $db_name"
    
    # Thiết lập options cho mysqldump
    local mysql_options="--single-transaction --quick --lock-tables=false"
    if [ -n "$DB_HOST" ]; then
        mysql_options="$mysql_options -h $DB_HOST"
    fi
    if [ -n "$DB_USER" ]; then
        mysql_options="$mysql_options -u $DB_USER"
    fi
    if [ -n "$DB_PASS" ]; then
        mysql_options="$mysql_options -p$DB_PASS"
    fi
    
    # Thực hiện backup
    if mysqldump $mysql_options "$db_name" | gzip > "$backup_file"; then
        local file_size=$(du -h "$backup_file" | cut -f1)
        log_message "Backup successful for $db_name. File: $backup_file ($file_size)"
        echo "$backup_file"
    else
        log_message "ERROR: Backup failed for database $db_name"
        rm -f "$backup_file"  # Xóa file backup lỗi
        return 1
    fi
}

# Hàm kiểm tra kết nối database
check_db_connection() {
    if command -v mysqladmin &> /dev/null; then
        local mysql_options=""
        if [ -n "$DB_HOST" ]; then
            mysql_options="$mysql_options -h $DB_HOST"
        fi
        if [ -n "$DB_USER" ]; then
            mysql_options="$mysql_options -u $DB_USER"
        fi
        if [ -n "$DB_PASS" ]; then
            mysql_options="$mysql_options -p$DB_PASS"
        fi
        
        if mysqladmin $mysql_options ping > /dev/null 2>&1; then
            return 0
        else
            log_message "ERROR: Cannot connect to database server"
            return 1
        fi
    else
        log_message "WARNING: mysqladmin not found, skipping connection test"
        return 0
    fi
}

# Main backup process
main() {
    log_message "Starting database backup process"
    
    # Kiểm tra kết nối database
    if ! check_db_connection; then
        exit 1
    fi
    
    # Xác định danh sách databases để backup
    local databases_to_backup=()
    if [ "${DATABASES[0]}" = "all" ]; then
        # Lấy tất cả databases
        if command -v mysql &> /dev/null; then
            local mysql_options=""
            if [ -n "$DB_HOST" ]; then
                mysql_options="$mysql_options -h $DB_HOST"
            fi
            if [ -n "$DB_USER" ]; then
                mysql_options="$mysql_options -u $DB_USER"
            fi
            if [ -n "$DB_PASS" ]; then
                mysql_options="$mysql_options -p$DB_PASS"
            fi
            
            databases_to_backup=$(mysql $mysql_options -e "SHOW DATABASES;" | grep -Ev "(Database|information_schema|performance_schema|mysql|sys)")
        else
            log_message "ERROR: mysql command not found"
            exit 1
        fi
    else
        databases_to_backup=("${DATABASES[@]}")
    fi
    
    # Thực hiện backup cho từng database
    local success_count=0
    local fail_count=0
    for db in "${databases_to_backup[@]}"; do
        if backup_database "$db"; then
            ((success_count++))
        else
            ((fail_count++))
        fi
    done
    
    # Xóa backups cũ
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -exec rm -f {} \;
    
    log_message "Backup completed. Successful: $success_count, Failed: $fail_count"
}

# Thực thi main function
main
```
Cách sử dụng:

Tạo file cấu hình: sudo nano /etc/db_backup.conf

Chỉnh sửa thông tin database trong file cấu hình

Lưu script thành file db_backup.sh

Cho phép thực thi: chmod +x db_backup.sh

Chạy script: sudo ./db_backup.sh
# Tự động dọn dẹp database backups cũ và các bảng dữ liệu không cần thiết
```bash
#!/bin/bash
# Automated Database Cleanup Script
LOG_FILE="/var/log/db_cleanup.log"
BACKUP_DIR="/var/backups/databases"
RETENTION_DAYS=7

# Hàm log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Hàm xóa backups cũ
cleanup_old_backups() {
    log_message "Cleaning up backups older than $RETENTION_DAYS days"
    
    local deleted_files=$(find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -print -delete | wc -l)
    
    if [ "$deleted_files" -gt 0 ]; then
        log_message "Deleted $deleted_files old backup files"
    else
        log_message "No old backup files found for deletion"
    fi
}

# Hàm xóa bảng dữ liệu cũ (tùy chỉnh theo nhu cầu)
cleanup_old_data() {
    log_message "Starting database data cleanup"
    
    # Thiết lập kết nối database
    local mysql_options=""
    if [ -n "$DB_HOST" ]; then
        mysql_options="$mysql_options -h $DB_HOST"
    fi
    if [ -n "$DB_USER" ]; then
        mysql_options="$mysql_options -u $DB_USER"
    fi
    if [ -n "$DB_PASS" ]; then
        mysql_options="$mysql_options -p$DB_PASS"
    fi
    
    # Ví dụ: Xóa các bản ghi cũ hơn 30 ngày từ bảng logs
    # Thay đổi truy vấn này phù hợp với cấu trúc database của bạn
    local cleanup_queries=(
        "DELETE FROM logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)"
        "OPTIMIZE TABLE logs"
        "DELETE FROM sessions WHERE last_activity < DATE_SUB(NOW(), INTERVAL 7 DAY)"
        "OPTIMIZE TABLE sessions"
    )
    
    for query in "${cleanup_queries[@]}"; do
        if mysql $mysql_options -e "$query" 2>/dev/null; then
            log_message "Executed cleanup query: $query"
        else
            log_message "WARNING: Failed to execute query: $query"
        fi
    done
}

# Hàm kiểm tra dung lượng ổ đĩa
check_disk_space() {
    local threshold=90
    local usage=$(df -h "$BACKUP_DIR" | awk 'NR==2 {print $5}' | tr -d '%')
    
    if [ "$usage" -gt "$threshold" ]; then
        log_message "WARNING: Disk usage is $usage%, considering more aggressive cleanup"
        # Tự động giảm retention days nếu dung lượng ổ đĩa quá cao
        local extra_retention=$((RETENTION_DAYS - 2))
        find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$extra_retention -print -delete
        log_message "Deleted backups older than $extra_retention days due to disk space constraints"
    fi
}

# Main cleanup process
main() {
    log_message "Starting database cleanup process"
    
    # Đọc cấu hình nếu tồn tại
    if [ -f "/etc/db_backup.conf" ]; then
        source "/etc/db_backup.conf"
    fi
    
    # Kiểm tra và tạo thư mục backup nếu chưa tồn tại
    mkdir -p "$BACKUP_DIR"
    
    # Thực hiện các tasks dọn dẹp
    cleanup_old_backups
    check_disk_space
    
    # Chỉ chạy cleanup data nếu có cấu hình database
    if [ -n "$DB_USER" ] && [ -n "$DB_PASS" ]; then
        cleanup_old_data
    fi
    
    log_message "Database cleanup completed"
}

# Thực thi main function
main
```
Đảm bảo đã có file cấu hình /etc/db_backup.conf (từ script backup)

Lưu script thành file db_cleanup.sh

Cho phép thực thi: chmod +x db_cleanup.sh

Chạy script: sudo ./db_cleanup.sh

# Kiểm tra tình trạng sức khỏe database và tối ưu hóa hiệu suất
```bash
#!/bin/bash
# Database Health Check Script
LOG_FILE="/var/log/db_health.log"

# Hàm log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Hàm kiểm tra kết nối và trạng thái database
check_db_status() {
    log_message "Checking database status"
    
    if command -v mysqladmin &> /dev/null && [ -f "/etc/db_backup.conf" ]; then
        source "/etc/db_backup.conf"
        
        local mysql_options=""
        if [ -n "$DB_HOST" ]; then
            mysql_options="$mysql_options -h $DB_HOST"
        fi
        if [ -n "$DB_USER" ]; then
            mysql_options="$mysql_options -u $DB_USER"
        fi
        if [ -n "$DB_PASS" ]; then
            mysql_options="$mysql_options -p$DB_PASS"
        fi
        
        # Kiểm tra trạng thái database
        if mysqladmin $mysql_options ping > /dev/null 2>&1; then
            log_message "Database server is running"
            
            # Kiểm tra các processes đang chạy
            local process_count=$(mysql $mysql_options -e "SHOW PROCESSLIST;" | wc -l)
            log_message "Number of database processes: $process_count"
            
            # Kiểm tra các connections
            local connection_count=$(mysql $mysql_options -e "SELECT COUNT(*) FROM information_schema.processlist;" | tail -1)
            log_message "Number of database connections: $connection_count"
            
            # Kiểm tra kích thước database
            mysql $mysql_options -e "SELECT table_schema 'Database', SUM(data_length + index_length) / 1024 / 1024 'Size (MB)' FROM information_schema.TABLES GROUP BY table_schema;" >> "$LOG_FILE"
            
        else
            log_message "ERROR: Database server is not responding"
        fi
    else
        log_message "SKIP: Database check tools or config not available"
    fi
}

# Hàm tối ưu hóa database
optimize_database() {
    log_message "Starting database optimization"
    
    if command -v mysql &> /dev/null && [ -f "/etc/db_backup.conf" ]; then
        source "/etc/db_backup.conf"
        
        local mysql_options=""
        if [ -n "$DB_HOST" ]; then
            mysql_options="$mysql_options -h $DB_HOST"
        fi
        if [ -n "$DB_USER" ]; then
            mysql_options="$mysql_options -u $DB_USER"
        fi
        if [ -n "$DB_PASS" ]; then
            mysql_options="$mysql_options -p$DB_PASS"
        fi
        
        # Lấy danh sách các bảng cần optimization
        local tables=$(mysql $mysql_options -e "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA NOT IN ('information_schema', 'mysql', 'performance_schema') AND Data_free > 0;" 2>/dev/null)
        
        if [ -n "$tables" ]; then
            for table in $tables; do
                if mysql $mysql_options -e "OPTIMIZE TABLE $table" 2>/dev/null; then
                    log_message "Optimized table: $table"
                fi
            done
        else
            log_message "No tables need optimization"
        fi
    fi
}

# Main health check process
main() {
    log_message "Starting database health check"
    check_db_status
    optimize_database
    log_message "Database health check completed"
}

# Thực thi main function
main
```

## Cấu Hình Crontab Mẫu
```bash
# Backup database hàng ngày lúc 2 giờ sáng
0 2 * * * /path/to/db_backup.sh

# Dọn dẹp database hàng ngày lúc 3 giờ sáng
0 3 * * * /path/to/db_cleanup.sh

# Kiểm tra sức khỏe database hàng tuần (Chủ nhật lúc 4 giờ sáng)
0 4 * * 0 /path/to/db_health_check.sh
```

# Ghi Chú Quan Trọng
1. Bảo mật thông tin database:

Không lưu mật khẩu trong script, sử dụng file cấu hình với quyền hạn chế

Đặt quyền cho file cấu hình: chmod 600 /etc/db_backup.conf

23. Đảm bảo thư mục backup tồn tại:

```bash
sudo mkdir -p /var/backups/databases
sudo chmod 700 /var/backups/databases
```
3. Đảm bảo thư mục log tồn tại:

```bash
sudo touch /var/log/db_backup.log /var/log/db_cleanup.log /var/log/db_health.log
sudo chmod 600 /var/log/db_*.log
```
4. Tùy chỉnh scripts:
- Chỉnh sửa các biến RETENTION_DAYS theo nhu cầu
- Điều chỉnh các truy vấn cleanup trong db_cleanup.sh phù hợp với cấu trúc database của bạn
- Thêm các cơ chế cảnh báo (email, notification) khi cần

5. Kiểm tra compatibility:
- Các script này hỗ trợ MySQL/MariaDB
- Cần cài đặt client MySQL: sudo apt-get install mysql-client (Ubuntu/Debian)