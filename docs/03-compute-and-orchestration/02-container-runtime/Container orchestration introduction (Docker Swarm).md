# Container Orchestration Introduction: Docker Swarm

## Overview

Container orchestration là lớp điều phối nhiều container thành service ổn định: scheduling, scaling, rolling update, service discovery, health state và self-healing.

Docker Swarm là orchestration mode tích hợp trong Docker Engine. Nó đơn giản hơn Kubernetes và phù hợp để học mental model orchestration hoặc chạy cụm nhỏ, nhưng với hệ sinh thái cloud-native hiện đại, Kubernetes thường là lựa chọn phổ biến hơn cho production phức tạp.

## Core Concepts

| Khái niệm | Ý nghĩa |
|---|---|
| Manager node | Node giữ cluster state, nhận lệnh và điều phối service |
| Worker node | Node chạy task/container theo phân công |
| Service | Desired state của workload, ví dụ image, replica, port, network |
| Task | Một instance cụ thể của service chạy trên node |
| Overlay network | Network nối service/container qua nhiều Docker host |
| Stack | Nhóm service khai báo bằng Compose file và deploy vào Swarm |

## Swarm Flow

1. Admin tạo hoặc join node vào Swarm.
2. Manager lưu desired state của service.
3. Scheduler chọn node cho từng task.
4. Worker chạy container tương ứng.
5. Nếu task chết hoặc node lỗi, Swarm tạo task thay thế theo desired state.

Đây cũng là mental model chung của orchestration: desired state được khai báo, control plane liên tục reconcile actual state.

## Orchestration Spectrum

Không phải công cụ nào chạy nhiều container cũng giải quyết cùng một lớp bài toán. Có thể nhìn orchestration theo phổ sau:

| Lớp | Ví dụ | Phù hợp khi | Giới hạn |
|---|---|---|---|
| Process manager trên một host | `systemd` chạy container | host đơn, appliance, service nhỏ cần boot/restart/log rõ | không có scheduler multi-node, service discovery hạn chế |
| Multi-container local model | Docker Compose | dev, lab, integration test, deployment nhỏ | không tự giải quyết HA nhiều node |
| Manual multi-host control plane | Helios-style master/agent | muốn operator quyết định workload chạy ở host nào | thiếu autoscaling/scheduling nâng cao |
| Full orchestrator | Swarm, Kubernetes | cần desired state, scheduler, self-healing, rollout và service discovery | control plane phức tạp hơn, cần vận hành cluster |
| Coordination/discovery backend | etcd, Consul, ZooKeeper | lưu metadata, service discovery, lock, election | không tự chạy container thay scheduler |

Điểm thiết kế quan trọng là tách **deployment decision** khỏi **service discovery**. Scheduler quyết định workload chạy ở đâu; service discovery giúp client hoặc proxy tìm endpoint healthy sau khi workload đã chạy.

## Tạo Swarm Cơ Bản

Trên manager đầu tiên:

```bash
docker swarm init --advertise-addr 10.0.0.10
```

Node khác join bằng token được tạo ra:

```bash
docker swarm join --token <TOKEN> 10.0.0.10:2377
```

Join token là credential để thêm node vào cluster. Không đưa token thật vào note, ticket, chat hoặc CI log; rotate token nếu nghi ngờ bị lộ.

Kiểm tra node:

```bash
docker node ls
```

## Chạy Service

Tạo service với nhiều replica:

```bash
docker service create \
  --name web \
  --replicas 3 \
  --publish 8080:80 \
  nginx
```

Quan sát service và task:

```bash
docker service ls
docker service ps web
docker service logs web
```

### Routing Mesh Và Published Port

Swarm routing mesh làm mỗi node trong swarm có thể nhận traffic cho service có published port, kể cả node đó không chạy task của service. Node nhận request sẽ forward vào task phù hợp trong cluster.

Mental model:

```text
client -> any swarm node published port -> routing mesh -> service task
```

Điểm này tiện cho cụm nhỏ, nhưng trong production cần quyết định rõ:

- dùng routing mesh hay publish theo host mode/load balancer ngoài;
- firewall/security group mở port ở node nào;
- health check của load balancer kiểm tra node hay kiểm tra service backend thật;
- MTU/overlay network có làm traffic chập chờn không;
- log access nằm ở load balancer, node nhận request hay container backend.

Scale service:

```bash
docker service scale web=5
```

Rolling update image:

```bash
docker service update --image nginx:<tag> web
```

Xóa service:

```bash
docker service rm web
```

## Overlay Network

Tạo overlay network cho service nội bộ:

```bash
docker network create --driver overlay app-net
docker service create --name api --network app-net --replicas 3 <image>:<tag>
```

Service trong cùng overlay network có thể resolve nhau bằng service name. Khi debug overlay, kiểm tra firewall giữa node, MTU, DNS nội bộ và trạng thái node.

## Stack Và Compose File

Swarm có thể deploy một nhóm service bằng Compose file:

```bash
docker stack deploy -c docker-compose.yml app
docker stack services app
docker stack ps app
docker stack rm app
```

Không phải mọi option của Docker Compose local đều có cùng ý nghĩa trong Swarm. Khi deploy stack, cần kiểm tra lại phần `deploy`, `replicas`, `placement`, `update_config`, network và volume.

## Volume Trong Swarm

Volume local chỉ nằm trên node đang chạy task. Nếu service có replica trên nhiều node, mỗi node có thể có volume cùng tên nhưng dữ liệu khác nhau.

Với workload stateful, cần storage backend dùng chung như NFS, SMB/CIFS, CephFS hoặc storage plugin phù hợp. Trước khi chạy production, phải có backup, restore test và hiểu rõ consistency của ứng dụng.

## Manager High Availability

Một Swarm production nên có nhiều manager để tránh single point of failure. Số manager nên là số lẻ để quorum rõ ràng.

```bash
docker node promote <node>
docker node demote <node>
docker node update --availability drain <node>
```

Không promote/demote hoặc drain node khi chưa hiểu trạng thái quorum, replica placement và capacity còn lại. `drain` có thể reschedule task sang node khác; nếu workload dùng local volume hoặc stateful service chưa thiết kế storage chung, thao tác này có thể gây mất availability hoặc nhìn như mất dữ liệu.

## Khi Nào Dùng Swarm

Swarm phù hợp khi:

- Cần orchestration đơn giản, ít thành phần.
- Đội vận hành đã quen Docker Engine.
- Workload nhỏ, ít yêu cầu ecosystem mở rộng.
- Mục tiêu chính là học scheduling, service, replica, overlay network.

Kubernetes phù hợp hơn khi cần ecosystem lớn, CRD/operator, autoscaling nâng cao, policy admission, storage orchestration và cloud-native integration sâu.

## Related Pages

- [Docker Compose Services](./05-Docker%20Compose%20services.md)
- [Network Mode Bridge, Host, Overlay](./03-Network%20mode%20bridge,%20host,%20overlay.md)
- [Volumes, Bind Mount, tmpfs](./04-Volumes,%20Bind%20mount,%20tmpfs.md)
- [Kubernetes Overview](../03-container-orchestration/01-kubernetes/overview.md)
