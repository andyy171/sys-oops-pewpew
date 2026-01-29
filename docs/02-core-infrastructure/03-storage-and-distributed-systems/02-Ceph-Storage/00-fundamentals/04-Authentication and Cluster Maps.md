
# Cluster Maps

![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/cluster-map.png)

Cluster maps là "GPS" giúp client và OSD biết vị trí dữ liệu. MON duy trì và phân phối.

- **OSD Map**: Liệt kê tất cả OSD (ID, trạng thái up/in).
    
    **Cơ chế vận hành**: Cập nhật khi OSD join/leave.
    
- **CRUSH Map**: Định nghĩa cấu trúc cluster (host, rack) và rule phân bổ.
    
    **Cơ chế vận hành**: Dùng để tính vị trí PG.
    
- **PG Map**: Vị trí từng PG (OSD nào là primary/replicas).
    
    **Cơ chế vận hành**: Giúp client đọc/ghi trực tiếp OSD mà không qua MON.
    
    **Ví dụ**: OSD Map như danh sách địa điểm, CRUSH Map như tuyến đường.

- **Monitor Map** chứa cluster fsid, vị trí, tên, địa chỉ và TCP port của mỗi monitor, cùng với epoch và thời gian tạo/sửa đổi



## Authentication
CephX Authentication Model
- **CephX** là **cơ chế xác thực nội bộ của Ceph**, được thiết kế tương tự **Kerberos** nhằm đảm bảo mọi giao tiếp giữa client và daemon đều được **xác minh danh tính và bảo vệ an toàn**.
- Cơ chế hoạt động như sau: **Client gửi yêu cầu xác thực đến Monitor (MON)** bằng cặp username/secret key. Nếu hợp lệ, MON **cấp một session ticket (keyring)** có thời hạn; client dùng ticket này để **ký và xác thực các yêu cầu** tới OSD, MDS hay MON khác mà không cần gửi lại mật khẩu.
- Cách làm này giống như **mua vé vào rạp**: người dùng lấy vé từ quầy (MON) rồi dùng nó để ra vào rạp (OSD). CephX giúp **ngăn truy cập trái phép**, **giảm rủi ro lộ khóa**, hỗ trợ **ACL và LDAP**, và được **kích hoạt mặc định trong mọi cụm Ceph**.

#### Authentication flow
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/authentication-flow.png)

Quy trình :
1. Client đọc file `/etc/ceph/ceph.conf` để tìm địa chỉ các monitor.
2. Tải file keyring (ví dụ: `/etc/ceph/ceph.client.admin.keyring`).
3. Kết nối đến một monitor và trình bày thông tin xác thực (credentials).
4. Monitor xác thực bằng cơ chế CephX.

```
Configuration Files

## /etc/ceph/ceph.conf
[global]
mon_host = 10.10.1.11,10.10.1.12,10.10.1.13
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx

## /etc/ceph/ceph.client.admin.keyring
[client.admin]
key = AQbVaBB1AAAABBAAH1kcPMpLVPUP7rGRQxQ==
caps mon = "allow *"
caps osd = "allow *"
caps mds = "allow *"
```

- Cluster Máp nhận được :
```
Maps Received:

Monitor Map: List of all monitors (epoch: 3)

OSD Map: All OSDs, their state, pools (epoch: 547)

CRUSH Map: Topology and placement rules

PG Map: Placement group states (if needed)

```

- Client-Side Calculation
```
CRUSH Calculation Process:
1. Split data: Break into 4MB objects

2. Hash object name: hash(object_name) % pg_num = PG_ID

3. CRUSH(PG_ID): Returns OSD list [primary, secondary1, secondary2]

4. No network call needed! All calculated locally
```

```
Example Calculation
## Object: rbd_data.1234.00000001
## Pool: rbd-pool (pg_num=128, size=3)

hash("rbd_data.1234.00000001") => 0x7a3b9c
0x7a3b9c % 128 = 47 ## PG 1.2f

CRUSH(PG 1.2f) -> [OSD.5, OSD.2, OSD.8]
                 ^ Primary
```
- Phân tích ví dụ : 
  + Đầu vào: Đối tượng cần tìm là rbd_data.1234.00000001 nằm trong rbd-pool có 128 PG (pg_num=128) và 3 bản sao (size=3).

  + Bước 1 (Băm): Tên đối tượng được băm ra giá trị 0x7a3b9c (giá trị thập lục phân).

  + Bước 2 (Tìm PG): Giá trị băm được lấy phần dư cho 128: 0x7a3b9c % 128 = 47. Trong Ceph, 47 được biểu diễn dưới dạng PG 1.2f (ký hiệu pool ID và PG ID).

  + Bước 3 (Tìm OSD): Thuật toán CRUSH nhận PG 1.2f và tính toán ra danh sách OSD: [OSD.5, OSD.2, OSD.8].

  => Kết luận: Máy khách biết rằng OSD 5 là OSD chính (Primary), và OSD 2, OSD 8 giữ các bản sao (replica). Máy khách sẽ kết nối trực tiếp với OSD.5 để thực hiện thao tác đọc/ghi.


- Sao chép song song :
Bước này là khâu thực hiện thao tác ghi (write) dữ liệu vào cụm Ceph, dựa trên vị trí OSD đã được tính toán ở Bước trước đó.

1. Tiếp nhận và Ghi cục bộ:

  + OSD Chính (Primary OSD) nhận đối tượng dữ liệu từ máy khách.

  + Nó lập tức ghi dữ liệu vào journal (nhật ký) hoặc đĩa cục bộ của nó.

2. Sao chép Song song:

  + Ngay sau khi ghi cục bộ, OSD Chính đồng thời gửi các bản sao (replicas) của đối tượng đến tất cả các OSD thứ cấp (Secondary OSDs) được xác định bởi CRUSH Map.

3. Đảm bảo Nhất quán (Consistency):

  + OSD Chính phải chờ xác nhận (ACK) từ TẤT CẢ các OSD thứ cấp rằng họ đã ghi dữ liệu thành công.

4. Phản hồi Máy khách:

  + Chỉ sau khi nhận được xác nhận từ tất cả các bản sao (bao gồm cả ghi thành công trên OSD Chính), OSD Chính mới gửi một tín hiệu ACK (Acknowledgement) duy nhất trở lại máy khách. Tín hiệu này báo hiệu rằng thao tác ghi đã hoàn tất và an toàn trong cụm.



### Capabilities & authorization
Capabilities (hay còn gọi là "caps") là cách Ceph kiểm soát quyền truy cập của người dùng hoặc client đối với các dịch vụ như MON, OSD, MDS, MGR. Chúng định nghĩa những hành động nào được phép thực hiện, như đọc (read), viết (write) hoặc thực thi (execute).

- Capabilities được viết dưới dạng chuỗi: `dịch_vụ 'allow <hành_động>'`. Các hành động phổ biến:
    `allow *`: Quyền đầy đủ.
    `allow rwx`: Đọc, viết, thực thi.
    `allow profile <dịch_vụ>`: Quyền mặc định cho dịch vụ (ví dụ: `profile osd` cho OSD).

Bạn có thể giới hạn quyền theo pool hoặc namespace cụ thể, ví dụ: `osd 'allow rw pool=liverpool'`.

- Khi client kết nối, CephX kiểm tra capabilities trong keyring để xác nhận quyền. Nếu không có quyền phù hợp, yêu cầu sẽ bị từ chối. Điều này giúp bảo mật, chỉ cho phép người dùng làm những gì cần thiết.


### User management
- User trong Ceph là các thực thể như `client.admin`, osd.0, dùng để xác thực. Mỗi user có key và capabilities liên kết. Quản lý user chủ yếu qua lệnh `ceph auth`.
### Tạo User
Sử dụng `ceph auth add` hoặc `ceph auth get-or-create` để tạo user và gán quyền.
**Ví dụ:**
```
ceph auth add client.john mon 'allow r' osd 'allow rw pool=liverpool'
ceph auth get-or-create client.paul mon 'allow r' osd 'allow rw pool=liverpool'
```
#### Gán hoặc Sửa Capabilities
Dùng ceph auth caps để cập nhật quyền.
**Ví dụ:**
```text
ceph auth caps client.john mon 'allow r' osd 'allow rw pool=liverpool'
```
Ý nghĩa: `r` - đọc, `w` - viết, `x` - thực thi, `*` - tất cả.
#### Liệt kê và Xem User

- Liệt kê tất cả user: `ceph auth ls`
- Xem chi tiết user: `ceph auth get client.admin`

#### Xóa User
`ceph auth del client.john`
User thường lưu trong keyring tại `/etc/ceph/ceph.client.admin.keyring`. Sao chép keyring đến node admin và set quyền file: `chmod 644`.

## Keyring management
Keyring là file chứa key bí mật và capabilities cho user. Client dùng keyring để xác thực với cluster.
### Vị trí Keyring Mặc định

- Client: `/etc/ceph/ceph.client.<name>.keyring`
- Daemon: `/var/lib/ceph/<dịch_vụ>/ceph-<id>/keyring` (ví dụ: OSD).

Cấu hình trong `ceph.conf`: `keyring = /etc/ceph/ceph.keyring`.

### Tạo Keyring
```bash
# Tạo keyring rỗng:
ceph-authtool -C /etc/ceph/ceph.keyring

# Thêm user vào keyring:
ceph auth get client.admin -o /etc/ceph/ceph.client.admin.keyring

# Tạo user trực tiếp trong keyring:
ceph-authtool -C /etc/ceph/ceph.keyring -n client.ringo --cap mon 'allow r' --cap osd 'allow rw pool=liverpool' --gen-key

## Sau đó thêm vào cluster:
ceph auth add client.ringo -i /etc/ceph/ceph.keyring
```

### Quay Key (Rotation)
Thay đổi key mới:
```bash
ceph auth rotate client.ringo
```
> Luôn bảo vệ keyring bằng quyền file đúng (`644`), tránh lưu key trực tiếp trong config. Sử dụng công cụ như cephadm để tự động hóa.