# Network System Construction And Operations

## Overview

Network system construction khÃ´ng chá»‰ lÃ  cáº¥u hÃ¬nh router/switch. NÃ³ lÃ  vÃ²ng Ä‘á»i tá»« kháº£o sÃ¡t nhu cáº§u, thiáº¿t káº¿ topology, cabling, láº¯p Ä‘áº·t thiáº¿t bá»‹, cáº¥u hÃ¬nh ná»n, nghiá»‡m thu, monitoring, váº­n hÃ nh Ä‘á»‹nh ká»³, change management vÃ  troubleshooting.

Note nÃ y giá»¯ pháº§n kiáº¿n thá»©c chung cÃ³ thá»ƒ Ã¡p dá»¥ng cho nhiá»u vendor. CÃ¡c vÃ­ dá»¥ CLI, tÃªn OS thiáº¿t bá»‹, tÃªn sáº£n pháº©m hoáº·c workflow khÃ³a vÃ o Huawei/eNSP/VRP Ä‘Æ°á»£c loáº¡i bá».

## Lifecycle

```text
Requirement -> Design -> Cabling -> Installation -> Baseline config
            -> Acceptance -> Monitoring -> Operation -> Optimization
            -> Incident/RCA -> Change improvement
```

## Requirement And Design

TrÆ°á»›c khi triá»ƒn khai, cáº§n lÃ m rÃµ:

- Sá»‘ site, sá»‘ user, sá»‘ server, loáº¡i workload vÃ  traffic chÃ­nh.
- PhÃ¢n tÃ¡ch máº¡ng: user, server, management, storage, guest, DMZ.
- YÃªu cáº§u availability: single uplink, dual uplink, dual aggregation, multi-site.
- YÃªu cáº§u security: firewall zone, ACL, AAA, logging, admin access.
- YÃªu cáº§u wireless: máº­t Ä‘á»™ client, roaming, coverage, guest network.
- YÃªu cáº§u operations: monitoring, backup config, change window, rollback.

Thiáº¿t káº¿ tá»‘t pháº£i chá»‰ ra cáº£ physical topology vÃ  logical topology. Physical topology tráº£ lá»i "dÃ¢y ná»‘i tháº¿ nÃ o"; logical topology tráº£ lá»i "VLAN, subnet, route, policy vÃ  failure domain náº±m á»Ÿ Ä‘Ã¢u".

## Cabling And Physical Layer

Cabling lÃ  ná»n cá»§a váº­n hÃ nh network. Nhiá»u sá»± cá»‘ khÃ³ chá»‹u báº¯t Ä‘áº§u tá»« lá»—i ráº¥t tháº¥p táº§ng: dÃ¢y sai chuáº©n, module khÃ´ng tÆ°Æ¡ng thÃ­ch, patch panel dÃ¡n nhÃ£n kÃ©m, fiber báº©n hoáº·c uplink khÃ´ng Ä‘Ãºng speed.

Checklist tá»‘i thiá»ƒu:

- Chuáº©n hÃ³a label cho rack, patch panel, switch port, uplink vÃ  endpoint.
- TÃ¡ch rÃµ copper, fiber single-mode, fiber multi-mode, transceiver vÃ  connector.
- Kiá»ƒm tra cable length, bend radius, EMI, PoE budget vÃ  airflow trong rack.
- Ghi láº¡i as-built diagram sau nghiá»‡m thu, khÃ´ng chá»‰ giá»¯ báº£n thiáº¿t káº¿ ban Ä‘áº§u.
- LÆ°u káº¿t quáº£ test cable/fiber náº¿u mÃ´i trÆ°á»ng yÃªu cáº§u audit.

## Hardware Installation

Khi láº¯p router, switch, firewall, AP hoáº·c network appliance:

- Kiá»ƒm tra nguá»“n, grounding, rack space, airflow vÃ  nhiá»‡t Ä‘á»™.
- Kiá»ƒm tra serial number, asset tag, firmware baseline vÃ  support status.
- KhÃ´ng cáº¯m uplink production trÆ°á»›c khi Ä‘Ã£ biáº¿t port mode, VLAN vÃ  STP/LACP behavior.
- CÃ³ rollback path náº¿u thay thiáº¿t bá»‹: backup config, console access, out-of-band access.
- Vá»›i thiáº¿t bá»‹ cÃ³ nhiá»u PSU, tÃ¡ch nguá»“n sang PDU/circuit khÃ¡c náº¿u cÃ³ thá»ƒ.

## Baseline Configuration

Baseline nÃªn vendor-neutral á»Ÿ má»©c policy:

- Hostname, management IP, timezone, NTP.
- Admin access qua SSH hoáº·c kÃªnh mÃ£ hÃ³a; trÃ¡nh Telnet trong production.
- AAA hoáº·c local emergency account cÃ³ kiá»ƒm soÃ¡t.
- SNMP/telemetry/logging gá»­i vá» há»‡ thá»‘ng quáº£n lÃ½ táº­p trung.
- Interface description vÃ  shutdown cÃ¡c port chÆ°a dÃ¹ng.
- VLAN, trunk/access policy, LACP/bonding policy.
- Default route/static route/dynamic routing theo thiáº¿t káº¿.
- Backup config Ä‘á»‹nh ká»³ vÃ  lÆ°u ngoÃ i thiáº¿t bá»‹.

## Acceptance

Nghiá»‡m thu khÃ´ng nÃªn chá»‰ kiá»ƒm tra "ping Ä‘Æ°á»£c". Cáº§n xÃ¡c nháº­n theo nhiá»u lá»›p:

| Lá»›p | Kiá»ƒm tra |
| --- | --- |
| Physical | link up, speed/duplex, optical power, error/CRC/drop |
| Layer 2 | VLAN Ä‘Ãºng, MAC learning á»•n, khÃ´ng loop, LACP/STP Ä‘Ãºng |
| Layer 3 | IP/subnet/gateway/route Ä‘Ãºng, route failover hoáº¡t Ä‘á»™ng |
| Services | DHCP, DNS, NTP, AAA, SNMP/logging hoáº¡t Ä‘á»™ng |
| Security | ACL/firewall rule Ä‘Ãºng hÆ°á»›ng, admin access Ä‘Æ°á»£c giá»›i háº¡n |
| Resilience | táº¯t thá»­ uplink/node theo ká»‹ch báº£n Ä‘Ã£ duyá»‡t |
| Documentation | diagram, IP plan, port map, config backup, rollback note |

## Operations Model

MÃ´ hÃ¬nh FCAPS giÃºp chia network operations thÃ nh 5 nhÃ³m:

- **Fault management**: phÃ¡t hiá»‡n lá»—i, alarm, incident, RCA.
- **Configuration management**: quáº£n lÃ½ config, backup, drift, change.
- **Accounting management**: theo dÃµi usage, tenant/user/team náº¿u cáº§n chargeback.
- **Performance management**: latency, packet loss, throughput, utilization, error.
- **Security management**: admin access, ACL, segmentation, audit, compliance.

Trong thá»±c táº¿, change management vÃ  documentation quyáº¿t Ä‘á»‹nh ráº¥t nhiá»u cháº¥t lÆ°á»£ng váº­n hÃ nh. Má»™t thay Ä‘á»•i nhá» vá» VLAN/trunk/route cÃ³ thá»ƒ gÃ¢y outage lá»›n náº¿u thiáº¿u review vÃ  rollback.

## Monitoring Signals

CÃ¡c signal nÃªn cÃ³:

- Interface status, link flap, speed/duplex, CRC, discard, error.
- Device CPU, memory, temperature, fan, PSU.
- Route neighbor state, LACP state, STP topology change.
- DHCP pool usage, DNS error, NTP sync.
- Firewall drop/deny, ACL hit count, VPN tunnel state.
- Latency, packet loss, jitter giá»¯a cÃ¡c site hoáº·c segment quan trá»ng.

SNMP vÃ  NTP lÃ  hai ná»n táº£ng ráº¥t phá»• biáº¿n: SNMP phá»¥c vá»¥ monitoring thiáº¿t bá»‹, NTP giÃºp log vÃ  certificate/token validation cÃ³ cÃ¹ng timeline. Time drift cÃ³ thá»ƒ lÃ m RCA sai hÆ°á»›ng.

## Troubleshooting Flow

Khi gáº·p lá»—i network, Ä‘i tá»« dÆ°á»›i lÃªn:

1. Link/interface cÃ³ up khÃ´ng, error counter cÃ³ tÄƒng khÃ´ng?
2. Port thuá»™c Ä‘Ãºng VLAN/access/trunk khÃ´ng?
3. ARP/MAC table cÃ³ há»c Ä‘Ãºng khÃ´ng?
4. IP/subnet/gateway cÃ³ Ä‘Ãºng khÃ´ng?
5. Route Ä‘i Ä‘Ã¢u, return path cÃ³ Ä‘á»‘i xá»©ng khÃ´ng?
6. ACL/firewall/security group cÃ³ drop khÃ´ng?
7. DNS resolve Ä‘Ãºng IP khÃ´ng?
8. Service port cÃ³ listen vÃ  tráº£ response Ä‘Ãºng protocol khÃ´ng?

KhÃ´ng nÃªn nháº£y ngay vÃ o dynamic routing hoáº·c firewall policy khi chÆ°a xÃ¡c nháº­n physical, VLAN vÃ  addressing.

## Automation Use Cases

Network automation nÃªn báº¯t Ä‘áº§u tá»« tÃ¡c vá»¥ Ã­t rá»§i ro:

- Inventory vÃ  backup config.
- Audit cáº¥u hÃ¬nh chuáº©n: NTP, SNMP, SSH, interface description, unused ports.
- Report interface error vÃ  capacity.
- Generate config tá»« template Ä‘Ã£ review.
- Bulk change cÃ³ canary device, dry-run, approval vÃ  rollback.

Automation khÃ´ng thay tháº¿ hiá»ƒu biáº¿t network. NÃ³ khuáº¿ch Ä‘áº¡i cáº£ cáº¥u hÃ¬nh Ä‘Ãºng láº«n cáº¥u hÃ¬nh sai, nÃªn cáº§n validation vÃ  blast-radius control.

## Related Pages

- [Network Overview](../Overview.md)
- [Network Troubleshooting Tools](./03-network-troubleshooting-tools.md)
- [Ethernet, Media, Topologies And Layer 2](../02-ethernet-switching/01-ethernet-media-topologies-and-layer2.md)
- [IPv4 Addressing And Subnetting](../03-ip-routing-subnetting/01-ipv4-addressing-and-subnetting.md)
- [Common Network Protocols And Ports](../04-protocols-and-services/01-common-network-protocols-and-ports.md)
