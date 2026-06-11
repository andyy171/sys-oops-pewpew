# OpenStack General Logs And Maintenance Debug

## Overview

OpenStack troubleshooting phải đi theo chuỗi bằng chứng. Một lỗi ở Horizon hoặc CLI thường chỉ là triệu chứng của service khác: Keystone token, endpoint sai, Nova scheduler, Neutron port, Cinder backend, RabbitMQ, database hoặc hypervisor/storage/network bên dưới.

Nguyên tắc:

- Reproduce bằng CLI trước khi kết luận UI lỗi.
- Ưu tiên read-only checks.
- Ghi lại thời điểm, command, project/user, request ID và service liên quan.
- Chỉ thay đổi một thứ tại một thời điểm.
- Backup config/database trước thay đổi lớn.
- Nếu một giả thuyết sai, revert thay đổi thử nghiệm trước khi thử hướng khác để tránh tạo thêm biến số.

## Troubleshooting Flow

```text
Symptom
  -> scope: user/project/service/node
  -> reproduce with CLI and --debug
  -> token/catalog/endpoint
  -> service status
  -> logs by timestamp/request-id
  -> DB/RabbitMQ/backend/network
  -> one fix
  -> verify
```

## Baseline Checks

```bash
openstack --version
openstack token issue
openstack catalog list
openstack endpoint list
openstack service list
openstack quota show <project>
```

Linux host baseline:

```bash
hostnamectl
timedatectl
ip addr
ip route
ss -lntup
df -h
free -h
systemctl status <service>
journalctl -u <service> --since "30 minutes ago"
```

Time sync quan trọng vì token có expiry. Clock skew có thể làm credential đúng nhưng token bị xem là invalid.

Nhóm công cụ Linux nền tảng:

| Công cụ | Dùng khi nào |
|---|---|
| `ps`, `pgrep` | Tìm process service/agent đang chạy và command line thực tế. |
| `top`/`htop` | Xem CPU, memory, load và process đang ăn tài nguyên. |
| `df`, `du` | Kiểm disk full ở log, image store, database, Swift/Cinder backend. |
| `ip addr`, `ip route` | Kiểm interface, IP, route, network namespace path. |
| `ss -lntup` | Kiểm port API/broker/database đang listen và process owner. |
| `find` | Tìm file config/log theo tên khi layout distro khác nhau. |

## Logs And Request ID

Service logs thường nằm dưới `/var/log/<service>/`, journald hoặc container log tùy deployment.

| Mảng | Log/command thường dùng |
|---|---|
| Keystone | `/var/log/keystone/`, `/var/log/httpd/*keystone*` |
| Horizon | `/var/log/horizon/horizon.log`, web server log |
| Glance | `/var/log/glance/api.log` |
| Nova | `nova-api.log`, `nova-scheduler.log`, `nova-conductor.log`, `nova-compute.log` |
| Neutron | `/var/log/neutron/server.log`, agent log, `/var/log/ovn/` |
| Cinder | `api.log`, `scheduler.log`, `volume.log`, `backup.log` |
| Swift | proxy/account/container/object logs |
| Heat | `heat-api.log`, `heat-engine.log` |

Debug CLI:

```bash
openstack server show <server> --debug
openstack image list --debug
```

Tìm `X-Openstack-Request-Id` trong output rồi đối chiếu log service.

Khi một thư mục log có nhiều file hoặc tên process không rõ, dùng `lsof` để map process đang ghi file log:

```bash
lsof /var/log/nova/*
lsof /var/log/cinder/*
```

Log rotation và logging stack:

- `/var/log/messages` thường chứa syslog chung.
- `/var/log/secure` thường chứa auth/security event.
- `/var/log/cron` thường chứa cron job.
- `logrotate` đổi tên/nén log cũ; config thường nằm ở `/etc/logrotate.conf` và `/etc/logrotate.d/`.
- `systemd-journald` thu event từ kernel/stdout/stderr/syslog, còn `rsyslog` thường ghi ra file dưới `/var/log` hoặc forward đi nơi khác.

Khi log file không có dòng mới, kiểm service có ghi sang journald/container stdout thay vì file truyền thống không.

## Database

Hầu hết service OpenStack dùng database để lưu control-plane state. Trước khi thay đổi lớn hoặc sửa state nhạy cảm, backup trước.

```bash
systemctl status mariadb
mysql -e "SHOW DATABASES;"
mysqldump --opt --all-databases > /safe-backup/openstack-all-databases.sql
mysqldump --opt <service-db> > /safe-backup/<service-db>.sql
```

Không sửa DB trực tiếp nếu còn CLI hoặc service command an toàn hơn.

Không ghi password thẳng vào command history khi backup. Ưu tiên file option có permission chặt, prompt tương tác hoặc secret manager của môi trường.

## RabbitMQ

RabbitMQ là message broker phổ biến cho OpenStack RPC. Nếu RabbitMQ lỗi, Nova/Neutron/Cinder có thể biểu hiện như service timeout, state không đổi hoặc worker không nhận job.

```bash
systemctl status rabbitmq-server
rabbitmqctl status
rabbitmqctl list_users
rabbitmqctl list_queues
```

Các tín hiệu đáng nhìn trong `rabbitmqctl status`: connection count, queue count, memory watermark, disk free watermark, listener `5672` cho AMQP và log path. RabbitMQ lỗi thường làm request kẹt kiểu timeout hoặc worker không nhận job dù API vẫn trả được phản hồi ban đầu.

Kiểm tra service config có trỏ đúng broker không, nhưng không paste secret thật vào note/ticket:

```bash
grep 'transport_url' /etc/nova/nova.conf
grep 'transport_url' /etc/neutron/neutron.conf
grep 'transport_url' /etc/cinder/cinder.conf
grep 'transport_url' /etc/glance/glance-api.conf
```

## Service Inventory

Khi nhận một cloud lạ, lập inventory trước khi sửa:

```bash
openstack compute service list
openstack network agent list
openstack volume service list
openstack hypervisor list
openstack availability zone list
```

Trong Horizon, Admin/System Information hữu ích để xem compute services, block storage services và network agents, nhưng CLI vẫn là cách tốt hơn để copy evidence.

## Nova Debug

```bash
openstack server list --all-projects
openstack server show <server>
openstack hypervisor list
openstack hypervisor show <hypervisor>
openstack compute service list
tail -f /var/log/nova/nova-api.log
tail -f /var/log/nova/nova-scheduler.log
tail -f /var/log/nova/nova-compute.log
```

Mapping nhanh:

- `No valid host`: quota, Placement inventory, compute service, aggregate/AZ, flavor extra specs.
- Instance `ERROR`: xem `fault`, `nova-compute`, Glance image, Neutron port, Cinder volume.
- Console lỗi: `nova-novncproxy`, endpoint, firewall/proxy.

## Neutron Debug

```bash
openstack network agent list
openstack network list
openstack subnet list
openstack router list
openstack port list
openstack floating ip list
openstack security group rule list <security-group>
ovs-vsctl show
ls /var/log/neutron/ /var/log/ovn
```

Flow:

```text
network/subnet -> port -> DHCP/OVN -> router -> floating IP -> security group -> provider network
```

Drill-down object:

```bash
openstack network show <network>
openstack router show <router>
openstack port show <port-id>
openstack floating ip show <floating-ip>
openstack extension list --network
```

Đọc các field như `external_gateway_info`, `interfaces_info`, `binding_host_id`, `binding_vif_type`, `device_owner`, `port_security_enabled` trước khi đi xuống OVS/OVN flow.

Với sự cố network phức tạp trên host Linux/OVS, có thể dùng công cụ như `plotnetcfg` để vẽ lại topology kernel network và xem quan hệ bridge, veth, namespace. Đây là công cụ hỗ trợ quan sát, không thay thế việc kiểm packet path bằng `ip`, `ovs-vsctl`, `ovs-ofctl`, security group và router/floating IP state.

## Cinder Debug

```bash
openstack volume service list
openstack volume list
openstack volume show <volume>
tail -f /var/log/cinder/api.log
tail -f /var/log/cinder/scheduler.log
tail -f /var/log/cinder/volume.log
tail -f /var/log/cinder/backup.log
```

Flow:

```text
volume state -> quota -> scheduler -> backend mapping/type -> storage backend -> Nova attachment
```

Với attach/detach fail, kiểm tra cả `nova-compute.log` vì compute host là nơi device được expose vào VM.

## Kolla Maintenance Notes

Trong Kolla-Ansible, config được render vào container. Sửa trực tiếp trong container thường chỉ có tác dụng tạm thời.

```bash
kolla-ansible -i <inventory> prechecks
kolla-ansible -i <inventory> reconfigure
docker ps
docker logs <container-name>
docker exec -it <container-name> bash
```

Thực hành tốt:

- Sửa cấu hình trong `/etc/kolla/config/` hoặc `globals.yml`.
- Chạy precheck trước thay đổi lớn.
- Reconfigure/redeploy bằng Kolla thay vì sửa tay trong container.
- Verify endpoint, service list và container health sau thay đổi.

## Observability Stack

| Thành phần | Vai trò |
|---|---|
| Prometheus | Metrics, PromQL, alert source. |
| Grafana | Dashboard và visualization. |
| Elasticsearch/OpenSearch | Index/search logs. |
| Fluent Bit/Fluentd | Forward/aggregate logs. |

Alert nền cho OpenStack:

- API endpoint down hoặc latency tăng.
- RabbitMQ queue depth tăng bất thường.
- Database connection lỗi.
- Nova/Neutron/Cinder service down.
- Hypervisor resource gần hết.
- Disk đầy ở log, DB, image store hoặc storage backend.

## Related Pages

- [OpenStack Client Debug](./openstack-client-debug.md)
- [OpenStack OVS Bridge RX Drops](./ovs-bridge-rx-drops.md)
- [OpenStack API And Automation Workflow](../02-operations/api-and-automation-workflow.md)
- [Nova](../01-core-fundamentals/services/nova.md)
- [Neutron](../01-core-fundamentals/services/neutron.md)
- [Cinder](../01-core-fundamentals/services/cinder.md)
