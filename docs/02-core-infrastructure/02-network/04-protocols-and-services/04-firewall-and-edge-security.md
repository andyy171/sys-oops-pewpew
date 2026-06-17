# Firewall And Edge Security

## Overview

Firewall là enforcement point kiểm soát traffic theo policy. Trong hạ tầng hiện đại, firewall có thể đồng thời làm routing, NAT, VPN, segmentation, logging, IPS, web filtering, SSL inspection và SD-WAN.

## Firewall Types

| Loại | Vai trò |
|---|---|
| Stateless ACL | Match packet theo source/destination/protocol/port, không giữ session state |
| Stateful firewall | Theo dõi session và cho phép return traffic hợp lệ |
| NGFW | Thêm application awareness, user identity, URL filtering, IPS, malware prevention |
| Host firewall | Chạy trên endpoint/server, bảo vệ local service |
| Cloud security group/NACL | Policy cloud-native quanh instance/subnet |

## Deployment Modes

| Mode | Ý nghĩa |
|---|---|
| L2 transparent | Firewall inline như bridge, ít thay đổi IP topology |
| L3 routed | Firewall là gateway/router giữa subnet/VLAN |
| One-arm / service insertion | Traffic được redirect qua firewall bằng route hoặc policy |
| East-west segmentation | Kiểm soát traffic nội bộ giữa VLAN/app tier |
| North-south edge | Kiểm soát traffic ra/vào Internet hoặc WAN |

Transparent mode không có nghĩa firewall chỉ inspect Layer 2. Nhiều platform vẫn có thể stateful inspection và application awareness tùy tính năng.

## NGFW Capabilities

- Stateful policy.
- NAT.
- IPsec/SSL VPN.
- IPS/IDS.
- Antivirus/malware prevention.
- Web filtering và DNS filtering.
- Application control.
- SSL/TLS inspection.
- Traffic shaping/QoS.
- Central logging và SIEM/SOC integration.

Thiết kế policy quan trọng hơn việc bật thật nhiều feature. Bật inspection mà không sizing, logging và exception process tốt có thể làm tăng latency hoặc gây false positive khó vận hành.

## Network Attack Patterns

Các attack network thường đánh vào ba lớp: link access, traffic path và service availability.

Ở link layer, rủi ro chính là thiết bị không được phép tham gia network, sniffing, ARP spoofing/poisoning hoặc MITM trong cùng broadcast domain. Control phù hợp gồm physical security, 802.1X, port security, DHCP Snooping, Dynamic ARP Inspection, segmentation và monitoring MAC/IP bất thường. MAC filtering đơn lẻ không đủ mạnh vì MAC có thể spoof.

Với Wi-Fi, tránh WEP và các cấu hình legacy yếu. Ưu tiên WPA2/WPA3 phù hợp thiết bị, password/PSK mạnh nếu dùng personal mode, enterprise authentication khi cần accountability, firmware được cập nhật và tách guest network khỏi production segment. Public/open Wi-Fi phải được xem là untrusted network; traffic nhạy cảm cần TLS/VPN/E2EE ở lớp cao hơn.

Passive interception chủ yếu nghe lén metadata hoặc payload không mã hóa. Active interception có thể sửa, delay, replay hoặc redirect traffic, ví dụ ARP poisoning hoặc rogue gateway. Encryption giúp bảo vệ confidentiality/integrity, nhưng metadata như IP, domain, timing và volume vẫn có thể lộ qua log/flow.

DoS/DDoS đánh availability. SYN flood lạm dụng TCP handshake, botnet tạo nhiều source phân tán, còn volumetric attack có thể vượt quá capacity trước khi firewall nội bộ kịp xử lý. Packet filter có thể rate limit, drop source xấu hoặc bật SYN protection, nhưng không thay thế upstream scrubbing, CDN/WAF, autoscaling, capacity headroom và runbook liên hệ provider.

Guardrail vận hành:

- Ưu tiên quan sát bằng flow log, firewall log, IDS/IPS, packet capture hẹp và metric saturation trước khi thay rule lớn.
- Khi block ICMP hoặc UDP diện rộng, đánh giá tác động tới DNS, NTP, Path MTU Discovery và troubleshooting.
- Với DDoS lớn, xử lý ở upstream/edge càng gần nguồn càng tốt; firewall nội bộ thường đã quá muộn nếu link Internet bị bão hòa.
- Sau containment, lưu evidence: thời gian, source/destination, protocol, packet sample, rule đã thay đổi và metric trước/sau.

## Firewall Performance

| Chỉ số | Ý nghĩa |
|---|---|
| Firewall throughput | Throughput khi policy/feature nhẹ, thường là số marketing cao nhất |
| Threat protection throughput | Throughput khi bật IPS/AV/app control, sát thực tế hơn |
| SSL inspection throughput | Throughput khi giải mã TLS, thường giảm mạnh |
| Concurrent sessions | Số session đồng thời |
| New sessions per second | Tốc độ tạo session mới |
| PPS | Packets per second, quan trọng khi packet nhỏ |

Sizing thực tế nên dựa trên traffic profile, feature bật thật, session/PPS và growth headroom. Đừng chọn firewall chỉ theo bandwidth Internet danh nghĩa.

## Operational Risks

- SSL inspection làm tăng CPU và có thể phá ứng dụng dùng certificate pinning.
- NAT nhiều lớp làm khó đọc log và truy vết.
- Rule quá rộng làm mất segmentation.
- Rule quá chi tiết nhưng không có naming/logging làm khó vận hành.
- Asymmetric routing làm stateful firewall drop traffic.
- HA failover không được test có thể gây outage khi sự cố thật.

## Troubleshooting Checklist

- Traffic match rule nào? Có log allow/deny không?
- Policy evaluation xảy ra trước hay sau NAT trên platform đó?
- Session table có entry không?
- Return path có đi qua cùng firewall không?
- SSL inspection có gây handshake/certificate lỗi không?
- IPS/app control có drop signature nào không?
- Throughput/session/PPS có chạm ngưỡng không?

## Best Practices

- Dùng object/group có naming rõ.
- Log deny quan trọng và log allow cho service nhạy cảm.
- Tách policy theo zone hoặc segment, không gom mọi thứ vào một rule lớn.
- Backup config trước thay đổi lớn.
- Có rollback plan cho rule/NAT/VPN thay đổi.
- Test HA failover và kiểm tra log sau failover.
- Theo dõi session, CPU, memory, drops, IPS events và VPN tunnel health.

## Related Pages

- [Routing, NAT And Virtual Router](../03-ip-routing-subnetting/02-routing-nat-and-virtual-router.md)
- [Security Concepts, Port Security, DHCP Snooping And DAI](../06-ccna-advanced-networking-and-security/02-security-port-security-dhcp-snooping-dai.md)
- [Network Troubleshooting Tools](../07-network-operations-lifecycle/03-network-troubleshooting-tools.md)
