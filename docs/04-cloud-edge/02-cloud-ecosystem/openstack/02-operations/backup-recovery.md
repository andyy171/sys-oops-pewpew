# OpenStack API And Automation Workflow

## Overview

OpenStack CLI, SDK, Ansible module và raw REST API đều đi qua cùng một nền tảng: Keystone token, service catalog, endpoint và API của từng service. Rough note `class-02-OpenStack-API-and-Development.md` trộn nhiều lab API, Fabric, Ansible, Kolla và debug; trang này giữ lại phần workflow có giá trị để dùng lâu dài.

## Mental Model

Luồng thao tác cơ bản:

```text
User / Script / CLI
      |
      v
Keystone auth -> token
      |
      v
Service catalog -> endpoint
      |
      v
Nova / Neutron / Cinder / Glance API
```

Khi một automation task lỗi, đừng debug ngay ở tool cao nhất. Hãy kiểm tra theo lớp:

1. Credentials và scope có đúng không.
2. Token issue được không.
3. Service catalog có endpoint đúng không.
4. API service trả lỗi gì.
5. Resource quota, RBAC/policy hoặc dependency service có chặn không.

## CLI Và Token

```bash
source /etc/kolla/admin-openrc.sh
openstack token issue
openstack endpoint list
openstack catalog list
openstack server list
```

Dùng `--debug` khi cần thấy request/response:

```bash
openstack endpoint list --debug
openstack server list --debug
```

Nếu CLI trả `401`, kiểm tra RC file, password/application credential, token expiry và clock skew. Nếu trả `403`, kiểm tra role assignment và policy.

## Raw API Debug

Khi cần xác minh endpoint hoặc debug tool automation, có thể gọi API trực tiếp bằng `curl`. Không ghi token thật vào note.

```bash
TOKEN="$(openstack token issue -f value -c id)"
curl -s -H "X-Auth-Token: ${TOKEN}" \
  http://<keystone-endpoint>:5000/v3/endpoints | python -m json.tool
```

Ví dụ gọi Nova:

```bash
PROJECT_ID="<PROJECT_ID>"
curl -s -H "X-Auth-Token: ${TOKEN}" \
  "http://<nova-endpoint>:8774/v2.1/${PROJECT_ID}/servers" | python -m json.tool
```

Nguyên tắc:

- Endpoint nên lấy từ service catalog thay vì hard-code.
- Token nên có scope đúng project/domain.
- Response code quan trọng hơn output dài: `401`, `403`, `404`, `409`, `500` gợi ý lớp lỗi khác nhau.

## Automation Tooling

OpenStack automation thường đi theo ba lớp:

| Lớp | Khi dùng | Lưu ý |
|---|---|---|
| CLI script | Lab, thao tác nhanh, runbook nhỏ | Dễ viết nhưng khó idempotent |
| Ansible/OpenStack modules | Cấu hình lặp lại, inventory, day-2 task | Cần kiểm soát idempotency và credentials |
| SDK/Terraform | Provisioning theo workflow ứng dụng | Cần quản lý state, drift và lifecycle |

Không nên dùng raw shell script cho những workflow cần idempotency mạnh như tạo network, router, security group hoặc volume lặp lại nhiều lần. Với hạ tầng lâu dài, dùng module/SDK/IaC phù hợp hơn.

## Kolla Container Debug

Kolla chạy service OpenStack trong container, nên debug cần đi qua cả lớp OpenStack service và lớp container runtime.

```bash
docker ps
docker logs <container-name>
docker exec -it <container-name> bash
```

Checklist:

- Container có đang restart không.
- Config được render vào container đúng chưa.
- Log service bên trong container có lỗi Keystone/DB/RabbitMQ không.
- Endpoint trong service catalog có trỏ đúng VIP/interface không.
- Sau khi đổi config bằng Kolla, dùng `reconfigure` thay vì sửa tay trong container rồi quên mất.

## Related Pages

- [OpenStack Common Commands](./common-commands.md)
- [OpenStack Client Debug](../04-troubleshooting/openstack-client-debug.md)
- [General Logs Debug](../04-troubleshooting/general-logs-debug.md)
- [Kolla-Ansible All-In-One Lab](./01-deployment/kolla-ansible-all-in-one-lab.md)
