# Mục lục
- [Mục lục](#mục-lục)
- [Tổng quan](#tổng-quan)
- [Cluster Maps](#cluster-maps)
- [Replication (Nhân bản Dữ Liệu) - Cơ chế Chịu lỗi Mặc định](#replication-nhân-bản-dữ-liệu---cơ-chế-chịu-lỗi-mặc-định)
  - [**Cơ chế hoạt động :**](#cơ-chế-hoạt-động-)
  - [Replication Strategy](#replication-strategy)
    - [Pool size và min\_size](#pool-size-và-min_size)
    - [Primary-copy Replication](#primary-copy-replication)

# Tổng quan


# Cluster Maps
Cluster maps là "GPS" giúp client và OSD biết vị trí dữ liệu. MON duy trì và phân phối.

- **OSD Map**: Liệt kê tất cả OSD (ID, trạng thái up/in).
    
    **Cơ chế vận hành**: Cập nhật khi OSD join/leave.
    
- **CRUSH Map**: Định nghĩa cấu trúc cluster (host, rack) và rule phân bổ.
    
    **Cơ chế vận hành**: Dùng để tính vị trí PG.
    
- **PG Map**: Vị trí từng PG (OSD nào là primary/replicas).
    
    **Cơ chế vận hành**: Giúp client đọc/ghi trực tiếp OSD mà không qua MON.
    
    **Ví dụ**: OSD Map như danh sách địa điểm, CRUSH Map như tuyến đường.

- MDS Map

- Monitor Map chứa cluster fsid, vị trí, tên, địa chỉ và TCP port của mỗi monitor, cùng với epoch và thời gian tạo/sửa đổi




# Replication (Nhân bản Dữ Liệu) - Cơ chế Chịu lỗi Mặc định
- Replication là phương pháp mặc định của Ceph để đảm bảo tính sẵn sàng và chịu lỗi, đặc biệt hiệu quả cho dữ liệu cần hiệu năng cao (hot data).

- Ceph tạo ra nhiều bản sao đầy đủ của cùng một đối tượng (object) và lưu trữ chúng trên các OSD khác nhau.

![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/rep-1.png)

##  **Cơ chế hoạt động :**
1. **Client Tính toán:** Client sử dụng CRUSH Lookup để xác định OSD Primary cho dữ liệu. </br> 
2. **Client Ghi:** Client ghi dữ liệu tới OSD Primary. </br> 
3. **OSD Primary Nhân bản:** OSD Primary chịu trách nhiệm nhân bản dữ liệu tới các OSD Secondary/Replica theo số lượng bản sao quy định (thường là 3 bản sao, tức 2 replicas). </br> 
4. **Xác nhận (ACK):** Chỉ sau khi nhận được xác nhận (ACK) từ tất cả OSD (Primary và Secondary) rằng dữ liệu đã được ghi an toàn, OSD Primary mới gửi ACK lại cho Client.

- **Ưu điểm :**
+ **Hiệu năng Đọc/Ghi cao:** Ghi nhanh (chỉ cần ghi 1 lần tới Primary, sau đó Replication là nội bộ OSD), đọc có thể được phân tán. </br> 
+ **Độ trễ thấp:** Phù hợp cho các ứng dụng đòi hỏi độ trễ thấp (như Block Device - RBD). </br> 
+ **Phục hồi Nhanh:** Dữ liệu đã đầy đủ, chỉ cần copy bản sao hiện có.

- **Nhược điểm :** Chi phí Lưu trữ cao: Với mức nhân bản mặc định là 3, bạn cần 3 lần dung lượng đĩa vật lý để lưu trữ dữ liệu (overhead 200%).

>Toàn bộ quá trình nhân bản giữa OSD Primary và Secondary diễn ra trên Cluster Network (Mạng riêng). Do đó, nếu mạng này chậm, nó sẽ ảnh hưởng trực tiếp đến tốc độ ghi của client, vì client phải chờ ACK. 

## Replication Strategy
### Pool size và min_size

size thiết lập số lượng replicas cho objects trong pool, trong khi min_size thiết lập số lượng replicas tối thiểu cần có để PGs active và cho phép I/O operations Scaleway
Write chỉ được acknowledge lại cho client khi min_size requirement của pool được đáp ứng, tức là write đã được persist trên ít nhất min_size OSDs Medium
Để high availability, Ceph Storage Cluster nên lưu nhiều hơn 2 copies của object (size = 3 và min_size = 2) để có thể tiếp tục chạy ở degraded state trong khi vẫn duy trì data safety


###  Primary-copy Replication


Trong mỗi Placement Group, Ceph gán một OSD làm Primary. Primary OSD điều phối tất cả write operations cho PG đó và đảm bảo consistency giữa các replicas Medium
Ceph OSDs sử dụng CRUSH algorithm để xác định vị trí lưu trữ của object replicas, và clients cũng dùng CRUSH để xác định vị trí của object Red Hat