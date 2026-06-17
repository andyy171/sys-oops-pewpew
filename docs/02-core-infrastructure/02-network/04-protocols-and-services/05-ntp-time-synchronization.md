# NTP And Time Synchronization

## Overview

Time synchronization giữ timestamp giữa các host đủ gần nhau để log correlation, certificate validation, token expiry, distributed lock, quorum service và replicated database hoạt động đúng. Trong distributed system, mỗi node có clock riêng; nếu không kiểm soát, clock skew và clock drift có thể làm event xảy ra sau nhưng lại có timestamp sớm hơn.

NTP dùng UDP/123 để đồng bộ thời gian theo mô hình time source phân cấp. Trong Linux production, `chrony` thường là lựa chọn thực tế vì xử lý network jitter và node không online liên tục tốt.

## Mental Model

| Khái niệm | Ý nghĩa |
|---|---|
| Clock skew | Độ lệch giữa hai clock tại cùng một thời điểm. |
| Clock drift | Clock chạy nhanh/chậm dần theo thời gian do oscillator, nhiệt độ, VM scheduling hoặc host load. |
| Accuracy | Độ gần với nguồn thời gian bên ngoài như UTC. |
| Precision | Độ gần giữa các clock nội bộ với nhau. |
| Stratum | Cấp gần nguồn tham chiếu; stratum thấp hơn thường đáng tin hơn, nhưng không thay thế kiểm tra reachability và offset. |
| Slew | Điều chỉnh clock dần để tránh thời gian nhảy lùi. |
| Step | Nhảy clock tức thì; chỉ nên dùng có kiểm soát, thường trong giai đoạn boot hoặc maintenance. |

Điểm vận hành quan trọng: thời gian không nên chạy lùi trên node đang phục vụ workload. Nhảy lùi có thể làm file timestamp, token expiry, lease, timer, job scheduler và database transaction ordering sai.

Linux thường có hai clock cần phân biệt:

- system/software clock: clock kernel dùng khi OS đang chạy;
- hardware/RTC clock: clock firmware/CMOS duy trì khi máy tắt.

Trong server production, RTC nên dùng UTC thay vì localtime để giảm lỗi DST/timezone khi clone image, migrate VM hoặc vận hành nhiều region.

## NTP Offset And Delay

Một client ước lượng offset với time server bằng các mốc thời gian gửi/nhận request và response. Vì network delay hai chiều không luôn bằng nhau, NTP không chỉ lấy thời gian server trả về rồi set ngay clock. Nó lấy nhiều mẫu, lọc mẫu có delay xấu, chọn offset đáng tin hơn và điều chỉnh dần.

Production implication:

- Đừng kết luận time source tốt chỉ vì port UDP/123 mở.
- Offset thấp nhưng jitter cao vẫn có thể làm hệ thống nhạy thời gian bất ổn.
- Nhiều source độc lập tốt hơn một source duy nhất, nhất là khi cluster phụ thuộc quorum, lease hoặc token.
- VM/container có thể bị ảnh hưởng bởi host clock, CPU steal và suspend/resume; kiểm tra cả hypervisor/host khi nhiều guest lệch cùng lúc.

## Read-Only Checks

Kiểm tra trạng thái đồng bộ:

```bash
timedatectl status
hwclock --show
chronyc tracking
chronyc sources -v
chronyc sourcestats -v
ntpstat 2>/dev/null || true
ntpq -p 2>/dev/null || true
```

Kiểm tra service:

```bash
systemctl status chronyd
ss -lunp | grep ':123'
```

Kiểm tra network path tới NTP server:

```bash
nc -vzu <ntp-server> 123
tcpdump -ni <interface> udp port 123
```

Với thiết bị network hoặc appliance, kiểm tra thêm:

```text
show ntp status
show ntp associations
show clock
```

Tên lệnh thực tế phụ thuộc vendor, nhưng câu hỏi cần trả lời giống nhau: node có source không, source có reachable không, offset/jitter có trong ngưỡng chấp nhận không, timezone/log format có nhất quán không.

## Production Guardrails

- Dùng NTP/chrony server nội bộ có upstream đáng tin; không để mọi node production bắn trực tiếp ra Internet nếu policy không cho phép.
- Tối thiểu có nhiều source độc lập; tránh cùng một failure domain cho toàn bộ time hierarchy.
- Monitor offset, root delay, root dispersion, leap status và source reachability.
- Alert theo ngữ cảnh service. Ví dụ Ceph MON, Kerberos, Kubernetes API, database replication và SIEM thường nhạy với clock skew hơn batch job thông thường.
- Chuẩn hóa timezone hiển thị cho log; đồng bộ thời gian là UTC/epoch, còn timezone là cách trình bày.
- Không sửa clock thủ công trên node đang chạy workload nhạy thời gian nếu chưa có kế hoạch maintenance.
- Không trộn leap-smearing source với non-smearing source trong cùng client time config; cách xử lý leap second khác nhau có thể tạo offset khó giải thích.
- Với fleet lớn, ưu tiên time source nội bộ hoặc source của provider/ISP đáng tin thay vì mọi node dùng trực tiếp public pool.

## Risky Operations

Các thao tác dưới đây có thể làm hệ thống nhảy thời gian hoặc restart service. Luôn kiểm tra read-only trước, đánh giá blast radius, rồi mới thao tác trong maintenance window nếu service nhạy thời gian.

Step clock chỉ dùng khi đã hiểu ảnh hưởng:

```bash
sudo chronyc makestep
```

Tắt NTP để set time thủ công là thao tác rủi ro, chỉ dùng trong lab hoặc maintenance có kiểm soát:

```bash
sudo timedatectl set-ntp false
sudo timedatectl set-time "2026-06-16 10:00:00"
sudo timedatectl set-ntp true
```

Ép RTC dùng UTC:

```bash
sudo timedatectl set-local-rtc 0
sudo hwclock --systohc
```

Restart có thể làm mất trạng thái tạm thời hoặc làm node mất sync ngắn hạn:

```bash
sudo systemctl restart chronyd
sudo systemctl restart ntpd
```

Rollback thực tế thường là khôi phục cấu hình NTP/chrony trước đó, trỏ lại source cũ, restart service nếu cần và xác nhận offset trở lại ngưỡng an toàn. Với cluster quorum, ưu tiên xử lý từng node, không restart time service đồng loạt trên toàn cluster.

## Troubleshooting

| Triệu chứng | Kiểm tra trước | Hướng xử lý |
|---|---|---|
| Token/certificate báo expired/not yet valid | `timedatectl`, `chronyc tracking`, timezone log | Sửa time sync trước khi debug auth sâu hơn. |
| Log giữa node lệch timeline | Offset từng node, log timezone, collector timestamp | Chuẩn hóa UTC, kiểm tra NTP source và log pipeline. |
| Cluster báo clock skew | Offset giữa peer, chrony source, host/hypervisor clock | Cô lập node lệch, xử lý từng node, tránh restart toàn cụm. |
| NTP không sync | UDP/123, firewall, DNS của NTP name, source reachability | Cho phép network path hoặc đổi sang source nội bộ reachable. |
| Offset dao động mạnh | Jitter, packet loss, VM steal, overloaded host | Kiểm tra network/host load, thêm source ổn định hơn. |

## ntpd Và chrony

`ntpd` là daemon NTP truyền thống, thường cấu hình bằng `/etc/ntp.conf` với directive `server`. `chronyd` là lựa chọn thực tế hơn trên nhiều distro hiện đại vì sync nhanh, chịu network không ổn định tốt hơn và phù hợp VM/node không online liên tục.

Ví dụ cấu hình nguồn:

```text
# /etc/ntp.conf
server 0.pool.ntp.org iburst
server 1.pool.ntp.org iburst

# /etc/chrony.conf hoặc /etc/chrony/chrony.conf
pool pool.ntp.org iburst
server time.example.com iburst
rtcsync
```

`rtcsync` trong chrony cho phép cập nhật RTC định kỳ từ system clock, giảm nhu cầu chạy `hwclock --systohc` thủ công. Sau khi sửa config, validate trước/sau restart:

```bash
systemctl status chronyd 2>/dev/null || systemctl status ntpd
chronyc tracking 2>/dev/null || ntpstat
chronyc sources -v 2>/dev/null || ntpq -p
```

Port NTP là UDP/123. Nếu client không sync, đừng chỉ kiểm service local; kiểm cả firewall/security group, DNS của time source, route và policy outbound.

## Related Pages

- [Common Network Protocols And Ports](./01-common-network-protocols-and-ports.md)
- [DNS, DHCP And Core Network Protocols](./02-dns-dhcp-and-core-protocols.md)
- [Network Troubleshooting Tools](../07-network-operations-lifecycle/03-network-troubleshooting-tools.md)
- [Distributed Coordination Patterns](../../../01-architecture/03-patterns/07-distributed-coordination-patterns.md)
