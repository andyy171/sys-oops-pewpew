# Cluster Maps và Client Flow trong Ceph

## 1. Cluster map là gì và vì sao Ceph cần nó
- Trong Ceph, “cluster map” không phải là một file đơn lẻ hay một bảng tra cứu tĩnh. Nó là tập hợp các map mô tả trạng thái hiện tại của cluster, bao gồm topology, thành phần đang tồn tại, thành phần nào đang up hoặc down, trạng thái placement groups, và các thông tin liên quan tới việc placement dữ liệu. Ceph docs định nghĩa cluster map là tập hợp các map như monitor map, OSD map, PG map, MDS map và CRUSH map; Squid architecture vẫn giữ mô hình năm map này.

- Điểm quan trọng là Ceph không dùng cluster map như một “bảng hỏi đáp vị trí object” theo kiểu client hỏi MON cho từng lần I/O. Thay vào đó, cluster map là đầu vào để client và daemon tự tính ra vị trí dữ liệu. Đây là khác biệt rất lớn giữa Ceph và nhiều kiến trúc lưu trữ truyền thống có broker, metadata service, hoặc controller trung tâm đứng giữa client và data path. Trong Ceph, MON giữ bản sao chủ của cluster map, còn client và OSD dùng bản sao hiện thời của map đó cộng với CRUSH để tự suy ra placement.

- Cũng vì cluster map là nền của toàn bộ việc định vị dữ liệu, Ceph yêu cầu client phải có map hiện thời trước khi thực hiện đọc hoặc ghi. Ceph Monitor docs ghi rõ rằng client phải kết nối tới MON để lấy current cluster map trước khi có thể đọc từ hoặc ghi tới OSD/MDS. Tuy nhiên, sau bước lấy map đó, client không còn cần một “phiên chatty” để hỏi vị trí từng object nữa; việc còn lại là tính toán cục bộ và kết nối trực tiếp tới OSD phù hợp.

## 2. Các map cấu thành cluster map
Theo Ceph glossary và Ceph architecture, cluster map ở nghĩa đầy đủ bao gồm monitor map, OSD map, PG map, CRUSH map và MDS map. Tuy nhiên, RHCS 8 Configuration Guide khi giới thiệu khái niệm “Ceph cluster maps” lại nhấn mạnh cluster map như một composite của monitor map, OSD map và placement group map. Đây là chỗ dễ gây hiểu nhầm nếu đọc tài liệu chéo phiên bản. Cần hiểu rằng đây là khác biệt trong cách đóng gói tài liệu, không phải thay đổi kiến trúc lõi: Ceph vẫn vận hành với đầy đủ các map thành phần, nhưng RHCS 8 config guide đang tập trung vào ba map quản trị cluster phổ biến nhất ở góc nhìn cấu hình và trạng thái.

### 2.1 Monitor Map

Monitor map chứa thông tin về chính các monitor: fsid của cluster, tên monitor, địa chỉ, cổng TCP, epoch hiện tại, thời điểm tạo và sửa đổi map. Đây là map cho phép client biết cần liên hệ với monitor nào để lấy thông tin mới nhất về cluster. Trong Squid architecture, monitor map vẫn được mô tả rõ là map số 1 trong cluster map, và cách xem điển hình vẫn là ceph mon dump.

### 2.2 OSD Map

OSD map là map quan trọng nhất đối với data path. Nó mô tả danh sách OSD, trạng thái up/in, thông tin pool, replica size, số lượng PG và các yếu tố cần thiết để hệ thống biết dữ liệu nên nằm ở đâu và OSD nào còn khả dụng. Pacific architecture và RHCS docs đều nhấn mạnh rằng OSD map thay đổi khi OSD được thêm, bị loại, down, out, hoặc khi topology/placement liên quan thay đổi. Đây là map mà client và OSD dựa vào để hiểu cluster hiện đang có những OSD nào thực sự tham gia vào placement.

### 2.3 PG Map

PG map phản ánh trạng thái của các placement group: phiên bản, timestamp, OSD map epoch cuối cùng liên quan, full ratios, Up Set, Acting Set, state như active+clean, cùng các thống kê dung lượng hoặc trạng thái pool. RHCS 8 config guide nhấn mạnh PG map ở góc nhìn quản trị: map này cho biết PG đang active hay inactive, clean hay degraded, và giúp admin theo dõi diễn biến cluster theo thời gian. Nếu OSD map cho biết “những OSD nào đang có mặt”, thì PG map cho biết “dữ liệu logic đang ở trạng thái nào”.

### 2.4 CRUSH Map

CRUSH map mô tả topology placement của cluster: danh sách thiết bị, hierarchy của failure domain như device, host, rack, row, room, và rules được dùng để duyệt cấu trúc này khi đặt dữ liệu. Đây không phải map “trạng thái động” theo nghĩa giống PG map, mà là mô hình placement và policy cho dữ liệu. Khi client hoặc OSD chạy CRUSH, chúng dựa vào chính map này để tính object/PG sẽ đi về OSD nào. Squid architecture vẫn liệt kê CRUSH map như một thành phần chính thức của cluster map.

### 2.5 MDS Map

MDS map chỉ thực sự liên quan khi sử dụng CephFS. Nó mô tả metadata servers nào đang up, in, pool metadata liên quan và epoch hiện hành của bản đồ MDS. Nếu file này đang nói về cluster map ở nghĩa tổng quát của Ceph, thì MDS map vẫn nên được nhắc tới; nhưng nếu chỉ nhìn từ data path chung của object/block storage, thì nó không tham gia trực tiếp vào client flow của RADOS object path như monitor map, OSD map, PG map và CRUSH map. Đây cũng là một lý do khiến một số tài liệu quản trị cluster nhấn mạnh 3 map đầu tiên hơn.

### Bảng tóm tắt các map
| Map                       | Chứa gì                                                                | Vai trò chính trong client flow                      |
| ------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------- |
| Monitor Map               | Danh sách monitor, địa chỉ, epoch                                      | Giúp client biết liên hệ monitor nào                 |
| OSD Map                   | Danh sách OSD, pool, trạng thái `up/in`, thông tin placement liên quan | Đầu vào chính để xác định OSD nào tham gia placement |
| PG Map                    | Trạng thái PG, Up Set, Acting Set, health/state                        | Giúp hiểu dữ liệu logic đang ở trạng thái nào        |
| CRUSH Map                 | Topology, failure domains, rules placement                             | Đầu vào cho phép tính placement                      |
| MDS Map                   | Trạng thái metadata servers và metadata pools                          | Liên quan riêng tới CephFS                           |
| ([Ceph Documentation][1]) |                                                                        |                                                      |

[1]: https://docs.ceph.com/en/squid/architecture/ "Architecture — Ceph Documentation"

## 3. Epoch và lịch sử thay đổi của map
- Một đặc điểm rất quan trọng của cluster maps là chúng không phải snapshot vô thời gian. Mỗi map có lịch sử phiên bản, và mỗi phiên bản được gọi là một epoch. RHCS 8 Configuration Guide nêu rất rõ rằng monitor map, OSD map và PG map đều duy trì lịch sử phiên bản, và mỗi version là một epoch; khi cluster có thay đổi đáng kể như OSD down hoặc PG degraded, cluster map sẽ được cập nhật để phản ánh trạng thái mới.

- Ý nghĩa thực tế của epoch là: client và daemon không chỉ cần “có map”, mà cần có map đủ mới để placement họ tính ra không bị lệch với trạng thái cluster hiện tại. Tuy nhiên, Ceph cũng không đòi hỏi mọi thành phần phải đi hỏi MON trước mỗi I/O. Thay vào đó, vì topology và state thường tương đối ổn định trong một phiên làm việc, client có thể hoạt động hiệu quả với bản sao map hiện có; khi cluster state đổi, client chỉ cần yêu cầu update map từ MON. RHCS 8 architecture guide nói rõ rằng khi cluster state thay đổi, client có thể đơn giản yêu cầu update cluster map từ Ceph monitor.

Đây là một điểm rất hay để hiểu Ceph: state được lan truyền theo mô hình “eventually refreshed but strongly authored by monitors”, chứ không theo mô hình “mọi thao tác đều phải round-trip qua control plane”. Nhờ vậy, Ceph vừa có tính nhất quán về nguồn chân lý của cluster state, vừa tránh được bottleneck trên control plane. Monitor config reference còn nhấn mạnh rằng MON duy trì master copy của cluster map và ghi thay đổi của monitor services qua Paxos vào key/value store để đảm bảo strong consistency ở lớp monitor state.

## 4. Client lấy cluster map như thế nào
- Trước khi có thể đọc hoặc ghi dữ liệu, client phải bind hoặc kết nối tới một Ceph Monitor để lấy current cluster map. Pacific architecture mô tả rất rõ: Ceph clients retrieve a copy of the cluster map from the Ceph Monitor; Squid architecture cũng giữ nguyên logic này và thậm chí viết thẳng rằng một Ceph Client phải contact monitor và obtain a current copy of the cluster map để có thể read/write vào cluster.

- Sau khi đã có map, client biết được:

    - cluster có những monitor nào
    - cluster có những OSD nào
    - nếu dùng CephFS thì có những metadata server nào
    - topology placement được mô tả ra sao
    - trạng thái cluster và placement logic hiện tại là gì ở mức cần thiết để thực hiện I/O.

> Điểm mấu chốt là client vẫn chưa biết object nằm ở đâu ngay cả khi đã có cluster map. Ceph docs ở cả Reef và Squid đều nhấn mạnh rõ điều này: có current cluster map không đồng nghĩa với việc biết object location; object location phải được tính toán. Đây là chỗ cluster map và CRUSH nối vào nhau. Cluster map cung cấp dữ kiện; CRUSH biến dữ kiện đó thành quyết định placement.

## 5. Từ cluster map đến object location: client tính placement ra sao
- Ceph không giữ một bảng trung tâm ánh xạ trực tiếp từ từng object tới từng OSD. Thay vào đó, object location được tính toán, không phải tra cứu. Khi client có được cluster map và thuật toán CRUSH thì có thể tính toán được vị trí của bất kỳ RADOS object nào và tương tác trực tiếp với OSDs .
- Quy trình logic là:

    1. client biết object ID và pool name
    2. client dùng object ID, hash, số lượng PG của pool và pool identity để tính PG ID
    3. client dùng CRUSH để ánh xạ PG đó tới một tập OSD
    4. client chọn primary OSD trong Acting Set để thực hiện thao tác đọc/ghi.

- Ở bản Squid ( 19.2.x) mo otar các bước tính PG rất rõ : 
```
nhập pool name và object ID 
            |
            v
hash object ID 
            |
            v
lấy modulo với số PG của pool để ra PG ID 
            |
            v
dùng pool name để lấy pool ID 
            |
            v
ghép pool ID với PG ID
            |
            v
từ đó dùng CRUSH để liên hệ primary OSD phù hợp. 
```

> Ý nghĩa quan trọng nhất : Vì vị trí các object được tính từ một số đầu vào ổn định trong phiên làm việc , client không cần gửi truy vấn “object X ở đâu?” qua một phiên chatty cho từng thao tác. Do đó việc tính toán vị trí object nhanh hơn nhiều so với việc phải query cluster
### Minh họa luồng tính placement
```
Object ID + Pool Name
        ↓
   Hash Object ID
        ↓
Hash mod PG count → PG ID
        ↓
Pool ID + PG ID
        ↓
CRUSH + OSD Map + CRUSH Map
        ↓
Acting Set
        ↓
Primary OSD
```

## 6. Client flow khi ghi dữ liệu
- Khi client ghi dữ liệu, nó không tự gửi replica tới mọi OSD. Client chỉ kết nối trực tiếp tới primary OSD trong Acting Set của PG tương ứng. Primary OSD trong Acting Set sẽ thay mặt client ghi replicas hoặc erasure-coded chunks tới secondary OSDs trong Acting Set. Đây là điểm rất quan trọng vì nó đơn giản hóa client interface và giảm workload phía client.

- RHCS 8 architecture guide mô tả write path khá rõ:

    - client dùng CRUSH để tính PG ID và primary OSD
    - client gửi object tới primary OSD
    - primary OSD tra replica count hoặc EC policy từ pool/cluster context
    - primary OSD dùng object ID, pool name và cluster map để tính secondary OSDs
    - primary OSD ghi object/chunks tới secondary OSDs
    - khi primary nhận được acknowledgments từ secondaries và chính nó hoàn tất local write, nó mới ack lại thành công cho client.

- Ở mức khái niệm, write path của Ceph vì vậy gồm hai giai đoạn:

    - giai đoạn client-to-primary
    - giai đoạn primary-to-secondaries

Đây là lý do không nên nói đơn giản rằng “client ghi vào pool”. Đúng hơn phải nói: client ghi vào pool thông qua primary OSD của PG được tính ra từ pool/object, còn pool chỉ là entry point logic để xác định policy placement và durability. RHCS 8 architecture guide còn nhấn mạnh rằng pool nhìn từ client như một logical partition có access controls, nhưng vai trò thực của pool trong placement phức tạp hơn và hoàn toàn trong suốt với client.

### Minh họa write flow
```
Client
  ↓
Lấy/đang giữ cluster map
  ↓
Tính PG ID và primary OSD
  ↓
Gửi write tới primary OSD
  ↓
Primary OSD tính secondary OSDs trong Acting Set
  ↓
Primary ghi local + gửi replica/chunk tới secondaries
  ↓
Secondaries ACK
  ↓
Primary ACK lại cho client
```

## 7. Client flow khi đọc dữ liệu
- Đối với đọc dữ liệu, client cũng dùng cluster map và CRUSH để xác định PG và OSD phù hợp.
    Ví dụ nếu object `foo` ban đầu được đặt trên OSD 5, với replicas trên OSD 10 và OSD 15, khi OSD 5 fail và cluster state thay đổi, client đọc `foo` sẽ tự động lấy nó từ OSD 10 như primary mới thông qua librados. Điều này cho thấy client flow không cứng vào một OSD cố định, mà phụ thuộc vào cluster map và placement hiện thời.

- Về logic chung, read path đơn giản hơn write path:

    - client có current map
    - client tính PG
    - client xác định primary OSD của Acting Set hiện tại
    - client đọc trực tiếp từ primary OSD.

> Điểm đáng chú ý là “đọc từ primary” trong các tài liệu architecture được dùng như mô hình mặc định để giải thích consistency và placement, đặc biệt trong replicated pools. Trong một số cơ chế tối ưu đọc hoặc read balancer hiện đại, hành vi phân phối đọc có thể được tối ưu thêm ở tầng vận hành, nhưng đó là chủ đề thuộc file operations hoặc advanced tuning, không phải logic nền tảng của client flow.

### Minh họa read flow
```
Client
  ↓
Có current cluster map
  ↓
Tính PG và Acting Set
  ↓
Xác định primary OSD hiện tại
  ↓
Đọc trực tiếp từ primary OSD
```

## 8. Acting Set, Up Set và tác động lên client flow
- Để hiểu vì sao client có thể “chuyển” từ OSD cũ sang OSD mới khi cluster state thay đổi, cần nắm hai khái niệm: **Acting Set** và **Up Set**. 
    - Acting Set là **tập OSD chịu trách nhiệm cho một PG;** khái niệm này có thể chỉ tập OSD hiện đang chịu trách nhiệm hoặc tập OSD đã từng chịu trách nhiệm ở một epoch cụ thể. 
    - Up Set là **phần “đang up” trong bối cảnh placement hiện tại**, và nó quan trọng vì Ceph có thể remap PG sang OSD khác khi có OSD fail.

- Khi OSD đầu tiên trong Acting Set — tức primary — bị lỗi, một secondary trong Up Set sẽ lên làm primary.  
    ví dụ osd.25, osd.32, osd.61, trong đó nếu osd.25 fail thì osd.32 trở thành primary và osd.25 bị loại khỏi Up Set. 
    > Điều này giải thích trực tiếp vì sao client read/write path trong Ceph là dynamic nhưng có thể tính được.

- Đây cũng là nơi cluster map và client flow nối với peering. Khi map thay đổi, placement logic có thể đổi; nhưng trước khi mọi thứ quay về trạng thái ổn định, các OSD liên quan phải peer để thống nhất về state của PG. 
    => Vì thế, trong thực tế, “client tự tính được vị trí” không có nghĩa “cluster luôn ngay lập tức clean”; nó chỉ có nghĩa là client có mô hình nhất quán để biết primary nào là điểm vào hợp lệ tại thời điểm hiện hành. Squid docs nhấn mạnh thêm rằng *"PGs agree on the state of the cluster do not necessarily have the current data yet"*, đây là chỗ cần phân biệt giữa agreement về state và data đã hoàn toàn clean.

## 9. Cluster map thay đổi thì client flow thay đổi ra sao
- Ceph không xem topology là bất biến. Khi bạn thêm OSD, xóa OSD, mark in/out, hoặc cluster state thay đổi do lỗi, các map liên quan sẽ đổi epoch. Khi đó, CRUSH computation cho placement cũng thay đổi. Nếu cluster map hoặc cluster state thay đổi, phép tính CRUSH cho OSDs lưu trữ các PG cũng thay đổi. Đây là nền tảng của rebalancing và failover placement trong Ceph.

- Khi thêm OSD mới vào cluster, cluster map được cập nhật; vì cluster map là một input của phép tính toán placement, object placement thay đổi theo; một số PGs, chứ không phải tất cả, sẽ migrate sang OSD mới. Docs cũng nhấn mạnh rằng ngay cả khi rebalancing, CRUSH vẫn ổn định theo nghĩa chỉ một phần placement groups bị chuyển đi, còn nhiều PG khác giữ nguyên. Điều này rất quan trọng để hiểu tại sao Ceph có thể mở rộng mà không cần “xáo trộn toàn bộ dữ liệu”.

- Ở góc nhìn client flow, điều này dẫn đến một hệ quả rất đẹp: client không cần học lại một “bảng mới” của từng object. Chỉ cần map mới, cùng object ID và pool name, client sẽ tính ra placement mới. Khi cluster state đổi, client đơn giản yêu cầu map update từ MON rồi tiếp tục hoạt động. RHCS 8 architecture guide nói điều này rất trực diện: *"if the cluster state changes, the client can simply request an update to the cluster map from the Ceph monitor."*

## 10. Data consistency, scrub và ý nghĩa của chúng đối với client flow

- Client flow không kết thúc ở chỗ *“ghi xong là xong”*. Ceph còn cần các cơ chế để đảm bảo dữ liệu trong replicas hoặc shards tiếp tục nhất quán theo thời gian. Squid architecture có một mục riêng về data consistency, trong đó nêu rằng OSDs thực hiện `scrubbing` các object trong placement groups bằng cách so sánh object metadata giữa các replica; `deep scrubbing` còn so sánh dữ liệu bit-for-bit. Đây là một phần quan trọng của data integrity và cũng giải thích vì sao cluster map/PG map không chỉ phục vụ placement mà còn phục vụ việc quan sát trạng thái clean hay không clean của PG.

- Tuy nhiên chúng ta cần phải ghi nhớ

    - cluster map giúp client đi đến đúng primary
    - primary và secondaries phối hợp để duy trì redundancy
    - PG map phản ánh cluster có đang active+clean hay không
    - scrub/deep-scrub là nền kiểm tra tính sạch của dữ liệu, chứ không phải bước bắt buộc trong mỗi I/O của client.

## Các lưu ý qua các phiên bản
- Từ Pacific đến Squid, về bản chất nó không thay đổi mô hình lõi của cluster máp và client flow . Cả 2 đều duy trì các điểm nền sau :
    - MON giữ master copy của cluster map
    - client phải lấy cluster map từ MON trước khi làm I/O
    - client dùng cluster map + CRUSH để tính object location
    - object được ánh xạ qua PG rồi mới tới OSD
    - client kết nối trực tiếp tới primary OSD
    - primary OSD thay mặt client lo phần replication hoặc EC secondary placement.

- Một hiểu lầm rất phổ biến là nghĩ rằng MON “biết object nằm ở đâu” và client phải hỏi MON mỗi lần đọc ghi. Điều này sai. MON giữ master copy của cluster map; còn object location được client/OSD tính bằng CRUSH từ cluster map chứ không phải tra cứu từ MON. Nếu hiểu sai chỗ này, toàn bộ ưu điểm scale-out và direct-to-OSD của Ceph sẽ trở nên mơ hồ.

- Hiểu lầm thứ hai là xem PG map như “map để client định vị object”. Thực ra PG map chủ yếu giúp mô tả trạng thái các placement groups, còn việc tính object → PG → Acting Set cần đến OSD map, CRUSH map và logic tính placement. PG map là phần trạng thái rất quan trọng của cluster, nhưng không phải là “bảng lookup object” dành cho client.

- Hiểu lầm thứ ba là cho rằng client phải tự xử lý replication. RHCS 5 và RHCS 8 architecture guides đều nêu rõ primary OSD trong Acting Set thay mặt client ghi replicas hoặc EC chunks tới secondary OSDs. Điều này là một trong những lý do giao diện client của Ceph tương đối đơn giản so với sự phức tạp bên trong cluster.

> Keynote: Cluster Map không phải là nơi “chứa sẵn vị trí từng object”, mà là tập hợp thông tin để client và daemon tự tính ra vị trí dữ liệu. Đây là khác biệt cực lớn giữa Ceph với nhiều kiến trúc lưu trữ tập trung: MON giữ trạng thái đúng của cụm, nhưng không đứng giữa mọi lần đọc ghi. Nói cách khác, Ceph tách rất rõ giữa nơi giữ sự thật về trạng thái và nơi luồng dữ liệu đi qua. MON giữ sự thật, OSD xử lý dữ liệu, còn client dùng map để đi thẳng tới OSD phù hợp.