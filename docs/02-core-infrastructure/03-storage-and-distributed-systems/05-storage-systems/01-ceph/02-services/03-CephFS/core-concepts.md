# CephFS

## 1. CephFS là gì

- `CephFS` là hệ thống tệp phân tán của Ceph, tương thích mạnh với mô hình POSIX và được xây dựng trực tiếp trên `RADOS`. Ceph docs mô tả CephFS như một file system dùng cho nhiều kiểu workload như shared home directories, HPC scratch space và distributed workflow shared storage. Điều quan trọng nhất là: CephFS không phải một backend tách biệt khỏi Ceph, mà là **file interface** được dựng lên trên cùng object store phân tán của cluster.

- Nếu nhìn từ phía ứng dụng, CephFS cho bạn thứ quen thuộc là thư mục, file, phân quyền, mount point và thao tác kiểu filesystem. Nhưng nếu nhìn từ phía Ceph, dữ liệu vẫn quay về các object trong `RADOS`. Đây là điểm cốt lõi nhất cần giữ trong đầu: **CephFS trình bày dữ liệu như file, nhưng backend thật vẫn là object store**. 

> `CephFS` không làm Ceph “biến thành một NAS truyền thống”. Đúng hơn, CephFS là cách Ceph dựng **ngữ nghĩa file** lên trên một lõi object store phân tán. Vì vậy, file là thứ người dùng nhìn thấy; object mới là thứ cluster thật sự lưu bên dưới. 

## 2. Kiến trúc cơ bản của CephFS

- Kiến trúc của CephFS dựa trên một tách biệt rất rõ giữa **metadata** và **file data**. Ceph docs Pacific và Squid đều nhấn mạnh rằng metadata của file được lưu trong một `RADOS pool` riêng, còn dữ liệu file được lưu trong một `RADOS pool` khác; phía trên đó là một cụm `MDS` có thể mở rộng để phục vụ metadata workloads. RHCS 5 File System Guide và RHCS 8 docs cũng yêu cầu tối thiểu hai pool: một cho metadata và một cho data. 

- Điểm đáng giá nhất của thiết kế này là client CephFS **đọc và ghi dữ liệu file trực tiếp xuống RADOS**, không phải đẩy toàn bộ luồng dữ liệu đi qua `MDS`. `MDS` chủ yếu điều phối metadata, trạng thái truy cập và cache metadata phân tán. Ceph docs nói rất rõ: there is no gateway or broker mediating data I/O for clients. Chính chi tiết này làm CephFS khác hẳn mô hình file server tập trung truyền thống. 

### Minh họa kiến trúc CephFS

```
Ứng dụng / Client CephFS
        ↓
  Metadata lookup qua MDS
        ↓
Xác định inode / path / quyền / layout
        ↓
Client đọc hoặc ghi file data trực tiếp vào RADOS
```

> Nếu phải gói CephFS vào một câu, thì câu đúng nhất là: MDS điều phối metadata, còn client đi thẳng tới RADOS để làm dữ liệu file. Chính vì vậy, MDS rất quan trọng, nhưng MDS không phải là “đường ống chở toàn bộ dữ liệu file”.

## 3. MDS thực sự làm gì

- MDS là Metadata Server của CephFS. Ceph docs mô tả MDS là nơi phục vụ metadata và là “authority” cho trạng thái của distributed metadata cache được duy trì phối hợp giữa client và MDS. Metadata ở đây bao gồm inode, quyền, thời gian, quan hệ thư mục-cha/con, tên file, layout và các thông tin cần thiết để hệ thống tệp hoạt động như một filesystem đúng nghĩa.

- Một ý rất quan trọng là MDS không lưu metadata state cục bộ như nguồn chân lý cuối cùng. Ceph docs nói rõ rằng các thay đổi metadata được MDS gom lại thành các lần ghi hiệu quả vào journal trên RADOS; không có metadata state nào được giữ cục bộ như “bản duy nhất” trong MDS. Điều này giúp CephFS vừa có semantics kiểu filesystem, vừa vẫn giữ được tinh thần phân tán của Ceph.

- CephFS còn hỗ trợ resizable cluster of MDS, tức là cụm MDS có thể mở rộng để tăng thông lượng metadata nếu workload thật sự cần. RHCS 5 cũng nhấn mạnh rằng từ RHCS 5 có thể chạy nhiều file systems active trên một cluster và mỗi CephFS có tập pool và tập MDS ranks riêng của nó. Điều này cho thấy MDS là lớp có thể scale cho metadata, chứ không phải một metadata server đơn lẻ cố định như nhiều hệ thống file phân tán đời cũ.

## 4. Data path và metadata path khác nhau ra sao

- Đây là chỗ dễ nhầm nhất khi học CephFS. Khi client truy cập /path/to/file, phần tra cứu tên đường dẫn, inode, quyền truy cập, layout và trạng thái cache metadata sẽ đi qua MDS. Nhưng khi client đã biết file nằm ở đâu và layout dữ liệu của file đó ra sao, thì các khối dữ liệu file được đọc và ghi trực tiếp xuống RADOS. Ceph docs Pacific và Squid đều khẳng định rất rõ điều này.

- Từ góc nhìn hệ thống, điều đó có hai hệ quả rất quan trọng. Thứ nhất, CephFS tránh được nút nghẽn dữ liệu tập trung ở metadata server. Thứ hai, hiệu năng của CephFS thường bị tách làm hai câu chuyện: metadata performance và data performance. Nếu workload tạo/xóa/đổi tên file hàng loạt hoặc duyệt cây thư mục rất nhiều, MDS sẽ là thành phần đáng chú ý nhất. Nếu workload chủ yếu là đọc ghi nội dung file lớn, lớp RADOS/OSD và mạng sẽ là nơi quyết định nhiều hơn.

> Muốn hiểu đúng CephFS, phải luôn tách luồng metadata và luồng dữ liệu file. Rất nhiều phán đoán sai về hiệu năng CephFS bắt nguồn từ việc coi cả hai là một.

## 5. Metadata cache phân tán và vì sao CephFS không quá “nặng MDS” như người mới hay tưởng

- Ceph docs về MDS Cache Configuration mô tả rằng MDS phối hợp một distributed metadata cache giữa các client CephFS và chính MDS. Cơ chế này giúp client giữ lại một phần metadata trong bộ nhớ để giảm độ trễ, trong khi MDS vẫn duy trì thẩm quyền đối với trạng thái metadata. Các mutation metadata được điều phối qua capabilities và leases để bảo đảm tính nhất quán.

- Điều này nghĩa là CephFS không chỉ là “mọi thao tác file đều hỏi MDS từng chút một”. Thực tế, MDS đóng vai trò điều phối và cấp quyền giữ cache metadata, giúp client xử lý nhiều thao tác hiệu quả hơn khi trạng thái đang nhất quán. Đây là một trong những lý do CephFS có thể phục vụ workload metadata đáng kể mà không biến MDS thành điểm nghẽn tuyệt đối ngay lập tức.

- Tuy nhiên, điểm cần nhớ là metadata vẫn là phần nhạy cảm và khó scale hơn dữ liệu file thuần túy. Chính vì vậy, CephFS thường phù hợp hơn khi bạn thực sự cần semantics của filesystem dùng chung, chứ không phải chỉ vì “Ceph cũng có file service”.

## 6. CephFS lưu dữ liệu ở tầng pool như thế nào

- RHCS 5 và RHCS 8 docs đều nhấn mạnh rằng CephFS thường dùng hai pool chính:
    - một pool cho metadata
    - một pool cho file data

- RHCS Data Security and Hardening Guide còn nói rõ hơn: metadata pool giữ dữ liệu của MDS, chủ yếu là inodes, quyền, timestamps, thư mục cha, và các thông tin liên quan; còn data pool giữ file data, và một file có thể được lưu thành một hoặc nhiều object, thường tương ứng với các phần nhỏ hơn của dữ liệu file như extents. Đây là một diễn đạt rất tốt vì nó nối filesystem semantics với object backend theo cách cực kỳ rõ ràng.

> Trong CephFS, “một file” không có nghĩa là “một object” hay “một file vật lý cục bộ trên đĩa OSD”. Một file logic có thể tương ứng với nhiều object trong data pool, còn metadata của nó lại nằm trong metadata pool. Đây là một ví dụ điển hình cho việc thứ người dùng thấy và thứ Ceph thật sự lưu là hai tầng khác nhau.

## 7. CephFS dùng trong trường hợp nào

- Ceph docs mô tả CephFS phù hợp với các kiểu workload như shared home directories, HPC scratch space và distributed workflow shared storage. Tức là những bài toán nơi nhiều client cùng cần một không gian file thống nhất, có semantics kiểu filesystem, và không muốn phải tự dựng NFS truyền thống hoặc các lớp chia sẻ file phía trên block storage.

- CephFS hợp nhất khi bạn thật sự cần:

    - cây thư mục dùng chung cho nhiều máy
    - phân quyền và metadata kiểu filesystem
    - truy cập qua mount thay vì API object hoặc volume block
    - một lớp file trực tiếp trên hạ tầng Ceph hiện có

- Ngược lại, nếu ứng dụng chỉ cần block device cho VM hoặc database, RBD thường tự nhiên hơn. Nếu ứng dụng nói ngôn ngữ S3/Swift, RGW thường đúng hơn. Đây là lý do trong nhiều môi trường cloud phổ thông, CephFS thường ít xuất hiện hơn RBD hoặc RGW: không phải vì nó yếu, mà vì bài toán cần filesystem shared semantics thực sự không phải lúc nào cũng phổ biến bằng block volumes hay object APIs. Đây là một suy luận kiến trúc dựa trên mô hình dùng service, không phải một giới hạn kỹ thuật tuyệt đối.

## 8. CephFS và khả năng sẵn sàng cao

- CephFS đạt tính sẵn sàng cao nhờ ba lớp kết hợp với nhau:
    - dữ liệu file nằm trên RADOS, nên hưởng toàn bộ cơ chế durability của cluster
    - metadata nằm trong metadata pool trên RADOS
    - MDS có thể chạy theo mô hình active/standby và scale theo ranks khi cần

- Điểm tinh tế ở đây là metadata path và data path cùng hưởng lợi từ Ceph, nhưng không theo cùng một cách. Data path hưởng lợi trực tiếp từ OSD/CRUSH/PG giống mọi workload RADOS khác. Metadata path hưởng lợi từ việc metadata state không bị giữ cục bộ như bản duy nhất ở MDS, mà được journal về RADOS. Điều này giúp CephFS tránh được nhiều điểm yếu truyền thống của file server tập trung.

## 9. CephFS và những giới hạn hoặc điểm cần thận trọng

- CephFS không phải lựa chọn “cứ có Ceph là nên bật thêm”. Nó phù hợp khi ứng dụng thực sự cần filesystem semantics. Ceph docs cho thấy xung quanh CephFS tồn tại cả một vùng quản trị riêng khá sâu: MDS states, journaling, distributed metadata cache, directory fragmentation, multiple active MDS daemons, snapshots, quotas, disaster recovery, metadata repair. Chỉ riêng độ rộng của bộ tài liệu này cũng cho thấy CephFS là một service có tính chuyên môn riêng chứ không chỉ là “RBD nhưng mount được như thư mục”.

- Một điểm rất thực tế là nếu bạn ít dùng CephFS, thì điều quan trọng nhất không phải học thuộc mọi lệnh MDS, mà là giữ một mô hình đúng:
    - CephFS là file interface
    - metadata đi qua MDS
    - file data vẫn đi thẳng xuống RADOS
    - metadata pool và data pool là hai lớp khác nhau
    - CephFS chỉ đáng chọn khi bạn thực sự cần semantics của filesystem dùng chung

## Tổng kết 
- CephFS là file interface của Ceph, được xây trên cùng lõi RADOS như các service khác. Điểm đặc trưng nhất của nó là tách metadata và data: MDS điều phối metadata và distributed metadata cache, còn client đọc ghi file data trực tiếp vào RADOS. Chính mô hình này giúp CephFS vừa giữ được semantics kiểu filesystem, vừa tránh trở thành file server tập trung ở data path.
> CephFS là file interface trên object backend, trong đó MDS quản metadata còn file data vẫn đi thẳng xuống RADOS.

- Các lưu ý quan trọng : 
    - CephFS vẫn là filesystem xây trên RADOS
    - metadata và data vẫn tách pool
    - MDS vẫn phục vụ metadata
    - client vẫn đi trực tiếp tới RADOS cho file data
    - không có gateway trung gian cho data I/O

### Những hiểu lầm phổ biến về CephFS

- Hiểu lầm phổ biến nhất là nghĩ rằng MDS đứng giữa mọi thao tác dữ liệu file. Điều này sai. MDS điều phối metadata và cache metadata; dữ liệu file thực tế vẫn được client đọc ghi trực tiếp vào RADOS. Nếu không tách hai đường này, bạn sẽ hình dung CephFS sai ngay từ gốc.

- Hiểu lầm thứ hai là nghĩ rằng CephFS có backend file storage riêng, tách khỏi RADOS. Thực tế, CephFS vẫn dựa trên RADOS object store như RBD và RGW. Khác biệt nằm ở semantics và lớp metadata phía trên, không nằm ở việc có một backend lưu trữ lõi khác.

- Hiểu lầm thứ ba là cho rằng “ít thấy dùng” đồng nghĩa “ít quan trọng về mặt kiến trúc”. Thực ra CephFS rất quan trọng để hiểu cách Ceph có thể cung cấp filesystem semantics trên object backend. Ngay cả khi không dùng nhiều trong thực tế, nó vẫn là một mảnh ghép rất giá trị để hiểu triết lý unified storage của Ceph. Đây là một suy luận kiến trúc từ bản chất service layer của Ceph.