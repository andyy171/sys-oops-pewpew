# Setup nâng cao TIG Stack 
## Sử dụng plugin [inputs.procstat] của TIG stack để giám sát process
- **Target:** Plugin `procstat` của Telegraf sử dụng thư viện `gopsutil` để truy vấn thông tin từ hệ thống tập tin `/proc` trên Linux. Khác với plugin cpu hay mem lấy thông số tổng quát từ `/proc/stat`, `procstat` nhắm mục tiêu vào các PID cụ thể để trích xuất dữ liệu cô lập cho từng tiến trình.

- Trong môi trường prod , việc thu thập dư thừa field sẽ làm phình dung lượng Disk I/O của InflfuxDB . Vậy nên hiếm khi cấu hình mặc định của Telegraf được sử dụng trên prod .

- Cấu hình mẫu cho Telegraf :
```bash
# File: /etc/telegraf/telegraf.d/procstat_services.conf

[[inputs.procstat]]
  ## CHẾ ĐỘ CHỌN TIẾN TRÌNH (Chỉ chọn 1 trong 3 cách sau cho mỗi block)
  # Cách 1: Theo tên file thực thi (Khuyên dùng cho Nginx, Docker, SSHD)
  exe = "nginx"
  
  # Cách 2: Theo chuỗi định danh trong lệnh chạy (Khuyên dùng cho Java/JVM App, Python)
  # pattern = ".*my-app-v1.*" 

  # Cách 3: Theo Systemd Unit (Chính xác nhất cho môi trường Systemd)
  # systemd_unit = "nginx.service"

  ## TỐI ƯU HÓA DỮ LIỆU (Field Filtering)
  # Chỉ thu thập những metric thực sự có giá trị cảnh báo
  fieldpass = [
    "cpu_usage",          # % CPU (0-100 * số core)
    "memory_rss",         # RAM thực tế đang chiếm dụng (Bytes)
    "memory_vms",         # RAM ảo
    "n_fd",               # Số lượng File Descriptors đang mở
    "pid_count",          # Số lượng tiến trình con (Dùng làm Healthcheck)
    "num_threads",        # Số lượng luồng
    "read_bytes",         # Tốc độ đọc đĩa
    "write_bytes"         # Tốc độ ghi đĩa
  ]

  ## PHÂN LOẠI DỮ LIỆU (Tagging)
  [inputs.procstat.tags]
    service_type = "load-balancer"
    criticality = "p0"

  ## PERFORMANCE TUNING
  # Khoảng thời gian thu thập (mặc định theo agent, nhưng có thể tăng cho process ít quan trọng)
  interval = "10s"

```
- Xử lý quyền truy cập : Telegraf chạy dưới user `telegraf`. Mặc định, user này không thể xem chi tiết một số thông số (như `n_fd`) của các process chạy quyền root hoặc user khác.
```bash
# Thêm quyền đọc kernel cho telegraf
sudo usermod -aG adm telegraf

# Kiểm tra thử cấu hình có lỗi hay không trước khi apply
sudo -u telegraf telegraf --config /etc/telegraf/telegraf.d/procstat_services.conf --test
```

- Truy vấn dữ liệu với Flux 
Biểu đồ CPU Usage (%) theo thời gian :
```
from(bucket: "primary_metrics")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "procstat")
  |> filter(fn: (r) => r.exe == "nginx")
  |> filter(fn: (r) => r._field == "cpu_usage")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "nginx_cpu_utilization")
```

- Biểu đồ Healthcheck (Số lượng Process đang sống):
> Nếu giá trị trả về < 1, nghĩa là dịch vụ đã chết.
```
from(bucket: "primary_metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "procstat" and r._field == "pid_count")
  |> last()
```

