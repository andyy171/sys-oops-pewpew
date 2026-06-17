# Keepalived And HAProxy Pattern

Keepalived + HAProxy là pattern phổ biến để tạo entrypoint HA tự quản lý trong private cloud hoặc bare metal.

## Vai Trò

- **HAProxy:** phân phối traffic L4/L7 đến backend.
- **Keepalived/VRRP:** quản lý virtual IP giữa nhiều load balancer node.

## Luồng Cơ Bản

```text
Client -> VIP -> active load balancer -> backend pool
```

Khi active load balancer lỗi, VIP được chuyển sang node còn lại.

## Điểm Thiết Kế

- Health check phải kiểm tra cả HAProxy process và khả năng route đến backend.
- Priority VRRP cần rõ ràng, tránh node tranh VIP.
- Config HAProxy giữa các node phải đồng nhất.
- Log và metric cần gom tập trung để debug failover.

## Khi Không Nên Dùng

- Hệ thống đã có cloud/provider load balancer đáp ứng SLA.
- Team không có năng lực vận hành network/VIP/failover.
- Multi-region cần DNS/GSLB thay vì chỉ VIP local.

## Liên Quan

- [Load Balancing Algorithms](../03-patterns/03-load-balancing-algorithms.md)
