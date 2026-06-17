# Least Privilege Và Rootless Container

## Overview

Container isolation không tự động biến root trong container thành an toàn. Docker dùng namespace, cgroup, capability, seccomp, mount policy và MAC như SELinux/AppArmor để giảm blast radius, nhưng Docker daemon vẫn là boundary rất mạnh: ai điều khiển được Docker API thường có thể đạt quyền root-equivalent trên host.

Mental model:

```text
docker CLI/API -> dockerd -> containerd -> runc -> namespace/cgroup/capability/seccomp/MAC -> process
```

Least privilege cho container nghĩa là giảm quyền ở từng lớp thay vì chỉ tin vào image:

- user runtime không phải root nếu application cho phép;
- không mount path host nhạy cảm;
- drop Linux capabilities không cần thiết;
- dùng seccomp/AppArmor/SELinux profile phù hợp;
- tránh `--privileged`, host namespace và Docker socket;
- giới hạn CPU, memory, PID và filesystem write surface.

## Docker Socket Là Root-Equivalent

Quyền chạy `docker run` trên host production không phải quyền "developer convenience". Container có thể mount filesystem host hoặc Docker socket để điều khiển daemon.

Ví dụ nguy hiểm cần hiểu, không chạy trên production:

```bash
docker run --rm -v /:/host busybox sh -c 'find /host/etc -maxdepth 1 -type f'
```

Guardrails:

- Coi user trong group `docker` như host-admin.
- Không mount `/var/run/docker.sock` vào CI/CD job hoặc tool container trừ khi runner được xem là host-admin.
- Nếu cần build image, ưu tiên rootless/remote BuildKit, dedicated builder hoặc Kubernetes build pod có RBAC hẹp.
- Audit ai có quyền Docker socket và thu hồi quyền khi không còn cần.

## Linux Capabilities

Linux capabilities chia nhỏ một phần quyền root thành các quyền như `CAP_NET_ADMIN`, `CAP_SYS_ADMIN`, `CAP_SYS_PTRACE`, `CAP_CHOWN`. Docker đã drop một số capability mặc định, nhưng container vẫn có nhiều quyền hơn phần lớn application cần.

Baseline an toàn là drop tất cả rồi add lại quyền tối thiểu:

```bash
docker run --rm \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  --user 10001:10001 \
  <image>:<tag>
```

Production notes:

- `CAP_SYS_ADMIN` quá rộng; tránh cấp nếu không có review rất rõ.
- `CAP_NET_ADMIN` cho phép thay đổi network namespace/firewall; chỉ dùng cho workload hạ tầng.
- `CAP_SYS_PTRACE` có thể đọc/trace process; không bật mặc định cho app.
- Nếu application chỉ cần bind port thấp, cân nhắc dùng port cao bên trong container rồi map ở load balancer thay vì thêm capability.

Validation:

```bash
docker inspect <container> --format '{{json .HostConfig.CapAdd}} {{json .HostConfig.CapDrop}}'
docker exec <container> id
```

## Seccomp

Seccomp giới hạn syscall mà process được gọi vào kernel. Đây là lớp quan trọng vì container chia sẻ kernel với host.

Docker có default seccomp profile; workload nhạy cảm có thể dùng profile hẹp hơn:

```bash
docker run --rm \
  --security-opt seccomp=/path/to/seccomp-profile.json \
  <image>:<tag>
```

Guardrails:

- Tạo profile từ observation/dynamic analysis chỉ là điểm bắt đầu; phải chạy test coverage đủ rộng.
- Nếu profile quá hẹp, app có thể lỗi chỉ ở code path hiếm như TLS, DNS, crash handling, backup, locale hoặc plugin.
- Rollout profile mới bằng staging/canary trước khi áp production rộng.
- Khi bị `Operation not permitted`, kiểm tra syscall/seccomp cùng capability và MAC, không chỉ Unix permission.

## SELinux/AppArmor Cho Container

SELinux và AppArmor là Mandatory Access Control. Chúng giới hạn process được đọc/ghi/execute path nào, bind port nào hoặc dùng capability nào, kể cả khi Unix permission có vẻ cho phép.

Ví dụ Docker với SELinux label type tùy policy:

```bash
docker run --rm \
  --security-opt label:type:<selinux_type_t> \
  <image>:<tag>
```

Ví dụ Docker với AppArmor profile:

```bash
docker run --rm \
  --security-opt apparmor=<profile-name> \
  <image>:<tag>
```

Không tắt SELinux/AppArmor vĩnh viễn chỉ vì container lỗi. Quy trình đúng là đọc denial, xác nhận hành vi hợp lệ, sửa context/boolean/profile hoặc policy, rồi enforce lại.

## Rootless Và User Namespace

Rootless Docker hoặc user namespace remap giảm rủi ro bằng cách map root trong container sang user ít quyền hơn trên host. Đây là lớp giảm blast radius tốt, nhưng không loại bỏ nhu cầu hardening khác.

Điểm cần kiểm tra:

- workload có cần privileged port, device, overlay/network feature đặc biệt không;
- volume/bind mount có UID/GID mapping phù hợp không;
- logging, backup, monitoring và debug tool có chạy được với user remap không;
- CI/CD runner có phụ thuộc Docker socket rootful không.

Không coi rootless là lý do để bỏ scan image, capability drop, seccomp hoặc policy admission.

## Runtime Hardening Checklist

- `USER` trong Dockerfile hoặc `--user` ở runtime.
- `--cap-drop ALL`, add lại quyền cụ thể nếu cần.
- Không dùng `--privileged` cho app thường.
- Không dùng `--pid host`, `--network host`, `--ipc host` nếu không phải workload hạ tầng.
- Mount config read-only khi có thể.
- Dùng `--read-only` và tmpfs riêng cho path cần ghi nếu app tương thích.
- Giới hạn `--memory`, `--cpus`, `--pids-limit`.
- Dùng seccomp/AppArmor/SELinux profile phù hợp.
- Không mount Docker socket hoặc root filesystem host.

Ví dụ baseline:

```bash
docker run -d --name app \
  --user 10001:10001 \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --memory 512m \
  --pids-limit 256 \
  <image>:<tag>
```

Rollback: nếu hardening làm app fail, rollback bằng cách chạy lại version cấu hình runtime trước đó, không nới toàn bộ sang `--privileged`. Mở từng quyền một, ghi lý do, owner và thời hạn review.

## Troubleshooting

| Symptom | Kiểm tra |
|---|---|
| `permission denied` dù file mode đúng | UID/GID, bind mount owner, SELinux/AppArmor denial |
| `Operation not permitted` | capability thiếu, seccomp deny, MAC policy |
| App không bind được port 80 | dùng port cao hoặc thêm `NET_BIND_SERVICE` có review |
| Debug tool không chạy trong distroless/rootless | debug image, sidecar, ephemeral container hoặc log/trace tốt hơn |
| Container cần `--privileged` để chạy | xác định device/capability cụ thể; tránh cấp toàn bộ |

## Related Pages

- [Docker Overview](./01-docker/overview.md)
- [Docker Practice And Operations Patterns](./06-docker-practice-and-operations-patterns.md)
- [Container Vs VM Concepts](./Container%20vs%20VM%20concepts.md)
- [Image Scanning](./Image%20scanning%20%28Trivy,%20Clair%29.md)
- [SELinux, AppArmor](../../05-infrastructure-automation/02-security-and-hardening/02-os-and-network-security/SELinux,%20AppArmor.md)
- [Kubernetes Security, RBAC Và Pod Hardening](../03-container-orchestration/01-kubernetes/04-security/overview.md)
