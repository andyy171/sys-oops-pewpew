# Cài đặt 1 node All-in-one Openstack 
✅ Cài Kolla-Ansible trên Ubuntu 24.04 (Caracal 2024.1)

## 1. Chuẩn bị hệ thống

1 con VM (4vCPU + 6-8GB RAM + 1 ổ đĩa - nếu cài cinder-volumes thì thêm 1 ổ đĩa nữa vào cài PV,VG và LVM - mạng 2 card 1 NAT + 1 Bridge, cấu hình NAT IP tĩnh và Bridge ko IP)

sudo nano /etc/netplan/.....

File cấu hình ( tùy chỉnh theo tên card mạng của máy)

network:
  version: 2
  renderer: networkd
  ethernets:
    ens33:          #NAT
      addresses:
        - 192.168.150.X/24
      routes:
        - to: default
          via: 192.168.150.2
      nameservers:
        addresses:
          - 8.8.8.8
      dhcp4: false

    ens34:         #Bridge
      dhcp4: false
      optional: true

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

### Cài đúng version ansible + kolla-ansible Caracal (2024.1)

python -m pip install 'ansible-core>=2.15,<2.16'

git clone https://opendev.org/openstack/kolla-ansible
cd kolla-ansible
git fetch --all --tags
git branch -a
git checkout stable/2024.1
python -m pip install .
```
#check which kolla-ansible
```

## 4. Copy file cấu hình mẫu
sudo mkdir -p /etc/kolla
sudo chown $USER:$USER /etc/kolla

cp -r etc/kolla/* /etc/kolla
cp ansible/inventory/all-in-one ~/openstack/
cp ansible/inventory/all-in-one .

## 5. Sinh password 

kolla-genpwd
```bash
# Kiểm tra mật khẩu 
wc -l /etc/kolla/passwords.yml
head -n 30 /etc/kolla/passwords.yml
```

// ~/openstack/kolla-ansible
cp etc/kolla/passwords.yml /etc/kolla/passwords.yml
sudo chown $USER:$USER /etc/kolla/passwords.yml
sudo chmod 640 /etc/kolla/passwords.yml

## 6. Chỉnh cấu hình globals.yml
sudo nano /etc/kolla/globals.yml
#Sửa file cấu hình : sudo nano /etc/kolla/globals.yml
```
kolla_base_distro: "ubuntu"
openstack_release: "2024.1"
kolla_internal_vip_address: "192.168.150.149"   # cùng dải với NAT chưa sử dụng 
network_interface: "ens33"                   # NIC mgmt
neutron_external_interface: "ens34"        # NIC external
nova_compute_virt_type: "qemu"                
enable_horizon: "yes"
```


## 7. Deploy

kolla-ansible install-deps

kolla-ansible bootstrap-servers -i ./all-in-one

kolla-ansible prechecks -i ./all-in-one

kolla-ansible deploy -i ./all-in-one

kolla-ansible post-deploy -i ./all-in-one


## 8. OpenStack client + init

pip install python-openstackclient -c https://releases.openstack.org/constraints/upper/2024.1

#Lấy tài khoản mật khẩu đăng nhập và kiểm tra dịch vụ Openstack

cd /etc/kolla/
ls
cat clouds.yaml

source /etc/kolla/admin-openrc.sh

cd ~/openstack/kolla-ansible/tools
./init-runonce

// auto-load mỗi lần SSH ( không khuyến khích prod)
echo "source /etc/kolla/admin-openrc.sh" >> ~/.bashrc