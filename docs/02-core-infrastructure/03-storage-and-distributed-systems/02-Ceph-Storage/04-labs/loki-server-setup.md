# Tích hợp loki cho Cluster 

## Tạo 1 node loki-server riêng cùng dải IP với Ceph Cluster và Openstack Node

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
        - 192.168.198.112/24  
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
sudo apt install -y wget unzip
sudo apt install -y python3 python3-pip podman vim htop lvm2 net-tools chrony curl openssh-server

# Install Docker
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io

sudo systemctl enable --now docker chrony 
```

- Mở port filewall  
```bash
sudo apt install -y ufw
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
# mở các port 
sudo ufw allow 22/tcp comment 'SSH Access'
sudo ufw allow from 192.168.198.0/24 to any port 3100 proto tcp
sudo ufw allow from 192.168.198.0/24 to any port 9096 proto tcp
sudo ufw allow from 192.168.198.0/24
sudo ufw enable
sudo ufw status verbose
```
- Tải và cài binary loki :
# Cài đặt công cụ hỗ trợ
sudo apt install -y wget unzip

# Tạo user và thư mục
sudo useradd --no-create-home --shell /bin/false loki
sudo mkdir -p /opt/loki/data
sudo mkdir -p /etc/loki

# Tải Loki (Phiên bản mới nhất)
cd /tmp
wget https://github.com/grafana/loki/releases/download/v3.5.9/loki-linux-amd64.zip
unzip loki-linux-amd64.zip
sudo mv loki-linux-amd64 /usr/local/bin/loki
sudo chmod +x /usr/local/bin/loki


- Tạo file cấu hình:
```bash
cat << EOF | sudo tee /etc/loki/loki.yml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096
  http_listen_address: 0.0.0.0
  grpc_listen_address: 0.0.0.0

common:
  instance_addr: 192.168.198.112
  path_prefix: /opt/loki/data
  storage:
    filesystem:
      chunks_directory: /opt/loki/data/chunks
      rules_directory: /opt/loki/data/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2025-11-11
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

# Cấu hình Retention (Đã xóa dòng shared_store gây lỗi)
compactor:
  working_directory: /opt/loki/data/compactor
  retention_enabled: true
  delete_request_store: filesystem

limits_config:
  retention_period: 168h 
  reject_old_samples: true
  reject_old_samples_max_age: 168h

analytics:
  reporting_enabled: false
EOF
```
sudo chown -R loki:loki /opt/loki

- Tạo Service và Chạy Loki:
Tạo `/etc/systemd/system/loki.service`:
```bash
cat << EOF | sudo tee /etc/systemd/system/loki.service
[Unit]
Description=Loki Service
After=network.target

[Service]
Type=simple
User=loki
ExecStart=/usr/local/bin/loki -config.file=/etc/loki/loki.yml
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
```

Khởi động :
```yaml
sudo systemctl daemon-reload
sudo systemctl enable --now loki
sudo systemctl status loki # Check log nếu lỗi
```

## Trên node Ceph quản trị  
- Mở cổng trên các node
```bash
  sudo ufw allow 3100/tcp
  sudo ufw allow out to 192.168.198.112 port 3100 proto tcp
  sudo ufw reload
```

Cephadm cho phép bạn inject cấu hình tùy chỉnh. Tạo file `promtail.yml` trên node quản trị:
```bash
sudo cat << EOF > promtail.yml.j2
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /var/lib/ceph/promtail/positions.yaml # Cephadm sẽ quản lý thư mục này

clients:
  - url: http://192.168.198.112:3100/loki/api/v1/push

scrape_configs:
- job_name: ceph-logs
  static_configs:
  - targets:
      - localhost
    labels:
      job: ceph-logs
      host: {{ host }}    # Cephadm sẽ điền hostname
      __path__: /var/log/ceph/*.log
EOF
```


Inject template custion vào Ceph mgr:
```bash
sudo ceph config-key set mgr/cephadm/services/promtail/promtail.yml.j2 -i promtail.yml.j2
```
Tạo lại file service spec (promtail-spec.yml)
```yaml
sudo cat << EOF > promtail-spec.yml
service_type: promtail
placement:
  hosts:
    - ceph-node01
    - ceph-node02
    - ceph-node03  # Deploy trên các node cụ thể
# Trường hợp muốn chỉ định version :
#image: grafana/promtail:v3.5.9
EOF
```

- Áp dụng Service Spec để deploy Promtail

```bash
sudo ceph orch apply -i promtail-spec.yml
```

- Kiểm tra :
```bash
sudo ceph orch ls | grep promtail
sudo ceph orch ps --daemon_type promtail
```
- Redeploy khi lỗi :
```bash
sudo ceph orch redeploy promtail
```
- Check Metrics và config của node :
```bash
http://<hostname>:9080/metrics
http://<hostname>:9080/config


# Trên loki server 
curl -s "http://192.168.198.112:3100/loki/api/v1/query_range?query=%7Bjob%3D%22ceph-logs%22%7D&limit=10" | jq .

## hoặc trên các node ceph 
curl http://localhost:9080/metrics
```



### Cách Thủ công 
Cài đặt promtail trên từng node ceph :

```bash
sudo apt update
sudo apt install -y wget unzip

sudo useradd --no-create-home --shell /bin/false promtail
sudo mkdir -p /etc/promtail /var/lib/promtail
sudo chown promtail:promtail /var/lib/promtail

cd /tmp
wget https://github.com/grafana/loki/releases/download/v3.5.9/promtail-linux-amd64.zip  
unzip promtail-linux-amd64.zip
sudo mv promtail-linux-amd64 /usr/local/bin/promtail
sudo chmod +x /usr/local/bin/promtail

cat << EOF | sudo tee /etc/promtail/promtail.yml
server:
  http_listen_port: 9080  # Cổng lắng nghe cho Promtail Metrics/Status
  grpc_listen_port: 0

positions:
  filename: /var/lib/promtail/positions.yaml

clients:
  # Thay thế IP và Port của Loki Server của bạn
  - url: http://192.168.198.112:3100/loki/api/v1/push

scrape_configs:
- job_name: ceph-logs
  static_configs:
  - targets:
      - localhost
    labels:
      job: ceph-logs
      host: $(hostname -s)    # Hostname ngắn của node (ví dụ: ceph-node01)
      __path__: /var/log/ceph/*.log
EOF

sudo chown promtail:promtail /etc/promtail/promtail.yml

LOG_GROUP=$(ls -ld /var/log/ceph/ | awk '{print $4}')

sudo usermod -aG $LOG_GROUP promtail
echo "User promtail đã được thêm vào nhóm: $LOG_GROUP"


cat << EOF | sudo tee /etc/systemd/system/promtail.service
[Unit]
Description=Promtail Service
After=network.target

[Service]
Type=simple
User=promtail
ExecStart=/usr/local/bin/promtail -config.file=/etc/promtail/promtail.yml
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now promtail
sudo systemctl status promtail  # Kiểm tra running
journalctl -u promtail -f  # Theo dõi push logs đến Loki
```



## Trên Openstack node AIO 
- Lưu ý kích hoạt Python venv trước đó : 

``` 
source ~/openstack/bin/activate
```

- Chỉnh file /etc/kolla/globals.yml (thêm các dòng sau)
```yaml
  enable_central_logging: "yes"
  enable_fluentd: "no"
  enable_promtail: "yes"
  kolla_logs_dir: "/var/log/kolla"
  promtail_clients:
  - url: "http://192.168.198.112:3100/loki/api/v1/push"
  promtail_extra_volumes:
    - "/var/log/kolla:/var/log/kolla:ro"
  promtail_extra_labels:
    job: "openstack-kolla"
    env: "openstack-aio"
```

- Cấu hình Promtail

Tạo thư mục cấu hình:
```bash
sudo mkdir -p /etc/kolla/config/promtail
```

Tạo file `/etc/kolla/config/promtail/promtail.yml`
```bash
sudo tee /etc/kolla/config/promtail/promtail.yml << 'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /var/lib/promtail/positions.yaml

clients:
  - url: http://192.168.198.112:3100/loki/api/v1/push

scrape_configs:
- job_name: openstack-kolla
  static_configs:
  - targets:
      - localhost
    labels:
      job: openstack-kolla
      host: openstack-aio
      __path__: /var/log/kolla/**/*.log
EOF

```

Deploy / Reconfigure OpenStack
```bash
cd ~/openstack/kolla-ansible
kolla-ansible reconfigure -i ./all-in-one
```

- Kiểm tra
OpenStack node:
```bash
# Kiểm tra container Promtail
sudo docker ps | grep promtail

# Kiểm tra config bên trong container
sudo docker exec promtail cat /etc/promtail/promtail.yml

# Kiểm tra log directory có được mount
sudo docker exec promtail ls /var/log/kolla

# Kiểm tra Promtail đang chạy thật
sudo docker exec promtail cat /proc/1/cmdline
## Output : /usr/bin/promtail -config.file=/etc/promtail/promtail.yml


# Kiểm tra kết nối Loki từ Promtail
sudo docker exec -it promtail sh
wget -qO- http://192.168.198.112:3100/ready
exit
```

- Loki server
```bash
# Query log OpenStack
curl -s \
"http://192.168.198.112:3100/loki/api/v1/query_range?query={job=\"openstack-kolla\"}&limit=10" \
| jq .
```