# Docker Practice And Operations Patterns

## Overview

Note này gom các pattern thực hành Docker thường gặp: hiểu vì sao dùng container, quản lý lifecycle container, expose port, volume/network, image build/push và các thao tác an toàn khi vận hành. Đây là lớp "daily operations" bổ sung cho các note Docker concept, command, Compose, network và volume đã có trong vault.

Docker phù hợp khi cần đóng gói application cùng dependency để chạy nhất quán giữa laptop, CI, staging và production. Với production nhiều node, Docker runtime thường cần orchestration như Kubernetes hoặc Swarm thay vì chỉ chạy nhiều container thủ công.

## Runtime Objects

| Object | Ý nghĩa |
|---|---|
| Image | Template read-only chứa application, runtime, libraries và metadata |
| Container | Instance đang chạy hoặc đã dừng được tạo từ image |
| Volume | Storage do Docker quản lý, bền hơn lifecycle container |
| Bind mount | Mount path từ host vào container, hay dùng cho dev/config |
| Network | Không gian mạng ảo cho container giao tiếp |
| Registry | Nơi lưu và phân phối image, ví dụ Docker Hub hoặc private registry |

Mental model: image là artifact build; container là process runtime; volume giữ dữ liệu; network quyết định cách container nói chuyện.

## Basic Lifecycle

Kiểm tra Docker daemon:

```bash
docker version
docker info
systemctl status docker
```

Pull và chạy container:

```bash
docker pull nginx:<tag>
docker run --name web -d -p 8080:80 nginx:<tag>
docker ps
docker logs --tail 100 web
```

`docker run` là shortcut gồm nhiều bước:

```text
resolve image/tag
-> pull image nếu local chưa có
-> create container metadata, writable layer, network, mount
-> start process chính của container
```

Khi cần tách rõ lifecycle, dùng `create` rồi `start`:

```bash
docker create --name web -p 8080:80 nginx:<tag>
docker start web
docker wait web
```

Container sống/chết theo process chính PID 1 bên trong nó. Nếu process đó exit, container dừng; `docker restart` chỉ start lại process chính theo config cũ, không tự sửa lỗi application.

Vào container để debug:

```bash
docker exec -it web sh
```

Thoát khỏi phiên attached mà không dừng container:

```text
Ctrl+P, Ctrl+Q
```

Dừng và xóa container:

```bash
docker stop web
docker rm web
```

### Graceful Termination

`docker stop` và `docker kill` không tương đương nhau:

| Lệnh | Hành vi mặc định | Dùng khi nào |
|---|---|---|
| `docker stop <container>` | Gửi `SIGTERM`, chờ grace period rồi mới gửi `SIGKILL` nếu process chưa thoát | Mặc định cho vận hành hằng ngày |
| `docker kill <container>` | Gửi `SIGKILL` ngay | Chỉ dùng khi container treo hoặc cần emergency stop |
| `docker kill --signal HUP <container>` | Gửi signal cụ thể | Reload config nếu application hỗ trợ rõ ràng |

Guardrails:

- Với workload có state, ưu tiên `docker stop --time <seconds>` để application flush dữ liệu, đóng connection và ghi checkpoint.
- Kiểm tra tài liệu application trước khi gửi signal như `HUP`, `USR1` hoặc `TERM`; đừng giả định mọi process đều xử lý giống nhau.
- Trước khi force stop production container, thu thập log và trạng thái read-only nếu còn kịp:

```bash
docker inspect <container>
docker logs --tail 200 <container>
docker top <container>
```

- Rollback sau force stop phải tính cả state ngoài container như volume, database, queue và lock file.

### Inspect Là Source Of Truth Khi Debug

Khi container chạy không đúng với kỳ vọng, `docker inspect` là bước kiểm tra cấu hình runtime thay vì chỉ nhìn output của `docker ps`.

```bash
docker inspect <container> --format '{{json .Mounts}}' | jq .
docker inspect <container> --format '{{json .NetworkSettings.Networks}}' | jq .
docker inspect <container> --format '{{.State.Status}} {{.State.ExitCode}} {{.State.OOMKilled}}'
```

Các điểm nên xác nhận:

- image/tag thực tế;
- command/entrypoint đang chạy;
- port publishing;
- bind mount, named volume và mode read-only/read-write;
- network, IP và DNS alias;
- exit code, restart count, OOMKilled và health status.

### `exec`, `attach` Và Debug Trong Container

`docker exec` chạy một process mới bên trong container đang chạy. Đây là cách phù hợp để debug hoặc kiểm tra cấu hình runtime mà không cần cài SSH server trong image.

```bash
docker exec <container> env
docker exec -it <container> sh
docker exec <container> sh -c 'find /tmp -type f -mtime +7 -print'
```

Guardrails:

- `exec` phụ thuộc binary có sẵn trong image. Với distroless/single-binary image, cần có debug workflow khác như debug image, sidecar hoặc ephemeral container ở orchestrator.
- Tránh chạy lệnh thay đổi dữ liệu bằng `exec` trên production trước khi có backup/maintenance plan. Ưu tiên lệnh read-only trước: `env`, `id`, `mount`, `df`, `ss`, `ps`, `cat` file config không chứa secret.
- Không thêm SSH server chỉ để “vào container”; nó tăng attack surface và phá vỡ model container là process runtime.
- `docker attach` gắn terminal vào STDIN/STDOUT của process chính. Dùng `Ctrl+P`, rồi `Ctrl+Q` để detach mà không gửi exit tới container. Với automation hoặc incident response, `docker exec` thường ít rủi ro hơn `attach`.

### Container Runtime Detection

Một số script cần biết mình đang chạy trong container hay host để tránh thao tác nhầm. File `/.dockerenv` có thể dùng như heuristic Docker-specific, nhưng không phải contract bảo mật ổn định.

```bash
if [ -f /.dockerenv ]; then
  echo "running inside a Docker container"
fi
```

Không dùng `/.dockerenv` làm security boundary hoặc quyết định destructive operation duy nhất. Nếu script có thể xóa dữ liệu, thay đổi network, format disk hoặc gọi cloud API, cần thêm guardrail rõ hơn như biến môi trường bắt buộc, allowlist hostname/context, dry-run mặc định và xác nhận explicit.

## Port Publishing

Container có port nội bộ riêng. Muốn truy cập từ host hoặc bên ngoài host, publish port:

```bash
docker run -d --name web -p 8080:80 nginx:<tag>
```

Đọc là: host port `8080` trỏ vào container port `80`.

Kiểm tra:

```bash
docker ps
docker port web
curl -I http://localhost:8080
```

Khi port không truy cập được, kiểm tra app listen trong container, port mapping, host firewall và security group/cloud firewall.

## Data And Config

Named volume cho dữ liệu bền:

```bash
docker volume create app-data
docker run -d --name app -v app-data:/var/lib/app <image>:<tag>
```

Bind mount cho code/config trong dev:

```bash
docker run --rm -it -v "$PWD":/work -w /work <image>:<tag> sh
```

Khuyến nghị:

- Database nên dùng named volume hoặc storage backend rõ ràng.
- Config có thể bind mount read-only nếu phù hợp.
- Không lưu secret thật trong image layer hoặc command history.
- Không dùng `docker commit` làm quy trình build chính cho production.

Environment variable phù hợp cho cấu hình không nhạy cảm hoặc reference tới secret backend:

```bash
docker run -d --name app \
  -e APP_ENV=prod \
  -e LOG_LEVEL=info \
  <image>:<tag>
```

Không truyền password/token thật qua command line nếu có lựa chọn tốt hơn, vì command có thể xuất hiện trong shell history, audit log hoặc process metadata.

## Dev Tool Container Và Host Integration

Container có thể được dùng như môi trường dev tạm thời để mang theo toolchain, dotfile hoặc GUI app. Pattern này hữu ích cho lab/dev, nhưng khi container mount sâu vào host thì boundary bảo mật gần như biến mất.

Ví dụ dev-only để mount source code vào tool container:

```bash
docker run --rm -it \
  -v "$PWD":/work \
  -w /work \
  <dev-tool-image>:<tag> sh
```

Các tích hợp cần coi là high-risk:

- Mount `/var/run/docker.sock` vào container cho phép container điều khiển Docker daemon trên host; về thực tế gần tương đương quyền root trên host.
- Mount X11 socket như `/tmp/.X11-unix` hoặc file `.Xauthority` cho phép container tương tác với desktop session; chỉ dùng trên máy dev tin cậy.
- `--network host`, `--ipc host` và `--privileged` làm giảm mạnh isolation; không dùng như mặc định cho tool container.
- Mount thư mục home hoặc root filesystem của host dễ làm lộ SSH key, kubeconfig, cloud credential và shell history.

Production guardrail: nếu cần automation tool chạy trong container, cấp quyền tối thiểu theo từng path/API, dùng service account riêng, mount read-only khi có thể và audit image nguồn trước khi chạy.

## Remote Docker Host

Các công cụ legacy như Docker Machine từng giúp provision VM và trỏ Docker client sang daemon remote. Mental model còn hữu ích: một Docker CLI có thể nói chuyện với nhiều Docker daemon, nhưng đây không phải là clustering hay scheduler.

Với môi trường hiện đại, ưu tiên Docker context, SSH hoặc TLS-mutual-auth thay vì daemon TCP mở rộng:

```bash
docker context ls
docker context use <context-name>
docker --context <context-name> ps
```

Guardrails:

- Không expose Docker API dạng `tcp://0.0.0.0:2375` không TLS.
- Tách context dev/staging/prod rõ ràng để tránh chạy nhầm lệnh destructive trên host production.
- Trước lệnh thay đổi trạng thái, kiểm tra context và host:

```bash
docker context show
docker info --format '{{.Name}} {{.ServerVersion}} {{.DockerRootDir}}'
```

- Với nhiều host production, dùng orchestrator hoặc automation có desired state; không vận hành deployment multi-host bằng chuỗi lệnh thủ công từ laptop.

## Image Build And Tagging

Build image bằng Dockerfile:

```bash
docker build -t registry.example.com/project-a/app:<tag> .
```

Tag và push:

```bash
docker tag app:local registry.example.com/project-a/app:<tag>
docker push registry.example.com/project-a/app:<tag>
```

Best practices:

- Pin base image bằng version tag hoặc digest theo policy nội bộ.
- Tối ưu layer cache nhưng không để cache che lỗi dependency.
- Dùng `.dockerignore` để tránh copy source thừa, secret, artifact lớn.
- Scan image trước khi promote.
- Dùng tag bất biến như git SHA/build number; không dùng `latest` làm release identity duy nhất.

## Dockerfile Instruction Notes

Các instruction dễ nhầm:

| Instruction | Ghi nhớ |
|---|---|
| `RUN` | Chạy lúc build image, tạo layer mới |
| `CMD` | Default command khi container chạy, có thể bị override |
| `ENTRYPOINT` | Entrypoint chính, phù hợp khi image hoạt động như executable |
| `ENV` | Biến môi trường trong image/container |
| `COPY` | Copy file từ build context vào image |
| `ADD` | Có thêm hành vi đặc biệt như unpack tar; chỉ dùng khi thật cần |

Với app production, ưu tiên Dockerfile có thể tái tạo thay vì sửa tay trong container rồi commit.

## Network Patterns

Network mặc định `bridge` phù hợp cho single-host lab/dev:

```bash
docker network create app-net
docker run -d --name db --network app-net postgres:<tag>
docker run -d --name api --network app-net -p 8080:8080 <api-image>:<tag>
```

Container cùng user-defined bridge network có thể resolve nhau bằng container name. Tránh phụ thuộc vào container IP vì IP có thể đổi khi recreate.

Kiểm tra:

```bash
docker network ls
docker network inspect app-net
```

## Compose And Multi-Service Apps

Compose phù hợp khi một app gồm nhiều service trên một host hoặc môi trường dev/lab:

```bash
docker compose config
docker compose up -d
docker compose ps
docker compose logs -f
docker compose down
```

Compose mô tả service, network, volume và environment bằng YAML. Với production nhiều host, cân nhắc scheduler/orchestrator thay vì coi Compose là cơ chế HA.

## Container Chạy Dưới systemd

Với một Docker host đơn lẻ, `systemd` có thể quản lý container như một service Linux bình thường: start khi boot, restart khi process lỗi, ghi log vào journal và thể hiện dependency với `docker.service` hoặc service khác. Pattern này phù hợp cho appliance nhỏ, edge node, lab production-like hoặc migration tạm thời trước khi có orchestrator.

Không nên bật đồng thời restart policy của Docker và restart policy của `systemd` cho cùng workload nếu chưa hiểu rõ hành vi. Hai lớp cùng cố restart có thể tạo loop khó debug.

Ví dụ unit tối giản:

```ini
[Unit]
Description=Example app container
Requires=docker.service
After=docker.service

[Service]
Restart=on-failure
RestartSec=10
ExecStartPre=-/usr/bin/docker rm app
ExecStart=/usr/bin/docker run --rm --name app -p 8080:8080 registry.example.com/app:<tag>
ExecStop=/usr/bin/docker stop --time 30 app

[Install]
WantedBy=multi-user.target
```

Guardrails production:

- đặt unit trong `/etc/systemd/system/` hoặc drop-in, không sửa unit package-provided;
- chạy `systemd-analyze verify /etc/systemd/system/<unit>.service` trước khi enable;
- dùng image tag/digest rõ ràng, không pull `latest` âm thầm khi restart;
- `ExecStop` nên dùng `docker stop --time <seconds>` để application flush state, không mặc định force remove;
- nếu unit có bind mount/volume, pre-check path, owner, backup và quyền read-only/read-write;
- khi container phụ thuộc service khác, dùng `Requires=`/`After=` cho dependency host-level, nhưng readiness của application vẫn cần health check hoặc retry.

Validation sau deploy:

```bash
systemctl daemon-reload
systemctl status <unit>.service --no-pager
journalctl -u <unit>.service --since "10 minutes ago" --no-pager
docker ps --filter name=app
curl -fsS http://127.0.0.1:8080/health
```

Rollback: disable unit mới, restore unit/drop-in cũ nếu có, reload `systemd`, sau đó start lại version container trước đó bằng tag/digest đã biết. Không xóa volume hoặc data path trong rollback trừ khi đã có backup và kế hoạch restore.

## Ansible Va Docker

Ansible co the bootstrap Docker host va goi Docker API de build image, pull image, tao container, publish port, mount volume va kiem tra trang thai. Pattern nay phu hop cho fleet nho, agent van hanh hoac lab co desired state ro.

Voi application nhieu service, Compose thuong doc hon mot playbook tu tao container/network/volume rieng le. Voi production nhieu node, dung orchestrator nhu Kubernetes hoac Swarm thay vi coi Ansible la scheduler. Voi image build, uu tien Dockerfile/BuildKit trong CI; dung Ansible ben trong container hoac `docker commit` chi nen la ngoai le co ly do.

## Swarm And Stack Reminder

Docker Swarm dùng `service`, `replica`, `node` và `stack` để chạy nhiều container trên nhiều host. Một số lệnh vận hành:

```bash
docker node ls
docker service ls
docker service ps <service>
docker service logs <service>
docker stack deploy -c compose.yaml <stack>
docker stack rm <stack>
```

Trước khi dùng Swarm cho production, cần thiết kế rõ load balancing, secret, network overlay, persistent storage, backup và upgrade strategy.

## Multi-Process Container Và PID 1

Container thường nên có một process chính đại diện cho lifecycle của workload. Khi process chính exit, container dừng. Nếu nhét nhiều service kiểu VM vào cùng container, bạn phải giải quyết các vấn đề mà init system thường xử lý: start order, signal forwarding, child process reaping, log handling, restart từng process và shutdown sạch.

Pattern multi-process có thể chấp nhận tạm thời khi:

- bootstrap legacy app từ VM sang container để giảm bước migration ban đầu;
- chạy dev/lab demo cần mô phỏng một host nhỏ;
- một nhóm process thật sự tạo thành một đơn vị vận hành không có giá trị tách riêng.

Guardrails:

- Ưu tiên tách service thành nhiều container và nối bằng network/Compose/orchestrator khi có thể.
- Nếu bắt buộc nhiều process, dùng init/supervisor rõ ràng như `tini`, `supervisord`, `runit` hoặc base image có init behavior được hiểu rõ; không tự viết shell script PID 1 sơ sài cho production.
- Log nên đi ra stdout/stderr hoặc collector chuẩn; không để mỗi service ghi log rải rác trong writable layer.
- Validation phải kiểm tra từng process con, không chỉ kiểm tra container còn "Up".
- Rollback cần tính cả state bên ngoài container như volume, database, queue và config mounted từ host.

## Operational Safety

### Production Logging Drivers

Container production nên ghi log ra stdout/stderr hoặc endpoint logging chuẩn, sau đó để runtime/logging agent ship đi. Tránh thiết kế mỗi container tự chạy một syslog daemon riêng nếu không có lý do legacy rõ.

Các lựa chọn thường gặp:

| Pattern | Khi dùng | Lưu ý |
|---|---|---|
| `json-file` + agent đọc file | Docker standalone, agent như Fluent Bit/Filebeat đọc log daemon | cần log rotation để tránh đầy disk |
| `journald` | host dùng systemd và muốn truy vấn bằng `journalctl` | cần retention/journal size rõ |
| `syslog`/remote driver | môi trường đã chuẩn hóa rsyslog/syslog | `docker logs` có thể không còn là source chính tùy driver |
| logging sidecar/agent | orchestration platform hoặc fleet lớn | chuẩn hóa metadata service/env/container/image |

Pre-check trước khi đổi log driver toàn daemon:

```bash
docker info --format '{{json .LoggingDriver}}'
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
journalctl --disk-usage 2>/dev/null || true
df -h /var/lib/docker /var/log 2>/dev/null
```

Guardrails:

- Đổi log driver mặc định có thể cần restart Docker daemon và ảnh hưởng workload đang chạy; làm trong maintenance window.
- Xác nhận `docker logs` còn dùng được hay operator phải chuyển sang `journalctl`, syslog hoặc centralized logging UI.
- Gắn metadata đủ để phân biệt container: service, environment, host, image digest, container name/id.
- Không ship secret/token/PII trong log; redaction nên xảy ra gần source nhất có thể.

### Container Metrics Và Runtime Monitoring

`docker stats` hữu ích để quan sát nhanh CPU, memory, network IO và block IO, nhưng không đủ cho alerting và RCA dài hạn. Production cần collector lưu metrics theo thời gian, ví dụ node exporter/container-aware agent/cAdvisor hoặc stack Prometheus tương đương.

Safe checks:

```bash
docker stats --no-stream
docker inspect <container> --format '{{.State.OOMKilled}} {{.HostConfig.Memory}} {{.HostConfig.NanoCpus}}'
docker events --since 10m
```

Collector container thường cần mount read-only các path host như `/sys`, rootfs hoặc Docker metadata. Đây là quyền quan sát sâu vào host, nên phải pin image, giới hạn network/UI, bật auth nếu có web UI và không expose dashboard nội bộ ra Internet.

### CPU Và Memory Controls

Resource limit là guardrail chống noisy neighbor, không phải capacity planning hoàn chỉnh. Các knob cần hiểu:

- `--cpus`: giới hạn CPU tương đối dễ đọc cho workload thường.
- `--cpuset-cpus`: pin container vào core cụ thể; hữu ích cho isolation/NUMA nhưng dễ làm lệch tải.
- `--cpu-shares`: weight tương đối khi có tranh chấp CPU; không phải hard limit.
- `--memory`: giới hạn memory.
- `--memory-swap`: tổng memory + swap; nếu cấu hình sai, container có thể swap nhiều hoặc bị OOM khác kỳ vọng.
- `--pids-limit`: hạn chế fork bomb/process leak.

Trước khi đặt limit, đo workload thật bằng metrics. Sau khi đặt limit, theo dõi latency, error rate, OOMKilled, restart count và host pressure. Không tăng memory/CPU mù quáng nếu nguyên nhân là leak, retry storm hoặc downstream chậm.

Không dùng `--oom-kill-disable` như cách "bảo vệ" application mặc định. Nếu tắt OOM killer cho container không có memory limit, kernel có thể giết process khác trên host trước và gây outage rộng hơn. Chỉ cân nhắc cho process hạ tầng cực kỳ đặc biệt, có memory limit rõ, capacity headroom, alerting và runbook rollback.

Kiểm tra OOM:

```bash
docker inspect <container> --format '{{.State.OOMKilled}} {{.State.ExitCode}}'
journalctl -k --since "1 hour ago" | grep -i oom
```

Các lệnh cleanup cần cẩn trọng:

```bash
docker system df
docker container prune
docker image prune
docker volume prune
docker system prune
```

Không chạy prune trên host production nếu chưa biết container/image/volume nào còn cần rollback hoặc chứa dữ liệu. `docker volume prune` có thể xóa dữ liệu không còn container tham chiếu.

Pre-check read-only trước khi cleanup:

```bash
docker system df -v
docker ps -a --format 'table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}'
docker volume ls
docker network ls
```

Nếu cần xóa container đã dừng, ưu tiên filter rõ ràng thay vì pipeline kiểu “nuke all”:

```bash
docker ps -a --filter status=exited
docker container prune
```

Warning: tránh alias kiểu `docker ps -a -q | xargs docker rm -f` trên máy có access production. `docker rm -f` sẽ force stop container đang chạy và có thể làm mất evidence incident hoặc gây mất dữ liệu chưa flush.

Trước khi xóa container exited hàng loạt, giữ lại thông tin lỗi nếu cần RCA:

```bash
docker ps -a --filter status=exited --filter exited=1
docker inspect <container> > container-inspect.json
docker logs --tail 500 <container> > container.log
```

Log và tài nguyên:

```bash
docker stats
docker events
docker inspect <container>
docker logs --tail 100 -f <container>
```

Nên cấu hình log rotation cho Docker daemon hoặc logging driver để tránh đầy disk.

Giới hạn tài nguyên giúp tránh một container chiếm toàn bộ host:

```bash
docker run -d --name app \
  --memory 512m \
  --cpus 1.5 \
  --pids-limit 256 \
  <image>:<tag>
```

Các limit này dựa trên cgroup. Khi container bị OOM kill, hãy kiểm tra `docker inspect`, `docker stats`, `dmesg`/`journalctl -k` và log application; đừng chỉ tăng memory nếu chưa biết workload tăng thật hay memory leak.

Healthcheck giúp runtime/orchestrator biết trạng thái application tốt hơn việc chỉ nhìn process còn sống:

```bash
docker run -d --name app \
  --health-cmd 'curl -fsS http://127.0.0.1:8080/health || exit 1' \
  --health-interval 30s \
  --health-timeout 5s \
  --health-retries 3 \
  <image>:<tag>
```

Docker standalone không tự thay thế container unhealthy như Kubernetes Deployment. Healthcheck chủ yếu cung cấp signal cho operator, Compose/Swarm hoặc tooling bên ngoài.

## Containerized Cron Jobs

Docker image có thể đóng gói runtime cho scheduled job: host chỉ cần cron/systemd timer gọi `docker run`, còn code/dependency nằm trong image. Pattern này hữu ích cho job nhỏ trên fleet có Docker sẵn, nhưng không nên thay thế scheduler/orchestrator khi job cần queue, retry phức tạp, distributed locking hoặc stateful workflow.

Baseline an toàn:

```text
timer/cron -> pull immutable tag/digest -> run one-shot container -> collect exit code/log -> alert on failure
```

Guardrails:

- Dùng tag immutable hoặc digest; tránh `latest` làm job production tự đổi behavior ngoài kiểm soát.
- Pull trước maintenance window hoặc qua pipeline nếu registry/network không ổn định.
- Mount path host tối thiểu và read-only nếu có thể.
- Không đặt secret trong crontab command line; dùng secret manager, env file có permission chặt hoặc runtime secret theo platform.
- Chống chạy trùng bằng `flock`, systemd timer hoặc scheduler có concurrency policy.
- Log stdout/stderr về journal/logging pipeline và alert theo exit code.

Ví dụ systemd timer gọi container one-shot thường dễ audit hơn cron thuần vì có journal và status riêng. Với Kubernetes, dùng CronJob thay vì cron trên node.

## Docker Daemon Configuration

Docker daemon config là control point của toàn bộ host container runtime. Với Linux host hiện đại, ưu tiên quản lý cấu hình trong `/etc/docker/daemon.json` hoặc systemd drop-in do config management/IaC kiểm soát, thay vì sửa lệnh `ExecStart` trực tiếp trong unit file vendor.

Pre-check trước khi đổi cấu hình:

```bash
docker version
docker info
systemctl status docker --no-pager
journalctl -u docker --since "30 minutes ago" --no-pager
test -f /etc/docker/daemon.json && cat /etc/docker/daemon.json
systemctl cat docker
```

Guardrails:

- Backup config hiện tại và ghi rõ rollback path trước khi đổi.
- Validate JSON trước khi restart; một lỗi cú pháp có thể làm Docker daemon không lên.
- Không đổi nhiều knob cùng lúc nếu đang xử lý incident; tách thay đổi để dễ rollback.
- Restart Docker có thể ảnh hưởng container đang chạy tùy cấu hình live-restore, runtime và workload; làm trong maintenance window nếu host đang chạy workload quan trọng.
- Thu thập `docker ps`, `docker inspect` cần thiết và daemon/kernel logs trước khi restart nếu đang debug sự cố.

Ví dụ validate và reload/restart:

```bash
jq . /etc/docker/daemon.json
sudo systemctl daemon-reload
sudo systemctl restart docker
docker info
docker ps
```

Rollback: khôi phục file config/drop-in cũ, chạy `systemctl daemon-reload`, restart Docker trong cùng maintenance window và xác nhận `docker info`, `docker ps`, log daemon, container health check.

## Docker Data Root Relocation

Docker lưu image, writable layer, container metadata và volume metadata trong data root của daemon. Khi `/var/lib/docker` đầy hoặc host có partition riêng cho container runtime, có thể cần chuyển data root. Đây là thay đổi production-risky vì sai thao tác có thể làm daemon không thấy image/container cũ hoặc làm container downtime.

Pre-check read-only:

```bash
docker system df
docker ps -a
docker volume ls
df -hT /var/lib/docker /data/docker 2>/dev/null
systemctl status docker --no-pager
```

Guardrails:

- Lập maintenance window nếu host đang chạy workload quan trọng.
- Backup `/etc/docker/daemon.json` và xác định rollback path trước khi đổi.
- Không sửa trực tiếp file bên trong `/var/lib/docker`; đây là state nội bộ của daemon.
- Dùng key `data-root` trong daemon config thay vì các flag cũ như `-g`.

Ví dụ config:

```json
{
  "data-root": "/data/docker"
}
```

Validation sau thay đổi:

```bash
docker info | grep -i "Docker Root Dir"
docker ps -a
docker run --rm hello-world
```

Rollback: khôi phục `daemon.json` cũ, restart Docker trong maintenance window, và kiểm tra lại `Docker Root Dir`. Nếu đã copy/move data thực, đừng xóa data root cũ cho đến khi đã verify image, container, volume và backup.

## Troubleshooting Checklist

| Triệu chứng | Kiểm tra |
|---|---|
| Container exit ngay | `docker logs`, `docker inspect`, command/entrypoint |
| Image pull fail | registry auth, tag, DNS, proxy, certificate |
| Không vào được port | `docker ps`, `docker port`, app listen, host firewall |
| Container không resolve được service | Docker network, service/container name, DNS nội bộ |
| Mất dữ liệu sau recreate | volume/bind mount, đường dẫn mount, `docker compose down -v` |
| Disk đầy | `docker system df`, log file, dangling image, unused volume |

### Fails Only On One Host

Nếu cùng một image chạy được trên host A nhưng fail trên host B, đừng chỉ nhìn image. Container vẫn phụ thuộc kernel, Docker daemon/runtime, storage driver, SELinux/AppArmor, cgroup mode, filesystem mount option và host network.

Triage read-only:

```bash
docker version
docker info
uname -a
docker inspect <container>
journalctl -u docker --since "1 hour ago" --no-pager
journalctl -k --since "1 hour ago" --no-pager
```

Nếu lỗi nằm ở syscall/file/kernel behavior, dùng `strace` ngắn có time window rõ hoặc attach vào PID container trên host. `strace` có overhead và có thể lộ path, argument hoặc secret trong syscall; không chạy kéo dài trên production nếu chưa có lý do.

## Related Pages

- [Docker Overview](./01-docker/overview.md)
- [Docker Commands](./01-docker/00-docker-commands.md)
- [Container Vs VM Concepts](./Container%20vs%20VM%20concepts.md)
- [Image Layer, Dockerfile Best Practices](./Image%20layer,%20Dockerfile%20best%20practices.md)
- [Docker Network Modes](./03-Network%20mode%20bridge,%20host,%20overlay.md)
- [Docker Volumes, Bind Mount Và tmpfs](./04-Volumes,%20Bind%20mount,%20tmpfs.md)
- [Docker Compose Services](./05-Docker%20Compose%20services.md)
- [Ansible Docker Container Automation](../../05-infrastructure-automation/07-configuration-management/01-ansible/09-docker-container-automation.md)
- [Container Orchestration Introduction](./Container%20orchestration%20introduction%20%28Docker%20Swarm%29.md)
