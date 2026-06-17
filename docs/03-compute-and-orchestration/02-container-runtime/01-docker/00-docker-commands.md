# Các lệnh Docker thường gặp 

## `docker run`
- Đây là lệnh quan trọng nhất, dùng để khởi tạo và chạy một container từ một image. Khi bạn chạy `docker run hello-world`, Docker sẽ tìm image `hello-world` trên máy local, nếu không có nó sẽ tự động tải về từ Docker Hub, tạo một container từ image đó, chạy lệnh mặc định của image, in ra thông báo, và sau đó container kết thúc. 

+ Để chạy container ở chế độ nền (daemon), bạn sử dụng flag `-d`
```bash
docker run -d nginx
```

+ Để ánh xạ cổng, ví dụ ánh xạ cổng 80 của container ra cổng 8080 trên máy host của bạn, cho phép bạn truy cập ứng dụng qua `http://localhost:8080`
```bash
docker run -p 8080:80 nginx
```

+ Đặt một tên tùy chỉnh cho container thay vì một cái tên ngẫu nhiên
```bash
docker run --name my-nginx -p 8080:80 nginx
```
- Lệnh docker run không chỉ dừng lại ở việc chạy một container. Flag `-i` (interactive) và `-t` (tty) thường được kết hợp thành `-it` là cánh cửa để bạn tương tác trực tiếp với tiến trình bên trong container.

```bash
docker run -it ubuntu /bin/bash
```
> Lệnh đang khởi động container và ngay lập tức bước vào một shell bên trong nó, có thể nhập lệnh như đang ngồi trong một máy chủ Ubuntu thực thụ. Điều này cực kỳ hữu ích cho việc debug, kiểm tra môi trường hoặc thực hiện các thao tác thủ công.

- Flag `-v` (volume) là xương sống cho việc quản lý dữ liệu tồn tại vượt qua vòng đời của container. Nó cho phép bạn ánh xạ một thư mục từ máy host vào bên trong container. Cú pháp là `-v /đường/dẫn/trên/host:/đường/dẫn/trong/container`

```bash
docker run -v /home/user/app:/var/www/html nginx
```
+ Lệnh sẽ ánh xạ thư mục `/home/user/app` trên host vào thư mục `/var/www/html` trong container. Mọi thay đổi ở một bên sẽ lập tức phản ánh ở bên kia.

+ Đối với các đường dẫn sâu, nguyên tắc vẫn giữ nguyên

```bash
docker run -v /home/user/projects/my-app/src:/app/src -v /home/user/projects/my-app/logs:/app/logs my-python-app
```
Điều này cho phép bạn phát triển code trực tiếp trên host bằng IDE yêu thích, trong khi container chạy với code đó, đồng thời log của ứng dụng được lưu ra ngoài để phân tích ngay cả khi container đã bị xóa. 

+ Cũng có thể tạo và sử dụng các `named volume` (`docker volume create ten_volume`) để Docker quản lý dữ liệu thay vì ánh xạ trực tiếp đến host, phù hợp cho dữ liệu cơ sở dữ liệu
```bash
docker run -v ten_volume:/var/lib/mysql mysql
```


## `docker ps`

Lệnh này liệt kê trạng thái của tất cả các container đang chạy. Nó cung cấp thông tin quan trọng như Container ID, image được sử dụng, lệnh đang chạy, trạng thái, và các cổng được ánh xạ. Để xem tất cả container, bao gồm những container đã dừng, bạn cần thêm `flag -a `thành `docker ps -a`. Đây là công cụ chính để bạn theo dõi và quản lý vòng đời của các container trên hệ thống.

```bash
docker ps
docker ps -a
```

## `docker stop` và `docker rm`
- Hai lệnh này quản lý việc kết thúc và xóa bỏ container. 

+ Lệnh docker stop gửi một tín hiệu dừng (SIGTERM) để container tự tắt một cách có trật tự
```bash 
docker stop my_webserver
```
Nếu container không phản hồi, bạn có thể buộc dừng ngay lập tức bằng `docker kill`
+ Sau khi container đã dừng, nó vẫn còn tồn tại trên đĩa và chiếm dung lượng. Để xóa hoàn toàn container đó đi, bạn dùng lệnh `docker rm`
```bash
docker rm my_webserver
```

+ Có thể kết hợp cả hai thao tác này bằng cách sử dụng flag `-f` (force) trong lệnh `rm`
```bash
docker rm -f my_webserver
```

Lệnh này sẽ buộc dừng container đang chạy (như `kill`) và sau đó xóa nó ngay lập tức.

## `docker images` và `docker rmi`
- Lệnh docker images liệt kê tất cả các image đã được tải về hoặc tạo ra trên máy local của bạn. Nó hiển thị kho repository, tag, image ID, kích thước và thời gian tạo. 
- Để xóa một image không còn cần thiết, giải phóng dung lượng đĩa, bạn sử dụng lệnh docker rmi

```bash
docker images
docker rmi nginx:latest
```

> Lưu ý quan trọng: bạn không thể xóa một image nếu vẫn còn có container (dù đã dừng) đang tham chiếu đến nó. Bạn phải xóa container phụ thuộc trước hoặc dùng flag `-f `để buộc xóa, tuy nhiên việc dùng `-f` cần thận trọng.

## `docker pull`
- Lệnh này dùng để tải hoặc cập nhật một image từ một registry (mặc định là Docker Hub) về máy local của bạn mà không chạy nó ngay lập tức.

```bash
docker pull nginx # Sẽ tải bản lastest
docker pull ubuntu:20.04 # Tải chính xác phiên bản
```

Việc này rất hữu ích cho việc chuẩn bị image trước để đảm bảo bạn có đúng phiên bản cần thiết, giúp quá trình `docker run` sau đó diễn ra nhanh chóng vì không phải tải image về nữa.

## Append a command 
- Khi chạy một container, bạn có thể ghi đè lệnh mặc định được định nghĩa trong image bằng cách append command ở cuối lệnh `run`
+ Ví dụ, image ubuntu có lệnh mặc định là `bash`, nhưng nếu bạn sử dụng lệnh `sleep` thì container sẽ chạy lệnh `sleep` thay vì khởi động shell `bash`
```bash
docker run -d ubuntu sleep 1000
```
Lúc này, container sẽ chạy lệnh sleep 1000 thay vì khởi động shell bash.

## `docker exec`
- Lệnh này được sử dụng để chạy một lệnh bổ sung bên trong một container đang chạy. Đây là công cụ cực kỳ quan trọng cho việc debug và tương tác.
- Flag -it là phổ biến nhất, kết hợp -i (giữ cho stdin mở) và -t (cấp phát một pseudo-TTY), tạo ra một phiên tương tác. 
+ Ví dụ, để mở một shell bash bên trong một container đang chạy có tên my_webserver
```bash
docker exec -it my_webserver /bin/bash
```
+ Cũng có thể chạy các lệnh một lần (non-interactive) mà không cần shell
```bash
docker exec my_webserver nginx -t # lệnh kiểm tra cấu hình file của Nginx
```

## Chạy ở chế độ Attach và Detach

- Đây là hai chế độ chạy container cơ bản. Chế độ mặc định là `attach` (tiền cảnh), nơi bạn gắn terminal của mình vào output tiêu chuẩn (stdout/stderr) của container. Container sẽ chạy và bạn nhìn thấy mọi log ngay lập tức, và nếu bạn nhấn `Ctrl+C`, container sẽ dừng theo. 
- Ngược lại, chế độ `detach` (hậu cảnh) được kích hoạt bằng flag `-d`. Khi đó, container chạy nền như một daemon, giải phóng terminal của bạn cho các công việc khác.
```bash
docker run -d nginx
```

- Có thể chuyển đổi giữa hai chế độ này khi container đang chạy.Để thoát khỏi một phiên attached mà không dừng container, bạn sử dụng tổ hợp phím `Ctrl+P` kết hợp với `Ctrl+Q`. 
+ Để gắn kết lại terminal của bạn vào một container đang chạy ở chế độ detached

```bash
docker attach <container_name>
```
> `docker exec -it` thường được ưa thích hơn vì nó cung cấp một phiên tương tác mới

## `docker inspect`

- Lệnh trả về một lượng thông tin khổng lồ dưới dạng JSON, bao gồm cấu hình chi tiết, thông tin mạng, trạng thái, mount point, và cả địa chỉ IP.
- Để lọc thông tin cụ thể, bạn sử dụng flag `--format `

+ Để lấy địa chỉ IP của một container một cách nhanh chóng
```bash
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ten_container
```


## `docker logs`
- Khi container của bạn chạy ở chế độ detached (`-d`), đây là cách duy nhất để xem đầu ra (output) của nó.

```bash
docker logs ten_container
# Lệnh hiển thị toàn bộ log mà container đã ghi ra stdout/stderr kể từ khi nó được khởi chạy
```

- Flag `-f` (follow) cho phép bạn theo dõi log trong thời gian thực, giống như lệnh` tail -f`, rất quan trọng để giám sát ứng dụng
```bash
docker logs -f ten_container
```

- Flag `--tail N` sẽ chỉ hiển thị N dòng log cuối cùng, hữu ích để xem lỗi gần nhất một cách nhanh chóng
```bash
docker logs --tail 50 ten_container
```

- Flag `-t` (timestamps) sẽ thêm múi giờ vào mỗi dòng log, giúp bạn dễ dàng xác định thời điểm sự kiện xảy ra.
```bash
docker logs -t ten_container
```

## Image Lifecycle Và Di Chuyển Image

### `docker commit`

`docker commit` tạo image mới từ trạng thái hiện tại của container.

```bash
docker commit <container> <image-name>:<tag>
```

Lệnh này hữu ích trong lab hoặc khi cần snapshot tạm để phân tích. Với CI/CD hoặc production image, ưu tiên Dockerfile vì dễ review, tái tạo và audit hơn.

### `docker save` và `docker load`

Khi cần copy image qua môi trường không có registry, có thể export/import image dạng tar.

```bash
docker save --output app-image.tar <image-name>:<tag>
docker load -i app-image.tar
```

Với production, registry vẫn là cách chuẩn hơn vì có versioning, access control, audit log, scanning và replication.

### `docker export` và `docker import`

`docker export` tạo TAR từ filesystem của một container, còn `docker import` tạo image mới từ filesystem phẳng đó. Cặp lệnh này không giữ đầy đủ image history, label, config, layer metadata như `save/load`.

```bash
docker export <container> -o container-rootfs.tar
docker import container-rootfs.tar imported-image:<tag>
```

Guardrails:

- Dùng `save/load` khi muốn di chuyển image release nguyên vẹn.
- Dùng `export/import` chủ yếu cho lab, migration hoặc flatten có kiểm soát.
- Không dùng `export/import` để che việc image từng chứa secret; nếu secret đã vào layer hoặc artifact, phải rotate/revoke secret và rebuild sạch.
- TAR image/rootfs cần checksum/signature nếu chuyển qua môi trường khác.

### `docker tag` và `docker push`

Tag image theo registry/repository trước khi push:

```bash
docker tag app:local registry.example.com/project-a/app:<tag>
docker push registry.example.com/project-a/app:<tag>
```

Tránh dùng `latest` như release identity duy nhất. Nên có tag theo version, git SHA hoặc build number.

### `docker history`

Xem layer của image và lệnh tạo layer:

```bash
docker history <image-name>:<tag>
```

Lệnh này hữu ích khi image phình to bất thường hoặc cần biết layer nào thêm package/file lớn.

## Quan Sát Runtime

### `docker stats`

Theo dõi CPU, memory, network I/O và block I/O của container:

```bash
docker stats
docker stats <container>
```

### `docker top`

Xem process đang chạy trong container:

```bash
docker top <container>
```

### `docker diff`

Xem thay đổi trong writable layer của container:

```bash
docker diff <container>
```

Ký hiệu thường gặp:

- `A`: added
- `C`: changed
- `D`: deleted

### `docker cp`

Copy file giữa host và container:

```bash
docker cp <container>:/path/in/container ./local-path
docker cp ./local-file <container>:/path/in/container
```

Với dữ liệu quan trọng, không dùng `docker cp` thay cho backup strategy. Hãy xác định volume/backend lưu dữ liệu thật.

Có thể extract file từ image mà không cần container đang chạy bằng `docker create` rồi `docker cp`:

```bash
cid=$(docker create <image>:<tag>)
docker cp "$cid":/path/in/image ./local-copy
docker rm "$cid"
```

Pattern này hữu ích khi entrypoint của image khó override hoặc image start lỗi. Guardrails: chỉ đọc file cần thiết, không copy secret ra workspace chung, và xóa container tạm sau khi copy xong. Nếu image rất tối giản, cách này vẫn hoạt động vì `docker cp` đọc filesystem container từ daemon, không cần `cat` bên trong image.

## Restart Policy Và Log Rotation

Restart policy:

```bash
docker run -d --restart unless-stopped --name app <image>:<tag>
docker update --restart unless-stopped app
```

Cấu hình log rotation mặc định cho Docker daemon thường đặt trong `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Warning: restart Docker daemon có thể ảnh hưởng container đang chạy tùy cấu hình và môi trường. Kiểm tra maintenance window, backup và kế hoạch rollback trước khi đổi cấu hình production.

```bash
sudo systemctl restart docker
```
## Quản lý image
### `docker pull` - Tải image từ Docker Hub hoặc registry 

### `docker images` - Liệt kê các image đã tải 

### `docker build` - Tạo image từ Dockerfile 

### `docker tag` - Gắn thẻ mới cho image 

### `docker push` - Đẩy image lên Docker Hub

### `docker rmi` Xóa image khỏi local 

### `docker image inspect` - Xem chi tiết thông tin image 

### `docker commit` - Tạo image từ container đang chạy 

### `docker save` Xuất image ra file tar 

### `docker load` - Import image từ file tar

### `docker image prune` - Xóa image không còn sử dụng 

## Quản lý Container 
### `docker ps` - Liệt kê container đang chạy 

### `docker rm` - Xóa container đã dừng 

### `docker create` - Tạo container nhưng không chạy 

### `docker rename` - Đổi tên container 

### `docker kill` - Force stop container ngay lập tức 

### `docker wait` - Chờ container dừng và trả về exit code 

### `docker run` - Tạo và khởi động container mới 

### `docker start` - Khởi động container đã tạo 

### `docker stop` - Dừng container đang chạy

### `docker restart` - Khởi động lại container

### `docker pause` - Tạm dừng container 

### `docker unpause` - Tiếp tục container đã pause 

## Thao tác trong container 

### `docker exec` - Chạy lệnh bên trong container đang chạy 

### `docker attach` - Gắn terminal vào tiếng trình chính của container 

### `docker logs` - Xem log xuất ra từ container 

### `docker top` - Liệt kê tiến trình đang chạy trong container 

### `docker inspect` - Xem chi tiết thông tin container (JSON)

### `docker stats` - Theo dõi tài nguyên container theo thời gian thực 


### `docker cp` - Copy file giữa container và host 


### `docker diff` - Xem những thay đổi trong filesystem container


## Dọn dẹp hệ thống
### `docker system df` - Xem tổng dung lượng Docker đang dùng 

### `docker system prune` - Xóa container, network, image không sử dụng 

Warning: `prune` có thể xóa dữ liệu/metadata bạn vẫn cần cho rollback hoặc debug. Luôn chạy lệnh quan sát trước:

```bash
docker system df
docker container ls -a
docker image ls
docker volume ls
docker network ls
```

### `docker container prune` - Xóa tất cả container đã dừng 

### `docker image prune` - Xóa image 'dangling'(lơ lửng không gắn tag hay liên kết bất kỳ container nào đang hoạt động, thường xuất hiện ở dạng <none>:<none>) hoặc không dùng đến 

### `docker network prune` - Xóa mạng không còn gắn container nào

## Related Pages

- [Docker Overview](./overview.md)
- [Image Layer, Dockerfile Best Practices](../Image%20layer,%20Dockerfile%20best%20practices.md)
- [Volumes, Bind Mount, tmpfs](../04-Volumes,%20Bind%20mount,%20tmpfs.md)
- [Network Mode Bridge, Host, Overlay](../03-Network%20mode%20bridge,%20host,%20overlay.md)
- [Docker Compose Services](../05-Docker%20Compose%20services.md)
