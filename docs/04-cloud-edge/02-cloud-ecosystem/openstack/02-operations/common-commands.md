# OpenStack Common Commands

## Overview

Đây là quick reference cho các thao tác OpenStack admin thường gặp: identity, catalog, image, network, compute, volume, object storage, orchestration và troubleshooting. Trước khi chạy lệnh, cần source đúng RC file hoặc export biến môi trường tương ứng.

```bash
source <openrc-file>
openstack token issue
openstack catalog list
```

Không lưu password/token thật trong note. Dùng placeholder như `<PASSWORD>`, `<PROJECT>`, `<USER>`, `<TOKEN>`.

## Environment Inventory

Khi nhận một môi trường OpenStack lạ, đừng bắt đầu bằng sửa config. Lập inventory trước để biết release, endpoint, service, agent và backend đang có gì.

```bash
openstack --version
openstack token issue
openstack service list
openstack endpoint list
openstack catalog list
openstack availability zone list
```

Kiểm tra version/service manager ở node control plane:

```bash
keystone-manage --version
nova-manage --version
neutron-server --version
glance-api --version
cinder-manage --version
systemctl list-units '*openstack*' --type=service
```

Không phải deployment nào cũng có binary/service giống nhau. Nếu API chạy qua WSGI hoặc container, kiểm tra web server/container runtime thay vì chỉ tìm `openstack-<service>` systemd unit.

Inventory năng lực vận hành:

```bash
openstack compute service list
openstack hypervisor list
openstack network agent list
openstack volume service list
openstack quota show <project>
openstack extension list --network
```

Mapping nhanh khi thấy service down:

| Kết quả inventory | Hướng đọc tiếp |
|---|---|
| Compute service down | `nova-compute`, hypervisor/libvirt, RabbitMQ, DB, host resource. |
| Network agent/OVN controller down | Neutron/OVN log, OVS bridge, RabbitMQ hoặc OVN NB/SB connectivity. |
| Volume service down | `cinder-volume`, backend driver, storage network, iSCSI/Ceph/NFS health. |
| Endpoint thiếu/sai | Keystone service catalog trước, service backend sau. |
| Quota đầy | Tăng quota hoặc dọn resource trước khi debug scheduler/backend. |

## Identity

```bash
# Domain
openstack domain list
openstack domain show <domain>
openstack domain create --description "<description>" <domain-name>
openstack domain delete <domain>

# Project
openstack project list
openstack project list --domain <domain>
openstack project show <project>
openstack project create --domain <domain> --description "<description>" <project-name>
openstack project delete <project>

# User
openstack user list
openstack user list --domain <domain>
openstack user show <user>
openstack user create --domain <domain> --password-prompt <user-name>
openstack user delete <user>

# Role
openstack role list
openstack role assignment list --user <user> --project <project>
openstack role add --user <user> --project <project> <role>
openstack role remove --user <user> --project <project> <role>
```

## Service Catalog

```bash
openstack service list
openstack service show <service>
openstack endpoint list
openstack endpoint show <endpoint-id>
openstack catalog list
```

## Image

```bash
qemu-img info <image-file>

openstack image create \
  --disk-format qcow2 \
  --container-format bare \
  --file <file.qcow2> \
  --public \
  <image-name>

openstack image list
openstack image show <image>
openstack image save <image> --file <local-file>
openstack image set --property os_name=linux <image>
openstack image add project <image> <project>
openstack image remove project <image> <project>
openstack image delete <image>
```

## Network

```bash
openstack network list
openstack network show <network>
openstack network create <network-name>

openstack subnet list
openstack subnet create \
  --network <network> \
  --gateway <gateway-ip> \
  --subnet-range <cidr> \
  <subnet-name>

openstack router list
openstack router create <router-name>
openstack router add subnet <router> <subnet>
openstack router set --external-gateway <external-network> <router>

openstack port list
openstack port show <port-id>

openstack floating ip list
openstack floating ip create <external-network>
openstack server add floating ip <server> <floating-ip>
```

## Security Group

```bash
openstack security group list
openstack security group create <security-group>
openstack security group rule list <security-group>
openstack security group rule create --protocol tcp --dst-port 22 --remote-ip <CIDR> <security-group>
openstack server add security group <server> <security-group>
openstack server remove security group <server> <security-group>
```

## Compute

```bash
openstack flavor list
openstack flavor show <flavor>
openstack flavor create --vcpus 2 --ram 4096 --disk 40 <flavor-name>

openstack keypair list
openstack keypair create --public-key ~/.ssh/id_rsa.pub <keypair-name>

openstack server list
openstack server list --all-projects
openstack server show <server>
openstack server create \
  --flavor <flavor> \
  --image <image> \
  --network <network> \
  --security-group <security-group> \
  --key-name <keypair> \
  <server-name>
openstack server stop <server>
openstack server start <server>
openstack server reboot <server>
openstack server image create --name <snapshot-name> <server>
openstack server delete <server>
```

## Volume

```bash
openstack volume service list
openstack volume list
openstack volume show <volume>
openstack volume create --size 20 <volume-name>
openstack volume create --size 20 --image <image> <volume-name>
openstack server add volume <server> <volume>
openstack server remove volume <server> <volume>
openstack volume delete <volume>

openstack volume snapshot create --volume <volume> <snapshot>
openstack volume snapshot list
openstack volume create --snapshot <snapshot> --size 20 <new-volume>

openstack volume backup create <volume>
openstack volume backup list
openstack volume backup restore <backup-id>
```

## Object Storage

```bash
swift stat
swift upload <container> <file-or-dir>
swift list
swift list <container>
swift stat <container> <object>
swift download <container> <object>

openstack container list
openstack container create <container>
openstack object list <container>
openstack object create <container> <file>
openstack object save <container> <object> --file <local-file>
```

## Heat

```bash
openstack orchestration template validate -t template.yaml
openstack stack create -t template.yaml <stack>
openstack stack list
openstack stack show <stack>
openstack stack resource list <stack>
openstack stack event list <stack>
openstack stack update -t template.yaml <stack>
openstack stack delete <stack>
```

## Troubleshooting

```bash
openstack --debug server list
openstack endpoint list
openstack service list
openstack compute service list
openstack network agent list
openstack volume service list
openstack hypervisor list
openstack availability zone list
openstack quota show <project>

systemctl status <openstack-service>
journalctl -u <openstack-service> --since "30 minutes ago"
tail -f /var/log/<service>/<log-file>.log
rabbitmqctl status
mysql -e "SHOW DATABASES;"
```

## Related Pages

- [OpenStack API And Automation Workflow](./api-and-automation-workflow.md)
- [OpenStack Client Debug](../04-troubleshooting/openstack-client-debug.md)
- [Keystone](../01-core-fundamentals/services/keystone.md)
- [Nova](../01-core-fundamentals/services/nova.md)
- [Neutron](../01-core-fundamentals/services/neutron.md)
- [Cinder](../01-core-fundamentals/services/cinder.md)
