# Wireless LAN Fundamentals, Architectures, Security And WLC

## Overview

Wireless LAN khác wired LAN vì medium là không khí: shared, nhiễu, bị ảnh hưởng bởi khoảng cách/vật cản và dễ bị nghe lén hơn. Vì vậy wireless cần hiểu RF, 802.11 frame, AP architecture, authentication/encryption và WLC.

## RF Fundamentals

Các khái niệm cần nắm:

- Frequency: tần số sóng, thường gặp 2.4 GHz, 5 GHz, 6 GHz.
- Amplitude: biên độ tín hiệu.
- Channel: lát tần số dùng cho truyền thông.
- Interference: nhiễu từ thiết bị khác hoặc channel overlap.
- Attenuation: suy hao tín hiệu theo khoảng cách/vật cản.
- Reflection/refraction/absorption/scattering: hành vi sóng khi gặp môi trường.

2.4 GHz đi xa hơn nhưng ít channel không overlap và dễ nhiễu. 5 GHz/6 GHz có nhiều channel hơn, thường sạch hơn, nhưng vùng phủ có thể ngắn hơn.

## 802.11 Building Blocks

Các mô hình:

- IBSS: peer-to-peer/ad hoc, không có AP.
- BSS: một AP và client của AP đó.
- ESS: nhiều BSS cùng SSID tạo trải nghiệm roaming.
- DS: distribution system, thường là wired LAN phía sau AP.

Client không gửi data trực tiếp cho client khác trong BSS infrastructure; nó gửi qua AP.

## AP Architectures

Autonomous AP tự xử lý hầu hết control/data function. Lightweight AP phụ thuộc WLC cho phần quản lý/control, phù hợp triển khai lớn.

![WLC architecture original page](./images/ccna-vol2-page-0296.jpg)

Các mô hình WLC:

- unified WLC: appliance/controller riêng;
- cloud WLC: controller chạy trong private/public cloud;
- embedded WLC: tích hợp trong switch hoặc AP tùy dòng thiết bị;
- Mobility Express/embedded AP controller: AP đóng vai trò controller cho nhóm nhỏ.

## Wireless Security

Wireless cần bảo vệ confidentiality, integrity và availability. Vì tín hiệu lan qua không khí, encryption và authentication quan trọng hơn wired access thông thường.

Các thế hệ/cơ chế:

- WEP: cũ, không an toàn.
- WPA/WPA2-Personal: dùng PSK.
- WPA3-Personal: dùng SAE, cải thiện bảo vệ trước offline dictionary attack.
- WPA-Enterprise: dùng 802.1X/EAP/RADIUS, phù hợp doanh nghiệp.
- TKIP: cũ, nên tránh.
- CCMP/AES và GCMP: encryption/integrity hiện đại hơn.

![WPA3 SAE original page](./images/ccna-vol2-page-0309.jpg)

## WLC Configuration Mental Model

WLC tách physical port và logical interface:

- physical port nối WLC vào switch;
- management interface dùng quản trị và giao tiếp control;
- dynamic interface thường map với VLAN/subnet cho WLAN client;
- WLAN/SSID map vào security policy, QoS profile và interface.

Khi cấu hình WLAN:

1. Chuẩn bị VLAN/subnet/DHCP/NTP/DNS.
2. Trunk từ switch đến WLC nếu nhiều VLAN.
3. Tạo dynamic interface cho VLAN client.
4. Tạo WLAN/SSID.
5. Chọn security mode: PSK/SAE hoặc 802.1X.
6. Chọn QoS profile.
7. Enable WLAN và kiểm tra AP join.

## Wireless Troubleshooting Checklist

- Client có thấy SSID không?
- AP có join WLC không?
- DHCP cho wireless VLAN có hoạt động không?
- Client fail ở association, authentication hay IP assignment?
- PSK/SAE/802.1X/RADIUS lỗi ở bước nào?
- Channel plan có overlap hoặc nhiễu mạnh không?
- RSSI/SNR có đủ không?
- WLAN có map đúng dynamic interface/VLAN không?
- ACL/captive portal/Layer 3 security có chặn sau khi client đã lấy IP không?
