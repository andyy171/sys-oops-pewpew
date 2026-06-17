# Infrastructure Automation

Domain này chứa tầng công cụ và quy trình vận hành: observability, security/hardening, CI/CD, infrastructure as code và automation scripting.

## Chứa Gì

- Observability: metrics, logs, traces, alerting, SLO/SLA, dashboards, Prometheus, Grafana, Loki, Tempo, Zabbix, TIG và eBPF observability.
- Security and hardening: access control, host security, network security, container/cloud security, incident response và security operations.
- CI/CD and DevOps integration: CI, CD, deployment strategy, GitOps, Argo CD, Helm/Kustomize trong bối cảnh release workflow.
- Infrastructure as Code: Terraform/OpenTofu, Ansible, Packer và automation patterns.
- Python/shell automation khi nội dung là tool/process vận hành hạ tầng.
- Language-based tooling khi nội dung là workflow vận hành bằng script/tool; kiến thức nền về Go, Python, C++ đặt ở [Programming Languages](../06-programming-languages/overview.md).
- Git/version control khi nội dung là workflow/tooling phục vụ automation, CI/CD hoặc vận hành.

## Không Chứa Gì

- Linux kernel/host internals, network protocol, storage backend và database engine; đặt ở [Core Infrastructure](../02-core-infrastructure/overview.md).
- Kubernetes object/control plane behavior; đặt ở [Compute And Orchestration](../03-compute-and-orchestration/overview.md).
- AWS/OpenStack/Azure/GCP service-specific architecture; đặt ở [Cloud Edge](../04-cloud-edge/overview.md).
- Go/Python/C++ language foundations, project structure, runtime model và generic programming patterns; đặt ở [Programming Languages](../06-programming-languages/overview.md).

## Learning Path

- [Observability And Monitoring](./01-observability-and-monitoring/overview.md)
- [Security And Hardening](./02-security-and-hardening/overview.md)
- [CI/CD And DevOps Integration](./03-cicd-devops-integration/overview.md)
- [Infrastructure As Code](./04-infrastructure-as-code/overview.md)
- [Python Automation](./05-python-automation/overview.md)
- [Git And Version Control](./06-git-and-version-control/overview.md)
- [Programming Languages](../06-programming-languages/overview.md)

## Ghi Chú Refactor

- Observability nên được chuẩn hóa theo capability trước, tool sau: metrics, logs, traces, alerting/SLO, dashboards, tools và runbooks.
- Security nên tiếp tục tách rõ fundamentals, access control, host security, network security, container/cloud security, security operations và incident response.
- Helm/Kustomize/Argo CD có thể xuất hiện song song với Kubernetes: Kubernetes giữ object/cluster-side behavior, CI/CD giữ release pipeline và GitOps workflow.
