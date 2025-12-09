# Thực hành mount một SMB Share
## Giới thiệu về SMB và Cài đặt Công cụ Cần thiết
**SMB** (hay **CIFS**) là giao thức do Microsoft phát triển, cho phép chia sẻ file, máy in, và tài nguyên mạng. Phiên bản **SMB1** đã lỗi thời và không an toàn (bị Microsoft khuyến cáo loại bỏ do lỗ hổng), nên Linux hiện đại mặc định dùng **SMB2.1** hoặc cao hơn (như **SMB3.0**) để bảo mật. Nếu server cũ yêu cầu SMB1, bạn có thể chỉ định (vers=1.0), nhưng nên nâng cấp server nếu có thể.

Để mount SMB share, cần gói `cifs-utils` (hỗ trợ module kernel cifs.ko). Gói này thường có sẵn, nhưng kiểm tra và cài nếu cần. Dưới đây là lệnh cho các distro phổ biến:
```bash
#Trên SUSE (SLES): Thường đã cài, kiểm tra bằng 
zypper search cifs-utils. 
##Cài đặt: 
sudo zypper install cifs-utils.
# Trên Ubuntu/Debian: 
sudo apt update && sudo apt install cifs-utils.
#Trên Red Hat (RHEL)/CentOS/Fedora: 
sudo dnf install cifs-utils .
```
> Lưu ý quan trọng: Trên một số distro như Ubuntu, bạn có thể cần thêm samba-common hoặc `smbclient` cho công cụ hỗ trợ (như liệt kê shares). Kiểm tra bằng `smbclient -L` //server để xác nhận kết nối. Tránh SMB1 trừ khi bắt buộc; thêm tùy chọn vers=3.0 để chỉ định phiên bản an toàn.

---

## Mount SMB Share Tạm thời trên Linux
- Để mount tạm thời (không tự động khi boot), sử dụng lệnh `mount -t cifs`. 
Trước tiên, tạo thư mục mount point:
```bash
sudo mkdir /smbshare01
```
- Mount với tùy chọn cơ bản, yêu cầu nhập username và password:
```bash
sudo mount -t cifs //server-hostname-or-ip/share-name /smbshare01/ -o username=your-username@domain
```
Ví dụ thực tiễn (áp dụng chung cho tất cả distro):
```bash
sudo mount -t cifs //matrix-VM02.matrixpost-lab.net/fileshare01 /smbshare01/ -o username=superuser@matrixpost-lab.net
```
Hệ thống hỏi password. Để tránh nhập thủ công, tạo file credentials (ví dụ: smb.cred) ở nơi an toàn như `/root`:
```bash
sudo vi /root/smb.cred
```
Nội dung:
```
textusername=your-username
password=your-password
domain=your-domain
```
Đặt quyền hạn:
```bash
sudo chown root:root /root/smb.cred
sudo chmod 600 /root/smb.cred
```

- Mount với credentials:
```bash
sudo mount -t cifs //matrix-VM02.matrixpost-lab.net/fileshare01 /smbshare01/ -o credentials=/root/smb.cred
```
- Kiểm tra mount:
```bash
mount | grep cifs
df -h /smbshare01
```

- Unmount:
```bash
sudo umount /smbshare01
```
> Lưu ý quan trọng: Thay server-hostname bằng IP nếu cần (kiểm tra bằng `ifconfig` hoặc `ip addr` trên server). Đối với share công khai (guest), thêm guest,sec=none. Trên Red Hat, tùy chọn giống hệt; trên Ubuntu, có thể cần thêm `nounix` nếu gặp lỗi quyền hạn.

## Mount SMB Share Vĩnh viễn qua /etc/fstab
- Để mount tự động khi boot, chỉnh sửa /etc/fstab. Sao lưu trước:
```bash
sudo cp /etc/fstab /etc/fstab.bak
```
Thêm dòng (áp dụng chung):
```
//server-hostname/share-name /mount-point cifs credentials=/path/to/smb.cred 0 0
```
**Ví dụ:**
```
//matrix-VM02.matrixpost-lab.net/fileshare01 /smbshare01/ cifs credentials=/root/smb.cred 0 0
```
**Kiểm tra và mount tất cả:**
```bash
sudo mount -a
```
Nếu lỗi, xem log:` dmesg | grep CIFS` hoặc `journalctl -xe`.

> Lưu ý quan trọng: Thêm `_netdev` để chờ mạng sẵn sàng, `nofail` để tránh treo boot nếu share không khả dụng. Trên Debian/Ubuntu, cấu hình tương tự; trên Fedora/RHEL, có thể cần thêm `x-systemd`.`automount` cho mount on-demand.

## Mount SMB Share với Tùy chọn Multiuser
- Multiuser cho phép nhiều user truy cập share với credentials riêng, hữu ích cho môi trường đa người dùng. Mount ban đầu dùng credentials root, sau đó user khác cung cấp key qua cifscreds.
Mount với multiuser (chung cho tất cả distro):
```bash
sudo mount -t cifs //matrix-VM02.matrixpost-lab.net/fileshare01 /smbshare01/ -o multiuser,credentials=/root/smb.cred
```
- Thêm vào `/etc/fstab`:
```
//matrix-VM02.matrixpost-lab.net/fileshare01 /smbshare01/ cifs multiuser,credentials=/root/smb.cred 0 0
```
- User khác gặp "Permission denied" ban đầu. Cung cấp credentials:
```bash
cifscreds add -u username -d domain-or-hostname
```
**Ví dụ:**
```bash
bashcifscreds add -u marcus.rath -d matrixpost-lab.net
```
- Kiểm tra multiuser:
```bash
mount | grep smbshare01
```

> Lưu ý quan trọng: Cifscreds yêu cầu gói `cifs-utils` và kernel hỗ trợ. Xóa key bằng cifscreds clear. Kiểm tra quyền NTFS trên share Windows. Trên Red Hat, tính năng này được hỗ trợ đầy đủ; trên Ubuntu, tương tự nhưng có thể cần cập nhật kernel.

## Lưu ý Bảo mật, Khắc phục Sự cố, và Công cụ Hỗ trợ
- Bảo mật: Sử dụng SMB3 với mã hóa (thêm `sec=ntlmssp` hoặc `krb5` cho Kerberos). Tránh guest access. Giới hạn port `445` qua firewall. Trên Debian, dùng YaST (nếu có) để cấu hình Samba client đồ họa.
- Khắc phục lỗi: `"Permission denied"` – kiểm tra credentials/quyền share. `"No such file"` – xác nhận share tồn tại bằng `smbclient -L //server`. Unmount cưỡng chế: `umount -l`.
- Công cụ hỗ trợ: Liệt kê shares: smbclient -L //server -U username. Trên Ubuntu, có thể dùng Nautilus GUI để mount qua `"Connect to Server"`.