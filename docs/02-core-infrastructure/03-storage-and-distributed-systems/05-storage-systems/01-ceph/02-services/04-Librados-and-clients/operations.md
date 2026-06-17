# Operations

## Nguyên tắc vận hành

Phần này không phải để dạy viết ứng dụng bằng API librados, mà để giúp người vận hành hiểu và quản được đường vào của client tới Ceph: user CephX, keyring, caps, cấu hình kết nối, và các thao tác object mức thấp bằng rados. Tài liệu kiến trúc của Red Hat nói rất rõ rằng một Ceph client cần tối thiểu địa chỉ monitor hoặc file cấu hình, pool name, user name và đường dẫn tới secret key để làm việc với cluster. Vì vậy, mọi vận hành ở phần này đều xoay quanh bốn thứ đó.

Nguyên tắc quan trọng nhất là: không bao giờ dùng client.admin cho ứng dụng chỉ vì “cho nhanh”. CephX được thiết kế để cấp quyền theo caps, và caps có thể giới hạn tới mức pool, namespace trong pool, hoặc tập pool theo application tags. Nghĩa là nếu một ứng dụng chỉ cần đọc ghi một pool hoặc một namespace, bạn nên tạo user riêng đúng với nhu cầu đó thay vì cấp toàn quyền. Cách làm này vừa an toàn hơn, vừa dễ debug hơn về sau.

Một thói quen vận hành rất nên giữ là: kiểm tra trước, cấp quyền hoặc đổi key sau, rồi xác nhận lại bằng test đọc ghi thật. Với client của Ceph, “tạo user thành công” chưa đủ; phải chứng minh được client thật sự dùng key đó vào được đúng pool, đúng namespace và làm được đúng thao tác mà mình muốn.

2. Tạo user, keyring và caps cho client
Tạo user mới đúng mục đích

Cách tạo user phổ biến nhất là dùng ceph auth get-or-create hoặc ceph auth get-or-create-key. Man page của ceph mô tả rõ:

get-or-create sẽ tạo hoặc trả lại authentication info cho entity cùng với caps
get-or-create-key sẽ tạo hoặc trả lại key cho entity; nếu key đã tồn tại thì caps truyền vào phải khớp với caps hiện có.

Ví dụ, với một ứng dụng direct librados chỉ cần dùng một pool riêng, bạn có thể tạo user theo hướng rất hẹp như sau:

ceph auth get-or-create client.app01 \
  mon 'allow r' \
  osd 'allow rw pool=app-data'

Hoặc nếu bạn chỉ cần lấy key để nhúng vào một hệ thống khác:

ceph auth get-or-create-key client.app01 \
  mon 'allow r' \
  osd 'allow rw pool=app-data'

Tài liệu User Management của Ceph còn chỉ ra rằng caps có thể giới hạn sâu hơn tới namespace trong pool. Đây là điểm rất đáng giá nếu bạn dùng direct librados cho nhiều nhóm dữ liệu logic trong cùng một pool.

Dùng profile khi phù hợp

Tài liệu User Management còn có các profile dựng sẵn. Với direct librados client, profile đáng nhớ nhất là profile simple-rados-client, được mô tả là cấp quyền đọc monitor, OSD và PG ở mức phù hợp cho các ứng dụng dùng librados trực tiếp. Khi nhu cầu đúng với profile có sẵn, dùng profile sẽ gọn và ít sai hơn tự viết caps dài ngay từ đầu.

Ví dụ:

ceph auth get-or-create client.app01 \
  mon 'profile simple-rados-client' \
  osd 'profile simple-rados-client pool=app-data'
Xuất keyring và quản lý keyring

Sau khi tạo user, bạn thường cần xuất keyring cho client node hoặc ứng dụng. Man page của ceph cho biết ceph auth export và ceph auth get có thể xuất keyring, còn ceph auth get-key hoặc print-key có thể in riêng secret key. Tài liệu kiến trúc của Red Hat cũng nhấn mạnh secret key phải được chuyển cho client một cách an toàn.

Ví dụ:

ceph auth get client.app01 -o /etc/ceph/ceph.client.app01.keyring

Nếu cần kiểm tra file keyring, ceph-authtool là công cụ chuẩn để tạo, xem và sửa keyring. Man page của ceph-authtool nói rõ keyring lưu một hoặc nhiều khóa Ceph authentication cùng với capability specification có thể đi kèm. Lệnh hay dùng nhất là:

ceph-authtool -l /etc/ceph/ceph.client.app01.keyring
ceph-authtool -p /etc/ceph/ceph.client.app01.keyring

-l sẽ liệt kê keys và caps trong keyring; -p sẽ in encoded key cho entity được chỉ định.

Sửa caps hoặc xóa user

Khi ứng dụng cần thêm quyền hoặc thu hẹp quyền, dùng ceph auth caps. Man page của ceph mô tả auth caps là lệnh cập nhật caps cho entity. Khi không dùng nữa, có thể xóa hẳn bằng ceph auth del.

Ví dụ:

ceph auth caps client.app01 \
  mon 'allow r' \
  osd 'allow rw pool=app-data namespace=tenant-a'

ceph auth del client.app01

Điểm rất hay sai: sửa caps xong mà không test lại thật. Với CephX, một dấu cách sai hoặc một match-spec quá hẹp cũng đủ làm ứng dụng “vào cluster được nhưng không chạm được dữ liệu”. Vì vậy, sau mỗi lần đổi caps, luôn phải có bước test bằng rados.

3. Kiểm tra kết nối client vào cluster
Kiểm tra bằng ceph CLI

Nếu trên client node có ceph.conf và keyring đúng, cách kiểm tra nhanh nhất là:

ceph -s

Nếu node không có ceph.conf chuẩn, rados man page cho biết bạn có thể chỉ định monitor bằng -m monaddress[:port] thay vì tra qua ceph.conf. Điều này rất hữu ích trong các bài test nhanh hoặc môi trường tối giản.

Ví dụ:

rados -m 10.10.10.11:6789 -n client.app01 --keyring /etc/ceph/ceph.client.app01.keyring lspools
Kiểm tra bằng rados

rados là công cụ object-level rất thực dụng. Man page của rados cho biết nó hỗ trợ:

liệt kê pool
xem dung lượng
put/get/rm object
liệt kê object
benchmark
thao tác omap/xattr
namespace operations ở mức chọn namespace cho object.

Bộ kiểm tra nhanh nên nhớ:

rados lspools
rados df
rados -p app-data ls -

rados lspools và rados df chứng minh client vào được cluster; rados -p <pool> ls - chứng minh client có thể chạm đúng pool.

Test đọc ghi thật bằng object nhỏ

Cách xác nhận tốt nhất luôn là thử put/get/rm với một object nhỏ. Man page của rados còn cảnh báo rất rõ rằng put tạo một RADOS object đơn lẻ có kích thước bằng đúng file đầu vào, nên chỉ nên dùng nó cho test object hợp lý; nếu dữ liệu không có kích thước hợp lý và đồng đều thì nên nghĩ tới RGW/S3, CephFS hoặc RBD thay vì ném file lớn thẳng bằng rados put. Đây là cảnh báo rất đáng giá cho junior.

Ví dụ test:

echo "hello ceph" > /tmp/hello.txt

rados -p app-data put hello-object /tmp/hello.txt
rados -p app-data stat hello-object
rados -p app-data get hello-object /tmp/hello.out
rados -p app-data rm hello-object

Nếu cả bốn bước chạy được, bạn đã xác nhận được đường vào cluster, caps OSD và data path cơ bản của client. stat, get, rm đều là lệnh chuẩn trong man page của rados.

4. Thao tác với object, pool và namespace bằng rados
Làm việc với object cơ bản

Với direct librados style operations, rados là công cụ gần với tư duy object nhất. Các thao tác hay dùng nhất là:

put
get
stat
rm
ls
listwatchers
listxattr, getxattr, setxattr
listomapkeys, listomapvals, getomapval, setomapval

Ví dụ:

rados -p app-data put obj01 /tmp/file.bin
rados -p app-data stat obj01
rados -p app-data listxattr obj01
rados -p app-data rm obj01

Đây là bộ lệnh rất phù hợp để:

xác minh caps của client
kiểm tra object có thật hay không
xem một object có xattr hoặc omap gì
làm test nhỏ trước khi ứng dụng chính thức chạy.
Dùng namespace khi cần tách dữ liệu logic

Tài liệu User Management của Ceph nói rất rõ:

object trong một pool có thể gắn với namespace
quyền truy cập có thể bị giới hạn tới namespace
namespace chỉ khả dụng khi dùng librados.

Còn man page của rados cho biết dùng -N hoặc --namespace để chỉ định namespace cho object, và --all với ls để liệt kê object ở mọi namespace.

Ví dụ:

rados -p app-data -N tenant-a put obj01 /tmp/file.bin
rados -p app-data -N tenant-a ls -
rados -p app-data --all ls -

Đây là capability rất hay cho các ứng dụng direct librados: bạn không cần tạo pool mới cho mọi tenant hoặc mọi nhóm dữ liệu logic, nhưng vẫn có thể tách namespace và cấp quyền theo namespace. Tài liệu Ceph còn giải thích lý do dùng namespace là vì namespace rẻ hơn pool về mặt chi phí tính toán và quản trị.

Đọc object từ snapshot của pool

Man page của rados nói -s hoặc --snap cho phép đọc từ pool snapshot trong các thao tác đọc của pool. Ví dụ trong docs:

rados -p foo mksnap mysnap
rados -p foo -s mysnap get myobject blah.txt.old

Điều này hữu ích trong các bài test hoặc kiểm tra dữ liệu object-level từ snapshot của pool.

5. Quản lý keyring và phân phối key an toàn
Khi nào dùng ceph auth và khi nào dùng ceph-authtool

ceph auth là nơi bạn tạo, xuất, sửa, xóa authentication info trong cluster. ceph-authtool là nơi bạn tạo, xem và sửa file keyring ở phía client. Đây là hai lớp khác nhau và không nên lẫn. Man page của ceph mô tả rõ các lệnh auth add, auth caps, auth del, auth export, auth get, auth get-or-create, auth get-or-create-key. Man page của ceph-authtool mô tả rõ nó là công cụ thao tác file keyring.

Kiểm tra keyring trước khi giao cho ứng dụng

Trước khi đưa keyring cho ứng dụng hoặc cho một host client mới, nên kiểm tra lại:

entity name có đúng không
caps có đúng không
file permission có an toàn không
keyring chỉ chứa đúng những entity cần thiết.

Ví dụ:

ceph-authtool -l /etc/ceph/ceph.client.app01.keyring

Nếu cần gộp nhiều keyring hoặc thêm caps trong file keyring cục bộ, ceph-authtool hỗ trợ --import-keyring và --cap theo đúng man page.

Quy tắc an toàn khi xoay key

Khi cần xoay key cho một ứng dụng:

tạo hoặc xuất key mới
cập nhật ứng dụng hoặc host client
test kết nối thật bằng rados
chỉ khi đã xác nhận ổn mới xóa key/user cũ hoặc thu hẹp caps cũ.

Đừng làm ngược thứ tự. Với direct client, keyring sai hoặc caps sai thường làm ứng dụng lỗi ngay ở lúc khởi tạo kết nối hoặc lúc chạm vào pool/object đầu tiên. Cách xoay key an toàn luôn là song song một thời gian ngắn rồi cắt cái cũ sau, nếu workflow của bạn cho phép.

6. Kiểm tra định kỳ và các việc nên làm thường xuyên

Với phần librados and clients, những việc nên kiểm tra định kỳ không nhiều, nhưng rất đáng giữ:

danh sách user và caps đang cấp có còn đúng không
ứng dụng nào đang dùng client.admin sai mục đích
keyring có bị phát tán quá rộng không
các bài test nhỏ bằng rados còn chạy được không sau khi đổi config, đổi mạng hoặc đổi MON endpoints.

Bộ lệnh gọn cho một lần rà soát:

ceph auth ls
ceph auth get client.app01
rados lspools
rados -p app-data ls -

Nếu bạn nghi có vấn đề với client-level access sau một thay đổi cấu hình, test put/get/rm một object nhỏ vẫn là cách xác nhận nhanh và đáng tin nhất. Nó tốt hơn nhiều so với việc chỉ nhìn ceph -s vì ceph -s chứng minh cluster sống, còn rados put/get mới chứng minh client thật sự dùng đúng key, đúng caps và đúng data path.

Ý chốt của file này:
Vận hành tốt phần librados and clients không phải là thuộc API lập trình, mà là quản được danh tính client, keyring, caps, và bài test object-level để chứng minh client thật sự vào được cluster đúng cách. Khi quản tốt phần này, rất nhiều vấn đề ở RBD, RGW, CephFS và các tích hợp khác sẽ dễ nhìn hơn ngay từ đầu.