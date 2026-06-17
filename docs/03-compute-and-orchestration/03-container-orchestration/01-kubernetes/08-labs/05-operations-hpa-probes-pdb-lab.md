# Kubernetes Operations HPA, Probes Và PDB Lab

## Goal

Thực hành các cơ chế vận hành căn bản: probes, HPA và PodDisruptionBudget. Lab này ưu tiên quan sát object/status/events hơn là tạo tải phức tạp.

## What You Will Learn

- Readiness quyết định Pod có nhận traffic hay không.
- HPA cần metrics backend và resource requests phù hợp.
- PDB bảo vệ availability khi drain/eviction tự nguyện.

## Topology

```text
Deployment
-> Pods with probes and requests
-> HPA watches metrics
-> PDB controls voluntary disruption
```

## Prerequisites

- Cluster lab.
- Metrics server nếu muốn HPA có metric thật.

## Safety Notes

Không test drain node production trong lab này.

## Steps

```bash
kubectl create ns k8s-lab
kubectl create deployment web --image=nginx:1.25 -n k8s-lab --replicas=2
kubectl set resources deployment/web -n k8s-lab --requests=cpu=100m,memory=128Mi --limits=cpu=500m,memory=256Mi
kubectl autoscale deployment web -n k8s-lab --cpu-percent=60 --min=2 --max=5
kubectl create pdb web-pdb -n k8s-lab --selector=app=web --min-available=1
```

## Validation

```bash
kubectl get deploy,pod,hpa,pdb -n k8s-lab
kubectl describe hpa web -n k8s-lab
kubectl get events -n k8s-lab --sort-by=.lastTimestamp
```

Nếu metrics server không có, HPA có thể hiện `<unknown>`. Đây là tín hiệu để học dependency của autoscaling, không phải lỗi Deployment.

## Cleanup

```bash
kubectl delete ns k8s-lab
```

## Common Failure Cases

- HPA không tính được vì container thiếu `requests.cpu`.
- Metrics API chưa sẵn sàng.
- PDB quá chặt làm maintenance khó.
- Readiness probe sai khiến Service không có endpoint.

## Related Theory

- [Resources, Probes, Autoscaling Và Disruption](../05-operations/01-resources-probes-autoscaling-and-disruption.md)
- [Kubernetes Troubleshooting Runbooks](../98-troubleshooting/overview.md)
