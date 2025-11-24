# Overview 
- OSI (Open Systems Interconnection) Model là mô hình khái niệm chia việc truyền thông mạng thành 7 lớp từ vật lý đến ứng dụng. Mục tiêu: tách bạch chức năng, chuẩn hóa giao tiếp giữa thiết bị/phần mềm khác nhau.

<img src="/networking/images/7-layer-osi-model.png">

Các lớp (từ dưới lên trên):
1. Physical (Vật lý) — bit, tín hiệu
2. Data Link (Liên kết dữ liệu) — frame, MAC address
3. Network (Mạng) — packet, IP address, routing
4. Transport (Vận chuyển) — segment, TCP/UDP, ports
5. Session (Phiên) — thiết lập/đóng phiên
6. Presentation (Trình bày) — mã hóa, nén, format
7. Application (Ứng dụng) — HTTP, FTP, SSH...

**Mỗi lớp cung cấp dịch vụ cho lớp trên và dùng dịch vụ của lớp dưới. Khi dữ liệu đi từ nguồn đến đích, nó được đóng gói (encapsulated) từng lớp một; khi đến đích dữ liệu được giải đóng gói (decapsulated).**

## Encapsulation

- Là quá trình bọc dữ liệu của một lớp vào phần payload của lớp bên dưới.
+ Ví dụ: Dữ liệu ứng dụng → được đóng gói thành segment (layer4) → được đóng gói trong packet (layer3) → được đóng gói trong frame (layer2) → chuyển thành tín hiệu (layer1).

- Demultiplexing / Decapsulation là quá trình ngược lại ở máy đích — tách header/tail ở mỗi lớp và chuyển payload lên lớp trên.

- Tại mọi điểm trung gian (ví dụ: router), chỉ frame (layer2) bị thay đổi; packet (layer3) thường giữ nguyên (trừ NAT hoặc các xử lý đặc biệt).

# 3. Layer 1 — Physical 
- Vai trò chính :Định nghĩa cách truyền các bit thô (0/1) trên môi trường vật lý.

- Bao gồm: phương tiện truyền (copper, fiber, radio/Wi-Fi), điện áp/biểu diễn tín hiệu, tốc độ (data rate), khoảng cách, kết nối vật lý (connector), phương pháp điều biến.

- Ví dụ : Ở môi trường vật lý (examples)


+ Copper → truyền bằng điện áp (ví dụ: +1V = 1, -1V = 0 trong ví dụ minh họa).

+ Fiber → truyền bằng ánh sáng.

+ Wi-Fi → truyền bằng sóng vô tuyến (radio frequency).

- Thuộc tính được chuẩn hóa (physical specs)
Voltage levels, timing, bit rate, max distance, modulation method, connector type (RJ45, SFP,...).

- Thiết bị layer1

+ NIC (Network Interface Card): chuyển đổi giữa bit ↔ tín hiệu vật lý.

+ Hub (multiport repeater): lặp lại mọi tín hiệu lên tất cả cổng — không hiểu frame hay địa chỉ.

- Hành vi quan trọng

+ Shared medium: khi dùng hub hoặc bus, mọi gói dữ liệu là broadcast đến tất cả thiết bị kết nối.
+ Không có địa chỉ thiết bị: Layer 1 không có khái niệm địa chỉ (điều này được giải quyết ở Layer 2).
+ Collision (va chạm): nếu nhiều thiết bị phát cùng lúc trên cùng medium → tín hiệu giao thoa → dữ liệu bị hỏng.
+ Không có Media Access Control (MAC): layer1 không ra quyết định ai được truyền; nếu muốn kiểm soát, phải nhờ layer2 (ví dụ CSMA/CD).

- Hệ quả
Mạng layer1 có một broadcast domain và một collision domain. Khi số thiết bị tăng, xác suất collision tăng — network khó mở rộng nếu chỉ layer1.

# Layer 2 — Data Link 
- Mục tiêu
+ Tạo giao tiếp thiết bị-đến-thiết bị trên cùng một mạng vật lý.
+ Thêm địa chỉ vật lý (MAC), kiểm soát truy cập lên môi trường vật lý, phát hiện/ xử lý collision (tùy công nghệ).
+ Đơn vị dữ liệu: frame.

## Khái niệm chính
- MAC Address: địa chỉ phần cứng (ví dụ xx:xx:xx:5b:76). Gán cho NIC.
- Frame: header (dst MAC, src MAC, type/length, ...), payload (dữ liệu), trailer (FCS/checksum).
- MAC table (Switch): ánh xạ MAC ↔ port; switch dùng để quyết định forward unicast frames.

## CSMA/CD (Carrier Sense Multiple Access / Collision Detection)

- Carrier Sense: trước khi transmit, device nghe xem có carrier (tín hiệu) trên medium không.
- Multiple Access: nhiều devices share cùng medium.
- Collision Detection: nếu detect collision khi phát, gửi jam signal và thực hiện backoff.
- Backoff algorithm: random wait; nếu collision tiếp tục, tăng thời gian backoff (binary exponential backoff — thời gian tăng theo cấp số nhân).

## Hubs vs Switches 

Hub (Layer1):

Chỉ lặp lại tín hiệu sang tất cả cổng.

Không có khái niệm frame hoặc MAC table.

Mọi port trong cùng một collision domain.

Switch (Layer2):

Hiểu được frame, đọc source MAC để học vào MAC table (port learning).

Khi có destination MAC đã biết → forward đến port đúng (unicast).

Nếu không biết → flood (broadcast) ra tất cả port ngoại trừ port nguồn.

Mỗi cổng là một collision domain riêng (giảm collision).

Store-and-forward: nhận frame, kiểm tra tính hợp lệ (FCS), sau đó forward; vì vậy switch thường không forward frame bị lỗi hoặc bị collision.

### Broadcast và Collision Domains
- Collision domain: nơi có thể xảy ra collision (hub: toàn bộ; switch: 1 per port).
- Broadcast domain: nơi broadcast frame (ví dụ ARP broadcast) tới tất cả host trong cùng mạng Layer2 — router phân chia broadcast domain (router không forward broadcast).

### Unicast, Broadcast
- Unicast: 1→1 using MAC dst.
- Broadcast: gửi đến ff:ff:ff:ff:ff:ff — mọi thiết bị trong same Layer2 network nhận.

- Ví dụ Luồng (Layer2 hoạt động)

1. Ứng dụng gửi dữ liệu → tầng 4 → (tầng 2 tạo frame).

2. Frame có dst MAC = MAC đích; nếu thiết bị biết MAC đích (qua ARP), frame gửi xuống layer1.

3. Nếu sử dụng hub → frame đến tất cả, mọi NIC sẽ kiểm tra dst MAC, chỉ host đúng mới chấp nhận.

4. Nếu sử dụng switch → switch đọc dst MAC; nếu trong MAC table → forward chỉ port tương ứng; nếu chưa biết → flood.

# Layer 3 — Network
- kết nối nhiều Layer2 networks với nhau. 
- Định tuyến (routing): chuyển packet từ source → destination qua nhiều mạng trung gian.
- Đơn vị dữ liệu: packet (IP packet).

## IP — cấu trúc packet
- IPv4: địa chỉ 32-bit, dạng dotted-decimal: 133.33.3.7.

+ Thực tế địa chỉ là 32 bit nhị phân (4 octet × 8 bit).

+ Mỗi octet: 0–255.

- IPv6: địa chỉ 128-bit — không đi sâu ở đây (script nói sẽ có video riêng).

- Trường quan trọng trong IP packet:

+ Source IP, Destination IP

+ Protocol: chỉ rõ tầng 4 (ví dụ TCP=6, UDP=17, ICMP=1)

+ TTL (Time To Live) (IPv4) / Hop Limit (IPv6): số hop tối đa packet có thể đi — tránh loop vô hạn.

+ Payload: dữ liệu của Layer4 (segment/UDP datagram).

- Packet: khi di chuyển qua internet, packet thường giữ nguyên; frame thay đổi mỗi hop.

## IP Addressing — Network part vs Host part — Subnet mask

>IP address = [network part] + [host part].

- Subnet mask xác định phần nào là network; ví dụ 255.255.0.0 tương đương /16 (16 bit 1).
- Máy tính dùng IP + Subnet mask để biết destination có cùng mạng hay không — từ đó biết có gửi trực tiếp hay gửi đến default gateway (router).

Ví dụ :

- IP: `133.33.3.7`

- Subnet mask: `255.255.0.0` → `/16 `→ network part là 133.33 (first 16 bits), host part là remaining.

- Quy trình tính start/end của network:

+ Start address = network bits (giữ nguyên) + host bits = all zeros → 133.33.0.0.

+ End address = network bits + host bits = all ones → 133.33.255.255.

Binary minh họa 
```makefile
IP: 133.33.3.7
  133 => 10000101
  33  => 00100001
  3   => 00000011
  7   => 00000111

Subnet 255.255.0.0 => /16 => binary: 11111111.11111111.00000000.00000000
Network = first 16 bits (133.33)
Start = 133.33.0.0
End   = 133.33.255.255


Kết luận: nếu hai địa chỉ có cùng network part → cùng one IP network (local) → gửi trực tiếp; nếu khác → gửi đến default gateway.
```

## Routing & Route Tables
Router = thiết bị Layer3; hiểu Layer1/2/3.

Route table: danh sách các route (destination prefix → next hop).

Ví dụ route entry: 52.217.13.0/24 -> next-hop 10.0.0.1

Lựa chọn route: nếu nhiều route match, chọn route có prefix dài nhất (most specific).

/32 = single IP (most specific); /0 = default route (matches all).

Default route: 0.0.0.0/0 — dùng khi không có route cụ thể hơn.

Quy trình forwarding:

Router nhận frame, strip frame → lấy packet.

Kiểm tra destination IP → tra route table → chọn next-hop.

Router encapsulate packet vào frame phù hợp với Layer2 network kế tiếp → gửi.

Ví dụ script (giải thích chi tiết)

Gửi packet đến 52.217.13.37.

Router MEOWISP có route table:

52.217.13.0/24 -> next-hop X

0.0.0.0/0 -> next-hop Y (default)

Cả 52.217.13.0/24 và 0.0.0.0/0 match, nhưng /24 more specific → chọn route /24.

## ARP (Address Resolution Protocol)
- **Mục đích:** tìm MAC address tương ứng với một IP địa chỉ trong cùng Layer2 network.

- Kịch bản local :

1. A muốn gửi packet đến B (IP dest = 133.33.3.10).

2. A so sánh IP của B với subnet mask để xác định B có local hay không → B là local.

3. A cần MAC của B để tạo frame.

4. A gửi ARP Request: broadcast frame với dst MAC ff:ff:ff:ff:ff:ff và ARP payload: "Who has IP 133.33.3.10? Tell 133.33.3.X".

5. B nhận ARP Request, thấy IP khớp → gửi ARP Reply (unicast) với MAC của B.

6. A nhận ARP Reply → lưu entry trong ARP cache (IP ↔ MAC).

7. A build frame: dst MAC = B's MAC, src MAC = A's MAC; payload = IP packet; gửi xuống layer1.

8. B nhận frame → layer2 kiểm tra dst MAC → đúng → strip frame → đưa packet lên layer3 → kiểm tra dst IP → đúng → deliver payload cho ứng dụng.

9. ARP cache: lưu tạm mapping; nếu hết hạn, ARP lại.

- ARP qua router:
Nếu destination remote → device ARP for default gateway's MAC (router in same L2 network) và gửi frame để tới router; router sẽ route tiếp.

## Packet life across networks
- Một packet có thể bị encapsulate/decapsulate nhiều lần (mỗi hop frame có thể khác).

- Packet thường không thay đổi (trừ NAT), nhưng frame thay đổi tùy công nghệ L2 (Ethernet, PPP, ATM,...).

Ví dụ: packet từ áo server → encapsulated in Ethernet frame → arrives at ISP router → router strips Ethernet frame, consult route table → re-encapsulate packet in frame for next link (PPP/MPLS/ethernet) → send to next hop → repeat.

# Layer 4 — Transport (TCP/UDP) & Layer 5 — Session

Mục tiêu :
- End-to-end communication giữa hai host (logical).

- Phân luồng ứng dụng dùng ports (cho phép nhiều ứng dụng trên same host).

- Đảm bảo thứ tự, tin cậy (TCP) hoặc rất nhanh/ít overhead (UDP).

- Segment là đơn vị dữ liệu.

## TCP — Transmission Control Protocol
- TCP thiết lập connection, trao đổi dữ liệu theo kênh 2 chiều rồi đóng connection.
- Tính năng:

+ Reliability (ACKs, retransmission)

+ Ordered delivery (sequence numbers)

+ Flow control (window)

+ Congestion control (algorithms beyond scope cơ bản nhưng đề cập)

- Cấu trúc header :

+ Source port, Destination port (xác định ứng dụng).

+ Sequence Number — số thứ tự byte/segment (dùng để ordering & retransmission).

+ Acknowledgement Number (ACK) — cho biết byte/số tiếp theo mà receiver mong đợi.

+ Flags (9 bits : e.g., SYN, ACK, FIN, RST, PSH, URG).

+ Data Offset (header length), reserved bits.

+ Window — số byte mà receiver sẵn sàng nhận trước khi gửi ACK → dùng cho flow control.

+ Checksum — kiểm tra lỗi của segment.

= Urgent Pointer — nếu set URG, con trỏ báo dữ liệu ưu tiên.


## UDP — User Datagram Protocol
Connectionless, minimal overhead, không đảm bảo ordering/reliability.

Dùng cho real-time apps (voice, video, DNS quick queries) nơi tốc độ > độ tin cậy.