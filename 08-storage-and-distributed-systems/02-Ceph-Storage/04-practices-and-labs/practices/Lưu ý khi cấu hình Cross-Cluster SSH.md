# Mục lục 


# Mục tiêu

Thiết lập SSH key-based authentication giữa các node của hai cụm A → B (hoặc hai chiều), phục vụ các thao tác copy file cấu hình và keyring.

# Các bước thực hiện 
## Tạo SSH Key riêng cho cross-cluster
```bash
ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519_mirror -C "cross-cluster-mirror"
```
Key tạo riêng giúp tách biệt với key của cụm nội bộ.

## Copy public key sang node đích

Sử dụng ssh-copy-id:
```bash
ssh-copy-id -i /root/.ssh/id_ed25519_mirror.pub root@nodeB
```

Hoặc thủ công : 
```bash
cat /root/.ssh/id_ed25519_mirror.pub
# copy nội dung → paste vào nodeB:
/root/.ssh/authorized_keys
```

## Thiết lập đủ quyền hạn cho file 
```bash
chmod 700 /root/.ssh
chmod 600 /root/.ssh/authorized_keys
chown root:root /root/.ssh -R
```

SSH config tối thiểu hoạt động với key:
- `PermitRootLogin prohibit-password` OK
- `PubkeyAuthentication yes` thường là default (dù có dòng #)
- Không cần sửa `AuthorizedKeysFile` nếu dùng mặc định `.ssh/authorized_keys`

## Kiểm tra key login bằng lệnh chỉ định key
```bash
ssh -i /root/.ssh/id_ed25519_mirror root@node5.ceph.local # có thể thay bằng hostname khác
```
