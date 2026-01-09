# Cài đặt TIG cho hạ tầng 

## Chuẩn bị hệ thống và Cài đặt InfluxDB 2.x

### 1. Thêm Repository chính thống:
```bash
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt các gói hỗ trợ
sudo apt install -y gpg current-archive-keyring

# Thêm InfluxData GPG key
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null

# Thêm source list
echo "deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main" | sudo tee /etc/apt/sources.list.d/influxdata.list

# Cài đặt InfluxDB
sudo apt update && sudo apt install influxdb2 -y

# Kích hoạt service
sudo systemctl enable --now influxdb
```

### 2. Setup qua CLI 
```bash
influx setup \
  --username admin \
  --password 'Mật-Khẩu-Cực-Khó-2025' \
  --org 'MyCompany' \
  --bucket 'System_Metrics' \
  --retention 30d \
  --force
```
> Lưu ý: Sau lệnh này, hệ thống sẽ tạo ra một Operator Token. Hãy lưu lại nó.

## Cài đặt và Cấu hình Telegraf Agent 
Telegraf cần được cấu hình để thu thập các thông số chuyên sâu. 

```bash
# 1 Cài đặt 
sudo apt install telegraf -y

# 2. Cấu hình chi tiết (/etc/telegraf/telegraf.conf): Xóa trắng file cũ và cấu hình mẫu

[global_tags]
  env = "production"
  server_role = "web-server"

[agent]
  interval = "10s"
  round_interval = true
  metric_batch_size = 1000  #5000
  metric_buffer_limit = 10000 #50000 trên prod giữ data trường hợp network chập chờn 
  collection_jitter = "0s"  #2s 
  flush_interval = "10s"
  hostname = "" # Để trống sẽ tự lấy hostname của máy

[[outputs.influxdb_v2]]
  urls = ["http://127.0.0.1:8086"] #endpoint đầu ra 
  token = "DÁN_TOKEN_BƯỚC_1_VÀO_ĐÂY" #token 
  organization = "MyCompany" #Có thể chỉnh sửa 
  bucket = "System_Metrics" #Có thể chỉnh sửa 

# Thu thập thông số CPU chuyên sâu
[[inputs.cpu]]
  percpu = true
  totalcpu = true
  collect_cpu_time = false
  report_active = true

# Thu thập thông số RAM
[[inputs.mem]]

# Thu thập thông số Disk I/O
[[inputs.disk]]
  ignore_fs = ["tmpfs", "devtmpfs", "devfs", "iso9660", "overlay", "aufs", "squashfs"]

[[inputs.diskio]]

# Thu thập thông số Network
[[inputs.net]]
  interfaces = ["eth*", "enp*"] # Chỉ lấy các card mạng vật lý

# Thu thập thông số System Load
[[inputs.system]]


# 3. Kiểm tra cấu hình và chạy 
# Kiểm tra xem cấu hình có lỗi cú pháp không
telegraf --test

# Khởi động lại
sudo systemctl restart telegraf

```

## Cài đặt Grafana 11.x
```bash
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

sudo apt update && sudo apt install grafana -y

# Tối ưu: Cho phép Grafana chạy trên port 80 nếu cần (Optional)
# sudo setcap 'cap_net_bind_service=+ep' /usr/sbin/grafana-server

sudo systemctl enable --now grafana-server
```

### Cấu hình Data Source (Kết nối InfluxDB v2)

Vào http://IP:3000 -> Connections -> Data Sources -> Add InfluxDB:
- Query Language: Flux
- URL: http://localhost:8086
- Basic Auth: Off
- InfluxDB Details:
- Organization: MyCompany
- Token: DÁN_TOKEN_BƯỚC_1
- Default Bucket: System_Metrics


## Bảo mật & Tối ưu

### Firewall (UFW)
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 3000/tcp  # Grafana UI
# Chỉ cho phép các IP nội bộ truy cập InfluxDB nếu có nhiều node Telegraf
sudo ufw allow from 10.0.0.0/8 to any port 8086 proto tcp
sudo ufw enable
```

### Thiết lập Log Rotation cho Telegraf: Tránh việc file log làm đầy ổ cứng:
```bash
sudo nano /etc/logrotate.d/telegraf

# Nội dung file 
/var/log/telegraf/*.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
}

```

=> Import Dashboard có sẵn và chọn Datasource là InfluxDB đã tạo 


## Cấu hình nâng cao
### Module hóa kiến trúc Telegraf
Trong Production, đừng sửa trực tiếp file `/etc/telegraf/telegraf.conf.` Hãy chia nhỏ cấu hình vào thư mục `/etc/telegraf/telegraf.d/` để dễ quản lý bằng Ansible/Terraform.

#### Cấu hình Log Collection (Thay thế một phần ELK)
Telegraf thu thập log cực mạnh nhờ plugin `tail` kết hợp với `grok` parser. Ví dụ cấu hình thu thập log Nginx (`/etc/telegraf/telegraf.d/nginx-logs.conf`):
```toml
[[inputs.tail]]
  files = ["/var/log/nginx/access.log"]
  from_beginning = false
  pipe = false
  data_format = "grok"
  # Grok pattern chuẩn cho Nginx
  grok_patterns = ["%{COMBINED_LOG_FORMAT}"] 
  name_override = "nginx_access_logs"

[[processors.enum]] # Chuyển đổi mã lỗi HTTP sang dạng số để vẽ biểu đồ
  [[processors.enum.mapping]]
    field = "resp_code"
    dest = "status_code_class"
    [processors.enum.mapping.value_mappings]
      200 = 2, 201 = 2, 404 = 4, 500 = 5, 502 = 5
```

#### Cấu hình Monitoring Database (MySQL/PostgreSQL)
```bash

# /etc/telegraf/telegraf.d/databases.conf
[[inputs.mysql]]
  servers = ["user:password@tcp(127.0.0.1:3306)/?tls=false"]
  metric_version = 2
  gather_innodb_metrics = true
  gather_process_list = true
  gather_table_schema_stats = true

[[inputs.redis]]
  servers = ["tcp://127.0.0.1:6379"]
```


#### Thu thập data với Script tùy chỉnh 
Trường hợp muốn tích hợp thêm script Python/Bash kiểm tra logic nghiệp vụ 
```bash
[[inputs.exec]]
  commands = ["python3 /opt/scripts/check_business_logic.py"]
  timeout = "5s"
  data_format = "json"
  name_override = "business_health"
```


### Tùy chỉnh hiệu năng InluxDB trong prod 
#### Tối ưu Systemd cho InfluxDB
Chỉnh sửa service để chịu tải cao (`sudo systemctl edit influxdb`):
```toml
[Service]
LimitNOFILE=65536
LimitNPROC=65536
# Giới hạn tài nguyên để không treo cả server nếu DB spike
MemoryHigh=8G 
MemoryMax=12G
```

#### Cấu hình HTTPS/TLS cho InfluxDB (Bắt buộc nếu Agent đẩy qua Internet)
1. Sử dụng Let's Encrypt hoặc Self-signed cert.
2. Cấu hình trong `/etc/default/influxdb2` hoặc biến môi trường:
```bash
INFLUXDB_TLS_CERT=/etc/ssl/influxdb/cert.pem
INFLUXDB_TLS_KEY=/etc/ssl/influxdb/key.pem
```

#### Quản lý Retention Policy & Bucket (Chiến lược lưu trữ)
Trong Prod, bạn không bao giờ giữ dữ liệu thô (raw data) mãi mãi. Để tiết kiệm chi phí lưu trữ trên Cloud, ta cần giảm độ phân giải dữ liệu cũ. Ví dụ: Dữ liệu 10 giây/lần sau 7 ngày sẽ được gộp thành trung bình 1 giờ/lần.
- Bucket system_high_res: Giữ 7 ngày (Dữ liệu thu thập mỗi 10s).
- Bucket system_summary: Giữ 1 năm (Dữ liệu đã qua xử lý Downsampling bằng InfluxDB Tasks).

Ví dụ vài Task Downsampling (Flux script chạy định kỳ):

```bash
option task = {name: "Daily_Summary", every: 1d}

from(bucket: "system_high_res")
  |> range(start: -1d)
  |> filter(fn: (r) => r._measurement == "cpu")
  |> aggregateWindow(every: 1h, fn: mean)
  |> to(bucket: "system_summary")

----------------------------------------------------

option task = {name: "Downsampling_1h", every: 1h}

from(bucket: "primary_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "cpu")
  |> aggregateWindow(every: 1h, fn: mean)
  |> to(bucket: "long_term_storage_1year")
```


#### Grafana Provisioning
```bash
# Tạo file /etc/grafana/provisioning/datasources/influxdb.yaml:

apiVersion: 1
datasources:
  - name: InfluxDB_v2
    type: influxdb
    access: proxy
    url: http://localhost:8086
    jsonData:
      version: Flux
      organization: MyOrg
      defaultBucket: System_Metrics
      tlsSkipVerify: true
    secureJsonData:
      token: "${INFLUX_TOKEN}" # Sử dụng biến môi trường

```

#### Tự giám sát chính TIG stack (Self-Monitoring)

1. **Telegraf Internal:** Bật plugin [[inputs.internal]] để theo dõi số lượng metric bị drop (buffer overflow).
2. **Alerting:** Cấu hình Grafana Alerting gửi thông báo qua Telegram/Slack ngay khi Disk của InfluxDB vượt quá 80%.


#### Lưu ý 
- **Time Sync:** Đảm bảo tất cả máy chủ chạy NTP (Chrony). InfluxDB cực kỳ nhạy cảm với lệch múi giờ.
- **Backup:** Script backup định kỳ `influx backup /path/to/backup`.
- **Buffer:** Tăng `metric_buffer_limit` trong Telegraf lên `100000` nếu network không ổn định.
- **Security:** Chạy Telegraf với user `telegraf`, không chạy bằng `root`. Nếu cần đọc log, hãy add user vào group `adm`.
- **Chặn Port:** InfluxDB (8086) và Grafana (3000) mặc định mở cho mọi IP. Dùng UFW để giới hạn.
- **SSL/TLS:** Sử dụng Nginx làm Reverse Proxy để chạy HTTPS cho Grafana thay vì chạy trực tiếp.
- **Tối ưu nhân Linux:** Tăng giới hạn file mở cho InfluxDB. ( Lưu ý không phải trường hợp nào cũng sử dụng )
```bash
# /etc/security/limits.conf
influxdb soft nofile 65536
influxdb hard nofile 65536
```