# Docker Volumes, Bind Mount Và tmpfs

## Overview

Container filesystem có tính tạm thời. Khi container bị xóa, writable layer của container cũng mất. Vì vậy dữ liệu quan trọng cần được đưa ra ngoài lifecycle của container bằng volume, bind mount hoặc backend storage khác.

## Ba Kiểu Mount Chính

| Kiểu | Dùng khi nào | Lưu ý |
|---|---|---|
| Named volume | Dữ liệu application/database do Docker quản lý | Dễ backup hơn bind mount nếu chuẩn hóa mount point |
| Bind mount | Mount trực tiếp thư mục/file từ host vào container | Phụ thuộc path host, dễ lệch giữa môi trường |
| tmpfs | Dữ liệu tạm nằm trong memory | Mất khi container dừng, phù hợp secret/cache tạm |

## Named Volume

Named volume được Docker tạo và quản lý.

```bash
docker volume create app-data
docker volume ls
docker volume inspect app-data
```

Mount volume vào container:

```bash
docker run -d \
  --name app \
  --mount source=app-data,target=/var/lib/app \
  nginx
```

Hoặc dùng cú pháp ngắn:

```bash
docker run -d --name app -v app-data:/var/lib/app nginx
```

Named volume phù hợp cho dữ liệu cần tồn tại sau khi container bị recreate, ví dụ database data dir, upload directory hoặc cache cần giữ.

## Bind Mount

Bind mount nối một path cụ thể trên host vào container.

```bash
docker run --rm -it \
  -v /srv/app/config:/etc/app:ro \
  -v /srv/app/data:/var/lib/app \
  nginx
```

Lưu ý:

- Dùng `:ro` cho config chỉ đọc.
- Kiểm tra ownership/permission giữa host UID/GID và user trong container.
- Tránh mount nhầm thư mục nhạy cảm như `/`, `/etc`, `/var/run/docker.sock` nếu không có lý do bảo mật rõ ràng.
- Bind mount vào một path đã có sẵn trong image sẽ che khuất nội dung gốc tại path đó. Nếu mount nhầm vào thư mục quan trọng như `/bin`, `/lib`, `/usr` hoặc data directory application, container có thể lỗi khó hiểu hoặc ghi dữ liệu vào nơi khác với kỳ vọng.

Pre-check trước khi bind mount production:

```bash
test -d /srv/app/data
ls -ld /srv/app/data
docker image inspect <image>:<tag>
docker run --rm <image>:<tag> sh -c 'ls -ld /var/lib/app || true'
```

Với host dùng SELinux/AppArmor, lỗi `permission denied` có thể đến từ security label chứ không chỉ Unix permission. Kiểm tra audit log và policy nội bộ trước khi tắt cơ chế bảo vệ; không coi disable SELinux là fix production.

### Read-Only Host Inspection Container

Một số lúc cần inspect host filesystem bằng tool không muốn cài trực tiếp lên host. Có thể chạy tool container với bind mount read-only:

```bash
docker run --rm -it \
  --workdir /host \
  -v /:/host:ro \
  <debug-image>:<tag> sh
```

Pattern này chỉ nên dùng cho debug/forensic có kiểm soát. Dù mount read-only giảm rủi ro ghi nhầm, container vẫn có thể đọc nhiều file nhạy cảm trên host như config, log, key, token hoặc kubeconfig nếu quyền host cho phép. Không dùng với image không tin cậy, không chạy trên host multi-tenant nếu chưa có approval, và không mount read-write trừ khi có backup/rollback rõ ràng.

### `VOLUME` Trong Dockerfile

Instruction `VOLUME` khai báo mount point cho dữ liệu runtime, nhưng không phải cơ chế seed dữ liệu production. Nếu Dockerfile ghi file vào path đã được khai báo là volume ở bước sau, hành vi có thể gây nhầm lẫn vì dữ liệu runtime nằm ngoài image layer thông thường.

Guardrails:

- Khai báo rõ volume ở Compose/orchestrator hoặc lệnh run thay vì phụ thuộc hoàn toàn vào `VOLUME` ẩn trong base image.
- Không đặt migration, seed database hoặc artifact quan trọng vào path sẽ bị volume che khuất.
- Khi debug mất dữ liệu, kiểm tra cả image layer và mount thực tế bằng `docker inspect`.

## tmpfs Mount

`tmpfs` lưu dữ liệu trong memory của host và không ghi xuống disk.

```bash
docker run --rm \
  --tmpfs /run/app:rw,noexec,nosuid,size=64m \
  nginx
```

Phù hợp cho runtime scratch data, token tạm hoặc socket file không cần giữ sau khi container dừng.

## Chia Sẻ Dữ Liệu Giữa Container

Hai container có thể mount cùng một named volume:

```bash
docker volume create shared-data
docker run -d --name writer -v shared-data:/data busybox sleep 3600
docker run --rm -it --name reader -v shared-data:/data busybox sh
```

Với production, cần hiểu ứng dụng có hỗ trợ nhiều process ghi đồng thời hay không. Volume chỉ cung cấp nơi lưu dữ liệu; nó không tự giải quyết locking, consistency hoặc schema migration.

Có thể mount volume read-only cho consumer chỉ cần đọc:

```bash
docker run -d --name writer -v shared-data:/data busybox sleep 3600
docker run --rm --name reader -v shared-data:/data:ro busybox ls /data
```

Legacy pattern `--volumes-from` cho phép container mới dùng lại mount của container khác:

```bash
docker run --rm --volumes-from writer busybox ls /data
```

Pattern này hữu ích trong lab hoặc migration cũ, nhưng với production nên khai báo volume rõ ràng theo tên để dễ audit, backup và tái tạo.

Data-only container là biến thể legacy của `--volumes-from`: container giữ định nghĩa volume, còn container khác mount lại volume đó. Container data-only không cần đang chạy, chỉ cần còn tồn tại. Rủi ro chính là ownership không rõ, volume orphan khó truy vết và disk usage tăng âm thầm.

Validation khi gặp pattern này:

```bash
docker ps -a --filter name=<data-container>
docker inspect <data-container> --format '{{json .Mounts}}' | jq .
docker system df -v
```

Nếu nhiều container cùng ghi log hoặc file trạng thái vào cùng volume, mỗi writer phải có path riêng hoặc cơ chế locking rõ ràng. Volume chỉ chia sẻ filesystem; nó không tự bảo vệ khỏi truncate, overwrite, interleaved log hoặc corruption do concurrent writer.

## Volume Trong Swarm Hoặc Multi-Node

Local volume chỉ tồn tại trên node nơi container chạy. Nếu service trong Swarm có nhiều replica trên nhiều node, mỗi node có thể tạo volume cùng tên nhưng dữ liệu không tự đồng bộ.

Với workload cần dữ liệu chung giữa node, dùng backend storage phù hợp như NFS, SMB/CIFS, CephFS hoặc storage plugin được vận hành rõ ràng. Trước khi chạy production cần kiểm tra:

- Latency và throughput của backend.
- Cơ chế locking/consistency của application.
- Backup/restore.
- Hành vi khi node hoặc storage network lỗi.

### Remote Filesystem Mounts

Remote filesystem như NFS, SMB/CIFS, SSHFS hoặc CephFS có thể được mount trên Docker host rồi bind/named-volume vào container. Cách này tách trách nhiệm: host/storage layer xử lý kết nối remote, container chỉ thấy một mount point.

Pre-check:

```bash
mount | grep /mnt/app-data
df -hT /mnt/app-data
findmnt /mnt/app-data
touch /mnt/app-data/.write-test
rm /mnt/app-data/.write-test
```

Guardrails:

- SSHFS/FUSE tiện cho dev hoặc migration nhỏ, nhưng thường không phù hợp production latency-sensitive vì phụ thuộc user-space process, SSH session và network path.
- NFS nên được quản trị ở host/storage layer; tránh cài NFS client trong từng application container nếu không có lý do rất rõ.
- Ưu tiên read-only cho reference data hoặc dataset dùng chung.
- Thiết kế timeout/retry của application theo failure mode của storage; network filesystem treo có thể làm process container bị block.
- Backup phải chạy ở nơi hiểu dữ liệu thật nằm trên backend nào, không chỉ backup writable layer của container.

Rollback: trước khi đổi backend mount, dừng writer hoặc chuyển application sang read-only/maintenance mode, verify dữ liệu trên backend cũ và giữ mount cũ cho đến khi restore test thành công.

### Dev-Only History Và Dotfile Mounts

Khi dùng container như shell tạm thời, có thể mount riêng file history hoặc dotfile để giữ lại lệnh đã chạy. Pattern này chỉ nên dùng cho máy dev:

```bash
docker run --rm -it \
  -e HISTFILE=/root/.bash_history \
  -v "$HOME/.docker-shell-history":/root/.bash_history \
  ubuntu:<tag> bash
```

Không mount chung trực tiếp shell history chính của host vào container nếu có khả năng lệnh chứa token, registry password, kubeconfig path hoặc command production. Với team, nên dùng history file riêng cho container và định kỳ review/xóa thông tin nhạy cảm.

## Cleanup Và Rủi Ro

Lệnh này xóa volume không còn được container nào tham chiếu:

```bash
docker volume prune
```

Warning: chỉ chạy sau khi đã kiểm tra dữ liệu không còn cần thiết. Với môi trường production, ưu tiên liệt kê và backup trước.

```bash
docker volume ls
docker ps -a --filter volume=app-data
docker volume inspect app-data
```

## Troubleshooting

Kiểm tra mount của container:

```bash
docker inspect app --format '{{json .Mounts}}' | jq .
docker exec -it app df -h
docker exec -it app id
```

Triệu chứng thường gặp:

| Triệu chứng | Kiểm tra |
|---|---|
| Application báo permission denied | UID/GID, mode file, SELinux/AppArmor label |
| Dữ liệu mất sau recreate | Có mount volume đúng path dữ liệu không |
| Bind mount rỗng | Path host có tồn tại và đúng môi trường không |
| Multi-node không thấy dữ liệu | Volume local đang nằm trên node khác |

## Best Practices

- Dùng named volume cho dữ liệu application cần bền.
- Dùng bind mount cho source code dev, config file hoặc path host đã quản trị rõ.
- Dùng `:ro` cho config, certificate public, static file không cần ghi.
- Không lưu secret lâu dài trong bind mount không kiểm soát quyền.
- Ghi rõ backup/restore path cho volume chứa database hoặc user upload.

## Related Pages

- [Docker Overview](./01-docker/overview.md)
- [Docker Commands](./01-docker/00-docker-commands.md)
- [Docker Compose Services](./05-Docker%20Compose%20services.md)
- [Container Vs VM Concepts](./Container%20vs%20VM%20concepts.md)
