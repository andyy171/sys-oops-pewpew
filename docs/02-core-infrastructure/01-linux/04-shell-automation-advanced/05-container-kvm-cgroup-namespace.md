# Container, KVM, cgroup và namespace

## 1. Linux Isolation Overview

Container và virtualization dựa trên các cơ chế isolation khác nhau:

- Namespace: cô lập view của process về hệ thống.
- cgroup: giới hạn và đo tài nguyên.
- Filesystem layer: rootfs/image cho container.
- KVM: virtualization ở mức VM, guest có kernel riêng.

Network namespace lab thực hành nằm ở [SSH, JumpHost, LLDP, Bridge và Network Namespace](../02-storage-networking/05-ssh-jumphost-lldp-bridge-netns.md). File này tập trung vào concept isolation/virtualization.

## 1.1 VM, Hypervisor Và Container Khác Nhau Thế Nào

VM mô phỏng một máy hoàn chỉnh: guest có kernel riêng, device ảo, firmware/boot flow riêng và lifecycle gần giống host vật lý. Container dùng chung kernel với host, cô lập bằng namespace/cgroup/rootfs và thường đóng gói một app hoặc app stack.

| Mô hình | Chạy ở đâu | Đặc điểm vận hành |
| --- | --- | --- |
| Type 1 hypervisor | Trực tiếp trên hardware hoặc lớp rất sát hardware | Phù hợp workload production cần isolation mạnh, quản lý resource và VM lifecycle rõ |
| Type 2 hypervisor | Như một application trên host OS | Phù hợp lab/dev desktop; phụ thuộc nhiều vào host OS |
| Container engine | Trên Linux host/kernel hiện tại | Nhanh, nhẹ, tốt cho app packaging, nhưng không phải boundary mạnh như VM |

Vì vậy đừng coi container là VM nhỏ. Khi cần chạy workload không tin cậy, kernel khác, driver/kernel module riêng hoặc hard multi-tenant isolation, VM thường là boundary rõ hơn. Khi cần packaging nhanh, rollout app, CI/CD hoặc density cao, container phù hợp hơn.

## 2. Namespace

Namespace cô lập tài nguyên kernel theo từng loại:

| Namespace | Cô lập |
| --- | --- |
| PID | Process tree |
| NET | Network stack |
| MNT | Mount points |
| UTS | Hostname/domain |
| IPC | IPC objects |
| USER | User/group ID mapping |
| CGROUP | cgroup view |

Kiểm tra:

```bash
lsns
readlink /proc/$$/ns/pid
readlink /proc/$$/ns/net
```

Chạy process trong namespace mới:

```bash
sudo unshare --fork --pid --mount-proc bash
```

## 3. chroot

`chroot` đổi root directory nhìn thấy bởi process hiện tại và process con. Process bên trong chroot không nhìn thấy path bên ngoài cây root mới theo cách thông thường, nhưng chroot không phải sandbox security hoàn chỉnh như container hoặc VM.

Use case phổ biến:

- Rescue hệ thống không boot được từ Live ISO.
- Reinstall bootloader hoặc rebuild initramfs.
- Sửa package/config khi root filesystem được mount từ môi trường khác.
- Build/test phần mềm trong một root filesystem tách biệt ở mức cơ bản.

Workflow rescue thường gặp:

```bash
sudo mount /dev/<root-partition> /mnt/sysroot
sudo mount -t proc proc /mnt/sysroot/proc
sudo mount --rbind /sys /mnt/sysroot/sys
sudo mount --rbind /dev /mnt/sysroot/dev
sudo mount --rbind /run /mnt/sysroot/run
sudo cp /etc/resolv.conf /mnt/sysroot/etc/resolv.conf
sudo chroot /mnt/sysroot /bin/bash
```

Sau khi hoàn tất:

```bash
exit
sudo umount -R /mnt/sysroot
```

Lưu ý vận hành:

- Kiến trúc CPU/userland của môi trường rescue và root target phải tương thích.
- Kernel module cần dùng phải được load từ kernel đang chạy, không phải kernel của root target.
- Mount `proc`, `sys`, `dev`, `run` giúp tool trong chroot nhìn thấy runtime API cần thiết.
- Không xem chroot là boundary chống attacker có quyền root.

## 4. cgroup

cgroup giới hạn, ưu tiên và đo tài nguyên như CPU, memory, IO, pids.

Linux hiện đại thường dùng cgroup v2 unified hierarchy. Một số distro hoặc phiên bản cũ còn dùng cgroup v1 hoặc hybrid, nên output và path có thể khác nhau.

```bash
systemd-cgls
systemd-cgtop
cat /proc/self/cgroup
```

Với systemd service, resource control có thể đặt trong unit:

```ini
[Service]
MemoryMax=1G
CPUQuota=50%
TasksMax=200
```

Apply:

```bash
sudo systemctl daemon-reload
sudo systemctl restart <service>
```

### cgroupfs: giao diện thật của kernel

Kernel expose cgroup qua pseudo filesystem, thường mount tại `/sys/fs/cgroup`. Không có một system call riêng kiểu `create_cgroup()`: thao tác cơ bản thực chất là tạo thư mục và ghi giá trị vào các file controller.

```bash
mount -l | grep cgroup
ls /sys/fs/cgroup
```

Tạo một cgroup con:

```bash
sudo mkdir /sys/fs/cgroup/hog_pen
```

Một số file hay gặp trong cgroup v2:

| File | Ý nghĩa |
| --- | --- |
| `cgroup.controllers` | Controller có thể bật cho subtree |
| `cgroup.subtree_control` | Bật/tắt controller cho cgroup con |
| `cgroup.procs` | Danh sách PID thuộc cgroup, đồng thời là nơi ghi PID để move process |
| `cpu.max` | Giới hạn CPU theo quota/period |
| `memory.max` | Giới hạn memory hard limit |
| `memory.current` | Memory đang dùng |
| `pids.max` | Giới hạn số process/thread |

Ví dụ giới hạn process dùng tối đa 50% CPU và 100 MB RAM:

```bash
echo "50000 100000" | sudo tee /sys/fs/cgroup/hog_pen/cpu.max
echo "100M" | sudo tee /sys/fs/cgroup/hog_pen/memory.max
```

Trong `cpu.max`, giá trị đầu là quota, giá trị thứ hai là period, đơn vị microsecond. `50000 100000` nghĩa là process được dùng 50 ms CPU trong mỗi chu kỳ 100 ms, tương đương 50% của một CPU. Trên máy nhiều core, quota có thể lớn hơn `100000`.

Move process đang chạy vào cgroup:

```bash
HOG_PID=$(pgrep -xo hog)
echo "${HOG_PID}" | sudo tee /sys/fs/cgroup/hog_pen/cgroup.procs
```

Nếu muốn process bị giới hạn ngay từ lúc start, hãy đưa parent shell vào cgroup rồi start child process từ shell đó, vì process con sẽ inherit cgroup của parent:

```bash
echo $$ | sudo tee /sys/fs/cgroup/hog_pen/cgroup.procs
./hog
```

Khi `memory.max` bị chạm, kernel có thể trigger OOM trong cgroup và kill process. Đây là cơ chế nền cho giới hạn memory của container và Kubernetes Pod.

Xóa cgroup khi không còn process bên trong:

```bash
cat /sys/fs/cgroup/hog_pen/cgroup.procs
sudo rmdir /sys/fs/cgroup/hog_pen
```

Không dùng `rm -rf` để xóa cgroup trong cgroupfs; các file controller là file ảo của kernel và không thể xóa như file thường.

### libcgroup và systemd-run

`cgcreate`, `cgset`, `cgexec` là wrapper giúp tránh thao tác trực tiếp với cgroupfs:

```bash
sudo cgcreate -g cpu,memory:/hog_pen
sudo cgset -r cpu.max="50000 100000" hog_pen
sudo cgset -r memory.max="100M" hog_pen
sudo cgexec -g cpu,memory:hog_pen ./hog
```

Trên nhiều distro systemd-based, systemd là cgroup manager chính. Với workload tạm thời, `systemd-run` thường dễ vận hành hơn:

```bash
sudo systemd-run -u hog -p CPUQuota=50% -p MemoryMax=100M ./hog
systemctl status hog.service --no-pager
systemd-cgls
```

Nếu transient unit bị fail và không tự dọn, có thể dùng:

```bash
sudo systemctl reset-failed
```

Với giới hạn dùng chung cho nhiều process hoặc container, tạo slice là cách rõ ràng hơn:

```ini
[Slice]
CPUQuota=50%
MemoryMax=100M
```

Docker/containerd/Kubernetes thường không tự ý tranh quyền quản lý cgroup với systemd. Trong production, nên thống nhất cgroup driver và tránh vừa thao tác trực tiếp `cgroupfs`, vừa để systemd/container runtime quản lý cùng một subtree.

## 5. Docker/Podman Basic

```bash
docker ps
docker images
docker run --rm -it alpine sh
docker logs <container>
docker inspect <container>
docker exec -it <container> sh
docker stats
docker port <container>
docker volume ls
docker network ls
```

Podman tương tự:

```bash
podman ps
podman info
podman system df
podman logs <container>
podman exec -it <container> sh
podman generate systemd --new --name <container>
```

Rootless Podman giúp giảm rủi ro chạy container bằng root.

### Docker Runtime Chain Và Socket Risk

Docker trên Linux hiện đại thường là một control plane nhỏ phía trên runtime chain:

```text
docker CLI
-> Docker daemon
-> containerd
-> runc / OCI runtime
-> Linux namespaces, cgroups, mounts, capabilities, seccomp
```

Khi debug container, cần tách lỗi ở tầng nào:

- Docker daemon không nhận lệnh: kiểm tra `systemctl status docker`, socket, permission group và daemon log.
- Image pull/build lỗi: kiểm tra registry, DNS, proxy, certificate, credential và disk space.
- Container start rồi exit: kiểm tra entrypoint, command, environment, mount, permission và `docker logs`.
- App chạy nhưng không vào được: kiểm tra port publishing, container network, host firewall và process listen bên trong container.

```bash
systemctl status docker
docker info
docker inspect <container>
docker logs --tail=200 <container>
docker exec -it <container> sh
```

Docker socket có quyền điều khiển daemon, nên mount `/var/run/docker.sock` vào container gần tương đương trao quyền quản trị host qua Docker API. Chỉ dùng pattern này cho tooling đã tin cậy, giới hạn host, audit image/source và ưu tiên cơ chế ít quyền hơn nếu có. Với CI runner, build agent hoặc automation, tách runner theo trust boundary và không dùng cùng daemon cho workload production lẫn job không tin cậy.

## 6. Container Log, Storage và Network Overview

Log:

```bash
docker logs <container>
journalctl CONTAINER_NAME=<name> 2>/dev/null
```

Storage:

- Image layer thường copy-on-write.
- Volume dùng cho data cần persist.
- Không lưu dữ liệu quan trọng chỉ trong writable container layer.

Network:

- Bridge network: container NAT qua host.
- Host network: container dùng network namespace của host.
- Overlay network: multi-host container network, thường qua orchestrator.

## 7. KVM Overview

KVM là hypervisor trong Linux kernel, cho phép chạy VM với hardware virtualization.

Kiểm tra CPU hỗ trợ:

```bash
egrep -c '(vmx|svm)' /proc/cpuinfo
lsmod | grep kvm
lscpu
virt-what 2>/dev/null || true
```

`vmx` là Intel VT-x, `svm` là AMD-V. Nếu thấy `hypervisor` flag, host hiện tại có thể đang là guest VM; lúc đó nested virtualization còn phụ thuộc cấu hình hypervisor bên ngoài. BIOS/UEFI có thể tắt virtualization extension dù CPU hỗ trợ, nên khi KVM không hoạt động cần kiểm tra cả firmware setting.

Ví dụ tạo VM ở mức overview:

```bash
virt-install \
  --name test-vm \
  --memory 2048 \
  --vcpus 2 \
  --disk size=20 \
  --cdrom /iso/linux.iso
```

Package thường gặp:

- `qemu-kvm`
- `libvirt`
- `virt-install`
- `virt-manager`

## 8. libvirt và virsh

```bash
systemctl status libvirtd 2>/dev/null || systemctl status virtqemud
virsh list --all
virsh dominfo <vm>
virsh start <vm>
virsh shutdown <vm>
virsh console <vm>
```

Storage pool:

```bash
virsh pool-list --all
virsh vol-list <pool>
```

Network:

```bash
virsh net-list --all
virsh net-info default
virsh net-dumpxml default
```

## 8.1 VM Clone, Template Và Identity

Clone/template giúp tạo VM nhanh, nhưng Linux guest cần được làm sạch identity trước khi đưa vào network production. Sau khi clone, kiểm tra:

- hostname;
- static IP hoặc DHCP reservation;
- NIC MAC address;
- `/etc/machine-id`;
- `/var/lib/dbus/machine-id`;
- SSH host keys nếu image được build sai quy trình;
- application-specific identity như agent ID, monitoring ID, cluster node ID.

Ví dụ regenerate machine-id trong lab:

```bash
sudo rm -f /etc/machine-id
sudo systemd-machine-id-setup
sudo dbus-uuidgen --ensure=/var/lib/dbus/machine-id
```

Không chạy máy clone song song với máy gốc nếu chưa xử lý hostname/IP/MAC/machine-id; lỗi duplicate identity có thể trở thành sự cố DNS, DHCP, monitoring hoặc cluster membership.

OVF/OVA là format đóng gói VM để export/import giữa hypervisor hỗ trợ chuẩn tương ứng. Sau khi import OVA/OVF, vẫn phải xử lý identity như clone: hostname, MAC, static IP, machine-id, SSH host key, agent ID và application-specific UUID.

P2V chuyển một máy vật lý thành VM. Đây không chỉ là copy disk: cần kiểm tra driver/initramfs, boot mode BIOS/UEFI, network naming, fstab/UUID, license binding, performance profile, backup agent và monitoring identity. Luôn test boot trong môi trường cô lập trước khi đưa VM P2V vào network production.

`cloud-init` là cơ chế chuẩn để cá nhân hóa image/instance ở lần boot đầu: hostname, user, SSH key, network config, package, script bootstrap. Với image dùng lại nhiều lần, giữ image càng generic càng tốt và đưa khác biệt môi trường qua metadata/user-data thay vì bake thủ công vào từng VM.

## 9. Virtual Networking

Mode thường gặp:

| Mode | Ý nghĩa |
| --- | --- |
| NAT | VM đi ra ngoài qua host NAT |
| Bridged | VM nằm trực tiếp trên LAN/VLAN |
| Isolated | VM chỉ giao tiếp trong private network |

Troubleshooting:

```bash
ip link
ip addr show virbr0
bridge link
virsh net-list --all
journalctl -u libvirtd 2>/dev/null || journalctl -u virtqemud
```

## 10. Production Notes

- Container không phải security boundary tuyệt đối như VM.
- Không chạy privileged container nếu không cần.
- Mount Docker socket vào container là rủi ro cao.
- Với VM production, quản lý snapshot/backup rõ ràng.
- Với cgroup limit, theo dõi OOM và throttling.
