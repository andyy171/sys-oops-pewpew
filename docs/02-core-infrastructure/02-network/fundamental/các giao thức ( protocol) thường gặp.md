**Danh mục**
- [Giao thức ARP](#arp---address-resolution-protocol)
- [Giao thức RARP](#rarp---reverse-address-resolution-protocol)
- [Giao thức BOOTP](#bootp---boot-protocol)
- [Giao thức DHCP](#dhcp---dynamic-host-configuration-protocol)
- [Giao thức DNS](#dns---domain-name-system)
- [Giao thức ICMP](#icmp---internet-control-message-protocol)
- [Giao thức IP](#ip---internet-protocol)
- [Giao thức TCP](#tcp---transport-control-protocol)
- [Giao thức UDP](#udp---user-datagram-protocol)
- [Giao thức BGP](#bgp---border-gateway-protocol)
- [Giao thức SMTP](#smtp---simple-mail-transport-protocol)
- [Giao thức SSH](#ssh---secure-shell-protocol)
- [Giao thức TLS](#tls---transport-layer-security)

---

# ARP - Address Resolution Protocol
- ARP (Address Resolution Protocol) là giao thức mạng dùng để ánh xạ địa chỉ IP (thường là IPv4) sang địa chỉ phần cứng **MAC** trên mạng cục bộ (LAN). Nó giúp các thiết bị giao tiếp bằng cách tìm địa chỉ **MAC** từ địa chỉ IP đã biết, đặc biệt trên Ethernet hoặc WiFi.

- ARP cần thiết vì địa chỉ IP (32-bit cho IPv4) và **MAC** (48-bit) có độ dài khác nhau, yêu cầu một cơ chế trung gian để dịch chuyển giữa chúng. Không có ARP, các thiết bị không thể gửi packet chính xác trên mạng cục bộ.
> Lưu ý: Với IPv6, ARP được thay thế bằng Neighbor Discovery Protocol (NDP), sử dụng ICMPv6 để thực hiện chức năng tương tự nhưng an toàn hơn.
> ARP chủ yếu dùng cho IPv4; trong môi trường hiện đại (2025), nhiều mạng kết hợp IPv4/IPv6, nhưng ARP vẫn phổ biến do tính tương thích cao

- ARP được phát triển đầu những năm 1980 như một giao thức dịch địa chỉ chung cho mạng IP, ban đầu cho Ethernet, sau mở rộng sang ATM, Token Ring và các loại mạng khác. Nó được định nghĩa trong RFC 826 (1982) và vẫn là tiêu chuẩn cơ bản đến nay.

- Mục đích chính của chúng là duy trì bảng ánh xạ IP-**MAC** (ARP cache) để các thiết bị trên LAN có thể nhanh chóng tìm địa chỉ **MAC** mà không cần broadcast liên tục. Nếu thiếu ARP, giao tiếp giữa các máy chủ sẽ thất bại vì không xác định được địa chỉ vật lý. 
> Trong các mạng hiện đại, ARP có thể bị lạm dụng cho tấn công spoofing (giả mạo địa chỉ), dẫn đến rủi ro bảo mật như MITM (Man-in-the-Middle). Các giải pháp như ARP inspection trên switch giúp giảm thiểu.

## Các loại ARP 
<img src="/images/base/type-of-arp.png">

Có bốn loại chính : 
- **Proxy ARP:** Router hoặc proxy trả lời thay cho thiết bị khác, thường dùng trong mạng con để định tuyến lưu lượng mà không cần cấu hình default gateway đầy đủ.
- **Gratuitous ARP:** Thiết bị gửi broadcast để thông báo địa chỉ IP-**MAC** của mình mà không cần yêu cầu, hữu ích cho cập nhật cache hoặc phát hiện xung đột IP.
>Gratuitous ARP ngày càng quan trọng trong môi trường đám mây và virtualization để tránh xung đột IP khi di chuyển VM.
- **Reverse ARP (RARP):** Thiết bị dùng **MAC** để tìm IP của chính mình, thường dùng cho boot từ xa (như diskless workstation), nhưng ít phổ biến nay do thay thế bởi BOOTP/DHCP.
- **Inverse ARP (InARP):** Sử dụng **MAC** để tìm IP, thường áp dụng trong Frame Relay hoặc ATM để ánh xạ địa chỉ lớp liên kết dữ liệu sang IP.

## Các thành phần quan trọng trong ARP
- **ARP Cache:** Bộ nhớ tạm lưu ánh xạ IP-**MAC** sau khi phân giải, giúp giảm broadcast. Cache có thời hạn (timeout) để cập nhật thay đổi.
- **ARP Cache Timeout:** Thời gian lưu trữ mục nhập (thường 2-20 phút tùy hệ thống), sau đó cần phân giải lại.
- **ARP Request:** Gói tin broadcast từ nguồn yêu cầu địa chỉ **MAC** của đích.
- **ARP Reply:** Phản hồi unicast từ đích gửi địa chỉ **MAC** về nguồn.

>Trong Windows (từ Vista trở lên), ARP cache được quản lý động với timeout mặc định 2 phút cho mục nhập không sử dụng, và lên đến 10 phút cho mục nhập hoạt động.

## Các loại địa chỉ trong một bản tin ARP
<img src="/images/base/address-type.png">

- **Sender Hardware Address:** Địa chỉ **MAC** của thiết bị gửi.
- **Sender Protocol Address:** Địa chỉ IP của thiết bị gửi.
- **Target Hardware Address:** Địa chỉ **MAC** của đích (ban đầu để trống trong request).
- **Target Protocol Address:** Địa chỉ IP của đích.

### Cách ARP hoạt động  
- Mạng máy tính hoạt động theo **mô hình phân lớp**. Ở tầng Network (tầng 3), các thiết bị **sử dụng địa chỉ IP để định danh logic**. Nhưng khi dữ liệu thực sự được truyền đi trên môi trường vật lý (tầng Data Link - tầng 2), **card mạng chỉ hiểu được địa chỉ **MAC**** (địa chỉ phần cứng). Đây chính là lý do ARP tồn tại - để làm cầu nối giữa hai thế giới địa chỉ này.

<img src="/images/base/arp-work.png">

- Khi máy tính của bạn chuẩn bị gửi dữ liệu, hệ điều hành đầu tiên sẽ tham khảo ARP cache - một bảng ánh xạ được lưu trữ trong bộ nhớ, ghi lại các cặp địa chỉ IP-**MAC** mà máy đã từng giao tiếp trước đó. Việc này giống như bạn kiểm tra danh bạ điện thoại trước khi gọi cho ai đó. Nếu may mắn tìm thấy địa chỉ **MAC** của 192.168.1.50 trong cache, quá trình diễn ra cực kỳ nhanh chóng - dữ liệu được đóng gói và gửi đi ngay lập tức.

- Tuy nhiên, trong trường hợp cache rỗng hoặc không có thông tin về địa chỉ đích, một cơ chế phức tạp hơn được kích hoạt. Máy tính của bạn sẽ tạo ra một gói tin ARP Request đặc biệt. Gói tin này chứa một thông điệp rất rõ ràng: "Tôi là 192.168.1.10 với **MAC** là AA:BB:CC:DD:EE:FF, ai là chủ nhân của địa chỉ IP 192.168.1.50? Hãy cho tôi biết địa chỉ **MAC** của bạn!"

- Điểm đặc biệt của gói tin ARP Request là nó được gửi dưới dạng broadcast - tức là gửi đến tất cả các thiết bị trong cùng mạng LAN. Địa chỉ **MAC** đích trong gói tin này là FF:FF:FF:FF:FF:FF, một địa chỉ đặc biệt báo hiệu "tất cả mọi người hãy lắng nghe". Switch trong mạng, khi nhận được gói broadcast này, sẽ chuyển tiếp nó ra tất cả các cổng (trừ cổng nhận vào), đảm bảo mọi thiết bị đều có cơ hội xem xét thông điệp.

- Tại mỗi thiết bị nhận được gói ARP Request, một quá trình kiểm tra diễn ra. Card mạng của thiết bị sẽ phân tích phần Target Protocol Address (địa chỉ IP đích cần tìm) trong gói tin và so sánh với địa chỉ IP được cấu hình cho chính nó. Hầu hết các thiết bị - như máy tính có IP 192.168.1.20, 192.168.1.30 - sẽ nhận ra đây không phải là gói tin dành cho mình và âm thầm loại bỏ nó. Không có phản hồi, không có thông báo lỗi - đơn giản là bỏ qua.

- Nhưng khi gói tin đến được máy chủ web 192.168.1.50, một chuỗi sự kiện khác diễn ra. Máy chủ nhận ra địa chỉ IP trong trường Target Protocol Address chính xác là địa chỉ của mình. Lúc này, nó không chỉ đơn thuần chuẩn bị trả lời mà còn thực hiện một tối ưu hóa thông minh. Từ gói ARP Request nhận được, máy chủ trích xuất thông tin về máy gửi (IP 192.168.1.10 và **MAC** AA:BB:CC:DD:EE:FF) và lưu vào ARP cache của chính nó. Đây là một động thái "học từ gói tin" rất hiệu quả - vì nếu sau này máy chủ cần gửi dữ liệu ngược lại cho máy 192.168.1.10, nó đã có sẵn thông tin **MAC** và không cần phát broadcast nữa.

- Tiếp theo, máy chủ tạo ra gói tin ARP Reply - một thông điệp trả lời mang tính chất unicast (gửi trực tiếp đến một đích cụ thể). Trong gói Reply này, máy chủ điền địa chỉ **MAC** của chính mình (giả sử 11:22:33:44:55:66) vào trường Sender Hardware Address. Khác với Request được broadcast, Reply được gửi trực tiếp đến địa chỉ **MAC** của máy hỏi (AA:BB:CC:DD:EE:FF), vì máy chủ đã biết chính xác địa chỉ này từ gói Request ban đầu.
Khi gói ARP Reply quay về máy tính của bạn, hệ thống sẽ phân tích và trích xuất thông tin quan trọng nhất: địa chỉ **MAC** 11:22:33:44:55:66 tương ứng với IP 192.168.1.50. Thông tin này ngay lập tức được cập nhật vào ARP cache với một timestamp (dấu thời gian) và thường có thời gian sống (TTL - Time To Live) từ vài phút đến vài giờ tùy cấu hình hệ điều hành. Việc lưu cache này đảm bảo rằng trong khoảng thời gian tiếp theo, mọi giao tiếp với 192.168.1.50 đều diễn ra mượt mà mà không cần phải broadcast ARP Request lại.

> Cơ chế này tuy nghe có vẻ tốn kém khi phải broadcast, nhưng thực tế lại rất hiệu quả. ARP Request chỉ được gửi một lần cho mỗi địa chỉ IP mới hoặc khi cache hết hạn. Trong môi trường mạng LAN hiện đại với switch, việc xử lý broadcast đã được tối ưu hóa rất tốt. Hơn nữa, việc cả hai bên (máy hỏi và máy trả lời) đều học và lưu thông tin của nhau từ quá trình trao đổi giúp giảm thiểu đáng kể lưu lượng ARP trong mạng.
> Nhờ ARP cache, một kết nối TCP/IP điển hình - có thể bao gồm hàng trăm gói tin qua lại - chỉ cần một cặp gói tin ARP Request/Reply duy nhất ở lần đầu tiên. Đây chính là lý do tại sao giao thức tưởng chừng đơn giản này lại là một phần không thể thiếu trong kiến trúc mạng TCP/IP.

# RARP - Reverse Address Resolution Protocol
- **RARP (Reverse Address Resolution Protocol)** là một giao thức lớp liên kết dữ liệu **(Layer 2)** được giới thiệu trong RFC 903 (1984). Nó được thiết kế với mục đích giúp các máy trạm không đĩa (diskless workstations) hoặc thiết bị không có bộ nhớ lưu trữ cố định có thể tự động lấy địa chỉ IP của mình khi khởi động, thay vì phải được cấu hình thủ công.

RARP được xem là **tiền thân của BOOTP và DHCP**, hai giao thức hiện đại hơn cung cấp khả năng cấp phát địa chỉ IP động và kèm theo thông tin cấu hình mạng khác.


## Cơ chế hoạt động của RARP
### Giai đoạn RARP Request
Khi một máy trạm vừa khởi động, nó chưa có địa chỉ IP, chỉ biết được địa chỉ MAC của chính nó. Để xin cấp IP, thiết bị này sẽ gửi một RARP Request ra mạng.

- Hình thức gửi: Broadcast đến tất cả các thiết bị trong cùng mạng LAN.

+ Địa chỉ MAC đích: ff:ff:ff:ff:ff:ff (broadcast).

+ Địa chỉ MAC nguồn: Là địa chỉ MAC của chính thiết bị.

+ Địa chỉ IP nguồn và đích: Cả hai đều là 0.0.0.0 vì thiết bị chưa có IP để gửi hoặc nhận.

- Loại frame: Ethernet II với EtherType = 0x8035 (định danh cho RARP).

- Opcode: 3 (reverse request).

- Nội dung của gói tin RARP Request bao gồm:

**Sender MAC:** Địa chỉ MAC của client.

**Sender IP:** 0.0.0.0

**Target MAC:** MAC của client (vì đang tự hỏi cho chính mình).

**Target IP:** 0.0.0.0

=> Nói cách khác, thông điệp RARP có thể hiểu là:

> “Tôi có MAC này, xin cho biết IP của tôi là gì?”

### Giai đoạn RARP Reply
Sau khi RARP Request được broadcast, RARP Server (máy chủ RARP) trong cùng subnet sẽ nhận được gói tin này.

- RARP Server tra cứu bảng ánh xạ MAC ↔ IP được cấu hình thủ công bởi quản trị viên.

- Nếu tìm thấy một bản ghi trùng khớp với địa chỉ MAC của client, server sẽ gửi RARP Reply (opcode 4) theo dạng unicast về client.

- Gói tin trả lời chứa địa chỉ IP tương ứng với MAC đó.

Ví dụ gói tin có thể quan sát bằng Wireshark:
```
Ethernet II, Src: [MAC server], Dst: [MAC client]
Type: Reverse ARP (0x8035)
Opcode: reverse reply (0x0004)
Sender MAC address: [MAC server]
Sender IP address: [IP được cấp cho client]
Target MAC address: [MAC client]
Target IP address: [IP được cấp cho client]
```
Sau khi nhận được phản hồi, thiết bị sẽ cấu hình IP được cấp vào giao diện mạng của mình và bắt đầu tham gia vào mạng.

## Đặc điểm và giới hạn của RARP
### Hoạt động ở lớp Data Link (Layer 2)
RARP hoạt động hoàn toàn ở tầng liên kết dữ liệu trong mô hình OSI. Điều này có nghĩa:
- Các gói RARP không thể đi qua router vì không có địa chỉ IP để định tuyến.
- Toàn bộ tiến trình chỉ diễn ra trong cùng một broadcast domain.

### Cấu hình tĩnh, khó mở rộng
- Quản trị viên phải duy trì bảng ánh xạ MAC-IP thủ công trên RARP Server.
- Mỗi lần thêm, thay đổi hoặc thay thế thiết bị, phải cập nhật lại cấu hình.
- Điều này khiến RARP không phù hợp cho mạng có số lượng thiết bị lớn hoặc thường xuyên thay đổi.

### Không hỗ trợ thông tin cấu hình mạng khác
- RARP chỉ cung cấp địa chỉ IP, không hỗ trợ gửi kèm các thông tin cần thiết khác như:
+ **Subnet Mask**
+ **Default Gateway**
+ **DNS Server**
+ **Thông tin Boot File**(dành cho khởi động mạng)

- Điều này khiến các máy trạm khởi động qua mạng (network boot) không thể hoạt động độc lập chỉ với RARP.

### Phạm vi hoạt động hạn chế
- Do không vượt qua được router, RARP chỉ hoạt động trong phạm vi LAN nội bộ.

- Nếu có nhiều subnet, mỗi subnet cần một RARP Server riêng.


## Kế thừa và thay thế
**RARP** nhanh chóng bị thay thế bởi các giao thức mới có khả năng cấp phát IP linh hoạt hơn và truyền qua nhiều mạng:

- **BOOTP (Bootstrap Protocol, 1985)**:
Giải quyết được các hạn chế của RARP bằng cách hoạt động ở **Layer 3 (IP Layer)**, cho phép truyền qua router và cung cấp thêm thông tin cấu hình (gateway, DNS, file boot...).

- **DHCP (Dynamic Host Configuration Protocol, 1993)**:
Mở rộng từ BOOTP, hỗ trợ cấp phát IP động, lease time, tự động tái cấp IP, và tự động hóa toàn bộ quá trình. DHCP trở thành tiêu chuẩn thực tế cho mọi hệ thống mạng hiện nay.
>
Mặc dù đã lỗi thời, RARP vẫn mang giá trị học thuật trong việc:

Hiểu rõ cơ chế ánh xạ giữa lớp liên kết dữ liệu và lớp mạng.

Nắm được tiến trình phát triển từ ARP → RARP → BOOTP → DHCP.

Là nền tảng để nghiên cứu network booting và các giao thức cấu hình tự động trong mạng IP.
>

# BOOTP - Boot Protocol
- **BOOTP (Bootstrap Protocol)** được định nghĩa trong RFC 951 (1985), ra đời nhằm khắc phục các giới hạn của RARP và mở rộng khả năng cấp phát địa chỉ IP cho các thiết bị khởi động qua mạng.
+ Không chỉ cung cấp IP, BOOTP còn truyền kèm thông tin cấu hình mạng (gateway, DNS, boot file, v.v.), đồng thời hoạt động ở tầng mạng (Layer 3) nên có thể truyền qua router, điều mà RARP không làm được.

>BOOTP là bước chuyển tiếp quan trọng từ cơ chế ánh xạ MAC–IP tĩnh sang hệ thống cấp phát cấu hình tự động, đặt nền móng cho DHCP (Dynamic Host Configuration Protocol) sau này.

## Cơ chế hoạt động của BOOTP
### Kiến trúc tổng thể
BOOTP gồm ba thành phần chính:
- **BOOTP Client:** Thiết bị cần được cấp IP và thông tin cấu hình mạng.
- **BOOTP Server:** Máy chủ chứa bảng ánh xạ MAC–IP và các thông tin cấu hình mạng khác.
- **BOOTP Relay Agent:** Thiết bị trung gian (thường là router) dùng để chuyển tiếp broadcast BOOTP từ subnet này sang subnet khác, giúp một server trung tâm phục vụ nhiều mạng con.

BOOTP hoạt động dựa trên UDP/IP:
- **Port 68:** Client lắng nghe phản hồi.
- **Port 67:** Server nhận yêu cầu từ client.

### Quá trình trao đổi BOOTP
**Bước 1 – BOOTP Request (Discover)**

Khi khởi động, BOOTP Client chưa có IP, nó sẽ gửi một gói BOOTP Request dưới dạng broadcast để yêu cầu cấp phát IP.
- **Địa chỉ IP nguồn:** `0.0.0.0` (vì chưa có IP).
- **Địa chỉ IP đích:** `255.255.255.255` (broadcast toàn mạng).
- **Địa chỉ MAC nguồn:** MAC của client.
- **Giao thức:** UDP (port `68` → `67`).

Nếu client và server **không nằm trong cùng subnet**, broadcast này sẽ **không đi qua router**.
→ Để khắc phục, router phải được cấu hình IP helper-address, cho phép chuyển tiếp (relay) gói BOOTP đến server trung tâm qua UDP unicast.

**Bước 2 – BOOTP Reply (Offer)**
Sau khi nhận được yêu cầu, BOOTP Server tra cứu bảng ánh xạ MAC–IP do quản trị viên cấu hình thủ công.

Nếu tìm thấy bản ghi tương ứng, server sẽ gửi lại BOOTP Reply theo dạng unicast hoặc broadcast (nếu client chưa có IP).

Gói phản hồi chứa nhiều thông tin hơn so với RARP, bao gồm:
- **Địa chỉ IP cấp cho client.**
- **Subnet Mask.**
- **Default Gateway.**
- **DNS Server(s).**
- **Tên file khởi động (Boot file name)** – dùng khi client cần tải file hệ điều hành qua TFTP/NFS để khởi động (dành cho diskless devices).

## Cấu trúc gói tin BOOTP
Một gói BOOTP có độ dài cố định (300 byte cơ bản, có thể mở rộng). Dưới đây là các trường chính:
### Trường cơ bản
- **Op:** Loại hoạt động (1 = Request, 2 = Reply).
- **Htype / Hlen:** Loại phần cứng và độ dài địa chỉ (Ethernet = 1, MAC = 6 bytes).
- **Hops:** Số lần relay (mỗi relay agent tăng giá trị này lên 1).
- **Xid (Transaction ID):** Mã định danh để ghép cặp Request–Reply.
- **Secs / Flags:** Thời gian client đã chờ và cờ broadcast.

### Địa chỉ IP liên quan
- **Ciaddr (Client IP Address):** IP hiện tại của client (nếu có).
- **Yiaddr (Your IP Address):** IP mà server cấp cho client.
- **Siaddr (Server IP Address):** IP của server BOOTP.
- **Giaddr (Gateway/Relay IP Address):** IP của relay agent (nếu có).

### Địa chỉ phần cứng
**Chaddr:** Địa chỉ MAC của client, thường được padding đến 16 bytes.

### Trường mô tả và tuỳ chọn
- **Sname:** Tên máy chủ BOOTP.
- **File:** Tên hoặc đường dẫn đến boot file (qua TFTP).
- **Options:** Thông tin mở rộng theo vendor (vendor-specific options), có thể chứa DNS, NTP, domain name, v.v.
→ Chính phần Options này sau này được mở rộng thành DHCP Options trong DHCP.

## Cơ chế hoạt động qua Relay Agent
Khi BOOTP Client nằm ở một subnet khác với server, BOOTP Relay Agent sẽ:
- Nhận gói broadcast BOOTP Request trong mạng cục bộ.
- Ghi địa chỉ IP của mình vào trường Giaddr.
- Gửi lại gói này đến BOOTP Server qua unicast UDP port 67.
- Khi server phản hồi, relay agent sẽ chuyển tiếp gói BOOTP Reply trở lại client tương ứng trong mạng ban đầu.

Cơ chế này giúp:
- Tập trung hóa việc quản lý (chỉ cần một BOOTP Server duy nhất).
- Phục vụ nhiều subnet khác nhau, giảm gánh nặng quản trị.

## Đặc điểm và hạn chế của BOOTP
### Ưu điểm so với RARP
- Hoạt động ở **Layer 3**, có thể route qua mạng.
- Cung cấp thêm thông tin cấu hình (mask, gateway, DNS, boot file).
- Hỗ trợ **relay agent**, dễ triển khai mô hình tập trung.
- Là cơ sở để phát triển DHCP.

### Hạn chế
- Cấp phát tĩnh: BOOTP vẫn yêu cầu cấu hình MAC–IP cố định trên server.
- Không hỗ trợ lease time: Địa chỉ IP được cấp vĩnh viễn, dễ gây xung đột khi thiết bị di chuyển giữa mạng.
- Thiếu tính linh hoạt: Không có cơ chế cấp IP động hoặc thu hồi IP tự động.
- Phụ thuộc vào quản trị viên: Mỗi thay đổi thiết bị cần chỉnh lại cấu hình thủ công.

## Sự kế thừa và phát triển
Do các hạn chế trên, BOOTP nhanh chóng được thay thế bởi **DHCP (Dynamic Host Configuration Protocol)** vào năm 1993.
DHCP kế thừa toàn bộ cấu trúc BOOTP, nhưng thêm nhiều khả năng mới:
- **Cấp phát IP động** (dynamic pool allocation).
- **Lease time** (thời hạn sử dụng IP).
- **Renewal & Rebinding** (gia hạn tự động).
- **Tùy chọn cấu hình mở rộng** qua DHCP Options.

Mặc dù DHCP hiện nay đã thay thế hoàn toàn BOOTP, nhiều thiết bị và router vẫn duy trì tương thích ngược để hỗ trợ các hệ thống cũ.

## Kết luận 
BOOTP đánh dấu bước ngoặt quan trọng trong lịch sử quản trị mạng:
- Là giao thức đầu tiên cầu nối giữa RARP và DHCP, mở rộng cấp phát IP từ phạm vi LAN sang mô hình liên mạng.
- Giúp hình thành khái niệm centralized configuration management – quản lý cấu hình tập trung qua IP.
- Là nền tảng của network boot (PXE) – cơ chế khởi động hệ điều hành qua mạng, vẫn được sử dụng phổ biến trong các hệ thống ảo hóa và cloud hiện nay.

>Tóm lại, BOOTP không chỉ là một giao thức quá khứ, mà là viên gạch đầu tiên trong tiến trình tự động hóa quản lý địa chỉ mạng – từ RARP tĩnh đến DHCP động, mở ra kỷ nguyên quản trị mạng hiện đại.

# DHCP - Dynamic Host Configuration Protocol
- **DHCP (Dynamic Host Configuration Protocol)** là giao thức cấu hình máy chủ động, cho phép cấp phát địa chỉ IP tự động cùng các thông tin cấu hình khác như subnet mask, default gateway, DNS server, giúp quản lý mạng hiệu quả hơn.

- DHCP cung cấp cơ sở dữ liệu trung tâm để theo dõi các thiết bị, tránh xung đột IP và giảm can thiệp thủ công. Nó hoạt động theo mô hình client-server, sử dụng UDP cổng 67 (server) và 68 (client).
> Với IPv6, DHCPv6 được sử dụng để cấp phát địa chỉ IPv6 và các thông số khác, thường kết hợp với Stateless Address Autoconfiguration (SLAAC).

- DHCP hỗ trợ cập nhật động DNS (Dynamic DNS updates), cho phép tự động cập nhật bản ghi DNS khi IP thay đổi. Trong Windows Server 2025, DHCP có tính năng Highly Available để đảm bảo tính sẵn sàng cao.

## Ưu điểm của việc cấp phát động so với cấp phát tĩnh

- **Giảm xung đột IP và chi phí quản trị** bằng cách tự động hóa việc cấp phát.
- **Tiết kiệm địa chỉ IP công cộng** cho ISP bằng cách tái sử dụng IP động.
- **Phù hợp cho thiết bị** di động **thường xuyên thay đổi mạng**.
- **Hỗ trợ mạng không dây và hotspot**, dễ dàng mở rộng mạng mà không cần cấu hình thủ công.

> Cấp phát động giúp tích hợp tốt hơn với đám mây và virtualization, nơi IP cần thay đổi linh hoạt.

## Cách DHCP hoạt động 

- Để một thiết bị có thể hoạt động trong mạng TCP/IP, nó cần tối thiểu bốn thông tin quan trọng: **địa chỉ IP duy nhất, subnet mask để xác định phạm vi mạng, default gateway để ra ngoài internet, và địa chỉ DNS server để phân giải tên miền**. Trước khi có DHCP, quản trị viên phải thủ công cấu hình từng máy một - một công việc tẻ nhạt, dễ sai sót và không khả thi với mạng lớn. DHCP ra đời để tự động hóa toàn bộ quá trình này.

- Khi laptop của bạn khởi động, card mạng được kích hoạt nhưng chưa có bất kỳ thông tin cấu hình nào. Lúc này, hệ điều hành khởi tạo một gói tin DHCPDISCOVER - về bản chất là một lời kêu gọi được phát đi khắp mạng. Gói tin này mang trong mình một nghịch lý thú vị: địa chỉ IP nguồn là 0.0.0.0 (vì máy chưa có IP), địa chỉ đích là 255.255.255.255 (địa chỉ broadcast đặc biệt), nhưng chứa đầy đủ địa chỉ **MAC** và hostname của máy tính. Đây chính là cách một thiết bị "vô danh" giới thiệu bản thân với thế giới mạng.
<img src="/images/base/dhcp-1.png">

+ Gói DHCPDISCOVER được truyền qua cổng UDP 68 (client port) và hướng đến cổng 67 (server port). Việc sử dụng broadcast đảm bảo rằng tất cả DHCP server trong cùng mạng LAN đều có thể nhận được yêu cầu này. Switch trong mạng, khi nhận được frame broadcast, sẽ sao chép và chuyển tiếp ra tất cả các cổng, đảm bảo thông điệp đến được mọi ngóc ngách của mạng.
<img src="/images/base/dhcp-2.png">

+ Tại phía server, khi DHCP server nhận được DHCPDISCOVER, nó bắt đầu một quá trình ra quyết định phức tạp. Server kiểm tra pool địa chỉ IP khả dụng, xem xét các địa chỉ đã được thuê, địa chỉ đã reserve cho thiết bị cụ thể, và thậm chí có thể áp dụng các chính sách phân bổ dựa trên **MAC** address hoặc subnet. Sau khi chọn được một địa chỉ IP phù hợp (giả sử 192.168.1.100), server tạo gói tin **DHCPOFFER**.
<img src="/images/base/dhcp-3.png">

+ Gói **DHCPOFFER** không chỉ đơn thuần chứa địa chỉ IP được đề xuất mà còn là một "gói quà" đầy đủ thông tin cấu hình: subnet mask (ví dụ 255.255.255.0), default gateway (192.168.1.1), DNS servers (có thể là 8.8.8.8 và 8.8.4.4), và quan trọng nhất là lease time - thời gian được phép sử dụng IP này (thường mặc định 8 ngày hay 691,200 giây trong nhiều hệ thống). Server cũng đính kèm địa chỉ IP của chính mình để client biết đang nhận Offer từ ai.
<img src="/images/base/dhcp-4.png">

+ Về mặt kỹ thuật, **DHCPOFFER** được gửi dưới dạng unicast trực tiếp đến **MAC** address của client nếu có thể. Tuy nhiên, vì client vẫn chưa có IP hợp lệ, một số hệ thống sẽ gửi Offer dưới dạng broadcast để đảm bảo client nhận được. Đây là một trong những thiết kế linh hoạt của DHCP, cho phép nó hoạt động trong nhiều môi trường mạng khác nhau.
<img src="/images/base/dhcp-5.png">

+ Điều thú vị xảy ra khi có nhiều DHCP server trong cùng một mạng - một tình huống phổ biến trong các tổ chức lớn để đảm bảo tính sẵn sàng cao. Client có thể nhận được nhiều **DHCPOFFER** từ các server khác nhau, mỗi Offer đề xuất một địa chỉ IP và cấu hình có thể khác nhau. Theo thiết kế của giao thức, client thường chấp nhận Offer đầu tiên mà nó nhận được, mặc dù một số triển khai cho phép client chọn lựa dựa trên các tiêu chí khác như lease time dài nhất.
<img src="/images/base/dhcp-6.png">

+ Sau khi quyết định chọn Offer từ một server cụ thể, client gửi gói tin DHCPREQUEST. Đây lại là một broadcast mang thông điệp kép: một mặt nó xác nhận với server được chọn rằng "Tôi chấp nhận IP mà bạn đề nghị", mặt khác nó thông báo cho tất cả các server khác rằng "Cảm ơn các đề nghị của bạn, nhưng tôi đã chọn rồi". Gói DHCPREQUEST chứa identifier của server được chọn, cho phép các server khác biết được họ không được chọn và có thể giải phóng các IP đã reserve cho client này.
<img src="/images/base/dhcp-7.png">

+ Khi server được chọn nhận DHCPREQUEST, nó thực hiện bước cuối cùng: ghi nhận giao dịch này vào database, đánh dấu IP đã được thuê, ghi lại **MAC** address, hostname, và thời điểm bắt đầu lease. Sau đó server gửi DHCPACK - gói tin xác nhận cuối cùng. DHCPACK về bản chất là sự xác nhận chính thức rằng giao dịch đã hoàn tất, client có toàn quyền sử dụng IP và cấu hình được cung cấp trong khoảng thời gian lease time.

- **Nhưng điều gì xảy ra nếu quá trình này thất bại?** Giả sử client gửi DHCPDISCOVER nhưng không nhận được Offer nào sau một khoảng thời gian timeout (thường vài giây). Client sẽ không bỏ cuộc ngay mà thực hiện retry - gửi lại DHCPDISCOVER với khoảng thời gian chờ tăng dần theo thuật toán exponential backoff. Sau bốn lần thử không thành công, một cơ chế dự phòng tự động được kích hoạt: **APIPA** (Automatic Private IP Addressing).

- **APIPA** là giải pháp tự cứu của hệ điều hành Windows và một số hệ thống khác. Client sẽ tự động gán cho mình một địa chỉ IP trong dải 169.254.0.1 đến 169.254.255.254 với subnet mask 255.255.0.0. Địa chỉ này được chọn ngẫu nhiên và sau đó client thực hiện ARP probe để đảm bảo không bị trùng với máy khác trong mạng. Mặc dù với **APIPA**, máy tính không thể ra ngoài internet hoặc truy cập tài nguyên ở subnet khác, nó vẫn có thể giao tiếp với các máy khác trong cùng mạng cục bộ cũng đang dùng **APIPA**. Client sẽ tiếp tục broadcast DHCPDISCOVER mỗi 5 phút hy vọng rằng DHCP server sẽ trở lại hoạt động.

### Cơ chế duy trì kết nối liên tục
- Sau khi client thành công nhận được IP và bắt đầu sử dụng, một cơ chế tự động ngầm hoạt động trong nền để duy trì kết nối. Lease time không phải là con số tĩnh mà là một đồng hồ đếm ngược liên tục. Khi đồng hồ này chạy đến mốc 50% (tức là sau 4 ngày nếu lease là 8 ngày), client tự động khởi động quá trình renewal.

- Quá trình renewal này diễn ra rất khác với lúc xin IP ban đầu. Thay vì broadcast, client gửi DHCPREQUEST unicast trực tiếp đến địa chỉ IP của server gốc đã cấp IP cho nó. Gói tin này về bản chất là một yêu cầu gia hạn: "Tôi vẫn đang ở đây và muốn tiếp tục sử dụng IP này". Nếu server vẫn hoạt động và không có lý do gì để từ chối, nó sẽ trả lời bằng DHCPACK với lease time được reset về giá trị ban đầu. Quá trình này diễn ra hoàn toàn trong nền, người dùng không hề hay biết, và vì sử dụng unicast nên không gây broadcast storm trong mạng.

- **Nhưng nếu server gốc đã offline hoặc không phản hồi thì sao?**Client không hoảng loạn ngay mà tiếp tục sử dụng IP hiện tại và đợi đến mốc 87.5% lease time (tức là ngày thứ 7 nếu lease là 8 ngày). Lúc này, một cơ chế khẩn cấp hơn được kích hoạt gọi là rebinding. Client broadcast DHCPREQUEST ra toàn mạng, không còn nhắm đến server cụ thể nào nữa mà chấp nhận bất kỳ DHCP server nào có thể gia hạn IP cho nó. Đây có thể là server backup, server mới được cài đặt, hoặc thậm chí server ở site khác trong hệ thống failover.

- Nếu cả rebinding cũng thất bại và lease time hết hạn hoàn toàn, client buộc phải giải phóng IP và quay về trạng thái ban đầu - gửi DHCPDISCOVER như một thiết bị mới hoàn toàn. Kết nối mạng sẽ bị gián đoạn cho đến khi nhận được IP mới. Đây là lý do tại sao các tổ chức quan trọng luôn triển khai nhiều DHCP server và giám sát chặt chẽ hoạt động của chúng.

### Vấn đề vượt qua ranh giới mạng
- DHCP được thiết kế dựa trên broadcast, nhưng broadcast có một hạn chế lớn: nó không thể vượt qua router. Khi một router nhận được gói broadcast, nó sẽ không chuyển tiếp sang subnet khác vì nếu làm thế, toàn bộ hệ thống mạng sẽ bị ngập trong broadcast. Điều này tạo ra một bài toán thực tế: nếu một công ty có 50 subnet khác nhau, liệu họ phải đặt 50 DHCP server, mỗi subnet một cái?

- Giải pháp nằm ở DHCP Relay Agent - một chức năng đặc biệt có thể được cấu hình trên router hoặc một máy tính chuyên dụng. Relay Agent hoạt động như một "người đưa thư" thông minh, nghe broadcast trong subnet cục bộ và chuyển đổi chúng thành unicast để gửi đến DHCP server ở subnet khác.

- Cơ chế này hoạt động như sau: Khi một laptop trong subnet 192.168.10.0/24 broadcast DHCPDISCOVER, router đóng vai trò Relay Agent sẽ bắt gói tin này. Thay vì loại bỏ như một router thông thường, Relay Agent thêm một thông tin quan trọng vào gói tin gọi là GIADDR (Gateway IP Address) - chính là địa chỉ IP của interface router nối với subnet của client. Sau đó, Relay Agent đóng gói lại và gửi unicast đến địa chỉ của DHCP server (đã được cấu hình sẵn), giả sử server ở subnet 10.0.0.0/8 với IP 10.0.0.5.

- DHCP server, khi nhận được gói tin từ Relay Agent, đọc thông tin GIADDR và nhận ra rằng client đến từ subnet 192.168.10.0/24. Dựa vào thông tin này, server chọn địa chỉ IP từ pool phù hợp với subnet đó (ví dụ 192.168.10.50) và tạo **DHCPOFFER**. Server không gửi Offer trực tiếp cho client vì client không cùng subnet, mà gửi unicast về Relay Agent theo địa chỉ GIADDR.
Relay Agent nhận **DHCPOFFER**, loại bỏ header unicast ra ngoài, và broadcast gói tin vào subnet cục bộ để client nhận được. Quá trình tương tự lặp lại với DHCPREQUEST và DHCPACK. Nhờ cơ chế này, một DHCP server duy nhất có thể phục vụ hàng chục, thậm chí hàng trăm subnet khác nhau, miễn là các router giữa chúng được cấu hình đúng chức năng Relay Agent.

+ Một chi tiết kỹ thuật quan trọng: không phải switch nào cũng mặc định chuyển tiếp broadcast trên cổng 67/68. Một số switch managed yêu cầu quản trị viên phải explicit cho phép DHCP traffic qua các cổng, đặc biệt trong các mạng có security policy nghiêm ngặt. Điều này đôi khi là nguyên nhân của việc DHCP không hoạt động trong mạng mới được triển khai.

### Những tình huống đặc biệt trong thực tế
- Trong môi trường doanh nghiệp lớn, DHCP không chỉ đơn thuần cấp IP mà còn trở thành công cụ quản lý mạng mạnh mẽ. Một client có thể nhận được hàng chục tùy chọn khác nhau qua DHCP: địa chỉ TFTP server để boot qua mạng, URL của file cấu hình tự động cho VoIP phone, thông tin về proxy server, NTP server cho đồng bộ thời gian, thậm chí cả thông tin về VLAN assignment.
+ Các hệ thống DHCP hiện đại cũng hỗ trợ reservation - khả năng gắn một địa chỉ IP cố định cho một **MAC** address cụ thể. Khi máy in văn phòng với **MAC** AA:BB:CC:DD:EE:FF yêu cầu IP, server sẽ luôn cấp cho nó 192.168.1.200, tạo ra sự ổn định mà không cần phải cấu hình IP tĩnh trên chính thiết bị.

- Failover và load balancing giữa các DHCP server là một chủ đề phức tạp khác. Hai DHCP server có thể được cấu hình để chia sẻ cùng một pool địa chỉ theo tỷ lệ 50-50 hoặc 80-20 (primary-backup). Chúng liên tục đồng bộ thông tin về các lease đang hoạt động qua một kênh riêng biệt, đảm bảo rằng nếu một server sập, server còn lại có thể tiếp quản ngay lập tức mà không gây gián đoạn service.

- Một vấn đề thực tế khác mà quản trị viên thường gặp là DHCP starvation attack - kiểu tấn công trong đó kẻ xấu gửi hàng ngàn DHCPDISCOVER với **MAC** address giả mạo khác nhau, nhanh chóng làm cạn kiệt pool địa chỉ IP và khiến người dùng hợp lệ không thể xin được IP. Các biện pháp phòng chống bao gồm DHCP snooping trên switch - chức năng cho phép switch theo dõi các giao dịch DHCP và chặn các gói tin bất thường, hoặc giới hạn số lượng **MAC** address trên mỗi cổng switch.

- Trong bối cảnh Windows Server, các bản cập nhật năm 2025 đôi khi gây ra vấn đề tương thích với DHCP service trên các server cũ, đặc biệt là khi có sự khác biệt về version giữa DHCP server và domain controller. Quản trị viên cần theo dõi sát các bulletin từ Microsoft và test kỹ lưỡng trên môi trường staging trước khi áp dụng patch lên production.

### Ý nghĩa trong kiến trúc mạng hiện đại
- DHCP đã trở thành xương sống của tính linh hoạt trong mạng máy tính hiện đại. Nó cho phép người dùng di chuyển laptop từ phòng họp này sang văn phòng kia, từ nhà đến quán cà phê, mà luôn được tự động cấu hình đúng. Đối với IoT devices - từ camera an ninh đến cảm biến nhiệt độ - DHCP là giải pháp duy nhất khả thi khi số lượng thiết bị lên đến hàng ngàn.

- Tuy nhiên, DHCP cũng mở ra các vấn đề bảo mật mới. Việc bất kỳ thiết bị nào cũng có thể xin IP chỉ bằng cách gửi DHCPDISCOVER có nghĩa là kiểm soát truy cập mạng không thể dựa hoàn toàn vào DHCP. Các giải pháp như 802.1X authentication, NAC (Network Access Control), và kết hợp với DHCP option 82 (relay agent information) được sử dụng để tăng cường bảo mật.

- Nhìn từ góc độ tối ưu hiệu suất, việc điều chỉnh lease time là một nghệ thuật cân bằng. Lease time quá ngắn (vài giờ) tạo ra nhiều traffic renewal không cần thiết. Lease time quá dài (vài tuần) khiến pool IP có thể bị cạn kiệt vì các địa chỉ được giữ bởi thiết bị không còn hoạt động. Trong mạng với thiết bị di động cao như WiFi khách, lease time 1-2 ngày thường là hợp lý. Trong mạng văn phòng ổn định, 7-14 ngày là lựa chọn phổ biến.

# DNS - Domain Name System
- **DNS (Domain Name System)** là hệ thống phân giải tên miền, đồng thời là giao thức (protocol) cho phép thiết lập tương ứng giữa tên miền dễ nhớ (như example.com) và địa chỉ IP (như 192.0.2.1). Nó được phát minh năm 1983 bởi Paul Mockapetris và chính thức triển khai năm 1984 cho Internet, định nghĩa trong RFC 1034 và 1035.

- DNS hoạt động như một cuốn sổ địa chỉ phân tán toàn cầu, giúp các thiết bị kết nối mà không cần nhớ địa chỉ IP phức tạp. Nó không chỉ là hệ thống mà còn là giao thức sử dụng UDP/TCP cổng 53 để trao đổi truy vấn và phản hồi.
```
Ví dụ: Chuyển `www.example.com` thành 93.184.216.34 (IPv4) hoặc 2606:2800:220:1:248:1893:25c8:1946 (IPv6)..
```

DNS đã phát triển với các tính năng bảo mật như [DNSSEC (DNS Security Extensions)](/04-network/principals/dnssec.md) để chống giả mạo, và [DoH (DNS over HTTPS)](/04-network/principals/dns-doh.md) để mã hóa truy vấn, giảm rủi ro theo dõi. DoH được hỗ trợ rộng rãi trên các trình duyệt như Chrome và Firefox, và các dịch vụ như Cloudflare (1.1.1.1) hoặc Google (8.8.8.8).

## Chức năng của DNS
- Chuyển dịch tên miền sang địa chỉ IP để định tuyến lưu lượng.
- Cung cấp alias (bí danh) cho máy chủ, như redirect subdomain sang tên khác.
- Phân tải (load balancing): Trả về nhiều IP cho cùng tên miền để phân phối tải giữa các server.
- Hỗ trợ các dịch vụ khác như email (qua MX records) và xác thực (qua TXT records cho SPF/DKIM).
>DNS còn hỗ trợ IPv6 migration và zero-configuration networking (như mDNS cho mạng cục bộ). Trong năm 2025, với sự gia tăng IoT, DNS đóng vai trò quan trọng trong dịch vụ discovery như Bonjour của Apple.

## Các Bản Ghi và Loại DNS Server
### Các bản ghi của DNS
- **A Record:** Trỏ tên miền đến địa chỉ IPv4 cụ thể, với TTL (Time to Live) để kiểm soát thời gian cache.
- **AAAA Record:** Tương tự A nhưng cho IPv6, hỗ trợ địa chỉ dài hơn.
- **CNAME Record:** Tạo alias, trỏ tên miền này sang tên miền khác (không phải IP trực tiếp), hữu ích cho subdomain.
- **MX Record:** Chỉ định mail server cho tên miền, với priority để ưu tiên server chính/phụ.
- **TXT Record:** Lưu trữ văn bản tùy ý, thường dùng cho xác thực (SPF, DKIM) hoặc metadata.
- **SRV Record:** Xác định dịch vụ chạy trên port nào, với priority, weight, port, và target.
- **NS Record:** Chỉ định name server cho domain hoặc subdomain, quản lý ủy quyền.

>Các bản ghi mới nổi bật năm 2025 bao gồm HTTPS records (RFC 9460) để chỉ định chứng chỉ TLS trực tiếp trong DNS, hỗ trợ Encrypted Client Hello (ECH) cho bảo mật tốt hơn.

### Các loại DNS Server
- **Root Name Servers:** 13 server logic (thực tế hàng trăm instance toàn cầu), chứa thông tin về TLD servers. Quản lý bởi các tổ chức như Verisign, ICANN.
- **Top-Level Domain (TLD) Servers:** Quản lý TLD như .com, .org, .net, .edu, và ccTLD như .vn, .uk. Ví dụ: Verisign quản lý .com, VNIX quản lý .vn.
- **Authoritative DNS Servers:** Server chính thức của tổ chức, lưu trữ bản ghi DNS cho domain cụ thể, cung cấp ánh xạ hostname-IP. Có thể tự host hoặc qua ISP/cloud như AWS Route 53.
- **Local/Recursive DNS Servers:** Server nội bộ (như của ISP hoặc công ty), xử lý truy vấn từ client, cache kết quả, và đệ quy đến các server khác nếu cần.


## Cách hoạt động của DNS
- **Truy vấn đệ quy (Recursive Query):** Client gửi query đến local server, local server đệ quy truy vấn đến root → TLD → authoritative, rồi trả kết quả đầy đủ về client. Phù hợp cho client đơn giản, nhưng tải nặng cho server.
<img src="/images/base/dns-1.png">

- **Truy vấn tuần tự (Iterative Query):** Local server nhận query, hỏi root và nhận referral (gợi ý server tiếp theo), rồi tự hỏi TLD, authoritative. Server chỉ trả referral, client/local server tự xử lý tiếp.
<img src="/images/base/dns-2.png">

- **Quy trình chung:** Client kiểm tra cache local → hỏi recursive server → đệ quy/iterative qua hierarchy → authoritative trả bản ghi.

>DNS sử dụng cả UDP (nhanh cho query nhỏ) và TCP (cho query lớn hoặc zone transfer). Năm 2025, QUIC(UDP-based) và DoQ ( DNS over QUIC) để tăng tốc bảo mật 

### DNS Cache và cập nhật các bản ghi
- Khi server nhận ánh xạ (mapping), nó cache với TTL để tránh query lặp lại. Cache ở nhiều cấp: client OS, local server, ISP.
- Khi bản ghi thay đổi, authoritative server đẩy update qua NOTIFY (RFC 1996) hoặc client refresh sau TTL hết hạn.
- Local servers thường cache TLD mappings để giảm tải root servers.

> Cache poisoning là rủi ro lớn

### Khung dạng bản tin
- Bản tin DNS gồm header (12 bytes): ID, flags (query/reply, recursion), counts (questions, answers, authority, additional).
- Phần Questions: Tên miền, type (A, MX,...), class (IN for Internet).
- Phần Answers/Authority/Additional: Resource records với name, type, class, TTL, length, data.
<img src="/images/base/dns-3.png">

> Bản tin hỗ trợ EDNS (Extension Mechanisms for DNS) cho query lớn hơn 512 bytes UDP, phổ biến trong IPv6 và DNSSEC.


# FTP - File Transfer Protocol
**Khái niệm:**  
**FTP (File Transfer Protocol)** là giao thức truyền tập tin thường được dùng để trao đổi tập tin qua mạng lưới truyền thông dùng giao thức TCP/IP.
- Hoạt động trên mô hình Client-Server.
- Không giống như các ứng dụng khác chạy trên nền TCP, FTP không chỉ cần một kết nối TCP mà các mô hình FTP được thiết kế xung quanh 2 kênh logic trong quá trình giao tiếp giữa client FTP và server FTP là control connection và data connection.
+ Control connection: được tạo ra khi phiên làm việc được thiết lập. Nó được duy trì trong suốt phiên làm việc và chỉ cho các thông tin điều khiển đi qua ví dụ như lệnh và trả lời. Nó không được sử dụng để gửi dữ liệu.
+ Data connection: Mỗi khi dữ liệu được gửi từ sever tới client hoặc ngược lại, một kết nối dữ liệu TCP riêng biệt được thiết lập giữa chúng. Dữ liệu được truyền qua kết nối này. Khi hoàn tất việc truyền dữ liệu, kết nối được hủy bỏ.
<img src="/images/base/ftp-1.png">

## Cơ chế hoạt động 
FTP hoạt động theo mô hình client-server, với các tiến trình riêng biệt để quản lý điều khiển và dữ liệu.

<img src="/images/base/ftp-flow.png">

### Tiến trình bên phía server
- **Server Protocol Interpreter (Server-PI):** Quản lý kênh điều khiển, lắng nghe kết nối trên cổng `21`, nhận lệnh từ client, gửi phản hồi và điều khiển quá trình truyền dữ liệu.
- **Server Data Transfer Process (Server-DTP):** Xử lý kênh dữ liệu, gửi/nhận file, tương tác với hệ thống file cục bộ để đọc/ghi dữ liệu.

### Tiến trình bên phía client
- **User Interface:** Giao diện người dùng để nhập lệnh đơn giản, theo dõi tiến trình và kết quả phiên FTP.
- **User Protocol Interpreter (User-PI):** Quản lý kênh điều khiển phía client, khởi tạo kết nối, gửi lệnh đến server và xử lý phản hồi, đồng thời điều khiển User-DTP.
- **User Data Transfer Process (User-DTP):** Xử lý kênh dữ liệu, gửi/nhận file, tương tác với hệ thống file cục bộ của client.

## Kết Nối, Chứng Thực và Quản Lý Dữ Liệu trong FTP
### Thiết lập kênh điều khiển và chứng thực người dùng
<img src="/images/base/ftp-2.png">

- Kênh điều khiển được thiết lập đầu tiên: Server-PI lắng nghe cổng 21 TCP; User-PI khởi tạo kết nối từ client đến server.
- **Chứng thực:** Client gửi lệnh `USER` (tên người dùng) rồi PASS (mật khẩu). Server kiểm tra cơ sở dữ liệu; nếu hợp lệ, xác nhận phiên; nếu sai, yêu cầu thử lại hoặc ngắt kết nối sau số lần giới hạn.

>Chứng thực FTP cơ bản dễ bị tấn công nghe lén (sniffing) vì gửi plaintext. Năm 2025, khuyến nghị sử dụng FTPS với TLS 1.3 để mã hóa, hoặc SFTP để tránh rủi ro.

### Quản lý kênh dữ liệu FTP
<img src="/images/base/ftp-3.png">

- FTP sử dụng hai chế độ để thiết lập kênh dữ liệu (thường trên cổng động):
- **Active Mode:** Server khởi tạo kết nối dữ liệu từ cổng `20` đến client (dựa trên `PORT` lệnh từ client). Phù hợp mạng không có firewall nghiêm ngặt, nhưng thường bị chặn bởi NAT/firewall.
- **Passive Mode:** Client khởi tạo kết nối (qua lệnh `PASV`); server mở cổng động và thông báo cho client. An toàn hơn với firewall, phổ biến trong môi trường hiện đại.

### Các phương thức truyền dữ liệu trong FTP
- **Stream Mode:** Truyền dữ liệu liên tục như dòng byte, không cấu trúc khối, kết thúc bằng EOF (End of File).
- **Block Mode:** Dữ liệu được chia thành khối với header (descriptor, size), hỗ trợ truyền gián đoạn.
- **Compressed Mode:** Nén dữ liệu trước khi truyền để tiết kiệm băng thông, sử dụng thuật toán đơn giản như Run-Length Encoding.

## Lệnh và Demo Sử Dụng FTP
### Bản tin yêu cầu (các lệnh FTP)
```
OPEN <server> <port>: Mở kết nối đến server FTP.
LOGIN: Bắt đầu đăng nhập (thường kết hợp USER và PASS).
USER <username>: Gửi tên người dùng.
PASS <password>: Gửi mật khẩu.
PWD: Hiển thị thư mục hiện tại.
CWD <pathname>: Thay đổi thư mục hiện tại.
RENAME: Đổi tên tệp/thư mục (kết hợp RNFR và RNTO).
RNFR <pathname>: Chỉ định tên cũ để đổi.
RNTO <pathname>: Chỉ định tên mới.
LIST: Liệt kê tệp và thư mục.
MKD <pathname>: Tạo thư mục.
RMD <pathname>: Xóa thư mục.
DELE <pathname>: Xóa tệp.
DOWNLOAD <pathname>: Tải về tệp/thư mục (thường dùng RETR).
UPLOAD: Tải lên tệp (thường dùng STOR).
CLOSE: Đóng kết nối (QUIT).
HELP: Hiển thị trợ giúp lệnh.
```

---

# SMTP - Simple Mail Transfer Protocol
**Định nghĩa:**  
- **SMTP** là viết tắt của **Simple Mail Transfer Protocol (Giao thức Truyền tải Thư tin Đơn giản hóa)**. Đây là một giao thức giao tiếp được sử dụng để gửi và nhận email qua Internet. Máy chủ thư và các công cụ truyền thư (MTA) sử dụng SMTP để gửi, nhận và chuyển tiếp thư điện tử.

- **SMTPS (Giao thức Truyền tải Thư tin Đơn giản hóa Bảo Mật)** là một phương pháp bảo mật SMTP bằng cách sử dụng bảo mật lớp truyền tải. Nó được dùng để xác thực các đối tác truyền thông, tính toàn vẹn và tính bảo mật của dữ liệu. 
+ Nó sử dụng **SSL (Lớp Cổng Bảo mật)** hoặc **TLS (Bảo mật Lớp Truyền tải)** để thiết lập kết nối bảo mật, đảm bảo tính bảo mật và tính toàn vẹn của việc truyền email. 
* Chứng chỉ SSL/TLS được sử dụng để thiết lập kết nối bảo mật trong SMTPS, đảm bảo tính bảo mật và toàn vẹn dữ liệu khi truyền email.
* **SSL (Lớp Cổng Bảo mật)** và **TLS (Bảo mật Lớp Truyền tải)** là các giao thức bảo mật được sử dụng để mã hóa kết nối **SMTP**. **TLS** là phiên bản cải tiến và an toàn hơn của SSL, thường được ưu tiên sử dụng trong các kết nối bảo mật hiện đại.
+ Máy khách và máy chủ phát ra SMTP bình thường ở lớp ứng dụng và kết nối được bảo mật bằng SSL hoặc TLS.

## Máy Chủ SMTP
- Máy chủ **SMTP**, còn được gọi là **máy chủ thư đi**, là một máy tính hoặc phần mềm xử lý các email gửi đi. Nói chung, một máy chủ thư là một hệ thống tập hợp, xử lý và gửi email. Máy chủ SMTP đề cập cụ thể đến thành phần của máy chủ thư sử dụng Giao thức Truyền tải Thư tin Đơn giản hóa (SMTP) để gửi thư đi. Trong khi máy chủ thư xử lý cả email đến và đi, thì máy chủ SMTP chỉ quan tâm đến tác vụ gửi và chuyển tiếp email gửi đi đến các đích phù hợp. Nó cũng có thể được gọi là một máy chủ email gửi đi.
+ Ví dụ : Máy chủ SMTP cho Gmail là smtp.gmail.com. Khi định cấu hình máy khách email hoặc máy chủ của bạn để gửi email bằng Gmail, bạn thường sử dụng địa chỉ máy chủ SMTP này cùng với thông tin chứng thực tài khoản Gmail của mình.

## Cách hoạt động 
- Trong mô hình **Giao thức Truyền tải Thư tin Đơn giản hóa (SMTP)**, máy khách email hoặc máy chủ của người gửi hoạt động như máy khách SMTP và máy chủ email của người gửi hoạt động như máy chủ SMTP. Máy khách này khởi tạo kết nối đến máy chủ và truyền email, hoàn thành bằng các chi tiết người nhận, chủ đề và nội dung. Máy chủ xử lý email này và xác định máy chủ tiếp theo phù hợp dựa trên địa chỉ của người nhận. Máy chủ tiếp theo này có thể là một máy chủ SMTP khác trong tuyến đường truyền hoặc đích cuối cùng, tức là máy chủ email của người nhận. Khi tin nhắn đến máy chủ của người nhận, nó sẽ được gửi đến hộp thư đến của người nhận bằng một giao thức khác, ví dụ như POP hoặc IMAP.

### Cách các máy chủ SMTP gửi email 
Máy chủ SMTP gửi email bằng cách làm theo lần lượt các bước:
- Đầu tiên, máy khách email hoặc máy chủ của người gửi thiết lập kết nối với máy chủ SMTP của người nhận và cung cấp thông tin cần thiết, ví dụ như địa chỉ email của người nhận. 
- Sau đó, máy chủ SMTP xử lý thông tin này và xác minh địa chỉ của người nhận để quyết định có chấp nhận email hay không. 
+ Nếu địa chỉ của người nhận hợp lệ, email sẽ được xếp hàng để gửi. 
- Tiếp theo, máy chủ của người nhận sẽ cố gắng gửi email đến hộp thư đến của người nhận hoặc một thư mục được chỉ định.

## Thiết Lập Máy Chủ SMTP
- Thiết lập máy chủ SMTP yêu cầu cài đặt phần mềm máy chủ SMTP trên máy tính, máy chủ hoặc trong đám mây. Các bước cụ thể để thiết lập máy chủ SMTP phụ thuộc vào phần mềm mà bạn chọn. Nói chung, bạn cần định cấu hình cài đặt của máy chủ, ví dụ như địa chỉ máy chủ, số cổng, giao thức bảo mật và các tùy chọn xác thực. Bạn cũng có thể phải định cấu hình cài đặt DNS và quy tắc tường lửa để đảm bảo gửi email phù hợp.

### Thiết lập SMTP dựa trên đám mây
Thiết lập dịch vụ SMTP (Giao thức truyền thư đơn giản) dựa trên đám mây thường liên quan đến việc sử dụng nhà cung cấp dịch vụ email bên thứ ba. Sau đây là các bước chung để thiết lập dịch vụ SMTP dựa trên đám mây:
- **Bước 1:** Chọn nhà cung cấp dịch vụ email
Nghiên cứu và chọn nhà cung cấp dịch vụ email dựa trên đám mây có uy tín chuyên cung cấp dịch vụ SMTP. Một số tùy chọn phổ biến bao gồm Amazon SES (Simple Email Service), SendGrid, Mailgun và Sendinblue.
- **Bước 2:** Đăng ký tài khoản
Tạo tài khoản với nhà cung cấp dịch vụ email được chọn. Bạn có thể cần cung cấp thông tin liên hệ và thanh toán của mình, phụ thuộc vào yêu cầu của nhà cung cấp.
- **Bước 3:** Xác minh miền của bạn
Xác minh miền mà bạn sẽ sử dụng để gửi email. Bước này liên quan đến việc chứng minh quyền sở hữu hoặc ủy quyền miền cho nhà cung cấp dịch vụ email. Quá trình xác minh chính xác sẽ khác nhau giữa các nhà cung cấp nhưng thường liên quan đến việc thêm bản ghi DNS hoặc sửa đổi cài đặt DNS.
- **Bước 4:** Định cấu hình cài đặt SMTP
Truy cập cài đặt SMTP do nhà cung cấp dịch vụ email của bạn cung cấp. Các cài đặt này thường bao gồm địa chỉ máy chủ SMTP, số cổng, tùy chọn mã hóa (SSL/TLS) và thông tin chứng thực (tên người dùng và mật khẩu/khóa API).
- **Bước 5:**Thiết lập gửi email
Định cấu hình ứng dụng hoặc máy khách email của bạn để sử dụng dịch vụ SMTP dựa trên đám mây. Điều này liên quan đến việc cập nhật cài đặt máy chủ SMTP trong cấu hình email của ứng dụng. Bạn sẽ cần nhập địa chỉ máy chủ SMTP, số cổng và thông tin xác thực được cung cấp bởi nhà cung cấp dịch vụ email của bạn.
- **Bước 6:** Kiểm tra và gửi email
Kiểm tra cấu hình SMTP bằng cách gửi email thử nghiệm từ ứng dụng hoặc máy khách email của bạn. Xác minh rằng email được gửi và nhận thành công mà không gặp bất kỳ sự cố nào. Bạn cũng có thể thực hiện kiểm tra bổ sung, ví dụ như kiểm tra khả năng gửi email và theo dõi số liệu email, bằng cách sử dụng các tính năng được cung cấp bởi nhà cung cấp dịch vụ email của bạn.


> Lưu ý: Điều quan trọng là phải tham khảo tài liệu và tài nguyên hỗ trợ được cung cấp bởi nhà cung cấp dịch vụ email được chọn để biết các hướng dẫn cụ thể phù hợp với nền tảng của họ. Họ có thể cung cấp hướng dẫn từng bước và hỗ trợ khắc phục sự cố để đảm bảo thiết lập thành công dịch vụ SMTP dựa trên đám mây.

---

# HTTP - Hypertext Transfer Protocol
**Khái niệm:**  
**HTTP (Hypertext Transfer Protocol)** là giao thức truyền siêu văn bản, được phát triển bởi **Tim Berners-Lee** tại CERN vào năm 1989 để hỗ trợ truyền thông tin trong **World Wide Web**. Phiên bản đầu tiên (HTTP/0.9) được công bố năm 1991, chỉ hỗ trợ phương thức GET đơn giản. Các phiên bản sau được chuẩn hóa bởi IETF và W3C qua các RFC.

- **HTTP nằm ở tầng ứng dụng (Application Layer)** của mô hình **TCP/IP**, trên tầng vận chuyển (Transport Layer - thường là TCP) và tầng mạng (Network Layer - IP). Nó quy định cách trao đổi dữ liệu web, **không quan tâm trực tiếp đến các tầng dưới **(như router hoặc modem). HTTP **có thể sử dụng bất kỳ giao thức vận chuyển đáng tin cậy nào, nhưng thường dùng TCP (cổng 80 cho không mã hóa) hoặc TLS-encrypted TCP (cổng 443 cho HTTPS). HTTP/3 sử dụng QUIC/UDP để tối ưu hóa.**

## Các phiên bản chính
- **HTTP/0.9 (1991):** Phiên bản cơ bản, chỉ hỗ trợ GET để lấy tài nguyên HTML, không có header, kết nối luôn đóng sau phản hồi. Đã lỗi thời và bị loại bỏ.
- **HTTP/1.0 (RFC 1945, 1996):** Thêm header, phương thức HEAD và POST; sử dụng kết nối TCP riêng biệt cho mỗi yêu cầu.
- **HTTP/1.1 (RFC 2616 năm 1999, cập nhật RFC 7230-7235 năm 2014 và RFC 9112 năm 2022):** Giới thiệu kết nối persistent, pipelining (gửi nhiều yêu cầu mà không chờ phản hồi), chunked encoding, byte-range requests, và header Host bắt buộc cho virtual hosting. Đây là phiên bản tiêu chuẩn internet.
- **HTTP/2 (RFC 7540 năm 2015, cập nhật RFC 9113 năm 2022):** Dựa trên SPDY của Google, sử dụng binary framing để nén header, multiplexing (nhiều luồng trên một kết nối), server push. Yêu cầu TLS cho bảo mật.
- **HTTP/3 (RFC 9114 năm 2022):** Sử dụng QUIC trên UDP thay vì TCP để giảm độ trễ, tránh head-of-line blocking, và cải thiện xử lý tắc nghẽn. Sử dụng QPACK để nén header.

## Cách hoạt động 
HTTP hoạt động theo mô hình **client-server**:

- **Client:** Thường là trình duyệt web (user-agent như Firefox, Safari) hoặc công cụ khác, gửi yêu cầu để lấy tài nguyên (HTML, hình ảnh, script). Client khởi tạo kết nối và xử lý phản hồi để hiển thị trang web.

- **Server:** Máy chủ web (như Apache) nhận yêu cầu, xử lý và gửi phản hồi chứa dữ liệu tương ứng. Có thể là một máy hoặc nhóm máy (load balancing), chia sẻ IP qua header Host.

>Các trung gian như proxy có thể nằm giữa: transparent (chuyển tiếp không thay đổi) hoặc non-transparent (thay đổi yêu cầu cho cache, lọc, xác thực).

- **HTTP là giao thức không trạng thái (stateless):** Server không lưu trữ thông tin về các yêu cầu trước của client, mỗi yêu cầu độc lập. Điều này đơn giản hóa server nhưng phức tạp hóa ứng dụng cần trạng thái (như giỏ hàng). Để duy trì trạng thái, sử dụng cookie, biến ẩn trong form, hoặc session qua header. Không phải là không có session; cookie cho phép session stateful.

<img src="/images/base/http-1.png">

```
Client mở kết nối TCP đến server (cổng 80 hoặc 443)
                    ||
Server chấp nhận kết nối
                    ||
Client gửi bản tin HTTP request, server xử lý và gửi response
                    ||
Sau đó, kết nối có thể đóng hoặc tái sử dụng. 
```

>HTTP yêu cầu giao thức vận chuyển đáng tin cậy; không dùng UDP trừ HTTP/3 với QUIC.

### Non-Persistent vs Persistent
- **Non-Persistent HTTP (HTTP/1.0 mặc định):** Mỗi đối tượng (file) sử dụng một kết nối TCP riêng. Ưu: Đơn giản. Nhược: Tốn thời gian thiết lập TCP nhiều lần (2 RTT cho kết nối + 2 RTT cho file), trình duyệt thường mở nhiều kết nối song song để tải nhanh hơn.
- **Persistent HTTP (HTTP/1.1 trở lên):** Nhiều đối tượng tải qua một kết nối duy nhất. Client gửi yêu cầu ngay khi cần mà không chờ, server giữ kết nối mở sau phản hồi. Ưu: Giảm độ trễ, chỉ khoảng 2 RTT cho tất cả đối tượng. Có pipelining (gửi nhiều request liên tục) nhưng khó triển khai và ít dùng. Header Connection kiểm soát (ví dụ: Connection: keep-alive).

> HTTP/2 cải tiến bằng multiplexing (nhiều luồng trên một kết nối), HTTP/3 tránh tắc nghẽn TCP.

## Bản Tin HTTP
- Cú pháp bản tin request thường ở dạng text (HTTP/1.x), chia dòng dễ đọc 

- Cấu trúc: 
+ **Request Line:** Method SP Request-URI SP HTTP-Version CRLF (ví dụ: GET /index.html HTTP/1.1).
+ **Headers:** Các trường như Host: www.example.com, User-Agent: Mozilla/5.0, Accept-Language: en-US (một dòng mỗi header, kết thúc bằng dòng trống).
+ **Entity Body:** Tùy chọn, cho dữ liệu như form trong POST.

ví dụ :
```
GET / HTTP/1.1
Host: developer.mozilla.org
Accept-Language: fr
```

## Phương Thức (Methods)
Phương thức định nghĩa hành động, case-sensitive. Server phải hỗ trợ GET và HEAD; các khác tùy chọn. An toàn (safe: không thay đổi server), idempotent (lặp lại không thay đổi kết quả), cacheable.

| Phương thức | Mô tả | Body? | Safe? | Idempotent? | Cacheable? | Phiên bản |
|-------------|-------|-------|-------|-------------|------------|-----------|
| GET | Lấy tài nguyên (bookmarkable, ưu tiên cho đọc). | Optional | Yes | Yes | Yes | 0.9+ |
| HEAD | Như GET nhưng chỉ header (lấy metadata như kích thước). | Optional | Yes | Yes | Yes | 1.0+ |
| POST | Gửi dữ liệu (form, upload), có thể thay đổi server. | Yes | No | No | Yes | 1.0+ |
| PUT | Tạo/thay thế tài nguyên tại URI. | Yes | No | Yes | No | 1.1+ |
| DELETE | Xóa tài nguyên tại URI. | Optional | No | Yes | No | 1.1+ |
| OPTIONS | Lấy phương thức hỗ trợ cho tài nguyên. | Optional | Yes | Yes | No | 1.1+ |
| CONNECT | Thiết lập tunnel (cho proxy). | Optional | No | No | No | 1.1+ |
| TRACE | Echo request cho debug. | No | Yes | Yes | No | 1.1+ |
| PATCH | Sửa đổi một phần tài nguyên (tiết kiệm băng thông). | Yes | No | No | No | RFC 5789 |


## Response

Bản tin response tương tự:
- Status Line: HTTP-Version SP Status-Code SP Reason-Phrase CRLF (ví dụ: HTTP/1.1 200 OK).
- Headers: Như Date, Server, Content-Type, Last-Modified.
- Entity Body: Tài nguyên yêu cầu (HTML, dữ liệu).

Ví dụ response:
```
HTTP/1.1 200 OK
Date: Sat, 09 Oct 2010 14:28:02 GMT
Server: Apache
Content-Type: text/html

<!doctype html>… (nội dung)
```

## Mã Trạng Thái (Status Codes)
3 chữ số, phân loại theo chữ số đầu; reason phrase mô tả ngắn.

**1xx Informational:** Tiếp tục xử lý (ví dụ: 100 Continue).
**2xx Success:** Thành công (200 OK: yêu cầu thành công với body; 204 No Content: không body).
**3xx Redirection:** Cần hành động thêm (301 Moved Permanently: di chuyển vĩnh viễn; 302 Found: tạm thời).
**4xx Client Error:** Lỗi client (400 Bad Request: cú pháp sai; 403 Forbidden: cấm truy cập; 404 Not Found: không tìm thấy).
**5xx Server Error:** Lỗi server (500 Internal Server Error: lỗi chung; 503 Service Unavailable: quá tải tạm thời).

> HTTPS là phiên bản bảo mật của HTTP, sử dụng TLS (port 443) để mã hóa, chống nghe lén và giả mạo. Hơn 85% website sử dụng HTTPS. HTTP/2 và HTTP/3 thường yêu cầu TLS. Xác thực: Basic (username/password base64), Digest (hashed). Header như Do-Not-Track cho quyền riêng tư. Stateless giúp tránh hijacking, nhưng cookie cần HTTPS để an toàn.



---

# SNMP - Simple Network Management Protocol
**Khái niệm:**  
- SNMP, viết tắt của Simple Network Management Protocol, là một giao thức chuẩn được sử dụng rộng rãi trong quản lý mạng dựa trên IP.

+ Nó cho phép các quản trị viên thu thập dữ liệu về hiệu suất, tình trạng và cấu hình của các thiết bị như router, switch, máy chủ, máy in hoặc thậm chí các thiết bị IoT, giúp phát hiện sớm các vấn đề như tắc nghẽn mạng hoặc lỗi phần cứng.

+ SNMP hoạt động chủ yếu ở tầng ứng dụng của mô hình TCP/IP, tập trung vào việc trao đổi thông tin quản lý mà không làm gián đoạn hoạt động chính của thiết bị, từ đó hỗ trợ giám sát thời gian thực và tự động hóa các nhiệm vụ bảo trì.

> Dùng để **giám sát và quản lý thiết bị mạng** (router, switch, server) qua port 161/162 (UDP).

## Các Phiên bản Chính
- **SNMPv1**

Đây là phiên bản cơ bản nhất, hỗ trợ các chức năng đọc và ghi dữ liệu quản lý đơn giản, chẳng hạn như lấy giá trị biến hoặc thay đổi cài đặt từ xa.
Xác thực dựa trên community string (một chuỗi mật khẩu đơn giản), nhưng toàn bộ dữ liệu được truyền dưới dạng văn bản thuần, dẫn đến rủi ro bị chặn bắt và giả mạo thông tin.

- **SNMPv2c**

Cải tiến từ v1 bằng cách thêm hỗ trợ cho các thông báo lớn hơn (trap) và lệnh get-bulk, cho phép lấy một lượng lớn dữ liệu chỉ trong một yêu cầu, rất hữu ích cho mạng lớn để giảm tải.
Vẫn giữ cơ chế xác thực community string mà không mã hóa, nên dễ bị khai thác trong môi trường không an toàn, nhưng tăng hiệu quả xử lý dữ liệu so với phiên bản trước.

- **SNMPv3**

Tập trung vào bảo mật cao cấp, với mô hình USM (User-based Security Model) cho phép xác thực người dùng qua các thuật toán như MD5 hoặc SHA, đồng thời mã hóa dữ liệu bằng DES hoặc AES để bảo vệ khỏi nghe lén.
Thêm kiểm soát truy cập chi tiết dựa trên người dùng và ngữ cảnh, giúp phân quyền cụ thể cho từng loại dữ liệu, làm cho nó phù hợp với các mạng doanh nghiệp yêu cầu tuân thủ tiêu chuẩn an ninh.
## Cách hoạt động
- SNMP sử dụng mô hình manager-agent: Manager là phần mềm trung tâm (như NMS - Network Management System) gửi yêu cầu đến agent cài đặt trên thiết bị để thu thập dữ liệu.
- Các lệnh cơ bản bao gồm Get (lấy giá trị cụ thể từ biến), Set (thay đổi cấu hình như bật/tắt cổng), và Trap (agent tự động gửi thông báo về sự kiện bất thường như mất kết nối hoặc quá tải CPU).
- Giao thức chạy trên UDP (cổng 161 cho yêu cầu manager-agent, cổng 162 cho trap), giúp truyền nhanh và tiết kiệm tài nguyên, nhưng có thể mất gói tin nên thường kết hợp với cơ chế retry.
- Dữ liệu được tổ chức trong MIB (Management Information Base), một cấu trúc cây hierarchical với các OID (Object Identifier) độc đáo cho từng biến, ví dụ như sysUpTime để theo dõi thời gian hoạt động của thiết bị.

### Đặc điểm Nổi bật
**Ưu điểm:** Thiết kế đơn giản giúp dễ tích hợp với hầu hết thiết bị mạng, hỗ trợ giám sát quy mô lớn mà không cần tài nguyên cao, và cho phép tùy chỉnh qua các MIB mở rộng từ nhà sản xuất.
**Nhược điểm:** Các phiên bản cũ dễ bị tấn công do thiếu mã hóa, dẫn đến rủi ro lộ thông tin nhạy cảm; cần cấu hình firewall cẩn thận để hạn chế truy cập không mong muốn và thường kết hợp với VPN cho môi trường công khai.
---
# Telnet 
**Khái niệm:**  
Telnet là giao thức mạng cổ điển dùng để cung cấp truy cập từ xa qua giao diện terminal ảo, cho phép người dùng kết nối và quản lý thiết bị như thể đang sử dụng trực tiếp.

- Nó hỗ trợ thực thi lệnh trên server từ xa, thường áp dụng cho các thiết bị mạng cũ như router hoặc hệ thống legacy nơi không cần bảo mật cao.
- Telnet hoạt động ở tầng ứng dụng, dựa trên TCP để duy trì kết nối ổn định, nhưng thiếu các biện pháp bảo vệ hiện đại.
>Giao thức điều khiển từ xa qua text (port 23).

## Cách Hoạt động
- Client kết nối đến server trên cổng 23, thiết lập phiên TCP và bắt đầu trao đổi dữ liệu dưới dạng văn bản thuần mà không mã hóa, bao gồm cả lệnh và phản hồi.
- Sử dụng NVT (Network Virtual Terminal) để chuẩn hóa định dạng dữ liệu giữa các hệ thống khác nhau, ví dụ như xử lý ký tự đặc biệt hoặc điều khiển dòng lệnh.
- Xác thực đơn giản chỉ dựa trên username và password được truyền rõ ràng, không có cơ chế kiểm tra toàn vẹn, dẫn đến dễ bị chặn bắt toàn bộ phiên làm việc.
- Kết nối có thể được duy trì lâu dài cho các lệnh liên tục, nhưng không hỗ trợ các tính năng nâng cao như tunneling hoặc chuyển file bảo mật.

## Đặc điểm Nổi bật
**Ưu điểm:** Thiết kế đơn giản giúp dễ triển khai và sử dụng trên các hệ thống cũ, không yêu cầu tài nguyên cao và tương thích rộng rãi với phần cứng legacy.

**Nhược điểm:** Hoàn toàn thiếu bảo mật do truyền plain text, dễ bị tấn công sniffing để lấy mật khẩu hoặc dữ liệu; không phù hợp với mạng công khai và thường bị thay thế bởi SSH trong môi trường hiện đại.

> **Bị thay thế hoàn toàn bởi SSH** vì lý do bảo mật.

---

# TCP - Transmission Control Protocol
**Khái niệm:**  
TCP, viết tắt của Transmission Control Protocol, là một giao thức tầng vận chuyển (transport layer) trong mô hình TCP/IP, được thiết kế để cung cấp kết nối đáng tin cậy và có thứ tự giữa các ứng dụng trên mạng.

- Nó đảm bảo rằng dữ liệu được truyền một cách chính xác, không bị mất mát hoặc lặp lại, bằng cách xử lý lỗi, kiểm soát dòng chảy và quản lý tắc nghẽn, rất phù hợp cho các ứng dụng yêu cầu độ tin cậy cao như email, web browsing hoặc chuyển file.
- TCP hoạt động trên nền IP, biến mạng không đáng tin cậy thành một kênh truyền ổn định, giúp các thiết bị trao đổi dữ liệu dưới dạng luồng byte liên tục mà không cần lo lắng về các vấn đề cơ bản của mạng.

## Cách Hoạt động
- TCP bắt đầu bằng quá trình thiết lập kết nối qua 3-way handshake: Client gửi SYN, server trả SYN-ACK, client xác nhận ACK, đảm bảo cả hai bên đồng bộ sequence numbers để theo dõi dữ liệu.
- Trong quá trình truyền, dữ liệu được chia thành segments với header chứa sequence number, acknowledgment number, và window size để kiểm soát dòng chảy (flow control), tránh overwhelm receiver.
- Nếu gói tin mất, TCP sử dụng retransmission dựa trên timeout hoặc duplicate ACK, đồng thời điều chỉnh tốc độ qua congestion control algorithms như slow start và congestion avoidance để tránh tắc nghẽn mạng.
- Kết thúc kết nối bằng 4-way handshake: Một bên gửi FIN, bên kia ACK và FIN, rồi ACK cuối cùng, đảm bảo tất cả dữ liệu được nhận trước khi đóng.
## Đặc điểm Nổi bật
- **Ưu điểm:** Đảm bảo độ tin cậy cao với error detection qua checksum, ordered delivery để dữ liệu đến đúng thứ tự, và full-duplex cho truyền hai chiều đồng thời, làm cho nó lý tưởng cho các ứng dụng không chấp nhận mất mát.
- **Nhược điểm:** Overhead cao do handshake và ACK làm tăng độ trễ, không phù hợp với ứng dụng thời gian thực như video call; cần tài nguyên CPU để quản lý trạng thái kết nối, và dễ bị ảnh hưởng bởi mất gói tin trong mạng không ổn định.

---

# UDP - User Datagram Protocol
**Khái niệm:**  
UDP, viết tắt của User Datagram Protocol, là giao thức tầng vận chuyển đơn giản, không kết nối, tập trung vào việc truyền dữ liệu nhanh chóng mà không đảm bảo độ tin cậy.

- Nó được sử dụng cho các ứng dụng cần tốc độ cao và chấp nhận mất mát nhỏ, như streaming video, gaming online, DNS queries hoặc VoIP, nơi độ trễ thấp quan trọng hơn việc retransmit dữ liệu mất.
- UDP hoạt động trên IP, gửi datagrams độc lập mà không thiết lập kết nối, giúp giảm overhead và phù hợp với multicast hoặc broadcast để phân phối dữ liệu đến nhiều receiver.

## Cách hoạt động 
- UDP gửi dữ liệu dưới dạng datagrams độc lập: Sender thêm header với port để multiplex các ứng dụng, length để xác định kích thước, và checksum tùy chọn để phát hiện lỗi cơ bản.
- Không có handshake hay acknowledgment: Dữ liệu được gửi ngay lập tức mà không chờ xác nhận, dẫn đến có thể mất, duplicate hoặc out-of-order delivery tùy thuộc vào mạng.
- Receiver kiểm tra checksum để loại bỏ datagrams hỏng, nhưng không retransmit; ứng dụng tầng trên phải xử lý lỗi nếu cần, ví dụ qua cơ chế riêng như FEC (Forward Error Correction).
- Hỗ trợ multicast bằng cách gửi đến địa chỉ nhóm, giúp hiệu quả cho phân phối dữ liệu rộng rãi mà không cần nhiều kết nối riêng lẻ.

## Đặc điểm nổi bật
- **Ưu điểm:** Overhead thấp với header chỉ 8 bytes, tốc độ cao do không quản lý trạng thái, và linh hoạt cho ứng dụng thời gian thực nơi retransmission có thể làm tệ hơn độ trễ.
- **Nhược điểm:** Không đảm bảo delivery hoặc thứ tự, dễ mất dữ liệu trong mạng kém; ứng dụng phải tự implement reliability nếu cần, và checksum yếu có thể bỏ sót lỗi phức tạp.

## So sánh TCP và UDP

-**Độ tin cậy:** TCP đảm bảo delivery qua ACK và retransmission; UDP không, dẫn đến mất mát có thể xảy ra.
-**Kết nối:** TCP connection-oriented với handshake; UDP connectionless, gửi ngay lập tức.
-**Ứng dụng:** TCP cho dữ liệu quan trọng như HTTP/FTP; UDP cho tốc độ cao như DNS/Streaming.
-**Overhead và Hiệu suất:** TCP có header lớn hơn (20+ bytes) và overhead cao; UDP nhẹ (8 bytes) nhưng yêu cầu ứng dụng xử lý lỗi.
---

# ICMP - Internet Control Message Protocol
**Khái niệm:**  
ICMP, viết tắt của Internet Control Message Protocol, là giao thức tầng mạng (network layer) dùng để báo cáo lỗi và cung cấp thông tin vận hành trong mạng IP.

- Nó giúp chẩn đoán vấn đề mạng như kết nối không đạt, tắc nghẽn hoặc route không tồn tại, thường được sử dụng bởi công cụ như ping để kiểm tra reachability và traceroute để theo dõi đường đi.
- ICMP không truyền dữ liệu người dùng mà chỉ hỗ trợ quản lý mạng, cho phép các thiết bị như router gửi thông báo về vấn đề mà không làm gián đoạn luồng dữ liệu chính.
>Giao thức kiểm tra và báo lỗi mạng (Layer 3).

## Cách hoạt động 
- ICMP gửi messages encapsulated trong IP packets, với header chứa type (ví dụ: 0 cho echo reply, 3 cho destination unreachable), code (chi tiết lỗi), và checksum để xác thực.
- Khi lỗi xảy ra, router hoặc host tạo message ICMP và gửi về nguồn, ví dụ: Nếu gói tin hết TTL, gửi time exceeded; nếu port không mở, gửi port unreachable.
- Công cụ như ping gửi echo request và đo thời gian cho echo reply, trong khi traceroute tăng dần TTL để thu thập route từ các time exceeded messages.
- Không sử dụng port như TCP/UDP mà dựa vào IP header, và có thể bị lọc bởi firewall để tránh lạm dụng như DDoS.

## Đặc điểm Nổi bật
- **Ưu điểm:** Thiết kế nhẹ giúp chẩn đoán nhanh mà không cần kết nối đầy đủ, hỗ trợ tự động hóa quản lý mạng và phát hiện vấn đề sớm để tối ưu hiệu suất.
- **Nhược điểm:** Dễ bị khai thác cho tấn công như ping flood hoặc smurf attack; một số message có thể bị bỏ qua bởi thiết bị, và không mã hóa dẫn đến rủi ro giả mạo.

---

# BGP - Border Gateway Protocol
**Khái niệm:**  
BGP, viết tắt của Border Gateway Protocol, là giao thức định tuyến ngoại vi (exterior gateway protocol) dùng để trao đổi thông tin route giữa các autonomous systems (AS) trên Internet.

- Nó đảm bảo dữ liệu được định tuyến hiệu quả qua các mạng độc lập, chọn đường đi tốt nhất dựa trên policy thay vì metrics đơn giản, rất quan trọng cho scalability của Internet toàn cầu.
- BGP hoạt động ở tầng ứng dụng nhưng dựa trên TCP, giúp kết nối các ISP, data center và mạng lớn để duy trì bảng route động.
> Giao thức định tuyến **liên miền (Exterior Gateway Protocol)** dùng trên Internet.

## Cách hoạt động
- BGP thiết lập kết nối với neighbors (peers) qua TCP port 179, sử dụng finite state machine để quản lý trạng thái từ idle đến established.
- Router trao đổi route qua update messages chứa prefix, attributes như NEXT_HOP, ORIGIN và LOCAL_PREF, với path vector mechanism để theo dõi AS path và tránh loop.
- Quyết định route dựa trên policy: Ưu tiên highest LOCAL_PREF, shortest AS_PATH, lowest MED, v.v., và quảng bá route tốt nhất đến peers.
- Có hai loại: eBGP (external, giữa AS khác) với TTL=1 để hạn chế, và iBGP (internal, trong AS) yêu cầu full mesh hoặc route reflector để lan tỏa route.

## Đặc điểm Nổi bật
- **Ưu điểm:** Linh hoạt với policy-based routing cho tùy chỉnh theo nhu cầu kinh doanh, scalable cho hàng triệu route trên Internet, và hỗ trợ convergence nhanh qua BFD (Bidirectional Forwarding Detection).
- **Nhược điểm:** Phức tạp để cấu hình, dễ bị route leak hoặc hijacking nếu không bảo mật; convergence chậm trong trường hợp lớn, và yêu cầu tài nguyên cao cho bảng route đầy đủ.

---