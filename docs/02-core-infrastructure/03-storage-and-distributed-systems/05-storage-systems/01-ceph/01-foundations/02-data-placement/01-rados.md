# RADOS
## 1. RADOS là gì

RADOS là viết tắt của Reliable Autonomic Distributed Object Store. Đây là lớp lưu trữ đối tượng phân tán nằm ở trung tâm của Ceph, và cũng là nền mà mọi giao diện lưu trữ khác của Ceph dựa vào. Tài liệu Ceph Pacific và RHCS 5/8 đều thống nhất rằng dù người dùng có truy cập Ceph dưới dạng block, file hay object, thì sâu bên dưới các giao diện đó vẫn là RADOS đang thực hiện lưu trữ và phân phối dữ liệu trong cụm.

Nói ngắn gọn, nếu Ceph là một hệ lưu trữ hợp nhất, thì RADOS chính là lõi lưu trữ thống nhất của hệ đó. RBD, CephFS và RGW chỉ là những cách khác nhau để trình bày cùng một nền lưu trữ cho ứng dụng. Chính vì vậy, file về RADOS không nên bị hiểu là “thêm một dịch vụ riêng nữa”, mà phải được hiểu là lớp nền tảng nhất của Ceph.

## 2. Vì sao Ceph cần RADOS

Ceph được xây dựng để tránh mô hình lưu trữ tập trung kiểu cũ, nơi một thành phần trung tâm vừa giữ vị trí dữ liệu vừa đứng giữa mọi thao tác đọc ghi. Pacific Architecture giải thích rằng trong kiến trúc truyền thống, client thường phải nói chuyện với một thành phần tập trung như gateway hoặc broker, tạo ra điểm nghẽn hiệu năng và điểm lỗi đơn. Ceph loại bỏ mô hình đó bằng cách để client và daemon dùng cùng một cơ chế tính toán placement, từ đó đi trực tiếp tới nơi dữ liệu nằm. RADOS là lớp làm cho điều đó trở thành hiện thực.

Vì vậy, RADOS tồn tại để giải quyết đồng thời bốn yêu cầu lớn của Ceph:

lưu dữ liệu dưới dạng đối tượng
phân phối dữ liệu trên nhiều node
bảo vệ dữ liệu bằng nhân bản hoặc mã xóa
cho phép client truy cập dữ liệu mà không cần một bảng tra cứu tập trung cho từng đối tượng.

Nếu chỉ hiểu Ceph là “một cụm OSD”, bạn sẽ bỏ sót phần quan trọng nhất: OSD chỉ là daemon thực thi, còn RADOS mới là mô hình lưu trữ phân tán khiến các daemon đó có thể hoạt động như một hệ thống thống nhất.

## 3. Bản chất của RADOS: vừa là dịch vụ lưu trữ, vừa là giao thức lõi

RADOS có hai lớp nghĩa cần phân biệt rõ. Thứ nhất, nó là dịch vụ lưu trữ đối tượng phân tán của Ceph. Thứ hai, nó cũng là giao thức lõi mà mọi Ceph client dùng để tương tác với cụm lưu trữ. RHCS 5 Architecture Guide nói rất rõ rằng tất cả Ceph clients đều dùng giao thức RADOS để tương tác với cụm Red Hat Ceph Storage, bất kể giao diện phía trên là block, file hay object.

Điều này giúp giải thích một điểm rất quan trọng: khi nói “RBD”, “CephFS” hay “RGW”, bạn đang nói về lớp truy cập; còn khi nói “RADOS”, bạn đang nói về lớp lưu trữ thực sự và ngôn ngữ chung mà các lớp truy cập đó cuối cùng phải nói với cluster. Nói cách khác, RADOS vừa là nền lưu trữ, vừa là ngôn ngữ nội bộ chung của Ceph.

## 4. RADOS lưu dữ liệu như thế nào

Pacific Architecture mô tả rất rõ rằng cụm Ceph nhận dữ liệu từ các Ceph clients và lưu dữ liệu đó dưới dạng RADOS objects. Mỗi object được lưu trên một Object Storage Device, và các Ceph OSD Daemons chịu trách nhiệm đọc, ghi và nhân bản dữ liệu trên các thiết bị lưu trữ đó. Đồng thời, các object trong RADOS tồn tại trong một không gian tên phẳng, tức là không có cấu trúc thư mục như filesystem truyền thống. Một object gồm ba phần cơ bản: định danh object, dữ liệu nhị phân và metadata đi kèm dưới dạng cặp tên/giá trị.

Điểm này cực kỳ quan trọng vì nó cho thấy RADOS không nghĩ theo mô hình “file trên filesystem” ở tầng lõi. Dù ứng dụng nhìn thấy block device, bucket S3 hay file POSIX, thì sâu bên dưới dữ liệu vẫn được biểu diễn thành các object và được quản lý theo logic của object store phân tán. Điều này cũng là nền để Ceph có thể hợp nhất block, file và object trong cùng một hệ.

### Minh họa tư duy lưu trữ của RADOS
```
Ứng dụng / Client
      ↓
Giao diện truy cập (RBD / CephFS / RGW / librados)
      ↓
RADOS object
      ↓
Pool
      ↓
Placement Group
      ↓
OSD
      ↓
Thiết bị lưu trữ vật lý
```

> Keynote: Cái mạnh nhất của RADOS không chỉ là “lưu object”, mà là lưu object theo cách phân tán mà không cần một bộ điều phối vị trí dữ liệu trung tâm cho từng I/O. Đó mới là chỗ Ceph khác biệt sâu sắc. Object không được tìm bằng một bảng tra cứu tập trung, mà được client và daemon tự tính ra từ map và CRUSH. Đây là một trong những ý quan trọng nhất của toàn bộ Ceph.
## 5. RADOS và các daemon cốt lõi

Tài liệu librados của Ceph nói rõ rằng API librados tương tác trực tiếp với hai loại daemon trong cụm Ceph Storage Cluster:

Ceph Monitor, nơi giữ bản sao chủ của Cluster Map
Ceph OSD Daemon, nơi lưu dữ liệu dưới dạng object trên node lưu trữ.

Điều này giúp nhìn RADOS rõ hơn ở góc hệ thống:

MON giữ trạng thái logic của cụm
OSD giữ dữ liệu thực
RADOS là lớp nối hai phần đó lại thành một hệ lưu trữ đối tượng phân tán có thể dùng được bởi client.

Nếu cần diễn đạt thật ngắn:
RADOS là mô hình lưu trữ phân tán; MON giữ trạng thái để mô hình đó hoạt động nhất quán; OSD thực thi mô hình đó trên dữ liệu thật.

## 6. RADOS và khả năng mở rộng của Ceph

Một trong những ưu điểm lớn nhất của RADOS là nó cho phép Ceph mở rộng mà không cần một bảng tra cứu tập trung cho từng object. Pacific Architecture giải thích rằng cả client lẫn OSD đều dùng thuật toán CRUSH để tính vị trí object một cách hiệu quả thay vì phụ thuộc vào một bảng tra cứu trung tâm. Nhờ đó, công việc định vị dữ liệu được phân tán ra tất cả client và OSD trong cụm, thay vì dồn vào một điểm trung tâm.

Đây là lý do vì sao RADOS mang tính distributed đúng nghĩa. Dữ liệu phân tán trên nhiều node, nhưng quan trọng hơn, cả trách nhiệm tính placement cũng được phân tán. Chính điều này làm cho Ceph scale-out tốt hơn các mô hình lưu trữ có bộ điều phối vị trí dữ liệu tập trung.

## 7. RADOS và ba lớp truy cập chính của Ceph

Squid Beginner’s Guide nói một câu rất đáng nhớ: Ceph có nhiều “storage interfaces”, gồm CephFS, RBD và RADOS, nhưng sâu bên dưới thì cả ba thực chất đều là RADOS object stores; CephFS và RBD chỉ đang tự trình bày mình như filesystem và block device. Đây là cách diễn đạt rất hay cho người học, vì nó buộc ta phải quay về bản chất thay vì bị cuốn theo giao diện bề ngoài.

RHCS 5 client components cũng đồng nhất với cách hiểu đó: client có thể khác nhau nhiều về cách trình bày dữ liệu, nhưng tất cả đều dùng giao thức RADOS để tương tác với cụm. Vì vậy, nếu không hiểu RADOS, thì hiểu biết về RBD, CephFS hay RGW sẽ rất dễ bị rơi vào kiểu “biết chức năng nhưng không hiểu nền”.

> Keynote: RADOS không phải là “một loại giao diện object khác bên cạnh RBD và CephFS”, mà là lõi lưu trữ thật sự của toàn bộ Ceph. Đây là điểm cực kỳ quan trọng. RBD, CephFS và RGW là các lớp truy cập; còn RADOS là nơi dữ liệu thực sự sống, được phân phối, bảo vệ và phục hồi. Một khi đã hiểu điều này, bạn sẽ thấy block, file và object trong Ceph không phải ba backend khác nhau, mà là ba kiểu trình bày khác nhau trên cùng một object backend.
## 8. RADOS và librados

- librados là**thư viện mức thấp cho phép ứng dụng truy cập trực tiếp vào RADOS.** Tài liệu Introduction to librados nói rõ rằng librados cho phép bạn tạo giao diện riêng của mình tới Ceph Storage Cluster, thay vì chỉ dùng các giao diện REST, block hay POSIX có sẵn. Điều này có nghĩa RADOS không chỉ là nền cho các dịch vụ của Ceph, mà còn là nền để lập trình viên tự xây dựng ứng dụng làm việc trực tiếp với object store phân tán.

- Đây là một điểm rất đáng chú ý về kiến trúc: Ceph không khóa người dùng vào một giao diện duy nhất. RADOS là lớp đủ cơ bản để có thể trở thành nền cho cả sản phẩm của Ceph lẫn ứng dụng tùy chỉnh của người dùng. Điều đó cũng giải thích vì sao nhiều tài liệu của Ceph luôn xem librados là “cửa sổ” nhìn thẳng vào RADOS.

## 9. Bốn ý nghĩa trong tên gọi RADOS

- Tên gọi Reliable Autonomic Distributed Object Store không chỉ là một cụm từ đẹp, mà phản ánh đúng bốn đặc tính cốt lõi của lớp này.

- RADOS là Reliable vì dữ liệu không dựa vào một bản duy nhất; nó được bảo vệ bằng nhân bản hoặc mã xóa và có các cơ chế phục hồi khi thành phần lưu trữ gặp lỗi. RHCS Architecture Guide nhấn mạnh rằng các OSD sử dụng tài nguyên CPU, bộ nhớ và mạng để thực hiện nhân bản dữ liệu, mã xóa, tái cân bằng, phục hồi, giám sát và báo cáo.

- RADOS là Autonomic vì nhiều hành vi nền của cụm diễn ra tự động, như giám sát, phát hiện lỗi, phục hồi và tái phân phối dữ liệu. Điều này không có nghĩa cluster “tự làm được mọi thứ mà không cần quản trị”, mà có nghĩa nhiều cơ chế quan trọng đã được đưa vào bản thân mô hình lưu trữ thay vì để người quản trị thao tác thủ công từng phần.

- RADOS là Distributed vì dữ liệu và trách nhiệm xử lý không bị dồn vào một máy hay một điểm điều phối trung tâm. Pacific Architecture nhấn mạnh rằng Ceph loại bỏ thành phần tập trung và phân phối công việc tính placement cho cả client lẫn OSD.

- RADOS là Object Store vì ở tầng lõi, dữ liệu được lưu dưới dạng object với định danh, dữ liệu nhị phân và metadata, thay vì dưới dạng file hệ điều hành truyền thống.


## Kết luận 
- Các điểm mấu chốt cần nắm :
      - RADOS là lõi lưu trữ đối tượng phân tán của Ceph
      - mọi giao diện truy cập cuối cùng đều dựa trên RADOS
      - client lấy Cluster Map rồi dùng CRUSH để tính placement
      - `MON` và `OSD` là hai loại daemon nền mà librados tương tác trực tiếp.
- Những hiểu lầm phổ biến về RADOS
      - Hiểu lầm phổ biến nhất là coi RADOS như một “dịch vụ object riêng biệt” nằm cạnh RBD, CephFS và RGW. Cách hiểu đó sai. RADOS không phải “một giao diện nữa” ngang hàng với các giao diện kia; nó là nền lõi mà các giao diện đó xây trên. Squid Beginner’s Guide nói rất rõ rằng sâu bên dưới, cả CephFS và RBD thực chất đều là RADOS object stores.
      > Mặc dù người dùng có thể nhìn Ceph theo 3 kiểu khác nhau : block device ( RBD), filesystem (CephFS) hoặc object storage (RGW), nhưng sâu bên dưới tất cả đều là RADOS object store. CephFS và RBD chỉ đang tự trình bày mình như filesystem và block device, nhưng thực chất vẫn là RADOS object store. RBD là cái ổ đĩa block mà VM thấy thực ra được chia thành rất nhiều object nhỏ trong RADOS, CephFS thì file và thư mục người dùng thấy , phần metadata và file data cuối cùng vẫn được lưu trong RADOS pools dưới dạng object. RGW thì đơn giản hơn, nó chỉ là một giao diện RESTful để truy cập trực tiếp vào RADOS object store.

      - Hiểu lầm thứ hai là nghĩ rằng muốn tìm dữ liệu trong RADOS thì phải hỏi một bảng tra cứu tập trung. Pacific Architecture nói rất rõ điều ngược lại: client và OSD dùng CRUSH để tính vị trí object thay vì phụ thuộc vào một bảng tra cứu trung tâm. Nếu không hiểu điểm này, sẽ rất khó hiểu vì sao Ceph có thể mở rộng tốt.

      - Hiểu lầm thứ ba là tưởng rằng RADOS đồng nghĩa với lệnh rados trên dòng lệnh. Thực ra lệnh rados chỉ là một tiện ích để tương tác với Ceph object storage cluster; nó không phải là bản thân RADOS. Tức là rados là công cụ, còn RADOS là lớp lưu trữ và giao thức lõi.
