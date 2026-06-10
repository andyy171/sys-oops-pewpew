# Container, KVM, cgroup và namespace

## 1. Linux Isolation Overview

Container và virtualization dựa trên các cơ chế isolation khác nhau:

- Namespace: cô lập view của process về hệ thống.
- cgroup: giới hạn và đo tài nguyên.
- Filesystem layer: rootfs/image cho container.
- KVM: virtualization ở mức VM, guest có kernel riêng.

Network namespace lab thực hành nằm ở [SSH, JumpHost, LLDP, Bridge và Network Namespace](../02-storage-networking/05-ssh-jumphost-lldp-bridge-netns.md). File này tập trung vào concept isolation/virtualization.

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

## 3. cgroup

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

## 4. Docker/Podman Basic

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

## 5. Container Log, Storage và Network Overview

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

## 6. KVM Overview

KVM là hypervisor trong Linux kernel, cho phép chạy VM với hardware virtualization.

Kiểm tra CPU hỗ trợ:

```bash
egrep -c '(vmx|svm)' /proc/cpuinfo
lsmod | grep kvm
```

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

## 7. libvirt và virsh

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

## 8. Virtual Networking

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

## 9. Production Notes

- Container không phải security boundary tuyệt đối như VM.
- Không chạy privileged container nếu không cần.
- Mount Docker socket vào container là rủi ro cao.
- Với VM production, quản lý snapshot/backup rõ ràng.
- Với cgroup limit, theo dõi OOM và throttling.
