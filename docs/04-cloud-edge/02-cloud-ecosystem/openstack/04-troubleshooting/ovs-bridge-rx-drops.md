# OpenStack OVS Bridge RX Drops

## Tổng Quan

Trong Red Hat OpenStack Platform hoặc các deployment OpenStack dùng Open vSwitch, đôi khi `ifconfig` hoặc `ip -s link` hiển thị `RX dropped` rất lớn trên interface như `br-int`, `br-ex` hoặc `br-<name>`.

Điểm dễ nhầm nhất:

```text
OVS bridge br-XXX
!=
local/internal interface br-XXX
```

Một OVS bridge thường có một local interface cùng tên với bridge:

```text
Bridge br-int
    Port br-int
        Interface br-int
            type: internal
```

Counter `RX dropped` mà `ifconfig br-int` hoặc `ip -s link show br-int` hiển thị là counter của local interface `br-int`, không phải kết luận trực tiếp rằng toàn bộ OVS bridge đang drop traffic của VM.

Counter này cũng không nhất thiết tăng giống nhau trên mọi node hoặc mọi bridge. Nó phụ thuộc vào traffic đi qua node, service/instance đang chạy, Neutron plugin hoặc OVN/OVS pipeline, và OpenFlow rule hiện có trên bridge.

## Khi Nào Không Phải Sự Cố

Với `br-int`, RX drops lớn thường không phải vấn đề nếu không có lỗi kết nối thực tế:

- `br-int` local interface thường không có IP/network configuration.
- Interface này có thể không `UP`.
- Broadcast, multicast hoặc unknown unicast bị flood tới local interface có thể bị kernel drop.
- Counter tăng không đồng nghĩa tenant VM mất traffic.

Với `br-ex` hoặc bridge khác, RX drops cũng có thể là bình thường nếu bridge nhận traffic không dành cho MAC của local interface đó. Điều này hay xảy ra khi bridge có OpenFlow rule kiểu `NORMAL`, khiến OVS cư xử như switch L2 thông thường.

```bash
ovs-ofctl dump-flows br-ex
```

Ví dụ signal cần chú ý:

```text
priority=0 actions=NORMAL
```

Rule `NORMAL` có thể làm broadcast hoặc unknown unicast được flood tới nhiều port trên bridge, bao gồm local interface `br-ex`. Nếu packet có destination MAC không phải MAC của `br-ex`, kernel có thể drop packet đó và tăng `RX dropped`.

## Khi Nào Cần Điều Tra

Chỉ coi `RX dropped` trên `br-XXX` là một tín hiệu sự cố khi nó đi kèm symptom thật:

- instance mất DHCP hoặc không nhận IP;
- VM không ping/SSH được qua tenant network hoặc floating IP;
- router namespace/provider network có lỗi reachability;
- security group đúng nhưng traffic vẫn không đi qua;
- packet capture cho thấy traffic production bị mất ở datapath;
- alert/metric khác cho thấy network degraded trên cùng thời điểm.

Nếu chỉ thấy counter lớn mà không có user impact, đừng vội restart Neutron/OVS hoặc thay đổi flow.

## Triage Nhanh

Kiểm tra counter:

```bash
ip -s link show br-int
ip -s link show br-ex
```

Kiểm tra topology OVS:

```bash
ovs-vsctl show
ovs-vsctl list-ports br-int
ovs-vsctl list-ports br-ex
```

Kiểm tra flow:

```bash
ovs-ofctl dump-flows br-int
ovs-ofctl dump-flows br-ex
```

Kiểm tra MAC của local interface:

```bash
ip link show br-ex
```

Capture trên local interface để xem packet nào đang đi vào interface đó:

```bash
tcpdump -i br-ex -e -nn -tttt
```

Nếu muốn nhìn nhanh các packet không đi tới MAC local interface của `br-ex`, lấy MAC trước rồi lọc ngược:

```bash
ip link show br-ex
tcpdump -i br-ex -e -nn -tttt | grep -v "<br-ex-mac>"
```

Nếu nhiều packet có destination MAC khác MAC của `br-ex`, chúng có thể chỉ là broadcast/flooded/unknown traffic bị đưa tới local interface rồi bị kernel drop. Đây là evidence để giải thích counter, không phải bằng chứng tự động rằng forwarding path của VM đang lỗi.

## Cách Diễn Giải Counter

| Signal | Diễn giải thận trọng |
|---|---|
| `RX dropped` lớn trên `br-int` nhưng VM/network bình thường | Thường là local interface drop traffic không dành cho nó; chưa đủ bằng chứng lỗi datapath. |
| `RX dropped` lớn trên `br-ex` và có rule `NORMAL` | Có thể do broadcast/unknown unicast bị flood tới local interface. |
| `RX dropped` tăng cùng thời điểm VM mất mạng | Cần điều tra tiếp theo packet path, flow, provider network, security group và upstream switch. |
| `RX errors`, `overruns`, `frame`, CRC hoặc NIC physical errors tăng | Không nên gộp với case OVS local interface; cần debug NIC/driver/link layer riêng. |

Khi ghi nhận ticket hoặc incident, nên lưu cùng một timestamp cho các bằng chứng sau:

```bash
date --iso-8601=seconds
ip -s link show br-ex
ovs-vsctl show
ovs-ofctl dump-flows br-ex
tcpdump -i br-ex -e -nn -tttt -c 50
```

## Debug Theo Packet Path

Khi có connectivity issue thật, đi theo path thay vì chỉ nhìn một counter:

```text
VM tap/vif
-> br-int
-> patch/tunnel/provider bridge
-> br-ex hoặc br-provider
-> bond/VLAN/physical NIC
-> upstream switch
-> gateway/router/firewall
```

Các câu hỏi cần trả lời:

- Packet có ra khỏi VM tap/vif không?
- OVS flow có match và forward đúng port không?
- Provider bridge có mapping đúng physnet/VLAN không?
- Security group/conntrack có chặn không?
- MTU/VLAN/upstream switch có mismatch không?
- Có packet loss thật trên physical NIC hoặc chỉ là local bridge interface counter?

## Rủi Ro Khi Xử Lý

- Không restart `openvswitch`, Neutron agent, OVN service hoặc network node chỉ vì thấy `RX dropped` lớn.
- Không xóa/sửa OpenFlow rule thủ công nếu chưa hiểu deployment đang dùng OVS agent hay OVN.
- Không thay đổi provider bridge, VLAN, bond hoặc uplink trong production nếu chưa có out-of-band access và rollback plan.
- Luôn lưu evidence trước khi thay đổi: timestamp, `ip -s link`, `ovs-vsctl show`, `ovs-ofctl dump-flows`, tcpdump sample và symptom từ VM/user.

## Trang Liên Quan

- [OpenStack General Logs And Maintenance Debug](./general-logs-debug.md)
- [Neutron](../01-core-fundamentals/services/neutron.md)
- [Network Troubleshooting Tools](../../../../02-core-infrastructure/02-network/07-network-operations-lifecycle/03-network-troubleshooting-tools.md)
