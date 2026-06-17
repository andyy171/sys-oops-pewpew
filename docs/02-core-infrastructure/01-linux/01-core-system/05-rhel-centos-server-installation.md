# RHEL/CentOS Server Installation

## 1. Mục Đích

Note này là runbook cài đặt Linux server thuộc họ RHEL cho lab hoặc môi trường thử nghiệm. Trọng tâm là chuẩn bị tài nguyên, verify ISO, cài server headless, cập nhật package và audit cơ bản sau installation.

Trong thực tế hiện nay, cần phân biệt rõ:

- RHEL là distribution enterprise có subscription, support, errata và lifecycle rõ ràng.
- Red Hat Developer Subscription for Individuals là lựa chọn no-cost cho cá nhân học, lab, demo, prototype và một số use case nhỏ theo điều khoản của Red Hat.
- CentOS Linux classic đã đi tới EOL; CentOS Stream hiện là distro phát triển liên tục, nằm ở vị trí midstream giữa Fedora và RHEL. Với lab muốn tương tự RHEL downstream, cân nhắc RHEL developer subscription, Rocky Linux hoặc AlmaLinux tùy mục tiêu.

## 2. Khi Nào Dùng

Phù hợp khi cần:

- Tạo VM học Linux server không GUI.
- Dựng môi trường lab để học `dnf`, `systemd`, boot log, SSH, network và package update.
- Chuẩn hóa checklist cài đặt trước khi đưa host vào bài lab lớn hơn.
- Kiểm tra nhanh installation trước khi cài application hoặc agent.

Không nên dùng nguyên xi cho production bare metal nếu chưa có thiết kế về partitioning, RAID, network, security baseline, backup, monitoring, remote console và rollback.

## 3. Chuẩn Bị Tài Nguyên

Với VM lab tối thiểu:

| Resource | Gợi ý lab |
| --- | --- |
| CPU | 2 vCPU nếu host đủ tài nguyên |
| Memory | 2-4 GB cho server lab nhẹ |
| Disk | 20 GB trở lên |
| Network | NAT cho internet; Bridged nếu cần SSH từ LAN |

Với server thật, sizing phải dựa trên workload. OS chỉ là phần nền; database, web server, container runtime, monitoring agent hoặc storage service sẽ cần CPU/RAM/disk/IO riêng.

## 4. Chuẩn Bị ISO Và Hypervisor

Nếu cài trong VM:

| Thành phần | Vai trò |
| --- | --- |
| Hypervisor | VirtualBox, VMware Workstation, Hyper-V, KVM/libvirt hoặc nền tảng tương đương |
| ISO image | File boot/install của RHEL, CentOS Stream hoặc distro tương thích |
| Virtual disk | Disk đích để installer ghi OS |
| Network adapter | NAT, Bridged hoặc host-only tùy mục tiêu lab |

Khi tải hypervisor, chọn package theo **host OS**, không theo guest OS. Ví dụ host Windows cài CentOS/RHEL guest thì tải VirtualBox cho Windows.

## 5. Verify ISO

Sau khi tải ISO, verify checksum trước khi dùng. ISO hỏng có thể vẫn boot được nhưng lỗi giữa quá trình install, gây mất thời gian debug sai hướng.

PowerShell:

```powershell
Get-FileHash .\rhel-*.iso -Algorithm SHA256
Get-FileHash .\CentOS-*.iso -Algorithm SHA256
```

Linux:

```bash
sha256sum ./rhel-*.iso
sha256sum ./CentOS-*.iso
```

So sánh hash local với checksum từ trang download chính thức. Nếu khác, tải lại ISO từ nguồn tin cậy.

## 6. Cài Trên VM

Luồng tổng quát:

```text
Tạo VM
-> Gán CPU/RAM/disk/network
-> Mount ISO vào virtual optical drive
-> Boot VM từ ISO
-> Chọn Install
-> Chọn ngôn ngữ
-> Chọn installation destination
-> Chọn software selection dạng Server hoặc Minimal Install
-> Bật network nếu cần
-> Đặt root password hoặc tạo admin user
-> Begin installation
-> Reboot
-> Remove ISO khỏi virtual drive
-> Boot lại từ virtual disk
```

Gợi ý lab với VirtualBox:

| Hạng mục | Gợi ý |
| --- | --- |
| VM name | `rhel-lab-1` hoặc `centos-stream-lab-1` |
| Disk type | VDI hoặc định dạng mặc định của hypervisor |
| Disk allocation | Dynamically allocated cho lab |
| Network Adapter 1 | NAT để có internet nhanh |
| Network Adapter 2 | Bridged nếu cần VM như một node trong LAN |
| Pointing Device | USB Tablet nếu VirtualBox bị lệch chuột |

Bridged Adapter giúp VM nhận IP trong cùng mạng với host, tiện cho SSH từ host hoặc từ máy khác trong LAN. Nếu chỉ cần VM ra internet để update package, NAT thường đủ và ít rủi ro hơn.

## 7. Cài Trên Bare Metal

Với server vật lý, không copy ISO như file thường vào USB. Cần tạo bootable USB bằng công cụ phù hợp, sau đó boot server từ USB.

```text
Download ISO
-> Verify checksum
-> Ghi ISO ra USB bootable
-> Kiểm tra boot mode BIOS/UEFI
-> Boot server từ USB
-> Install OS
-> Remove USB
-> Boot từ disk nội bộ
```

Production notes:

- Kiểm tra out-of-band access như IPMI, iDRAC hoặc iLO trước khi thao tác từ xa.
- Xác nhận đúng disk trước khi partition/format vì installer có thể xóa dữ liệu.
- Với server thật, cần quyết định trước layout disk, LVM, RAID, encryption, network bonding/VLAN và hostname.

## 8. Cập Nhật Sau Cài Đặt

Sau boot đầu tiên, cập nhật package:

```bash
sudo dnf list upgrades
sudo dnf upgrade
```

Nếu kernel hoặc system library quan trọng được update, lên kế hoạch reboot và kiểm tra lại kernel đang boot:

```bash
uname -r
rpm -q kernel
```

Không reboot production chỉ vì thói quen; với lab thì reboot sau update lớn giúp xác nhận hệ thống boot sạch.

## 9. Audit Installation

Kiểm tra boot và phiên bản:

```bash
systemctl get-default
systemctl --failed
journalctl -p warning..alert -b --no-pager
dmesg -T | tail -100
cat /etc/redhat-release
uname -r
cat /proc/version
bash --version
```

Với server headless, default target thường nên là:

```text
multi-user.target
```

Nếu thấy `graphical.target`, kiểm tra lại software selection hoặc dependency GUI có thật sự cần không.

## 10. Checklist

- [ ] Xác định mục tiêu: RHEL, CentOS Stream, Rocky Linux hoặc AlmaLinux.
- [ ] Kiểm tra CPU/RAM/disk đủ cho host, hypervisor và VM.
- [ ] Tải ISO từ nguồn chính thức hoặc mirror tin cậy.
- [ ] Verify SHA256 checksum của ISO.
- [ ] Tạo VM hoặc bootable USB.
- [ ] Chọn Server/Minimal Install nếu dùng cho server headless.
- [ ] Cấu hình network phù hợp: NAT, Bridged, VLAN hoặc static IP nếu cần.
- [ ] Tạo admin user và đặt password theo policy lab/production.
- [ ] Remove ISO/USB sau khi cài.
- [ ] Chạy `dnf list upgrades` và `dnf upgrade`.
- [ ] Kiểm tra boot log, failed unit, default target, distro version và kernel version.
- [ ] Ghi lại hostname, IP, credentials owner, package baseline và thay đổi ban đầu.

## 11. Trang Liên Quan

- [Linux Overview, Boot Process và systemd](./01-linux-overview-boot-systemd.md)
- [Package, Process và Service Management](./03-package-process-service.md)
- [Kernel, /proc, /sys và System Information](./04-kernel-proc-sys-system-info.md)

## 12. Tham Khảo

- [CentOS Linux EOL - The CentOS Project](https://www.centos.org/centos-linux-eol/)
- [CentOS Stream - The CentOS Project](https://www.centos.org/centos-stream/)
- [No-cost Red Hat Enterprise Linux Individual Developer Subscription: FAQs](https://developers.redhat.com/articles/faqs-no-cost-red-hat-enterprise-linux)
