# Tích hợp Ceph với Openstack

## 1. Tích hợp Glance với Ceph 

Trên Ceph : 
- Tạo pool trên ceph 
ceph osd pool create images 128 128
rbd pool init images
ceph osd pool application enable images rbd

- Tạo user keyring cho pool :
ceph auth get-or-create client.glance mon 'profile rbd' osd 'profile rbd pool=images' -o /tmp/ceph.client.glance.keyring

// ceph fsid 
// cat /etc/ceph/ceph.conf
```
[global]
fsid = 4013f349-c4ba-11f0-baa6-000c294aff60
mon_host = [v2:192.168.56.101:3300/0,v1:192.168.56.101:6789/0] [v2:192.168.56.102:3300/0,v1:192.168.56.102:6789/0] [v2:192.168.56.103:3300/0,v1:192.168.56.103:6789/0]

auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx

```

Trên Openstack:
sudo mkdir -p /etc/kolla/config/glance

- Chỉnh sửa `/etc/kolla/globals.yml`:
```yaml
glance_backend_file: "no"
glance_backend_ceph: "yes"
glance_api_image_data_store: "rbd"

ceph_glance_user: "glance"
ceph_glance_pool_name: "images"
ceph_glance_keyring: "client.glance.keyring"
ceph_glance_conf_path: "/etc/ceph/ceph.conf"
```
- Copy `ceph.conf` và keyring từ cụm Ceph sang 
scp /etc/ceph/ceph.conf ubuntu@192.168.198.165:/tmp/ceph.conf
scp ceph.client.glance.keyring  ubuntu@192.168.198.165:/tmp/ceph.client.glance.keyring

- Di chuyển keyring vào folder config và set permission
sudo mv /tmp/ceph.conf /etc/kolla/config/glance/ceph.conf
sudo mv /tmp/ceph.client.glance.keyring /etc/kolla/config/glance/ceph.client.glance.keyring

// check ls -l 

- Đặt lại quyền hạn 
sudo chown $USER:root /etc/kolla/config/glance/ceph.client.glance.keyring
sudo chmod 640 /etc/kolla/config/glance/ceph.client.glance.keyring
sudo chown $USER:root /etc/kolla/config/glance/ceph.conf
sudo chmod 644 /etc/kolla/config/glance/ceph.conf
cat <<EOF | sudo tee /etc/kolla/config/glance/glance-api.conf
[glance_store]
stores = rbd
default_backend = rbd
default_store = rbd

[rbd]
rbd_store_pool = images
rbd_store_user = glance
rbd_store_ceph_conf = /etc/ceph/ceph.conf
rbd_store_chunk_size = 8
rados_connect_timeout = 5
EOF

- Reconfigure:
kolla-ansible -i all-in-one -t glance reconfigure

kolla-ansible reconfigure -i all-in-one -t glance
- Test 
source /etc/kolla/admin-openrc.sh

wget https://download.cirros-cloud.net/0.6.3/cirros-0.6.3-x86_64-disk.img -O /tmp/cirros.img

openstack image create "Cirros-Ceph-Test2" \
  --container-format bare \
  --disk-format qcow2 \
  --min-disk 1 --min-ram 512 \
  --file /tmp/cirros.img