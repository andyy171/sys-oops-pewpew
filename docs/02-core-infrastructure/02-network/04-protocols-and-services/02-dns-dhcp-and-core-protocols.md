# DNS, DHCP And Core Network Protocols

## Overview

Core network protocols là lớp keo giúp host tìm địa chỉ, xin cấu hình, kiểm tra lỗi, quản trị thiết bị và trao đổi traffic ứng dụng. Trang này gom các note lẻ về ARP, RARP, BOOTP, DHCP, DNS, DoH, DNSSEC, ICMP, BGP, HTTP, SNMP, Telnet, TCP và UDP thành một reference vận hành.

## ARP, RARP And BOOTP

ARP ánh xạ IPv4 sang MAC trong cùng broadcast domain. Nếu host cần gửi tới IP local nhưng chưa biết MAC, nó gửi ARP request broadcast và nhận ARP reply unicast.

```bash
ip neigh
arp -n
tcpdump -ni <interface> arp
```

Các biến thể cần biết:

- **Gratuitous ARP:** host tự thông báo IP/MAC của mình, hữu ích khi failover VIP hoặc VM migrate.
- **Proxy ARP:** thiết bị trả lời ARP thay host khác; có thể hữu ích nhưng dễ làm topology khó hiểu.
- **RARP:** dùng MAC để xin IP, lịch sử cũ cho diskless workstation, hầu như được thay bằng BOOTP/DHCP.
- **BOOTP:** tiền thân của DHCP, có thể cấp IP, gateway, DNS và boot file nhưng thường cấu hình tĩnh hơn DHCP.

## DHCP

DHCP cấp IP, subnet mask, default gateway, DNS và option khác cho client. Flow nền tảng là DORA:

```text
Discover -> Offer -> Request -> Acknowledge
```

DORA nên được đọc như một state machine vận hành:

- `Discover`: client chưa có IP, broadcast để tìm DHCP server.
- `Offer`: server đề xuất IP, subnet mask, default gateway, DNS server và lease time.
- `Request`: client chọn một offer và xin dùng lease đó.
- `Acknowledge`: server xác nhận lease; client bắt đầu dùng cấu hình.

Lease không phải quyền sở hữu vĩnh viễn. Client cần renew trước khi hết hạn; nếu server hết pool, relay sai, hoặc DHCP Snooping trust boundary sai, lỗi có thể hiện ra như "máy không có mạng" dù switch port vẫn up.

Khi DHCP server khác subnet với client, cần DHCP relay:

```text
interface vlan 10
 ip helper-address 10.0.0.20
```

Troubleshooting DHCP:

- Client có gửi Discover không?
- Offer có quay lại không?
- Relay/helper-address đặt trên đúng SVI/interface chưa?
- DHCP pool còn lease không?
- DHCP Snooping trust port có đúng không?
- Firewall/ACL có chặn UDP 67/68 không?

## DNS

DNS chuyển tên thành địa chỉ và metadata dịch vụ. Cần phân biệt:

- **Recursive resolver:** hỏi thay client và cache kết quả.
- **Authoritative server:** giữ câu trả lời chính thức cho zone.
- **TTL:** thời gian cache record.
- **Record phổ biến:** `A`, `AAAA`, `CNAME`, `MX`, `NS`, `PTR`, `TXT`, `SRV`.

Flow đơn giản khi client truy cập một service theo hostname:

```text
client/application
  -> local resolver hoặc recursive resolver
  -> authoritative DNS server nếu cache miss
  -> IP address trả về cho client
  -> client mở connection tới IP/port đích
```

DNS chỉ trả lời "tên này map tới đâu"; nó không chứng minh route đúng, firewall mở, TLS certificate hợp lệ, load balancer healthy hoặc application đang phục vụ request.

### Forward Và Reverse Lookup

`Forward lookup` chuyển hostname/domain thành IP, ví dụ `www.example.com -> 192.0.2.10`. Đây là path phổ biến khi application mở kết nối tới service.

`Reverse lookup` chuyển IP thành tên thông qua `PTR` record. Nó hữu ích cho troubleshooting, mail reputation và một số hệ thống logging/security, nhưng không nên dùng như control xác thực duy nhất vì PTR có thể thiếu, stale hoặc do owner khác quản lý.

```bash
dig example.com A
dig -x 192.0.2.10
getent hosts example.com
```

Khi debug production, so sánh kết quả từ application host, resolver nội bộ và authoritative server. DNS đúng ở laptop của operator không chứng minh DNS đúng trong subnet, namespace, container hoặc VPC nơi workload đang chạy.

### DNS As Distributed Naming Service

DNS scale bằng cách chia name space thành các zone, dùng authoritative name server cho từng zone, recursive resolver để hỏi thay client và TTL cache để giảm lookup lặp lại.

| Thành phần | Vai trò vận hành |
|---|---|
| Zone | Phạm vi authority được một team/provider quản lý. |
| SOA | Metadata của zone, serial và thông tin authority. |
| NS | Name server có authority cho zone/subzone. |
| CNAME | Alias tới canonical name; giống symbolic link ở tầng DNS. |
| MX | Mail exchanger cho domain. |
| SRV | Service discovery theo service/protocol. |
| PTR | Reverse lookup từ IP sang tên. |

Name resolution có hai kiểu chính:

- **Iterative:** resolver hỏi từng authoritative server và tự đi tiếp theo referral.
- **Recursive:** một recursive resolver thực hiện toàn bộ quá trình thay client và cache intermediate result.

Production guardrails:

- TTL là contract vận hành. TTL quá cao làm failover chậm; TTL quá thấp tăng tải resolver/authoritative server.
- Zone transfer thường cần TCP và phải giới hạn tới secondary server hợp lệ.
- CNAME không nên đặt tùy tiện ở path nóng nếu làm tăng số lookup hoặc che ownership thật của endpoint.
- SRV hữu ích cho service discovery nội bộ nhưng client phải thật sự hỗ trợ SRV.
- Modern DNS có thể đi qua resolver bên ngoài, DoH/DoT hoặc browser policy, làm giảm visibility của DNS nội bộ.
- Với CDN/GSLB, resolver location có thể ảnh hưởng lựa chọn replica; external resolver xa client có thể làm locality sai.

```bash
dig example.com
dig @8.8.8.8 example.com
dig +trace example.com
nslookup example.com
```

DNS lỗi có thể làm service trông như down dù port và application vẫn khỏe.

## DoH, DoT And DNSSEC

| Cơ chế | Mục tiêu | Port thường gặp | Điểm cần nhớ |
|---|---|---:|---|
| DNS truyền thống | Resolve tên | 53 UDP/TCP | Dễ quan sát nhưng không mã hóa |
| DoT | DNS over TLS | 853 TCP | Mã hóa DNS trên port riêng |
| DoH | DNS over HTTPS | 443 TCP | Dễ đi qua firewall nhưng khó quan sát DNS nội bộ |
| DNSSEC | Xác thực dữ liệu DNS | 53 UDP/TCP | Ký record để chống giả mạo, không mã hóa nội dung |

DNSSEC dùng các record như `DNSKEY`, `RRSIG`, `DS`, `NSEC/NSEC3` để tạo chain of trust từ root tới domain. Nó chống spoofing/cache poisoning nhưng không che giấu domain đang truy vấn.

Trong doanh nghiệp, bật DoH không kiểm soát có thể làm giảm visibility của DNS monitoring. Cần policy rõ cho browser, endpoint và resolver nội bộ.

DNS privacy và DNS integrity là hai bài toán khác nhau:

- DNSSEC xác thực dữ liệu trả về nhưng không mã hóa query.
- DoT/DoH mã hóa kênh tới resolver nhưng không tự chứng minh record là đúng nếu thiếu validation.
- QNAME minimization giảm lượng thông tin gửi tới từng authoritative server bằng cách chỉ hỏi phần tên cần thiết ở từng bước.

## ICMP

ICMP báo lỗi và hỗ trợ chẩn đoán mạng. `ping` dùng echo request/reply; `traceroute` dựa vào TTL/hop limit và ICMP time exceeded hoặc UDP/TCP response tùy implementation.

Lưu ý:

- ICMP bị chặn không luôn đồng nghĩa service down.
- Chặn toàn bộ ICMP có thể làm Path MTU Discovery lỗi.
- ICMP unreachable/time exceeded giúp đọc path và firewall behavior.
- Rate limit ICMP ở edge có thể hợp lý, nhưng block mù toàn bộ ICMP thường làm troubleshooting và MTU issue khó hơn.

## TCP And UDP

TCP là reliable byte stream, có handshake, sequence, ACK, retransmission, flow control và congestion control. UDP là datagram connectionless, overhead thấp, không đảm bảo delivery/order.

| Tiêu chí | TCP | UDP |
|---|---|---|
| Connection | Có handshake | Không handshake |
| Reliability | Có ACK/retransmission | Best effort |
| Use case | HTTP, SSH, SMTP, database | DNS, NTP, VoIP, QUIC |
| Debug | SYN/SYN-ACK/ACK, reset, timeout | request/response, packet loss, app retry |

## BGP

BGP là exterior routing protocol dùng để trao đổi route giữa autonomous systems hoặc giữa các routing domain lớn. BGP chạy trên TCP port 179 và chọn route theo policy, không chỉ theo metric ngắn nhất.

Các khái niệm cần biết:

- eBGP giữa AS khác nhau.
- iBGP trong cùng AS.
- AS_PATH giúp tránh loop và thể hiện đường đi qua các AS.
- LOCAL_PREF, MED, NEXT_HOP và policy quyết định đường được chọn/quảng bá.

Vận hành BGP cần kiểm soát route leak, prefix filter, max-prefix, authentication và observability.

## HTTP And HTTPS

HTTP là application protocol phổ biến cho web/API. HTTPS là HTTP qua TLS, thường dùng port 443.

```text
GET / HTTP/1.1
Host: example.com
```

Khi debug HTTP/HTTPS:

```bash
curl -v http://example.com
curl -vk https://example.com
openssl s_client -connect example.com:443 -servername example.com
```

Nếu TCP connect được nhưng HTTP lỗi, hãy kiểm tra Host header, TLS/SNI, certificate, reverse proxy route, upstream health và application log.

## SNMP, SSH And Telnet

SNMP dùng cho monitoring thiết bị mạng qua manager-agent model. SNMPv1/v2c dùng community string và không mã hóa mạnh; ưu tiên SNMPv3 với authentication và privacy.

SSH là baseline cho remote management. Telnet truyền plaintext nên chỉ phù hợp lab/legacy cô lập, không dùng production nếu có thể tránh.

## Related Pages

- [Common Network Protocols And Ports](./01-common-network-protocols-and-ports.md)
- [HTTP Và Web Application Operations](./06-http-web-application-operations.md)
- [Network Troubleshooting Tools](../07-network-operations-lifecycle/03-network-troubleshooting-tools.md#dns-tools)
- [Security Concepts, Port Security, DHCP Snooping And DAI](../06-ccna-advanced-networking-and-security/02-security-port-security-dhcp-snooping-dai.md)
