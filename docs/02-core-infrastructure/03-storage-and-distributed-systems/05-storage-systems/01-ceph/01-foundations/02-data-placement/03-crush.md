# CRUSH
## 1. CRUSH là gì

- CRUSH là viết tắt của Controlled Replication Under Scalable Hashing. Đây là cơ chế cốt lõi mà Ceph dùng để xác định dữ liệu nên được đặt ở đâu trong cluster. Ceph docs mô tả CRUSH là thuật toán tính toán vị trí lưu trữ dữ liệu thay vì tra cứu một bảng vị trí tập trung; nhờ đó client có thể giao tiếp trực tiếp với OSD thay vì phải đi qua một máy chủ hoặc bộ điều phối trung tâm. Đây là một trong những nền tảng quan trọng nhất làm nên khả năng mở rộng của Ceph.

- Nói ngắn gọn, CRUSH trả lời câu hỏi: object hoặc PG này nên nằm trên những OSD nào. Nhưng điều quan trọng hơn là cách nó trả lời: không dựa vào một bảng tra cứu vị trí được cập nhật liên tục cho từng object, mà dựa vào tính toán có thể lặp lại được từ cùng một đầu vào. Điều đó có nghĩa là nếu client và OSD cùng có Cluster Map hiện tại, chúng sẽ tự tính ra cùng một kết quả placement mà không cần hỏi một “metadata server” trung tâm cho từng lần đọc hoặc ghi.

> CRUSH không phải là “một hàm băm để chia đều dữ liệu” theo nghĩa đơn giản. Nó là cơ chế biến chính sách placement và topology vật lý của cluster thành quyết định cụ thể: object nào đi vào PG nào, PG đó đi tới những OSD nào, replica hoặc shard đó phải nằm cách nhau theo failure domain ra sao. Nếu chỉ hiểu CRUSH là “hàm băm”, bạn sẽ bỏ lỡ đúng thứ làm Ceph khác biệt với nhiều hệ lưu trữ phân tán khác.

## 2. CRUSH giải quyết bài toán gì

- Trước khi hiểu CRUSH làm việc ra sao, cần hiểu bài toán mà nó được sinh ra để giải. Trong một hệ lưu trữ phân tán lớn, cluster phải làm được bốn việc cùng lúc: phân phối dữ liệu đủ đều, tránh điểm nghẽn tập trung, tách bản sao qua các miền lỗi khác nhau, và khi topology thay đổi thì chỉ di chuyển lượng dữ liệu tối thiểu cần thiết. Ceph docs và RHCS Architecture Guides đều nhấn mạnh rằng CRUSH giúp client và OSD tính vị trí dữ liệu mà không phụ thuộc vào bảng tra cứu trung tâm, đồng thời cho phép Ceph tự tái cân bằng và tự phục hồi khi OSD hoặc host thay đổi.

- Nếu không có CRUSH, Ceph sẽ phải chọn một trong hai hướng đều tệ:

    - hoặc giữ một bảng vị trí khổng lồ cho từng object
    - hoặc đặt dữ liệu bằng một cách quá đơn giản, dẫn tới replica rơi vào cùng một vùng lỗi hoặc di chuyển dữ liệu quá nhiều khi cluster thay đổi

- CRUSH là cách Ceph tránh cả hai cực đoan đó. Nó dùng một mô hình giả ngẫu nhiên có kiểm soát: đủ ngẫu nhiên để phân phối dữ liệu đều, nhưng đủ có kiểm soát để phản ánh topology thật của cluster và chính sách mà người quản trị muốn áp dụng.

> CRUSH không tồn tại để “chia tải cho đẹp”. Nó tồn tại để làm cho một cluster lớn vừa mở rộng được, vừa chịu lỗi được, vừa không cần bộ điều phối vị trí dữ liệu trung tâm. Đây mới là giá trị thật của CRUSH.

## 3. CRUSH làm việc ở tầng nào trong Ceph

- CRUSH không làm việc trực tiếp ở tầng “file” hay “block” mà ứng dụng nhìn thấy. Nó làm việc ở tầng placement nội bộ của RADOS. Ceph Architecture mô tả luồng cơ bản là: dữ liệu được biểu diễn thành object, object được ánh xạ vào Placement Group (PG), và từ PG đó CRUSH tính ra tập OSD chịu trách nhiệm lưu dữ liệu. Điều này có nghĩa CRUSH không phải là “bước cuối của write path”, mà là động cơ placement nằm giữa PG và OSD.

- Đây là chỗ rất dễ nhầm. Người mới học Ceph thường nghĩ theo cách: *object được băm rồi đi thẳng tới OSD*. Thực tế, **Ceph dùng một lớp trung gian là PG để tránh phải quản lý placement ở mức từng object riêng lẻ**. Vì vậy, CRUSH phải được hiểu đúng là:

    1. object được ánh xạ vào PG
    2. rồi PG mới được CRUSH ánh xạ tới một tập OSD

=> Khi hiểu theo cách này, bạn sẽ thấy ngay vì sao các khái niệm như recovery, backfill, active, clean, degraded đều gắn chặt với PG chứ không gắn với object riêng lẻ.

### Minh họa vị trí của CRUSH trong luồng placement
```
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
## 4. CRUSH Map là gì

- CRUSH không thể làm việc nếu không có CRUSH Map. Ceph docs mô tả CRUSH Map là tập hợp gồm:

    - danh sách các OSD
    - một hệ phân cấp các bucket
    - và các rule mô tả cách đặt dữ liệu trong cluster.

- Nói cách khác, CRUSH Map là nơi biểu diễn mô hình vật lý và logic của cluster. Nó không chỉ nói “cluster có những OSD nào”, mà còn nói:

    - OSD nào thuộc host nào
    - host nào nằm trong rack nào
    - rack nào nằm trong hàng hoặc trung tâm dữ liệu nào
    - và dữ liệu nên được đặt theo quy tắc nào qua các tầng đó.

- Điểm rất quan trọng là CRUSH Map không chỉ phản ánh failure domains mà còn có thể phản ánh performance domains. RHCS Architecture Guide và Storage Strategies Guide đều nói rằng CRUSH có thể nhận diện các OSD theo loại phần cứng hoặc nhóm hiệu năng, từ đó đặt dữ liệu không chỉ theo miền lỗi mà còn theo miền hiệu năng. Đây là cơ sở cho các khái niệm như device class và placement lên hdd, ssd, nvme.

> CRUSH Map không phải là “bản đồ của các OSD”. Nó là mô hình placement của toàn cluster. Nếu object là dữ liệu và pool là chính sách, thì CRUSH Map là nơi biến chính sách đó thành quyết định placement dựa trên hạ tầng thật.

## 5. Bucket hierarchy: vì sao CRUSH cần cây phân cấp

- Ceph docs về CRUSH map edits nói rất rõ: để ánh xạ PG tới OSD qua các failure domain, CRUSH Map định nghĩa một danh sách phân cấp các kiểu bucket. Mục đích của việc tạo cây bucket này là tách các leaf node theo failure domains, ví dụ host, chassis, rack, row, room, datacenter. Với ngoại lệ là các leaf node biểu diễn OSD, phần còn lại của cây này là tùy ý và người quản trị có thể thiết kế theo hạ tầng của mình.

- Điểm cực kỳ quan trọng ở đây là: Ceph không quan tâm “rack” hay “row” như những khái niệm thần thánh có sẵn. **Ceph chỉ biết những gì bạn mô tả trong CRUSH hierarchy. Tức là failure domain không tự nhiên xuất hiện; nó phải được mô hình hóa trong CRUSH Map.** Điều này giải thích vì sao hai cluster cùng chạy Ceph nhưng có thể có hành vi chịu lỗi rất khác nhau nếu CRUSH hierarchy được xây khác nhau.

- Ví dụ cây CRUSH đơn giản
```
root default
 ├── rack-a
 │    ├── host-01
 │    │    ├── osd.0
 │    │    └── osd.1
 │    └── host-02
 │         ├── osd.2
 │         └── osd.3
 └── rack-b
      ├── host-03
      │    ├── osd.4
      │    └── osd.5
      └── host-04
           ├── osd.6
           └── osd.7
```
Nếu rule yêu cầu ba replica ở ba host khác nhau, CRUSH sẽ chọn qua tầng `host`. Nếu rule yêu cầu tách qua `rack`, CRUSH sẽ phải nhìn lên tầng `rack` trước khi chọn xuống `host` và `osd`. Điều này cho thấy topology không chỉ là sơ đồ minh họa; nó tác động trực tiếp tới nơi replica sẽ thực sự được đặt.

## 6. Failure domain: điều CRUSH thật sự bảo vệ bạn khỏi

- CRUSH cho phép bản sao hoặc shard được đặt qua các failure domain. Điều này có nghĩa cluster không chỉ tránh đặt hai replica lên cùng một OSD, mà còn có thể tránh đặt chúng lên cùng một host, cùng một rack, cùng một nguồn điện hoặc cùng một trung tâm dữ liệu nếu topology được mô hình hóa tương ứng.

- Đây là một trong những điểm “vỡ ra” quan trọng nhất của CRUSH:
    `replica count không tự động đồng nghĩa với an toàn.`
    - Nếu bạn có ba bản sao nhưng cả ba đều rơi vào cùng một host hoặc cùng một rack, thì về mặt thực tế bạn vẫn có thể mất cả ba cùng lúc khi failure domain đó sập. Chính vì vậy, CRUSH ruleset mới là thứ biến “có 3 bản sao” thành “3 bản sao thật sự nằm ở các miền lỗi độc lập”.

> Nhiều người nghĩ durability nằm ở con số size=3. Thực ra durability nằm ở size=3 cộng với placement đúng qua failure domains. Đây là khác biệt rất lớn giữa “có nhiều bản sao” và “có nhiều bản sao thực sự hữu ích khi hạ tầng lỗi”.

## 7. Performance domain và device class

- Ngoài failure domain, CRUSH còn có thể thể hiện performance domain. RHCS guides nói rõ CRUSH có thể nhận diện OSD theo loại thiết bị lưu trữ và tổ chức placement theo các cấu hình phần cứng khác nhau. Ceph docs Pacific còn mô tả rằng device classes được triển khai bằng cách tạo một shadow CRUSH hierarchy cho mỗi lớp thiết bị đang dùng, ví dụ hdd, ssd, nvme; các rule có thể đặt dữ liệu lên shadow hierarchy tương ứng.

- Điều này tạo ra một phân biệt rất có giá trị:

    - failure domain trả lời câu hỏi: replica phải tách nhau về mặt rủi ro như thế nào
    - performance domain trả lời câu hỏi: dữ liệu nên rơi vào loại phần cứng nào

- Nếu không tách rõ hai thứ này, người học rất dễ lẫn lộn rằng “SSD” hay “NVMe” là failure domain. Thực ra đó chủ yếu là miền hiệu năng, không phải miền lỗi. Miền lỗi thường là host, rack, datacenter; còn device class là cách chọn đúng nhóm thiết bị phù hợp với workload.

## 8. CRUSH rule: nơi chính sách placement trở thành hành động

- CRUSH Map không chỉ có hierarchy mà còn có rule. Rule là nơi mô tả placement policy cụ thể cho pool. Ceph docs nói rằng rules describe how replicas are placed in terms of the hierarchy, ví dụ “ba replica ở ba rack khác nhau”. Khi một pool dùng một CRUSH rule nào đó, rule này chính là cầu nối giữa policy logic của pool và hành động placement thực tế.

- Một cách hiểu rất hữu ích là:
    - pool nói “dữ liệu này dùng chính sách gì”
    - CRUSH rule nói “chính sách đó được thực hiện như thế nào trên topology thật”

- Với replicated pool, quyết định lớn nhất khi tạo rule thường là chọn failure domain, ví dụ host hay rack. Ceph docs cũ hơn nhưng vẫn đúng về nguyên lý giải thích rằng nếu chọn host, mỗi replica sẽ nằm trên host khác nhau; nếu chọn rack, mỗi replica sẽ nằm trên rack khác nhau. Với erasure-coded pools, các shard cũng phải được đặt sao cho không dồn vào cùng failure domain; docs về EC còn khuyến nghị phần lớn deployment EC cần ít nhất k+m failure domains, và thường tốt hơn nếu có k+m+1.

> CRUSH rule mới là thứ làm cho câu “pool này replicated” có nghĩa ở ngoài đời thật. Nếu pool là nơi gắn policy, thì CRUSH rule là nơi policy đó bước xuống hạ tầng. Không có rule phù hợp, policy chỉ là lời nói.

## 9. Weight: vì sao CRUSH không chỉ biết topology mà còn biết tỷ trọng

- Ceph docs về CRUSH map edits nói rằng CRUSH phân phối object lên các thiết bị lưu trữ theo một per-device weight value, xấp xỉ một phân phối xác suất đồng đều có xét tới trọng số. Nói cách khác, CRUSH không chỉ biết “OSD này nằm ở đâu”, mà còn biết “OSD này nên gánh bao nhiêu dữ liệu tương đối so với OSD khác”. Điều này cực kỳ quan trọng trong cluster không đồng nhất về dung lượng hoặc hiệu năng.

- Vì vậy, placement trong Ceph không đơn thuần là “chia đều số object”. Nó là sự kết hợp của:

    - topology
    - rule
    - failure domain
    - và trọng số của từng thiết bị hoặc bucket

- Khi bạn thay đổi weight hoặc thêm OSD mới, CRUSH sẽ tính lại placement theo mô hình mới. Điều đáng giá là nó không làm điều đó bằng cách xáo toàn bộ dữ liệu một cách mù quáng, mà cố gắng giữ mức di chuyển dữ liệu thấp nhất có thể. Đây chính là thứ làm Ceph có khả năng mở rộng mềm mại hơn nhiều hệ thống khác.

## 10. Vì sao CRUSH giúp Ceph tự tái cân bằng và tự phục hồi

- RHCS Architecture Guides nói rất rõ: bằng cách dùng CRUSH để gán object vào PG và gán PG vào tập OSD, OSD có thể dùng CRUSH để tự tái cân bằng cluster hoặc phục hồi từ lỗi OSD một cách động. Khi một host mới cùng các OSD mới được thêm vào cluster, cluster map thay đổi; vì CRUSH phân phối PG một cách giả ngẫu nhiên và đồng đều, một phần PG sẽ được gán lại sang OSD mới. Điều đó có nghĩa người quản trị không phải tái cân bằng thủ công toàn bộ cluster.

- Đây là một đặc tính rất quan trọng của CRUSH mà người mới thường chỉ hiểu ở mức “thêm OSD thì cluster tự cân bằng lại”. Ý sâu hơn là:

    - CRUSH làm cho placement có thể tính lại được
    - từ đó cluster biết dữ liệu nên ở đâu sau khi topology đổi
    - rồi recovery/backfill/rebalancing chỉ việc làm cho dữ liệu thật sự tiến dần về vị trí đó

=> Tức là CRUSH không trực tiếp chuyển dữ liệu, nhưng nó là thứ xác định trạng thái placement mới mà cluster phải hội tụ về.

## 11. CRUSH và việc không có bảng tra cứu tập trung

- Ceph Architecture ở Pacific, Reef và các bản mới đều nhấn mạnh rằng **client và OSD dùng CRUSH để tính thông tin vị trí dữ liệu thay vì phụ thuộc vào một bảng tra cứu trung tâm.** Đây không chỉ là một chi tiết tối ưu hóa, mà là điểm tạo nên kiến trúc scale-out thật sự của Ceph. Nếu mỗi lần đọc hoặc ghi object đều phải hỏi một server trung tâm “object này đang ở đâu”, thì đến một quy mô nào đó server đó sẽ thành nút thắt, cả về hiệu năng lẫn độ tin cậy.

- CRUSH giải bài toán đó bằng cách biến placement thành tính toán chia sẻ:

    - MON giữ Cluster Map
    - client lấy map
    - client và OSD cùng chạy cùng một logic CRUSH
    - cả hai cùng đi tới cùng một kết quả placement

=> Đây là một trong những ý giá trị nhất của Ceph: không phải mọi thứ đều phân tán ở dữ liệu; bản thân phép quyết định vị trí dữ liệu cũng được phân tán.

> CRUSH không chỉ bỏ bảng tra cứu trung tâm; nó biến việc định vị dữ liệu thành một phần của chính client và OSD. Nói cách khác, Ceph không chỉ phân tán storage, mà còn phân tán luôn cả trí tuệ placement.

## Kết luận 
- CRUSH là động cơ placement của Ceph. Nó làm cho client và OSD có thể tự tính vị trí dữ liệu mà không cần một bảng tra cứu tập trung, đồng thời biến topology vật lý và chính sách lưu trữ thành placement cụ thể qua CRUSH Map và CRUSH rules. Nhờ CRUSH, Ceph không chỉ phân phối dữ liệu đều, mà còn có thể tách replica qua failure domains, đặt dữ liệu lên đúng loại phần cứng, tự tái cân bằng khi cluster mở rộng và tự phục hồi khi thành phần hỏng.
- Các lưu ý chính của CRUSH:
    - CRUSH tính vị trí lưu trữ thay vì tra bảng trung tâm
    - CRUSH Map gồm hierarchy, buckets và rules
    - failure domain và performance domain vẫn là hai trục quan trọng
    - object đi qua PG rồi mới tới OSD
    - CRUSH là nền cho tự cân bằng và tự phục hồi.

- Có một thay đổi đáng chú ý ở dòng phát triển mới hơn là MSR (Multi-Step Retry) CRUSH rule type xuất hiện trong Squid/Tentacle release notes để cho phép cấu hình EC linh hoạt hơn. Tuy nhiên, đây là mở rộng ở tầng rule chuyên biệt, không làm thay đổi mô hình nền của CRUSH mà người học cần nắm ở file này. Vì vậy, về mặt ghi chép kiến thức cốt lõi, tốt nhất là xem Pacific và Squid đồng nhất về nguyên lý, chỉ lưu ý rằng các bản mới tiếp tục mở rộng khả năng biểu đạt của CRUSH rules trong một số tình huống nâng cao.

### Những hiểu lầm phổ biến về CRUSH

- Hiểu lầm phổ biến nhất là nghĩ rằng CRUSH chỉ là “hàm băm chia đều dữ liệu”. Điều này quá đơn giản hóa. CRUSH không chỉ chia đều, mà còn phải phản ánh topology, tách replica qua failure domain, chọn đúng performance domain và giảm mức di chuyển dữ liệu khi cluster thay đổi. Nếu chỉ hiểu CRUSH là hashing, bạn sẽ không hiểu vì sao Ceph cần CRUSH Map và CRUSH rules.

- Hiểu lầm thứ hai là cho rằng size=3 tự nó đã bảo đảm an toàn. Thực ra, ba bản sao chỉ thật sự có giá trị khi CRUSH đặt chúng ở các miền lỗi phù hợp. Ba bản sao trên cùng một host hoặc cùng một rack vẫn có thể cùng mất một lúc. Điều bảo vệ bạn không chỉ là số replica, mà là replica count cộng placement đúng qua failure domains.

- Hiểu lầm thứ ba là tưởng rằng CRUSH trực tiếp quản lý từng object ở quy mô vận hành. Thực tế, object được ánh xạ vào PG, rồi CRUSH mới ánh xạ PG vào OSD. Chính lớp PG này mới làm cho placement và self-healing của Ceph có thể mở rộng.

- Hiểu lầm cuối cùng là xem device class như failure domain. SSD, HDD, NVMe chủ yếu là miền hiệu năng, còn host, rack, datacenter mới là miền lỗi. CRUSH có thể đồng thời nhìn cả hai, nhưng hai khái niệm này phục vụ hai mục tiêu khác nhau và không nên trộn làm một.