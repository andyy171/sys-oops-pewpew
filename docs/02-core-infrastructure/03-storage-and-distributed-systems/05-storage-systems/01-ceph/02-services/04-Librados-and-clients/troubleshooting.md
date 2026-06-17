# Troubleshooting 

## Cách nghĩ đúng khi debug phần client của Ceph

Khi một ứng dụng hoặc một lệnh rados không làm việc được với Ceph, đừng vội kết luận là cluster hỏng. Với phần librados and clients, lỗi thường rơi vào một trong bốn tầng: kết nối tới MON, CephX và keyring, caps không đủ hoặc sai phạm vi pool/namespace, hoặc cluster-level issue ở phía dưới. Tài liệu Red Hat mô tả rất rõ rằng client cần tối thiểu file cấu hình hoặc tên cluster kèm địa chỉ monitor, tên pool, user name và đường dẫn tới secret key để làm việc với cluster; nghĩa là thiếu hoặc sai bất kỳ mắt xích nào trong bốn thứ đó đều đủ làm client hỏng.

Bộ kiểm tra nhanh nên chạy đầu tiên gần như luôn là:

ceph -s
ceph health detail
ceph auth get client.<name>
ceph-authtool -l /etc/ceph/ceph.client.<name>.keyring

ceph -s và ceph health detail giúp xác nhận cluster còn sống và có health check gì lớn không. ceph auth get cho biết entity đó còn tồn tại trong cluster và đang có caps gì. ceph-authtool -l giúp kiểm tra file keyring thực tế trên máy client có đúng entity và key hay không. ceph-authtool được Ceph mô tả là công cụ để tạo, xem và sửa file keyring, còn ceph là công cụ quản trị cluster và auth.

Điểm phải nhớ:
Nếu chưa xác định được lỗi nằm ở tầng nào, đừng sửa bừa caps hoặc xóa user ngay. Với phần client, cách an toàn nhất là đi từ kết nối → xác thực → phân quyền → thử đọc ghi thật bằng rados.

2. Lỗi không kết nối được tới cluster hoặc báo không tìm thấy monitor

Nếu rados hay ứng dụng báo kiểu “không kết nối được cluster”, “không tìm thấy monitor”, hoặc ceph -s đứng rất lâu, hướng nghĩ đầu tiên phải là: client không có đủ thông tin MON hoặc không đọc được cấu hình kết nối. Red Hat ghi rõ client cần file cấu hình Ceph hoặc tên cluster và địa chỉ monitor; man page của rados cũng ghi rõ có thể chỉ định monitor trực tiếp bằng -m monaddress[:port] thay vì phụ thuộc hoàn toàn vào ceph.conf.

Cách kiểm tra nên đi từ đơn giản nhất:

ceph -s
rados -m <mon-ip>:6789 lspools

Nếu ceph -s lỗi mà rados -m ... lspools lại chạy được, rất có thể vấn đề nằm ở file cấu hình local chứ không phải cluster chết. Nếu cả hai đều không chạy được, phải nhìn tiếp mạng tới MON hoặc tình trạng MON daemon. Ceph docs về monitor troubleshooting và man page ceph-mon đều nhấn mạnh cần chắc chắn monitor đang chạy và có quorum trước khi debug sâu hơn.

Điểm rất hay sai:
Junior hay nhảy ngay sang nghi keyring sai, trong khi thực tế client còn chưa nói chuyện được với MON. Với nhóm lỗi này, luôn xác minh đường tới MON trước khi đụng vào CephX.

3. Lỗi CephX: keyring sai, user không tồn tại, hoặc secret key không khớp

Nếu client nói chuyện được với MON nhưng vẫn bị từ chối, hướng nghĩ tiếp theo phải là CephX đang sai. Ceph docs về User Management mô tả user Ceph là danh tính xác thực ở tầng cluster; docs về ceph-authtool nói keyring chứa một hoặc nhiều khóa Ceph auth kèm caps có thể có; còn auth config reference nhấn mạnh CephX là cơ chế xác thực và bảo vệ cluster khỏi sửa đổi thông điệp ở giữa đường truyền. Nghĩa là nếu entity name, secret key hoặc file keyring sai, client có thể vào tới MON nhưng vẫn không được phép làm gì tiếp.

Bộ lệnh nên dùng để đối chiếu là:

ceph auth get client.app01
ceph-authtool -l /etc/ceph/ceph.client.app01.keyring
ceph-authtool -p /etc/ceph/ceph.client.app01.keyring

Ở đây, ceph auth get cho biết cluster đang giữ auth info gì cho entity đó; ceph-authtool -l cho biết file keyring local đang chứa entity nào; -p in key từ keyring để bạn đối chiếu khi cần. Nếu keyring local không đúng entity hoặc key không khớp với auth info trên cluster, đó chính là gốc lỗi.

Nếu cần cấp lại key hoặc tạo lại auth info đúng chuẩn, dùng:

ceph auth get-or-create client.app01 \
  mon 'allow r' \
  osd 'allow rw pool=app-data' \
  -o /etc/ceph/ceph.client.app01.keyring

get-or-create là lệnh chính thức của ceph để tạo hoặc lấy lại auth info cho entity cùng caps đi kèm.

Điểm rất hay sai:
Nhiều người thấy lỗi auth là xóa user rồi tạo lại ngay. Cách an toàn hơn là so auth info trên cluster với keyring local trước. Rất nhiều case chỉ là copy nhầm keyring hoặc keyring cũ chưa được cập nhật.

4. Vào được cluster nhưng không chạm được pool hoặc object

Đây là nhóm lỗi rất hay gặp và cũng rất dễ làm người mới rối. Dấu hiệu điển hình là:

ceph -s chạy được
rados lspools chạy được
nhưng rados -p <pool> ls hoặc put/get/rm lại lỗi

Khi gặp tình huống này, hướng nghĩ đúng là: CephX đã đúng ở mức kết nối, nhưng caps không đủ hoặc không đúng phạm vi. Tài liệu User Management nói rõ caps có thể giới hạn quyền ở mức monitor, OSD, pool, namespace trong pool, hoặc nhóm pool theo application tags. Nghĩa là một user hoàn toàn có thể “vào cluster được” nhưng vẫn không được đọc ghi đúng pool mà ứng dụng cần.

Cách kiểm tra:

ceph auth get client.app01
rados lspools
rados -p app-data ls -

Nếu lspools chạy được nhưng rados -p app-data ls - lỗi, gần như chắc chắn phải nhìn lại osd caps của user. Ví dụ đúng kiểu giới hạn pool thường là:

ceph auth caps client.app01 \
  mon 'allow r' \
  osd 'allow rw pool=app-data'

Ceph docs mô tả rõ cú pháp caps và khả năng giới hạn theo pool.

Điểm rất hay sai:
Thấy ceph -s chạy được rồi tưởng auth đã ổn hoàn toàn. Không đúng. ceph -s chỉ chứng minh được phần monitor access ở mức nào đó; còn data path vào pool vẫn phụ thuộc mạnh vào osd caps.

5. Lỗi do namespace: client vào đúng pool nhưng vẫn không thấy object cần thấy

Namespace là chỗ rất dễ bị quên vì nó chỉ lộ rõ khi dùng direct librados hoặc rados. Tài liệu User Management của Ceph nói rõ có thể hạn chế truy cập theo namespace trong pool, và đây là khả năng chỉ khả dụng với librados; man page của rados cho biết -N hoặc --namespace dùng để chỉ định namespace, còn --all với ls cho phép nhìn object ở mọi namespace.

Triệu chứng rất hay gặp là:

put thành công ở một chỗ
ls ở một chỗ khác lại không thấy object
hoặc ứng dụng nói “mất object” trong khi thực ra object đang ở namespace khác

Cách kiểm tra:

rados -p app-data -N tenant-a ls -
rados -p app-data --all ls -
ceph auth get client.app01

Nếu --all nhìn thấy object còn -N tenant-a không thấy, bạn đang đứng sai namespace. Nếu object nằm đúng namespace nhưng user vẫn không thấy, hãy nhìn lại caps kiểu:

ceph auth caps client.app01 \
  mon 'allow r' \
  osd 'allow rw pool=app-data namespace=tenant-a'

Ceph docs cũng nói rõ namespace có thể dùng như một lớp phân tách logic rẻ hơn việc tạo pool mới cho từng nhóm dữ liệu.

Điểm rất hay sai:
Junior thường chỉ kiểm tra pool mà quên namespace. Với direct client, đó là sai lầm rất thường gặp. Quy tắc nên nhớ là: vào được pool nhưng không thấy dữ liệu thì phải nghĩ ngay đến namespace.

6. rados put/get/rm lỗi hoặc hành vi không như mong đợi

rados là công cụ test rất mạnh vì nó chạm gần trực tiếp vào RADOS. Nhưng cũng vì vậy mà nhiều hiểu nhầm xảy ra ở đây. Man page của rados nói rất rõ rados put sẽ tạo một object đơn lẻ có kích thước bằng đúng file đầu vào. Docs còn cảnh báo nếu dữ liệu không có kích thước hợp lý và đồng đều thì không nên đẩy thẳng kiểu đó, mà nên cân nhắc RGW/S3, CephFS hoặc RBD.

Nếu put/get/rm lỗi, hãy đi theo thứ tự:

kiểm tra kết nối cluster
kiểm tra auth và caps
kiểm tra đúng pool chưa
kiểm tra namespace nếu có
mới nghĩ tới cluster-level issue

Bộ test nhỏ chuẩn nên là:

echo "hello ceph" > /tmp/hello.txt
rados -p app-data put hello-object /tmp/hello.txt
rados -p app-data stat hello-object
rados -p app-data get hello-object /tmp/hello.out
rados -p app-data rm hello-object

Nếu stat được mà get hoặc rm không được, gần như chắc chắn bạn cần nhìn lại quyền ở tầng OSD caps hoặc tình trạng cluster phía dưới. rados stat, get, rm, put đều là lệnh chuẩn trong man page của rados.

Điểm rất hay sai:
Dùng rados put cho file lớn rồi kết luận Ceph “không tối ưu”. rados là công cụ object-level để test và thao tác quản trị, không phải con đường đúng cho mọi kiểu dữ liệu của ứng dụng.

7. Keyring đúng, caps đúng, nhưng ứng dụng vẫn lỗi

Nếu bạn đã xác nhận:

MON reachable
user tồn tại
keyring đúng
caps nhìn có vẻ đủ

mà ứng dụng vẫn lỗi, lúc này phải quay lại đúng kiểu client path. Tài liệu API của Ceph nói rõ mọi Ceph client hoặc dùng trực tiếp librados hoặc dùng cùng chức năng được gói trong librados; Red Hat cũng nhấn mạnh các client khác nhau có cùng nhu cầu nền như config file, monitor address, pool name, user name và secret key path. Điều đó nghĩa là direct rados test chạy được chưa chắc service-level client như librbd, libcephfs hay một ứng dụng có logic riêng sẽ chạy ngay y như vậy.

Với nhóm lỗi này, cách nghĩ đúng là: tầng CephX có thể đã ổn, nhưng đường client cụ thể của ứng dụng còn yêu cầu thêm thứ khác. Ví dụ:

ứng dụng trỏ nhầm pool
ứng dụng dùng namespace khác
ứng dụng cần caps rộng hơn một chút so với bài test rados
ứng dụng cache config/keyring cũ

Vì vậy, khi direct rados test chạy được mà ứng dụng vẫn hỏng, đừng phá auth vội. Hãy dùng bài test object-level như một mốc để nói: đường vào Ceph cơ bản đã đúng, giờ cần nhìn lại client path của chính ứng dụng.

8. Khi nào phải dừng ở mức client và đẩy xuống cluster-level

Có những dấu hiệu cho thấy lỗi đã vượt khỏi phạm vi librados and clients:

ceph health detail báo health check lớn
nhiều client khác nhau cùng lỗi
rados test object-level cũng lỗi trên nhiều host
cluster nearfull, backfillfull, full
MON không quorum hoặc OSD path rõ ràng có vấn đề

Ceph health checks docs mô tả rõ các health state là tín hiệu chính thức của cluster; Red Hat architecture guide cũng nhấn mạnh client cần MON để lấy cluster map, nên nếu MON layer hoặc OSD layer có vấn đề thì không thể mong client path ổn định.

Khi gặp các dấu hiệu đó, hãy dừng debug ở mức keyring/caps và chuyển sang:

ceph -s
ceph health detail
ceph osd perf
nếu cần thì kiểm tra MON/OSD daemon trạng thái

Với phần client, biết lúc nào không còn là lỗi client nữa quan trọng không kém biết chỉnh caps thế nào.

9. Ý chốt của file này

Phần librados and clients hay bị xem là “đơn giản, chỉ là auth với keyring”, nhưng thực tế đây là nơi rất nhiều lỗi nền tảng xuất phát. Muốn debug tốt phần này, hãy luôn đi theo đúng thứ tự:

kết nối tới MON
CephX và keyring
caps theo pool/namespace
thử đọc ghi thật bằng rados
nếu vẫn lỗi thì mới đẩy xuống cluster-level hoặc client-path cụ thể

Nếu phải nhớ file này bằng một câu, hãy nhớ: client của Ceph hiếm khi hỏng vì một thứ duy nhất; gần như luôn phải kiểm tra đồng thời kết nối, xác thực, phân quyền và bài test object-level thật.