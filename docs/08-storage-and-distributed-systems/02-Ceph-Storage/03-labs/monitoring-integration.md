# Tích hợp monitoring cho Cluster 

- Tạo 1 node monitoring riêng cùng dải IP với Ceph Cluster và Openstack Node

- config host
```bash
cat << EOF | sudo tee /etc/hosts
127.0.0.1   localhost
192.168.198.101 ceph-node1 
192.168.198.102 ceph-node2 
192.168.198.103 ceph-node3 

192.168.198.110 openstack
192.168.198.111 monitor-node
192.168.198.112 loki-server 

EOF
```
- config hostname 
```bash
echo "network: {config: disabled}" | sudo tee /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg

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
      addresses:
        - 192.168.198.111/24  
      routes:
        - to: default
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
sudo netplan apply
```

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip podman vim htop lvm2 net-tools chrony curl openssh-server

# Install Docker
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io

sudo systemctl enable --now docker
```

- Mở port filewall trên node monitor 
```bash
sudo apt install -y ufw
sudo ufw --force reset

# mở các port 
sudo ufw allow 22/tcp comment 'SSH Access'
sudo ufw allow 9090/tcp
sudo ufw allow 9100/tcp
sudo ufw allow 9103/tcp
sudo ufw allow 9273/tcp
sudo ufw allow 9283/tcp comment 'Ceph Prometheus'
sudo ufw allow 9104/tcp
sudo ufw allow 9180/tcp comment 'openstack-exporter'
sudo ufw allow 9090/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 6789/tcp
sudo ufw allow 3300/tcp
sudo ufw allow 514/tcp
## sudo ufw allow 3100/tcp # Loki

sudo ufw allow from 192.168.198.0/24
sudo ufw enable
sudo ufw status verbose
```


- Trên Node Grafana và Openstack mở cổng các cổng 
  - Trên các node ceph 
  sudo ufw allow 3000/tcp
  sudo ufw allow from <IP_Node_Monitor> to any port 9100 proto tcp
  sudo ufw allow from 192.168.198.111 to any port 9100 proto tcp

  sudo ufw allow from <IP_Node_Monitor> to any port 9103 proto tcp
  sudo ufw allow from 192.168.198.111 to any port 9283 proto tcp
  sudo ufw allow from 192.168.198.111 to any port 6789 proto tcp  # MON

  sudo ufw reload
```bash

# Lấy thông tin về Prometheus (thường ở 9095)
ceph mgr module enable prometheus
ceph orch ps --daemon-type prometheus
```
  - Trên Openstack 
  sudo ufw allow from 192.168.198.111 to any port 9180 proto tcp
  source ~/openstack/bin/activate
  pip install --force-reinstall 'bcrypt==4.0.1' 'passlib==1.7.4'
  CHỈNH FILE /etc/kolla/globals.yml (thêm các dòng sau)
  ```yaml
  enable_grafana: "yes"
  enable_prometheus: "yes"
  enable_prometheus_openstack_exporter: "yes"
  enable_prometheus_libvirt_exporter: "yes"
  enable_prometheus_mysqld_exporter: "yes"
  enable_prometheus_haproxy_exporter: "yes"
  enable_prometheus_cadvisor: "yes"
  enable_prometheus_node_exporter: "yes"
  ```

Quay trở lại monitor node :
- Tải và cài binary prometheus :
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v3.5.0/prometheus-3.5.0.linux-amd64.tar.gz

tar xvfz prometheus-*.tar.gz
cd prometheus-3.5.0.linux-amd64

sudo mkdir -p /opt/prometheus /etc/prometheus
sudo cp prometheus promtool /opt/prometheus/




sudo ln -s /opt/prometheus/prometheus /usr/local/bin/
sudo ln -s /opt/prometheus/promtool /usr/local/bin/

- Tạo user và config file:
sudo useradd --no-create-home --shell /bin/false prometheus
sudo chown -R prometheus:prometheus /opt/prometheus /etc/prometheus

- Sửa file /tmp/prometheus-3.5.0.linux-amd64/prometheus.yml (dùng nano/vi):
```yaml
global:
  scrape_interval: 15s
  scrape_timeout: 10s
  evaluation_interval: 15s
  external_labels:
    cluster: 'openstack-ceph'

scrape_configs:
  # Scrape Prometheus self
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # OpenStack Node Exporter
  - job_name: 'openstack-node'
    static_configs:
      - targets: ['192.168.198.110:9100']
        labels:
          node_type: 'openstack-aio'

  # OpenStack Service Exporters
  - job_name: 'openstack-exporter'
    static_configs:
      - targets: ['192.168.198.110:9198']
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'up|openstack_.*'
        action: keep

  # Scrape Ceph (federate từ MONs, giả sử enable module prometheus)
  - job_name: 'ceph-mgr'
    honor_labels: true
    static_configs:
      - targets:
          - '192.168.198.101:9283'
          - '192.168.198.102:9283'
          - '192.168.198.103:9283'
        labels:
          cluster: 'ceph-prod'
  # Ceph Node Exporters (nếu cài)
  - job_name: 'ceph-nodes'
    static_configs:
      - targets:
          - '192.168.198.101:9100'
          - '192.168.198.102:9100'
          - '192.168.198.103:9100'
```

(Lưu ý: Nếu Ceph chưa enable module, chạy ceph mgr module enable prometheus trên một Ceph node.)

sudo cp /tmp/prometheus-3.5.0.linux-amd64/prometheus.yml /etc/prometheus/

sudo mkdir /opt/prometheus/data && sudo chown -R prometheus:prometheus /opt/prometheus/data

// Trường hợp port openstack-exporter lỗi thì kiểm tra lại xem đang chạy ở cổng nào và chỉnh sửa lại job trên
ps aux | grep openstack-exporter



- Chạy như service (systemd):
Tạo `/etc/systemd/system/prometheus.service`:
```yaml
[Unit]
Description=Prometheus Server
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/opt/prometheus/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/opt/prometheus/data 
Restart=always

[Install]
WantedBy=multi-user.target
```

Khởi động :
```yaml
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus
sudo systemctl status prometheus  # Check log nếu lỗi
```

// Check output journalctl -u prometheus -e

> Test: Truy cập http://192.168.198.111:9090/targets – thấy UP cho các targets. Nếu DOWN, check firewall (sudo ufw allow 9090 hoặc iptables).

- Cài và config Grafana
  - Thêm repo và cài
  ```yaml
  sudo apt-get install -y apt-transport-https software-properties-common wget
  sudo mkdir -p /etc/apt/keyrings/
  wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
  echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
  sudo apt-get update
  sudo apt-get install grafana -y
  ```

  - Khởi động service:
  ```yaml
  sudo systemctl daemon-reload
  sudo systemctl enable grafana-server
  sudo systemctl start grafana-server
  sudo systemctl status grafana-server
  ```

> Test: Truy cập http://192.168.198.111:3000 (user: admin, pass: admin – đổi ngay). Mở port nếu cần: sudo ufw allow 3000.


- Config Grafana cho monitoring 
  - Đăng nhập Grafana > Configuration > Data Sources > Add data source > Prometheus.
    - URL: http://localhost:9090 (hoặc IP node nếu remote).
    - Save & Test – phải Success.
  - Import dashboard:
    - Ceph: Tìm "Ceph Dashboard" (ID ~12644) tại grafana.com/dashboards – import và chọn datasource Prometheus.
    - OpenStack: Tìm "OpenStack Exporter Overview" (ID ~3662) hoặc Kolla-specific (~14000) – import tương tự.
    - Thêm panel tùy chỉnh nếu cần (query ceph_cluster_health cho Ceph, openstack_nova_* cho OpenStack).


// Tùy chọn trên cụm ceph có thể làm tăng tải nhưng tăng số metrics có thể thu thập được ceph config set mgr mgr/prometheus/exclude_perf_counters false

Test Ceph 
ceph osd pool create testbench 100 100
//Write
rados bench -p testbench 300 write --no-cleanup -t 16 --object-size 4MB
// Read
rados bench -p testbench 300 rand
// Cleanup 
rados bench -p testbench 300 rand

// Cài công cụ test tốt hơn 
sudo apt install fio -y
# 1. Tạo một RBD image 50GB trong pool 'rbd'
rbd create rbd/fio_test_image --size 5G

# 2. Map RBD image thành một thiết bị block device (optional, but cleaner)
# Tuy nhiên, FIO có thể sử dụng ioengine=rbd để truy cập trực tiếp.

CÁc kịch bản 
Tỷ lệ Đọc/Ghi Ngẫu nhiên (70% Đọc, 30% Ghi):

```Bash

fio --name=db_rand_rw --ioengine=rbd --pool=POOL_NAME --rbdname=RBD_IMAGE_NAME \
--rw=randrw --rwmixread=70 --bs=4k --iodepth=64 \
--size=10G --runtime=300 --group_reporting --time_based
--rw=randrw: Đọc/Ghi ngẫu nhiên (Random Read/Write).
```
--rwmixread=70: Tỷ lệ đọc là 70%, ghi là 30%.

--bs=4k: Kích thước khối 4KB (điển hình cho database).

--iodepth=64: Độ sâu hàng đợi 64 (concurrency cao).

--runtime=300: Chạy trong 300 giây (5 phút).

