# Observability And Monitoring

Khu vuc nay gom cac note ve metrics, logs, traces, alerting, dashboard, Linux/runtime observability va cac stack giam sat nhu Prometheus, Grafana, Zabbix, TIG stack.

## Suggested Reading

- [Prometheus Architecture](./01-metrics-and-monitoring/Prometheus/Architecture.md)
- [Centralized Logging Rsyslog Logstash Elasticsearch](./02-logs-and-traces/Centralized%20logging%20rsyslog%20%E2%86%92%20Logstash%20%E2%86%92%20Elasticsearch.md)
- [Kibana visualization](./02-logs-and-traces/Kibana%20visualization.md)
- [Distributed tracing with Jaeger and OpenTelemetry](./02-logs-and-traces/Distributed%20tracing%20%28Jaeger,%20OpenTelemetry%29.md)
- [SLA, SLO, SLI design](./03-alerting-&-SLA/SLA,%20SLO,%20SLI%20design.md)
- [Zabbix Installation](./04-Zabbix/Zabbix-Installation.md)
- [TIG Stacks Overview](./05-TIG-stacks/Overview.md)
- [eBPF Observability And Security](./06-ebpf-observability/overview.md)

## Domain Map

```text
01-observability-and-monitoring/
|-- 01-metrics-and-monitoring/
|-- 02-logs-and-traces/
|-- 03-alerting-&-SLA/
|-- 04-Zabbix/
|-- 05-TIG-stacks/
`-- 06-ebpf-observability/
```

## Operating Principles

- Metrics cho xu huong va alert.
- Logs cho chi tiet hanh vi va loi.
- Traces cho request path qua nhieu service.
- Events cho thay doi trang thai he thong.
- eBPF/runtime signals dung khi can nhin sau vao kernel, syscall, network hoac security behavior.
