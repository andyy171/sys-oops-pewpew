# OpenStack API And Automation Workflow

## Overview

OpenStack CLI, Horizon, SDK, Ansible module, Terraform provider và raw REST API đều đi qua cùng một nền tảng: Keystone token, service catalog, endpoint và API của từng service. Khi hiểu luồng này, việc debug automation sẽ dễ hơn nhiều vì ta biết lỗi đang nằm ở credential, catalog, policy, service API hay backend.

## Mental Model

```text
User / Script / CLI / Horizon
  -> Keystone authentication
  -> token + service catalog
  -> chọn endpoint theo service/region/interface
  -> gọi Nova / Neutron / Glance / Cinder / Swift / Heat API
  -> service xử lý qua DB, message queue, scheduler/worker/backend
```

Khi một automation task lỗi, đừng debug ngay ở tool cao nhất. Hãy kiểm tra theo lớp:

1. RC file/credential/scope có đúng không.
2. Token issue được không.
3. Service catalog có endpoint đúng không.
4. API service trả HTTP status gì.
5. Policy, quota hoặc dependency service có chặn không.
6. Backend thật có lỗi không.

## OpenStack CLI

Ưu tiên `python-openstackclient` và lệnh `openstack` chung. Một số client cũ như `nova`, `glance`, `cinder`, `swift` vẫn hữu ích trong vài tình huống, nhưng learning path nên bắt đầu từ `openstack`.

```bash
openstack --version
openstack help
openstack help server create
```

Interactive mode:

```bash
openstack
(openstack) help
(openstack) server list
```

## RC File

RC file chứa biến môi trường để CLI biết auth URL, project, domain, user và API version.

```bash
source <openrc-file>
openstack token issue
openstack catalog list
openstack endpoint list
```

Biến thường gặp:

```bash
OS_AUTH_URL
OS_PROJECT_NAME
OS_USERNAME
OS_PASSWORD
OS_USER_DOMAIN_NAME
OS_PROJECT_DOMAIN_NAME
OS_IDENTITY_API_VERSION
OS_REGION_NAME
```

Không lưu password thật trong note hoặc script public. Với automation dài hạn, cân nhắc application credential hoặc secret manager phù hợp.

## Debug Bằng HTTP Status

| HTTP status | Ý nghĩa thường gặp |
|---|---|
| `401 Unauthorized` | Token sai/hết hạn, credential sai, clock skew, source nhầm RC file. |
| `403 Forbidden` | Token hợp lệ nhưng role/policy không cho phép action. |
| `404 Not Found` | Sai resource ID/name, endpoint/API version sai, region/interface sai. |
| `409 Conflict` | State không hợp lệ, quota/conflict, resource đang bị thao tác khác. |
| `500` | Service backend lỗi, DB/RabbitMQ/dependency lỗi hoặc bug. |

Dùng `--debug` để thấy endpoint, request, response và request ID:

```bash
openstack server list --debug
openstack image list --debug
```

## Raw API Debug

Khi cần xác minh endpoint hoặc debug tool automation, có thể gọi API trực tiếp bằng `curl`.

```bash
TOKEN="$(openstack token issue -f value -c id)"
curl -s -H "X-Auth-Token: ${TOKEN}" \
  "http://<keystone-endpoint>:5000/v3/endpoints" | python -m json.tool
```

Ví dụ gọi Nova:

```bash
PROJECT_ID="<PROJECT_ID>"
curl -s -H "X-Auth-Token: ${TOKEN}" \
  "http://<nova-endpoint>:8774/v2.1/${PROJECT_ID}/servers" | python -m json.tool
```

Nguyên tắc:

- Lấy endpoint từ service catalog thay vì hard-code.
- Token phải scope đúng project/domain.
- Không paste token thật vào ticket, note hoặc log công khai.
- Ghi lại `X-Openstack-Request-Id` để trace qua log.

## Horizon Handoff

Horizon là client web. Nó có thể download RC file, nhưng không expose toàn bộ API option. Nếu thao tác trong UI lỗi:

1. Reproduce bằng CLI.
2. Nếu CLI OK, kiểm tra Horizon session/log/browser devtools.
3. Nếu CLI cũng lỗi, debug Keystone/service API/backend.

## Automation Tooling

| Lớp | Khi dùng | Lưu ý |
|---|---|---|
| CLI script | Lab, thao tác nhanh, runbook nhỏ | Dễ viết nhưng khó idempotent. |
| Ansible/OpenStack modules | Day-2 task và cấu hình lặp lại | Cần kiểm soát idempotency và credential. |
| SDK | Workflow ứng dụng hoặc tool nội bộ | Cần handle retry, pagination, token refresh. |
| Terraform/OpenTofu | Provisioning có state | Cần quản lý drift và lifecycle. |
| Heat | Orchestration native trong OpenStack | Phù hợp stack resource liên quan chặt. |

Không nên dùng raw shell script cho workflow cần idempotency mạnh như tạo network/router/security group/volume lặp lại nhiều lần.

## Kolla Container Debug

Với Kolla-Ansible, service chạy trong container:

```bash
docker ps
docker logs <container-name>
docker exec -it <container-name> bash
```

Checklist:

- Container có restart loop không.
- Config render vào container đúng chưa.
- Log service có lỗi Keystone/DB/RabbitMQ không.
- Endpoint trong catalog có trỏ đúng VIP/interface không.
- Sau khi đổi config, dùng `kolla-ansible reconfigure` thay vì sửa tay trong container.

## Related Pages

- [OpenStack Common Commands](./common-commands.md)
- [OpenStack Client Debug](../04-troubleshooting/openstack-client-debug.md)
- [General Logs Debug](../04-troubleshooting/general-logs-debug.md)
- [Horizon](../01-core-fundamentals/services/horizon.md)
- [Keystone](../01-core-fundamentals/services/keystone.md)
