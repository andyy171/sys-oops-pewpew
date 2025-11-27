# Các câu lệnh thường dùng


## Kiểm tra Cluster health
Quick overview về tình trạng Cluster, các lỗi (nếu có), tình trạng các OSD, node.
```
ceph status
```
## Kiểm tra dung lượng Ceph Cluster
Kiểm tra dung lượng đã sử dụng trên Ceph Cluster
```
ceph df
```
## Xem CRUSH map
```
ceph osd tree
```

## Tạo hoặc xóa OSD
```
ceph osd create || ceph osd rm osd.<id>
```
## List cluster key
```
ceph auth list
```


## `ceph orch redeploy `
- Lệnh ceph orch redeploy là một công cụ mạnh mẽ, ép buộc Ceph áp dụng lại cấu hình dịch vụ và khởi động lại các daemon. Redeploy thực hiện việc khởi động lại hoàn toàn kèm theo việc áp dụng lại cấu hình, trong khi restart chỉ khởi động lại một cách nhẹ nhàng mà không đọc lại toàn bộ cấu hình. Chỉ nên sử dụng redeploy khi thực sự cần thiết, chẳng hạn để các thay đổi về cấu hình hoặc phiên bản có hiệu lực.

![](./images/ceph-redeploy.png)

### Một số thay đổi quan trọng 
1. Khi chỉnh sửa các tham số đòi hỏi phải khởi động lại dịch vụ để áp dụng:

```bash
ceph config set mds mds_cache_memory_limit 8G
ceph orch redeploy mds
```

2. Khi một số daemon đang chạy các phiên bản khác nhau sau khi nâng cấp

```bash
ceph orch redeploy mon  # Dành cho sự khác biệt phiên bản monitor
```

3. Khi các dịch vụ ở trạng thái thất bại hoặc lỗi và không tự phục hồi:
```bash
ceph orch redeploy grafana
```

4. Sau khi áp dụng các bản vá CVE đòi hỏi khởi động lại dịch vụ:

```bash
ceph orch redeploy all  # Dành cho cập nhật bảo mật toàn cụm
```

5. Khi dịch vụ bị giết do hết bộ nhớ (OOM) hoặc chạm giới hạn tài nguyên:

```bash
ceph orch redeploy osd --name osd.12  # Dành cho OSD cụ thể đang gặp vấn đề
```

6. Sau khi cập nhật chứng chỉ SSL cho RGW hoặc dashboard MGR:
```bash
ceph orch redeploy rgw
```

7. Khi chỉnh sửa thiết lập mạng cụm ảnh hưởng đến giao tiếp daemon:
```bash
ceph orch redeploy mon
```

8. Đối với các cảnh báo như "daemon không chạy phiên bản mới nhất" hoặc "cấu hình chưa áp dụng":

```bash
ceph orch redeploy mds.mycluster
```

- Khi Không Nên Sử Dụng Redeploy:
    - Để khởi động lại thông thường (thay vào đó dùng ceph orch restart)
    - Trong giờ cao điểm làm việc (gây gián đoạn dịch vụ tạm thời)
    - Là bước khắc phục sự cố đầu tiên (kiểm tra nhật ký trước với ceph logs)

> Luôn kiểm tra trạng thái dịch vụ trước:
> ```bash
>ceph orch ps --daemon-type mds  # Kiểm tra trạng thái >MDS trước khi redeploy
>ceph orch redeploy mds --dry-run  # Xem trước những gì sẽ xảy ra
```
