# Performance Troubleshooting

## 1. Methodology: CPU, Memory, Disk I/O, Network

Điều tra performance nên đi theo bottleneck thay vì chỉ nhìn một command.

Thứ tự nhanh:

1. Xác định triệu chứng và time window.
2. Kiểm tra CPU/load.
3. Kiểm tra memory/swap/OOM.
4. Kiểm tra disk I/O/iowait/latency.
5. Kiểm tra network/socket/packet loss.
6. Xác định process hoặc workload gây tải.
7. Ghi lại baseline trước và sau khi xử lý.

## 2. Quick Triage Commands

```bash
uptime
top
free -h
vmstat 1
iostat -xz 1
pidstat 1
sar -u 1 5
ss -s
dmesg -T | tail -100
journalctl -p warning --since "1 hour ago"
```

Nếu thiếu tool:

```bash
# Debian/Ubuntu
sudo apt install sysstat

# RHEL/Fedora
sudo dnf install sysstat
```

### Chọn tool theo lớp

| Lớp cần nhìn | Tool ưu tiên | Tín hiệu |
| --- | --- | --- |
| Process | `ps`, `top`, `pstree`, `pidstat` | PID/PPID, state, CPU, RSS, command, parent-child |
| Memory | `free`, `vmstat`, `pmap`, `/proc/<pid>/maps` | available memory, swap, page cache, process mapping |
| CPU / scheduler | `mpstat`, `top -H`, `pidstat -u`, `perf top` | per-core usage, thread hot spot, run queue |
| Disk I/O | `iostat -xz`, `iotop`, `pidstat -d` | throughput, latency, iowait, per-process I/O |
| Network | `ss`, `ip -s link`, `ethtool`, `tcpdump` | socket state, drops/errors, link, packet evidence |
| Kernel runtime | `/proc`, `/sys`, `dmesg`, `journalctl -k` | device/driver state, kernel warning, runtime counters |

Đừng đọc một metric đơn lẻ. Ví dụ load average cao có thể do CPU, disk I/O, NFS/iSCSI hoặc task state `D`; cần nhìn đồng thời `top`, `vmstat`, `iostat` và process state.

`/proc`, `/sys`, `/dev` và debugfs là các view runtime của kernel, không phải tài liệu tĩnh. Đọc chúng thường an toàn; ghi vào `/proc/sys`, `/sys` hoặc bật tracing/debugfs có thể đổi hành vi hệ thống ngay lập tức và cần rollback rõ ràng.

## 3. High CPU

### Triệu chứng

- `%CPU` cao kéo dài.
- App latency tăng.
- Load average tăng nhưng iowait thấp.

### Kiểm tra

```bash
top
ps -eo pid,ppid,user,stat,%cpu,%mem,cmd --sort=-%cpu | head -20
pidstat -u 1
perf top 2>/dev/null
```

### Nguyên nhân thường gặp

- Process loop.
- Worker/thread quá nhiều.
- Compression/encryption/build job.
- Query hoặc batch job nặng.

Đọc CPU theo capacity thực tế: architecture (`x86_64`, `aarch64`), số socket/core/thread, clock, cache và NUMA đều ảnh hưởng workload. Thêm core chỉ giúp khi workload có thể chạy song song; workload single-thread hoặc bị lock contention có thể chậm dù máy còn nhiều core rảnh.

```bash
lscpu
cat /proc/cpuinfo | head -40
```

### Xử lý

- Xác định owner của process.
- Kiểm tra log app trong cùng time window.
- Giảm concurrency nếu app hỗ trợ.
- Restart service chỉ khi hiểu tác động.
- Với incident, thu thập `ps`, `top`, log trước khi kill.

## 4. High Memory / OOM

### Triệu chứng

- Swap tăng.
- App bị kill.
- `dmesg` có OOM killer.

### Kiểm tra

```bash
free -h
vmstat 1
ps -eo pid,user,%mem,rss,vsz,cmd --sort=-rss | head -20
dmesg -T | grep -i -E 'out of memory|oom|killed process'
journalctl -k --since "1 hour ago"
```

### Nguyên nhân thường gặp

- Memory leak.
- Cache/buffer bị hiểu nhầm là used memory.
- Batch job tăng memory.
- Container/cgroup memory limit quá thấp.

### Xử lý

- Phân biệt `available` với `free`.
- Kiểm tra process RSS.
- Kiểm tra container/cgroup limit nếu chạy workload container.
- Phân biệt VSS/RSS/PSS/USS khi xem memory theo process:
  - VSS là virtual address space, thường lớn hơn memory thật đang giữ.
  - RSS là resident memory trong RAM, gồm cả shared library.
  - PSS chia phần shared memory theo tỷ lệ giữa các process dùng chung.
  - USS là phần unique/private của process, hữu ích khi tìm process thật sự giữ memory riêng.
- Restart process leak theo quy trình.
- Điều chỉnh limit hoặc capacity nếu workload hợp lệ.

## 5. High Load Average

Load average cao không luôn đồng nghĩa CPU cao. Nó gồm task running và uninterruptible sleep, thường liên quan I/O.

Ba số trong `uptime` là load trung bình 1, 5 và 15 phút. So sánh chúng với nhau để biết tải mới tăng đột biến hay đã kéo dài; so sánh với số CPU logical để tránh kết luận sai. Ví dụ load `8` trên máy 2 vCPU nghiêm trọng hơn nhiều so với load `8` trên máy 64 vCPU, nhưng vẫn cần kiểm tra process state và iowait.

```bash
uptime
top
vmstat 1
ps -eo state,pid,ppid,cmd | awk '$1 ~ /D/ {print}'
```

Nếu nhiều process state `D`, nghi ngờ disk/NFS/iSCSI/storage backend.

## 6. High iowait / Disk Latency

### Triệu chứng

- `%wa` cao trong `top`.
- App đọc/ghi chậm.
- Load cao nhưng CPU user/system không cao.

### Kiểm tra

```bash
iostat -xz 1
pidstat -d 1
df -h
lsblk
dmesg -T | grep -i -E 'i/o error|reset|timeout|blk'
```

Chỉ số cần chú ý trong `iostat`:

- `%util`
- `await`
- `r/s`, `w/s`
- `rkB/s`, `wkB/s`
- queue size nếu có

### Nguyên nhân thường gặp

- Disk/backend chậm.
- Log hoặc backup job ghi nhiều.
- Filesystem gần đầy.
- Storage network lỗi với NFS/iSCSI.
- VM noisy neighbor.

### Xử lý

- Xác định process I/O cao bằng `pidstat -d`.
- Tạm dừng backup/batch job nếu được phép.
- Kiểm tra storage backend/cloud volume metric.
- Kiểm tra mount network storage nếu path nằm trên NFS/iSCSI.

## 7. Network Latency / Connection Saturation

### Triệu chứng

- Timeout.
- Connection refused/reset.
- Latency tăng.
- Socket backlog hoặc connection count cao.

### Kiểm tra

```bash
ip -s link
ss -s
ss -tan state established | wc -l
ss -tulpn
nload
iftop
ping -c 10 <target>
tracepath <target>
curl -w '@-' -o /dev/null -s https://example.com <<'EOF'
time_namelookup:  %{time_namelookup}
time_connect:     %{time_connect}
time_appconnect:  %{time_appconnect}
time_starttransfer: %{time_starttransfer}
time_total:       %{time_total}
EOF
```

Nguyên nhân thường gặp:

- DNS chậm.
- Packet loss.
- Firewall/security group.
- App không listen hoặc backlog đầy.
- Ephemeral port exhaustion.

`nload` và `iftop` là tool realtime hữu ích nếu đã được cài; trong môi trường production hạn chế package mới, ưu tiên `ip -s link`, `ss -s` và metric từ monitoring trước.

## 8. Common Report Template

```text
Incident time window:
Affected host/service:
User-visible symptom:

CPU:
- uptime/load:
- top process:

Memory:
- free/available/swap:
- OOM evidence:

Disk I/O:
- iostat summary:
- disk full/inode:

Network:
- DNS/route/latency/socket:

Likely cause:
Action taken:
Risk/rollback:
Follow-up:
```

## 9. Production Notes

- Thu thập số liệu trước khi restart/kill process.
- Không drop cache để “sửa memory” nếu chưa hiểu tác động.
- Không xóa dữ liệu/log tùy tiện khi đang RCA.
- Với database, dùng tool native để xem query/lock/cache.
- Với container, kiểm tra cả host và cgroup/container metric.
