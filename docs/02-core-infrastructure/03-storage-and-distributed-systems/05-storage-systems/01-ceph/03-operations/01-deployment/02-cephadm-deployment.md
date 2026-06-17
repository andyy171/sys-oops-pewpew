# Triển khai một cụm ceph 3 node nhanh với cephadm
## 1. Chuẩn bị

- 3 node ceph 

1. Setup host name :
```bash
# Trên từng node, set hostname tương ứng
hostnamectl set-hostname ceph-node01   # ceph02, ceph03 tương tự

# Thêm vào /etc/hosts trên cả 3 node
cat <<EOF | sudo tee /etc/hosts
127.0.0.1 localhost
[IP_NODE_1] ceph-node01
[IP_NODE_2] ceph-node02
[IP_NODE_3] ceph-node03
EOF


## Xóa các file do cloud-init sinh ra
sudo rm -f /etc/netplan/50-cloud-init.yaml
sudo rm -f /etc/netplan/90-installer-network.yaml
sudo cloud-init clean --logs
cat << EOF | sudo tee /etc/netplan/01-netcfg.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens33:
      dhcp4: true
    ens37:
      dhcp4: no
      addresses:
        - [IP_NODE_1]/24
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
EOF

sudo chmod 600 /etc/netplan/01-netcfg.yaml
sudo netplan apply
```

2. Tắt swap
```bash
swapoff -a
sed -i '/swap/d' /etc/fstab
```

3. Cài đặt package
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip vim podman htop lvm2 net-tools chrony curl openssh-server

systemctl enable --now chrony ssh

curl -LO https://download.ceph.com/rpm-19.2.3/el9/noarch/cephadm

chmod +x cephadm
sudo mv cephadm /usr/local/bin/
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.ceph.com/keys/release.asc | gpg --dearmor | sudo tee /etc/apt/keyrings/ceph.gpg > /dev/null

echo "deb [signed-by=/etc/apt/keyrings/ceph.gpg] https://download.ceph.com/debian-squid/ $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/ceph.list

sudo apt update && sudo apt install -y ceph-common=19.2.3-*

```

- Đặt password root trên các node
```bash
sudo passwd root # 3node 
```

## 2. Bootstrap Cluster
- Bootstrap cluster
```bash
cephadm bootstrap --mon-ip [IP_NODE_1] --initial-dashboard-user admin --initial-dashboard-password 'YourStrongPass123!' --dashboard-password-noupdate --ssh-user root --allow-fqdn-hostname

## CHỈ dùng --cluster-network [INTERNAL_NETWORK]/24 nếu có network riêng cho replication (cluster network)

# Copy public key to other nodes
ssh-copy-id -f -i /etc/ceph/ceph.pub root@ceph-node02
ssh-copy-id -f -i /etc/ceph/ceph.pub root@ceph-node03

# Verify
ceph -s
ceph orch status

## Dashboard
 https://[IP_NODE_1]:8443/
```
- Add node
```bash

# Add node
ceph orch host add ceph-node02 <IP_NODE2>
ceph orch host add ceph-node03 <IP_NODE3>

ceph orch host ls
ceph orch host label add ceph-node01 _admin

```

Triển khai monitor , manager 
```bash
ceph orch apply mon --placement="ceph-node01,ceph-node02,ceph-node03"
ceph mon stat

ceph orch apply mgr --placement="ceph-node01,ceph-node02,ceph-node03"
ceph mgr stat
```

Kiểm tra disk
```bash
ceph orch device ls --wide
lsblk 

# Wipe disk cụ thể trên node cụ thể nếu cần
ceph orch device zap ceph-node01 /dev/sdb --force
# Repeat cho ceph02, ceph03
```

Triển khai OSD
```bash
cat > osd-spec.yaml <<EOF
service_type: osd
service_id: osd-default
placement:
  hosts:
    - ceph-node01
    - ceph-node02
    - ceph-node03
spec:
  data_devices:
    rotational: 1
EOF

ceph orch apply -i osd-spec.yaml
```

## Cấu hình cho cluster sau khi deploy 
- Cấu hình cluster cơ bản
```bash
ceph osd pool set .mgr size 3
ceph osd pool set .mgr min_size 0

ceph config set global osd_pool_default_size 3
ceph config set global osd_pool_default_min_size 0

ceph config set osd osd_op_threads 8
ceph config set osd osd_disk_threads 4
ceph config set osd osd_recovery_max_active_hdd 3
ceph config set osd osd_max_backfills 2

# ceph config set osd osd_scrub_begin_hour 2
# ceph config set osd osd_scrub_end_hour 6

```

- Encable các module quan trọng :
```bash
ceph mgr module enable dashboard
ceph mgr module enable prometheus
```

- Verify 
```bash
ceph health detail
ceph osd tree
ceph orch ps
```


## Cấu hình kết nối Openstack 
- Tạo pool test 
```bash
# Tạo pool với pg_num tính toán
ceph osd pool create volumes 8
ceph osd pool create images 8
ceph osd pool create vms 8


ceph osd pool set volumes size 3
ceph osd pool set volumes min_size 0
ceph osd pool set volumes pg_autoscale_mode on
ceph osd pool application enable volumes rbd

ceph osd pool set images size 3
ceph osd pool set images min_size 0
ceph osd pool set images pg_autoscale_mode on
ceph osd pool application enable images rbd

ceph osd pool set vms size 3
ceph osd pool set vms min_size 0
ceph osd pool set vms pg_autoscale_mode on
ceph osd pool application enable vms rbd
```

## Lab Safety Notes

Các bước trong `_inbox/Báo cáo thực tập - Quản trị cơ bản Ceph...md` và `_inbox/Ceph Install notes.md` có nhiều lệnh phù hợp cho lab, nhưng khi đưa vào note canonical cần giữ một số nguyên tắc:

- Không dùng password dashboard mặc định hoặc password yếu ngoài lab.
- Không bật root password login lâu dài; chỉ dùng tạm để bootstrap nếu lab cần, sau đó chuyển về SSH key và tắt password authentication.
- Trước khi `zap`, `destroy`, `purge`, `pool delete`, luôn xác nhận đúng node/disk/pool và có backup hoặc dữ liệu test.
- Với cluster ít OSD, tránh đặt `min_size = 0` trong môi trường có dữ liệu thật; lab có thể dùng để quan sát hành vi, production cần chính sách an toàn hơn.
- Sau bootstrap, luôn verify bằng `ceph -s`, `ceph health detail`, `ceph orch ps`, `ceph osd tree` và dashboard.

## Basic Lab Workflows

### RADOS Object Test

```bash
ceph osd pool create testpool 32
ceph osd pool application enable testpool rados

echo "hello ceph" > /tmp/hello.txt
rados -p testpool put myobj /tmp/hello.txt
rados -p testpool ls
rados -p testpool get myobj /tmp/hello-rcvd.txt
rados -p testpool rm myobj
```

### RBD Pool, Image, Map

```bash
ceph osd pool create rbdtest 32 32
rbd pool init rbdtest

rbd create rbdtest/testing --size 1G
rbd info rbdtest/testing
rbd map rbdtest/testing
mkfs.ext4 /dev/rbd0
mkdir -p /mnt/rbdtest
mount /dev/rbd0 /mnt/rbdtest

echo "Ceph RBD test OK" > /mnt/rbdtest/test.txt
cat /mnt/rbdtest/test.txt

umount /mnt/rbdtest
rbd unmap /dev/rbd0
```

### Snapshot, Clone, Resize

```bash
rbd snap create rbdtest/testing@snap1
rbd snap protect rbdtest/testing@snap1
rbd clone rbdtest/testing@snap1 rbdtest/testing-clone
rbd flatten rbdtest/testing-clone
rbd resize --size 2G rbdtest/testing
rbd snap ls rbdtest/testing
```

### CephFS Smoke Test

```bash
ceph fs volume create myfs
ceph fs ls

mkdir -p /mnt/cephfs
mount -t ceph :/ /mnt/cephfs -o name=admin
echo "cephfs ok" > /mnt/cephfs/test.txt
cat /mnt/cephfs/test.txt
umount /mnt/cephfs
```

### RGW Smoke Test

```bash
ceph orch apply rgw rgw --placement="1 ceph-node01"
ceph orch ps --daemon_type rgw

radosgw-admin user create --uid="lab-user" --display-name="Lab User"
```

Nếu dùng AWS CLI để test RGW/S3 API, lưu access key và secret key trong secret manager hoặc file tạm ngoài repo; không commit key vào knowledge base.

## Common RBD Pool Error

Triệu chứng:

```text
rbd: error opening pool 'rbdpool': (2) No such file or directory
```

Nguyên nhân thường gặp:

- Pool chưa được tạo.
- Gõ sai tên pool.
- Đang chạy ngoài `cephadm shell` nhưng host thiếu `ceph.conf` hoặc keyring.
- Pool đã tạo nhưng chưa `rbd pool init`.

Checklist xử lý:

```bash
ceph -s
ceph osd pool ls
ceph osd pool create rbdpool 32 32
rbd pool init rbdpool
rbd ls rbdpool
```

Nếu đứng ngoài shell:

```bash
sudo cephadm shell -- rbd pool init rbdpool
```
