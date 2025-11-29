#  —  Networking Cơ bản và Cấu hình 
## 1. Basic Network
### 1.1. Network Interface
- Network Interface (Giao diện mạng) là kênh kết nối giữa thiết bị và mạng. Có thể có nhiều interface hoạt động cùng lúc, các interface có thể được kích hoạt (actived) hoặc không kích hoạt (de-actived)
- File cấu hình network ở những nơi khác nhau tùy vào mỗi nền tảng:
    + Debian: `/etc/network/interfaces`
    + CentOS: `/etc/sysconfig/Network-scripts`
    + SUSE: `/etc/sysconfig/network`

#### Lệnh ip
- Lệnh hiển thị thông tin trên từng Ethernet được kết nối
```sh
ip addr show
```

![](./images/showip.png)

- Hiển thị bảng định tuyến
```sh
ip route show
```

![](./images/showiproute.png)

- Gán IP cho một giao diện mạng
```sh
ip addr add 192.168.1.112 dev ens33
```

![](./images/ganip.png)

- Gỡ bỏ IP từ giao diện mạng
```sh
ip addr del 192.168.1.112/32 dev ens33
```

- Thêm một định tuyến mới
`# ip route add <dia_chi_IP> via <gateway>`

- Xóa định tuyến
`# ip route del default`

- Xóa định tuyến cần xóa
`# ip router del <dia_chi_IP> via <gateway>`

#### Lệnh route
Lệnh route được sử dụng để xem hoặc thay đổi bảng định tuyến IP
- Hiển thị bảng định tuyến
```sh
route -n
```

![](./images/showdinhtuyen.png)

- Thêm định tuyến
```sh
route add -net 112.176.0.0 netmask 255.255.255.0 dev ens33
```

![](./images/adddinhtuyen.png)

- Xóa định tuyến
```sh
route del -net 112.176.0.0 netmask 255.255.255.0 dev ens33
```

![](./images/xoadinhtuyen.png)

### 1.4. Đặt IP tĩnh trên CentOS-7
- Vào thư mục `/etc/sysconfig/network-scripts`

![](./images/listcard.png)

- Chọn card muốn set ip tĩnh. Ở đây em chọn ens33
```sh
vi ifcfg-ens33
```

![](./images/ens33.png)

- Thoát và lưu lại
- Khởi động lại card mạng bằng lệnh 
```sh
systemctl restart network.service
```
- Kiểm tra lại IP được cài đặt

![](./images/ktraip.png)

### 1.5. Linux Virtual Networking
- Linux Virtual Networking có thể dễ dàng tạo ra từ `libvirt` và `linux virtual bridge`
- Cài đặt và bắt đầu kích hoạt `libvirt`:
```sh
yum install libvirt
systemctl start libvirtd
systemctl enable libvirtd
```
- `libvirt` hỗ trợ các loại mạng ảo sau
    + Network Address Translation mode (Chế độ dịch địa chỉ mạng - NAT)
    + Routed Mode (Chế độ định tuyến)
    + Isolated Mode (Chế độ cô lập)
    + Bridged Mode (Chế độ bridged)

#### 1.5.1. Virtual Networking trong NAT mode
- Khi trình nền `libvirt` được cài đặt trên máy chủ, nó đi kèm với cấu hình chuyển đổi mạng ảo, switch ảo mặc định ở chế độ NAT và được sử dụng bởi các máy ảo để liên lạc với mạng bên ngoài thông qua máy chủ vật lí
- File cấu hình được lưu tại `/etc/libvirt/qemu/networks/default.xml`
- Interface virbr0 cũng được tạo trên máy chủ

![](./images/libvirt.png)

- Lệnh `virsh` dùng để kiểm tra và cấu hình mạng ảo
```sh
virsh net-list.
```

![](./images/virsh.png)

- Khi `libvirt` đang chạy mặc định, ta sẽ thấy 1 bridge bị cô lập. Bridge này không có bất kỳ interface vật lý nào thêm vào, vì nó sử dụng NAT để kết nối mạng ra ngoài

![](./images/brctl.png)

- `libvirt` sẽ thêm quy tắc `iptable`. Nó cũng sẽ kích hoạt `ip-forward`

![](./images/ipforward.png)
