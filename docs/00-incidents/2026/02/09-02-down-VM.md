title: "VM khách bị báo down đột ngột "
date: 09/02/2026


## Các bước dự đoán nguyên nhân đã thực hiện 

1. Kiểm tra trạng thái Instance trên dashboard Openstack hoặc trong controller node trạng thái VM vẫn là `active` và `running`
```bash
openstack server show <INSTANCE_ID> -c OS-EXT-STS:vm_state -c OS-EXT-STS:power_state
+------------------------+---------+
| Field                  | Value   |
+------------------------+---------+
| OS-EXT-STS:power_state | Running |
| OS-EXT-STS:vm_state    | active  |
+------------------------+---------+

# Optional check fault xem có lỗi từ nova không 
openstack server show <INSTANCE_ID> -c fault
```
-> Trạng thái VM vẫn là `active` và `running`
-> VM không bị stop ở control-plane

2. Check compute node của nó 
```bash
openstack server show <INSTANCE_ID> -c "OS-EXT-SRV-ATTR:host" # Tìm host của compute 

# Trên compute node 
journalctl --since "YYYY-MM-DD 00:00" --until "YYYY-MM-DD 12:00" | grep -i -E "tap|Lost carrier|Link DOWN|Link UP|ovs|neutron|agent|libvirt|qemu|rbd|blocked for more" | grep -iv "telegraf"

## check Neutron logs xem có thể nguyên nhân do live migration thất bại hay Neutron agent bị flap
journalctl -u neutron-openvswitch-agent
```
- Nếu không có log bất thường hoặc không log , loại trừ các lỗi  
    - compute reboot
    libvirt crash
    - qemu bị kill
    - Ceph blocked I/O
    - OVS agent restart

> Lưu ý , log có thể bị miss nếu như có log rotation xảy ra hoặc journald config không lưu đủ 

- Trường hợp có log 
```bash
tapXXXX: Link DOWN
tapXXXX: Lost carrier
tapXXXX: Link UP
```
=> Interface bị remove rồi add lại 
Thường xảy ra khi : 
+ Reboot VM
+ Nova replug interface
+ Port detach/attach
+ OVS dataplane reload


3. Kiểm tra VM có thực sự chạy không 
```bash
# trên compute node 
virsh domstate <uuid>
virsh dominfo <uuid>


## Kết quả thường thấy 
State: running 
Memory full allocated

=> không phải crash

# Check thêm CPU/memory usage xem VM có bị thiếu resource không 
virsh domstats <uuid> --cpu-total
virt-top

# Kiểm tra để chắc chắn process qemu vẫn còn sống 
ps aux | grep qemu
```
VM thực sự vẫn chạy ở hypervisor.
=> Loại trừ các khả năng 
- VM crash
- Kernel panic hypervisor
- qemu chết
- Nova destroy

4. Kiểm tra network 
```bash
ping 8.8.8.8
ping <IP_INSTANCE>

journalctl --since -30min | grep tap
=> Không log thì loại trừ nguyên nhân networkcompute 

ip -s link show tapXXXX
# Kết quả bình thường 
RX errors: 0
TX errors: 0
dropped: 0
carrier: 0



## Kiểm tra OVS flows
ovs-ofctl dump-flows br-int
```
Nếu không báo lỗi gì từ log thì loại trừ các nguyên nhân :
- Packet drop
- NIC error
- Buffer overrun
- Carrier issue vật lý

=> Network ở compute không lỗi.

4. Kiểm tra trong ceph 
```bash
# Kiểm tra các trạng thái: 
ceph -s

ceph pg stats 
rbd status <pool>/<image>


```
Nếu Ceph không có trạng thái lỗi gì thì loại trừ nguyên nhân do Storage 

=> Chỉ còn nguyên nhân do Guest OS treo 
- Dấu hiệu đặc trưng:
    - VM Running nhưng không truy cập được
    - Không có log hypervisor
    - Reboot là hết
    - Windows Server (Cloudbase-init có log)
    - Không có storage/network error
- Các nguyên nhân thường gặp:
    - Windows update stuck
    - Antivirus deadlock
    - Service chiếm 100% CPU
    - Driver virtio lỗi
    - Application deadlock
    - RDP service crash
    - Windows networking stack freeze

## Thao tác xử lý 

Xác định được lỗi tỷ lệ lớn do Guest OS , yêu cầu khách reboot lại hoặc tự reboot cho khách



