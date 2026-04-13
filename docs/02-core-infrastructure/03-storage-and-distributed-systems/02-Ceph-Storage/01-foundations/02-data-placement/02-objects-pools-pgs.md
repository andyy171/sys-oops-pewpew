# Objects, Pools và Placement Groups (PGs)

## 1. Vì sao ba khái niệm này phải đi cùng nhau

- Trong Ceph, `object`, `pool` và `placement group (PG)` không phải ba khái niệm rời rạc, mà là ba tầng liên tiếp của cùng một đường đi dữ liệu. Dữ liệu ở tầng lõi của Ceph luôn được quản lý dưới dạng **object**; các object luôn thuộc về một **pool**; và trước khi được đặt lên các `OSD`, các object sẽ được gom logic qua **PG**. Ceph Architecture và các tài liệu về Placement Groups đều mô tả đúng chuỗi này: client ghi object vào pool, object được ánh xạ vào PG, rồi PG được ánh xạ tới tập `OSD` thông qua `CRUSH`. 

- Điểm quan trọng nhất cần nhớ là ba khái niệm này nằm ở **ba tầng khác nhau**. `Object` là đơn vị dữ liệu nền tảng. `Pool` là đơn vị chính sách và tách biệt logic. `PG` là đơn vị phân phối và quản trị nội bộ mà Ceph dùng để làm cho placement, recovery và rebalancing có thể mở rộng ở quy mô lớn. Nếu không tách rõ ba tầng này, người học rất dễ rơi vào kiểu hiểu sai như “pool là nơi dữ liệu thật nằm”, hay “PG là object lớn hơn”, trong khi bản chất của chúng hoàn toàn khác nhau.

> Ceph không lưu “block”, “file” hay “bucket item” như cách ứng dụng nhìn thấy ở tầng ngoài. Ở tầng lõi, Ceph luôn quay về object. Nhưng Ceph cũng không đi quản lý trực tiếp từng object theo cách riêng lẻ ở quy mô lớn; nó cần `PG` làm lớp trung gian để việc placement và self-healing còn khả thi. Vì vậy, nếu phải nhớ thật ngắn, hãy nhớ chuỗi này: **object là dữ liệu, pool là chính sách, PG là đơn vị quản trị nội bộ**. 

## 2. Object: đơn vị dữ liệu nền tảng của RADOS

- Trong RADOS, object là đơn vị lưu trữ cơ bản. Ceph Architecture mô tả một `RADOS object` gồm ba phần chính: một định danh duy nhất, dữ liệu nhị phân và metadata đi kèm dưới dạng cặp tên/giá trị. Các object này tồn tại trong một **không gian tên phẳng**, nghĩa là ở tầng lõi không có cấu trúc thư mục kiểu filesystem truyền thống. Đây là điểm rất quan trọng, vì nó cho thấy Ceph không xây storage backend của mình trên khái niệm “file trong cây thư mục”, mà trên khái niệm “object trong namespace phẳng”. 

- Từ góc nhìn của ứng dụng, object có thể bị ẩn đi. Với `RBD`, người dùng thấy một block device. Với `CephFS`, người dùng thấy file và thư mục. Với `RGW`, người dùng thấy object S3/Swift. Nhưng ở tầng RADOS, dữ liệu cuối cùng vẫn được biểu diễn thành object. Đây là một trong những “điểm vỡ ra” quan trọng nhất khi học Ceph: **thứ ứng dụng nhìn thấy không nhất thiết là thứ Ceph thực sự lưu ở tầng lõi**.

## 3. Pool: phân vùng logic và đơn vị chính sách

- Ceph docs định nghĩa `pool` là **phân vùng logic** dùng để lưu `RADOS objects`. Tài liệu Pools của Ceph và RHCS 8 Architecture Guide đều nói rất rõ rằng cluster lưu data objects trong các logical partitions gọi là pools. Người quản trị có thể tạo nhiều pool cho nhiều loại dữ liệu khác nhau, ví dụ pool cho block devices, pool cho object gateway, hay pool để tách các nhóm người dùng hoặc workload.
- Nhưng nếu chỉ dừng ở câu *“pool là vùng logic chứa object”* thì vẫn còn quá nông. Pool không chỉ dùng để “gom object cho gọn”, mà còn là nơi xác định một số chính sách nền tảng của dữ liệu. Ceph Architecture nêu rằng client ghi `RADOS objects` vào pools, và cách Ceph đặt dữ liệu trong pool được quyết định bởi `size` hoặc số replica, `CRUSH rule`, và số lượng `PG` của pool. Tài liệu Pools của Ceph còn nêu thêm rằng pool cung cấp khả năng lập kế hoạch chịu lỗi song song, đặt quota, nén dữ liệu, và ánh xạ đến các OSD cụ thể qua CRUSH. Nói cách khác, pool là **điểm mà chính sách durability, placement và quản trị bắt đầu bám vào dữ liệu**. 
### Pool thường quyết định những gì

- dữ liệu đó thuộc workload hoặc nhóm người dùng nào  
- dữ liệu dùng **replicated** hay **erasure-coded** policy  
- dữ liệu đi theo `CRUSH rule` nào  
- dữ liệu có bao nhiêu `PG`  
- dữ liệu có quota hoặc thuộc tính riêng gì ở cấp pool hay không 

**Ghi chú cốt lõi:**  
Pool không phải là “nơi dữ liệu thật nằm”, mà là **nơi Ceph gắn chính sách lên dữ liệu**. Nếu object là câu trả lời cho câu hỏi “dữ liệu thực sự là gì”, thì pool là câu trả lời cho câu hỏi “dữ liệu này phải được đối xử như thế nào”. Đây là một khác biệt rất quan trọng: object là **dữ liệu**, còn pool là **chính sách**. 

## 4. Placement Group (PG): lớp trung gian bắt buộc của Ceph

Ceph docs về Placement Groups nói rất thẳng rằng `PG` là tập con của mỗi pool logic, và Ceph quản lý dữ liệu nội bộ ở **granularity của PG** vì làm như vậy mở rộng tốt hơn so với quản lý từng `RADOS object` riêng lẻ. Lý do là việc theo dõi placement của từng object một là quá tốn kém về tính toán ở quy mô lớn; một hệ có hàng triệu hoặc hàng tỷ object không thể thực tế vận hành nếu mọi placement, peering, recovery và metadata tracking đều phải chạy ở mức từng object riêng biệt.

PG vì vậy là **lớp trung gian bắt buộc** giữa object và OSD. Object không đi thẳng tới OSD. Thay vào đó, object được ánh xạ vào một PG, rồi PG mới được ánh xạ tới một tập `OSD`. Tài liệu Architecture của Reef/Squid diễn giải chuỗi này rất rõ: client chia dữ liệu thành object, rồi `CRUSH` ánh xạ object tới PG, và PG tới `OSD Daemons`. Ceph docs mới còn nhấn mạnh rằng Ceph manages data internally at placement-group granularity.

Điều này có hậu quả kiến trúc rất lớn. Khi cluster rebalance, recover hoặc peer sau lỗi, Ceph không làm việc “theo từng object lẻ” theo cách người học thường hình dung, mà làm việc thông qua PG. Đây là lý do tại sao các khái niệm như `active`, `clean`, `degraded`, `peering`, `backfill`, `recovery` đều gắn mạnh với PG hơn là với object riêng lẻ. 

**Ghi chú cốt lõi:**  
Nếu phải chọn một ý quan trọng nhất của cả file này, thì đó là: **Ceph không quản lý dữ liệu ở mức từng object riêng lẻ khi vận hành cluster, mà ở mức PG**. Đây là chìa khóa để hiểu vì sao Ceph có thể scale, vì sao recovery không đòi hỏi một metadata table khổng lồ theo từng object, và vì sao các trạng thái sức khỏe của dữ liệu lại luôn được diễn đạt bằng PG. 

## 5. Chuỗi quan hệ: object → pool → PG → OSD

Có thể hình dung luồng logic cơ bản của RADOS như sau. Client tạo hoặc ghi dữ liệu. Dữ liệu đó được biểu diễn thành object. Mỗi object thuộc về một pool cụ thể. Từ object và thông tin của pool, Ceph tính ra PG tương ứng. Sau đó `CRUSH` dùng PG cùng `CRUSH map`, `OSD map` và policy của pool để tính ra tập OSD chịu trách nhiệm lưu dữ liệu đó. Đây là chuỗi nền mà cả Ceph docs lẫn RHCS docs đều lặp đi lặp lại khi giải thích placement. 

### Minh họa luồng placement cơ bản

```text id="n0e4n4"
Client
  ↓
Object
  ↓
Pool
  ↓
Placement Group (PG)
  ↓
CRUSH
  ↓
Primary OSD + Replica / Shard OSDs
```


> Ceph Architecture còn nhấn mạnh một điểm tinh tế nhưng rất quan trọng: vì client ghi vào một pool cụ thể, nên toàn bộ data đã được chia thành object trong thao tác đó sẽ được ánh xạ vào các PG thuộc cùng pool đó, và vì vậy dùng cùng CRUSH map và cùng quyền truy cập. Điều này giúp pool trở thành ranh giới rất tự nhiên cho chính sách placement và truy cập.

## 6. Vì sao Ceph không thể bỏ PG

- Về mặt lý thuyết, người ta có thể tưởng tượng một hệ object store phân tán nơi mỗi object tự ánh xạ trực tiếp tới OSD mà không cần lớp trung gian. Nhưng Ceph docs nói rất rõ rằng cách làm đó không thực tế ở quy mô lớn vì tracking placement và metadata theo từng object là quá tốn kém. PG chính là cách Ceph đưa vào một lớp gom nhóm đủ lớn để giảm chi phí quản trị nội bộ, nhưng vẫn đủ nhỏ để cluster có thể rebalance và recover linh hoạt.

- PG vì thế không phải một “chi tiết phụ” của Ceph, mà là một quyết định kiến trúc nền tảng. Nếu không có PG, Ceph sẽ phải chọn giữa:

    - hoặc quản lý placement theo từng object với chi phí khổng lồ
    - hoặc gom dữ liệu quá thô, làm mất cân bằng và mất khả năng recovery linh hoạt

PG là điểm cân bằng giữa hai cực đó. Đây là lý do mọi giải thích tốt về Ceph cuối cùng đều phải quay lại PG, dù lúc đầu người học thường chỉ chú ý tới object, pool hay OSD.

## 7. PG là logic, OSD là vật lý
- Một nhầm lẫn rất thường gặp là xem PG như một “thư mục thật trên đĩa” hoặc một “vùng vật lý” cố định. Cách hiểu này không đúng. PG là đơn vị logic nội bộ mà Ceph dùng để quản lý placement và trạng thái dữ liệu. OSD mới là nơi gắn với thiết bị lưu trữ vật lý và là nơi object data thực sự được lưu thông qua backend như BlueStore. PG nằm ở giữa: nó không phải dữ liệu thô, cũng không phải đĩa vật lý, mà là lớp tổ chức nội bộ của RADOS.

> Đây là một cặp phân biệt rất đáng nhớ:
>> - object là đơn vị dữ liệu 
>> - PG là đơn vị tổ chức logic 
>> - OSD là đơn vị thực thi lưu trữ trên hạ tầng thật


## 8. Pool và khả năng chịu lỗi

- Tài liệu Pools của Ceph nói rằng pool cung cấp resilience: nếu cluster dùng replicated pools, **số OSD có thể hỏng song song mà không mất dữ liệu là ít hơn một đơn vị so với số lượng replicas**; còn số OSD có thể hỏng mà dữ liệu chưa trở nên không truy cập được thường là hai trong một số cấu hình điển hình. Dù công thức chính xác còn phụ thuộc vào topology và failure domain, ý chính ở đây là **pool là nơi gắn durability policy với dữ liệu. Pool không chỉ “chứa object”, mà còn quyết định cluster sẽ chịu lỗi ra sao đối với nhóm object đó.**

- Đây là một lý do nữa khiến không thể xem pool như thư mục hay namespace đơn giản. Pool là nơi cluster gắn các quyết định như replicated hay erasure-coded, số replica, CRUSH rule, quota, và từ đó quyết định dữ liệu trong pool được bảo vệ như thế nào. Trong bức tranh kiến trúc, pool là đơn vị chính sách bền vững dữ liệu, không phải chỉ đơn vị phân loại dữ liệu.

## 9. Số lượng PG và vì sao đây là bài toán cân bằng

- Ceph docs Pacific và các tài liệu Red Hat đều nói rất rõ rằng **số lượng PG có ảnh hưởng trực tiếp tới khả năng cân bằng và chi phí vận hành của cluster**. **Ít PG quá thì placement kém mịn, dữ liệu phân bố không đều và khi thêm OSD mới cluster khó chia tải đẹp. Nhiều PG quá thì OSD phải quản lý quá nhiều trạng thái, peering lâu hơn, tiêu tốn nhiều bộ nhớ và CPU hơn.** Ceph docs cho ví dụ rằng một cluster với số PG lớn hơn thường được cân bằng tốt hơn, nhưng cũng nhấn mạnh rằng PGs are computationally expensive.

- Trong các tài liệu cũ hơn hoặc ở Pacific, người đọc thường gặp mốc kinh nghiệm khoảng 100 PG trên mỗi OSD như một cấu hình điển hình. Ở tài liệu Ceph mới hơn, **autoscaler thường nhắm tới xấp xỉ 150 PG trên mỗi OSD trong cấu hình thông thường**. Điều này không phải thay đổi kiến trúc, mà là sự trưởng thành dần của khuyến nghị vận hành và của cơ chế tự điều chỉnh. Điều quan trọng hơn con số chính xác là phải hiểu bản chất: PG là tài nguyên logic có giá thành, nên số lượng PG luôn là bài toán cân bằng giữa độ mịn của placement và chi phí quản trị của OSD.

## 10. PG autoscaler và điều cần hiểu đúng

- Tài liệu Red Hat về placement groups cho biết từ RHCS 5 trở đi, pg_autoscale_mode mặc định là on cho các pool mới; các cluster nâng cấp thì giữ nguyên cấu hình cũ. Điều đó nghĩa là trong Ceph hiện đại, người quản trị không nên học PG chỉ như “một con số phải tự tay tính theo công thức rồi cố định mãi mãi”, mà phải hiểu thêm rằng cluster có thể tự điều chỉnh số lượng PG theo cách sử dụng thực tế của pool.

- Tuy vậy, autoscaler không làm cho kiến thức về PG trở nên không cần thiết. Trái lại, nó làm cho việc hiểu đúng PG còn quan trọng hơn: bạn phải biết **autoscaler đang điều chỉnh đơn vị gì, vì sao nó điều chỉnh, và vì sao việc điều chỉnh đó có thể khiến cluster tạm thời vào trạng thái recovering hoặc phải dịch chuyển placement**. Nói cách khác, autoscaler không thay thế hiểu biết; nó **chỉ thay thế một phần thao tác thủ công**.

## 11. Object, pool và PG nhìn từ ba giao diện của Ceph

- Một trong những quan trọng nhất là nhận ra cả ba giao diện lớn của Ceph đều quay về object/pool/PG ở tầng lõi.

    - Với RBD, thứ người dùng nhìn thấy là block device, nhưng backend thật vẫn là object trong pool và PG.
    - Với CephFS, người dùng nhìn thấy file và thư mục, nhưng dữ liệu file vẫn đi xuống RADOS object store.
    - Với RGW, giao diện ngoài đã là object storage, nên nó gần với bản chất lõi hơn, nhưng vẫn đi qua pool và PG như các workload khác.

## Kết luận 
- Các kiến thức cần ghi nhớ :
    - object là đơn vị dữ liệu lõi
    - pool là phân vùng logic chứa object
    - PG là tập con của pool và là đơn vị placement nội bộ
    - Ceph quản lý dữ liệu ở granularity của PG thay vì theo từng object riêng lẻ
    - object → PG → OSD là chuỗi placement cơ bản của cluster.

- Object, pool và PG là ba bậc thang liên tiếp trong mô hình dữ liệu của Ceph. Object là dữ liệu thật ở tầng lõi. Pool là nơi Ceph gắn chính sách lên nhóm dữ liệu đó. PG là lớp trung gian giúp Ceph quản lý placement, recovery và self-healing ở quy mô lớn mà không phải theo dõi từng object một cách riêng lẻ. Hiểu rõ ba tầng này là một trong những mốc quan trọng nhất để chuyển từ “biết dùng Ceph” sang “hiểu Ceph hoạt động như thế nào”.

> Object là dữ liệu, pool là chính sách, PG là đơn vị quản trị nội bộ mà Ceph dùng để đưa dữ liệu tới OSD.
### Những hiểu lầm phổ biến

- Hiểu lầm phổ biến nhất là nghĩ rằng pool chỉ là “một cái container chứa object”. Cách hiểu này thiếu phần quan trọng nhất: pool là nơi Ceph gắn chính sách lên dữ liệu, bao gồm durability, placement và nhiều thuộc tính quản trị khác. Nếu quên điều đó, người học sẽ khó hiểu vì sao chỉ đổi pool mà hành vi của dữ liệu có thể thay đổi mạnh đến vậy.

- Hiểu lầm thứ hai là nghĩ rằng PG là một “object lớn hơn” hoặc một “thư mục vật lý trên đĩa”. Điều đó sai. PG là đơn vị logic nội bộ để Ceph quản lý placement, peering, recovery và balance ở quy mô lớn. Nó không phải là dữ liệu ứng dụng nhìn thấy, cũng không phải là block vật lý.

- Hiểu lầm thứ ba là cho rằng dữ liệu block của RBD hay file của CephFS ở tầng lõi không còn là object nữa. Thực tế, chính đây là bản chất quan trọng nhất của Ceph: dù giao diện ngoài là block hay file, backend lõi vẫn là object store phân tán. 