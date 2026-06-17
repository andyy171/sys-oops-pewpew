# DevOps Hands-On Labs

## Overview

Note này gom các lab DevOps rời rạc trong `_inbox`: CI/CD Jenkins/GitLab, Docker web app, deploy app lên Kubernetes, pipeline end-to-end và monitoring bằng Prometheus/Grafana. Mục tiêu là giữ lại flow thực hành có thể xem nhanh, không copy từng lab dài theo kiểu checklist máy móc.

## Lab 1: Web App Với Docker

Mục tiêu:

- tạo app đơn giản;
- viết Dockerfile;
- build image;
- chạy container;
- dùng Docker Compose khi app có nhiều service.

Flow:

```text
Source code -> Dockerfile -> docker build -> docker run -> docker logs/curl
```

Checklist:

```bash
docker build -t example-app:<tag> .
docker run --name example-app -d -p 8080:8080 example-app:<tag>
docker ps
docker logs --tail 100 example-app
curl -I http://localhost:8080
```

Điểm cần hiểu: image là artifact build, container là runtime instance. Nếu sửa source, phải rebuild image hoặc dùng bind mount trong môi trường dev.

## Lab 2: CI/CD Cơ Bản Với Jenkins Hoặc GitLab CI

Pipeline tối thiểu:

```text
checkout -> build -> test -> package -> publish artifact -> deploy
```

Ví dụ stage logic:

```yaml
stages:
  - build
  - test
  - package
  - deploy
```

Điểm cần kiểm tra:

- pipeline trigger theo branch/tag nào;
- secret được lưu trong CI variable, không hard-code;
- artifact có version;
- deploy có log và rollback path;
- fail ở stage nào thì dừng ở stage đó, không deploy artifact lỗi.

## Lab 3: Deploy App Lên Kubernetes

Flow:

```text
Container image -> Deployment -> Service -> Ingress/NodePort -> health check
```

Manifest tối thiểu thường gồm:

- Deployment để quản lý replica và rollout;
- Service để có endpoint ổn định;
- Ingress nếu cần HTTP routing từ bên ngoài;
- ConfigMap/Secret nếu app cần cấu hình.

Kiểm tra nhanh:

```bash
kubectl get deploy,rs,pod,svc,ingress -n <namespace>
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace>
kubectl rollout status deploy/<deployment> -n <namespace>
```

## Lab 4: Pipeline End-To-End

Pipeline trưởng thành hơn:

```text
Git push
  -> CI build/test
  -> code quality gate
  -> artifact/image publish
  -> image vulnerability scan
  -> deploy staging
  -> smoke test
  -> approval hoặc promotion
  -> deploy production
  -> monitor/alert
```

Điểm đáng học nhất là artifact promotion: cùng một artifact/image đã test ở staging nên được promote sang production, thay vì build lại một artifact khác cho production.

## Lab 5: Monitoring Prometheus Và Grafana

Mục tiêu:

- Prometheus scrape metrics từ app/exporter;
- Grafana visualize metric;
- alert hoặc dashboard giúp phát hiện vấn đề sau deploy.

Flow:

```text
App/exporter exposes /metrics -> Prometheus scrape -> Grafana dashboard -> alert/evidence
```

Khi lab bằng Docker Compose, cần kiểm tra:

```bash
docker compose ps
docker compose logs -f prometheus
docker compose logs -f grafana
```

Khi lab bằng Kubernetes, cần kiểm tra ServiceMonitor/PodMonitor nếu dùng Prometheus Operator, hoặc scrape config nếu dùng Prometheus thuần.

## Troubleshooting Mindset

Khi pipeline fail, đừng nhảy thẳng vào sửa YAML. Đi theo layer:

1. Source có đúng branch/commit không?
2. Build dependency có resolve được không?
3. Test fail vì code hay vì môi trường?
4. Artifact/image có publish đúng registry không?
5. Deploy dùng đúng tag chưa?
6. App có Ready không?
7. Service/Ingress có route đúng không?
8. Monitoring/log có cho thấy lỗi runtime không?

## Related Pages

- [DevOps Lifecycle, Environments And Interview Flow](./00-devops-lifecycle-environments-and-interview-flow.md)
- [Jenkins, GitLab CI, GitHub Actions](./01-continuous-integration/Jenkins,%20GitLab%20CI,%20GitHub%20Actions.md)
- [Docker Practice And Operations Patterns](../../03-compute-and-orchestration/02-container-runtime/06-docker-practice-and-operations-patterns.md)
- [Kubernetes Troubleshooting Runbooks](../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/troubleshooting/overview.md)
