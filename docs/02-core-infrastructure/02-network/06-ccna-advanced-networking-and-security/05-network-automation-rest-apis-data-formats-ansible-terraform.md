# Network Automation, REST APIs, Data Formats, Ansible And Terraform

## Overview

Network automation chuyển network từ thao tác CLI thủ công sang mô hình có controller, API, data format, template, state và workflow lặp lại được. Mục tiêu không phải "thay network engineer", mà là giảm drift, giảm lỗi lặp lại và làm thay đổi có kiểm soát hơn.

## Management, Control And Data Planes

Cần tách ba plane:

- Data plane: forwarding packet/frame thật.
- Control plane: học route, MAC, topology, neighbor, policy để data plane biết chuyển tiếp thế nào.
- Management plane: cấu hình, monitoring, logging, SSH, SNMP, API.

Automation chủ yếu tác động management plane, đôi khi qua controller làm thay đổi control/data plane gián tiếp.

## SDN

SDN tách logic điều khiển khỏi từng thiết bị riêng lẻ và đưa vào controller. Controller có cái nhìn tập trung hơn về topology, policy và intent.

![ACI fabric original page](./images/ccna-vol2-page-0351.jpg)

Các ví dụ Cisco ở mức khái niệm:

- SD-Access: campus fabric, policy/segmentation tập trung.
- SD-WAN: overlay tunnel qua nhiều WAN underlay, controller quản lý policy/path.
- ACI: data center fabric với spine-leaf underlay và VXLAN overlay, APIC là controller.

## AI And ML In Network Operations

AI/ML trong network thường dùng cho:

- anomaly detection;
- dự đoán capacity/congestion;
- root cause suggestion;
- log/event correlation;
- tạo cấu hình hoặc giải thích policy.

Vẫn cần kiểm chứng. Với production network, output của AI nên đi qua review, test và rollback plan như mọi thay đổi khác.

## REST API And HTTP

REST API dùng HTTP method để thao tác resource. Các method cần nhớ:

- `GET`: đọc resource.
- `POST`: tạo hoặc gửi action.
- `PUT`: thay thế resource.
- `PATCH`: sửa một phần.
- `DELETE`: xóa resource.

![HTTP request original page](./images/ccna-vol2-page-0360.jpg)

HTTP status code:

- `2xx`: thành công.
- `3xx`: redirect.
- `4xx`: lỗi phía client/request/authz.
- `5xx`: lỗi phía server.

Authentication phổ biến:

- Basic auth: đơn giản nhưng cần TLS, ít nên dùng lâu dài.
- Bearer access token dùng token ngắn hạn, phổ biến với API hiện đại.
- API key: nhận diện application, không nên xem như user auth đầy đủ.
- OAuth flow: ủy quyền truy cập resource thay mặt user/app.

## Data Formats

JSON, XML và YAML là cách serialize dữ liệu để app/tool trao đổi được.

JSON:

```json
{
  "hostname": "r1",
  "interfaces": [
    {
      "name": "GigabitEthernet0/0",
      "enabled": true
    }
  ]
}
```

YAML dễ đọc cho config nhưng nhạy indentation:

```yaml
hostname: r1
interfaces:
  - name: GigabitEthernet0/0
    enabled: true
```

XML verbose hơn nhưng vẫn gặp trong NETCONF và nhiều hệ thống enterprise.

## Configuration Management

Vấn đề chính là configuration drift: thiết bị lệch khỏi baseline vì thay đổi thủ công, hotfix, thiếu chuẩn hoặc không có source of truth.

![Ansible operations original page](./images/ccna-vol2-page-0389.jpg)

Ansible:

- thường agentless;
- dùng inventory, playbook, module, template, variable;
- procedural hơn Terraform;
- hợp cấu hình thiết bị, đẩy thay đổi, audit trạng thái.

Terraform:

- declarative;
- dùng provider và state;
- hợp provisioning infrastructure, cloud resource, một số network platform có API tốt;
- cần quản lý state cẩn thận.

## Safe Automation Checklist

- Có source of truth rõ không?
- Template có được render/test trước khi apply không?
- Có diff hoặc dry-run không?
- Thay đổi có batch nhỏ và rollback không?
- Credential/API token được lưu trong vault/secret manager không?
- Log của automation có đủ để audit không?
- Có phân biệt desired state, observed state và actual device state không?
- Có guardrail tránh push nhầm toàn bộ fleet không?
