# Docker Compose Services

## Overview

Docker Compose dùng một file YAML để mô tả nhiều container chạy cùng nhau trên một Docker host. Thay vì chạy nhiều lệnh `docker run` rời rạc, Compose gom service, network, volume, environment và port mapping thành một model có thể version control.

Compose phù hợp cho local development, lab, demo, integration test hoặc deployment nhỏ. Với production nhiều node, cần cân nhắc Swarm, Kubernetes hoặc nền tảng orchestration phù hợp.

## Mental Model

| Thành phần | Ý nghĩa |
|---|---|
| `services` | Các container logic của ứng dụng |
| `networks` | Network nội bộ giữa service |
| `volumes` | Dữ liệu bền ngoài lifecycle container |
| `ports` | Port published từ host vào container |
| `environment` | Biến môi trường runtime |
| `depends_on` | Thứ tự start cơ bản, không thay health check thực sự |

## Compose Như Contract Cho Multi-Container Lab

Compose hữu ích nhất khi nó biến một nhóm lệnh `docker run` dễ sai thành một file khai báo có thể review, version control và chạy lại. Service, network, volume, port mapping và biến môi trường nằm trong cùng một model, nên người vận hành có thể thấy topology của stack trước khi start container.

Mental model:

```text
compose.yaml
-> services
-> user-defined network
-> named volume / bind mount
-> container runtime state
```

Không nên dùng Compose để che giấu dependency thật của application. `depends_on` chỉ xử lý thứ tự start cơ bản; nó không chứng minh database đã sẵn sàng nhận write, cache đã warm up hay dependency bên ngoài đã healthy. Application vẫn cần retry/backoff, health check và timeout rõ ràng.

## Ví Dụ Compose File

```yaml
services:
  web:
    image: nginx:<tag>
    ports:
      - "8080:80"
    volumes:
      - ./site:/usr/share/nginx/html:ro
    networks:
      - app-net

  db:
    image: postgres:<tag>
    environment:
      POSTGRES_PASSWORD: "<PASSWORD>"
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - app-net

networks:
  app-net:

volumes:
  db-data:
```

Lưu ý: không commit password thật vào compose file. Với môi trường nghiêm túc hơn, dùng secret manager, `.env` đã được kiểm soát quyền hoặc cơ chế secret của nền tảng deploy.

## Lệnh Vận Hành Thường Gặp

Khởi chạy:

```bash
docker compose up -d
```

Xem trạng thái:

```bash
docker compose ps
docker compose logs -f
docker compose logs --tail 100 web
```

Chạy lệnh trong service:

```bash
docker compose exec web sh
docker compose exec db psql -U <user>
```

Recreate sau khi đổi config/image:

```bash
docker compose up -d --force-recreate
```

Dừng và xóa container/network do Compose tạo:

```bash
docker compose down
```

Warning: thêm `-v` vào `down` sẽ xóa cả named volume do Compose quản lý.

```bash
docker compose down -v
```

Chỉ dùng sau khi đã backup hoặc chắc chắn dữ liệu không cần giữ.

## Network Và Service Discovery

Service trong cùng Compose project thường tự resolve nhau bằng service name.

Ví dụ `web` gọi database bằng hostname `db`, không cần hard-code IP container. Container IP có thể đổi khi recreate, còn service name ổn định hơn trong network của Compose.

Compose hiện đại nên ưu tiên user-defined network và service name thay vì legacy `links`. `links` từng inject hostname và environment giữa container, nhưng phụ thuộc thứ tự start, khó thay container đã chết và không phản ánh tốt topology khi stack lớn lên.

Khi cần alias ổn định khác tên service, dùng network alias có kiểm soát trong Compose thay vì hard-code IP. Alias nên mô tả role, ví dụ `primary-db` hoặc `internal-api`, không mô tả container instance.

## Adapter/Proxy Container Cho Legacy Tool

Một pattern đôi khi hữu ích trong lab là đặt một binary chỉ chạy local sau một adapter/proxy container để các service khác gọi qua TCP. Ví dụ: một container nhận kết nối TCP, gọi binary hoặc CLI bên trong, rồi trả output lại cho client.

Pattern này chỉ nên dùng cho dev, integration test hoặc migration ngắn hạn:

- mỗi container nên giữ một trách nhiệm rõ: backend process, proxy, client hoặc test harness;
- bind mount dữ liệu từ host vào container phải có path cụ thể, quyền tối thiểu và backup nếu là dữ liệu thật;
- không biến SQLite, CLI admin hoặc local tool thành "server production" nếu tool đó không được thiết kế cho concurrency, locking, auth và audit;
- nếu cần production service, chọn database/server chính thức thay vì bọc binary bằng `socat`, `telnet` hoặc shell proxy.

## Volume Và Dữ Liệu

Nên dùng named volume cho dữ liệu database:

```yaml
services:
  db:
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

Bind mount phù hợp cho source code hoặc static content trong môi trường dev:

```yaml
services:
  web:
    volumes:
      - ./site:/usr/share/nginx/html:ro
```

## Troubleshooting

Kiểm tra config sau khi Compose merge biến môi trường:

```bash
docker compose config
```

Kiểm tra container và network thật:

```bash
docker compose ps
docker network ls
docker network inspect <project>_app-net
```

Debug service không lên:

```bash
docker compose logs <service>
docker compose events
docker inspect <container>
```

Triệu chứng thường gặp:

| Triệu chứng | Hướng kiểm tra |
|---|---|
| Service start trước database rồi fail | Health check, retry logic trong application |
| Không gọi được service khác | Network, service name, port nội bộ |
| Mất dữ liệu sau `down -v` | Volume đã bị xóa; cần restore từ backup |
| Config không như kỳ vọng | `docker compose config`, `.env`, override file |

## Best Practices

- Commit compose file nhưng không commit secret thật.
- Đặt tên service rõ ràng theo vai trò: `web`, `api`, `db`, `cache`.
- Dùng named volume cho dữ liệu bền.
- Dùng bind mount read-only cho config/static file nếu có thể.
- Thêm health check hoặc retry trong application thay vì chỉ dựa vào `depends_on`.
- Tách compose file dev/lab khỏi production deployment nếu yêu cầu vận hành khác nhau.

## Related Pages

- [Docker Commands](./01-docker/00-docker-commands.md)
- [Network Mode Bridge, Host, Overlay](./03-Network%20mode%20bridge,%20host,%20overlay.md)
- [Volumes, Bind Mount, tmpfs](./04-Volumes,%20Bind%20mount,%20tmpfs.md)
- [Container Orchestration Introduction](./Container%20orchestration%20introduction%20%28Docker%20Swarm%29.md)
