# Common Linux Troubleshooting Runbooks

## 1. Service Failed

### Triệu chứng

- `systemctl status` báo `failed`.
- Application không listen port.
- Health check fail sau deploy/restart.

### Lệnh kiểm tra nhanh

```bash
systemctl status <service>
journalctl -u <service> -xe
journalctl -u <service> -b
systemctl cat <service>
systemctl list-dependencies <service>
```

### Nguyên nhân thường gặp

- Config syntax lỗi.
- File path hoặc environment file không tồn tại.
- User chạy service thiếu quyền.
- Port đã bị process khác chiếm.
- Dependency như mount/network/database chưa sẵn sàng.

### Cách xử lý

```bash
# Ví dụ kiểm tra port
sudo ss -tulpn | grep <port>

# Kiểm tra config nếu service hỗ trợ
nginx -t
sshd -t

# Reload/restart sau khi sửa
sudo systemctl daemon-reload
sudo systemctl restart <service>
```

### Rollback / Lưu ý prod

- Revert config gần nhất.
- Kiểm tra `systemctl edit` override.
- Không `restart` service stateful nếu chưa rõ tác động.

## 2. Permission Denied

### Triệu chứng

- App báo permission denied khi đọc config/ghi log.
- User không truy cập được directory.
- Script chạy bằng cron/systemd fail nhưng chạy tay thì được.

### Lệnh kiểm tra nhanh

```bash
id <user>
ls -lah <path>
namei -l <path>
getfacl <path>
sudo -l -U <user>
getenforce 2>/dev/null
```

### Nguyên nhân thường gặp

- Owner/group sai.
- Directory cha thiếu execute bit.
- ACL hoặc SELinux chặn.
- Service chạy bằng user khác với user test.
- Mount option như `ro`, `noexec`, `nosuid`.

### Cách xử lý

```bash
sudo chown app:app <path>
sudo chmod 750 <dir>
sudo restorecon -RFv <path> 2>/dev/null || true
```

### Rollback / Lưu ý prod

- Tránh `chmod -R 777`.
- Ghi lại permission cũ nếu sửa recursive.
- Ưu tiên group/ACL có phạm vi hẹp.

## 3. Package Manager Lock / Repo Error

### Triệu chứng

- `apt` báo lock.
- `dnf/yum` không tải repo metadata.
- Package install dở dang.

### Lệnh kiểm tra nhanh

```bash
ps aux | grep -E 'apt|dpkg|dnf|yum'
sudo lsof /var/lib/dpkg/lock-frontend 2>/dev/null
sudo apt update
sudo dnf repolist
```

### Nguyên nhân thường gặp

- Auto update đang chạy.
- Package transaction bị interrupt.
- DNS/proxy/certificate lỗi.
- Repo URL hoặc distro codename sai.

### Cách xử lý

```bash
# Debian/Ubuntu
sudo dpkg --configure -a
sudo apt -f install
sudo apt update

# RHEL/Fedora
sudo dnf clean all
sudo dnf makecache
```

### Rollback / Lưu ý prod

- Không xóa lock file khi process package thật sự đang chạy.
- Với production, kiểm tra change window trước khi upgrade.

## 4. Mount / fstab Error

### Triệu chứng

- Boot vào emergency mode.
- `mount -a` fail.
- Filesystem không mount sau reboot.

### Lệnh kiểm tra nhanh

```bash
findmnt --verify
mount -a
lsblk -f
blkid
journalctl -xb
```

### Nguyên nhân thường gặp

- UUID sai.
- Mountpoint chưa tồn tại.
- Filesystem type sai.
- Network mount thiếu `_netdev`, `nofail`.
- Disk chưa attach hoặc bị đổi mapping.

### Cách xử lý

```bash
sudo cp /etc/fstab /etc/fstab.bak.$(date +%F-%H%M)
sudo editor /etc/fstab
sudo findmnt --verify
sudo mount -a
```

### Rollback / Lưu ý prod

- Giữ root shell đang mở.
- Với entry không critical, thêm `nofail`.
- Không reboot trước khi `mount -a` sạch.

## 5. DNS / Route / SSH Failed

### Triệu chứng

- Ping IP được nhưng hostname không resolve.
- Không SSH được server.
- App timeout khi gọi endpoint.

### Lệnh kiểm tra nhanh

```bash
ip addr
ip route
ip route get <target-ip>
resolvectl status
getent hosts example.com
dig example.com
ssh -vvv user@host
nc -vz host 22
```

### Nguyên nhân thường gặp

- Sai route/gateway.
- DNS server không reachable.
- Firewall/security group chặn.
- SSH key/permission sai.
- Bastion/ProxyJump sai.

### Cách xử lý

- Tách lỗi theo layer: local interface, route, DNS, firewall, service listen, authentication.
- Kiểm tra cả chiều đi và chiều về nếu có routing phức tạp.

### Rollback / Lưu ý prod

- Với server remote, không restart network bừa nếu không có console.
- Khi sửa SSH, test session mới trước khi đóng session cũ.

## 6. Disk Full

### Triệu chứng

- App không ghi log/data.
- Package install fail.
- Database stop hoặc read-only.

### Lệnh kiểm tra nhanh

```bash
df -h
df -ih
du -xh / --max-depth=1 2>/dev/null | sort -h
lsof +L1
journalctl --disk-usage
```

### Nguyên nhân thường gặp

- Log tăng nhanh.
- Backup ghi vào local disk.
- Deleted file vẫn bị process giữ.
- Inode hết.
- Docker/container image/log đầy.

### Cách xử lý

```bash
sudo journalctl --vacuum-time=7d
sudo logrotate -f /etc/logrotate.conf
```

Với deleted file:

```bash
sudo lsof +L1
sudo systemctl restart <service-holding-deleted-file>
```

### Rollback / Lưu ý prod

- Không xóa file database thủ công.
- Không xóa bừa dưới `/var/lib`, container storage hoặc data directory của service khi chưa biết owner/impact.
- Trước khi xóa log, kiểm tra yêu cầu retention/RCA.
- Sau khi xử lý, thêm rotation/retention.

## 7. Boot Issue

### Triệu chứng

- Server boot vào emergency mode.
- Kernel panic.
- Không lên network sau boot.

### Lệnh kiểm tra nhanh

```bash
journalctl -xb
systemctl --failed
mount -a
lsblk -f
cat /proc/cmdline
```

### Nguyên nhân thường gặp

- `/etc/fstab` lỗi.
- Root filesystem lỗi.
- Kernel/initramfs/GRUB config lỗi.
- Driver/storage path lỗi.
- Service critical fail.

### Cách xử lý

- Dùng console/rescue mode.
- Remount root filesystem read-write nếu cần.
- Sửa fstab/config lỗi.
- Rebuild initramfs/GRUB theo distro nếu thay storage/driver.

### Rollback / Lưu ý prod

- Cần console hoặc out-of-band management.
- Ghi lại kernel version và thay đổi gần nhất.
- Không xóa kernel cũ trước khi kernel mới boot ổn.

## 8. Khi Nào Escalation

Escalate sớm khi có một trong các dấu hiệu:

- Ảnh hưởng production rộng hoặc có customer impact.
- Dữ liệu có nguy cơ mất/corrupt, đặc biệt database, block storage, backup.
- Cần reboot, restart service stateful, thay đổi firewall/network route hoặc sửa boot/GRUB.
- Không có console/out-of-band access nhưng thao tác có thể làm mất SSH.
- Log cho thấy security incident, unauthorized access hoặc thay đổi không rõ nguồn.

## 9. Evidence Checklist

Trước và trong khi xử lý incident, nên ghi lại:

```text
Time window:
Timezone:
Affected host/service:
User-visible impact:
Recent change/deploy:
Commands run:
Important output/log path:
Rollback attempted:
Current risk:
Next owner/escalation:
```
