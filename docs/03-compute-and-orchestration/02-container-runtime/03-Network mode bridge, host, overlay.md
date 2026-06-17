# Docker Network Mode: Bridge, Host, Overlay

## Overview

Docker network quyết định container giao tiếp với container khác, host và bên ngoài như thế nào. Khi debug container network, cần tách rõ ba lớp:

- Container process lắng nghe trên port nào bên trong network namespace.
- Docker network driver tạo đường đi giữa các container ra sao.
- Port publishing (`-p`) ánh xạ traffic từ host vào container như thế nào.

## Core Concepts

| Khái niệm | Ý nghĩa |
|---|---|
| Network namespace | View mạng riêng của container: interface, route, port, firewall scope |
| Bridge network | Docker tạo Linux bridge trên host, container nối vào bridge bằng veth pair |
| Host network | Container dùng trực tiếp network namespace của host |
| Overlay network | Network trải qua nhiều Docker host, thường dùng với Docker Swarm |
| Port publishing | NAT/forwarding từ port trên host vào port trong container |
| Service discovery | Container cùng user-defined network có thể gọi nhau bằng container/service name |
| `none` network | Container chỉ có loopback, không có path ra network ngoài nếu không cấu hình thêm |

Legacy `--link` từng được dùng để tạo alias và inject environment giữa container. Trên Docker hiện đại, ưu tiên user-defined bridge network và DNS nội bộ thay vì `--link`, vì network rõ ràng hơn, ít phụ thuộc thứ tự start và dễ migrate sang Compose/orchestrator hơn.

## Bridge Network

`bridge` là mode phổ biến nhất trên một Docker host. Container trong cùng user-defined bridge network có thể gọi nhau bằng tên.

```bash
docker network create --driver bridge app-net
docker run -d --name web --network app-net nginx
docker run --rm --network app-net curlimages/curl http://web:80
```

Có thể đặt network alias khi một service cần tên ổn định khác container name:

```bash
docker network connect --alias api app-net web
docker run --rm --network app-net curlimages/curl http://api:80
```

Nếu cần expose service ra ngoài host, dùng `-p`:

```bash
docker run -d --name web --network app-net -p 8080:80 nginx
```

Ý nghĩa:

- `80` là port trong container.
- `8080` là port trên host.
- Client ngoài Docker truy cập `http://<host>:8080`.
- Container khác trong cùng `app-net` nên gọi `http://web:80`, không cần đi vòng qua port published.

## Default Bridge Vs User-Defined Bridge

Default bridge (`bridge`, thường đi qua `docker0`) hữu ích cho thử nghiệm nhanh, nhưng không phải lựa chọn tốt cho application nhiều container. User-defined bridge tạo một group sandbox riêng, có DNS nội bộ theo container/service name và tách traffic khỏi container không cùng network.

Khác biệt vận hành quan trọng:

- container trên cùng user-defined bridge có thể gọi nhau bằng tên và IP;
- container trên default bridge thường không có service discovery theo tên như user-defined bridge;
- container gắn vào nhiều bridge có nhiều interface và có thể đóng vai trò bastion/proxy giữa các network;
- container ở hai bridge khác nhau không nên coi là reach được nhau nếu không có route/proxy rõ ràng.

Kiểm tra an toàn:

```bash
docker network ls
docker network inspect app-net
docker inspect <container>
docker exec <container> ip addr
```

Việc `docker network connect` một container đang chạy vào network khác có thể mở thêm path truy cập ngoài thiết kế ban đầu. Trước khi làm trên môi trường dùng chung, kiểm tra security group/firewall nội bộ, port listening và service nào sẽ thấy container đó.

## Host Network

Với `--network host`, container dùng network namespace của host.

```bash
docker run --rm --network host nginx
```

Lưu ý vận hành:

- Không có NAT riêng cho container.
- Port conflict trực tiếp với process trên host.
- Cách ly mạng yếu hơn bridge network.
- Phù hợp cho một số agent, monitoring hoặc workload cần nhìn network host, nhưng cần cân nhắc bảo mật.

Host network là cách bypass Docker networking, không phải optimization mặc định. Nó bỏ port publishing/NAT/veth/bridge overhead, nhưng container nhìn cùng port space với host: hai process cùng listen `0.0.0.0:80` sẽ conflict trực tiếp. Với môi trường multi-tenant, coi `--network host` như nới isolation đáng kể và cần review như thay đổi bảo mật.

## Overlay Network

`overlay` dùng để kết nối container/service chạy trên nhiều Docker host trong Docker Swarm.

```bash
docker network create --driver overlay app-overlay
docker service create --name web --network app-overlay --replicas 3 nginx
```

Overlay network hữu ích khi service replica nằm trên nhiều node nhưng vẫn cần service discovery và routing nội bộ. Khi dùng overlay, cần kiểm tra firewall giữa các node, control plane Swarm và MTU nếu gặp lỗi gói tin bị drop hoặc kết nối chập chờn.

## Substrate Network Qua Nhiều Host

Substrate network là lớp network phần mềm đặt lên trên network có sẵn để làm container ở nhiều host nhìn như cùng một private network. Các công cụ overlay/substrate như Weave Net hoặc Docker overlay có thể giảm nhu cầu hard-code topology theo host, nhưng đổi lại có thêm control process, encapsulation overhead, MTU risk và firewall dependency.

Guardrails khi dùng network nhiều host:

- xác định rõ port/protocol control plane và data plane cần mở giữa các node;
- đo baseline latency, packet loss và throughput trước khi kết luận lỗi thuộc application;
- kiểm tra MTU end-to-end, vì encapsulation có thể làm gói tin lớn bị drop chập chờn;
- không dùng substrate network để bypass segmentation/bastion policy nếu boundary đó được đặt ra vì security;
- với workload stateful hoặc consensus, test partition behavior và quorum trước khi đưa vào production.

## Port Publishing Không Giống Container Network

Một container có thể nghe port `80` bên trong nhưng không expose ra host nếu không có `-p`.

```bash
docker run -d --name internal-nginx nginx
docker ps
```

Container khác cùng network vẫn có thể gọi port nội bộ nếu có network path. Client ngoài host thì cần port publishing hoặc reverse proxy/load balancer phía trước.

## Wildcard DNS Cho Lab

Một số stack dev/test cần hostname hợp lệ thay vì IP trực tiếp, ví dụ ingress rule, virtual host routing, cookie domain hoặc TLS certificate test. Trong lab, có thể dùng wildcard DNS nội bộ hoặc dịch vụ public dạng ánh xạ IP trong hostname.

Mental model:

```text
app.<encoded-ip>.<wildcard-domain> -> <decoded-ip>
```

Pattern này tiện cho demo nhanh, nhưng không nên dùng cho production hoặc UAT nghiêm túc:

- DNS query có thể lộ layout IP nội bộ hoặc tên app ra bên thứ ba.
- Availability, logging policy và bảo mật của dịch vụ public không nằm trong kiểm soát của bạn.
- HTTPS vẫn cần certificate khớp hostname; không bỏ qua kiểm tra TLS chỉ để demo.
- Với môi trường nội bộ, ưu tiên DNS zone riêng, split-horizon DNS hoặc record tạm trong DNS doanh nghiệp.

Pre-check khi debug:

```bash
dig +short <test-hostname>
curl -v http://<test-hostname>:<port>
```

## Troubleshooting

Kiểm tra network và endpoint:

```bash
docker network ls
docker network inspect app-net
docker inspect web
docker port web
docker exec -it web ss -lntp
```

Kiểm tra từ container khác trong cùng network:

```bash
docker run --rm --network app-net curlimages/curl -v http://web:80
```

Kiểm tra từ host:

```bash
curl -v http://127.0.0.1:8080
ss -lntp | grep 8080
```

### Debug Network Namespace Và Veth Pair

Khi image tối giản không có `ip`, `ss`, `tcpdump` hoặc `curl`, có thể dùng tool trên host để quan sát network namespace của container thay vì cài tool vào image. Quy trình an toàn là đọc trước, can thiệp sau:

```bash
docker inspect <container> --format '{{.State.Pid}}'
docker exec <container> ip addr 2>/dev/null || true
docker network inspect <network>
```

Với quyền phù hợp trên host, `nsenter` có thể chạy command trong network namespace của process container:

```bash
PID=$(docker inspect --format '{{.State.Pid}}' <container>)
sudo nsenter --target "$PID" --net ss -tupan
sudo nsenter --target "$PID" --net tcpdump -i any -nn -c 100
```

Để map container interface sang veth trên host, kiểm tra `peer_ifindex` trong namespace container rồi đối chiếu interface index trên host. Chỉ dùng thao tác như disable veth, đổi route hoặc đổi MTU trong maintenance/debug window, vì đây là thay đổi network live có thể làm rớt traffic.

Guardrails:

- `tcpdump`/`tcpflow` có thể capture payload nhạy cảm; lưu file capture theo chính sách incident/evidence.
- Không sửa `/etc/resolv.conf`, route hoặc firewall trong container/host nếu chưa có rollback.
- Khi capture trên `docker0`, lọc theo container IP/port để tránh thu quá nhiều traffic của container khác.
- Với production, ưu tiên mirror/pcap ngắn có time window rõ thay vì capture dài không giới hạn.

## Best Practices

- Tạo user-defined bridge network thay vì dùng default bridge cho application nhiều container.
- Dùng service/container name cho traffic nội bộ, tránh hard-code container IP.
- Chỉ publish port thật sự cần truy cập từ ngoài Docker host.
- Tránh `--network host` nếu không có lý do rõ ràng.
- Với Swarm/overlay, kiểm tra firewall, MTU và network storage trước khi chạy workload stateful.

## Related Pages

- [Docker Overview](./01-docker/overview.md)
- [Docker Commands](./01-docker/00-docker-commands.md)
- [Docker Compose Services](./05-Docker%20Compose%20services.md)
- [Container Orchestration Introduction](./Container%20orchestration%20introduction%20%28Docker%20Swarm%29.md)
