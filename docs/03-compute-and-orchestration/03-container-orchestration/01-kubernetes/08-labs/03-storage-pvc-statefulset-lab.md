# Kubernetes Storage PVC Và StatefulSet Lab

## Goal

Tạo PVC và StatefulSet đơn giản để quan sát identity ổn định, volume claim và storage binding.

## What You Will Learn

- PVC là claim; PV/backend storage mới là nơi dữ liệu thật.
- StatefulSet tạo Pod identity ổn định như `app-0`, `app-1`.
- StorageClass/CSI quyết định cách volume được provision.

## Topology

```text
StatefulSet
-> volumeClaimTemplate
-> PVC
-> PV
-> StorageClass / CSI backend
```

## Prerequisites

- Cluster lab có default StorageClass.

## Safety Notes

Không dùng StorageClass production hoặc volume chứa dữ liệu thật.

## Steps

Tạo namespace:

```bash
kubectl create ns k8s-lab
```

Apply StatefulSet tối giản:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
  namespace: k8s-lab
spec:
  serviceName: web
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        volumeMounts:
        - name: data
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```

## Validation

```bash
kubectl get statefulset,pod,pvc,pv -n k8s-lab
kubectl describe pvc -n k8s-lab
```

## Cleanup

```bash
kubectl delete ns k8s-lab
```

Nếu PV reclaim policy là `Retain`, cần kiểm tra PV sau khi xóa namespace:

```bash
kubectl get pv
```

## Common Failure Cases

- PVC Pending do không có default StorageClass.
- CSI provisioner lỗi hoặc storage backend không sẵn sàng.
- Access mode không phù hợp workload.

## Related Theory

- [Persistent Storage Và StatefulSet](../03-storage/01-persistent-storage-and-statefulsets.md)
