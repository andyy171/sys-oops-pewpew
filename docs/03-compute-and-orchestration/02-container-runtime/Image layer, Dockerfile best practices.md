# Image Layer Và Dockerfile Best Practices

## Overview

Docker image là tập hợp các layer read-only. Mỗi instruction trong Dockerfile thường tạo thêm một layer mới. Khi container chạy, Docker thêm một writable layer mỏng phía trên image để lưu thay đổi runtime.

Mục tiêu khi viết Dockerfile là tạo image:

- reproducible: build lại cho kết quả dự đoán được
- nhỏ vừa đủ
- ít chứa secret/tool thừa
- tận dụng cache hợp lý
- chạy bằng user ít quyền khi có thể

## Image Layer Mental Model

Một image thường gồm:

- **Base image layer**: root filesystem nền.
- **Application dependency layer**: package, runtime, library.
- **Application code layer**: code/config được copy vào image.
- **Image config**: entrypoint, command, env, working dir, exposed port.

Layer được address bằng digest. Nhiều image có thể share cùng layer, vì vậy registry và host có thể tiết kiệm dung lượng nếu build/tag hợp lý.

## Dockerfile Cơ Bản

Ví dụ tối giản:

```dockerfile
FROM <base-image>:<tag>

WORKDIR /app
COPY . /app

RUN <install-dependencies-command>

EXPOSE 8080
USER 10001
ENTRYPOINT ["./app"]
```

Các instruction thường gặp:

| Instruction | Ý nghĩa |
|---|---|
| `FROM` | Chọn base image |
| `COPY` / `ADD` | Đưa file vào image; ưu tiên `COPY` nếu không cần tính năng đặc biệt của `ADD` |
| `RUN` | Chạy lệnh trong lúc build image |
| `ENV` | Đặt environment variable mặc định |
| `WORKDIR` | Đặt thư mục làm việc |
| `USER` | Chọn user runtime |
| `EXPOSE` | Ghi metadata port, không tự publish port ra host |
| `ENTRYPOINT` / `CMD` | Lệnh mặc định khi container chạy |
| `HEALTHCHECK` | Định nghĩa lệnh kiểm tra sức khỏe application |
| `ONBUILD` | Trigger instruction chạy khi image được dùng làm base cho image khác |

### `COPY` Vs `ADD`

Ưu tiên `COPY` cho hầu hết trường hợp vì hành vi rõ ràng: copy file/folder từ build context vào image. Dùng `ADD` khi thật sự cần một tính năng đặc biệt:

- tự giải nén local tar archive vào image;
- lấy nội dung từ URL trong lúc build;
- tận dụng thay đổi nội dung remote resource để bust cache có chủ ý.

Guardrails:

- `ADD` local tar archive có thể tự unpack, nhưng `ADD <url>` thường tải file về thay vì tự giải nén như local tar. Đừng dựa vào hành vi này nếu chưa test rõ.
- Remote `ADD` làm build phụ thuộc network, DNS, TLS và availability của endpoint; production build nên pin version/digest/checksum khi có thể.
- File được thêm vào image có thể mang owner/permission không như mong muốn. Kiểm tra UID/GID và quyền đọc/execute trước khi chạy non-root.
- Nếu chỉ muốn đưa source/config vào image, dùng `COPY`.

## Build Context Và Reproducibility

`docker build <path>` không chỉ đọc Dockerfile. Docker client gửi build context trong `<path>` cho builder, sau đó các instruction như `COPY` và `ADD` chọn file từ context đó. Nếu context chứa `.git`, secret, log, cache dependency hoặc artifact lớn, image có thể phình to, build chậm và lộ dữ liệu nhạy cảm.

Checklist:

- Đặt Dockerfile gần source cần build, nhưng giữ context cắt gọn.
- Dùng `.dockerignore` để loại `.git`, `.env`, key, test output, local cache và binary artifact không cần thiết.
- Tách bước copy dependency manifest và bước copy source code để cache build có ý nghĩa.
- Không clone private repository bằng token trong Dockerfile nếu token có thể rớt vào layer/history. Dùng BuildKit secret mount hoặc pipeline checkout bên ngoài image.
- Build output phải truy vết được về commit/build ID; trạng thái thủ công trong container không thay thế Dockerfile.

## ENTRYPOINT Vs CMD

`ENTRYPOINT` thường dùng cho executable chính của image. `CMD` thường dùng làm default argument hoặc command mặc định có thể override.

```dockerfile
ENTRYPOINT ["/usr/local/bin/app"]
CMD ["--config", "/etc/app/config.yaml"]
```

Khi chạy:

```bash
docker run app-image --config /etc/app/other.yaml
```

Argument phía sau `docker run` có thể thay phần `CMD` nhưng vẫn giữ `ENTRYPOINT`.

Khi image được dùng như một CLI/tool đóng gói sẵn, `ENTRYPOINT` giúp cố định executable còn `CMD` cung cấp default argument. Với tool có thể thay đổi hoặc xóa dữ liệu, entrypoint script vẫn phải validate input rõ ràng; không dựa vào `CMD` default như guardrail duy nhất.

Guardrails cho tool image:

- Dùng exec-form cho `ENTRYPOINT`/`CMD` để signal forwarding rõ hơn.
- Có `--help`, `--dry-run` hoặc mode read-only mặc định nếu tool thao tác dữ liệu.
- Không mount thư mục production vào tool container nếu chưa kiểm tra quyền ghi và rollback.
- Ghi rõ path nào container sẽ đọc/ghi khi người dùng mount volume.

## Tối Ưu Layer Và Cache

Nguyên tắc:

- Copy dependency manifest trước, install dependency, sau đó mới copy toàn bộ source code để tận dụng cache.
- Gom các lệnh package install/cleanup liên quan vào cùng một `RUN`.
- Không để cache package manager, build artifact hoặc file tạm trong final image.
- Dùng `.dockerignore` để tránh copy `.git`, log, secret, build output không cần thiết.

Ví dụ pattern:

```dockerfile
FROM <runtime-base>:<tag>

WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY . .
USER 10001
CMD ["npm", "start"]
```

### Cache Invalidation Có Kiểm Soát

Docker build cache giúp build nhanh, nhưng cũng có thể giấu lỗi nếu một bước download/clone/package install thay đổi ở ngoài Dockerfile. Các mức xử lý:

| Cách | Khi dùng | Rủi ro |
|---|---|---|
| `docker build --no-cache` | sanity check build từ đầu hoặc nghi cache bẩn | chậm, tốn network/compute, không phù hợp mọi build CI |
| đổi instruction hoặc comment có chủ ý | bust cache từ một dòng cụ thể khi đang debug | dễ để lại thay đổi noise trong Dockerfile |
| `ARG CACHEBUST=<value>` | bust cache theo tham số từ CI/lệnh build | nếu lạm dụng sẽ làm cache mất tác dụng |
| remote checksum/version marker | chỉ bust cache khi upstream đổi | phụ thuộc endpoint marker đáng tin cậy |

Ví dụ dùng build arg có kiểm soát:

```dockerfile
ARG CACHEBUST=stable
RUN npm ci --omit=dev
```

```bash
docker build --build-arg CACHEBUST="$(date +%Y%m%d%H%M%S)" .
```

Best practice production:

- Với dependency quan trọng, pin version hoặc lockfile thay vì luôn lấy "mới nhất".
- Chạy periodic no-cache build trong CI để phát hiện dependency/network assumption bị che bởi cache.
- Không dùng `RUN git clone <branch>` làm nguồn build chính nếu có thể checkout source ở CI rồi `COPY` vào context; cách này dễ audit commit hơn.
- Nếu dùng remote marker để bust cache, marker phải ổn định và phản ánh đúng artifact cần rebuild, tránh HTML/API response thay đổi vì timestamp hoặc tracking token.

### Package Drift Và Dependency Pinning

Dockerfile làm build rõ ràng hơn, nhưng không tự bảo đảm reproducible nếu package repository bên ngoài thay đổi. Các lệnh kiểu `apt-get install nginx` hoặc `apk add curl` có thể tạo image khác nhau ở hai thời điểm khác nhau.

Production guardrails:

- Pin base image bằng digest hoặc tag theo policy nội bộ.
- Dùng lockfile cho language dependency như `package-lock.json`, `poetry.lock`, `Gemfile.lock`, `go.sum`.
- Với OS package quan trọng, pin version hoặc dùng repository snapshot/mirror nội bộ thay vì lấy trực tiếp “latest” từ internet.
- Chạy scheduled rebuild để phát hiện CVE và dependency drift, nhưng promote bằng tag/digest immutable sau khi test.
- Khi pin version quá chặt làm build fail vì package bị gỡ khỏi repo, coi đó là tín hiệu review thay đổi dependency, không tự động nới version trong production pipeline.

Ví dụ Debian/Ubuntu:

```dockerfile
RUN apt-get update \
  && apt-get install -y --no-install-recommends nginx=<version> \
  && rm -rf /var/lib/apt/lists/*
```

Không pin package chỉ để “đóng băng mãi mãi”; cần có quy trình cập nhật định kỳ, scan và rollback.

## Multi-Stage Build

Multi-stage build giúp tách môi trường build khỏi môi trường runtime.

```dockerfile
FROM <builder-image>:<tag> AS builder
WORKDIR /src
COPY . .
RUN <build-command>

FROM <runtime-image>:<tag>
WORKDIR /app
COPY --from=builder /src/dist /app
USER 10001
CMD ["./app"]
```

Lợi ích:

- Final image nhỏ hơn.
- Không mang compiler, build cache hoặc source không cần thiết vào runtime.
- Giảm surface area bảo mật.

### Secrets Trong Build Layer

Secret đã từng xuất hiện trong một layer thì việc xóa ở layer sau không làm secret biến mất khỏi image history. Nếu Dockerfile copy SSH key, token, certificate hoặc `.env` rồi `rm` ở bước sau, secret vẫn có thể bị trích xuất từ layer cũ.

Guardrails:

- Không đưa secret vào build context; dùng `.dockerignore` cho `.env`, key, kubeconfig, cache và artifact nhạy cảm.
- Dùng BuildKit secret mount hoặc CI checkout bên ngoài image khi cần truy cập private dependency.
- Không truyền secret qua `ARG`/`ENV` nếu secret có thể xuất hiện trong history, logs hoặc metadata.
- Nếu phát hiện secret đã vào image layer: revoke/rotate secret trước, xóa image khỏi registry/cache theo quy trình incident, rebuild sạch từ Dockerfile. Không coi flatten/export-import là biện pháp xử lý đủ cho production.

Ví dụ BuildKit secret mount:

```dockerfile
# syntax=docker/dockerfile:1.6
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
  npm ci --omit=dev
```

```bash
docker build --secret id=npmrc,src=.npmrc -t app:<tag> .
```

Flatten image bằng `docker export | docker import` có thể làm mất history layer, nhưng cũng làm mất metadata, cache benefit, provenance và có thể che khuất vấn đề supply chain. Chỉ dùng như kỹ thuật migration/lab có kiểm soát, không dùng để “rửa” secret đã lộ.

### Build Orchestration

Dockerfile nên là nguồn mô tả image chính, nhưng pipeline có thể dùng Makefile, shell script, Ansible, Chef hoặc tool build khác để chuẩn bị context, render template, chạy test và gọi `docker build`.

Guardrails:

- Build orchestration phải nằm trong Git và review được như source code.
- Build context phải explicit; tránh gửi cả workspace lớn chứa secret, cache hoặc repository không liên quan.
- Biến build phải có default an toàn và được ghi vào build metadata/tag nếu ảnh hưởng artifact.
- Không để Makefile/script sinh Dockerfile tạm rồi quên commit thay đổi quan trọng.
- Output artifact lấy ra từ container build nên có checksum và owner/permission rõ ràng.

## Base Image Strategy

Chọn base image là trade-off giữa size, security và khả năng debug:

- **distroless** giảm package manager, shell và tool thừa trong runtime image, phù hợp workload đã có observability/debug path tốt;
- **slim/optimized image** như Debian Slim hoặc Alpine giảm kích thước nhưng vẫn dễ debug hơn distroless;
- **full OS image** dễ tương thích với chuẩn enterprise, nhưng thường kéo theo attack surface và thời gian pull lớn hơn.
- **scratch/static binary** phù hợp binary tự đủ dependency như một số Go/Rust/C app static-linked, nhưng cần tự lo CA certificates, timezone data, user, DNS behavior và debug path.

Một lộ trình thực tế là bắt đầu với base image quen thuộc, sau đó chuyển dần sang slim image, rồi distroless khi team đã có logging, tracing, debug sidecar hoặc ephemeral container workflow đủ tốt. Không nên chọn distroless chỉ vì nhỏ nếu incident response vẫn phụ thuộc vào shell bên trong container.

Image nhỏ không luôn tốt hơn. Nếu nhiều team dùng chung cùng runtime/package baseline, một base image nội bộ lớn nhưng ổn định có thể tiết kiệm bandwidth nhờ layer sharing và giảm drift. Điều kiện bắt buộc là base image phải có owner, changelog, scan, regression test và lịch phát hành rõ ràng; nếu không, nó sẽ trở thành “golden image” khó nâng cấp.

### Base Image Ownership Trong Platform

Base image nội bộ là product của platform team, không phải file nền vô chủ. Nó cần contract rõ với application team:

- image gồm runtime/package nào, version policy ra sao;
- ai xử lý CVE và rebuild khi upstream phát hành patch;
- lịch release, deprecation và migration window;
- test compatibility tối thiểu trước khi promote base image mới;
- cơ chế ép hoặc nhắc workload rebuild khi base image cũ hết hạn.

Mô hình tốt là platform team sở hữu base image và pipeline phát hành, còn application team sở hữu rebuild/test ứng dụng. Nếu platform tự động rebuild hàng loạt image ứng dụng, cần dry-run, canary, rollback và audit vì thay đổi base layer có thể làm app fail dù source code không đổi.

### Image Size Optimization

Ưu tiên giảm size bằng thiết kế build thay vì sửa tay trong container:

- chọn base image phù hợp;
- dùng multi-stage build;
- bỏ package manager/build tool khỏi final stage;
- clean package cache trong cùng layer cài đặt;
- dùng `.dockerignore`;
- scan và đo size trước/sau bằng `docker history` hoặc tool SBOM/layer analyzer.

Manual slimming bằng cách vào container rồi xóa package/file chỉ nên dùng để học hoặc điều tra. Nếu muốn đưa vào production, chuyển kết quả thành Dockerfile/multi-stage build có test. Những kỹ thuật dựa trên quan sát file access như `inotifywait` dễ xóa nhầm file chỉ cần ở code path hiếm, locale khác, TLS CA, timezone hoặc tình huống lỗi.

### Dynamic Slimming Và Runtime Profile

Một số tool có thể chạy application trong giai đoạn học để suy ra file nào được đọc và syscall nào được dùng, sau đó tạo image nhỏ hơn hoặc seccomp/AppArmor profile hẹp hơn. Ý tưởng này hữu ích để giảm attack surface, nhưng rủi ro chính là coverage.

Production guardrails:

- Chỉ dùng kết quả dynamic profiling nếu test đã đi qua các endpoint, job nền, error path, TLS/DNS path, backup/restore path và plugin thường gặp.
- Không dùng profile sinh tự động như policy cuối cùng nếu chưa review.
- Canary trước khi rollout rộng, vì profile thiếu syscall/file có thể chỉ fail dưới tải hoặc trong tình huống lỗi.
- Giữ rollback về image/profile trước đó.
- Vẫn cần SBOM, scan, provenance và secret handling; image nhỏ không đồng nghĩa image an toàn.

### Foreign Package Conversion

Convert package giữa distro, ví dụ `.deb` sang `.rpm`, là best-effort và nên là ngoại lệ. Production nên ưu tiên:

- package native cho distro đang dùng;
- upstream image chính thức hoặc vendor-supported package;
- build package từ source với checksum/signature rõ;
- đổi base image nếu dependency chính thuộc distro khác.

Nếu buộc phải convert package, cần kiểm tra maintainer script, dependency, signature/checksum, license và scan vulnerability sau khi install. Không coi conversion tool là supply-chain boundary.

## Image Tagging In CI/CD

Image tag phải giúp trả lời "artifact này đến từ commit/build nào". Các tag hữu ích thường gắn với:

- Git commit SHA;
- build ID của CI system;
- release version;
- kết hợp `git-sha-build-id` nếu cần truy vết cả source và pipeline run.

Không dùng `latest` làm tag production. `latest` là alias mutable, không đủ để audit, diff, promote hay rollback. Với workload quan trọng, ưu tiên deploy bằng image digest hoặc tag immutable do registry policy bảo vệ.

## USER, Capability Và Port Privileged

`USER` trong Dockerfile chọn user mặc định khi container chạy. Đây là lớp giảm blast radius quan trọng, nhưng cần thiết kế UID/GID và permission volume ngay từ đầu.

```dockerfile
RUN addgroup --system app && adduser --system --ingroup app app
USER app
```

Lưu ý:

- User non-root không bind được port thấp như `80` nếu thiếu capability phù hợp; thường chọn port cao như `8080` bên trong container rồi publish ra `80` ở host/load balancer.
- Bind mount từ host có thể gây `permission denied` nếu UID/GID trong container không khớp owner trên host.
- Không dùng `--privileged` để "sửa nhanh" permission hoặc device access nếu chưa hiểu quyền cần cấp.

`ONBUILD` có thể tiện cho base image nội bộ, nhưng dễ tạo hành vi ẩn: image con build sẽ chạy instruction mà maintainer Dockerfile con không nhìn thấy trực tiếp trong file của họ. Chỉ dùng khi team có convention rõ và tài liệu hóa base image.

## Timezone, Locale Và Encoding Trong Image

Container dùng kernel clock của host, nhưng cách application diễn giải thời gian, timezone, locale và encoding đến từ file/environment bên trong image hoặc runtime environment. Minimal image có thể thiếu locale mặc định, dẫn tới lỗi kiểu `UnicodeEncodeError`, `unmappable character`, `ASCII`, `UTF-8` hoặc format ngày giờ khác giữa dev và production.

Khuyến nghị:

- Ưu tiên log và lưu timestamp bằng UTC; convert timezone ở presentation layer khi có thể.
- Nếu app cần timezone cụ thể, cấu hình rõ `TZ` hoặc `/etc/localtime` trong image/runtime theo policy của platform.
- Cấu hình locale/encoding rõ ràng, thường là UTF-8, đặc biệt với app xử lý text, report, CSV, PDF hoặc tên file đa ngôn ngữ.
- Test build/runtime với dữ liệu có ký tự ngoài ASCII để phát hiện lỗi encoding sớm.

Ví dụ:

```dockerfile
ENV TZ=UTC
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
```

Với base image không có locale mong muốn, cần cài/generate locale theo distro. Không assume Ubuntu/Debian/Alpine/distroless có cùng bộ locale hoặc timezone data.

## docker commit Chỉ Nên Dùng Có Kiểm Soát

`docker commit` tạo image từ trạng thái hiện tại của container:

```bash
docker commit <container> debug-image:manual
```

Lệnh này hữu ích cho lab hoặc snapshot tạm khi debug, nhưng không nên là cách build image chính trong CI/CD vì khó review, khó reproduce và dễ đưa thay đổi thủ công vào production. Với image chính thức, hãy viết Dockerfile và lưu trong version control.

Giới hạn quan trọng:

- `docker commit` chỉ capture filesystem diff trong container, không capture process đang chạy, memory state, socket, file descriptor hoặc timer runtime.
- Volume, bind mount, database bên ngoài, object storage, queue và service dependency không nằm trong image commit.
- Shell history hoặc file tạm có thể vô tình rơi vào image; kiểm tra secret trước khi tag/push.
- Nếu commit dùng để giữ trạng thái debug, tag image bằng tên tạm rõ ràng và cleanup sau khi RCA/triage xong.

Không dùng `docker commit` như chiến lược backup chính. Commit container đang chạy có thể pause container, chỉ lưu filesystem diff của container, không bảo vệ database/volume/object storage bên ngoài, không có consistency point rõ và dễ làm mất provenance. Nếu bắt buộc snapshot để forensic/RCA, làm theo maintenance/incident workflow: ghi thời điểm, image digest gốc, container id, volume liên quan, log evidence, người thực hiện và retention; sau đó vẫn phải backup dữ liệu bằng cơ chế của backend thật.

## Inspect Và Debug Image

```bash
docker image ls
docker image inspect <image>
docker history <image>
docker diff <container>
```

`docker history` giúp thấy layer nào làm image phình to. `docker diff` giúp thấy container đã ghi thêm file gì so với image gốc.

Khi image nhiều tag/layer và khó nhìn quan hệ kế thừa, có thể xuất metadata bằng các công cụ chuẩn trước khi dùng tool vẽ graph:

```bash
docker image ls -a
docker history <image>
docker image inspect <image>
```

Nếu dùng tool graph/visualizer chạy trong container, coi việc mount `/var/run/docker.sock` là cấp quyền root-equivalent trên host. Chỉ chạy tool đã trust, pin image version/digest, chạy trên host lab nếu có thể và không dùng output graph thay cho SBOM hoặc vulnerability scan.

Khi cần debug file xuất hiện ở layer nào, ưu tiên `docker history`, BuildKit output, SBOM/layer analyzer hoặc build lại với stage rõ ràng. Tránh chạy tool lạ với mount `/var/run/docker.sock` chỉ để inspect layer nếu chưa trust tool đó.

## Best Practices

- Pin base image theo tag rõ ràng hoặc digest cho workload quan trọng.
- Không dùng `latest` trong production pipeline nếu cần rollout/rollback dự đoán được.
- Không copy secret vào image; dùng secret manager hoặc runtime secret.
- Chạy container bằng non-root user khi ứng dụng cho phép.
- Tách build stage và runtime stage.
- Scan image trước khi push/deploy.
- Ghi rõ `ENTRYPOINT`, `CMD`, port, config path và health check ở tài liệu vận hành.

## Related Pages

- [Docker Overview](./01-docker/overview.md)
- [Docker Commands](./01-docker/00-docker-commands.md)
- [Private Registry, Nexus, Harbor](./Private%20registry,%20NexusHarbor.md)
- [Least Privilege & Rootless Container](./Least%20privilege%20&%20rootless%20container.md)
- [Image Scanning](./Image%20scanning%20%28Trivy,%20Clair%29.md)
