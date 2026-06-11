# ✅ Cài Kolla-Ansible trên Ubuntu 24.04 (Caracal 2024.1)

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
        - 192.168.91.X/24
      routes:
        - to: default
          via: 192.168.91.2
      nameservers:
        addresses:
          - 8.8.8.8
      dhcp4: false

    ens34:         #Bridge
      dhcp4: false
      optional: true

## 2. Chạy lệnh cập nhật

sudo apt update && sudo apt -y upgrade

sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io

sudo systemctl start docker
sudo systemctl enable docker

sudo apt-get install -y git python3-dev libffi-dev gcc libssl-dev pkg-config libdbus-1-dev build-essential cmake libglib2.0-dev mariadb-server

sudo apt install -y python3-venv

mkdir openstack
cd openstack/
python3 -m venv .
source bin/activate
pip install --upgrade pip
pip install setuptools docker dbus-python

#Set pasword for all

sudo EDITOR=nano visudo

// kéo xuống cuối file r ghi đè (tên user) ALL=(ALL) NOPASSWD:ALL


## 3. Cài đúng version ansible + kolla-ansible Caracal (2024.2)

pip install 'ansible-core>=2.15,<2.16'


#clone repo rồi xem các tag/branches:

git clone https://opendev.org/openstack/kolla-ansible
cd kolla-ansible
git branch -a
git checkout stable/2024.2
pip install .

## 4. Copy file cấu hình mẫu
sudo mkdir -p /etc/kolla

sudo chown $USER:$USER /etc/kolla

cp -r ~/openstack/share/kolla-ansible/etc_examples/kolla/* /etc/kolla

cp ~/openstack/share/kolla-ansible/ansible/inventory/all-in-one .


## 5. Sinh password + chỉnh cấu hình

kolla-genpwd

sudo nano /etc/kolla/globals.yml


#Sửa file cấu hình : sudo nano /etc/kolla/globals.yml

kolla_base_distro: "ubuntu"
openstack_release: "2024.2"
kolla_internal_vip_address: "192.168.1.149"   # VIP mgmt(chọn 1 địa chỉ IP chưa dùng trong VM và có cùng dải địa chỉ với NAT)
network_interface: "ens33"                   # NIC mgmt
neutron_external_interface: "ens34"        # NIC external
nova_compute_virt_type: "qemu"                # vì chạy trên VM
enable_horizon: "yes"


## 6. Deploy    

kolla-ansible install-deps

kolla-ansible bootstrap-servers -i ./all-in-one

kolla-ansible prechecks -i ./all-in-one

kolla-ansible deploy -i ./all-in-one

kolla-ansible post-deploy -i ./all-in-one


## 7. OpenStack client + init

pip install python-openstackclient -c https://releases.openstack.org/constraints/upper/2024.1

./share/kolla-ansible/init-runonce

#Lấy tài khoản mật khẩu đăng nhập và kiểm tra dịch vụ Openstack

cd /etc/kolla/
ls
cat clouds.yaml

source /etc/kolla/admin-openrc.sh
