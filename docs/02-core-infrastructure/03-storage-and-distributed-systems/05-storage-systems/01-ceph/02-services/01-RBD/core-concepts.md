# Các khái niệm cốt lõi của RBD
## 1. RBD là gì và bản chất thật của nó
### 1.1 RBD là block interface trên object backend

- RBD là viết tắt của **RADOS Block Device**. Ở mặt ngoài, nó cung cấp cho ứng dụng hoặc hypervisor một block device logic có thể được map vào máy Linux, gắn cho máy ảo, hoặc dùng làm backend cho các nền tảng như QEMU/KVM và OpenStack. Nhưng ở mặt trong, RBD không làm Ceph trở thành một hệ block storage “thuần block” theo nghĩa vật lý; nó chỉ làm cho Ceph trình bày lõi object store của mình dưới dạng block interface. Tài liệu Glossary của Ceph nói rất rõ rằng Ceph Block Device chia dữ liệu block-based thành các “chunks”, và RADOS lưu các chunks đó như các object. rbd(8) cũng mô tả RBD images là các block devices được striped trên nhiều objects và được lưu trong RADOS object store.

- Đây là điểm bản chất nhất của toàn bộ RBD: VM thấy ổ đĩa, nhưng Ceph thấy object. Nếu không giữ được câu này trong đầu, người học rất dễ hiểu nhầm rằng một RBD image ở backend là một “file ổ đĩa” nguyên khối giống kiểu disk image cục bộ. Thực tế không phải vậy. Ở tầng lõi, Ceph không lưu “ổ đĩa” như ứng dụng đang tưởng tượng; Ceph lưu các object đại diện cho những phần của image đó, rồi đặt chúng qua pool, PG, CRUSH và OSD như mọi dữ liệu RADOS khác.

> RBD không phải “một file block lớn nằm trong Ceph”. RBD là một lớp ngữ nghĩa block được dựng trên một backend object phân tán. Đây là điểm phải nhớ trước mọi feature, mọi lệnh và mọi troubleshooting về sau.

### 1.2 RBD nằm ở đâu trong kiến trúc Ceph

- Trong kiến trúc Ceph, RBD nằm ở lớp service / client interface, phía trên RADOS. Ở dưới cùng, Ceph vẫn là object store phân tán với pool, PG, CRUSH và OSD. Ở phía trên, RBD cung cấp cho ứng dụng một giao diện block. Kiến trúc tổng quát này được tài liệu Ceph mô tả rất nhất quán: block, file và object là các giao diện khác nhau; còn lõi lưu trữ thật bên dưới vẫn là RADOS. RBD vì thế không phải một backend tách biệt, mà là một trong những lớp trình bày dữ liệu ra ngoài của Ceph.

- Nếu nhìn theo luồng từ trên xuống, thứ tự đúng là: ứng dụng hoặc hypervisor thao tác với block device; client path của RBD chuyển yêu cầu block thành object operations; các object này được đặt vào pool, ánh xạ vào PG, rồi CRUSH xác định OSD chịu trách nhiệm. Nói cách khác, RBD là lớp dịch ngữ nghĩa block sang ngữ nghĩa object phân tán. Chính vì vậy, mọi hiện tượng bạn thấy ở RBD cuối cùng đều nối về các lớp foundations như pool, PG, OSD, BlueStore và network.

### 1.3 Vì sao RBD quan trọng trong Ceph và trong môi trường cloud

- RBD thường là service quan trọng nhất của Ceph trong private cloud vì đa số vòng đời hạ tầng tính toán đều xoay quanh block storage: volume cho VM, image backend, boot-from-volume, clone image, snapshot volume, backup block-level, và các workflow tương tự. Tài liệu Ceph về OpenStack integration còn khuyến nghị dùng các pool riêng như images, volumes, backups, vms, rồi khởi tạo chúng bằng rbd pool init, cho thấy RBD là thành phần rất trung tâm khi Ceph đóng vai trò storage backend cho cloud.

- Điểm quan trọng là RBD không chỉ “quan trọng vì được dùng nhiều”. Nó còn quan trọng vì nó là nơi hội tụ giữa ba thế giới: storage semantics của hệ điều hành, lifecycle của cloud platform, và sự thật kỹ thuật của RADOS. Khi một volume OpenStack bị chậm, bị lệch dung lượng, bị kẹt snapshot, hay mirror gặp lỗi, bạn thường phải hiểu đồng thời cả ba tầng này. Đó là lý do RBD đáng được xem là service cần học kỹ nhất, chứ không chỉ là block driver “có sẵn” của Ceph.

## 2. RBD image thực chất được lưu như thế nào
### 2.1 RBD image không phải một file block nguyên khối

- Khi người dùng nhìn một RBD image, họ thường hình dung ra một ổ đĩa ảo hoàn chỉnh, ví dụ 100 GiB hay 500 GiB. Nhưng ở backend, RBD image không tồn tại như một khối duy nhất. rbd(8) mô tả rất rõ rằng RBD images là các block devices được striped over objects, tức là được chia và trải ra trên nhiều object trong RADOS. Glossary của Ceph dùng cách diễn đạt đơn giản hơn: dữ liệu block-based được chia thành các chunks, và RADOS lưu các chunks đó như object.

- Ý nghĩa của điều này rất lớn. Nó giải thích vì sao:

    - dung lượng thực dùng của image không nhất thiết bằng kích thước logic của image,
    - snapshot và clone có thể hoạt động rất nhanh ở thời điểm tạo,
    - rbd du phản ánh actual used space ở tầng object,
    - và xóa file trong guest OS không tự động làm footprint backend giảm ngay nếu block-level extents chưa được xử lý theo cách phù hợp.
- Tất cả các hiện tượng đó chỉ trở nên sáng rõ khi bạn bỏ ý nghĩ “RBD image là một file block nguyên khối”.
### 2.2 Object layout, object size và striping

- rbd ghi rõ rằng RBD image được striped trên nhiều object, và kích thước object mà image được striping qua phải là lũy thừa của 2. Điều này cho thấy ngay từ tầng image, RBD đã có một mô hình layout riêng, không phải kiểu “để filesystem hoặc kernel tự lo hết”. Block image logic được cắt thành các đơn vị đủ phù hợp để lưu và phân phối lên object store, và chính cách cắt này ảnh hưởng tới hành vi của image về sau.

- Một cách hiểu rất hữu ích là: block size mà ứng dụng ghi và object size mà Ceph dùng để tổ chức backend không phải là cùng một thứ. Ứng dụng nghĩ bằng sector, block, partition và filesystem extents; còn Ceph nghĩ bằng object layout của image. Đây là lý do nhiều hiện tượng ở RBD luôn có hai mặt: mặt block mà guest thấy và mặt object mà cluster thật sự đang thao tác. Nếu không tách được hai tầng này, người vận hành rất dễ chẩn đoán sai nguyên nhân của các vấn đề về snapshot, actual used space hoặc performance.

### 2.3 Quan hệ giữa image, pool, PG và OSD

- Một RBD image luôn nằm trong một pool cụ thể. Pool đó quy định policy nền như replicated hay erasure-coded, CRUSH rule, số PG, quota và các thuộc tính liên quan. Các object của image sau đó được ánh xạ vào PG, và CRUSH tính ra tập OSD chịu trách nhiệm lưu dữ liệu. Tài liệu kiến trúc của Ceph nói rất rõ rằng Ceph Block Device stripes image qua nhiều object; mỗi object được ánh xạ vào placement group; rồi placement groups được phân phối qua các ceph-osd daemons trong cluster.

- Đây là một điểm cực kỳ quan trọng về tư duy: khi bạn tạo một image trong pool volumes, bạn không chỉ “tạo một ổ đĩa mới”, mà bạn đang đặt một tập object mới vào một policy domain cụ thể. Vì vậy, mọi thứ như durability, availability, recovery behavior và placement của image đó đều đi theo pool và PG của nó, chứ không phải là thuộc tính riêng lẻ tách biệt của image. Nói cách khác, image là đơn vị người dùng thấy; nhưng placement và durability của nó vẫn do các lớp pool–PG–OSD quyết định.

### 2.4 Điều ứng dụng nhìn thấy khác gì điều Ceph thật sự lưu

- Ở tầng ứng dụng, RBD cho cảm giác rất giống một block device truyền thống: có thể partition, format filesystem, mount hoặc gắn vào VM. Nhưng Ceph không bao giờ lưu “filesystem của guest” như một cấu trúc hiểu sẵn ở backend. Ceph chỉ thấy block updates của image, và dưới sâu hơn nữa là các object đại diện cho các phần của image đó. Điều này có nghĩa:

    - guest filesystem used là một chỉ số của tầng guest,
    - còn rbd du là một chỉ số gần hơn với actual object allocation của tầng RBD/RADOS.

- Đây là lý do rất nhiều tranh cãi về “sao khách chỉ dùng từng này GB mà backend lại ghi nhận lớn hơn” thực ra không phải lỗi ngay lập tức. Chúng thường là hậu quả của việc so hai tầng semantics khác nhau. Nếu file này chỉ dạy một insight duy nhất về RBD, thì đó nên là insight này: đừng bao giờ đồng nhất cái guest đang thấy với cái Ceph đang lưu. Với RBD, hai tầng đó liên hệ rất chặt nhưng không bao giờ hoàn toàn trùng nhau.

> RBD image là một block abstraction. Pool, PG và OSD mới là nơi durability và placement thật sự được quyết định. Còn object layout mới là nơi dữ liệu block được Ceph tổ chức ở backend. Muốn hiểu đúng RBD, phải nhìn được cả ba tầng này cùng lúc.

## 3. Đường I/O của RBD
### 3.1 Read path của RBD

Ở mặt ngoài, một thao tác đọc trên RBD trông như đọc một block device thông thường. Nhưng ở mặt trong, client RBD phải biết image thuộc pool nào, layout của image ra sao, và object nào tương ứng với vùng block đang được đọc. Sau đó thao tác này được chuyển thành truy cập tới các object liên quan trong RADOS. Vì RBD được striped trên objects, nên read path của nó bản chất là dịch yêu cầu đọc block thành đọc object backend. Đây là hệ quả trực tiếp từ mô hình được mô tả trong rbd(8) và Ceph Architecture.

Điều cần hiểu ở đây là một lần đọc block không phải lúc nào cũng tương ứng một “lần đọc file” ở backend theo cách người dùng hình dung. Tùy layout, feature, cache path và tình trạng cluster, read path có thể chịu ảnh hưởng bởi object placement, cache hit/miss, snapshot lineage hoặc các lớp client-side behavior. Đây là lý do hiệu năng đọc của RBD không thể đánh giá đúng nếu chỉ nhìn từ phía guest OS. Phải luôn nhớ rằng read path đang đi qua một lớp block abstraction đặt trên object store phân tán.

### 3.2 Write path của RBD

- Write path của RBD còn quan trọng hơn vì nó chạm trực tiếp tới consistency và durability. Ở mặt ngoài, ứng dụng ghi vào block device. Nhưng ở mặt trong, client path của RBD chuyển thao tác đó thành cập nhật lên các object liên quan của image, rồi các object này đi theo write path chung của RADOS. Điều đó có nghĩa **mọi yếu tố như primary OSD, replica/chunk placement, commit/apply latency và backend storage path đều ảnh hưởng trực tiếp tới write latency mà guest đang cảm nhận.**

- Một điểm rất dễ bị bỏ qua là write path của RBD không **chỉ chịu ảnh hưởng của cluster**, mà còn c**hịu ảnh hưởng của feature set của image và client behavior**. Ví dụ, caching policies của librbd, snapshot lineage, exclusive-lock, object-map hay persistent caches đều có thể làm write path thực tế khác đi đáng kể. Vì vậy, nói “RBD write path” mà chỉ nhìn vào RADOS replication thôi thì vẫn chưa đủ. RBD là nơi block semantics, image features và cluster durability chồng lên nhau.

### 3.3 Vai trò của primary OSD trong block I/O

- Dù ứng dụng thấy block device, write path cuối cùng vẫn quay về mô hình primary-copy của Ceph ở tầng RADOS. Nghĩa là dữ liệu block sau khi được dịch thành object operations vẫn đi tới acting set của các object đó, và primary OSD vẫn là điểm điều phối logic của đường ghi. Đây là hệ quả trực tiếp từ việc RBD chỉ là block interface trên RADOS object store, chứ không có một “đường block riêng” tách biệt khỏi cơ chế lưu trữ chung của Ceph.

- Điều này giải thích vì sao khi OSD chậm, PG `degraded`, `recovery/backfill` mạnh, hoặc backend BlueStore có vấn đề, thì VM dùng RBD có thể thấy latency tăng ngay dù hypervisor và guest không hỏng gì. Block I/O mà guest thấy thực chất vẫn đang chịu tác động của toàn bộ trạng thái thật của cluster. Nói cách khác, RBD không tách người dùng block ra khỏi sự thật của RADOS; nó chỉ che giấu sự thật đó sau một block abstraction.

### 3.4 RBD consistency thực chất được bảo đảm ở đâu

- Một hiểu nhầm phổ biến là nghĩ RBD tự nó có một lớp consistency riêng độc lập với phần còn lại của Ceph. Thực tế, consistency của RBD được bảo đảm nhờ hai lớp chồng lên nhau:

    - ở tầng client/image: feature semantics như exclusive-lock, cache policy, snapshot behavior
    - ở tầng backend: consistency của RADOS write path, PG state và OSD durability path.

- Điều này rất quan trọng vì nó giúp bạn hiểu đúng nhiều lỗi “tưởng là RBD hỏng”. Nhiều khi thứ đang hỏng không phải block abstraction, mà là:

    - client-side cache semantics,
    - stale lock/watcher,
    - PG inconsistency,
    - hoặc cluster-side degradation.
- RBD consistency vì thế không nằm ở một chỗ duy nhất; nó là kết quả của việc block interface này được dựng đúng trên cả client path lẫn backend path của Ceph.

> Muốn hiểu đúng I/O của RBD, phải bỏ cách nghĩ “guest ghi block là backend ghi block”. Đúng hơn, guest ghi block, RBD dịch thành object updates, rồi RADOS chịu trách nhiệm placement và durability. Tức là block I/O của RBD luôn là block semantics ở trên, object reality ở dưới.

## 4. Client path của RBD
### 4.1 librbd là gì

librbd là thư viện user-space để ứng dụng làm việc với RBD. Trong thực tế, các tích hợp như QEMU/KVM thường dùng librbd để nói chuyện trực tiếp với Ceph cluster. Điều này cho phép ứng dụng khai thác nhiều feature phong phú của RBD ở tầng user-space, đồng thời mở đường cho nhiều cơ chế cache và lifecycle management phức tạp hơn so với kernel path thuần. Tài liệu Ceph block devices mô tả rõ client block của Ceph có thể giao tiếp qua kernel modules hoặc librbd.

### 4.2 `krbd` là gì
`krbd` là đường dùng Linux kernel rbd driver để map image thành block device trong kernel. Nó phù hợp với mô hình “ổ đĩa block gắn vào host” theo kiểu truyền thống hơn. Nhưng vì nó là kernel path, tập feature hỗ trợ và nhịp theo kịp tính năng mới thường phụ thuộc vào kernel support. Config reference của Ceph còn ghi rõ nhiều feature có mốc hỗ trợ riêng cho `KRBD`, ví dụ fast-diff hay deep-flatten có các mốc hỗ trợ khác nhau theo version.

### 4.3 Khi nào đi qua librbd, khi nào đi qua `krbd`

- Một cách hiểu rất thực tế là:
    - khi hypervisor hoặc ứng dụng tích hợp trực tiếp với Ceph ở user-space, thường bạn đang đi qua librbd
    - khi host Linux map image thành thiết bị block trong kernel, bạn đang đi qua `krbd`

- Sự khác biệt này không chỉ là đường kỹ thuật. Nó quyết định:
    - feature nào khả dụng,
    - cache nào khả dụng,
    - hành vi lock/watcher ra sao,
    - và một số kiểu tối ưu/giới hạn compatibility trong vận hành.
### 4.4 Vì sao client path ảnh hưởng trực tiếp tới feature và hành vi của RBD

- Đây là điểm mà rất nhiều note RBD viết quá sơ sài. librbd hay krbd không chỉ là “hai cách map image”. Chúng là hai con đường vận hành khác nhau của block service. Ví dụ, tài liệu về persistent write-back cache và persistent write log cache đều gắn rất mạnh với librbd path và nhấn mạnh phụ thuộc vào exclusive-lock. Tức là có cả một lớp behavior của RBD chỉ thật sự lộ ra khi bạn biết client đang đi con đường nào.

- Chính vì vậy, khi troubleshooting hoặc thiết kế feature set cho image, câu hỏi “client đang đi qua librbd hay krbd?” quan trọng không kém câu hỏi “cluster đang khỏe hay không?”. Nhiều hiện tượng như cache semantics, feature mismatch, stale lock hay hiệu năng không như mong đợi sẽ không thể hiểu đúng nếu bỏ qua client path. Đây là một trong những insight có giá trị thực chiến cao nhất của RBD.

> RBD không chỉ là chuyện của cluster. Nó còn là chuyện của client path. Cùng một image, nhưng đi qua librbd hay krbd có thể làm feature support, cache behavior và troubleshooting path khác nhau rõ rệt. Nếu không xác định đúng client path, bạn rất dễ chẩn đoán sai bản chất vấn đề.

## 5. Những khả năng cốt lõi của RBD
### 5.1 Thin provisioning

Một trong những khả năng quan trọng nhất của RBD là thin provisioning. Điều này có nghĩa image có thể được khai báo với kích thước logic lớn ngay từ đầu, nhưng backend không nhất thiết phải cấp phát toàn bộ dung lượng đó ngay lập tức. Chỉ những phần block thực sự được ghi mới dần trở thành object có dữ liệu ở phía RADOS. Đây là lý do RBD rất phù hợp với môi trường cloud, nơi người dùng thường muốn volume “to về mặt logic” nhưng hạ tầng không thể lãng phí raw space cho mọi volume chưa dùng tới.

> Thin provisioning làm cho RBD image có thể “trông lớn hơn” nhiều so với phần backend thực sự đã được cấp phát. Vì vậy, kích thước image và dung lượng thực đã dùng là hai đại lượng khác nhau ngay từ bản chất, không phải chỉ khác nhau do lỗi đo đạc.

### 5.2 Resize

RBD hỗ trợ resize image, tức là thay đổi kích thước logic của block device sau khi tạo. Đây là khả năng rất quan trọng trong vòng đời volume vì block storage trong thực tế hiếm khi giữ nguyên một kích thước mãi mãi. Tuy nhiên, resize ở RBD chỉ thay đổi kích thước image logic; còn partition table, filesystem hoặc LVM bên trong guest là một lớp khác và phải được xử lý riêng nếu muốn tận dụng dung lượng mới. Điều này phản ánh rất rõ một quy luật quen thuộc của RBD: block abstraction ở mặt ngoài và trạng thái guest filesystem ở bên trong không phải cùng một tầng.

### 5.3 Snapshot

Snapshot của RBD là ảnh chụp chỉ-đọc của trạng thái image tại một thời điểm. Các tài liệu block device của Red Hat mô tả snapshot là một read-only copy of the state of an image at a particular point in time, và cũng nhấn mạnh đây là nền của nhiều workflow quản trị, clone và bảo vệ dữ liệu. Snapshot rất nhanh để tạo vì RBD tận dụng cơ chế copy-on-write ở backend thay vì sao chép đầy đủ toàn bộ image ngay tại thời điểm snapshot.

### 5.4 Clone và layering

Ceph hỗ trợ snapshot layering, tức là tạo clone từ snapshot một cách rất nhanh. Tài liệu snapshot management của Red Hat mô tả rõ rằng Ceph supports snapshot layering, which allows you to clone images quickly and easily. Clone ban đầu không phải bản sao đầy đủ độc lập; nó dựa vào snapshot cha theo mô hình copy-on-write. Vì vậy clone nhanh và tiết kiệm dung lượng lúc đầu, nhưng đồng thời tạo ra một quan hệ phụ thuộc giữa image con và image cha.

### 5.5 Copy-on-write

Copy-on-write là cơ chế làm cho snapshot và clone của RBD trở nên mạnh về mặt vận hành. Nhưng điểm phải hiểu đúng là copy-on-write không phải “miễn phí vô hạn”. Nó chuyển chi phí từ thời điểm tạo snapshot/clone sang giai đoạn sống lâu dài của lineage. Khi image con tiếp tục ghi đè, hoặc khi snapshot/clone chain kéo dài, cluster phải theo dõi ngày càng nhiều quan hệ giữa dữ liệu gốc và dữ liệu phát sinh. Đây là nền của rất nhiều vấn đề vận hành về sau như flatten chậm, parent không xóa được, hay snapshot chain ảnh hưởng hiệu năng.

### 5.6 Diff và actual used space

Một khả năng cực kỳ giá trị nhưng dễ bị bỏ qua của RBD là khả năng tính diff và actual used space. Tài liệu config reference của Ceph ghi rõ fast-diff làm cho việc tạo diff giữa snapshots nhanh hơn nhiều, và cũng làm cho việc tính actual data usage của snapshot hoặc volume qua rbd du nhanh hơn rất nhiều. Điều này có ý nghĩa thực tế rất lớn vì nhiều thao tác backup, replication, audit dung lượng và capacity planning của RBD đều phụ thuộc vào khả năng thấy cái gì đã thay đổi và cái gì thực sự đang chiếm backend space.

## 6. Image features và ý nghĩa kiến trúc của chúng
### 6.1 Vì sao phải xem image features như một phần của kiến trúc

Rất nhiều người nhìn image features của RBD như một danh sách “cờ bật/tắt”. Cách nhìn đó đúng ở mức CLI, nhưng chưa đúng ở mức kiến trúc. Trong RBD, feature không chỉ thêm khả năng phụ; chúng thay đổi cách image được theo dõi, cách lineage hoạt động, cách diff được tính, cách lock vận hành, và cả việc image đó có thể tham gia các workflow mirroring hay không. Tài liệu rbd(8) và config reference của Ceph liệt kê rõ các feature như layering, exclusive-lock, object-map, fast-diff, deep-flatten, journaling, đồng thời cũng chỉ ra các quan hệ phụ thuộc giữa chúng.

> Feature set của image không phải “trang sức”. Nó quyết định image này đang sống theo kiểu nào: có lineage ra sao, có tính được diff nhanh không, có mirror được theo kiểu journal không, có cần lock semantics chặt không. Vì vậy, muốn hiểu đúng RBD image, phải nhìn nó cùng feature set của nó, không thể chỉ nhìn size và pool.

### 6.2 Layering

Layering là feature nền cho snapshot-based clone. Nếu không có layering, bạn không có clone lineage kiểu copy-on-write đúng nghĩa. Vì RBD clone dựa trên snapshot cha, layering chính là feature cho phép image con sống như một nhánh mới mà vẫn còn phụ thuộc vào image cha ở giai đoạn đầu. Đây là feature rất “cloud-native”, vì nó làm cho việc sinh nhiều volume hoặc VM từ một golden image trở nên rẻ và nhanh.

### 6.3 Exclusive-lock

Exclusive-lock là một trong những feature quan trọng nhất nhưng cũng hay bị hiểu sai nhất. Theo tài liệu rbd(8) và config reference, nhiều feature khác phụ thuộc vào nó, trực tiếp hoặc gián tiếp. Ý nghĩa cốt lõi của exclusive-lock là image có một thực thể client ghi chính đang giữ quyền khóa độc quyền, nhờ đó Ceph mới có thể an toàn triển khai các cơ chế theo dõi và tối ưu ở tầng image/client. Vì vậy, exclusive-lock không phải “một lỗi khóa cần tránh”, mà thường là nền cho các feature mạnh hơn của RBD.

### 6.4 Object-map

Object-map là feature giúp RBD theo dõi sự tồn tại và trạng thái của các object thuộc image. Nó đặc biệt quan trọng vì fast-diff phụ thuộc vào `object-map`, và `object-map` lại phụ thuộc vào `exclusive-lock`. Nói cách khác, nếu bạn muốn image có khả năng diff nhanh và tính actual used space nhanh, `object-map` gần như là lớp nền bắt buộc. Đây là một ví dụ rất điển hình cho việc feature của RBD không sống độc lập mà tạo thành một chuỗi phụ thuộc có ý nghĩa vận hành rõ rệt.

### 6.5 Fast-diff

Fast-diff làm cho việc tính diff giữa snapshots và tính dung lượng thực qua rbd du nhanh hơn rất nhiều. Tài liệu Ceph viết rất trực tiếp về điều này. Đây là feature cực kỳ có giá trị cho backup, replication, audit dung lượng và bất kỳ workflow nào cần biết chính xác phần block nào đã thay đổi. Nếu thiếu fast-diff, nhiều thao tác sẽ vẫn làm được, nhưng đường tính toán nặng hơn rõ rệt.

### 6.6 Deep-flatten

Deep-flatten là feature rất hay bị lướt qua, nhưng ý nghĩa của nó rất lớn. Tài liệu config reference giải thích rằng nếu không có deep-flatten, snapshots của image con vẫn còn phụ thuộc vào parent, nên parent chưa thể bị xóa cho tới khi các snapshots đó được xử lý. Deep-flatten làm cho parent độc lập với clones ngay cả khi clone còn snapshots, đổi lại là dùng thêm dung lượng OSD. Điều này cho thấy deep-flatten không phải “feature phụ”, mà là một lựa chọn kiến trúc về việc bạn muốn tối ưu độ độc lập của lineage hay mức tiết kiệm backend space.

### 6.7 Journaling

Journaling là feature hỗ trợ journaled I/O và là nền rất quan trọng cho journal-based mirroring. rbd(8) nêu rõ journaling yêu cầu exclusive-lock. Điều đó cho thấy journal không phải chỉ là “ghi log cho vui”, mà là một phần của semantics cần thiết để một số workflow nâng cao, đặc biệt là DR/mirroring, có thể hoạt động đúng. Trong thực tế, image có hay không có journaling là một điểm phân biệt rất lớn giữa “volume block bình thường” và “volume block có vai trò trong kiến trúc mirror/DR”.

### 6.8 Quan hệ phụ thuộc giữa các feature

- Ceph docs cho thấy rất rõ một chuỗi phụ thuộc quan trọng:

    - object-map cần exclusive-lock
    - fast-diff cần object-map
    - journaling cần exclusive-lock

- Đây là một trong những điểm đáng nhớ nhất của image features. Nhiều khi người vận hành thấy một lệnh như rbd du chậm, hay mirror không lên như kỳ vọng, hoặc một image không thể bật feature nào đó, rồi chỉ nhìn đúng feature bị thiếu. Nhưng với RBD, muốn hiểu đúng behavior của image, phải nhìn chuỗi dependency của feature set, chứ không chỉ nhìn một feature đơn lẻ.

### 6.9 Feature nào là nền cho performance, lifecycle và mirroring

- Có thể chia như sau:

    - nghiêng về lifecycle và lineage: layering, deep-flatten
    - nghiêng về tracking và tối ưu thao tác: object-map, fast-diff
    - nghiêng về lock/consistency ở client path: exclusive-lock
    - nghiêng về DR / journaled replication semantics: journaling

- Cách phân loại này hữu ích hơn nhiều so với việc chỉ học tên feature. Nó giúp bạn hiểu vì sao cùng là “RBD image”, nhưng image phục vụ VM thông thường, image dùng cho backup/diff-heavy workflows, và image dùng cho mirroring có thể cần feature set rất khác nhau.

## 7. Snapshot, clone và lineage
### 7.1 Snapshot trong RBD thực chất là gì

Snapshot là read-only copy của trạng thái image tại một thời điểm. Docs của Red Hat mô tả rất rõ điều này. Đây là định nghĩa kỹ thuật đúng, nhưng vẫn chưa đủ nếu muốn hiểu bản chất. Snapshot trong RBD không phải là “sao chép toàn bộ image thành một image mới” theo kiểu thô. Nó là một mốc trạng thái dùng để giữ lại lịch sử của image và làm nền cho clone/layering về sau. Chính vì vậy snapshot tạo rất nhanh, nhưng giá trị thật của snapshot không nằm ở thao tác tạo mà nằm ở toàn bộ lineage mà nó mở ra.

### 7.2 Protect / unprotect

Snapshot muốn dùng làm parent cho clone thì phải được protect. Khi snapshot đang là cha của clone, bạn không thể đơn giản xóa nó. Muốn gỡ snapshot, phải xử lý quan hệ phụ thuộc trước rồi mới unprotect và xóa. Đây là một behavior cực kỳ quan trọng của RBD vì nó phản ánh rằng clone lineage không phải “tham chiếu lỏng lẻo”, mà là quan hệ phụ thuộc thực sự ở tầng image/object semantics.

### 7.3 Clone từ snapshot

Clone trong RBD được tạo từ snapshot, không phải từ head đang ghi của image. Điều này rất quan trọng vì nó giữ cho clone có một điểm cha rõ ràng, ổn định và read-only. Đây là nền khiến snapshot layering của RBD vừa nhanh vừa nhất quán. Khi bạn clone từ một golden image snapshot, cái bạn đang tạo ra thực chất là một nhánh mới trong lineage chứ chưa phải một bản sao độc lập hoàn toàn.

### 7.4 Parent-child relationship

- Một khi clone được tạo ra, image con sẽ giữ quan hệ cha-con với snapshot parent. Chính quan hệ này là thứ làm clone ban đầu tiết kiệm thời gian và dung lượng. Nhưng đây cũng là nơi các vấn đề vận hành bắt đầu xuất hiện:

    - parent chưa xóa được
    - snapshot chưa unprotect được
    - clone vẫn còn phụ thuộc lineage
    - flatten trở thành thao tác cần thiết
- Vì vậy, muốn hiểu clone trong RBD, phải hiểu clone không phải “copy rẻ”, mà là copy-on-write child với lineage thật.
### 7.5 Flatten và deep-flatten

Flatten làm cho image con trở thành **một image độc lập hơn bằng cách chấm dứt phụ thuộc vào parent ở mức dữ liệu liên quan**. Deep-flatten còn đi xa hơn khi **giúp cả snapshots của image con cũng không còn phụ thuộc parent nữa**. Ceph docs mô tả rất rõ rằng nếu thiếu deep-flatten, snapshots của image vẫn có thể còn dựa vào parent, khiến parent chưa xóa được. Điều này cho thấy flatten không phải lệnh “dọn dẹp cosmetic”, mà là bước chuyển lineage từ phụ thuộc sang độc lập, đổi bằng chi phí backend space và thời gian xử lý.

### 7.6 Vì sao lineage là điểm mạnh nhưng cũng là nguồn gốc của nhiều vấn đề vận hành

- Lineage là một trong những thứ đẹp nhất của RBD vì nó cho phép:

    - tạo clone rất nhanh
    - tiết kiệm dung lượng ban đầu
    - xây workflow golden image hiệu quả
    - tận dụng snapshot như mốc cha hợp lệ

- Nhưng lineage cũng là nơi vận hành bắt đầu phức tạp:

    - snapshot tích tụ
    - parent-child graph dài
    - cleanup khó
    - flatten nặng
    - các thao tác xóa hoặc đổi trạng thái bị chặn bởi dependency chain

> Snapshot và clone không đắt ở lúc tạo; chúng đắt ở vòng đời quan hệ phụ thuộc mà chúng để lại. Nói cách khác, lineage là tài sản lớn của RBD, nhưng cũng là một dạng “nợ vận hành” nếu không có kỷ luật lifecycle đủ tốt.

## 8. Các feature mở rộng và các hướng mở rộng chức năng của RBD
### 8.1 RBD Mirroring

- RBD mirroring là cơ chế nhân bản bất đồng bộ các RBD image giữa hai hoặc nhiều Ceph clusters để phục vụ disaster recovery. Tài liệu Red Hat mô tả rất rõ rằng đây là một quá trình replication block images giữa các cluster đặt ở các vị trí địa lý khác nhau, giúp giảm downtime và data loss khi site chính gặp sự cố; đồng thời journal-based mirroring có thể giữ replica point-in-time consistent cho các thay đổi của image, bao gồm cả resize, snapshot, clone và flatten. Điều quan trọng về mặt kiến trúc là mirroring không thay đổi bản chất block của RBD, mà mở rộng RBD từ “block service trong một cluster” thành “block service có thể sao chép trạng thái sang cluster khác”.

- Về mặt tư duy, mirroring không nên bị hiểu như một “feature snapshot nâng cao” hay “backup nhanh hơn”. Nó là một lớp khả năng DR được gắn thêm lên RBD image, đòi hỏi thêm image features, daemon rbd-mirror, quan hệ peer giữa hai cluster và cả một logic failover/failback riêng. Vì vậy, trong file core-concepts, điều quan trọng không phải học toàn bộ lệnh mirror, mà là hiểu rằng RBD không dừng ở “tạo một block device”, mà còn có thể trở thành một đối tượng block có khả năng replication liên cluster.

### 8.2 RBD Migration 

- RBD migration là khả năng di chuyển image giữa các pool, giữa các layout/format khác nhau, và cả từ một số nguồn ngoài vào trong RBD. Tài liệu Red Hat về live migration mô tả rằng khi migration được khởi động, source image sẽ được deep copied sang destination image, đồng thời cố gắng giữ sparse allocation của dữ liệu khi có thể. Đây là một capability rất quan trọng vì nó cho thấy RBD không chỉ là “nơi image tồn tại”, mà còn có cơ chế chính thức để thay đổi nơi ở, hình thức hoặc layout của image mà không cần lúc nào cũng dựa vào export/import thô.

- Điểm đáng nhớ hơn là migration làm lộ ra một đặc điểm rất trưởng thành của RBD: image không phải một thực thể bất động. Trong vòng đời thực tế, image có thể cần chuyển pool, đổi feature profile, đổi format hoặc đổi nguồn dữ liệu. Việc RBD có hẳn một state machine migration riêng cho thấy block service này không chỉ tối ưu cho I/O thường ngày, mà còn được thiết kế để hỗ trợ thay đổi cấu trúc vận hành về sau. Đây là lý do migration nên xuất hiện trong core-concepts: không phải để đi sâu lệnh, mà để người đọc thấy RBD có khả năng biến đổi vòng đời chứ không chỉ có khả năng tồn tại tĩnh.

### 8.3 Cache phía client và ý nghĩa của nó

- RBD không chỉ có backend-side behavior; nó còn có các tối ưu phía client. Ceph Pacific release notes giới thiệu một persistent write-back cache mới hoạt động theo kiểu log-structured và cung cấp point-in-time consistency cho backing image; RHCS 5 block device guide cũng có chương riêng về Persistent Write Log Cache, cùng các thao tác flush, invalidate và discard. Điều này cho thấy block semantics của RBD không chỉ được quyết định bởi cluster, mà còn có thể được mở rộng bởi một lớp cache bền vững ở phía client.

- Ý nghĩa kiến trúc của phần này rất lớn: cùng một RBD image, nhưng nếu client path có thêm persistent cache thì hành vi hiệu năng, độ trễ nhìn thấy và failure mode phía client đều có thể thay đổi. Nói cách khác, RBD không chỉ là “block device nói chuyện với cluster”, mà là “block device đi qua một client path có thể được tăng tốc và làm phức tạp thêm bằng cache semantics”. Đây là một trong những lý do mà về sau, troubleshooting RBD luôn phải hỏi thêm câu: client đang đi path nào và có đang dùng cache gì không.

### 8.4 Trash, export/import, export-diff/import-diff

- Tài liệu block device guide của Red Hat mô tả khá rõ rằng trong quá trình migration, source image có thể được chuyển vào RBD trash để tránh bị sử dụng nhầm; các release notes của Ceph cũng nhắc tới khả năng cấu hình purge trash theo lịch ở các release mới hơn. Cùng với đó, rbd còn có các họ thao tác như export, import, export-diff, import-diff, vốn biến RBD image thành một thực thể có thể được xuất, nhập, di chuyển, so sánh delta và quản lý vòng đời ngoài trạng thái online thông thường.

- Về mặt khái niệm, nhóm khả năng này cho thấy RBD không chỉ mạnh ở I/O runtime, mà còn mạnh ở lifecycle management. Một block image trong RBD có thể được snapshot, clone, mirror, migrate, đưa vào trash, export ra ngoài rồi import lại hoặc replay diff. Đó là một bức tranh rất khác với cách người mới thường hình dung block device như một “ổ đĩa chỉ có read/write”. Với RBD, block image là một đối tượng có vòng đời quản trị rất phong phú.

### 8.5 Các feature này đứng ở đâu: core capability hay vận hành nâng cao

- Nếu nhìn theo trọng tâm kiến trúc, có thể chia các khả năng của RBD làm hai tầng. Tầng thứ nhất là core capability của image: thin provisioning, resize, snapshot, clone, lineage, image features. Tầng thứ hai là khả năng mở rộng vòng đời và vận hành nâng cao: mirroring, migration, persistent cache, trash, diff/import-export. Tài liệu chính thống của Ceph và RHCS đều phản ánh đúng cấu trúc này khi dành các chương riêng cho mirroring, live migration, kernel/client modules, caching và image operations nâng cao thay vì trộn chúng hoàn toàn vào phần giới thiệu block image.

- Cách chia này rất hữu ích cho việc học. Nó giúp người đọc hiểu rằng một image RBD trước hết phải được hiểu như một block abstraction có object-backed semantics, sau đó mới hiểu tiếp rằng image đó có thể tham gia các kiến trúc lớn hơn như DR, migration pipeline, caching path hay import/export workflow. Nói ngắn gọn: những feature ở mục 8 không làm thay đổi “RBD là gì”, nhưng chúng mở rộng mạnh mẽ câu hỏi “RBD có thể trở thành gì trong một hệ thống thật”.

### 8.6 Vì sao cần biết chúng từ góc nhìn kiến trúc dù chưa đi sâu vận hành

- Ngay cả khi chưa đi sâu lệnh và runbook, vẫn cần nhắc các feature như mirroring, migration, cache và trash trong core-concepts, vì nếu không người học sẽ có một hình ảnh quá hẹp về RBD: chỉ là create/map/snapshot/clone. Trong thực tế, RBD được dùng trong cloud và storage platforms không chỉ như một block device, mà như một block object có vòng đời dài, có lineage, có DR path, có migration path, có client optimization path và có policy về xóa/khôi phục. Các tài liệu Ceph/RHCS về block device guide phản ánh đúng điều này bằng cách dành rất nhiều phần riêng cho các chủ đề đó.

> Nếu các mục trước trả lời “RBD là gì” và “RBD hoạt động ra sao”, thì mục này trả lời “RBD có thể được mở rộng thành những vai trò lớn hơn nào”. Đây là chỗ chuyển từ block image như một đối tượng kỹ thuật sang block image như một đối tượng vận hành có vòng đời đầy đủ.

## 9. Kết luận
### 9.1 Tóm tắt bản chất của RBD

- RBD là lớp block storage của Ceph, nhưng bản chất thật của nó không phải một block backend độc lập, mà là block interface trên object backend. Image của RBD không tồn tại như một khối nguyên vẹn ở dưới, mà được striped thành nhiều objects trong RADOS object store. Điều đó khiến mọi vấn đề của RBD, từ dung lượng, hiệu năng, snapshot, clone đến mirroring và migration, đều phải được hiểu trên cả hai tầng: block semantics ở mặt ngoài và object reality ở mặt trong.

- Cũng vì vậy, muốn hiểu RBD đúng mức nền tảng, phải đồng thời nhìn được bốn lớp: image layout, đường I/O, client path và feature set. Chỉ khi ghép đủ bốn lớp đó, bạn mới hiểu được vì sao cùng là “một volume block”, nhưng behavior của nó có thể thay đổi rất nhiều tùy pool, feature, client path, lineage, cache hay DR mode. Đây chính là lý do RBD xứng đáng được coi là một trong những service phức tạp và quan trọng nhất của Ceph.

### 9.2 Những hiểu lầm phổ biến về RBD

- Hiểu lầm phổ biến nhất là nghĩ rằng RBD image là một “file ổ đĩa nguyên khối” nằm trong Ceph. Tài liệu rbd(8) và glossary đều cho thấy điều ngược lại: image được striped trên objects và lưu trong RADOS object store. Đây là hiểu lầm gốc làm kéo theo rất nhiều hiểu lầm khác về snapshot, diff, dung lượng và performance.

- Hiểu lầm thứ hai là cho rằng snapshot nhanh nghĩa là snapshot gần như miễn phí. Snapshot đúng là rất nhanh để tạo, nhưng clone lineage, parent-child dependency, flatten và cleanup cho thấy chi phí thật của snapshot thường đến về sau chứ không phải ở thời điểm bấm lệnh tạo snapshot. Vì vậy, snapshot là công cụ mạnh, nhưng không phải tài nguyên “dùng thoải mái không cần vòng đời”.

- Hiểu lầm thứ ba là cho rằng exclusive-lock là một dạng lỗi hoặc trở ngại. Thực tế, nhiều feature quan trọng của RBD phụ thuộc vào exclusive-lock, bao gồm object-map, fast-diff, journaling và các cơ chế cache phía client. Nghĩa là lock ở đây thường là nền của khả năng nâng cao, chứ không phải mặc định là điều xấu.

- Hiểu lầm thứ tư là nghĩ rằng guest filesystem used phải luôn gần bằng footprint backend của RBD. Điều này không đúng, vì guest đang nhìn block/file semantics của hệ điều hành, còn RBD/rbd du đang nhìn allocation và diff state ở tầng object-backed image. Hai số liệu có thể liên quan nhưng không bắt buộc phải trùng. Đây là một trong những insight vận hành quan trọng nhất của RBD.

- Hiểu lầm cuối cùng là coi mirroring, migration hay client cache như “các phần phụ không quan trọng”. Thực ra chúng cho thấy một sự thật rất lớn về RBD: image block trong Ceph không chỉ là đối tượng read/write, mà là một đối tượng có thể clone, mirror, migrate, cache, trash, diff và sống trong những workflow phức tạp của cloud hạ tầng. Hiểu được điều đó là bước chuyển từ “biết dùng RBD” sang “hiểu RBD như một thành phần kiến trúc”.