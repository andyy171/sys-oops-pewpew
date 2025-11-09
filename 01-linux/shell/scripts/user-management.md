---
title: "Các lệnh tham khảo cho User Management"
date: 2025-01-01T00:00:00+07:00
draft: false
---

# Tạo user mới nếu chưa tồn tại
```bash
#!/bin/bash
# User Account Management Script
USERNAME="newuser"
LOG_FILE="/var/log/user_management.log"

# Kiểm tra nếu user đã tồn tại
if id "$USERNAME" &>/dev/null; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - User $USERNAME already exists." >> "$LOG_FILE"
else
    # Tạo user mới với home directory
    useradd -m "$USERNAME"
    
    # Đặt mật khẩu mặc định hoặc yêu cầu đổi ở lần đăng nhập đầu tiên
    echo "$USERNAME:temp_password" | chpasswd
    chage -d 0 "$USERNAME"  # Yêu cầu đổi mật khẩu ở lần login đầu tiên
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - User $USERNAME created successfully." >> "$LOG_FILE"
    
    # Ghi thông tin user vào file log
    echo "User details:" >> "$LOG_FILE"
    finger "$USERNAME" >> "$LOG_FILE" 2>/dev/null || id "$USERNAME" >> "$LOG_FILE"
fi

# Log rotation
tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
```
- Cách sử dụng:

+ Chỉnh sửa biến USERNAME theo tên user muốn tạo

+ Lưu thành file user_management.sh

+ Cho phép thực thi: chmod +x user_management.sh

+ Chạy script với quyền root: sudo ./user_management.sh
# Tạo mật khẩu ngẫu nhiên an toàn
```bash
#!/bin/bash
# Password Generator Script
LENGTH=12
LOG_FILE="/var/log/password_generator.log"

# Kiểm tra xem openssl có sẵn không, nếu không dùng /dev/urandom
if command -v openssl &> /dev/null; then
    PASSWORD=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9!@#$%^&*()_+-=' | head -c "$LENGTH")
else
    PASSWORD=$(tr -dc 'a-zA-Z0-9!@#$%^&*()_+-=' < /dev/urandom | head -c "$LENGTH")
fi

# Ghi log mật khẩu được tạo (trong thực tế nên cẩn thận với việc log mật khẩu)
echo "$(date '+%Y-%m-%d %H:%M:%S') - Generated password: $PASSWORD" >> "$LOG_FILE"

# Hiển thị mật khẩu (chỉ cho mục đích testing, trong production nên gửi qua kênh an toàn)
echo "Generated password: $PASSWORD"

# Log rotation
tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
```
Cách sử dụng:

Chỉnh sửa biến LENGTH theo độ dài mật khẩu mong muốn

Lưu thành file password_generator.sh

Cho phép thực thi: chmod +x password_generator.sh

Chạy script: ./password_generator.sh

Lưu ý quan trọng: Trong môi trường production, không nên log hoặc hiển thị mật khẩu. Thay vào đó, hãy gửi mật khẩu qua kênh an toàn (email mã hóa, etc.).

# Kiểm tra thời hạn mật khẩu của người dùng
```bash
#!/bin/bash
# User Password Expiry Checker Script
LOG_FILE="/var/log/password_expiry.log"
WARNING_DAYS=7  # Cảnh báo trước số ngày

echo "$(date '+%Y-%m-%d %H:%M:%S') - Checking password expiry for all users" >> "$LOG_FILE"

# Kiểm tra cho tất cả user có shell đăng nhập (không chỉ bash)
getent passwd | while IFS=: read -r username _ _ _ _ shell _; do
    # Chỉ kiểm tra user có shell đăng nhập (bash, sh, zsh, etc.)
    if [[ "$shell" == *"bash"* || "$shell" == *"sh"* ]]; then
        # Lấy thông tin hết hạn mật khẩu
        expiry_info=$(chage -l "$username" 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            # Trích xuất ngày hết hạn
            expires=$(echo "$expiry_info" | grep "Password expires" | awk -F': ' '{print $2}')
            
            if [ "$expires" = "never" ]; then
                echo "User: $username, Password never expires" >> "$LOG_FILE"
            else
                # Chuyển đổi ngày hết hạn thành timestamp
                expiry_date=$(date -d "$expires" +%s 2>/dev/null)
                current_date=$(date +%s)
                
                if [ -n "$expiry_date" ]; then
                    # Tính số ngày còn lại
                    days_left=$(( (expiry_date - current_date) / 86400 ))
                    
                    if [ "$days_left" -le 0 ]; then
                        echo "ALERT: User $username password has EXPIRED" >> "$LOG_FILE"
                    elif [ "$days_left" -le "$WARNING_DAYS" ]; then
                        echo "WARNING: User $username password expires in $days_left days" >> "$LOG_FILE"
                    else
                        echo "User: $username, Password expires in $days_left days" >> "$LOG_FILE"
                    fi
                fi
            fi
        fi
    fi
done

# Log rotation
tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
```