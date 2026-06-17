# Network

Folder này chứa kiến thức nền tảng và vận hành mạng: OSI/TCP-IP, Ethernet, switching, addressing, routing, subnetting, network protocol, firewall, DNS, troubleshooting tools và các network service phổ biến.

## Canonical Learning Path

1. [Network Overview, Types And Architecture](./01-foundations/01-network-overview-types-and-architecture.md)
2. [OSI, TCP/IP And Encapsulation](./01-foundations/02-osi-tcpip-and-encapsulation.md)
3. [Addressing, Ports And Sockets](./01-foundations/03-addressing-ports-and-sockets.md)
4. [Ethernet, Media, Topologies And Layer 2](./02-ethernet-switching/01-ethernet-media-topologies-and-layer2.md)
5. [VLAN, LACP And Layer 2 Operations](./02-ethernet-switching/02-vlan-lacp-and-layer2-operations.md)
6. [IPv4 Addressing And Subnetting](./03-ip-routing-subnetting/01-ipv4-addressing-and-subnetting.md)
7. [Routing, NAT And Virtual Router](./03-ip-routing-subnetting/02-routing-nat-and-virtual-router.md)
8. [Common Network Protocols And Ports](./04-protocols-and-services/01-common-network-protocols-and-ports.md)
9. [DNS, DHCP And Core Network Protocols](./04-protocols-and-services/02-dns-dhcp-and-core-protocols.md)
10. [Proxy, Load Balancer, VPN And Expose Endpoints](./04-protocols-and-services/03-proxy-load-balancer-vpn-and-expose-endpoints.md)
11. [Firewall And Edge Security](./04-protocols-and-services/04-firewall-and-edge-security.md)
12. [NTP And Time Synchronization](./04-protocols-and-services/05-ntp-time-synchronization.md)
13. [HTTP Và Web Application Operations](./04-protocols-and-services/06-http-web-application-operations.md)
14. [Network Operations Lifecycle](./07-network-operations-lifecycle/overview.md)

## Operations And Troubleshooting

- [Network Troubleshooting Tools](./07-network-operations-lifecycle/03-network-troubleshooting-tools.md)
- [Network System Construction And Operations](./07-network-operations-lifecycle/01-network-system-construction-and-operations.md)
- [Enterprise Campus Network Design Case Study](./07-network-operations-lifecycle/02-enterprise-campus-network-design-case-study.md)

## Ghi Chú Tổ Chức

- `01-foundations/`, `02-ethernet-switching/`, `03-ip-routing-subnetting/`, `04-protocols-and-services/`, `06-ccna-advanced-networking-and-security/` và `07-network-operations-lifecycle/` là luồng canonical chính.
- Các note legacy ở root, `fundamental/`, `Tools & Troubleshooting/` và `Network Services/` đã được hấp thụ vào các note canonical tương ứng.
- Khi bổ sung note mới, ưu tiên merge vào luồng canonical nếu nội dung là kiến thức nền hoặc vận hành có thể tái sử dụng.

## Troubleshooting Mindset

Khi gặp lỗi kết nối, tách rõ từng lớp:

1. Link/interface.
2. VLAN và L2 path.
3. IP/subnet/route.
4. DNS.
5. Firewall/security policy.
6. Service port và application log.
