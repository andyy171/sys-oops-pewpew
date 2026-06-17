# Failure Domain và Device Class
## 1. Vì sao hai khái niệm này phải đi cùng nhau

- Failure domain và device class thường bị nhầm lẫn vì cả hai đều nằm trong CRUSH Map và đều ảnh hưởng trực tiếp tới nơi dữ liệu được đặt. Nhưng chúng giải quyết hai bài toán hoàn toàn khác nhau. Failure domain trả lời câu hỏi: những bản sao hoặc các shard phải tách nhau ra như thế nào để không cùng mất khi hạ tầng lỗi. Device class trả lời câu hỏi: dữ liệu nên rơi vào loại phần cứng nào để đạt đúng mục tiêu hiệu năng hoặc chi phí. Ceph và RHCS đều mô tả CRUSH vừa dùng để hiện thực hóa các miền lỗi, vừa dùng để hiện thực hóa các miền hiệu năng dựa trên loại thiết bị.

- Hiểu đúng cặp này là một trong những bước chuyển quan trọng nhất khi học Ceph. Rất nhiều người mới chỉ nhớ rằng “CRUSH đặt replica lên host khác nhau” hoặc “pool này dùng SSD”, nhưng chưa nhận ra rằng đó là hai trục khác nhau của placement. Một trục bảo vệ dữ liệu trước lỗi hạ tầng, trục còn lại tối ưu workload theo khả năng phần cứng. Nếu không tách được hai trục này, bạn sẽ rất khó thiết kế pool và rule đúng cho từng bài toán.

> Failure domain là câu chuyện về rủi ro cùng chết, còn device class là câu chuyện về tính cách phần cứng. Một cái bảo vệ bạn khỏi mất dữ liệu khi host hoặc rack sập; một cái giúp dữ liệu đi đúng vào HDD, SSD hay NVMe. Hai thứ cùng nằm trong CRUSH, nhưng không bao giờ nên hiểu là một.

## 2. Failure domain là gì

- Failure domain là ranh giới mà khi một sự cố xảy ra, toàn bộ tài nguyên bên trong ranh giới đó có thể mất cùng lúc. Ceph docs mô tả CRUSH hierarchy như một cây các bucket phản ánh hạ tầng vật lý, trong đó các yếu tố liên quan có thể gồm host, rack, chassis, row, room, datacenter, nguồn điện dùng chung, mạng dùng chung hoặc các yếu tố tương quan lỗi khác. Mục tiêu của việc mô hình hóa các tầng này là để CRUSH có thể tránh đặt các bản sao hoặc shard vào cùng một nơi có thể hỏng cùng nhau.

- Nói cách khác, failure domain không phải là “tầng nào đó Ceph tự biết sẵn”, mà là cách bạn dạy Ceph nhìn hạ tầng của mình. Nếu cluster của bạn có hai rack nhưng trong CRUSH hierarchy chỉ có host chứ không có rack, thì đối với Ceph, rủi ro cấp rack gần như không tồn tại trong mô hình placement. Điều này giải thích vì sao hai cụm Ceph cùng số node, cùng số OSD vẫn có thể có mức chịu lỗi rất khác nhau: không chỉ vì số replica, mà vì chúng có thể đang mô hình failure domain khác nhau.

- Một số failure domain điển hình
    - `osd`: một thiết bị hoặc một OSD đơn lẻ
    - `host`: một máy chủ vật lý
    - `rack`: một tủ rack
    - `room` hoặc `datacenter`: phạm vi lỗi lớn hơn nhiều
    - các miền lỗi tùy biến khác nếu hạ tầng cần mô hình hóa nguồn điện, mạng hoặc khu vực riêng biệt
## 3. Failure domain tác động lên placement như thế nào

- Ceph docs về CRUSH Maps nêu rất rõ: khi tạo rule cho một replicated pool, quyết định quan trọng đầu tiên là chọn failure domain. Nếu chọn `host`, CRUSH sẽ bảo đảm mỗi replica nằm trên một host khác nhau. Nếu chọn `rack`, mỗi replica sẽ nằm trên một `rack` khác nhau. Điều đó có nghĩa failure domain không phải chỉ là “nhãn mô tả”, mà là **tham số trực tiếp quyết định placement thực tế của replica.**

- Từ nguyên lý đó, có thể suy ra một điều rất quan trọng trong thiết kế. Nếu bạn cấu hình pool có size = 3 nhưng rule yêu cầu tách theo rack, thì về mặt logic bạn cần ít nhất ba rack độc lập để thỏa mãn trọn vẹn chính sách đó. Nếu cluster chỉ có hai rack, CRUSH không thể biến “ba replica ở ba rack khác nhau” thành hiện thực hoàn hảo. Đây không phải lỗi của Ceph; đây là việc topology vật lý không đủ để thỏa policy đã đặt ra. Chính vì vậy,**chọn failure domain luôn phải đi cùng với việc nhìn thẳng vào hạ tầng thật**.

> Nhiều người nghĩ độ an toàn nằm ở size=3. Thực ra size=3 chỉ mới nói “có ba bản sao”. Độ an toàn thật nằm ở câu hỏi tiếp theo: ba bản sao đó có nằm trên ba miền lỗi độc lập hay không. Nếu không, con số replica chỉ đẹp trên giấy tờ.

## 4. Failure domain trong replicated pools và erasure-coded pools

- **Với replicated pool,** failure domain quyết định các bản sao hoàn chỉnh sẽ được tách nhau ra sao. RHCS 8 Architecture Guide nói rõ replica pools lưu nhiều bản sao sâu của object bằng cách dùng CRUSH failure domain để tách các bản sao đó lên các phần cứng vật lý khác nhau. Ý nghĩa của việc này là khi một thiết bị, host hoặc rack lỗi, cluster vẫn còn bản sao nằm ngoài miền lỗi đó để tiếp tục phục vụ dữ liệu.

- **Với erasure-coded pool,** ý tưởng vẫn giống nhau nhưng đối tượng placement không còn là full replicas mà là data chunks và coding chunks. Ceph docs và RHCS storage strategies đều cho ví dụ crush-failure-domain=rack, trong đó rule tương ứng sẽ bảo đảm không có hai chunk cùng rơi vào một rack. Điều này rất quan trọng vì erasure coding chỉ thật sự mang lại độ bền mong muốn nếu các chunk được phân tán qua đủ failure domains độc lập.

## 5. Device class là gì

- Device class là cách Ceph gắn loại thiết bị lưu trữ cho mỗi OSD, ví dụ `hdd`, `ssd`, `nvme`. Ceph dùng device classes để hiện thực hóa performance domains, tức là **các miền hiệu năng dựa trên phần cứng bên dưới**. Nhờ đó, trong cùng một cluster bạn có thể **đồng thời có các workload thiên về dung lượng trên HDD, workload thiên về IOPS trên SSD, và workload độ trễ rất thấp trên NVMe.**

- Điểm quan trọng là **device class không tạo ra backend mới**. Nó chỉ tạo ra một cách chọn đúng nhóm OSD trong cùng một cluster. Tài liệu Ceph nêu rằng device classes được triển khai bằng cách tạo một “shadow” CRUSH hierarchy cho mỗi lớp thiết bị đang dùng, và các CRUSH rule có thể đặt dữ liệu lên shadow hierarchy đó. Điều này cho phép placement dựa trên class mà vẫn tương thích với client cũ.

## 6. Vì sao Ceph cần device class

- Trước khi có device class, nếu cluster dùng nhiều loại phần cứng khác nhau trong cùng các host, quản trị viên thường phải duy trì nhiều CRUSH hierarchy riêng hoặc dùng các cách đặt tên host logic khá rườm rà để tách placement. Tài liệu Red Hat về CRUSH administration nói rất rõ rằng device classes loại bỏ sự rườm rà này bằng cách cho **CRUSH rule biết cần dùng class thiết bị nào, nhờ đó đơn giản hóa mạnh việc quản lý CRUSH**.

- Đây là một cải tiến rất đáng giá về mặt tư duy. Thay vì cố “bẻ” topology để tách SSD khỏi HDD bằng nhiều cây logic chồng chéo, giờ bạn có thể giữ một topology failure domain sạch sẽ, rồi chồng thêm lựa chọn theo class ở tầng rule. Điều này làm cho thiết kế cluster trong các bản Ceph hiện đại rõ ràng hơn rất nhiều.

> Device class không thay thế topology; nó làm cho topology đỡ bị lạm dụng vào mục đích phân loại phần cứng. Nói cách khác, nhờ device class mà cây CRUSH có thể tập trung mô tả miền lỗi, còn rule có thể thêm điều kiện về loại thiết bị mà không cần bẻ gãy cấu trúc hạ tầng.

## 7. Device class khác gì failure domain

- Đây là cặp phân biệt quan trọng nhất của cả file.
    - Failure domain trả lời câu hỏi: các bản sao hoặc chunk phải tránh ở cùng đâu để không mất cùng lúc.
    - Device class trả lời câu hỏi: dữ liệu nên đi vào loại phần cứng nào.

- Một host có thể vừa là failure domain, vừa chứa nhiều device classes khác nhau. Ví dụ một máy có 12 HDD và 2 NVMe:

    - nếu bạn chọn failure domain là host, CRUSH sẽ cố đặt replica trên các host khác nhau
    - nếu bạn chọn device class là nvme, CRUSH sẽ chỉ chọn trong tập OSD gắn nhãn nvme
    - hai quyết định này cùng đúng, nhưng mỗi quyết định trả lời một câu hỏi khác nhau.

Đây là chỗ rất dễ bị nhầm trong thực tế. Nhiều người nói “tôi muốn replica tách sang SSD khác” như thể SSD là failure domain. Nhưng SSD hay HDD chỉ cho biết hành vi hiệu năng và loại phần cứng; nó không cho biết các thiết bị đó có chết cùng nhau hay không. Thứ quyết định rủi ro cùng chết vẫn là host, rack, pdu, room hay datacenter.

## 8. CRUSH dùng device class như thế nào

- Ceph Pacific docs nêu rằng device classes được hiện thực bằng một shadow CRUSH hierarchy cho từng class đang dùng, trong đó chỉ chứa các thiết bị của class đó. Sau đó CRUSH rules có thể phân phối dữ liệu lên shadow hierarchy tương ứng. Điều này giải thích vì sao bạn có thể viết rule kiểu “replicated trên host, nhưng chỉ trong class SSD” mà không cần xây hẳn một cây topology hoàn toàn khác chỉ cho SSD.

- Tài liệu RHCS 8 Storage Strategies Guide cũng cho ví dụ trực tiếp về cú pháp rule: bạn có thể tạo rule replicated với failure domain và class như ceph osd crush rule create-replicated fast default host ssd. 
    - Cú pháp đó phản ánh đúng hai tầng placement đang nói tới:
        - host là failure domain
        - ssd là device class
- Minh họa tư duy rule
```
Pool policy
   ↓
CRUSH rule
   ├─ Chọn miền lỗi: host / rack / datacenter
   └─ Chọn loại thiết bị: hdd / ssd / nvme
   ↓
CRUSH hierarchy + shadow hierarchy theo class
   ↓
OSD đích
```
## 9. Phối hợp failure domain và device class trong thiết kế thực tế

- Thiết kế đúng thường không chọn một trong hai, mà dùng cả hai cùng lúc. Ví dụ:

    - workload dung lượng lớn, ít nhạy độ trễ: chọn device class = hdd, failure domain = host hoặc rack
    - workload cơ sở dữ liệu, nhạy IOPS: chọn device class = ssd, failure domain = host
    - workload độ trễ cực thấp: chọn device class = nvme, failure domain vẫn là host hoặc rack tùy topology

- Nhìn theo cách này, failure domain và device class giống như hai bộ lọc liên tiếp:

    - bộ lọc thứ nhất bảo đảm dữ liệu không dồn vào cùng miền lỗi
    - bộ lọc thứ hai bảo đảm dữ liệu đi vào đúng loại phần cứng

- Đây là một cách tư duy rất hữu ích khi thiết kế pool. Nó giúp bạn không còn nói chung chung “pool này để trên SSD”, mà phải nói chính xác hơn: pool này đặt trên SSD và các replica được tách theo host. Khi nói được đến mức đó, bạn mới thật sự hiểu mình đang thiết kế storage strategy chứ không chỉ tạo pool.

## KẾt luận 
- Failure domain và device class là hai trục placement rất quan trọng của Ceph. Trục thứ nhất bảo vệ dữ liệu khỏi các lỗi có tính tương quan trong hạ tầng bằng cách tách replica hoặc chunk qua các miền lỗi phù hợp. Trục thứ hai giúp dữ liệu đi vào đúng loại thiết bị để đạt mục tiêu hiệu năng hoặc chi phí mong muốn. Cả hai cùng sống trong CRUSH, nhưng chúng không làm cùng một việc.
> Failure domain trả lời “đừng để chết cùng nhau ở đâu”, còn device class trả lời “hãy đặt lên loại phần cứng nào”.

- Các lưu ý cốt lõi :
    - CRUSH dùng hierarchy để hiện thực hóa failure domains
    - device classes dùng để hiện thực hóa performance domains
    - rules có thể kết hợp cả failure domain lẫn class
    - shadow hierarchy theo class vẫn là cách Ceph hiện thực device classes

### Những hiểu lầm phổ biến

- Hiểu lầm phổ biến nhất là cho rằng failure domain và device class là một. Đây là sai lầm nguy hiểm nhất. host, rack, datacenter mô tả rủi ro cùng chết; còn hdd, ssd, nvme mô tả đặc tính phần cứng và hiệu năng. Nếu trộn hai thứ này, bạn sẽ rất dễ thiết kế một cluster “đúng loại ổ” nhưng placement lại không chịu lỗi tốt, hoặc ngược lại.

- Hiểu lầm thứ hai là nghĩ rằng có nhiều replica là đủ an toàn. Thực tế, replica chỉ có ý nghĩa khi chúng được đặt qua các failure domains hợp lý. Ba replica trên cùng một rack không cho bạn mức bảo vệ giống ba replica trên ba rack. Sự khác biệt đó không đến từ replica count, mà đến từ CRUSH placement.

- Hiểu lầm thứ ba là cho rằng device class tạo ra một cluster logic riêng biệt. Thực tế, device class chỉ là cơ chế chọn một tập OSD trong cùng cluster thông qua class và shadow hierarchy. Nó không tạo ra một Ceph mới, mà chỉ giúp policy placement tinh vi hơn.

> Nhiều kiến trúc storage hỏng không phải vì thiếu replica, mà vì replica đúng số nhưng sai chỗ. Failure domain quyết định “đúng chỗ để không chết cùng nhau”; device class quyết định “đúng chỗ để chạy đúng hiệu năng”. Ceph mạnh vì CRUSH cho bạn điều khiển được cả hai.