# Kolla-Ansible All-In-One Lab

## Overview

Note này gom rough note `Kolla _ all-in-one.txt` thành một runbook lab để dựng OpenStack all-in-one bằng Kolla-Ansible. Đây là môi trường học/lab, không phải blueprint production. Các IP, interface và release trong ví dụ cần được thay theo lab thật.

Ví dụ nguồn dùng Ubuntu 24.04 và OpenStack/Kolla nhánh 2024.2, trong khi phần mô tả có nhắc Caracal 2024.1. Khi làm thật, phải chọn một release duy nhất và kiểm tra lại matrix tương thích giữa OS, Python, Ansible, Kolla-Ansible và OpenStack release.

## Lab Topology

Khuyến nghị tối thiểu cho VM lab:

| Thành phần | Khuyến nghị |
|---|---|
| CPU | 4 vCPU trở lên |
| RAM | 6-8 GB trở lên |
| Disk | Một disk hệ điều hành, thêm disk riêng nếu thử Cinder LVM |
| NIC 1 | NAT/management, có IP tĩnh |
| NIC 2 | External/provider bridge, thường không đặt IP trên host |

Ví dụ interface từ rough note:

```text
ens33: management/NAT, ví dụ 192.168.1.149/24
ens34: external/provider network, dùng cho Neutron external interface
```

## Chuẩn Bị Network

Ví dụ netplan cho lab hai NIC:

```yaml
network:
  version: 2
  ethernets:
    ens33:
      dhcp4: false
      addresses:
        - 192.168.1.149/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 1.1.1.1
    ens34:
      dhcp4: false
      optional: true
```

Apply và kiểm tra:

```bash
sudo netplan apply
ip addr show
ip route
```

## Cài Docker Và Dependency

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release git python3-dev python3-pip python3-venv build-essential libffi-dev libssl-dev pkg-config
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

Với lab cá nhân, có thể thêm user hiện tại vào group `docker`. Với production, cần quản lý quyền Docker cẩn thận vì quyền này gần tương đương root.

```bash
sudo usermod -aG docker "$USER"
```

## Tạo Python Virtual Environment

```bash
mkdir -p ~/openstack
cd ~/openstack
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools wheel
pip install "ansible-core>=2.15,<2.16" docker dbus-python
```

Nếu dùng sudo không cần password trong lab, ghi rõ đây là lab-only:

```bash
sudo visudo
```

Ví dụ:

```text
<USER> ALL=(ALL) NOPASSWD:ALL
```

Không dùng cấu hình này cho production nếu chưa có kiểm soát truy cập, audit và hardening phù hợp.

## Cài Kolla-Ansible

```bash
cd ~/openstack
git clone https://opendev.org/openstack/kolla-ansible.git
cd kolla-ansible
git checkout stable/2024.2
pip install .
```

Chuẩn bị cấu hình:

```bash
sudo mkdir -p /etc/kolla
sudo cp -r etc/kolla/* /etc/kolla/
sudo cp ansible/inventory/all-in-one ~/openstack/all-in-one
kolla-genpwd
sudo cp /etc/kolla/passwords.yml /etc/kolla/passwords.yml.bak
```

## globals.yml Tối Thiểu

Ví dụ lab:

```yaml
kolla_base_distro: "ubuntu"
openstack_release: "2024.2"
kolla_internal_vip_address: "192.168.1.149"
network_interface: "ens33"
neutron_external_interface: "ens34"
nova_compute_virt_type: "qemu"
enable_horizon: "yes"
```

Lưu ý:

- `kolla_internal_vip_address` trong all-in-one có thể trỏ về IP management của node lab.
- `neutron_external_interface` không nên có IP host nếu dùng làm provider bridge.
- `nova_compute_virt_type: qemu` phù hợp khi nested virtualization chưa bật; nếu có KVM thật, kiểm tra lại `/dev/kvm`.

## Deploy

```bash
source ~/openstack/.venv/bin/activate
kolla-ansible install-deps
kolla-ansible -i ~/openstack/all-in-one bootstrap-servers
kolla-ansible -i ~/openstack/all-in-one prechecks
kolla-ansible -i ~/openstack/all-in-one deploy
kolla-ansible -i ~/openstack/all-in-one post-deploy
```

Sau deploy:

```bash
source /etc/kolla/admin-openrc.sh
openstack service list
openstack compute service list
openstack network agent list
```

Nếu cần chạy init demo resource:

```bash
/usr/local/share/kolla-ansible/init-runonce
```

## Troubleshooting Nhanh

```bash
docker ps
docker logs <container-name>
kolla-ansible -i ~/openstack/all-in-one prechecks
openstack endpoint list
openstack token issue
```

Các lỗi thường gặp:

- Sai interface trong `globals.yml`: Neutron external network không hoạt động.
- Host chưa resolve hostname chính nó: Ansible/Kolla task lỗi bất thường.
- Thiếu RAM/disk: container restart hoặc service timeout.
- Không có `/dev/kvm`: Nova cần dùng `qemu` hoặc bật nested virtualization.
- Source sai RC file: OpenStack CLI trả `401` hoặc endpoint không đúng.

## Related Pages

- [Deployment](./deployment.md)
- [OpenStack Common Commands](../common-commands.md)
- [OpenStack Client Debug](../../04-troubleshooting/openstack-client-debug.md)
- [Ceph Integration With OpenStack](../../../../../02-core-infrastructure/03-storage-and-distributed-systems/02-ceph-storage/03-operations/03-integration/02-Integration-openstack.md)
