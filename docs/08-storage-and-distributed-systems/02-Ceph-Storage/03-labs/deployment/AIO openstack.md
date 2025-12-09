#  —  Cài đặt 1 node All-in-one Openstack 
✅ Cài Kolla-Ansible trên Ubuntu 24.04 (Caracal 2024.1)

## 1. Chuẩn bị hệ thống

1 con VM (4vCPU + 6-8GB RAM + 1 ổ đĩa - nếu cài cinder-volumes thì thêm 1 ổ đĩa nữa vào cài PV,VG và LVM - mạng 2 card 1 NAT + 1 Bridge, cấu hình NAT IP tĩnh và Bridge ko IP)

echo "network: {config: disabled}" | sudo tee /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg

## Xóa các file do cloud-init sinh ra
sudo rm -f /etc/netplan/50-cloud-init.yaml
sudo rm -f /etc/netplan/90-installer-network.yaml
## File cấu hình ( tùy chỉnh theo tên card mạng của máy)
cat << EOF | sudo tee /etc/netplan/01-netcfg.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens33:
      addresses:
        - 192.168.198.167/24
      routes:
        - to: 0.0.0.0/0
          via: 192.168.198.2
      nameservers:
        addresses:
          - 8.8.8.8
      dhcp4: false

    ens34:
      dhcp4: false
      optional: true
EOF

sudo chmod 600 /etc/netplan/01-netcfg.yaml
sudo chown root:root /etc/netplan/01-netcfg.yaml


sudo netplan generate
sudo netplan apply


## 2. Chạy lệnh cập nhật

sudo apt update && sudo apt -y upgrade

#Set pasword for all

sudo EDITOR=nano visudo

// Ghi thêm cuối file 

(tên user) ALL=(ALL) NOPASSWD:ALL

sudo apt install python3.12-venv git ceph-common -y


## 3. Cài Kolla-Ansible

mkdir ~/openstack && cd ~/openstack

python3 -m venv .

source bin/activate

python -m pip install --upgrade pip

### Cài đúng version ansible + kolla-ansible (2025.1)

python -m pip install 'ansible-core>=2.15,<2.16'

cd ~/openstack
git clone https://opendev.org/openstack/kolla-ansible
cd kolla-ansible
git fetch --all --tags
git branch -a
git checkout stable/2025.1
python -m pip install .
```
#check which kolla-ansible
```

## 4. Copy file cấu hình mẫu
sudo mkdir -p /etc/kolla
sudo chown $USER:$USER /etc/kolla
cd ~/openstack/kolla-ansible
cp -r etc/kolla/* /etc/kolla
cp ansible/inventory/all-in-one ~/openstack/all-in-one
ls ~/openstack

```python
bin/  kolla-ansible/  all-in-one  share/  lib/  ...

```

## 5. Sinh password 
kolla-genpwd -p /etc/kolla/passwords.yml
sudo chown $USER:$USER /etc/kolla/passwords.yml
sudo chmod 640 /etc/kolla/passwords.yml

```bash
# Kiểm tra mật khẩu 
wc -l /etc/kolla/passwords.yml
head -n 20 /etc/kolla/passwords.yml
```
## 6. Chỉnh cấu hình globals.yml
sudo nano /etc/kolla/globals.yml
```
kolla_base_distro: "ubuntu"
openstack_release: "2025.1"

kolla_internal_vip_address: "192.168.198.149"

network_interface: "ens33"
neutron_external_interface: "ens34"

nova_compute_virt_type: "qemu"

enable_horizon: "yes"

```


## 7. Deploy
cd ~/openstack
source bin/activate
kolla-ansible install-deps

kolla-ansible bootstrap-servers -i ./all-in-one
kolla-ansible prechecks -i ./all-in-one
kolla-ansible deploy -i ./all-in-one

kolla-ansible post-deploy -i ./all-in-one


## 8. OpenStack client + init

pip install python-openstackclient -c https://releases.openstack.org/constraints/upper/2024.1


### Lấy tài khoản mật khẩu đăng nhập và kiểm tra dịch vụ Openstack

cd /etc/kolla/
ls
cat clouds.yaml

source /etc/kolla/admin-openrc.sh

cd ~/openstack/kolla-ansible/tools
./init-runonce



// auto-load mỗi lần SSH ( không khuyến khích prod)
echo "source /etc/kolla/admin-openrc.sh" >> ~/.bashrc