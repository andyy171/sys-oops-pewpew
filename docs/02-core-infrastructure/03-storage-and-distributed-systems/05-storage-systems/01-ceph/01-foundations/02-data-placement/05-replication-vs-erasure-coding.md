# Replication và Erasure Coding
1. Hai cách bảo vệ dữ liệu của Ceph

Trong Ceph, dữ liệu ở tầng lõi luôn nằm trong các pool, nhưng cách Ceph bảo vệ dữ liệu trong pool có thể đi theo hai hướng rất khác nhau: replication hoặc erasure coding. Với replicated pool, mỗi object được sao chép thành nhiều bản đầy đủ trên nhiều OSD. Với erasure-coded pool, mỗi object được chia thành K data chunks và M coding chunks, rồi các chunk này được đặt lên các OSD khác nhau. Ceph docs và RHCS docs đều nhất quán rằng đây là hai cơ chế durability chính của cluster.

Điểm cần hiểu ngay từ đầu là đây không chỉ là bài toán tiết kiệm dung lượng. Replication và erasure coding khác nhau ở chính mô hình ghi, mô hình phục hồi, số lượng failure domain cần có, chi phí CPU và độ phù hợp với từng kiểu workload. Nếu chỉ nhớ “replication tốn dung lượng hơn, EC tiết kiệm hơn” thì vẫn chưa nắm được bản chất.

Ghi chú cốt lõi:
Replication và erasure coding không phải hai cách “lưu cùng một thứ theo hai định dạng khác nhau”, mà là hai cách Ceph đánh đổi giữa đơn giản của đường ghi, chi phí dung lượng, độ phức tạp phục hồi và kiểu workload phù hợp. Replication thiên về sự đơn giản và độ trễ dễ đoán hơn; erasure coding thiên về hiệu quả dung lượng nhưng phải trả giá bằng đường I/O và phục hồi phức tạp hơn.

2. Replication: lưu nhiều bản sao đầy đủ

Với replicated pool, Ceph bảo vệ dữ liệu bằng cách lưu nhiều bản sao hoàn chỉnh của cùng một object. Tài liệu Ceph mô tả replicated pool là kiểu pool mặc định, trong đó mỗi object được copy tới nhiều đĩa. Ở mức kiến trúc, client tính ra PG và primary OSD; sau đó primary OSD nhận mọi thao tác ghi và phối hợp ghi replica tới các secondary OSDs trong acting set. Cách làm này giúp đường ghi tương đối dễ hiểu: một object logic được biến thành nhiều bản sao đầy đủ.

Điểm mạnh lớn nhất của replication là tính trực quan và tính ổn định về hành vi. Mỗi replica là một bản hoàn chỉnh của object, nên khi một replica mất hoặc lạc nhịp, cluster có thể phục hồi bằng cách sao chép lại từ replica còn tốt. Đây là lý do replicated pool thường phù hợp hơn cho các workload cần độ trễ thấp, nhiều ghi ngẫu nhiên nhỏ, metadata dày, hoặc các lớp truy cập như block storage nơi hành vi ghi đè và cập nhật một phần object xảy ra thường xuyên.

Cách hiểu đúng về replicated pool
size = 3 nghĩa là Ceph muốn có ba bản sao hoàn chỉnh của object.
min_size là ngưỡng tối thiểu để Ceph còn chấp nhận ghi an toàn khi cluster đang suy giảm.
độ bền thực tế không chỉ phụ thuộc vào số replica, mà còn phụ thuộc vào CRUSH rule và failure domain xem các replica có thực sự tách nhau về rủi ro hay không.

Ghi chú cốt lõi:
Replication không chỉ là “copy nhiều bản”. Nó là cách Ceph biến một object logic thành nhiều bản đầy đủ, dễ hiểu, dễ phục hồi. Vì mỗi replica tự nó đã là dữ liệu hoàn chỉnh, replicated pool thường là lựa chọn an toàn và đơn giản hơn khi cần hành vi ghi đè, cập nhật nhỏ lẻ và phục hồi dễ dự đoán.

3. Erasure Coding: chia object thành data chunks và coding chunks

Erasure coding bảo vệ dữ liệu theo cách khác hẳn. Thay vì lưu nhiều bản đầy đủ, Ceph chia mỗi object thành K data chunks và tạo thêm M coding chunks, rồi đặt tổng cộng K+M chunks đó lên các OSD khác nhau. Ceph docs mô tả đây là cơ chế dùng các phần parity/coding để dựng lại dữ liệu khi một số chunks bị mất hoặc hỏng. Mức chịu lỗi phụ thuộc trực tiếp vào M: nếu mất tối đa M chunks mà các chunk còn lại vẫn đủ, cluster vẫn có thể tái tạo object.

Ưu điểm lớn nhất của erasure coding là hiệu quả dung lượng. RHCS docs đưa ví dụ rất rõ: một cấu hình như 8+3 có thể cho mức dư thừa tương đương 3-way replication nhưng chỉ dùng khoảng 1.5x dung lượng logic thay vì 3x. Ceph docs về profile mặc định cũng cho ví dụ k=2, m=2: để lưu 1 TB dữ liệu cần khoảng 2 TB raw storage, thay vì 3 TB nếu replicated size 3. Điều này làm EC đặc biệt hấp dẫn cho dữ liệu lớn, lưu lâu, ít sửa đổi, hoặc các workload object/cold data.

Nhưng lợi thế dung lượng đó không miễn phí. RHCS và Ceph đều nhấn mạnh EC tốn CPU hơn, đường ghi và phục hồi phức tạp hơn, và thường đòi hỏi nhiều failure domains hơn replication để placement đúng nghĩa. K+M không chỉ là công thức mã hóa; nó còn là yêu cầu về số vị trí mà cluster phải có khả năng đặt các chunks ra đủ rộng.

Điều cần nhớ về EC pool
K là số data chunks.
M là số coding chunks, cũng là số chunks có thể mất mà vẫn dựng lại dữ liệu được.
tổng số chunk là K+M, và đây cũng là số OSD mục tiêu trong acting set của object đó.
profile EC không thể sửa trực tiếp sau khi pool đã được tạo; nếu cấu hình sai, thường phải tạo pool mới và di chuyển dữ liệu.

Ghi chú cốt lõi:
Erasure coding không phải “replication nhưng thông minh hơn”. Nó là một mô hình bảo vệ dữ liệu khác hẳn: thay vì giữ nhiều bản hoàn chỉnh, Ceph giữ một tập mảnh dữ liệu và mảnh mã hóa đủ để dựng lại object. Vì vậy, EC mạnh ở chỗ tiết kiệm dung lượng, nhưng cũng kéo theo cách nghĩ khác về ghi, đọc, phục hồi và topology cần có.

4. Đường ghi: replication và EC khác nhau ở đâu

Ở replicated pool, primary OSD nhận write và gửi bản sao hoàn chỉnh của object tới các secondary OSDs. Mô hình này tương đối thẳng: một object logic được copy nguyên bản nhiều lần.

Ở erasure-coded pool, primary OSD vẫn là điểm vào của write path, nhưng thay vì gửi full replicas, nó phải tham gia quá trình tạo K+M chunks và đặt từng chunk đó lên các OSD tương ứng. RHCS Architecture Guide mô tả rõ rằng primary OSD vẫn nhận mọi write operations, nhưng object được chia thành data chunks và coding chunks, và mỗi chunk nằm trên một OSD trong acting set. Vì vậy, write path của EC phức tạp hơn replication ngay từ bản chất.

Đây là lý do tại sao EC thường phù hợp hơn với dữ liệu lớn, ít ghi đè, hoặc write once/read many, còn replication thường phù hợp hơn với block storage hoặc workload có nhiều cập nhật nhỏ. Bản chất khác biệt nằm ở chỗ replication nhân bản object hoàn chỉnh, còn EC buộc hệ thống phải encode/decode và quản lý nhiều chunk phụ thuộc lẫn nhau.

Minh họa đơn giản
Replication:
Object
  ↓
Primary OSD
  ↓
Replica 1, Replica 2, Replica 3

Erasure Coding:
Object
  ↓
Primary OSD
  ↓
K data chunks + M coding chunks
  ↓
Mỗi chunk trên một OSD khác nhau
## 5. Đường phục hồi: giống nhau ở mục tiêu, khác nhau ở cơ chế

- Cả replication và erasure coding đều có cùng mục tiêu: khi một phần dữ liệu bị mất, cluster phải khôi phục lại mức dư thừa mong muốn. Nhưng cách phục hồi của chúng rất khác nhau.

- **Với replication,** nếu mất một replica, cluster chỉ cần sao chép lại từ replica còn tốt. Đây là mô hình đơn giản hơn về mặt tư duy: object còn nguyên ở đâu đó, chỉ cần copy lại sang nơi mới.

- **Với erasure coding,** khi mất một chunk, cluster phải đọc đủ các data/coding chunks còn lại để dựng lại chunk bị mất. Điều đó khiến phục hồi EC thường có chi phí tính toán và chi phí I/O cao hơn. Ceph docs về erasure coding và trang “erasure coding enhancements” đều nêu rõ mục tiêu của các cải tiến mới là giảm khuếch đại I/O, giảm băng thông mạng và giảm độ trễ, đặc biệt cho các truy cập nhỏ ngẫu nhiên. Chỉ riêng việc có hẳn một nhánh tối ưu hóa như vậy cũng cho thấy đường phục hồi và truy cập của EC vốn phức tạp hơn replication.

> Replication phục hồi bằng cách chép lại bản đầy đủ còn tốt. Erasure coding phục hồi bằng cách dựng lại mảnh bị mất từ các mảnh còn lại. Hai cách này khác nhau sâu sắc về chi phí I/O, CPU và độ phức tạp vận hành, và đó là lý do không nên nhìn EC chỉ như một “phiên bản tiết kiệm dung lượng” của replication.

## 6. Dung lượng: chỗ mạnh nhất của EC, nhưng không phải mọi thứ

- Ưu thế lớn nhất của erasure coding là hiệu quả sử dụng dung lượng. Ceph docs và RHCS docs đều lặp lại ý này rất rõ. So với replication, EC thường cho nhiều usable capacity hơn trên cùng một lượng raw storage. Ví dụ 3-way replication cần khoảng 3x raw storage cho 1x dữ liệu logic, trong khi một profile EC như k=2, m=2 cần 2x, và ví dụ 8+3 có thể chỉ khoảng 1.5x.

- Nhưng vì dung lượng là thứ dễ nhìn thấy nhất, nhiều người vô thức biến nó thành tiêu chí duy nhất. Đây là chỗ rất dễ sai. Nếu workload là block storage có nhiều ghi đè nhỏ, hoặc file system với nhiều metadata và file nhỏ, tiết kiệm dung lượng có thể không bù nổi chi phí về độ trễ và độ phức tạp. Ceph docs về CephFS còn khuyến nghị không dùng EC pool làm default data pool nếu mục tiêu là hiệu năng tốt cho các đối tượng nhỏ và inode backtraces; thậm chí metadata pool bắt buộc phải replicated.

## 7. Failure domain: EC thường đòi hỏi topology rộng hơn

- Replication và EC đều cần failure domain, nhưng EC thường cần nhiều failure domains hơn để thực sự phát huy đúng thiết kế. Ceph docs nói thẳng rằng tùy workload và profile, EC thường cần nhiều failure domains hơn replication. Điều này là hợp lý: nếu bạn có K+M chunks, các chunk đó phải được trải ra đủ rộng để ý nghĩa chịu lỗi của M thật sự còn nguyên.

    - Ví dụ, nếu replicated pool size 3 chỉ cần ba vị trí hợp lý để đặt ba bản sao, thì một EC profile như k=4, m=2 cần sáu vị trí logic phù hợp cho sáu chunks. Nếu failure domain bạn chọn là host, điều đó đồng nghĩa cluster cần đủ số host tương ứng để placement đúng nghĩa. Đây là chỗ mà nhiều thiết kế “nhìn trên giấy rất đẹp” nhưng khi triển khai thật lại bị bó bởi topology vật lý.

> EC không chỉ hỏi “có đủ dung lượng không”, mà còn hỏi “có đủ topology không”. Nhiều khi bottleneck của EC không nằm ở ổ đĩa, mà nằm ở chỗ cluster không có đủ failure domains độc lập để đặt K+M chunks đúng như policy mong muốn.

## 8. Overwrites: ranh giới lớn giữa EC cho object và EC cho block/file

- Một điểm cực kỳ quan trọng là: theo mặc định, erasure-coded pools **chỉ làm việc tốt với các thao tác ghi toàn bộ object, rất phù hợp với nhiều workload object storage**. Để EC pool dùng được cho RBD, CephFS hoặc librados với các cập nhật một phần object, cần bật `allow_ec_overwrites`=true. Ceph docs nhấn mạnh rằng từ Luminous, partial writes for EC pools có thể được bật bằng cấu hình này.

- Nhưng kể cả khi bật `allow_ec_overwrites`, vẫn còn một giới hạn quan trọng: **EC pools không hỗ trợ OMAP**. Vì vậy, để dùng EC với RBD và CephFS, dữ liệu người dùng có thể ở EC pool, nhưng metadata vẫn phải ở replicated pool. Ceph docs nói rất thẳng điều này, cả ở phần erasure code lẫn CephFS createfs. Đây là một khác biệt nền tảng giữa “EC cho data” và “replication cho metadata”.

    - Thêm nữa, `allow_ec_overwrites` chỉ được hỗ trợ khi OSD dùng BlueStore. Ceph docs nêu rõ BlueStore checksumming được dùng trong deep scrub để phát hiện bitrot/corruption, và dùng FileStore với EC overwrites vừa không an toàn vừa chậm hơn. Với Ceph hiện đại thì đây ít còn là trở ngại thực tế vì BlueStore đã là backend mặc định và FileStore đã biến mất khỏi các release mới, nhưng về mặt khái niệm đây vẫn là một điểm rất đáng nhớ.

> EC vốn sinh ra rất tự nhiên cho object writes kiểu ghi trọn object. Muốn đem nó sang block và file, Ceph phải mở rộng mô hình bằng `allow_ec_overwrites`, và ngay cả khi đó metadata vẫn thường phải ở replicated pool vì OMAP. Đây là lý do nói “EC dùng được cho RBD/CephFS” là đúng, nhưng nếu không nói tiếp “chỉ cho data, còn metadata vẫn replicated” thì vẫn là một cách hiểu chưa đủ.

## 9. Workload nào hợp với replication, workload nào hợp với EC

- Nếu nhìn từ docs chính thống, có thể rút ra một quy luật khá ổn định.

- Replication phù hợp hơn với:

    - block storage cho VM
    - workload có nhiều ghi đè nhỏ
    - metadata-heavy workload
    - tình huống cần đường ghi đơn giản và độ trễ dễ đoán hơn.

- Erasure coding phù hợp hơn với:

    - object storage dung lượng lớn
    - dữ liệu lớn, ít sửa đổi
    - lưu trữ lạnh hoặc lưu lâu
    - các workload ưu tiên tiết kiệm raw capacity hơn là tối ưu ghi nhỏ lẻ.

- Ceph docs về CephFS còn khuyến nghị nếu dự định dùng EC cho file data thì vẫn nên để default data pool là replicated để hỗ trợ tốt hơn cho các đối tượng nhỏ và inode backtraces. Điều này cho thấy cả trong file workloads, câu trả lời không phải “CephFS = replication hay EC”, mà là có thể phối hợp cả hai theo vai trò.

## Kết luận
- Replication và erasure coding là hai cơ chế bảo vệ dữ liệu nền tảng của Ceph, nhưng chúng đại diện cho hai triết lý rất khác nhau. Replication đánh đổi dung lượng để lấy sự đơn giản của bản sao đầy đủ, đường ghi rõ ràng và phục hồi dễ hiểu hơn. Erasure coding đánh đổi CPU, I/O và độ phức tạp để lấy hiệu quả dung lượng cao hơn, đặc biệt hấp dẫn cho dữ liệu lớn hoặc lưu lâu.
> Replication giữ nhiều bản đầy đủ để đơn giản hóa độ bền; erasure coding giữ đủ mảnh để dựng lại dữ liệu và tiết kiệm dung lượng.
- Các lưu ý cốt lõi :
    - replicated pool vẫn là kiểu mặc định
    - EC vẫn dựa trên K+M
    - primary OSD vẫn là điểm vào của write path
    - allow_ec_overwrites vẫn là chìa khóa để dùng EC cho RBD/CephFS data
    - metadata/OMAP vẫn khiến replicated pool giữ vai trò quan trọng trong nhiều thiết kế hỗn hợp.
### Những hiểu lầm phổ biến

- Hiểu lầm phổ biến nhất là nghĩ rằng erasure coding luôn “tốt hơn” replication vì tiết kiệm dung lượng hơn. Điều này sai. EC mạnh ở dung lượng, nhưng không mặc định tốt hơn replication cho mọi workload. Nếu dữ liệu có nhiều ghi đè nhỏ, metadata nhiều hoặc độ trễ nhạy, replication thường phù hợp hơn.

- Hiểu lầm thứ hai là nghĩ rằng EC có thể thay replication hoàn toàn. Thực tế, ngay cả khi dùng EC cho data, nhiều trường hợp metadata vẫn phải ở replicated pool vì OMAP không được hỗ trợ trên EC pools. Điều này đặc biệt rõ với RBD và CephFS.

- Hiểu lầm thứ ba là coi replication chỉ đơn giản là “copy nhiều bản”, còn EC chỉ là “chia nhỏ dữ liệu”. Cách hiểu này bỏ qua phần quan trọng nhất: khác biệt thật nằm ở đường ghi, đường phục hồi, yêu cầu topology, và kiểu workload mà mỗi cơ chế phục vụ tốt nhất.