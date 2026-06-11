# Triển khai 1 cụm OpenStack đơn giản với Ceph

> Nếu cần dựng lab all-in-one bằng Kolla-Ansible, xem thêm [Kolla-Ansible All-In-One Lab](./kolla-ansible-all-in-one-lab.md). Trang hiện tại giữ vai trò checklist triển khai OpenStack đơn giản với Ceph, còn trang Kolla AIO đi sâu vào setup lab một node.

## Hạ tầng khuyến nghị 
- Controller Node : CPU 16+ cores , RAM 64GB+ , Storage nhanh ( SSD/NVMe) , Network 10Gbps+
- Compute Node : CPU tùy theo workload  , RAM tùy theo yêu cầu máy ảo , Storage có thể là SSD/HDD cho local hoặc Ceph , Network 10Gbps+
- Storage Node : Ceph OSD , Storage nhanh ( SSD/NVMe) , Network 10Gbps+


## Steps
1. Chuẩn bị 
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip chrony

sudo timedatectl set-timezone UTC
sudo systemctl enable --now chronyd

```
Ngoài setup OS còn chuẩn bị 
- tách network:
    - management
    - storage
    - external
- sync time (NTP) → cực quan trọng cho cluster
- chuẩn bị disk (RAID / NVMe)

2. Install Kolla-Ansible
```bash
sudo apt install python3-pip
sudo pip install kolla-ansible

```


3. Config file global.yml:
```yml
kolla_base_distro: "ubuntu"
network_interface: "eth0"
neutron_external_interface: "eth1"
kolla_internal_vip_address: "10.10.10.254"
```

4. Deploy OpenStack:
```bash
kolla-ansible bootstrap-servers
kolla-ansible prechecks
kolla-ansible deploy
```

5. Verify 
```bash
kolla-ansible post-deploy
source /etc/kolla/admin-openrc.sh

openstack service list
openstack compute service list --service nova-compute
```

6. Network & Identity
Sau khi control plane chạy, bước tiếp theo không phải tạo VM ngay, mà là phải xây network và identity model.
```bash
openstack network create private-net
openstack subnet create --network private-net --subnet-range 192.168.1.0/24 private-subnet

openstack router create main-router
openstack router set --external-gateway public-net main-router
openstack router add subnet main-router private-subnet


openstack security group create secure-group
openstack security group rule create --proto tcp --dst-port 22 secure-group



keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
keystone-manage credential_setup --keystone-user keystone --keystone-group keystone


openstack role create admin
openstack user create --password-prompt cloud-admin
openstack role add --project service --user cloud-admin admin

```

7. Validation
```bash
openstack flavor create --id 0 --vcpus 1 --ram 64 --disk 1 m1.nano
openstack server create --flavor m1.nano --image cirros --network private validation-instance

openstack compute service list
openstack hypervisor list
```

8. Deploy thử VM
```bash
openstack flavor create --id 1 --vcpus 4 --ram 8192 --disk 80 production-small

openstack keypair create --public-key ~/.ssh/id_rsa.pub prod-key

openstack server create \
  --flavor production-small \
  --image ubuntu-20.04 \
  --security-group default \
  --key-name prod-key \
  prod-instance-01
```


9. Tuning hệ thống
```bash
# Nova config
cpu_allocation_ratio = 1.5
ram_allocation_ratio = 1.2
disk_allocation_ratio = 1.0

```

## Related Pages

- [Kolla-Ansible All-In-One Lab](./kolla-ansible-all-in-one-lab.md)
- [OpenStack Common Commands](../common-commands.md)
- [Ceph Integration With OpenStack](../../../../../02-core-infrastructure/03-storage-and-distributed-systems/02-ceph-storage/03-operations/03-integration/02-Integration-openstack.md)
