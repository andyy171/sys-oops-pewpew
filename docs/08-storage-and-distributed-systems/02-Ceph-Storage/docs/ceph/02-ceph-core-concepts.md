# Các khái niệm chính của Ceph 

## Các dịch vụ cốt lõi của Ceph
![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/ceph-core-services.png)


## Các khái niệm nền tảng & Cơ chế Phân tán Dữ liệu
### 



### 

### 

### E
### 
### 

###  Ceph pools
- Nhóm logic chứa nhiều PG, định nghĩa chính sách lưu trữ (replication size, crush rule).
- Mỗi pool có ID riêng, dùng cho object/block/file. Ceph tự tạo PG khi tạo pool.
- Ceph pool cung cấp khả năng quản lý storage = pool. Ceph pool = logical partition để lưu các obj. Mỗi pool trong Ceph lưu 1 số các placement group – giữ số lượng acsc obj mapp tới OSDs trên khắp cluster. Vì thế mỗi single pool được phân phối khắp cluster nodes.

## Các Giao Diện Truy Cập
### 




## Các Thành Phần Phụ Trợ & Tối Ưu Hóa



### 

### Smart Daemons, Failure Domain, Reweighting
- **Smart Daemons**: Daemon tự động điều chỉnh (OSD báo full, MON tự elect leader).
    
    **Cơ chế vận hành**: Dùng agent để monitor và tự sửa.
    
- **Failure Domain**: Đơn vị chịu lỗi (rack, host, OSD) trong CRUSH map.
    
    **Cơ chế vận hành**: Đảm bảo replicas không cùng domain (như 3 replicas ở 3 rack).
    
    **Ví dụ**: Không để tất cả trứng trong một giỏ.
    
- **Reweighting**: Điều chỉnh trọng số OSD (0-1) để cân bằng dữ liệu.
    
    **Cơ chế vận hành**: Giảm weight cho OSD chậm/full, dữ liệu được di chuyển dần. Lệnh: ceph osd reweight.
    
    **Ví dụ**: Như giảm tải xe nếu bánh xe yếu.


