# Core Concepts
## 1. Librados là gì và vì sao nó quan trọng
1.1 Librados là cổng vào mức thấp của RADOS

librados là thư viện cung cấp truy cập mức thấp vào dịch vụ RADOS. Tài liệu chính thức của Ceph mô tả rất rõ: librados là lớp cho phép client kết nối tới cluster và thực hiện các thao tác trực tiếp với object, pool và các chức năng cốt lõi của RADOS. Nói ngắn gọn, nếu RBD là block interface, CephFS là file interface, còn RGW là object service qua HTTP, thì librados là con đường đi thẳng vào lõi object store của Ceph.

Điểm quan trọng nhất cần giữ trong đầu là: librados không phải “một client phụ ít ai dùng”, mà là lớp nền chung cho cách client nói chuyện với Ceph. Khi hiểu librados, bạn sẽ hiểu vì sao nhiều service khác nhau của Ceph tuy nhìn rất khác ở bề mặt nhưng vẫn gặp nhau ở cùng một lõi truy cập dữ liệu. Đây là mảnh ghép nối giữa phần foundations, RADOS và các service như RBD, RGW, CephFS.

> librados không phải “một tính năng riêng”, mà là ngôn ngữ chung ở tầng thấp để client làm việc với Ceph. Muốn hiểu Ceph thật sự hoạt động từ phía client ra sao, gần như không thể bỏ qua lớp này.

### 1.2 Vì sao mọi client Ceph đều quay về cùng một lõi truy cập

- Tài liệu API của Ceph nói rất rõ: mọi Ceph client hoặc dùng trực tiếp `librados`, hoặc dùng cùng chức năng đã được gói lại trong `librados` để tương tác với object store. Ví dụ, librbd và libcephfs đều dựa trên lớp chức năng này. Red Hat cũng mô tả cùng một ý: các Ceph client khác nhau ở cách trình bày giao diện lưu trữ, nhưng cuối cùng đều dùng giao thức RADOS để tương tác với cluster.

- Đây là lý do khi học Ceph theo hệ thống, không nên nghĩ RBD, RGW, CephFS là ba con đường hoàn toàn tách biệt. Chúng khác nhau ở block, object service hay file semantics, nhưng khi xuống đủ sâu, chúng lại gặp nhau ở client path tới RADOS. Vì vậy, `librados` là nơi giúp bạn nhìn ra phần “ruột chung” của toàn bộ hệ thống client của Ceph.

### 1.3 Vì sao librados quan trọng dù người vận hành ít dùng trực tiếp

Trong thực tế, nhiều người vận hành sẽ hiếm khi tự viết ứng dụng dùng `librados` trực tiếp. Họ thường gặp Ceph qua rbd, cephfs, radosgw, QEMU, OpenStack hay các công cụ sẵn có. Nhưng điều đó không làm `librados` kém quan trọng. Ngược lại, chính vì nhiều lớp cao hơn che đi chi tiết bên dưới, nên khi xảy ra lỗi khó hoặc cần hiểu thật sâu đường đi của dữ liệu, bạn lại phải quay về logic của `librados`: client lấy cluster map ra sao, object được chọn placement thế nào, auth và caps đứng ở đâu, và vì sao client không cần hỏi một máy chủ trung tâm để biết object đang nằm ở OSD nào.

## 2. Client của Ceph thật sự nói chuyện với cluster như thế nào
### 2.1 Client bắt đầu bằng việc lấy cluster map từ MON

- Red Hat Ceph Storage Architecture Guide mô tả rất rõ luồng nền: client trước hết truy cập MON để lấy bản sao mới nhất của cluster map. Sau đó client đưa vào librados hai thông tin chính là tên object và tên pool; từ đó librados tính ra PG và primary OSD của object bằng thuật toán CRUSH.

- Đây là điểm cực kỳ quan trọng. MON không phải nơi mọi dữ liệu đọc ghi đều phải đi qua. MON chủ yếu giữ bản đồ của cluster và làm phần điều khiển. Sau khi đã có map đúng, client đi tiếp xuống các OSD thích hợp. Điều này giải thích vì sao Ceph có thể mở rộng tốt mà không cần một máy tra cứu trung tâm cho mọi thao tác dữ liệu.

### 2.2 Client không cần bảng tra cứu object-to-OSD tập trung

- Một trong những ý đẹp nhất của kiến trúc Ceph là client không phải giữ bảng object-to-OSD và cũng không phải gọi một dịch vụ chỉ mục trung tâm để hỏi object đang nằm ở đâu. Red Hat mô tả điều này rất rõ: client giữ object ID và pool name, lấy cluster map từ MON, rồi librados dùng CRUSH để tự tính placement.

=> Ý nghĩa của chuyện này rất lớn: Ceph tránh được nút nghẽn ở tầng tra cứu vị trí dữ liệu. Muốn hiểu vì sao Ceph khác với nhiều hệ thống lưu trữ tập trung, đây là một trong những điểm phải nắm thật chắc. Client biết object gì và pool nào; còn chuyện object được đặt vào PG nào và OSD nào là việc librados cùng CRUSH xử lý từ cluster map.

### 2.3 Data path đi thẳng từ client tới OSD

- Tài liệu Red Hat ghi rất trực tiếp rằng sau khi librados tính ra primary OSD, client kết nối thẳng tới primary OSD để thực hiện đọc và ghi, và không có máy chủ trung gian, broker hay bus nào nằm giữa client và OSD. Ceph documentation cũng nhấn mạnh việc Ceph loại bỏ cổng trung tâm để client có thể làm việc trực tiếp với OSD daemons.

- Đây là chỗ rất dễ bị hiểu sai nếu chỉ nhìn bề ngoài. Nhiều người mới học thường nghĩ MON giống “server trung tâm” của Ceph. Điều này không đúng ở data path. MON rất quan trọng, nhưng vai trò chính là giữ cluster map và trạng thái điều khiển. Luồng dữ liệu thật sự lại đi từ client tới OSD sau khi client đã có map đúng.

> Trong Ceph, đường điều khiển và đường dữ liệu phải được tách thật rõ. Client hỏi MON để biết bản đồ, nhưng client ghi và đọc dữ liệu với OSD. Nếu không tách được hai đường này, gần như mọi phần sau của Ceph đều rất dễ bị hiểu sai.

### 2.4 Vì sao điều này làm Ceph khác nhiều hệ thống lưu trữ khác

- Khi client có thể tự tính placement từ map và nói chuyện trực tiếp với OSD, cluster sẽ bớt lệ thuộc vào một thành phần tra cứu tập trung ở data path. Điều này làm Ceph mở rộng tốt hơn và cũng giải thích vì sao các client của Ceph “thông minh” hơn mức người mới thường nghĩ. Chúng không chỉ gửi yêu cầu đến một server rồi chờ server đó quyết định mọi thứ; chúng tự dùng map và CRUSH để tham gia vào việc tìm đường tới dữ liệu.

## 3. CephX, keyring và caps đứng ở đâu
### 3.1 Client user trong Ceph là gì

- Ceph client users là các cá nhân hoặc tác nhân hệ thống, ví dụ ứng dụng, sử dụng Ceph clients để tương tác với cluster. Những user này không phải user Linux thường, mà là danh tính ở tầng cluster, dùng để xác thực và phân quyền khi client nói chuyện với Ceph.

> Lưu ý : Các loại danh tính. client.admin, client.cinder, client.glance, client.libvirt hay một direct librados application đều là cluster client users theo nghĩa của CephX. Chúng tồn tại để xác định “ai đang nói chuyện với cluster” và “được phép làm gì”.

### 3.2 CephX là cơ chế xác thực và phân quyền của cluster

- Ceph sử dụng CephX để xác thực user và daemon, đồng thời bảo vệ khỏi các kiểu tấn công sửa đổi thông điệp ở giữa đường truyền. Tài liệu CephX Config Reference nói rõ nếu tắt xác thực thì bạn có nguy cơ bị tấn công kiểu man-in-the-middle làm thay đổi thông điệp client/server với hậu quả rất nghiêm trọng. Tài liệu kiến trúc cũ của Ceph cũng mô tả CephX là hệ thống dùng để nhận diện user và daemon trong cluster.

- Điểm phải hiểu đúng là: CephX không chỉ là “một mật khẩu để đăng nhập”. Nó là cơ chế xác thực và phân quyền của toàn cluster. Vì vậy, khi một client librados kết nối được hay không, đọc được pool này hay ghi được object kia, phần lớn câu trả lời nằm ở CephX user, secret key và caps của user đó.

### 3.3 Caps là gì và vì sao chúng quan trọng

- Trong Ceph, caps là tập quyền gắn cho client user, quy định user được làm gì với MON, OSD, MGR, MDS hoặc các phần khác của cluster. Tài liệu User Management của Ceph còn liệt kê sẵn một số profile, ví dụ profile simple-rados-client được mô tả là dành cho các ứng dụng direct librados client, với quyền đọc dữ liệu monitor, OSD và PG ở mức phù hợp.

- Đây là điểm rất thực tế: một direct librados application thường không nên chạy bằng client.admin. Nó nên có user riêng với caps tối thiểu cần thiết. Nếu không hiểu caps, rất dễ rơi vào hai thái cực: hoặc cấp quá rộng gây nguy hiểm, hoặc cấp quá hẹp khiến ứng dụng lỗi mà không hiểu vì sao.

### 3.4 Keyring và file cấu hình đứng ở đâu trong bức tranh

- Để client kết nối vào cluster, thông thường bạn cần tối thiểu:

    - định danh cluster hoặc file cấu hình đủ để biết MON ở đâu
    - user name
    - secret key, thường được giữ trong keyring hoặc file tương đương

- Red Hat Architecture mô tả client cần object IDs, pool name, user name và đường dẫn tới secret key để làm việc với cluster. Điều này cho thấy keyring không phải “một file phụ tiện lợi”, mà là một phần thực thi rất cụ thể của CephX ở phía client.

> Nếu librados là cách client nói chuyện với Ceph, thì CephX + keyring + caps là cách cluster trả lời câu hỏi “anh là ai và anh được phép làm gì”. Hai lớp này luôn đi cùng nhau.

## 4. Các loại client và các con đường truy cập khác nhau
### 4.1 Direct librados client là gì

- Direct librados client là ứng dụng dùng thẳng thư viện librados để đọc ghi object, thao tác pool và làm việc trực tiếp với RADOS. Tài liệu Librados (C) và Librados (Python) của Ceph đều đưa ví dụ kết nối cluster, mở context tới pool và thao tác object trực tiếp. Đây là kiểu client gần lõi nhất vì nó cho bạn cái nhìn ít bị che chắn nhất về Ceph: pool, object, namespace, async I/O, notify/watch, và các thao tác trực tiếp ở tầng object. Nó cũng giúp giải thích vì sao nhiều dịch vụ khác của Ceph chỉ là các lớp cao hơn dựng trên cùng một nền.

### 4.2 `librbd` và `libcephfs` khác direct librados ra sao

- `librbd` và `libcephfs` không phải thư viện “không liên quan” đến librados. Tài liệu API của Ceph nói rõ chúng sử dụng cùng chức năng đã được gói trong librados để tương tác với object store. Khác biệt nằm ở chỗ:

    - `librados` cho bạn object interface trực tiếp
    - `librbd` dựng block semantics lên trên
    - `libcephfs` dựng file semantics lên trên

> Đây là chỗ rất đáng nhớ vì nó làm sáng tỏ toàn bộ lớp service của Ceph. Càng đi lên cao, client càng “thấy ít object hơn” và “thấy nhiều block/file semantics hơn”; nhưng ở bên dưới, chúng vẫn đang dựa vào cùng lõi truy cập object store.

### 4.3 RGW đứng ở đâu so với librados

- RGW cũng không đứng ngoài cuộc. Glossary của Ceph mô tả rất rõ Ceph Object Gateway là object storage interface built on top of librados. Nghĩa là RGW là một lớp object service qua HTTP, nhưng sâu bên dưới nó vẫn là một client path đi về lõi librados/RADOS.

- Điều này rất quan trọng vì direct librados client và RGW cùng làm việc với object ở một mức nào đó, nhưng chúng hoàn toàn khác nhau về tầng giao diện. Direct librados là object ở mức thấp của Ceph; RGW là object service ở mức ứng dụng với user riêng, bucket riêng và API riêng. Nếu không tách hai tầng này, rất dễ nghĩ “đều là object nên giống nhau”, trong khi thực tế chúng khác nhau rất nhiều ở lớp sử dụng.

### 4.4 krbd, kernel path và user-space path

Với block, còn có một khác biệt quan trọng nữa: kernel path và user-space path. krbd là đường kernel, còn librbd là đường user-space. Cả hai đều cuối cùng đi về Ceph cluster qua cùng nguyên lý nền, nhưng feature support, cache, cách lộ lỗi và hành vi vận hành có thể khác nhau đáng kể. Đây là lý do trong thực tế, câu hỏi “client đang đi đường nào?” rất quan trọng khi debug.

### 4.5 Namespace trong librados là gì và khi nào cần nghĩ tới nó

- Tài liệu User Management của Ceph có một điểm rất đáng chú ý: namespace chỉ khả dụng khi dùng librados. Tài liệu còn giải thích rằng thay vì tạo pool riêng cho từng user hoặc từng nhóm user, bạn có thể dùng namespace để gắn namespace vào tên object mà không phải chịu chi phí tính toán như một pool riêng biệt.

- Đây là một chi tiết rất giá trị vì nó cho thấy direct librados client có một số khả năng mà khi đi qua service cao hơn bạn không còn thấy trực tiếp nữa. Namespace là ví dụ điển hình: nó không thay thế pool, nhưng cho phép phân tách logic tốt hơn trong một pool khi ứng dụng thật sự đi thẳng bằng librados.

> Cùng là “Ceph client”, nhưng direct librados, librbd, libcephfs, RGW hay kernel path không giống nhau ở lớp giao diện và cách lộ ra cho người dùng. Chúng giống nhau ở chỗ cuối cùng đều quay về cùng một lõi truy cập RADOS.

## 5. Điều ứng dụng thấy khác điều cluster thật sự lưu

- Một direct librados client thường phải nghĩ bằng pool, object name, namespace và caps. Nhưng ngay cả ở mức này, điều ứng dụng thấy vẫn không đồng nhất hoàn toàn với placement vật lý trong cluster. Client không biết và cũng không cần giữ bản đồ object-to-OSD cố định. Nó chỉ cần object name, pool name và cluster map; phần còn lại do librados cùng CRUSH tính ra.

- Điều này rất đáng nhớ vì nó cho thấy “trực tiếp tới RADOS” không có nghĩa là “biết hết vật lý bên dưới”. Ngay cả direct client cũng đang làm việc với một lớp logic: object name và pool name. Còn placement thật trên PG, primary OSD và acting set vẫn là kết quả của map và thuật toán phân bố dữ liệu.

## 6. Kết luận

- librados là lớp truy cập mức thấp vào RADOS, và là mảnh ghép giúp giải thích vì sao các client rất khác nhau của Ceph vẫn gặp nhau ở cùng một lõi. Client lấy cluster map từ MON, dùng object name và pool name để librados tính placement bằng CRUSH, rồi đi thẳng tới OSD cho luồng dữ liệu. Song song với đó, CephX, keyring và caps trả lời câu hỏi “client là ai và được phép làm gì”.
- Các lưu ý :
    - librados là truy cập mức thấp vào RADOS
    - client lấy cluster map từ MON
    - client đưa object name và pool name cho librados
    - librados tính PG và primary OSD bằng CRUSH
    - data path đi thẳng từ client tới OSD
    - CephX, caps và keyring là nền của auth và phân quyền client
> mọi client của Ceph nhìn bề ngoài có thể khác nhau, nhưng khi xuống đủ sâu, chúng đều quay về cùng một lõi: `librados` hoặc cùng chức năng được gói trong `librados`, dùng cluster map và CRUSH để nói chuyện trực tiếp với OSD.