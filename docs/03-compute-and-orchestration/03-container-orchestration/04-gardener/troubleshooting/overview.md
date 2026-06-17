# Gardener Troubleshooting

## Overview

Troubleshooting Gardener nên bắt đầu từ `Shoot` object trong Garden cluster, sau đó mới đi xuống Seed và Shoot. Luôn xác nhận context trước khi chạy lệnh vì cùng một câu lệnh `kubectl` có thể đang trỏ vào Garden, Seed hoặc Shoot.

## First Checks

```bash
kubectl config current-context
kubectl get shoots -A
kubectl describe shoot <shoot-name> -n <project-namespace>
kubectl get events -n <project-namespace> --sort-by=.metadata.creationTimestamp
```

## Runbooks

- [Shoot Reconcile Failed](./01-shoot-reconcile-failed.md)
- [Shoot Access And Kubeconfig](./02-shoot-access-and-kubeconfig.md)
- [Seed Or gardenlet Not Ready](./03-seed-or-gardenlet-not-ready.md)

## Related Pages

- [Gardener Observability Và Troubleshooting Map](../07-observability-and-troubleshooting-map.md)
- [Gardener Architecture And Core Concepts](../01-architecture-and-core-concepts.md)
