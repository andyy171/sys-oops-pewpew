# Gardener Seed Or gardenlet Not Ready

## Triệu Chứng

- Nhiều Shoot trên cùng Seed reconcile chậm hoặc fail.
- Shoot mới không được schedule vào Seed.
- Seed condition không healthy.
- gardenlet Pod lỗi, restart hoặc mất kết nối Garden API.

## Triage Nhanh

Trong Garden cluster:

```bash
kubectl get seeds
kubectl describe seed <seed-name>
```

Trong Seed cluster:

```bash
kubectl get pods -A | grep gardenlet
kubectl describe pod <gardenlet-pod> -n <gardenlet-namespace>
kubectl logs <gardenlet-pod> -n <gardenlet-namespace>
kubectl get ns | grep shoot--
```

## Nguyên Nhân Thường Gặp

- gardenlet không kết nối được Garden API.
- Certificate/bootstrap hoặc RBAC của gardenlet lỗi.
- Seed thiếu capacity hoặc node pressure.
- Extension controller trong Seed lỗi.
- Network giữa Seed và Shoot/control plane bị lỗi.
- Upgrade Seed hoặc gardenlet chưa hoàn tất.

## Mitigation

- Không restart hàng loạt component nếu chưa giữ log và event.
- Xác định blast radius: Seed này đang host Shoot nào.
- Nếu capacity issue, giảm scheduling vào Seed hoặc mở rộng Seed theo runbook.
- Nếu gardenlet cert/RBAC issue, xử lý theo quy trình platform, tránh cấp quyền rộng tạm thời rồi quên thu hồi.

## Related Pages

- [Seed Operations Và Capacity](../05-seed-operations-and-capacity.md)
- [Observability Và Troubleshooting Map](../07-observability-and-troubleshooting-map.md)
