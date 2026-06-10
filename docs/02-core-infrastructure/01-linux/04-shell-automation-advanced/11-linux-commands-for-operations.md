# Linux Commands For Operations

## Mục Tiêu

Note này gom các lệnh Linux hữu ích theo tác vụ vận hành, thay vì học theo danh sách alphabet. Khi dùng trong production, ưu tiên hiểu lệnh đang đọc signal gì, lệnh nào chỉ quan sát, lệnh nào thay đổi trạng thái, và lệnh nào có thể phá dữ liệu hoặc làm mất kết nối.

Các note chuyên sâu vẫn là nơi chính để học concept:

- [Shell, Basic Commands, Pipe và Redirection](./01-shell-basic-commands-pipe-redirection.md)
- [Text Processing: grep, sed, awk, regex và vim](./02-text-processing-grep-sed-awk-regex-vim.md)
- [Bash Scripting, cron và systemd timer](./03-bash-scripting-cron-systemd-timer.md)
- [Package, Process và Service Management](../01-core-system/03-package-process-service.md)
- [Disk, Filesystem, Mount và Swap](../02-storage-networking/01-disk-filesystem-mount-swap.md)
- [IP, Route, DNS và Firewall](../02-storage-networking/04-ip-route-dns-firewall.md)
- [Logs, journald, rsyslog và logrotate](../03-security-logs-troubleshooting/01-logs-journald-rsyslog-logrotate.md)

## Nguyên Tắc Dùng Lệnh

- Bắt đầu bằng lệnh read-only: `hostnamectl`, `uptime`, `df`, `du`, `ip`, `ss`, `systemctl status`, `journalctl`.
- Tách rõ lệnh xem trạng thái với lệnh thay đổi trạng thái. Ví dụ `systemctl status` an toàn hơn `systemctl restart`; `ip route` an toàn hơn `ip route del`.
- Với filesystem, network, firewall, bootloader, kernel parameter và user access, luôn có backup/rollback trước khi sửa.
- Không paste lệnh từ cheatsheet vào production nếu chưa hiểu option và phạm vi path.
- Các lệnh phá hủy như `rm -rf`, `mkfs`, `wipefs`, `dd`, `lvremove`, `vgremove`, `userdel -r`, `iptables -F`, `nft flush ruleset` cần được coi như change có rủi ro cao.

## File Và Directory

Các lệnh nền tảng:

```bash
pwd
ls -lah
cd /var/log
mkdir -p /srv/app
touch app.log
cp -a /src/. /dst/
mv old.conf old.conf.bak
ln -s /opt/app/current /usr/local/bin/app
file /bin/bash
stat /etc/passwd
namei -l /srv/app/config.yml
```

`cp -a` giữ mode, owner, timestamp và symlink tốt hơn `cp -r` trong nhiều tình huống backup/copy cấu hình. `namei -l` hữu ích khi debug `Permission denied` vì nó cho thấy permission của từng directory trên đường dẫn.

Xóa file là thao tác phá hủy. Ưu tiên kiểm tra trước:

```bash
find /tmp/app-cache -type f -name "*.tmp" -mtime +7 -print
rm -i file.txt
rm -rI old-directory/
```

Với đồng bộ dữ liệu:

```bash
rsync -avh --dry-run /src/ user@host:/dst/
rsync -avh /src/ user@host:/dst/
rsync -avh --delete --dry-run /src/ user@host:/dst/
```

`--delete` có thể xóa dữ liệu ở đích; luôn chạy `--dry-run` trước.

## Tìm File Và Tìm Nội Dung

```bash
find /var/log -type f -name "*.log"
find /var/log -type f -mtime +7 -print
find /srv/app -type f -size +100M -print
grep -Rni --exclude-dir=.git "error" /var/log
locate nginx.conf
updatedb
which nginx
whereis nginx
```

Không dùng `find ... -delete` ngay ở lần đầu. Hãy `-print` để xác nhận danh sách trước, sau đó mới đổi sang action phá hủy nếu cần.

## Archive Và Compression

```bash
tar -czf etc-backup.tgz /etc
tar -tzf etc-backup.tgz | head
tar -xzf etc-backup.tgz -C /tmp/restore
gzip app.log
gunzip app.log.gz
xz large.log
zip -r site.zip public/ -x "*.git*"
unzip site.zip -d /tmp/site
```

Với backup cấu hình, cần test restore tối thiểu bằng `tar -tzf` hoặc extract vào thư mục tạm. Backup chưa từng restore thử thì chưa nên xem là đáng tin.

## Text Processing

Nhóm lệnh này thường dùng để đọc log, lọc output và tạo báo cáo nhanh:

```bash
grep -E "error|failed|timeout" app.log
grep -A 3 -B 3 "panic" kernel.log
awk -F: '$3 >= 1000 {print $1, $3}' /etc/passwd
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
sed -n '1,80p' nginx.conf
sed -i.bak 's/old.example/new.example/g' app.conf
cut -d: -f1 /etc/passwd
jq -r '.items[].name' data.json
diff -u old.conf new.conf > change.patch
patch --dry-run < change.patch
```

`sed -i` nên đi kèm suffix backup như `.bak` khi sửa config quan trọng. Với patch, chạy `patch --dry-run` trước để tránh sửa nhầm file.

## Permission, ACL Và Attribute

```bash
id
groups
ls -ld /srv/app
stat /srv/app/config.yml
chmod u=rwX,g=rX,o= /srv/app
chown -R app:app /srv/app
umask
getfacl /srv/app
setfacl -m u:deploy:rwx /srv/app
getfattr -d file.txt
getcap /usr/bin/ping
```

Khi debug permission, kiểm tra theo thứ tự:

1. User/group thực tế của process.
2. Ownership và mode bit của file.
3. Permission của từng directory cha bằng `namei -l`.
4. ACL bằng `getfacl`.
5. SELinux/AppArmor hoặc capability nếu mode bit nhìn có vẻ đúng.

`chmod -R` và `chown -R` có blast radius lớn. Hãy chạy trên path cụ thể, tránh biến rỗng và quote path nếu lấy từ biến.

## User, Group Và sudo

```bash
useradd -m -s /bin/bash alice
passwd alice
usermod -aG sudo alice
id alice
chage -l alice
passwd -l alice
passwd -u alice
visudo
last
lastb
who
```

`usermod -aG` cần có `-a`; thiếu `-a` có thể thay toàn bộ supplementary groups của user. Không sửa trực tiếp `/etc/sudoers` bằng editor thường; dùng `visudo` để có kiểm tra syntax.

## Package, Process Và Service

Package:

```bash
apt update
apt install nginx
dpkg -i package.deb
apt -f install
dnf install nginx
rpm -qa | grep nginx
rpm -ql nginx
zypper install nginx
apk add curl
```

Process:

```bash
ps aux --sort=-%mem | head
pstree -ap
top
htop
lsof -iTCP:443 -sTCP:LISTEN
fuser -v /var/log/app.log
kill -TERM 1234
timeout 30s command
watch -n 2 'df -h; free -m'
```

Service:

```bash
systemctl status nginx --no-pager
systemctl cat nginx
journalctl -u nginx --since "1 hour ago" --no-pager
systemctl reload nginx
systemctl restart nginx
systemctl enable --now nginx
systemctl --failed
```

Thu thập trạng thái và log trước khi restart service, vì restart có thể làm mất evidence tạm thời.

## Disk, Filesystem, Swap Và LVM

Read-only inventory:

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL
blkid
findmnt
df -hT
du -xh --max-depth=1 /var | sort -h
smartctl -a /dev/sda
```

Mount/swap:

```bash
mount -o ro /dev/sdb1 /mnt/recover
umount /mnt/recover
swapon --show
mkswap /swapfile
swapon /swapfile
swapoff /swapfile
```

Filesystem và partitioning là vùng rủi ro cao:

```bash
mkfs.xfs -f /dev/vdb1
parted /dev/vdb
partprobe /dev/vdb
resize2fs /dev/vg0/data
xfs_growfs /data
```

LVM:

```bash
pvs
vgs
lvs
pvcreate /dev/vdb
vgcreate vg0 /dev/vdb
lvcreate -n data -L 100G vg0
lvextend -r -L +50G /dev/vg0/data
lvremove /dev/vg0/data
```

`mkfs`, `dd`, `wipefs`, `pvcreate`, `lvremove`, `vgremove` và `parted` có thể phá dữ liệu. Trước khi chạy cần xác nhận đúng device, có backup, có cửa sổ bảo trì nếu ảnh hưởng workload, và có kế hoạch rollback hoặc restore.

## Network, DNS Và Firewall

Quan sát network theo lớp:

```bash
ip -br link
ip -br addr
ip route
ip neigh
resolvectl status 2>/dev/null || cat /etc/resolv.conf
ss -tupan
ping -c 3 10.0.0.1
tracepath example.com
mtr -rw example.com
dig example.com
tcpdump -i eth0 -nn host 10.0.0.5 and port 443
ethtool eth0
```

Firewall:

```bash
nft list ruleset
iptables -L -n -v
firewall-cmd --list-all
ufw status verbose
```

Lệnh thay đổi route, firewall, DNS, bridge, VLAN hoặc interface có thể làm mất SSH. Khi thao tác remote host, cần có console/out-of-band access hoặc rollback tự động.

## Kernel, Boot Và Logging

Kernel/runtime:

```bash
uname -a
lsmod
modinfo br_netfilter
modprobe br_netfilter
sysctl -a
cat /proc/cmdline
dmesg -T | tail -100
```

Boot/systemd/logging:

```bash
efibootmgr -v
systemd-analyze
systemd-analyze blame
journalctl -xb
journalctl -p warning..alert --since "1 hour ago" --no-pager
logger "manual test log entry"
shutdown -r +5 "planned reboot"
```

Không sửa GRUB, initramfs, kernel module tự động load hoặc `sysctl` production nếu chưa có rollback. `sysctl -w` là thay đổi runtime ngay lập tức, không chỉ là chỉnh file.

## Hardware Và System Information

```bash
hostnamectl
timedatectl
localectl
free -h
lscpu
nproc
lsmem
lspci
lsusb
lsscsi
lshw -short
inxi -F
fwupdmgr get-devices
hwclock --show
```

Các signal phần cứng như SMART warning, ECC/MCE, thermal throttling hoặc firmware lỗi nên được tách khỏi lỗi application. Bắt đầu từ `dmesg`, `journalctl`, SMART, BMC/IPMI nếu có, rồi mới kết luận workload.

## Virtualization, Container Và Cloud CLI

```bash
docker ps
docker logs --tail=100 <container>
docker inspect <container>
virsh list --all
virsh domifaddr vm01
qemu-img info disk.qcow2
qemu-img convert -f qcow2 -O raw disk.qcow2 disk.raw
rclone sync /data remote:backup/data --dry-run
```

`docker`, `virsh`, `qemu-img`, `rclone` và cloud CLI có thể ảnh hưởng workload hoặc dữ liệu ngoài host. Với sync/delete, snapshot/image conversion hoặc container prune, chạy dry-run hoặc kiểm tra inventory trước.

## Bash, Terminal Và Help

```bash
man 5 systemd.service
apropos systemd
whatis ss
tldr tar
help test
type cd
alias ll='ls -lah'
unalias ll
printf "%s\n" "hello"
screen -S maint
screen -r maint
```

Bash scripting building blocks:

```bash
if command; then
  echo "ok"
fi

while getopts "f:v" opt; do
  case "$opt" in
    f) file=$OPTARG ;;
    v) verbose=1 ;;
  esac
done

trap 'rm -f "$tmp"' EXIT
```

Với script vận hành, ưu tiên `set -euo pipefail` khi phù hợp, quote biến path, validate input, log rõ action và có mode dry-run cho thao tác thay đổi trạng thái.

## Mảng Nên Đặt Ở Note Khác Hoặc Chỉ Dùng Khi Cần

Một số lệnh trong inbox không nên trở thành trọng tâm của Linux server operations:

- Printer và desktop GUI: `lpadmin`, `xrandr`, `gsettings`, `gnome-session-quit`.
- Audio/Bluetooth: `alsamixer`, `pactl`, `bluetoothctl`, `hciconfig`.
- Database CLI: `mysql`, `mysqldump`, `psql`, `pg_dump` nên đặt trong knowledge base database khi cần chi tiết.
- Cloud vendor CLI như `aws` nên đặt trong cloud/vendor operations khi cần chi tiết.
- Media/document converter như `ffmpeg`, `pandoc`, `magick`, `pdftotext` hữu ích nhưng không phải core Linux ops; chỉ ghi vào runbook cụ thể nếu workload cần.

## Checklist Trước Khi Chạy Lệnh Nguy Hiểm

- Đã xác nhận hostname, environment và path/device chưa?
- Có đang SSH vào đúng host không?
- Lệnh có xóa, format, detach, restart, reload, đổi route/firewall, đổi user access hoặc đổi boot/kernel state không?
- Có backup config hoặc data chưa?
- Có validation sau thay đổi không?
- Có rollback hoặc out-of-band access nếu mất network không?
- Có cần giữ evidence trước khi restart hoặc cleanup không?

