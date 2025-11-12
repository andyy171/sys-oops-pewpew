Triển khai Ceph All-in-one (Quincy/Reef) - CentOS 9 / Ubuntu 24.04
---
# Mục lục 


---

# Chuẩn bị và Yêu cầu
Sử dụng 1 Node, chạy CentOS Stream 9 hoặc Ubuntu Server 24.04 LTS (64bit).

| Thành phần | Yêu cầu tối thiểu | Vai trò |
|---|---|---|
| **CPU** | 4 core | Quản lý và I/O |
| **RAM** | 8 GB | Tốt hơn cho BlueStore |
| **Disk** | /dev/sda : OS | Hệ điều hành |
| | /dev/sdb , /dev/sdc , /dev/sdd : 3 Disk OSD | Thiết bị lưu trữ dữ liệu (BlueStore) |
| **Network** | ens33 : 192.168.2.x | **Public Network** (Truy cập Ceph) |
| | ens34 : 192.168.3.x | **Cluster Network** (Replicate Data) |


# Cài đặt và Cấu hình Cơ bản
## 1. Cấu hình chuẩn bị trên Node
### Tạo Ceph User 
Tạo Ceph user 'cephuser' và cấp quyền sudo không cần mật khẩu.
```bash
# Áp dụng cho cả CentOS và Ubuntu
sudo useradd -m -s /bin/bash cephuser
sudo passwd cephuser
# Cấp quyền sudo (thay vì sed trên /etc/sudoers)
echo "cephuser ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/cephuser
sudo chmod 0440 /etc/sudoers.d/cephuser
```

### Cấu hình NTP và Update OS
```bash
# Cấu hình NTP
## Ubuntu 24.04
sudo timedatectl set-timezone Asia/Ho_Chi_Minh
sudo timedatectl set-ntp true
sudo apt update -y && sudo apt upgrade -y

## CentOS Stream 9
sudo systemctl enable --now chronyd
sudo yum update -y

```

### Vô hiệu hóa SELinux/Firewall
```bash
# CentOS
sudo sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
sudo setenforce 0
sudo systemctl stop firewalld
sudo systemctl disable firewalld

# Ubuntu
sudo ufw disable
```

### Cấu hình Host File
Sử dụng địa chỉ Public Network (192.168.2.x) cho tên host.
```bash
# Thay đổi tên Hostname
sudo hostnamectl set-hostname ceph-aio
# Cấu hình hosts file
sudo tee -a /etc/hosts <<EOF
192.168.2.133 ceph-aio
EOF
```

## 2. Cấu hình SSH
Đảm bảo cephuser có thể SSH tới chính nó

- Đăng nhập bằng `cephuser`: `su - cephuser`
- Tạo SSH Key : 
```bash
ssh-keygen -t ed25519
```

- Thêm Key vào authorized_keys
```bash
ssh-copy-id ceph-aio


# Thủ công 
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
```

- Kiểm tra: `ssh ceph-aio`

## 3. Cài đặt và Khởi tạo cephadm
### Cài đặt Container Engine (Podman được ưu tiên)

```bash
sudo yum install podman -y //CentOS 9
sudo apt install podman -y //Ubuntu
```

### Cài đặt cephadm
```bash
// Ubuntu
sudo apt install cephadm -y

// CentOS
sudo yum install -y dnf-utils
sudo dnf config-manager --add-repo https://download.ceph.com/rpm-quincy/el9/ceph.repo
sudo yum install cephadm -y

```

### Khởi tạo Ceph Cluster
Chuyển sang thư mục làm việc và chạy `bootstrap` để cài đặt MON và MGR đầu tiên, và tạo cấu hình cơ bản.

```bash
# Đảm bảo đang là cephuser
mkdir ceph-cluster
cd ceph-cluster/

sudo cephadm bootstrap \
  --mon-ip 192.168.2.133 \
  --initial-dashboard-password <MẬT_KHẨU_DASHBOARD> \
  --allow-fqdn-hostnames \
  --skip-monitoring-stack

```


## 4. Cấu hình Network và Cài đặt Tool

Copy key `ceph.conf` và `ceph.client.admin.keyring` về thư mục `$HOME/.ssh/` và cài đặt `ceph-common` để sử dụng lệnh ceph.

```bash
sudo cephadm shell -- ceph config set global public_network 192.168.2.0/24
sudo cephadm shell -- ceph config set global cluster_network 192.168.3.0/24

sudo cephadm install ceph-common -y

# Copy keyring cho cephuser để chạy lệnh ceph
sudo cp /etc/ceph/ceph.conf ~/.ceph/ceph.conf
sudo cp /etc/ceph/ceph.client.admin.keyring ~/.ceph/ceph.client.admin.keyring
sudo chown cephuser:cephuser ~/.ceph/*


ceph status
```

## 5. Triển khai các dịch vụ 
```bash
# Xác định các thiết bị có sẵn 
ceph orch device ls ceph-aio

# Triển khai OSD trên tất cả các đĩa trống
ceph orch apply osd --all-available-devices
## Hoặc với các đĩa cụ thể 
ceph orch apply osd --device-class hdd --hosts ceph-aio /dev/sdb /dev/sdc /dev/sdd

# Kiểm tra 
ceph osd tree
ceph -s
```

