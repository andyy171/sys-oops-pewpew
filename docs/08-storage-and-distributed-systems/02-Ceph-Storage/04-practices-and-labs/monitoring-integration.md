# Tích hợp monitoring cho Cluster 

- Tạo 1 node monitoring riêng cùng dải 

- config host
```bash
cat << EOF | sudo tee /etc/hosts
127.0.0.1   localhost
192.168.198.101 ceph-node1 
192.168.198.102 ceph-node2 
192.168.198.103 ceph-node3 

192.168.198.202 openstack
192.168.198.122 prometheus
192.168.198.123 grafana

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
        - 192.168.198.122/24  
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

```

- Mở port filewall
```bash
sudo apt install -y ufw
sudo ufw --force reset

# mở các port 
sudo ufw allow 22/tcp comment 'SSH Access'
sudo ufw allow 9090/tcp
## sudo ufw allow 3100/tcp # Loki

sudo ufw allow from 192.168.198.0/24
sudo ufw enable
sudo ufw status verbose
```

- Node Grafana tương tự mở cổng 3000 sudo ufw allow 3000/tcp

- Trên các node ceph 
```bash
ceph orch rm grafana
ceph orch status

# Lấy thông tin về Prometheus (thường ở 9095)
ceph mgr module enable prometheus
ceph orch ps --daemon-type prometheus
```
