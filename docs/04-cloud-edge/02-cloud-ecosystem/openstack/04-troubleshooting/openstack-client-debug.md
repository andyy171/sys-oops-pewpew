# OpenStack Client Debug

## Overview

Trang này gom phần có giá trị từ rough note OpenStack API lab: cách debug OpenStack CLI và REST API theo lớp token, endpoint, service catalog và response code. Khi client lỗi, đừng nhảy ngay vào log Nova/Neutron; trước tiên hãy chứng minh request đi đúng identity scope và đúng endpoint.

## Baseline Checks

```bash
source <openrc-file>
openstack token issue
openstack endpoint list
openstack catalog list
openstack service list
```

Nếu `openstack token issue` đã lỗi, vấn đề nằm ở credentials, Keystone endpoint, domain/project scope hoặc clock skew. Nếu token issue được nhưng service command lỗi, chuyển sang kiểm tra endpoint, policy, quota hoặc service backend.

## Dùng --debug

```bash
openstack server list --debug
openstack endpoint list --debug
openstack volume list --debug
```

`--debug` giúp thấy URL được gọi, method, headers, response code và traceback client-side. Khi đọc output, tập trung vào:

- URL endpoint có đúng region/interface không.
- Request đi tới public/internal/admin endpoint nào.
- HTTP status code là `401`, `403`, `404`, `409` hay `500`.
- Traceback nằm ở client parsing hay server response.

## Debug Theo Response Code

| Code | Ý nghĩa thường gặp | Hướng kiểm tra |
|---|---|---|
| `401 Unauthorized` | Token/credential không hợp lệ hoặc hết hạn | RC file, password/app credential, Keystone, NTP |
| `403 Forbidden` | Có identity nhưng thiếu quyền | Role assignment, project scope, policy |
| `404 Not Found` | Resource hoặc endpoint sai | Resource ID, region, service catalog |
| `409 Conflict` | Conflict trạng thái hoặc quota | Quota, resource state, operation đang chạy |
| `500` | Lỗi server-side | Log service tương ứng, DB, RabbitMQ, dependency |

## Raw API Check

Không ghi token thật vào tài liệu hoặc ticket. Token dưới đây chỉ là biến tạm trong shell.

```bash
TOKEN="$(openstack token issue -f value -c id)"
curl -s -H "X-Auth-Token: ${TOKEN}" \
  http://<keystone-endpoint>:5000/v3/endpoints | python -m json.tool
```

Ví dụ kiểm tra Nova server list:

```bash
PROJECT_ID="<PROJECT_ID>"
curl -s -H "X-Auth-Token: ${TOKEN}" \
  "http://<nova-endpoint>:8774/v2.1/${PROJECT_ID}/servers" | python -m json.tool
```

Nếu raw API chạy được nhưng CLI/automation lỗi, vấn đề có thể nằm ở client config, SDK version, clouds.yaml hoặc cách tool chọn endpoint.

## Related Pages

- [OpenStack API And Automation Workflow](../02-operations/api-and-automation-workflow.md)
- [OpenStack Common Commands](../02-operations/common-commands.md)
- [General Logs Debug](./general-logs-debug.md)
