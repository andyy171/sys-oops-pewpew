# Enterprise Campus Network Design Case Study

## Tá»•ng Quan

Enterprise campus network thÆ°á»ng Ä‘Æ°á»£c thiáº¿t káº¿ theo nhiá»u lá»›p Ä‘á»ƒ tÃ¡ch rÃµ Internet edge, security boundary, core, distribution, access, wireless, data center/server farm vÃ  remote connectivity. Má»¥c tiÃªu lÃ  vá»«a cÃ³ segmentation, vá»«a cÃ³ redundancy, vá»«a dá»… váº­n hÃ nh khi sá»± cá»‘ xáº£y ra.

Note nÃ y cháº¯t lá»c tá»« áº£nh `_inbox/enterprise-network-topo.jpg` thÃ nh mÃ´ hÃ¬nh tham kháº£o. KhÃ´ng dÃ¹ng IP trong áº£nh nhÆ° cáº¥u hÃ¬nh production tháº­t; khi lab hoáº·c triá»ƒn khai, thay báº±ng dáº£i Ä‘á»‹a chá»‰ phÃ¹ há»£p.

## Layer Map

| Layer | ThÃ nh pháº§n | Vai trÃ² |
|---|---|---|
| Internet edge | Dual ISP, edge routers, eBGP | Nháº­n káº¿t ná»‘i Internet tá»« nhiá»u ISP, inject default route vÃ o ná»™i bá»™. |
| Security layer | FortiGate HA active/passive | Firewall, IPS/IDS, URL filtering, SSL inspection, VPN vÃ  threat prevention. |
| Core layer | Core switches, OSPF area 0 | Backbone tá»‘c Ä‘á»™ cao, route giá»¯a distribution, firewall, data center vÃ  server farm. |
| Distribution layer | Distribution switches, HSRP, LACP | Gateway redundancy cho VLAN, policy aggregation vÃ  uplink redundancy. |
| Access layer | Access switches, EtherChannel/LACP | Káº¿t ná»‘i user/device vÃ o VLAN tÆ°Æ¡ng á»©ng. |
| Wireless | WLC, AP, SSID-to-VLAN mapping | TÃ¡ch SSID theo VLAN vÃ  policy: corp, voice, engineering, guest/IoT. |
| Services | AD, DNS, DHCP, NTP | Dá»‹ch vá»¥ ná»n báº¯t buá»™c cho domain, name resolution, cáº¥p IP vÃ  thá»i gian. |
| Remote/WAN | SSL VPN, site-to-site IPsec VPN | Remote user access vÃ  branch connectivity. |

## Traffic And Routing Model

Luá»“ng Internet outbound Ä‘iá»ƒn hÃ¬nh:

```text
client VLAN
-> access switch
-> distribution gateway
-> core
-> firewall HA
-> edge router
-> ISP / Internet
```

Luá»“ng server/internal service:

```text
client VLAN
-> distribution gateway
-> core
-> data center/server farm VLAN
-> service
```

Luá»“ng branch hoáº·c remote user:

```text
remote user / branch
-> SSL VPN hoáº·c IPsec VPN
-> firewall
-> core/distribution
-> internal VLAN/service
```

## Redundancy Patterns

| Pattern | DÃ¹ng á»Ÿ Ä‘Ã¢u | Ã nghÄ©a |
|---|---|---|
| Dual ISP + eBGP | Internet edge | Giáº£m phá»¥ thuá»™c vÃ o má»™t ISP vÃ  cho phÃ©p policy routing Internet. |
| Firewall HA | Security layer | Active/passive failover cho firewall state/session náº¿u thiáº¿t bá»‹ há»— trá»£ sync. |
| OSPF area 0 | Core | Dynamic routing ná»™i bá»™, giáº£m cáº¥u hÃ¬nh static route thá»§ cÃ´ng. |
| HSRP/VRRP gateway | Distribution | Default gateway redundancy cho VLAN ngÆ°á»i dÃ¹ng/server. |
| LACP EtherChannel | Access/distribution uplink | TÄƒng bÄƒng thÃ´ng logic vÃ  giáº£m rá»§i ro má»™t link Ä‘Æ¡n láº». |
| WLC + VLAN mapping | Wireless | Quáº£n lÃ½ SSID táº­p trung vÃ  gáº¯n traffic wireless vÃ o segmentation Ä‘Ãºng. |

## VLAN And Service Segmentation

Má»™t campus network nÃªn tÃ¡ch VLAN theo má»¥c Ä‘Ã­ch, má»©c tin cáº­y vÃ  policy:

| Segment | VÃ­ dá»¥ | Ghi chÃº |
|---|---|---|
| Admin | VLAN quáº£n trá»‹ | Háº¡n cháº¿ truy cáº­p, log Ä‘áº§y Ä‘á»§, MFA/VPN náº¿u remote. |
| Voice | IP phone/voice | Cáº§n QoS vÃ  tÃ¡ch khá»i data user thÃ´ng thÆ°á»ng. |
| Engineering/User | Workstation theo team | Ãp policy theo nhu cáº§u truy cáº­p service. |
| Guest/IoT | khÃ¡ch hoáº·c thiáº¿t bá»‹ Ã­t tin cáº­y | Cháº·n lateral movement, thÆ°á»ng chá»‰ cho Internet. |
| Data center/server | server ná»™i bá»™ | Kiá»ƒm soÃ¡t east-west traffic vÃ  backup/monitoring. |
| Server farm/DMZ | service expose hoáº·c shared | TÃ¡ch rÃµ khá»i user VLAN vÃ  management VLAN. |

## Design Checklist

- CÃ³ Ã­t nháº¥t hai Ä‘Æ°á»ng uplink quan trá»ng hoáº·c cÃ³ phÆ°Æ¡ng Ã¡n failover.
- Default gateway cho VLAN production cÃ³ redundancy.
- Firewall lÃ  security boundary rÃµ rÃ ng giá»¯a Internet, VPN vÃ  internal network.
- Routing protocol ná»™i bá»™ cÃ³ scope rÃµ, khÃ´ng leak route khÃ´ng cáº§n thiáº¿t.
- VLAN naming, subnet, gateway vÃ  DHCP scope nháº¥t quÃ¡n.
- Guest/IoT khÃ´ng Ä‘i tháº³ng vÃ o server/internal management network.
- DNS, DHCP, NTP, AD vÃ  logging/monitoring cÃ³ HA hoáº·c recovery plan.
- Wireless SSID map Ä‘Ãºng VLAN/policy.
- VPN remote user vÃ  site-to-site VPN cÃ³ route/policy riÃªng, khÃ´ng dÃ¹ng quyá»n quÃ¡ rá»™ng.

## Troubleshooting Entry Points

Khi campus network lá»—i, Ä‘á»«ng debug theo sÆ¡ Ä‘á»“ lá»›n ngay. Cáº¯t theo symptom:

| Symptom | Kiá»ƒm tra trÆ°á»›c |
|---|---|
| User máº¥t Internet | VLAN gateway, HSRP state, route default, firewall policy, ISP edge. |
| Má»™t VLAN khÃ´ng láº¥y Ä‘Æ°á»£c IP | DHCP scope, relay/helper, VLAN trunk, firewall giá»¯a VLAN vÃ  DHCP server. |
| Wi-Fi vÃ o Ä‘Æ°á»£c nhÆ°ng khÃ´ng tháº¥y internal service | SSID-to-VLAN mapping, ACL/firewall, DNS, route tá»›i server VLAN. |
| Branch VPN up nhÆ°ng app timeout | IPsec phase, route, policy, MTU/MSS, DNS vÃ  server port. |
| Server reachable báº±ng IP nhÆ°ng hostname lá»—i | DNS record, DNS server reachability, search domain vÃ  client resolver. |

## Trang LiÃªn Quan

- [Network Overview, Types And Architecture](../01-foundations/01-network-overview-types-and-architecture.md)
- [VLAN, LACP And Layer 2 Operations](../02-ethernet-switching/02-vlan-lacp-and-layer2-operations.md)
- [Routing, NAT And Virtual Router](../03-ip-routing-subnetting/02-routing-nat-and-virtual-router.md)
- [Common Network Protocols And Ports](../04-protocols-and-services/01-common-network-protocols-and-ports.md)
- [Proxy, Load Balancer, VPN And Expose Endpoints](../04-protocols-and-services/03-proxy-load-balancer-vpn-and-expose-endpoints.md)
