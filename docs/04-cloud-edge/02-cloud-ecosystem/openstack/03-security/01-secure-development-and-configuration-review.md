# OpenStack Secure Development Và Configuration Review

## Tổng Quan

OpenStack hiếm khi yếu vì một lỗi đơn lẻ. Rủi ro thường xuất hiện khi API mở, dashboard, service-to-service communication, cấu hình yếu, file permission rộng, automation script không an toàn và secret không được bảo vệ kết hợp thành một attack path.

Note này tập trung vào defensive review: nhận diện pattern nguy hiểm, giải thích vì sao quan trọng trong môi trường OpenStack và ghi lại pattern an toàn hơn.

## Attack Surface Mental Model

| Boundary | Điều cần chú ý |
|---|---|
| Dashboard | Horizon hoặc custom portal có thể gặp XSS, CSRF, open redirect, session handling yếu và render dữ liệu user không an toàn. |
| API | Public/internal APIs mang token, credential, project ID, resource ID và action nhạy cảm. |
| Identity | Keystone quản lý authentication, token, service catalog, role assignment và trust giữa services. |
| Networking | Neutron policy, provider network, VLAN/VXLAN, router, security group và metadata access là security boundary quan trọng. |
| Storage | Cinder, Swift, Glance và backend như Ceph/RBD có thể lộ hoặc hỏng dữ liệu nếu policy/credential/config yếu. |
| Compute | Nova, libvirt, qemu/KVM, image handling, metadata và isolation lỗi có thể mở đường từ workload tenant tới host/control plane. |
| Config/secrets | Config file, log, debug output, keyring, password, token và temp file thường là đường lộ quyền nhanh nhất. |

## Attack Path Review Cho OpenStack

Khi đọc một lỗi bảo mật trong OpenStack, không nên chỉ hỏi "bug nằm ở service nào". Cần map thành attack path:

```text
entry point
-> identity / token / session
-> policy check
-> OpenStack API object
-> backend control-plane state
-> runtime resource
-> data exposure hoặc privilege escalation
```

Các điểm cần soi:

- API endpoint public/internal có đang nhận token, credential hoặc admin action qua kênh không bảo mật không?
- Keystone role, project, service user và policy có cho phép thao tác vượt quá blast radius mong muốn không?
- Horizon hoặc custom portal có render resource name, metadata, error message, redirect target hoặc form action từ input không tin cậy không?
- Neutron có boundary rõ giữa tenant network, provider network, metadata service, security group và router namespace không?
- Cinder, Swift, Glance và backend như Ceph/RBD có bị lộ credential, endpoint hoặc object/volume permission qua config/log không?
- Nova, image handling, metadata và hypervisor layer có tạo đường leo thang từ VM tenant sang host hoặc control plane không?

Một lỗi code nhỏ như open redirect, XSS, path traversal hoặc secret logging có thể trở thành cloud incident lớn nếu nó chạm vào Keystone session, service credential, admin API hoặc backend storage.

## File Permission Và Ownership

OpenStack services thường lưu database credential, RabbitMQ credential, Keystone token, service password, TLS key, Ceph keyring và endpoint config trong file. Các file này không nên world-readable hoặc world-writable.

Checklist:

- Tránh permission như `0666` cho file chứa secret hoặc service config.
- Dùng least privilege: chỉ service user và group thật sự cần thiết mới có quyền đọc.
- Ưu tiên `0600` cho file chỉ owner cần đọc/ghi.
- Kiểm tra owner/group sau khi package, Kolla-Ansible hoặc config management render file.
- Không giả định Python tạo file an toàn nếu `umask` chưa được kiểm soát.

```bash
chmod 0600 secureserv.conf
ls -l secureserv.conf
```

Với Python, đặt permission ngay lúc tạo file:

```python
import os

flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
with os.fdopen(os.open("service-secret.conf", flags, 0o600), "w") as fout:
    fout.write("secret data")
```

Áp dụng đặc biệt cho `/etc/kolla`, `/etc/ceph`, service config directories, generated password files và TLS materials.

## Unsafe Parsing Và Deserialization

Automation, operator script và service extension thường xử lý YAML, JSON-like payload hoặc config do người khác cung cấp. Không dùng parser có thể tạo object hoặc chạy code với input không tin cậy.

| Risk area | Tránh | Nên dùng |
|---|---|---|
| YAML | `yaml.load()` với input không tin cậy | `yaml.safe_load()` cho data-only YAML |
| pickle / cPickle | `pickle.load()` hoặc `pickle.loads()` từ input ngoài | Không dùng pickle làm interchange format |
| eval | `eval(user_input)` | Parser/schema rõ ràng |
| exec | `exec(user_input)` | Workflow explicit, không chạy code từ input |

## Subprocess Safety

Script vận hành OpenStack hay gọi `openstack`, `rbd`, `ceph`, `ovs-vsctl`, `ip netns`, `qemu-img`, `curl` hoặc database command. Tránh string concatenation kèm `shell=True` khi có input từ user, ticket, API hoặc file ngoài.

```python
import subprocess

def ping(host):
    args = ["ping", "-c", "1", host]
    return subprocess.check_output(args, shell=False)
```

Khi cần pipe nhiều lệnh, tạo process riêng và nối `stdout/stdin` thay vì bật shell chỉ vì tiện.

## URL Redirect Validation

Login flow, dashboard, billing portal hoặc support portal thường có tham số `next`/`return`. Redirect target là user-controlled input, nên phải giữ trong host/domain cho phép.

```python
from urllib.parse import urlparse, urljoin

def is_safe_redirect_url(host_url, target):
    base = urlparse(host_url)
    dest = urlparse(urljoin(host_url, target))
    return dest.scheme in ("http", "https") and base.netloc == dest.netloc
```

Open redirect trong portal cloud nên được xem là identity/dashboard security issue, không phải lỗi web nhỏ.

## CSRF Và Session-Bound Actions

Dashboard hoặc portal quản trị cloud thường có các thao tác nhạy cảm: tạo/xóa instance, gán floating IP, sửa security group, upload image, tạo volume, reset password, cấp role hoặc thay đổi project membership. Những action này phải được bảo vệ như state-changing operation, không chỉ như form web thông thường.

Checklist:

- Dùng CSRF token cho mọi request thay đổi state.
- Không cho phép action nhạy cảm chạy qua `GET`.
- Kiểm tra `Origin`/`Referer` khi phù hợp, đặc biệt với admin portal.
- Session cookie nên có `Secure`, `HttpOnly`, `SameSite` phù hợp với luồng đăng nhập.
- Với action có blast radius lớn, yêu cầu xác nhận bổ sung, audit log và policy check rõ ràng.

Trong OpenStack, CSRF không chỉ là rủi ro web UI. Nếu user đang có Horizon session hợp lệ, một request bị ép từ trang khác có thể trở thành thao tác thật trên Nova, Neutron, Cinder hoặc Keystone thông qua API phía sau dashboard.

## TLS Và Certificate Verification

OpenStack API calls thường mang token, project ID, service catalog và admin action. Không tắt certificate verification trong production automation.

```python
import requests

requests.get("https://openstack.example.local/", verify="/path/to/ca_cert.pem")
```

Nguyên tắc:

- Tách rõ lab shortcut với production posture.
- Internal API traffic vẫn có thể mang token nhạy cảm.
- HTTPS, SSH, LDAPS, database TLS và service-to-service TLS đều cần identity verification phù hợp.
- Endpoint production nên mặc định `https` khi có thể.

## Temporary File Safety

Không tạo temporary file bằng path đoán được hoặc check-then-open vì dễ gặp race condition.

```python
import os
import tempfile

fd, path = tempfile.mkstemp()
try:
    with os.fdopen(fd, "w") as tmp:
        tmp.write("stuff")
finally:
    os.remove(path)
```

Áp dụng cho config fragment, token file, downloaded image, command output, database dump, migration artifact và temporary credential file.

## Path Traversal Prevention

Không ghép user input trực tiếp vào filesystem path. Các rủi ro thường gặp nằm ở image upload helper, dashboard plugin, report download endpoint, support bundle tool, object viewer hoặc file-serving utility.

```python
import os

def is_safe_path(basedir, path, follow_symlinks=True):
    basedir = os.path.realpath(basedir)
    matchpath = os.path.realpath(path) if follow_symlinks else os.path.abspath(path)
    return basedir == os.path.commonpath([basedir, matchpath])
```

Thiết kế tốt hơn là map user-facing ID sang path server-side đã biết, thay vì expose path thật.

## Database Query Parameterization

Không build SQL bằng string formatting từ project ID, user ID, resource name, filter hoặc admin input.

```python
query = "select username from users where username = %s"
cur.execute(query, (username_value,))
```

Với SQLAlchemy, dùng bind parameter:

```python
query = "select username from users where username = :name"
result = connection.execute(query, name=username_value)
```

Escaping thủ công yếu hơn parameterized query đúng nghĩa.

## Secret Và Log Redaction

Không để password, token, connection string, private key, API key hoặc service credential xuất hiện trong debug log, config dump hoặc troubleshooting bundle. Với `oslo.config`, option nhạy cảm nên được đánh dấu `secret=True`.

```python
cfg.StrOpt(
    "password",
    help="Password of the host.",
    secret=True,
)
```

Khi thu thập log của nova, neutron, cinder, glance, keystone, placement, rabbitmq, mariadb, haproxy hoặc kolla, giả định log có thể chứa secret cho tới khi đã review/redact.

## XSS Prevention

Horizon, custom portal, monitoring page, report viewer và billing system đều có thể render resource name, metadata, project description, image name hoặc error message do user kiểm soát.

```python
from html import escape

def render_name(name):
    safe_name = escape(name)
    return f"<html><body>Hello {safe_name}!</body></html>"
```

Dùng template engine escape mặc định, tránh đánh dấu untrusted content là safe HTML và escape theo đúng output context.

## Neutron, Storage Và Privilege Escalation Notes

Một số nhóm lỗi không nằm gọn trong code review nhưng cần được ghi vào security review vì chúng quyết định blast radius:

- Neutron: kiểm tra provider network exposure, VLAN/VXLAN segmentation, security group rule, metadata access, router namespace và bridge/OVS/OVN flow khi nghi ngờ tenant có thể intercept hoặc reroute traffic.
- Cinder/Swift/Glance: kiểm tra policy, service credential, backend credential, object/container permission, image visibility, volume attachment và log/debug output trước khi kết luận dữ liệu an toàn.
- Keystone: token, role assignment, trust, application credential và service catalog là điểm nối giữa authentication và authorization; cấu hình yếu có thể biến lỗi nhỏ thành privilege escalation.
- Hypervisor: Nova/libvirt/qemu/KVM, image format, metadata injection và console access là boundary giữa workload tenant và host; không xử lý như app bug thuần túy.
- Patch posture: default password, service user quá rộng quyền, thiếu update bảo mật và debug mode bật lâu dài đều là điều kiện làm attack path dễ khai thác hơn.

Khi điều tra, bắt đầu bằng read-only evidence: policy effective, role assignment, service endpoint, network topology, security group, route, log đã redact, audit event và backend permission. Tránh sửa trực tiếp DB/control-plane state hoặc restart service trước khi có rollback plan.

## Practical Review Checklist

- Service config, keyring, password file và TLS material đã đúng owner/group/permission chưa?
- Có code nào dùng `yaml.load`, `pickle`, `eval` hoặc `exec` với input không tin cậy không?
- Automation có dùng `shell=True` hoặc string formatting để tạo command không?
- Dashboard/portal có validate `next` hoặc `return` redirect target không?
- Dashboard/portal có CSRF protection cho state-changing action không?
- OpenStack API và service-to-service calls có verify certificate không?
- Temporary file có dùng `tempfile` API an toàn không?
- User-controlled filename có thoát khỏi base directory được không?
- Database query có parameterized thay vì nối chuỗi không?
- Config/log/troubleshooting bundle có thể lộ password/token/private key không?
- HTTP lab shortcut có bị ghi nhầm thành production best practice không?
- User-controlled web output có được escape đúng context không?
- Neutron, storage, Keystone và hypervisor boundary đã được review theo blast radius thay vì chỉ theo lỗi code đơn lẻ chưa?

## Boundary Của Note

Note này không thay thế các chủ đề hardening production như Keystone policy design, endpoint TLS deployment, Fernet key rotation, Barbican, RabbitMQ/MariaDB hardening, hypervisor hardening, Neutron tenant isolation, audit logging, vulnerability management hoặc Kolla-Ansible production security profile. Các chủ đề đó nên có note riêng và link lại khi cần.

## Trang Liên Quan

- [OpenStack Security](./overview.md)
- [OpenStack API And Automation Workflow](../02-operations/api-and-automation-workflow.md)
- [OpenStack Operations](../02-operations/operations.md)
- [Keystone](../01-core-fundamentals/services/keystone.md)
- [Horizon](../01-core-fundamentals/services/horizon.md)
- [Neutron](../01-core-fundamentals/services/neutron.md)
- [Cinder](../01-core-fundamentals/services/cinder.md)
- [Glance](../01-core-fundamentals/services/glance.md)
