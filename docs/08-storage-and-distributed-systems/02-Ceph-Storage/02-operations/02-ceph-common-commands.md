






# Các câu lệnh thường dùng
###Kiểm tra Cluster health
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
