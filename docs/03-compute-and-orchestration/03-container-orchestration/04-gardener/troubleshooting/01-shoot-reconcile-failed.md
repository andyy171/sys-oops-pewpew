# Gardener Shoot Reconcile Failed

## Triệu Chứng

- `Shoot.status.lastOperation` báo `Error`, `Failed` hoặc reconcile kẹt lâu.
- Shoot không tạo xong, update không hoàn tất hoặc delete bị kẹt.
- Events trong Project namespace lặp lại cùng một lỗi.

## Triage Nhanh

```bash
kubectl describe shoot <shoot-name> -n <project-namespace>
kubectl get events -n <project-namespace> --sort-by=.metadata.creationTimestamp
kubectl get shoot <shoot-name> -n <project-namespace> -o yaml
```

## Nguyên Nhân Thường Gặp

- Không tìm được Seed phù hợp.
- Credentials provider thiếu quyền hoặc hết hạn.
- Provider quota không đủ.
- CloudProfile không còn option hợp lệ.
- Network CIDR overlap hoặc DNS/network extension fail.
- Worker pool machine type/OS image không còn support.
- Extension controller lỗi hoặc version không tương thích.

## Debug Theo Lớp

1. Đọc `lastOperation` và condition.
2. Xác định lỗi thuộc scheduling, infrastructure, control plane, worker hay add-on.
3. Nếu đã có `seedName`, chuyển sang Seed cluster và kiểm tra gardenlet/extension.
4. Nếu lỗi provider, kiểm tra quota, permission, region, subnet, DNS và LB.
5. Sau khi sửa, theo dõi reconcile tiếp theo thay vì apply nhiều thay đổi cùng lúc.

## Mitigation

- Sửa credential/quota/provider config trước nếu lỗi nằm ở hạ tầng.
- Nếu update spec gây lỗi, rollback về spec gần nhất đã chạy được nếu field cho phép.
- Nếu delete kẹt, kiểm tra finalizer và extension cleanup; không xóa finalizer khi chưa hiểu tài nguyên external còn lại.

## Related Pages

- [Shoot Lifecycle Và Day-2 Operations](../02-shoot-lifecycle-and-day2-operations.md)
- [Observability Và Troubleshooting Map](../07-observability-and-troubleshooting-map.md)
