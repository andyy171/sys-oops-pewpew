# Neutron

## Overview

Neutron là Networking service của OpenStack. Nó cung cấp network, subnet, router, port, floating IP, security group và integration với backend như Open vSwitch hoặc OVN. Khi một instance boot, Nova cần Neutron cấp port/NIC, IP, security group và đường routing phù hợp trước khi VM thật sự usable.

Mental model:

```text
Project
  -> network
  -> subnet / IP allocation
  -> port gắn vào instance/router
  -> router nối internal network ra external network
  -> floating IP nếu cần public access
```

## Components

| Component | Vai trò |
|---|---|
| `neutron-server` | Nhận API request và gọi ML2/mechanism driver. |
| ML2 plugin | Mapping logical network sang backend implementation. |
| OVS agent hoặc OVN controller | Lập trình datapath trên compute/network node. |
| L3/DHCP/metadata agent | Thường gặp trong mô hình OVS agent truyền thống. |
| OVN northbound DB | Lưu logical network config từ Neutron ML2/OVN. |
| OVN southbound DB | Lưu logical flow để `ovn-controller` lập trình OVS. |
| `neutron-ovn-metadata-agent` | Cung cấp metadata path cho instance trong OVN deployment. |

Trong deployment mới, OVN thường thay thế nhiều Neutron agent truyền thống. Vì vậy khi debug phải biết cloud đang dùng OVS agent hay OVN.

## Object Model

| Object | Vai trò | Trường/trạng thái cần nhìn khi debug |
|---|---|---|
| Network | Broadcast domain logic của project hoặc provider network. | `status`, `admin_state_up`, `provider:network_type`, `provider:physical_network`, `provider:segmentation_id`, `router:external`, `mtu`. |
| Subnet | IPAM scope gắn với network. | CIDR, gateway, allocation pool, DHCP enabled/disabled, DNS. |
| Router | Logical router nối tenant subnet ra external network. | `external_gateway_info`, `interfaces_info`, `enable_snat`, `status`, `routes`. |
| Port | Điểm gắn với VM VIF, router interface, DHCP, floating IP hoặc service port. | `status`, `device_owner`, `device_id`, `binding_host_id`, `binding_vif_type`, `fixed_ips`, `port_security_enabled`, `security_group_ids`. |
| Floating IP | Public/reachable IP được associate vào port của instance. | `floating_ip_address`, `fixed_ip_address`, `port_id`, `router_id`, `status`. Floating IP chưa associate thường chưa có `port_id` và có thể hiển thị `DOWN`. |
| Security group | Firewall policy gắn với port/instance. | Direction, ethertype, protocol, port range, remote CIDR/group, stateful/stateless tuỳ backend. |

Một port `DOWN` không luôn nghĩa là network hỏng. Port của VM tắt, port chưa bind, port floating IP chưa associate hoặc port đặc biệt của router/DHCP có thể có trạng thái khác nhau tuỳ backend.

## OVS Và OVN

Open vSwitch là virtual switch trên host. Các command hữu ích:

```bash
ovs-vsctl -V
ovs-vsctl show
ovs-vsctl list-br
ovs-vsctl list-ports br-int
```

OVS thường có ba bridge quan trọng:

| Bridge | Vai trò |
|---|---|
| `br-int` | Integration bridge, nơi VIF/tap của instance được gắn vào datapath. |
| `br-ex` | External/provider bridge, nối với physical NIC hoặc provider network. |
| `br-tun` | Tunnel bridge trong mô hình VXLAN/GRE OVS agent. |

Thành phần OVS trên host gồm kernel datapath, `ovs-vswitchd` và `ovsdb-server`. Trong mô hình OVS agent, `neutron-openvswitch-agent` nhận RPC từ `neutron-server` qua message broker rồi cấu hình OVS local. Routing/NAT không phải nhiệm vụ chính của OVS agent; thường do `neutron-l3-agent` và namespace/router path xử lý.

OVN thêm control plane logical networking phía trên OVS:

```text
Neutron API
  -> ML2/OVN driver
  -> OVN northbound DB
  -> ovn-northd
  -> OVN southbound DB
  -> ovn-controller
  -> Open vSwitch flows
```

OVN database path:

| Thành phần | Vai trò vận hành |
|---|---|
| OVN northbound DB | Lưu logical switch/router/ACL/DHCP option từ ML2/OVN. Thường gặp OVSDB listener ở port `6641`. |
| `ovn-northd` | Biến desired logical config trong NB DB thành logical flow cho SB DB. |
| OVN southbound DB | Lưu logical flow, chassis và binding. Thường gặp OVSDB listener ở port `6642`. |
| `ovn-controller` | Chạy trên compute/network node, đọc SB DB và lập trình OpenFlow vào OVS. |
| OVN metadata agent | Cung cấp metadata path cho instance, thường qua namespace/HAProxy local theo chassis. |

Khác biệt vận hành:

| Mảng | OVS agent truyền thống | OVN |
|---|---|---|
| L2 datapath | OVS + neutron-openvswitch-agent | OVS + ovn-controller |
| L3/DHCP | L3 agent, DHCP agent, namespace riêng | OVN logical router/DHCP |
| Metadata | neutron-metadata-agent | OVN metadata agent/HAProxy |
| Debug đầu tiên | `openstack network agent list`, OVS bridge, namespace | `openstack network agent list`, OVN NB/SB, ovn-controller log |

## Network Resource Workflow

Tạo external provider network:

```bash
openstack network create \
  --share \
  --external \
  --provider-physical-network physnet1 \
  --provider-network-type flat \
  ext-net

openstack subnet create \
  --network ext-net \
  --no-dhcp \
  --allocation-pool start=<PUBLIC_START>,end=<PUBLIC_END> \
  --gateway <PUBLIC_GW> \
  --subnet-range <PUBLIC_CIDR> \
  ext-subnet
```

Tạo tenant network:

```bash
openstack network create demo-net
openstack subnet create \
  --network demo-net \
  --gateway 10.0.0.1 \
  --subnet-range 10.0.0.0/24 \
  demo-subnet

openstack router create demo-router
openstack router add subnet demo-router demo-subnet
openstack router set --external-gateway ext-net demo-router
```

Kiểm tra:

```bash
openstack network list
openstack network show <network>
openstack subnet list
openstack router list
openstack router show <router>
openstack port list
openstack port show <port-id>
```

Floating IP:

```bash
openstack floating ip create ext-net
openstack server add floating ip <server> <floating-ip>
openstack floating ip list
```

Capability của cloud không nên đoán theo tên release. Kiểm tra extension/thực thi:

```bash
openstack extension list --network
```

Các extension hay ảnh hưởng troubleshooting: `external-net`, `provider`, `router`, `port-security`, `binding`, `quotas`, `quota_details`, `qos`, `rbac-policies`, `security-group`, `trunk`, `network-ip-availability`.

## Security Groups

Security group là firewall rule ở mức port/instance. Với OVN, rule thường được hiện thực bằng conntrack/flow logic phía dưới; với OVS agent truyền thống, implementation có thể khác, nhưng user-facing model vẫn là security group/rule.

```bash
openstack security group create web-sg
openstack security group rule create --protocol tcp --dst-port 22 --remote-ip <MGMT_CIDR> web-sg
openstack security group rule create --protocol tcp --dst-port 80 --remote-ip 0.0.0.0/0 web-sg
openstack security group rule list web-sg
openstack server add security group <server> web-sg
openstack server remove security group <server> web-sg
```

Nguyên tắc:

- Chỉ mở port/protocol cần thiết.
- SSH/RDP nên giới hạn theo management CIDR.
- Không dựa vào floating IP như một boundary bảo mật.
- Review default security group của mỗi project.

## Quota

Network quota giới hạn số lượng network, subnet, port, router, floating IP, security group và security group rule theo project.

```bash
openstack quota list --network --detail
openstack quota show <project>
openstack quota set --secgroups <number> <project>
```

Nếu boot instance fail vì không cấp được port hoặc floating IP, quota là một trong các điểm phải kiểm tra sớm.

## Verification

```bash
openstack network agent list
systemctl status neutron-server
tail -f /var/log/neutron/server.log
ls /var/log/neutron/ /var/log/ovn
```

Trong Horizon, các view hữu ích là Network Topology, Networks, Routers, Security Groups và Admin/System Information/Network Agents.

## Troubleshooting

| Triệu chứng | Hướng kiểm tra |
|---|---|
| Instance không có IP | Subnet DHCP, port status, Neutron/OVN agent, quota port. |
| Không SSH/ping được | Security group, floating IP association, router gateway, route, provider network. |
| Router không ra ngoài | External gateway, SNAT, provider bridge/physnet mapping, upstream gateway. |
| Port `DOWN` | Instance binding, compute host agent/ovn-controller, binding host, VIF type. |
| Security group không có tác dụng | Rule direction/remote CIDR, port security, OVN/OVS flow, conntrack state. |
| Network agent down | `openstack network agent list`, service log, RabbitMQ, host connectivity. |

Debug theo chuỗi:

```text
network/subnet -> router -> port -> security group -> floating IP -> agent/OVN -> provider fabric
```

## Related Pages

- [Nova](./nova.md)
- [OpenStack General Logs And Maintenance Debug](../../04-troubleshooting/general-logs-debug.md)
- [OpenStack OVS Bridge RX Drops](../../04-troubleshooting/ovs-bridge-rx-drops.md)
- [OpenStack Security](../../03-security/overview.md)
