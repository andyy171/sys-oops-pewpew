# Centralized Logging Rsyslog Logstash Elasticsearch

## Cach Hieu Nhanh

Centralized logging gom log tu nhieu host ve mot pipeline chung de search, correlate va dieu tra incident nhanh hon viec SSH vao tung may. ELK/Elastic Stack la mot pattern pho bien:

```text
application / system logs
-> agent: Filebeat / rsyslog / Fluent Bit
-> processor: Logstash / ingest pipeline
-> storage/index: Elasticsearch
-> query/visualization: Kibana
```

Agent gan source log voi metadata nhu hostname, service, environment va file path. Processor parse, enrich, filter va route log. Storage index phuc vu search. Kibana giup explore, dashboard va drill-down.

## Khi Nen Dung

- Fleet co nhieu host hoac container, khong the grep thu cong tren tung node.
- Can dieu tra request/error tren nhieu tier.
- Can log authentication, web access, application error, firewall/security event.
- Can dashboard tam thoi cho traffic spike, 4xx/5xx, auth failure hoac deployment issue.

Khong nen xem centralized logging la noi do tat ca moi thu vo han. Log co chi phi storage, network, indexing va privacy.

## Pipeline Components

| Component | Vai tro |
|---|---|
| Filebeat/agent | Doc file log, track offset, gui event ve processor/output |
| Logstash | Parse/enrich/filter/route log, xu ly format khac nhau |
| Elasticsearch | Index va search log theo time range/field |
| Kibana | Discover, dashboard, filter, visualize va incident investigation |

Common inputs:

- `/var/log/auth.log` hoac `/var/log/secure` cho SSH/sudo/auth event.
- Web access log nhu Nginx/Apache combined log.
- Application structured JSON log.
- System service logs tu journald/rsyslog.
- Container stdout/stderr collected tu Docker/Kubernetes runtime hoac logging agent.

## Log Shipping Pattern

Agent tren app/web host nen gui log ve endpoint trung tam:

```yaml
filebeat_output_logstash_enabled: true
filebeat_output_logstash_hosts:
  - "logs.example.com:5044"

filebeat_inputs:
  - type: log
    paths:
      - /var/log/auth.log
  - type: log
    paths:
      - /var/log/nginx/access.log
```

Production guardrails:

- Dung TLS cho traffic agent -> collector/Logstash.
- Khong dat `ssl_insecure`/skip verification trong production.
- Certificate phai match hostname/SAN cua endpoint log.
- Khong ship secret, token, password hoac PII neu khong co masking/redaction.
- Log agent config phai duoc deploy bang automation va review nhu code.

## Validation Workflow

Sau khi deploy logging pipeline:

```text
agent running
-> output endpoint reachable
-> test log written
-> event appears in index
-> Kibana Discover can filter by host/service/path
-> dashboard/alert reads expected field names
```

Safe checks:

```bash
systemctl status filebeat
systemctl status logstash
systemctl status elasticsearch
journalctl -u filebeat -n 100 --no-pager
```

Neu dung Nginx access log, co the sinh traffic nho de test ingestion. Khong load test production chi de kiem tra logging.

## Container Log Considerations

Container log nen gan du metadata de truy vet:

- host/node;
- service/application;
- environment;
- container id/name;
- image tag va digest;
- namespace/project neu co orchestrator;
- deployment/release version.

Voi Docker standalone, log co the den tu `json-file`, `journald`, `syslog` hoac agent doc file runtime. Voi Kubernetes, log thuong di qua node agent nhu Fluent Bit/Filebeat/Vector va duoc enrich bang Pod/namespace/label metadata.

Guardrails:

- Doi Docker log driver co the lam thay doi cach operator dung `docker logs`; can thong bao va cap nhat runbook.
- Log file local van can rotation/retention de tranh day disk truoc khi agent ship kip.
- Khong dung container filesystem lam noi luu log dai han; container recreate co the mat writable layer.
- Neu log driver gui truc tiep qua network, thiet ke backpressure/failure behavior ro rang de logging outage khong lam app outage ngoai y muon.
- Chuan hoa structured log neu co the; parse regex muon trong pipeline lam tang CPU va false parsing.

## Troubleshooting

| Symptom | Check |
|---|---|
| Kibana khong thay event moi | Time range, index pattern/data view, agent output error |
| Agent doc file nhung khong gui | File permission, registry/offset, output endpoint, TLS error |
| Logstash nhan nhung index sai | Pipeline filter, index naming, Elasticsearch permission |
| Dashboard rong | Field mapping khac, time field sai, filter dang qua hep |
| Log delay | Agent backpressure, Logstash queue, Elasticsearch indexing pressure |

Nginx co the buffer access log; neu event khong xuat hien ngay, kiem tra flush/buffering va file offset cua agent truoc khi ket luan pipeline hong.

## Performance Va Retention

Logging pipeline can duoc thiet ke theo volume:

- Estimate events/second, average event size va retention.
- Tach hot/warm/cold storage neu volume lon.
- Dung lifecycle/retention policy de tranh day disk.
- Parse structured logs o source neu co the; regex grok phuc tap trong Logstash co the ton CPU.
- Giam high-cardinality fields khong can thiet.

## Security Guardrails

- Gioi han network inbound vao Logstash/collector chi tu host can ship log.
- Dung service account/API key co privilege toi thieu de write index.
- Bat auth cho Kibana/Elasticsearch; khong public UI ra Internet.
- Redact secret trong application log truoc khi ship.
- Log security/auth event can retention va access control khac log debug.

## Automation Notes

Ansible phu hop de:

- cai dat agent/collector.
- render config Filebeat/Logstash/Nginx reverse proxy.
- quan ly certificate file permission.
- them input log theo role inventory.
- validate service state sau deploy.

Voi production, dung canary host truoc, sau do rolling theo group. Neu thay doi parser/filter, test tren sample log truoc de tranh lam mat truong/field ma alert/dashboard dang dung.

## Trang Lien Quan

- [Kibana visualization](./Kibana%20visualization.md)
- [Observability And Monitoring](../overview.md)
