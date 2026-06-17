# Kibana Visualization

## Cach Hieu Nhanh

Kibana la UI de search, filter, visualize va dashboard du lieu trong Elasticsearch. Trong logging workflow, Kibana dung de tra loi nhanh:

- Loi xay ra khi nao?
- Host/service nao phat sinh log?
- Rate event co spike khong?
- Status code, user agent, source IP, endpoint nao bat thuong?
- Log nao lien quan toi incident window?

Kibana khong thay the alerting/runbook. Dashboard giup dieu tra; alert can signal ro, threshold co ly do va owner xu ly.

## Data View / Index Pattern

Truoc khi Discover hoac dashboard co du lieu, Kibana can data view/index pattern tro toi index dung, vi du:

```text
filebeat-*
logs-*
app-prod-*
```

Chon time field dung, thuong la `@timestamp`. Neu dashboard rong, kiem tra:

- time range dang xem.
- data view co match index that khong.
- event co `@timestamp` dung timezone/format khong.
- filter/KQL co qua hep khong.

## Discover Workflow

Workflow dieu tra log co ban:

```text
chon data view
-> set time range theo incident
-> filter service/host/environment
-> search error/status/path/user/session
-> mo event de xem fields
-> pin/copy query cho runbook/RCA
```

Vi du KQL:

```text
host.name: "web-1" and log.file.path: "/var/log/nginx/access.log"
http.response.status_code >= 500
service.name: "api" and message: "timeout"
```

Guardrails:

- Khong paste secret/customer data vao saved query hoac dashboard title.
- Khi chia se screenshot, redact IP/customer identifier neu khong phai public/test data.
- Saved searches nen co owner va muc dich ro neu dung trong runbook.

## Dashboard Design

Dashboard logging tot nen tra loi mot cau hoi van hanh ro:

- Web traffic: request rate, 4xx/5xx, top path, latency bucket neu co.
- Auth/security: failed login rate, sudo event, source IP bat thuong.
- Application errors: error rate theo service/version/host.
- Pipeline health: ingest rate, dropped events, agent errors.

Tranh dashboard chi co nhieu chart dep nhung khong co action. Moi panel nen giup triage hoac quyet dinh tiep theo.

## Performance Va Cost

- Gioi han time range khi query log volume lon.
- Uu tien filter indexed fields thay vi full-text search rong.
- Tranh tao dashboard auto-refresh qua nhanh tren index lon.
- Can nhac retention va index lifecycle cho log co volume cao.
- High-cardinality fields co the lam query/dashboard cham va tang chi phi storage.

## Troubleshooting

| Symptom | Kiem tra |
|---|---|
| Khong co data | Data view, time range, index existence, ingest pipeline |
| Co log nhung field thieu | Parser/filter, mapping, source log format |
| Dashboard sai so | Query/filter, time zone, duplicate shipping |
| Query cham | Time range qua rong, field khong indexed, cardinality cao |
| Log moi delay | Agent/Logstash/Elasticsearch backpressure |

## Production Guardrails

- Kibana phai co authentication/authorization.
- Dashboard security/auth nen gioi han quyen xem.
- Khong public Kibana ra Internet khong qua identity proxy/VPN/bastion.
- Backup saved objects quan trong hoac quan ly bang IaC/export.
- Khi nang version Elastic/Kibana, test saved objects va field mapping truoc.

## Trang Lien Quan

- [Centralized Logging Rsyslog Logstash Elasticsearch](./Centralized%20logging%20rsyslog%20%E2%86%92%20Logstash%20%E2%86%92%20Elasticsearch.md)
- [Observability And Monitoring](../overview.md)
