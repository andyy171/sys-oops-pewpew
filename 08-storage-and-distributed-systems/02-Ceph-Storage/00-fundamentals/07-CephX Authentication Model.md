# Mục lục 


# Overview 

CephX Authentication Model
- **CephX** là **cơ chế xác thực nội bộ của Ceph**, được thiết kế tương tự **Kerberos** nhằm đảm bảo mọi giao tiếp giữa client và daemon đều được **xác minh danh tính và bảo vệ an toàn**.
- Cơ chế hoạt động như sau: **Client gửi yêu cầu xác thực đến Monitor (MON)** bằng cặp username/secret key. Nếu hợp lệ, MON **cấp một session ticket (keyring)** có thời hạn; client dùng ticket này để **ký và xác thực các yêu cầu** tới OSD, MDS hay MON khác mà không cần gửi lại mật khẩu.
- Cách làm này giống như **mua vé vào rạp**: người dùng lấy vé từ quầy (MON) rồi dùng nó để ra vào rạp (OSD). CephX giúp **ngăn truy cập trái phép**, **giảm rủi ro lộ khóa**, hỗ trợ **ACL và LDAP**, và được **kích hoạt mặc định trong mọi cụm Ceph**.

# Capabilities & authorization
Capabilities (hay còn gọi là "caps") là cách Ceph kiểm soát quyền truy cập của người dùng hoặc client đối với các dịch vụ như MON, OSD, MDS, MGR. Chúng định nghĩa những hành động nào được phép thực hiện, như đọc (read), viết (write) hoặc thực thi (execute).

- Capabilities được viết dưới dạng chuỗi: `dịch_vụ 'allow <hành_động>'`. Các hành động phổ biến:
    `allow *`: Quyền đầy đủ.
    `allow rwx`: Đọc, viết, thực thi.
    `allow profile <dịch_vụ>`: Quyền mặc định cho dịch vụ (ví dụ: `profile osd` cho OSD).

Bạn có thể giới hạn quyền theo pool hoặc namespace cụ thể, ví dụ: `osd 'allow rw pool=liverpool'`.

- Khi client kết nối, CephX kiểm tra capabilities trong keyring để xác nhận quyền. Nếu không có quyền phù hợp, yêu cầu sẽ bị từ chối. Điều này giúp bảo mật, chỉ cho phép người dùng làm những gì cần thiết.


# User management
- User trong Ceph là các thực thể như `client.admin`, osd.0, dùng để xác thực. Mỗi user có key và capabilities liên kết. Quản lý user chủ yếu qua lệnh `ceph auth`.
## Tạo User
Sử dụng `ceph auth add` hoặc `ceph auth get-or-create` để tạo user và gán quyền.
**Ví dụ:**
```
ceph auth add client.john mon 'allow r' osd 'allow rw pool=liverpool'
ceph auth get-or-create client.paul mon 'allow r' osd 'allow rw pool=liverpool'
```
## Gán hoặc Sửa Capabilities
Dùng ceph auth caps để cập nhật quyền.
**Ví dụ:**
```text
ceph auth caps client.john mon 'allow r' osd 'allow rw pool=liverpool'
```
Ý nghĩa: `r` - đọc, `w` - viết, `x` - thực thi, `*` - tất cả.
## Liệt kê và Xem User

- Liệt kê tất cả user: `ceph auth ls`
- Xem chi tiết user: `ceph auth get client.admin`

## Xóa User
`ceph auth del client.john`
User thường lưu trong keyring tại `/etc/ceph/ceph.client.admin.keyring`. Sao chép keyring đến node admin và set quyền file: `chmod 644`.

# Keyring management
Keyring là file chứa key bí mật và capabilities cho user. Client dùng keyring để xác thực với cluster.
## Vị trí Keyring Mặc định

- Client: `/etc/ceph/ceph.client.<name>.keyring`
- Daemon: `/var/lib/ceph/<dịch_vụ>/ceph-<id>/keyring` (ví dụ: OSD).

Cấu hình trong `ceph.conf`: `keyring = /etc/ceph/ceph.keyring`.

## Tạo Keyring
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

## Quay Key (Rotation)
Thay đổi key mới:
```bash
ceph auth rotate client.ringo
```
> Luôn bảo vệ keyring bằng quyền file đúng (`644`), tránh lưu key trực tiếp trong config. Sử dụng công cụ như cephadm để tự động hóa.