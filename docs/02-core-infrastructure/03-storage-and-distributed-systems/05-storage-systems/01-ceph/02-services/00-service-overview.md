# Service Overview

## 1. Ceph cung cấp “dịch vụ” theo nghĩa nào

- Ceph thường được nhìn như một hệ lưu trữ hợp nhất có thể cung cấp **block**, **file** và **object** trong cùng một cụm. Cách nhìn này đúng, nhưng nếu dừng ở đó thì vẫn còn quá bề mặt. Điều quan trọng hơn là: Ceph không xây ba backend lưu trữ tách biệt rồi ghép chúng vào chung một sản phẩm; thay vào đó, Ceph có một lõi lưu trữ thống nhất là **RADOS**, và các “service” như `RBD`, `CephFS` hay `RGW` chỉ là các lớp trình bày và truy cập khác nhau lên cùng một lõi đó. Ceph docs và RHCS Architecture Guides đều nhấn mạnh rằng các client interfaces của Ceph khác nhau ở cách chúng trình bày dữ liệu, nhưng đều dựa trên RADOS để tương tác với cluster.

- Nói cách khác, khi bàn về “services” trong Ceph, ta đang bàn về **các giao diện lưu trữ** chứ không phải **các backend độc lập**. `RBD` trình bày dữ liệu ra ngoài như block device, `CephFS` trình bày ra như filesystem, còn `RGW` trình bày ra như object storage qua S3/Swift-compatible APIs. Nhưng sâu bên dưới, dữ liệu vẫn được lưu trong RADOS dưới dạng object, đi qua pool, placement group và OSD như nhau. Đây là một trong những điểm quan trọng nhất để tránh hiểu sai toàn bộ kiến trúc của Ceph. 

> Ceph không phải “ba hệ lưu trữ khác nhau dùng chung một giao diện quản trị”, mà là **một lõi lưu trữ duy nhất có thể được trình bày ra ngoài bằng ba kiểu giao diện khác nhau**. Vì vậy, khi đánh giá một service của Ceph, luôn phải tách hai câu hỏi: **ứng dụng nhìn thấy gì** và **cluster thật sự lưu gì bên dưới**. Với Ceph, hai câu trả lời đó rất thường không trùng nhau. 

## 2. Bản đồ tổng quát của các service

- Có thể hình dung toàn bộ lớp services của Ceph theo sơ đồ rất ngắn như sau:

```
Ứng dụng / Client
    ↓
RBD  |  CephFS  |  RGW  |  librados
    ↓
RADOS
    ↓
Pools / PGs / CRUSH
    ↓
OSDs
```

- Sơ đồ này phản ánh đúng tinh thần của Ceph docs và RHCS docs: các client interfaces đi vào cluster thông qua pool name, user/secret và cluster map, nhưng dữ liệu cuối cùng vẫn nằm trên cùng một nền RADOS. librados còn là thư viện mức thấp cho phép ứng dụng làm việc trực tiếp với RADOS, nghĩa là ngoài ba service phổ biến nhất, Ceph còn cho phép truy cập thẳng vào lõi object store nếu ứng dụng thực sự cần điều đó.

- Điểm đáng chú ý là ba service chính không chỉ khác nhau ở giao thức bên ngoài, mà còn khác nhau ở kỳ vọng của ứng dụng. Ứng dụng dùng RBD kỳ vọng một block device có thể gắn vào VM hoặc máy chủ. Ứng dụng dùng CephFS kỳ vọng cây thư mục, file, metadata và ngữ nghĩa gần kiểu POSIX. Ứng dụng dùng RGW kỳ vọng bucket, object và API HTTP tương thích S3/Swift. Chính sự khác nhau ở kỳ vọng này khiến mỗi service có một lớp logic riêng ở phía trên RADOS, dù backend lưu trữ vẫn thống nhất.

## 3. RBD: block interface trên object backend

- `RBD` là Ceph Block Device, tức giao diện block storage của Ceph. Ceph docs mô tả RBD là thin-provisioned, resizable, có thể stripe dữ liệu qua nhiều OSD, và tận dụng các khả năng sẵn có của RADOS như snapshotting, replication và strong consistency. RHCS client components cũng diễn giải RBD như một block storage interface cho ứng dụng, máy ảo và các lớp ảo hóa.

- Điểm bản chất của RBD là: ứng dụng nhìn thấy một **ổ đĩa block logic**, nhưng RADOS không lưu một “ổ đĩa nguyên khối” ở tầng lõi. Glossary của Ceph nói rất rõ rằng Ceph Block Device chia dữ liệu block-based thành các **chunks**, và RADOS lưu các chunks đó như các object. Đây là một “điểm vỡ ra” rất quan trọng: block là cách service trình bày dữ liệu cho ứng dụng, còn object mới là cách Ceph thật sự lưu dữ liệu ở tầng lõi.

- Trong thực tế, RBD phù hợp nhất khi bạn cần block storage cho:
    - máy ảo trên OpenStack, KVM hoặc hypervisor khác
    - máy chủ hoặc ứng dụng cần gắn block device
    - workload cần snapshot, clone, resize ở tầng block
    Đây là service gần nhất với cách các nền tảng ảo hóa và điện toán đám mây truyền thống nghĩ về lưu trữ, nên nó thường là giao diện Ceph được dùng nhiều nhất trong môi trường OpenStack.

> RBD không biến Ceph thành “block storage backend theo đúng nghĩa vật lý”; nó chỉ làm cho Ceph trình bày object backend của mình dưới dạng block interface. Nói ngắn gọn: RBD là block interface trên object backend.

## 4. CephFS: file interface trên object backend

- `CephFS` là **distributed file system** của Ceph. Ceph docs mô tả CephFS như một POSIX-compliant file system được xây dựng trên cùng RADOS object store, và nhấn mạnh rằng metadata của filesystem được quản lý bởi một cụm MDS, còn dữ liệu file thực sự vẫn được lưu trong RADOS. Đây là điểm cốt lõi nhất để hiểu CephFS đúng bản chất.

- Điểm làm CephFS khác với RBD là ứng dụng nhìn thấy **file, thư mục và metadata filesystem** thay vì block device. Nhưng điều đó không có nghĩa CephFS có một backend kiểu filesystem hoàn toàn tách khỏi Ceph lõi. CephFS chỉ là cách Ceph dựng một file interface phía trên object store phân tán, với MDS chịu trách nhiệm về metadata và state của cây thư mục, còn dữ liệu file vẫn đổ xuống RADOS.

- CephFS phù hợp khi bạn cần:
    - không gian file dùng chung cho nhiều client
    - semantics gần kiểu POSIX
    - ứng dụng, pipeline hoặc môi trường cần mount filesystem thay vì dùng block hay object API
    => Nó đặc biệt có ý nghĩa khi ứng dụng thực sự cần khái niệm file, thư mục, quyền truy cập, duyệt cây thư mục và thao tác metadata phong phú.

> CephFS không làm cho dữ liệu “thôi không còn là object nữa”. Nó chỉ làm cho người dùng và ứng dụng thấy dữ liệu dưới dạng file, trong khi backend lõi vẫn là object store. Nói ngắn gọn: CephFS là file interface trên object backend.

## 5. RGW: object interface gần nhất với bản chất RADOS
- `RGW` là RADOS Gateway hay Ceph Object Gateway, tức lớp cung cấp object storage service qua các API tương thích S3 và Swift. RHCS client components mô tả gateway này như một object storage service với RESTful interfaces và cơ chế quản lý user riêng của nó. Đây là điểm khiến RGW khác với RBD và CephFS ở mặt giao tiếp bên ngoài: nó đã là object ngay từ phía ứng dụng.

- Vì object interface của RGW gần với bản chất object store của RADOS nhất, RGW thường là service dễ hiểu nhất nếu chỉ nhìn theo trục “giao diện ngoài và backend trong”. Dù vậy, vẫn cần nhớ rằng object mà người dùng nhìn thấy ở tầng S3/Swift không nên bị đồng nhất hoàn toàn một cách máy móc với object nội bộ của RADOS ở mọi lớp triển khai. Điều đúng hơn là: RGW là service gần nhất về mặt mô hình với lõi RADOS, nên nó ít tạo cảm giác “dịch một loại lưu trữ sang loại khác” hơn RBD hoặc CephFS.

- RGW phù hợp khi bạn cần:

    - object storage qua HTTP API
    - bucket, object, access key/secret key
    - dịch vụ lưu trữ kiểu S3/Swift cho ứng dụng, backup, archive, hoặc data platform
    Nó đặc biệt tự nhiên trong các bài toán lưu trữ ứng dụng web, backup object-based, hoặc tích hợp với các công cụ đã nói S3.

> Nếu RBD và CephFS là hai cách “dịch” object backend thành block và file, thì RGW là lớp giao diện ít phải dịch nhất, vì cả bên ngoài lẫn bên dưới đều xoay quanh mô hình object. Nói ngắn gọn: RGW là object interface trên object backend.

## 6. librados: lớp truy cập trực tiếp vào lõi

- Ngoài ba service phổ biến nhất, Ceph còn có `librados`, là thư viện mức thấp để ứng dụng truy cập trực tiếp vào RADOS. Tài liệu `librados` của Ceph nói rõ đây là **low-level library cho phép ứng dụng xây giao diện riêng tới Ceph Storage Cluster**. Điều này rất đáng chú ý vì nó cho thấy Ceph không khóa người dùng vào RBD, CephFS hay RGW; về nguyên tắc, ứng dụng có thể nói trực tiếp với lõi object store nếu cần mức kiểm soát thấp hơn.

- Tuy nhiên, librados không phải lựa chọn mặc định cho đa số hệ thống ứng dụng thông thường. Nó phù hợp hơn khi bạn đang xây:

    - một ứng dụng tùy biến làm việc trực tiếp với object semantics
    - một lớp truy cập chuyên biệt không trùng hoàn toàn với RBD, CephFS hay RGW
    - một thành phần hạ tầng cần làm việc ở mức thấp với cluster
> RBD, CephFS và RGW là các lựa chọn tiện dụng, nhưng không phải là lớp lõi duy nhất có thể dùng để tương tác với Ceph.

## 8. Chọn service nào: đừng bắt đầu từ “Ceph có gì”, hãy bắt đầu từ “ứng dụng cần gì”

- Cách chọn service đúng không phải là nhìn từ phía Ceph trước, mà phải nhìn từ phía ứng dụng hoặc nền tảng sử dụng trước. Nếu ứng dụng cần block semantics, muốn gắn volume như ổ đĩa và để filesystem/OS phía trên tự quyết, thì RBD là lựa chọn tự nhiên hơn. Nếu ứng dụng cần file semantics, cần thư mục, inode, metadata và nhiều client cùng truy cập một không gian file chung, thì CephFS phù hợp hơn. Nếu ứng dụng hoặc hệ sinh thái của bạn đã nói ngôn ngữ S3/Swift, thì RGW là lựa chọn đúng hơn về mặt giao diện và mô hình sử dụng.

- Điểm này nghe có vẻ hiển nhiên, nhưng rất quan trọng vì nó giúp tránh một sai lầm phổ biến: **chọn service theo cảm giác “cái nào hiện đại hơn” hoặc “cái nào backend tiết kiệm hơn” thay vì theo mô hình truy cập thực sự của ứng dụng**. Trong Ceph, **lõi lưu trữ có thể thống nhất, nhưng semantics bên ngoài của block, file và object vẫn khác nhau đủ nhiều để quyết định đúng service ngay từ đầu** có giá trị rất lớn.

- Một cách chọn rất ngắn
    - Cần **ổ đĩa** → nghĩ tới `RBD`
    - Cần **thư mục** và **file** → nghĩ tới `CephFS`
    - Cần **bucket** và **HTTP object API** → nghĩ tới `RGW`
    - Cần **truy cập trực tiếp object store ở mức thấp** → nghĩ tới `librados`

## Tổng kết 
- Lớp services của Ceph là lớp biến một lõi lưu trữ object phân tán thành nhiều kiểu trải nghiệm lưu trữ khác nhau cho ứng dụng. RBD biến Ceph thành block interface, CephFS biến Ceph thành file interface, RGW biến Ceph thành object service qua HTTP APIs, và librados cho phép đi thẳng vào lõi khi cần. Nhưng dù nhìn từ service nào, Ceph vẫn giữ một bản chất rất nhất quán: backend thật của nó là RADOS object store.
> Ceph có nhiều service, nhưng chỉ có một lõi lưu trữ; khác nhau nằm ở giao diện và semantics, không nằm ở việc mỗi service có một backend riêng.

- Các lưu ý cốt lõi :
    - Ceph cung cấp object, block và file trong một hệ thống thống nhất
    - các service khác nhau chủ yếu ở giao diện và semantics bên ngoài
    - backend lõi vẫn là RADOS
    - client interfaces cần cluster identity, monitor address, pool name và thông tin xác thực để làm việc với cluster.
### Những hiểu lầm phổ biến về services của Ceph

- Hiểu lầm phổ biến nhất là cho rằng Ceph có “ba loại backend lưu trữ”: block backend, file backend và object backend. Cách hiểu này sai ở tầng kiến trúc. Ceph chỉ có một lõi lưu trữ thống nhất là RADOS object store; sự khác nhau của RBD, CephFS và RGW nằm chủ yếu ở giao diện, ngữ nghĩa truy cập và lớp logic phía trên, không nằm ở việc mỗi service có một backend hoàn toàn riêng biệt.

- Hiểu lầm thứ hai là nghĩ rằng CephFS hay RBD “không còn là object” ở tầng lõi vì ứng dụng nhìn thấy file hoặc block. Thực tế, chính đây là điểm mạnh của Ceph: nó có thể trình bày object backend ra thành nhiều kiểu giao diện khác nhau. Block và file là cách ứng dụng nhìn thấy dữ liệu; object là cách Ceph thật sự tổ chức dữ liệu ở tầng nền.

- Hiểu lầm thứ ba là nghĩ RGW chỉ là “một cổng web ở phía trước Ceph”. Dù đúng là RGW là gateway theo nghĩa giao diện HTTP, nó không chỉ là reverse proxy đơn thuần, mà là lớp object service với mô hình user, bucket và API compatibility riêng của nó. Điều này khiến RGW trở thành một service thực sự, không phải chỉ là một adapter mỏng.