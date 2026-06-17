# Kubernetes Networking Service, Ingress Và DNS Lab

## Goal

Expose Deployment bằng Service, kiểm tra EndpointSlice và DNS nội bộ. Nếu cluster có ingress controller, mở rộng lab với Ingress.

## What You Will Learn

- Service chỉ route traffic khi có endpoint backend.
- DNS nội bộ trỏ tới Service name.
- Ingress/Gateway là lớp routing HTTP bên ngoài Service.

## Topology

```text
client Pod
-> DNS/CoreDNS
-> Service
-> EndpointSlice
-> Pod IP
```

## Prerequisites

- Cluster lab.
- Optional: ingress controller đã cài.

## Safety Notes

Dùng namespace riêng và không expose lab ra internet nếu chưa kiểm soát ingress.

## Steps

```bash
kubectl create ns k8s-lab
kubectl create deployment web --image=nginx:1.25 -n k8s-lab --replicas=2
kubectl expose deployment web --port=80 --target-port=80 -n k8s-lab
kubectl get svc,endpointslice,pod -n k8s-lab -o wide
```

Test từ client Pod:

```bash
kubectl run curl -n k8s-lab --image=curlimages/curl:8.8.0 --restart=Never -- sleep 3600
kubectl exec -n k8s-lab curl -- curl -sS http://web
```

## Validation

```bash
kubectl get svc web -n k8s-lab
kubectl get endpointslice -n k8s-lab -l kubernetes.io/service-name=web
kubectl describe svc web -n k8s-lab
```

## Cleanup

```bash
kubectl delete ns k8s-lab
```

## Common Failure Cases

- Service selector không match Pod label nên không có endpoint.
- Pod chưa Ready nên không nhận traffic.
- DNS lỗi do CoreDNS không healthy.
- Ingress host sai hoặc ingress controller chưa nhận rule.

## Related Theory

- [Service Discovery, Ingress Và Network Policy](../02-networking/01-service-discovery-ingress-and-network-policy.md)
- [Debug Flow Từ Symptom Đến Control Plane Decision](../98-troubleshooting/01-symptom-to-control-plane-debug-flow.md)
