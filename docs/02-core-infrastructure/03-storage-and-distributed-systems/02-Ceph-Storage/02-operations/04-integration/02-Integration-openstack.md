# Tích hợp Ceph với Openstack

> Hướng dẫn này giúp tích hợp Ceph làm backend lưu trữ cho OpenStack, bao gồm Glance (images), Cinder (volumes/backups), và Nova (vms). Các bước được thực hiện trên các node Ceph và Kolla, đảm bảo quyền truy cập root và cấu hình keyring để OpenStack có thể kết nối an toàn với Ceph.

## Cấu Hình Root Access
Cấu hình này cho phép truy cập root qua SSH, cần thiết để copy file và chạy lệnh từ xa giữa các node mà không cần sudo lặp lại.
1. Đặt mật khẩu cho root
```bash
sudo passwd root
```
2. Bật root login SSH
Cho phép root login bằng mật khẩu qua SSH, tiện lợi cho việc copy config từ Ceph sang Kolla node (nhưng nên tắt sau khi hoàn tất để tăng bảo mật).
```bash
sudo nano /etc/ssh/sshd_config

#Thêm 2 dòng:

PermitRootLogin yes
PasswordAuthentication yes

#Lưu → restart SSH:

sudo systemctl restart ssh
```
## Tạo Pools Cho OpenStack Trên Ceph
Tạo các pool riêng biệt cho từng dịch vụ OpenStack để phân chia lưu trữ, tối ưu hóa hiệu suất và quản lý quyền truy cập.
```bash
for pool_name in volumes images backups vms
do
  ceph osd pool create $pool_name
  rbd pool init $pool_name
done
```

## Tạo Ceph Keyrings
> Tạo keyring cho từng client (Glance, Cinder, Nova) để cấp quyền truy cập cụ thể vào các pool, đảm bảo an ninh và tuân thủ nguyên tắc least privilege.

```bash
ceph auth get-or-create client.glance mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=images' -o /etc/ceph/ceph.client.glance.keyring

ceph auth get-or-create client.cinder mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=volumes, allow rwx pool=images' -o /etc/ceph/ceph.client.cinder.keyring

ceph auth get-or-create client.nova mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=vms, allow rx pool=images' -o /etc/ceph/ceph.client.nova.keyring

ceph auth get-or-create client.cinder-backup mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=backups' -o /etc/ceph/ceph.client.cinder-backup.keyring
```


### Kiểm Tra Ceph
> Kiểm tra trạng thái Ceph để xác nhận pools và keyrings đã tạo thành công, tránh lỗi tích hợp sau này.
```bash
ceph status; ceph osd tree; ceph df
ceph orch ps; ceph osd pool ls
ls -lh /etc/ceph/
```

## Cấu Hình Trên Node Kolla (Chạy Dưới Quyền Root)
> Thực hiện trên node Kolla để copy config từ Ceph và cập nhật Kolla, cho phép OpenStack sử dụng Ceph làm backend.
### Tạo Thư Mục Config
mkdir /etc/kolla/config
mkdir /etc/kolla/config/nova
mkdir /etc/kolla/config/glance
mkdir -p /etc/kolla/config/cinder/cinder-volume
mkdir /etc/kolla/config/cinder/cinder-backup

### Copy Files Từ Node Ceph
> Copy ceph.conf và keyrings từ node Ceph (ví dụ: ceph1) sang Kolla để các dịch vụ có thể kết nối (sửa ceph.conf nếu có lỗi tab/khoảng trắng trước khi copy).

Chạy trên node Ceph:
```bash
scp -r /etc/ceph/ root@$node:/etc/
```
Chạy trên node Kolla:
```bash
cp /etc/ceph/ceph.conf /etc/kolla/config/cinder/
cp /etc/ceph/ceph.conf /etc/kolla/config/nova/
cp /etc/ceph/ceph.conf /etc/kolla/config/glance/
cp /etc/ceph/ceph.client.glance.keyring /etc/kolla/config/glance/
cp /etc/ceph/ceph.client.nova.keyring /etc/kolla/config/nova/
cp /etc/ceph/ceph.client.cinder.keyring /etc/kolla/config/nova/
cp /etc/ceph/ceph.client.cinder.keyring /etc/kolla/config/cinder/cinder-volume/
cp /etc/ceph/ceph.client.cinder.keyring /etc/kolla/config/cinder/cinder-backup/
cp /etc/ceph/ceph.client.cinder-backup.keyring /etc/kolla/config/cinder/cinder-backup/
```


### Cấu Hình Globals.yml

> Thêm biến vào globals.yml (hoặc file config tương ứng) để kích hoạt Ceph backend cho Glance, Cinder, Nova.

Thêm vào file `sudo nano /etc/kolla/globals.yml`:
```bash
enable_cinder: "yes"
ceph_glance_user: "glance"
ceph_glance_keyring: "client.glance.keyring"
ceph_glance_pool_name: "images"
ceph_cinder_user: "cinder"
ceph_cinder_keyring: "client.cinder.keyring"
ceph_cinder_pool_name: "volumes"
ceph_cinder_backup_user: "cinder-backup"
ceph_cinder_backup_keyring: "client.cinder-backup.keyring"
ceph_cinder_backup_pool_name: "backups"
ceph_nova_keyring: "client.nova.keyring"
ceph_nova_user: "nova"
ceph_nova_pool_name: "vms"
glance_backend_ceph: "yes"
cinder_backend_ceph: "yes"
nova_backend_ceph: "yes"
```
### Áp dụng thay đổi 
```bash
kolla-ansible -i all-in-one reconfigure
kolla-ansible reconfigure -i all-in-one
```
