# Network Monitoring And Packet Analysis

## Overview

Network monitoring giúp đội vận hành và bảo mật hiểu baseline traffic, phát hiện lệch chuẩn và điều tra sự cố. Với SOC, trọng tâm là dấu hiệu xâm nhập, command and control, lateral movement và data exfiltration. Với NOC/SRE, trọng tâm là latency, packet loss, saturation, routing và availability.

Hai góc nhìn này bổ sung cho nhau: cùng một packet capture có thể trả lời cả câu hỏi "vì sao service chậm" lẫn "có traffic bất thường rời khỏi hệ thống không".

## Core Concepts

| Khái niệm | Ý nghĩa vận hành |
|---|---|
| Network traffic | lượng và loại dữ liệu đi qua network |
| Network data | nội dung được truyền giữa các thiết bị |
| Baseline | mẫu hoạt động bình thường để so sánh khi có bất thường |
| Packet | đơn vị dữ liệu gồm header, payload và đôi khi có trailer |
| Packet capture | file hoặc stream chứa packet đã bắt, thường là `.pcap` |
| Packet sniffer | công cụ như `tcpdump`, Wireshark, TShark |
| Flow analysis | phân tích hướng đi, port, protocol, volume và timing của traffic |

Header thường cho biết source/destination IP, port, protocol và flag. Payload có thể chứa dữ liệu application, nhưng với traffic mã hóa như TLS thì nội dung sẽ không đọc được nếu không có key giải mã.

## What To Monitor

Nên theo dõi ít nhất các nhóm tín hiệu sau:

- Flow bất thường: kết nối tới IP lạ, port hiếm, protocol không khớp port.
- Volume bất thường: upload lớn, transfer ngoài giờ, spike theo một host hoặc subnet.
- Temporal pattern: traffic lặp đều bất thường, beaconing, job chạy sai khung giờ.
- DNS pattern: domain mới, domain sinh tự động, nhiều NXDOMAIN, truy vấn tới domain hiếm.
- Authentication/network access: nhiều login từ IP lạ, truy cập dịch vụ nội bộ từ segment không mong muốn.
- Payload hoặc metadata nhạy cảm: dấu hiệu data exfiltration, nếu môi trường và chính sách cho phép inspect.

## Passive Và Active Interception

Passive interception là nghe traffic hoặc flow mà không sửa đường đi. Dấu hiệu có thể rất mờ: một span/tap không được quản lý, host lạ trong cùng segment, hoặc log flow cho thấy traffic bị quan sát ở điểm không mong muốn. Với traffic đã mã hóa, payload có thể an toàn hơn nhưng metadata như domain, IP, size, timing và tần suất vẫn có giá trị điều tra.

Active interception làm thay đổi path hoặc nội dung: ARP poisoning, rogue gateway, DNS spoofing, proxy trái phép, route leak hoặc TLS interception không được quản trị. Khi nghi ngờ, kiểm tra đồng thời ARP/neighbor table, default gateway, DNS resolver, certificate chain, route path và firewall/proxy log.

Read-only checks nên đi trước thay đổi:

```bash
ip neigh
ip route
resolvectl status 2>/dev/null || cat /etc/resolv.conf
openssl s_client -connect example.com:443 -servername example.com </dev/null
```

Không xóa cache, đổi DNS, đổi gateway hoặc flush ARP diện rộng khi chưa ghi lại bằng chứng và hiểu blast radius. Các thao tác đó có thể che mất dấu vết incident hoặc làm gián đoạn workload hợp lệ.

## SOC Và NOC

| Đội | Trọng tâm | Ví dụ câu hỏi |
|---|---|---|
| SOC | threat detection và incident response | Có dấu hiệu C2, exfiltration, malware callback không? |
| NOC/SRE | performance và availability | Packet có loss không, route có đúng không, service có listen không? |

Trong sự cố thật, hai đội thường cần cùng một dữ liệu: log firewall, VPC Flow Logs, NetFlow, packet capture, DNS log, proxy log và SIEM events.

## Data Exfiltration Pattern

Một chuỗi exfiltration thường có các pha:

1. Initial access qua phishing, credential leak hoặc service exposed.
2. Lateral movement để tìm tài sản có giá trị.
3. Data discovery với file share, database, object storage hoặc repository.
4. Staging/compression để gom dữ liệu.
5. Exfiltration qua HTTP/S, DNS tunnel, cloud storage, email hoặc kênh đã bị compromise.

Dấu hiệu cần chú ý:

- Host nội bộ upload lượng lớn tới destination hiếm.
- Traffic ra ngoài vào khung giờ không bình thường.
- Nhiều file nhỏ được gom thành archive rồi gửi ra ngoài.
- DNS query có entropy cao hoặc kích thước bất thường.
- Tài khoản hợp lệ nhưng hành vi không giống baseline.

## Packet Capture Workflow

Quy trình điều tra gọn:

1. Xác định câu hỏi: packet không tới, bị reset, latency cao hay nghi exfiltration?
2. Xác định điểm capture: client, server, gateway, firewall hoặc span port.
3. Capture hẹp bằng filter host/port/protocol.
4. Ghi lại thời gian, interface, filter, host liên quan.
5. Phân tích header trước, payload sau nếu cần và được phép.
6. Lưu evidence an toàn vì `.pcap` có thể chứa dữ liệu nhạy cảm.

```bash
sudo tcpdump -i any -nn 'host 10.0.0.10 and port 443' -w incident-443.pcap
sudo tcpdump -r incident-443.pcap -nn -vv
```

## Defensive Controls

- Dùng MFA và least privilege để giảm rủi ro initial access.
- Duy trì asset inventory để biết host nào được phép nói chuyện với dịch vụ nào.
- Thu thập DNS, proxy, firewall, flow log và authentication log vào SIEM.
- Tạo alert theo baseline, không chỉ theo IOC tĩnh.
- Dùng IDS/IPS hoặc NDR để phát hiện payload/pattern nghi vấn.
- Với môi trường cloud, bật flow log và audit log ở boundary quan trọng.

## Related Pages

- [Network Troubleshooting Tools](../../../02-core-infrastructure/02-network/07-network-operations-lifecycle/03-network-troubleshooting-tools.md)
- [IDS/IPS](<./IDS-IPS (Snort, Suricata).md>)
- [Security And Hardening Overview](../overview.md)
