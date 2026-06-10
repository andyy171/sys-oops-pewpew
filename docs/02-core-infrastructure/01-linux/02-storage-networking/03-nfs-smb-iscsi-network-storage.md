# NFS, SMB/CIFS và iSCSI Network Storage

## 1. Network Storage Overview

Network storage cho phép host truy cập dữ liệu qua mạng thay vì local disk.

| Công nghệ | Mô hình | Use case |
| --- | --- | --- |
| NFS | File-level, Unix/Linux native | Shared directory giữa Linux hosts |
| SMB/CIFS | File-level, Windows-friendly | Windows/Linux file sharing |
| iSCSI | Block-level qua TCP/IP | Expose block device cho host |

Khác biệt quan trọng:

- NFS/SMB share filesystem qua mạng.
- iSCSI expose block device; client phải tự tạo filesystem/mount.

## 2. NFS

NFSv3 thường dựa nhiều vào RPC service phụ trợ và UID/GID mapping đơn giản. NFSv4 gom nhiều chức năng hơn qua một port chính, hỗ trợ namespace/export hiện đại hơn và thường dễ vận hành qua firewall hơn. Khi troubleshoot, luôn kiểm tra version client/server đang thương lượng.

### Server

```bash
# Debian/Ubuntu
sudo apt install nfs-kernel-server

# RHEL/CentOS/Fedora
sudo dnf install nfs-utils
```

Export directory:

```bash
sudo mkdir -p /srv/nfs/share
sudo chown nobody:nogroup /srv/nfs/share 2>/dev/null || true
```

`/etc/exports`:

```text
/srv/nfs/share 10.0.0.0/24(rw,sync,no_subtree_check)
```

Apply:

```bash
sudo exportfs -rav
sudo exportfs -v
sudo systemctl enable --now nfs-server
```

### Client

```bash
sudo apt install nfs-common
sudo dnf install nfs-utils
showmount -e <nfs-server>
sudo mkdir -p /mnt/nfs
sudo mount -t nfs <nfs-server>:/srv/nfs/share /mnt/nfs
```

`fstab`:

```text
<nfs-server>:/srv/nfs/share /mnt/nfs nfs defaults,_netdev,nofail 0 0
```

## 3. SMB/CIFS Client Mount

Install client:

```bash
sudo apt install cifs-utils
sudo dnf install cifs-utils
```

Mount thủ công:

```bash
sudo mkdir -p /mnt/smb
sudo mount -t cifs //fileserver/share /mnt/smb \
  -o username=your-username,domain=EXAMPLE,vers=3.0
```

Credential file:

```bash
sudo install -m 600 /dev/null /etc/samba/creds-fileserver
sudo editor /etc/samba/creds-fileserver
sudo chmod 600 /etc/samba/creds-fileserver
```

Nội dung:

```text
username=your-username
password=your-password
domain=EXAMPLE
```

`fstab`:

```text
//fileserver/share /mnt/smb cifs credentials=/etc/samba/creds-fileserver,vers=3.0,_netdev,nofail,uid=1000,gid=1000 0 0
```

Không hardcode password trực tiếp trong `/etc/fstab`; dùng credential file quyền `600` hoặc cơ chế Kerberos/secret manager phù hợp.

Nếu môi trường dùng Kerberos:

```bash
kinit user@EXAMPLE.COM
sudo mount -t cifs //fileserver/share /mnt/smb -o sec=krb5,cruid=$(id -u),vers=3.0
```

## 4. Samba Server

Install:

```bash
sudo apt install samba
sudo dnf install samba samba-client
```

Tạo share:

```bash
sudo mkdir -p /srv/samba/share
sudo chown -R nobody:nogroup /srv/samba/share 2>/dev/null || true
```

`/etc/samba/smb.conf`:

```ini
[share]
   path = /srv/samba/share
   browsable = yes
   writable = yes
   guest ok = no
   valid users = @smbusers
```

User:

```bash
sudo groupadd smbusers
sudo usermod -aG smbusers <username>
sudo smbpasswd -a <username>
sudo testparm
sudo systemctl enable --now smb nmb 2>/dev/null || sudo systemctl enable --now smbd nmbd
```

## 5. iSCSI Target và Initiator

iSCSI gồm:

- Target: server expose block device.
- Initiator: client kết nối và thấy block device.

### Initiator

```bash
sudo apt install open-iscsi
sudo dnf install iscsi-initiator-utils
sudo systemctl enable --now iscsid
```

Discovery:

```bash
sudo iscsiadm -m discovery -t sendtargets -p <target-ip>
```

Login:

```bash
sudo iscsiadm -m node -T <iqn> -p <target-ip> --login
sudo iscsiadm -m session
sudo iscsiadm -m node
lsblk
```

Logout:

```bash
sudo iscsiadm -m node -T <iqn> -p <target-ip> --logout
```

Chỉ delete node record khi chắc chắn không còn filesystem/service đang dùng block device đó:

```bash
sudo iscsiadm -m node -T <iqn> -p <target-ip> --op delete
```

Production notes:

- Với iSCSI multipath, cấu hình `multipathd` thay vì mount trực tiếp một path.
- Không mount cùng một filesystem read-write từ nhiều initiator nếu filesystem không hỗ trợ cluster.
- iSCSI block device cần backup/ownership lifecycle như local disk.

## 6. fstab và Boot-safe Mount Options

Network mount có thể làm boot chậm/hỏng nếu network chưa sẵn sàng.

NFS:

```text
server:/export /mnt/nfs nfs defaults,_netdev,nofail,x-systemd.automount 0 0
```

CIFS:

```text
//server/share /mnt/smb cifs credentials=/etc/samba/creds,_netdev,nofail,x-systemd.automount,vers=3.0 0 0
```

Gợi ý:

- `_netdev`: đánh dấu mount phụ thuộc network.
- `nofail`: không fail boot nếu mount lỗi.
- `x-systemd.automount`: mount khi có truy cập, giảm rủi ro boot.
- Thiếu các option này có thể làm boot chậm hoặc treo khi storage/network chưa sẵn sàng.

## 7. Troubleshooting

### NFS

```bash
showmount -e <server>
rpcinfo -p <server>
exportfs -v
journalctl -u nfs-server
mount -v -t nfs <server>:/export /mnt/test
```

Kiểm tra firewall, export policy, UID/GID mapping và permission trên server.

### SMB/CIFS

```bash
smbclient -L //<server> -U <user>
testparm
journalctl -u smbd
mount -v -t cifs //<server>/<share> /mnt/test -o username=<user>,vers=3.0
```

Kiểm tra domain, protocol version, credential, path share và SELinux context nếu server là Linux.

### iSCSI

```bash
iscsiadm -m session
iscsiadm -m node
journalctl -u iscsid
dmesg -T | tail -100
lsblk
multipath -ll
```

Kiểm tra target IP/port `3260`, IQN, CHAP, network path và multipath.
