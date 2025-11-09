---
title: "Các lệnh tham khảo cho Network and Connectivity  "
date: 2025-01-01T00:00:00+07:00
draft: false
---

# Kiểm tra kết nối mạn
```bash
#!/bin/bash
# Kiểm tra kết nối bằng /dev/tcp
if timeout 2 bash -c "echo > /dev/tcp/google.com/80" 2>/dev/null; then
    echo "Network is up"
else
    echo "Network is down"
fi
```
`chmod +x network_check.sh`
`./network_check.sh`

# Kiểm tra website
```bash
#!/bin/bash
# Kiểm tra website bằng /dev/tcp
if timeout 2 bash -c "echo -e 'HEAD / HTTP/1.1\nHost: google.com\n\n' > /dev/tcp/google.com/80" 2>/dev/null; then
    echo "Website is up"
else
    echo "Website is down"
fi
```

# Hiển thị thông tin interface 
```bash
#!/bin/bash
# Hiển thị thông tin interface từ /sys
echo "Available interfaces:"
ls /sys/class/net/

echo -e "\nIP addresses:"
for interface in /sys/class/net/*; do
    iface=$(basename $interface)
    ip=$(ip addr show $iface 2>/dev/null | grep "inet " | awk '{print $2}')
    [ -n "$ip" ] && echo "$iface: $ip"
done
```

## Kiểm tra DNS 
```bash
#!/bin/bash
# Kiểm tra DNS bằng getent
if getent hosts google.com >/dev/null 2>&1; then
    echo "DNS working"
else
    echo "DNS failed"
fi
```

# Kiểm tra port
```bash
#!/bin/bash
# Kiểm tra port bằng /dev/tcp
if timeout 2 bash -c "echo > /dev/tcp/google.com/80" 2>/dev/null; then
    echo "Port 80 is open"
else
    echo "Port 80 is closed"
fi
```
# Kiểm tra nhiều host cùng lúc
```bash
#!/bin/bash
# Kiểm tra nhiều host
hosts=("google.com:80" "github.com:443" "stackoverflow.com:80")

for host in "${hosts[@]}"; do
    address=${host%:*}
    port=${host#*:}
    if timeout 2 bash -c "echo > /dev/tcp/$address/$port" 2>/dev/null; then
        echo "✓ $host"
    else
        echo "✗ $host"
    fi
done
```
