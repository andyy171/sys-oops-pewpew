# Các khái niệm cốt lõi của Ceph

## 1. RADOS: lớp lõi của Ceph
- RADOS, viết tắt của Reliable Autonomic Distributed Object Store, là lớp lưu trữ nền tảng của toàn bộ Ceph. Đây không phải là một “service nhỏ” nằm bên dưới các gateway, mà là lõi lưu trữ thực sự của cluster: nơi dữ liệu được tổ chức, phân phối, bảo vệ và phục hồi khi có lỗi. Các lớp truy cập như RBD, CephFS, RGW hay librados chỉ là những cách khác nhau để ứng dụng giao tiếp với cùng một lõi RADOS đó.

- Điểm quan trọng nhất cần nắm là Ceph không được xây dựng xoay quanh một storage controller trung tâm. Thay vào đó, Ceph phân phối cả dữ liệu lẫn trách nhiệm xử lý I/O ra nhiều daemon trong cluster, đặc biệt là các OSD. Chính RADOS là lớp cho phép việc này diễn ra một cách nhất quán: object được đưa vào pool, được ánh xạ vào placement group, rồi được CRUSH phân phối tới các OSD phù hợp. Cách thiết kế này giúp Ceph mở rộng theo chiều ngang, giảm bottleneck và loại bỏ sự phụ thuộc vào một metadata service trung tâm cho từng thao tác đọc ghi.

- Về mặt tư duy kiến trúc, có thể hình dung Ceph gồm hai lớp lớn. 
    - Ở phía trên là lớp truy cập mà ứng dụng nhìn thấy, ví dụ block, file hoặc object API. 
    - Ở phía dưới là RADOS, nơi mọi thứ cuối cùng đều quy về object storage phân tán. Điều này rất quan trọng, vì nó giúp người đọc hiểu rằng dù use case là VM disk, bucket S3 hay file system phân tán, bản chất lưu trữ bên dưới vẫn đi qua cùng một cơ chế lõi.


### Các đặc tính nền tảng của RADOS
- RADOS được mô tả bằng bốn đặc tính cơ bản ngay trong tên gọi của nó: Reliable( Đáng tin cậy), Autonomic(Tự quản trị), Distributed ( Phân tán) và Object Store( Lưu trữ dưới dạng Object). Tuy nhiên, thay vì nhớ theo khẩu hiệu, nên hiểu chúng theo ý nghĩa kỹ thuật.
    - RADOS là reliable vì nó không dựa vào một bản copy duy nhất của dữ liệu. Dữ liệu có thể được bảo vệ bằng replication hoặc erasure coding, và cluster có các cơ chế recovery, peering, backfill và rebalance để giữ dữ liệu ở trạng thái an toàn ngay cả khi OSD hoặc host bị lỗi. 
    - RADOS là autonomic vì nhiều quá trình quản trị nền như phát hiện lỗi, phân phối lại dữ liệu và phục hồi redundancy diễn ra tự động thay vì đòi hỏi quản trị viên phải điều khiển từng object. 
    - RADOS là distributed vì placement không phụ thuộc vào một bảng metadata trung tâm cho từng object, mà dựa vào cluster map và thuật toán CRUSH chạy phân tán ở client/daemon. 
    - Cuối cùng, RADOS là object store vì ở lõi thấp nhất, dữ liệu được quản lý dưới dạng object chứ không phải file hệ điều hành truyền thống.


## 2. Mô hình dữ liệu trong Ceph
Muốn hiểu Ceph, cần bắt đầu từ cách nó nhìn dữ liệu. Ceph không quản lý trực tiếp “một file lớn” hay “một disk ảo nguyên khối” ở tầng thấp nhất. Thay vào đó, dữ liệu được biểu diễn thành các object, các object thuộc về một pool, rồi được gom logic qua placement group (PG) trước khi được ánh xạ xuống các OSD. Đây là lớp trung gian quan trọng nhất trong thiết kế nội bộ của Ceph.

### 2.1 Object

- **Object là đơn vị lưu trữ cơ bản của RADOS.** Một object bao gồm dữ liệu nhị phân và metadata đi kèm, và tồn tại trong một namespace phẳng bên trong pool. Điều này có nghĩa là ở lõi RADOS không có khái niệm thư mục như trong filesystem truyền thống; **thứ được quản lý là object name, data và metadata**. Ceph docs cũng nhấn mạnh rằng **ở tầng librados, ứng dụng chỉ cần biết object name và các thuộc tính liên quan**; phần placement xuống OSD được hệ thống xử lý thông qua cluster map và CRUSH.

- Khi nói `“RBD image được chia thành object”` hay `“dữ liệu object storage được lưu dưới dạng object”`, điều đó không có nghĩa object là một file Linux dễ thấy trên filesystem của node. **Object là đơn vị logic của RADOS; còn việc OSD ghi chúng xuống thiết bị vật lý như thế nào là trách nhiệm của backend lưu trữ như BlueStore**. Đây là một chỗ người mới rất hay hiểu sai.

### 2.2 Pool

- **Pool là vùng logic chứa object và đồng thời là đơn vị áp dụng chính sách lưu trữ**. Một object **luôn thuộc về một pool cụ thể**, và chính pool quyết định nhiều thuộc tính quan trọng như **kiểu bảo vệ dữ liệu (replicated hay erasure-coded), số lượng PG, CRUSH rule sử dụng** và đôi khi cả các **giới hạn quota hoặc application tag**. Nói ngắn gọn, nếu object là đơn vị dữ liệu cơ bản, thì **pool là đơn vị chính sách cơ bản.**

- Trong tài liệu vận hành, người ta thường nói` “tạo pool cho RBD”`, `“pool metadata cho CephFS”`, hay `“pool data cho RGW”`. Điều đó phản ánh đúng vai trò của pool: tách biệt workload và tách biệt chính sách. Một cluster thường có nhiều pool để đáp ứng các kiểu truy cập và độ quan trọng dữ liệu khác nhau.

### 2.3 Placement Group (PG)

- Placement Group là một trong những khái niệm quan trọng nhất của Ceph. Theo docs, **object không được ánh xạ trực tiếp tới OSD, mà trước tiên được ánh xạ vào PG; sau đó PG mới được ánh xạ tới một tập OSD**. Lý do tồn tại của lớp trung gian này là để **tránh việc hệ thống phải quản lý placement và lịch sử của từng object một cách riêng lẻ**, vốn sẽ rất tốn kém ở quy mô lớn.

- Có thể xem PG như một `“đơn vị phân phối và quản lý nội bộ”` của Ceph. Hệ thống **không rebalance từng object độc lập** theo cách người dùng nhìn thấy, mà **rebalance ở mức PG**. Tương tự,**recovery, peering hay backfill cũng gắn chặt với PG**. Nhờ có PG, **Ceph có thể mở rộng cluster mà vẫn giữ được mô hình placement có thể tính toán được**, thay vì biến việc quản trị object thành một bài toán quá lớn.

### 2.4 Acting set, up set và primary OSD
- **Mỗi PG tại một thời điểm sẽ gắn với một nhóm OSD**. Trong số đó, có **một OSD giữ vai trò primary**, chịu trách nhiệm điều phối thao tác đọc ghi cho PG. Ceph docs về peering phân biệt khá rõ giữa acting set và up set:   
    - acting set là danh sách OSD đang hoặc đã chịu trách nhiệm cho PG trong một epoch nhất định.
    - up set phản ánh tập OSD mà CRUSH tính ra nên chịu trách nhiệm theo map hiện tại. 
    > Khi cluster ổn định, hai tập này thường trùng nhau; khi có thay đổi topology hoặc lỗi, chúng có thể tạm thời khác nhau.
- Việc nắm hai khái niệm này giúp đọc trạng thái PG dễ hơn rất nhiều. Nó cũng giải thích tại sao trong thời gian rebalance hoặc recovery, PG có thể chưa clean: vì placement “lý tưởng” theo map mới và placement “đang có dữ liệu thực tế” chưa đồng nhất hoàn toàn.

### 2.5 Vì sao Ceph cần lớp trung gian là PG

- Lý do tồn tại của PG không chỉ là tiện cho placement, mà còn là nền tảng cho khả năng scale-out của Ceph. Nếu client phải biết trực tiếp object nào nằm trên OSD nào, thì mỗi lần thêm OSD hoặc thay đổi topology, số lượng metadata và số quyết định phải cập nhật sẽ tăng khổng lồ. Bằng cách đưa vào lớp PG, Ceph chỉ cần thay đổi ánh xạ giữa PG và OSD, còn object vẫn đi theo PG tương ứng. Docs Ceph mô tả rất rõ đây là “lớp abstraction và indirection” giữa client và OSD.

### Bảng tóm tắt 
| Khái niệm            | Vai trò chính                       | Ý nghĩa thực tế                                |
| -------------------- | ----------------------------------- | ---------------------------------------------- |
| Object               | Đơn vị dữ liệu cơ bản               | Dữ liệu lõi của RADOS                          |
| Pool                 | Đơn vị chính sách lưu trữ           | Quyết định durability, PG, CRUSH rule          |
| PG                   | Đơn vị placement và quản trị nội bộ | Giúp rebalance, recovery, peering ở quy mô lớn |
| Primary OSD          | OSD điều phối I/O của PG            | Đầu mối xử lý đọc ghi cho PG                   |
| Acting set / Up set  | Tập OSD thực tế / lý tưởng của PG   | Quan trọng khi cluster thay đổi trạng thái     |
| ([docs.ceph.com][1]) |                                     |                                                |

[1]: https://docs.ceph.com/en/pacific/dev/placement-group/"PG (Placement Group) notes - Ceph Documentation"

### Minh hoạt liên kết 
```
Ứng dụng / Client
      ↓
   Object
      ↓
    Pool
      ↓
     PG
      ↓
CRUSH tính ra OSD set
      ↓
Primary OSD + Replica/Shard OSDs
```

>> Keynote : Trong Ceph, rất nhiều khái niệm dễ bị nhầm vì chúng nằm ở các tầng khác nhau. Pool là đơn vị chính sách, PG là đơn vị phân phối và quản trị nội bộ, OSD là đơn vị thực thi lưu trữ, còn object mới là đơn vị dữ liệu nền tảng. Điểm quan trọng là Ceph không quản lý trực tiếp từng object theo kiểu một bảng tra cứu trung tâm, mà dùng lớp trung gian là PG để làm cho placement, recovery và rebalancing có thể mở rộng ở quy mô lớn. Hiểu được “Ceph quản lý dữ liệu theo PG chứ không theo từng object độc lập” là một trong những chìa khóa lớn nhất để hiểu toàn bộ hệ thống.
## 3. CRUSH và topology của cluster
- CRUSH là một trong những thành phần làm nên bản sắc của Ceph. Nếu PG là lớp trung gian giữa object và OSD, thì CRUSH là cơ chế quyết định PG đó sẽ được đặt ở đâu trong cluster. Điểm đặc biệt là CRUSH không cần một bảng metadata trung tâm để tra cứu vị trí dữ liệu. Thay vào đó, client và daemon dùng cùng cluster map và cùng thuật toán để tính ra cùng một kết quả placement. Đây chính là nền tảng của kiến trúc phân tán trong Ceph.
### 3.1 CRUSH là gì
- CRUSH là viết tắt của Controlled Replication Under Scalable Hashing. Khác với việc băm đơn thuần rồi chọn đích ngẫu nhiên, CRUSH là một cơ chế pseudo-random có kiểm soát: nó vừa phân phối dữ liệu đều, vừa tôn trọng topology vật lý và chính sách placement mà quản trị viên đã định nghĩa trong CRUSH map. Do đó, placement trong Ceph vừa có tính xác định, vừa có khả năng phản ánh cấu trúc thực của hạ tầng như host, rack hoặc datacenter.

- Một đặc tính rất quan trọng của CRUSH là *deterministic mapping*. Với cùng đầu vào gồm object/PG, CRUSH map và CRUSH rule, **mọi thành phần đều tính ra cùng một danh sách OSD đích**. Điều này loại bỏ nhu cầu hỏi một metadata server trung tâm mỗi khi cần đọc hoặc ghi dữ liệu. Đây là một lợi ích cực lớn khi cluster có quy mô lớn và nhiều client hoạt động đồng thời.

### 3.2 CRUSH map
- CRUSH không hoạt động trong khoảng trống; nó dựa vào CRUSH map. Đây là cấu trúc mô tả topology logic của cluster và các rule placement áp dụng cho từng kiểu workload. Trong CRUSH map, OSD là các leaf node, còn các lớp bên trên như host, rack, row, room hay datacenter là các bucket. Chính cấu trúc này cho phép Ceph “hiểu” khái niệm failure domain và phân phối replica hoặc shard ra các vùng lỗi khác nhau.
- Điều quan trọng cần nhớ là CRUSH map không chỉ là “danh sách OSD”. Nó là **mô hình placement của cả cluster**. Khi **topology thay đổi**, ví dụ thêm OSD mới hoặc thay đổi weight, kết quả tính toán **placement thay đổi theo**. Nhờ đặc tính minimal remap của CRUSH, chỉ phần dữ liệu liên quan mới cần di chuyển, thay vì toàn cluster phải xáo trộn toàn bộ.

### 3.3 Bucket hierarchy và failure domain
- Một CRUSH map điển hình có dạng phân cấp như sau:
```
root
 ├── rack-a
 │    ├── host-01
 │    │    ├── osd.0
 │    │    └── osd.1
 │    └── host-02
 │         ├── osd.2
 │         └── osd.3
 └── rack-b
      ├── host-03
      │    ├── osd.4
      │    └── osd.5
      └── host-04
           ├── osd.6
           └── osd.7
```

- Docs Ceph mô tả rõ mục tiêu của bucket hierarchy là tách các leaf node theo failure domain, chẳng hạn host, chassis, rack, row, room hoặc datacenter. Việc tạo hierarchy như vậy giúp replica hoặc EC shard không dồn vào cùng một vùng lỗi vật lý. Đây là nền tảng để Ceph chịu được lỗi host, lỗi rack hoặc lỗi mức cao hơn tùy cách thiết kế cluster.

- Failure domain không phải là một khái niệm trừu tượng để “cho đẹp tài liệu”, mà là quyết định trực tiếp ảnh hưởng tới tính sẵn sàng. Nếu cluster có nhiều rack nhưng rule chỉ tách replica theo host, thì một sự cố mất điện cả rack vẫn có thể làm nhiều replica cùng biến mất. Ngược lại, nếu cấu hình failure domain quá lớn so với thực tế topology, ví dụ chỉ có 2 rack nhưng cố chọn 3 replica ở 3 rack khác nhau, cluster sẽ khó đạt trạng thái placement như mong muốn. Vì vậy, **failure domain phải đi cùng hiện trạng vật lý thực và số replica hoặc số EC shard cần đặt.**

### 3.4 Device class và performance domain
- Ngoài topology vật lý, Ceph còn cho phép phân loại OSD theo **device class** như `hdd`, `ssd` hoặc `nvme`. Docs Ceph cho biết CRUSH rule có thể được tạo theo pool type, failure domain và tùy chọn thêm device class. Điều này rất hữu ích khi muốn tách pool “nóng” chạy trên SSD/NVMe và pool “lạnh” chạy trên HDD mà vẫn dùng chung một cluster.

- Device class không thay thế failure domain. Nó giải quyết một bài toán khác: **performance domain.** Failure domain giúp tránh mất dữ liệu cùng lúc do sự cố vật lý; device class giúp gom workload theo loại thiết bị để tối ưu hiệu năng hoặc chi phí. Hai khái niệm này thường đi cùng nhau trong thiết kế cluster nhưng không nên gộp làm một.

### 3.5 CRUSH rules
- CRUSH rule là tập quy tắc mô tả cách placement được thực hiện. Với replicated pool, rule thường yêu cầu chọn một số replica trên các leaf thuộc các failure domain khác nhau. Với erasure-coded pool, rule cần đảm bảo các shard được phân phối đủ rộng để cluster có thể chịu lỗi theo profile EC. Docs Ceph nêu rõ CRUSH rules có thể được tạo bằng CLI bằng cách chỉ rõ loại pool, failure domain và tùy chọn device class; trường hợp đặc biệt mới phải chỉnh map thủ công.
- Trong thực tế, khi đọc một pool của Ceph, người quản trị nên luôn tự hỏi ba điều: pool đó dùng replicated hay EC, CRUSH rule của nó là gì, và rule đó đang tách dữ liệu theo failure domain nào. Ba câu hỏi này thường giải thích được hầu hết các hành vi placement quan trọng của pool.


## 4. Durability và tính nhất quán
- Khả năng lưu trữ phân tán chỉ thực sự có ý nghĩa khi hệ thống vừa giữ được dữ liệu an toàn, vừa cung cấp hành vi nhất quán cho client. Trong Ceph, hai cơ chế bảo vệ dữ liệu chính là replication và erasure coding. Bên cạnh đó, docs cũng nhấn mạnh rằng thao tác đọc ghi đi qua primary OSD và các OSD trong PG phải đồng thuận về trạng thái thông qua peering, từ đó đảm bảo cluster không chỉ “có nhiều bản copy” mà còn duy trì được logic nhất quán của dữ liệu.

### 4.1 Replication
- Replication là cơ chế dễ hiểu nhất: mỗi object hoặc mỗi PG được lưu thành nhiều bản sao trên nhiều OSD khác nhau. Trong mô hình replicated pool, một OSD đóng vai trò primary, các OSD còn lại giữ replica. Khi client ghi dữ liệu, primary OSD điều phối việc ghi và đồng bộ tới các replica theo chính sách của pool. Cách làm này đơn giản, dễ vận hành và rất phù hợp với các workload cần độ trễ thấp hoặc cần hỗ trợ đầy đủ tính năng metadata/omap.

- Replication có ưu điểm là quá trình phục hồi và truy xuất thường dễ hiểu hơn EC, nhưng đổi lại chi phí dung lượng cao hơn. Ví dụ, pool size 3 nghĩa là tổng raw storage tiêu tốn sẽ xấp xỉ gấp ba dung lượng logic của dữ liệu.

### 4.2 Erasure Coding

- Erasure coding (EC) bảo vệ dữ liệu bằng cách chia object thành các phần dữ liệu và phần parity thay vì sao chép nguyên bản hoàn chỉnh nhiều lần. Cách làm này tiết kiệm không gian hơn replication, đặc biệt với dữ liệu lớn hoặc lạnh. Tuy nhiên, EC thường đánh đổi bằng độ phức tạp cao hơn trong tính toán, ghi và phục hồi. Vì vậy, EC phù hợp với những workload mà hiệu quả dung lượng quan trọng hơn độ trễ ghi thấp.

- Điều quan trọng là không nên hiểu EC như `“RAID phần mềm phóng to”`. Trong Ceph, EC vẫn gắn với pool, PG, CRUSH rule và failure domain của cluster phân tán. Shard của cùng một object cần được đặt trên các OSD khác nhau một cách có chủ đích; đây là điểm giúp EC trong Ceph mạnh hơn so với một cơ chế parity chỉ gói gọn trong một máy chủ.

### 4.3 Strong consistency trong Ceph

- Ceph hướng tới tính nhất quán mạnh ở mức object thông qua cơ chế primary OSD và ordering trong PG. Docs về peering cho thấy các OSD lưu cùng một PG phải “đưa nhau về cùng nhận thức” về trạng thái object và metadata của PG đó. Tuy nhiên, việc cùng đồng ý về trạng thái không tự động đồng nghĩa rằng mọi bản copy đã luôn có dữ liệu mới nhất ở mọi thời điểm trung gian; chính vì vậy peering, recovery và authoritative log mới tồn tại.

- Đối với người học Ceph ở mức core concepts, điều cần nhớ là: client không ghi thẳng vào mọi replica, mà ghi vào primary OSD của PG; primary OSD là đầu mối điều phối consistency. Đây là nền tảng của hành vi đọc ghi trong Ceph replicated model.

### 4.4 Khi nào dùng replicated pool và khi nào dùng erasure-coded pool
Không có một kiểu pool phù hợp cho mọi bài toán. Lựa chọn nên dựa trên tính chất workload.

- Replicated pool phù hợp với:
    - dữ liệu nóng
    - metadata-heavy workload
    - block storage cho VM
    - workload cần latency thấp
- Erasure-coded pool phù hợp với:
    - dữ liệu lớn, ít sửa đổi
    - object storage dung lượng lớn
    - archive, backup, cold data
    - workload ưu tiên hiệu quả dung lượng hơn tốc độ ghi nhỏ lẻ

### So sánh replicated và erasure-coded pool
| Tiêu chí                 | Replicated pool               | Erasure-coded pool                      |
| ------------------------ | ----------------------------- | --------------------------------------- |
| Cơ chế bảo vệ dữ liệu    | Nhiều bản sao hoàn chỉnh      | Chia shard dữ liệu và parity            |
| Hiệu quả dung lượng      | Thấp hơn                      | Cao hơn                                 |
| Độ đơn giản khi vận hành | Dễ hơn                        | Phức tạp hơn                            |
| Workload phù hợp         | Dữ liệu nóng, block, metadata | Dữ liệu lớn, archive, object            |
| Trade-off chính          | Tốn raw storage               | Tốn CPU/độ phức tạp khi ghi và phục hồi |
| ([Red Hat Docs][1])      |                               |                                         |

[1]: https://docs.redhat.com/en/documentation/red_hat_ceph_storage/5/html-single/architecture_guide/"Architecture Guide | Red Hat Ceph Storage | 5"

## 5. Cluster maps và cách client định vị dữ liệu

Một trong những chỗ người mới hay hiểu sai là nghĩ rằng MON “nắm giữ vị trí từng object” và client phải hỏi MON mỗi lần đọc hoặc ghi. Thực tế không phải vậy. MON phân phối các loại cluster map, còn client và daemon dùng các map này để tự tính toán placement. Chính điểm này làm Ceph khác rất nhiều so với các kiến trúc phụ thuộc vào một metadata server trung tâm cho từng I/O.

### 5.1 Monitor map

Monitor map mô tả các monitor trong cluster, gồm thông tin định danh và địa chỉ cần thiết để client hoặc daemon kết nối đúng vào quorum MON. Đây là bản đồ ở mức “làm sao nói chuyện với cluster control plane”.

### 5.2 OSD map

OSD map mô tả các OSD hiện có, trạng thái của chúng, các pool liên quan và những thông tin placement cần thiết khác. Khi trạng thái OSD thay đổi, OSD map thay đổi theo epoch mới. Đây là một trong những bản đồ quan trọng nhất đối với placement và trạng thái của PG.

### 5.3 CRUSH map

CRUSH map là phần topology và rules phục vụ placement. Nó là “mô hình hạ tầng” mà CRUSH dùng để tính xem PG cần đặt lên OSD nào. Đây là lý do vì sao CRUSH map luôn phải được nhìn cùng OSD map: một bên cho biết cái gì đang có, một bên cho biết cách chọn từ những gì đang có.

### 5.4 PG map

PG map cung cấp thông tin về trạng thái các placement group trong cluster. RHCS architecture guide cũng nhấn mạnh vai trò của Ceph Manager trong việc duy trì thông tin chi tiết hơn về placement group để cải thiện hiệu năng ở quy mô lớn, đồng thời xử lý nhiều truy vấn read-only liên quan tới PG statistics.

### 5.5 Client-side calculation

Khi client có đủ cluster map, nó không cần phải hỏi “object này đang nằm ở đâu” cho từng thao tác. Thay vào đó, object được ánh xạ vào PG, rồi PG được CRUSH ánh xạ tới một tập OSD. Docs librados và architecture docs đều mô tả mô hình này: client biết object name, pool và cluster map là đủ để đi tới đúng primary OSD.

### Luồng liên kết
```
MON cung cấp map
      ↓
Client dùng map + object/pool
      ↓
Tính ra PG
      ↓
CRUSH tính ra OSD set
      ↓
Client kết nối trực tiếp primary OSD
```

## 6. Xác thực và phân quyền
Ceph không cho phép mọi client hoặc daemon tự do nói chuyện với nhau mà không kiểm soát. Cơ chế xác thực mặc định là **Cephx**, dùng để xác minh danh tính các thành phần tham gia cluster và cấp quyền truy cập phù hợp. Docs RHCS 5 configuration guide và Ceph user management đều tách khá rõ giữa authentication và authorization: trước tiên phải xác thực thành công, sau đó các capability mới quyết định client được làm gì.

### 6.1 Cephx là gì

Cephx là cơ chế auth nội bộ của Ceph. Client dùng secret tương ứng trong keyring để xác thực với cluster, nhận ticket có thời hạn, rồi dùng ticket đó khi làm việc với các daemon như OSD, MON hoặc MDS. Điểm hay của mô hình này là client không cần gửi “mật khẩu gốc” cho mọi request sau đó; thay vào đó, ticket và session material được dùng để tiếp tục giao tiếp an toàn hơn. RHCS 5 config guide cũng nhắc rõ ticket của client có thời gian sống nhất định.

### 6.2 Keyring

Keyring là nơi chứa key và capability của client hoặc daemon. Với daemon, data directory mặc định thường nằm dưới /var/lib/ceph/$type/<cluster-id>; RHCS 5 config guide cũng lưu ý monitor keyring có đặc điểm riêng: nó chứa key nhưng không có capabilities và không nằm trong auth database theo cách user thông thường.

### 6.3 Capabilities (caps)

- Capabilities là cơ chế phân quyền theo service trong Ceph. Chúng định nghĩa client hoặc daemon được phép làm gì với mon, osd, mds, mgr. Docs user management của Ceph nhấn mạnh rằng Ceph Storage Cluster user không giống với user của RGW hay user của CephFS ở tầng ứng dụng; đây là chỗ rất dễ nhầm nếu chỉ đọc tài liệu theo gateway.

- Ở mức khái niệm, có thể hiểu:

    - `mon` caps điều khiển quyền thao tác với monitor
    - `osd` caps điều khiển quyền truy cập dữ liệu/pool
    - `mds` caps liên quan tới CephFS
    - `mgr` caps liên quan tới manager APIs hoặc module tương ứng
### 6.4 Authentication flow ở mức khái niệm

Một luồng auth đơn giản có thể hình dung như sau:
```
Client đọc ceph.conf / mon endpoints
      ↓
Client nạp keyring
      ↓
Kết nối MON và xác thực bằng Cephx
      ↓
Nhận ticket / session material
      ↓
Dùng ticket làm việc với OSD/MDS/MON theo caps được cấp
```

> Trong RHCS 5, ngoài Cephx, security in transit còn được tăng cường bởi messenger v2 với mã hóa mặc định cho traffic mạng. Tuy vậy, về mặt core concepts, người đọc chỉ cần nắm chắc rằng Cephx xử lý danh tính và quyền, còn transport security là một lớp khác bổ trợ cho giao tiếp an toàn.


## 7. Các cơ chế nền giúp cluster hoạt động liên tục

Một cluster Ceph không chỉ là tập OSD nhận dữ liệu rồi “để đó”. Khi topology thay đổi, OSD lỗi hoặc cluster mở rộng, Ceph cần các cơ chế nền để giữ dữ liệu an toàn và đưa cluster trở về trạng thái bình thường. Bốn khái niệm cốt lõi cần nắm là peering, recovery, backfill và rebalancing. RHCS architecture guide và docs Ceph đều xem đây là các hành vi tự nhiên của cluster chứ không phải tác vụ “bên ngoài” do quản trị viên tự dựng lên.

### 7.1 Peering

- Peering là quá trình đưa các OSD lưu cùng một PG về sự đồng thuận đối với trạng thái object và metadata của PG đó. Docs Ceph nói rất rõ: việc các OSD cùng đồng ý về trạng thái không có nghĩa là chúng đều đã có dữ liệu mới nhất, nhưng nó là điều kiện cần để cluster biết bản log nào authoritative và cần phục hồi từ đâu.

- Peering vì vậy là bước logic rất quan trọng sau các thay đổi về OSDMap hoặc sau sự cố. Nếu không hiểu peering, người đọc sẽ rất khó hiểu vì sao một PG có thể “up” nhưng chưa “clean”.

### 7.2 Recovery

Recovery là quá trình khôi phục mức redundancy bị thiếu sau khi xảy ra lỗi hoặc gián đoạn. Nếu một replica bị mất hoặc outdated, cluster cần đồng bộ lại để PG trở về trạng thái an toàn. Về bản chất, recovery ưu tiên khôi phục độ bền dữ liệu trước khi nghĩ tới cân bằng đẹp hay tối ưu phân bố. Đây là phản ứng tự nhiên của cluster trước lỗi.

### 7.3 Backfill

Backfill thường xuất hiện khi cần đưa dữ liệu tới một OSD mới hoặc tới placement mới mà OSD đích chưa có lịch sử cần thiết để chỉ đồng bộ delta nhỏ. So với recovery dựa trên khác biệt hẹp, backfill thường “nặng” hơn vì phải chuyển một phần dữ liệu lớn hơn ở mức PG. Đây là lý do backfill thường được xem là loại tác vụ dễ tạo tải I/O và mạng đáng kể trong cluster.

### 7.4 Rebalancing

- Rebalancing là quá trình cluster phân phối lại dữ liệu khi topology thay đổi, ví dụ thêm OSD mới, thay đổi weight hoặc loại bỏ OSD. Ceph architecture docs nhấn mạnh rằng chính lớp PG và CRUSH cho phép cluster tăng hoặc giảm quy mô rồi phân phối lại object một cách động. Khi placement “lý tưởng” theo map mới khác placement cũ, cluster sẽ dần chuyển dữ liệu để tiến về trạng thái cân bằng mới.

- Điều cần nhớ là rebalancing không có nghĩa `“mọi dữ liệu đều bị xáo trộn lại”`. Một ưu điểm quan trọng của CRUSH là **chỉ di chuyển phần dữ liệu liên quan tới thay đổi topology, nhờ đó cluster vẫn có thể mở rộng mà không phải remap toàn bộ.** - Di chuyển ít biến động nhất.

### So sánh các cơ chế nền
| Cơ chế              | Mục tiêu chính                                                   | Khi nào xuất hiện               |
| ------------------- | ---------------------------------------------------------------- | ------------------------------- |
| Peering             | Đồng thuận về trạng thái PG                                      | Sau thay đổi map hoặc sau sự cố |
| Recovery            | Khôi phục bản sao/shard bị thiếu hoặc cũ                         | Khi redundancy bị suy giảm      |
| Backfill            | Chuyển dữ liệu tới OSD/placement mới chưa có nền lịch sử phù hợp | Khi thêm OSD hoặc remap lớn     |
| Rebalancing         | Phân phối lại dữ liệu theo topology mới                          | Khi thay đổi cấu trúc cluster   |
| ([Red Hat Docs][1]) |                                                                  |                                 |

[1]: https://docs.redhat.com/en/documentation/red_hat_ceph_storage/5/html/architecture_guide/the-core-ceph-components"Chapter 2. The core Ceph components | Architecture Guide"

## 8. Các khái niệm quản trị thường gặp

File core concepts không nên biến thành tài liệu admin chi tiết, nhưng có một số khái niệm quản trị hiện đại vẫn nên có mặt vì chúng ảnh hưởng trực tiếp tới cách hiểu Ceph ngày nay, đặc biệt trong RHCS 5 và Ceph Pacific.

### 8.1 PG autoscaler

- Tài liệu hiện đại của Ceph và RHCS 5 đều nhấn mạnh PG autoscaler. Ceph docs mô tả PG là chi tiết triển khai nội bộ để phân phối dữ liệu và cho phép cluster tự đưa ra khuyến nghị hoặc tự động điều chỉnh số PG tùy theo cấu hình pg_autoscale_mode. RHCS cũng nêu rõ rằng từ RHCS 5 trở đi, pg_autoscale_mode mặc định là on cho pool mới.

- Điều này rất quan trọng vì nhiều tài liệu cũ thường đặt nặng công thức tính PG thủ công. Trong cluster hiện đại, người đọc vẫn cần hiểu bản chất PG count ảnh hưởng tới balancing và tài nguyên, nhưng không nên coi công thức cũ là trung tâm duy nhất nữa. Autoscaler đã trở thành phần quan trọng trong vận hành thực tế.

### 8.2 Pool quotas

Quota cho phép giới hạn số object hoặc tổng dung lượng mà pool có thể sử dụng. Đây không phải là khái niệm placement cốt lõi, nhưng nó là khái niệm quản trị nền rất thực tế vì pool là đơn vị chính sách và tách biệt workload. Khi dùng nhiều pool cho nhiều dịch vụ khác nhau, quota giúp tránh việc một workload “ăn hết” raw capacity của cluster.

### 8.3 Application tags

Application tag là nhãn cho biết pool được dùng bởi lớp truy cập nào, ví dụ rbd, cephfs, rgw. Đây là metadata quản trị hữu ích để cluster và công cụ quản trị hiểu pool đang phục vụ mục đích gì. Trong thiết kế tài liệu, application tags nên được xem là “thông tin định danh workload”, không phải cơ chế placement.

### 8.4 Global flags thường gặp

Trong vận hành thực tế, quản trị viên thường gặp các flag toàn cluster như `noout`, `norebalance` hoặc `noautoscale`. Những flag này có tác động lớn tới hành vi của cluster khi topology thay đổi. 
    Ví dụ, `noout` ngăn OSD bị đánh dấu out khi nó ngừng hoạt động, trong khi `norebalance` ngăn cluster tự động rebalance khi OSD mới được thêm vào. Hiểu rõ ý nghĩa và tác động của các flag này là rất quan trọng để tránh những hậu quả không mong muốn khi cluster gặp sự cố hoặc thay đổi topology.


## 9. Những điều rất dễ hiểu sai về Ceph
### 9.1 Ceph không có metadata server trung tâm cho mọi I/O

MON không phải nơi giữ “bản đồ object chi tiết” để trả lời từng lần client hỏi. Client lấy cluster map từ MON, sau đó tự tính placement và nói chuyện trực tiếp với OSD. Đây là đặc tính cốt lõi của kiến trúc Ceph.

### 9.2 Pool không chỉ là một “bucket logic”

Cách ví pool như “container lớn chứa dữ liệu” chỉ đúng ở mức rất sơ cấp. Quan trọng hơn, pool là đơn vị áp chính sách durability, PG count và CRUSH rule. Không hiểu điều này thì sẽ khó thiết kế cluster đúng ngay từ đầu.

### 9.3 PG không phải là dữ liệu vật lý

PG là đơn vị logic nội bộ dùng để placement và quản trị object ở quy mô lớn. Nó không phải “một thư mục trên đĩa” theo nghĩa đơn giản mà người mới hay hình dung. Docs Ceph gọi PG là chi tiết triển khai nội bộ của cách Ceph phân phối dữ liệu.

### 9.4 BlueStore không phải một dịch vụ độc lập

BlueStore là backend lưu trữ của OSD, không phải một gateway hay một layer truy cập riêng. Khi nói “Ceph lưu object bằng BlueStore”, điều đúng hơn là OSD dùng BlueStore để ghi dữ liệu xuống thiết bị lưu trữ. RHCS config guide cũng cho thấy data directory của daemon nằm dưới /var/lib/ceph/..., nhưng việc backend lưu như thế nào là phần bên trong của OSD chứ không phải một service độc lập.

### 9.5 Công thức PG cũ không còn là toàn bộ câu chuyện

Trong cluster hiện đại dùng RHCS 5 hoặc Ceph Pacific, cần hiểu PG count vẫn quan trọng, nhưng autoscaler đã thay đổi đáng kể cách cluster được vận hành. Vì vậy, tài liệu core nên giải thích bản chất và vai trò của PG, rồi mới nhắc autoscaler, thay vì dạy người mới phụ thuộc hoàn toàn vào công thức cũ.

## 10. Kết luận

- Ceph là một hệ thống lưu trữ phân tán mà lõi của nó là RADOS. Trong RADOS, dữ liệu được quản lý dưới dạng object, thuộc về pool, đi qua placement group và được CRUSH ánh xạ tới các OSD dựa trên topology của cluster. Chính sự kết hợp giữa object model, PG indirection, cluster maps và CRUSH đã tạo ra kiến trúc phi tập trung đặc trưng của Ceph: client tự tính được placement, cluster tự phục hồi khi có lỗi và dữ liệu có thể được phân phối lại khi hệ thống mở rộng.

### Phụ lục minh họa : bức tranh tổng thể
```
                +----------------------+
                |  RBD / CephFS / RGW  |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |        RADOS         |
                |  Object / Pool / PG  |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |        CRUSH         |
                |  Rule / Topology     |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |       OSD Set        |
                | Primary + Replicas   |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |  Device / BlueStore  |
                +----------------------+
```