# Peering, Recovery, Backfill và Rebalance

## 1. Vì sao bốn khái niệm này phải đi cùng nhau

- Trong Ceph, `peering`, `recovery`, `backfill` và `rebalance` không phải bốn cơ chế rời rạc. Chúng là bốn giai đoạn hoặc bốn kiểu phản ứng khác nhau của cluster khi trạng thái thay đổi. Ceph được thiết kế để chịu lỗi liên tục ở quy mô lớn, nên khi một `OSD` xuống, quay lại, bị đánh dấu `out`, hoặc khi topology thay đổi do thêm bớt thiết bị, cluster phải vừa xác định lại trạng thái đúng của dữ liệu, vừa khôi phục mức dư thừa mong muốn, vừa di chuyển dữ liệu về vị trí mới theo `CRUSH`. Ceph docs và RHCS docs đều mô tả đúng tinh thần này: `OSD` tự đủ thông tin từ `CRUSH maps` và `OSD maps` để nhân bản, backfill, phục hồi và tái cân bằng một cách động. 

- Nếu phải nhìn chúng như một chuỗi logic, có thể hiểu như sau: cluster phát hiện thay đổi trạng thái qua heartbeat và `OSD map`; các `PG` liên quan phải `peer` để thống nhất trạng thái và lịch sử có thẩm quyền; sau đó nếu dữ liệu thiếu hoặc placement đã thay đổi thì cluster sẽ `recover`, `backfill` và dần `rebalance` để quay về trạng thái `active+clean`. Chính vì vậy, học bốn khái niệm này riêng lẻ thường không hiệu quả bằng học chúng như một luồng tự chữa lành hoàn chỉnh của Ceph. 

> Ceph không chỉ “chịu lỗi” bằng cách giữ nhiều bản sao. Ceph chịu lỗi bằng cách có một chuỗi cơ chế giúp cluster **biết rằng có lỗi**, **xác định dữ liệu đúng đang ở đâu**, rồi **đưa dữ liệu về trạng thái an toàn mới**. Nói ngắn gọn, durability trong Ceph không nằm ở replica count đơn thuần, mà nằm ở cả khả năng **hội tụ lại về trạng thái đúng sau thay đổi**.

## 2. Heartbeat: cách cluster biết ai còn sống

- Trước khi có peering hay recovery, cluster phải biết thành phần nào còn sống và thành phần nào có vấn đề. RHCS 8 Configuration Guide nêu rõ mỗi `Ceph OSD` kiểm tra heartbeat của các `OSD` khác theo chu kỳ, và nếu một `OSD` lân cận **không gửi heartbeat trong khoảng thời gian gia hạn thì nó có thể bị coi là có vấn đề**. Tài liệu Troubleshooting OSDs của Ceph cũng nhấn mạnh rằng heartbeat cùng với peering, replication và recovery đều phụ thuộc mạnh vào mạng; hiện tượng flapping OSD hay network latency có thể làm cluster hiểu sai hoặc hiểu chậm về trạng thái của `OSD`. 

- Điểm cần nhớ là heartbeat không tự nó quyết định dữ liệu đúng hay sai, mà nó cung cấp **tín hiệu sống/chết** để `MON` và các `OSD` còn lại cập nhật `OSD map`. Từ thay đổi của `OSD map`, các `PG` mới biết rằng acting set hoặc up set của chúng đã đổi và phải bước vào một vòng peering mới. Vì vậy heartbeat là điểm bắt đầu của luồng kiểm soát trạng thái, chứ chưa phải là cơ chế phục hồi dữ liệu. 

### Luồng kiểm soát trạng thái ở mức khái quát

```text id="rq47hh"
OSD heartbeat
    ↓
Phát hiện OSD có vấn đề / quay lại
    ↓
OSD map thay đổi
    ↓
PG liên quan bước vào peering
    ↓
Nếu thiếu dữ liệu hoặc đổi placement:
recovery / backfill / rebalance
```

## 3. Peering là gì

- Ceph docs định nghĩa peering là quá trình đưa tất cả các OSD đang lưu một Placement Group (PG) vào sự đồng thuận về trạng thái của mọi object và metadata trong PG đó. Tài liệu cũng nhấn mạnh một chi tiết rất quan trọng: “đồng ý về trạng thái” không có nghĩa là tất cả OSD đã có nội dung dữ liệu mới nhất. RHCS 5 và RHCS 8 Administration Guides lặp lại chính ý này: hoàn tất peering nghĩa là các OSD liên quan đồng ý về trạng thái hiện tại của PG, nhưng chưa chắc mọi replica đã có bản dữ liệu mới nhất.

- Đây là một phân biệt cực kỳ quan trọng. Nhiều người thấy peering xong thì tưởng dữ liệu đã hoàn toàn “sạch” ngay, nhưng thật ra peering chủ yếu giải quyết câu hỏi: ai là primary hiện tại, acting set nào hợp lệ, lịch sử ghi nào là có thẩm quyền, và muốn cập nhật các bản sao thì phải dựa vào đâu. Sau khi giải được câu hỏi đó, cluster mới có nền để bước tiếp sang recovery hoặc backfill nếu còn replica thiếu hoặc placement đã đổi.

## 4. Acting Set, Up Set và vì sao peering cần chúng

- Ceph docs về peering định nghĩa acting set là danh sách có thứ tự các OSD đang hoặc đã từng chịu trách nhiệm cho một PG ở một epoch nào đó. Up set là tập OSD mà cluster hiện cho là nên chịu trách nhiệm cho PG theo OSD map và CRUSH hiện hành. Khi cluster ổn định, hai tập này thường trùng nhau. Khi có lỗi hoặc thay đổi topology, chúng có thể lệch nhau, và đó là dấu hiệu rằng cluster đang phải peer, recover, hoặc rebalance. Chính trang Monitoring OSDs and PGs của Ceph cũng nói rằng nếu Up Set và Acting Set không khớp, cluster có thể đang tự tái cân bằng hoặc đang có vấn đề.

- Nói dễ hiểu hơn, **acting set** giống như “những ai hiện đang gánh trách nhiệm thực tế”, còn **up set** giống như “những ai theo bản đồ hiện tại lẽ ra phải gánh trách nhiệm”. Peering là cơ chế giúp cluster đi từ chỗ hai tập này có thể đang lệch hoặc chưa chắc chắn, tới chỗ có một primary hợp lệ và một trạng thái PG đủ nhất quán để tiếp tục phục vụ dữ liệu. Đây là lý do peering luôn gắn chặt với PG, chứ không được mô tả ở mức từng object riêng lẻ.

## 5. Authoritative history: lịch sử có thẩm quyền của PG

- RHCS 5 và RHCS 8 Administration Guides có một đoạn giải thích rất hay: Ceph sẽ không xác nhận ghi thành công cho client cho tới khi tất cả OSD trong acting set persist thao tác ghi đó. Cách làm này đảm bảo rằng ít nhất một thành viên của acting set sẽ giữ được bản ghi của mọi thao tác ghi đã được xác nhận kể từ lần peering thành công gần nhất. Từ đó, Ceph có thể dựng nên một authoritative history của PG, tức là một lịch sử đầy đủ và có thứ tự của các thao tác đủ để đưa bản sao cũ của PG lên trạng thái hiện tại.

- Đây là ý rất sâu của Ceph. Cluster không chỉ cần biết “OSD nào còn sống”, mà còn cần biết lịch sử ghi nào là lịch sử đúng khi các bản sao có thể bị lệch nhau sau lỗi mạng, crash hoặc restart. Peering chính là quá trình thiết lập lại nền lịch sử đó để recovery không trở thành một trò đoán mò. Một khi hiểu được authoritative history, bạn sẽ thấy peering không còn là “thủ tục kiểm tra sức khỏe”, mà là cơ chế xác lập sự thật của dữ liệu ở cấp PG.

> Heartbeat chỉ nói “ai có vẻ còn sống”. Peering mới trả lời “ai đang giữ lịch sử đúng của PG”. Hai thứ này liên quan nhau nhưng không thay thế nhau. Ceph không thể phục hồi an toàn chỉ bằng việc biết OSD nào còn online; nó cần biết bản ghi nào là đáng tin để các bản sao khác đồng bộ theo.

## 6. `active`, `clean`, `degraded`: ba trạng thái rất hay bị hiểu lẫn

- RHCS 5 và 8 giải thích khá rõ ba trạng thái này. Khi một PG là `active`, điều đó nghĩa là dữ liệu trong PG nhìn chung đã sẵn sàng cho đọc và ghi trên primary và các replicas. Khi một PG là `clean`, điều đó nghĩa là primary và replicas đã peer thành công, không còn stray replicas và tất cả object đã được nhân bản đủ số lần mong muốn. Ngược lại, `degraded` nghĩa là PG đang thiếu mức dư thừa mong muốn, ví dụ do OSD xuống hoặc replicas chưa được tạo lại đầy đủ.

- Điểm rất dễ gây nhầm là: một PG có thể `active+degraded`. Tài liệu RHCS nói rõ lý do là một OSD có thể đã hoạt động và PG có thể đã sẵn sàng phục vụ I/O, nhưng nó chưa giữ đủ toàn bộ object hoặc cluster chưa tạo lại đủ replicas. Nói cách khác, đang hoạt động được không có nghĩa là đã quay về trạng thái an toàn tối ưu. Đây là một trong những điểm quan trọng nhất khi đọc sức khỏe cluster trong Ceph.


## 7. Recovery là gì

- Ceph OSD Config Reference nói rõ: khi cluster khởi động, hoặc khi một OSD crash rồi quay lại, OSD đó sẽ bắt đầu peering với các OSD khác trước khi ghi mới có thể diễn ra. Nếu OSD quay lại nhưng dữ liệu của nó đã tụt hậu so với các replicas còn lại, nó sẽ đi vào recovery mode để lấy bản mới nhất của dữ liệu và cập nhật lại map của mình. RHCS 5 và 8 Administration Guides diễn giải tương tự: khi một OSD đi xuống rồi quay lại, contents của các PG liên quan có thể đã lạc hậu và cần được cập nhật lại để phản ánh trạng thái hiện tại.

- Điểm mấu chốt của recovery là:**đưa một thành viên hoặc một bản sao bị tụt hậu trở lại cùng trạng thái dữ liệu hiện hàn**h. Recovery thường gắn với tình huống **cluster đã biết dữ liệu đúng nằm ở đâu, acting set nào hợp lệ, nhưng một hoặc nhiều thành viên cần được kéo lên để theo kịp authoritative history**. Nó không nhất thiết có nghĩa là topology đã đổi; có thể chỉ là một OSD tạm thời biến mất rồi quay lại.

## 8. Backfill là gì

- Ceph OSD Config Reference của Squid mô tả rất rõ: **khi thêm hoặc xóa OSD, CRUSH sẽ tái cân bằng cluster bằng cách di chuyển các PG tới hoặc khỏi các OSD để khôi phục mức sử dụng cân bằng. Quá trình di chuyển PG và các object bên trong chúng được gọi là backfilling**, và Ceph thực hiện backfill với ưu tiên thấp hơn các yêu cầu đọc ghi của client để giảm ảnh hưởng tới hiệu năng hoạt động bình thường.

- Nói dễ hiểu hơn, **backfill xuất hiện mạnh nhất khi cluster cần đặt dữ liệu sang vị trí mới mà ở đó chưa có sẵn bản sao đủ gần để chỉ cập nhật chênh lệch nhỏ**. Ví dụ điển hình là thêm OSD mới, thay OSD hỏng, hoặc thay đổi placement khiến một PG cần có mặt ở những OSD chưa từng giữ dữ liệu đó trước đây. Khi đó cluster phải “đổ lại” dữ liệu của PG sang vị trí mới. Đây là lý do backfill thường tạo tải rõ rệt lên mạng và đĩa.

> Recovery thường mang nghĩa “đưa bản sao tụt hậu theo kịp lịch sử đúng”. Backfill thường mang nghĩa “đổ dữ liệu sang một vị trí placement mới”. Trên thực tế hai quá trình có thể đan xen, nhưng nếu giữ được cặp phân biệt này trong đầu, bạn sẽ đọc trạng thái cluster và log dễ hơn rất nhiều.

## 9. Rebalance là gì

- Rebalance là bức tranh lớn hơn, còn backfill là một trong những cơ chế thực thi cụ thể để cluster hội tụ về phân bố dữ liệu mới. RHCS 8 Storage Strategies Guide nêu rằng nhờ CRUSH maps, các OSD đủ hiểu cluster để xử lý replication, backfilling và recovery, đồng thời biết cách tái cân bằng cluster và phục hồi từ lỗi một cách động. Điều này có nghĩa rebalance không chỉ là “chia cho đều ổ đĩa”, mà là đưa placement thực tế của dữ liệu về gần với placement mà CRUSH hiện tại yêu cầu.

- Khi thêm OSD, đổi trọng số, hoặc đánh dấu OSD là out, cluster map thay đổi. Từ đó CRUSH cho ra một kết quả placement mới, và cluster phải di chuyển một phần PG để phản ánh sự thay đổi đó. Chính quá trình hội tụ từ phân bố cũ sang phân bố mới là rebalance. Backfill là cách Ceph chuyển dữ liệu để rebalance diễn ra mà vẫn ưu tiên I/O của client ở mức hợp lý.

## 10. Quan hệ giữa peering, recovery, backfill và rebalance

Bốn cơ chế này liên hệ với nhau theo một chuỗi rất tự nhiên. Khi trạng thái cluster thay đổi, OSD map đổi trước. Từ đó các PG liên quan phải peer để xác định acting set hợp lệ và authoritative history. Sau khi peering xong, nếu có thành viên bị tụt hậu thì cluster thực hiện recovery. Nếu placement mới yêu cầu một PG hoặc object phải nằm ở vị trí mà trước đây chưa có dữ liệu, cluster thực hiện backfill. Toàn bộ quá trình hội tụ đó, xét ở cấp độ toàn cluster, chính là rebalance.

Minh họa luồng tự chữa lành
```
Heartbeat / sự cố / thay đổi topology
                ↓
            OSD map đổi
                ↓
              Peering
                ↓
Xác định primary, acting set, authoritative history
                ↓
  Nếu thiếu hoặc lệch dữ liệu → Recovery
  Nếu placement mới cần vị trí mới → Backfill
                ↓
       Cluster dần Rebalance lại
                ↓
           PG quay về active+clean
```
## 11. Vì sao Ceph có thể vừa phục vụ I/O vừa tự chữa lành

- Một điểm rất hay trong OSD/PG docs là Ceph luôn cố cân bằng giữa việc phục vụ yêu cầu mới của client và việc phục hồi dữ liệu cũ. Tài liệu Monitoring OSDs and PGs nói rõ có nhiều tham số điều khiển sự tranh chấp tài nguyên giữa các yêu cầu mới và nhu cầu recovery để đưa PG về trạng thái hiện hành; ví dụ `osd_recovery_delay_start` cho phép OSD `restart`, re-`peer` và xử lý một số replay trước khi bắt đầu recovery. Điều đó cho thấy Ceph không coi self-healing là tác vụ ngoại lệ tách hẳn khỏi hoạt động bình thường, mà là một phần của vòng đời thường trực của cluster.

- Đây cũng là lý do bạn có thể thấy `active+degraded`: cluster vẫn ưu tiên cho dịch vụ còn tiếp tục chạy, đồng thời âm thầm hoặc bán âm thầm thực hiện `recovery/backfill` để quay lại an toàn tối ưu. Ceph được thiết kế cho thế giới mà lỗi phần cứng và lỗi mạng là chuyện thường xuyên, nên mô hình của nó là vừa phục vụ, vừa chữa lành, chứ không phải “dừng hết rồi mới sửa”.

## 12. Heartbeat và mạng: vì sao peering hay flapping thường là vấn đề mạng trước tiên

- Tài liệu Troubleshooting OSDs của Ceph nói rất rõ: khi OSD peer và kiểm tra heartbeat, chúng dùng mạng cluster (nếu có), và các vấn đề mạng có thể dẫn tới flapping OSDs. RHCS cũng nói OSD heartbeat, replication và recovery traffic có thể đi trên cluster network tách riêng. Điều này giải thích tại sao các vấn đề peering rất thường không bắt đầu từ “dữ liệu hỏng”, mà bắt đầu từ mạng không ổn định hoặc sự cố liên kết giữa các OSD.

- Về mặt tư duy, đây là điểm rất quan trọng: **peering là cơ chế logic, nhưng nó sống trên nền của giao tiếp mạng giữa các OSD**. *Nếu mạng chập chờn, cluster có thể liên tục hiểu rằng acting set đang thay đổi, OSD lúc lên lúc xuống, và PG rất khó về clean ngay cả khi đĩa không hỏng.* Vì vậy, đọc trạng thái peering, degraded, recovering mà không nhìn mạng thì thường mới chỉ nhìn được một nửa vấn đề.

## Kết luận

- `Peering`, `recovery`, `backfill` và `rebalance` là bốn mặt của cùng một năng lực cốt lõi của Ceph: tự đưa mình trở lại trạng thái đúng và an toàn sau thay đổi. Heartbeat và OSD map cho cluster biết điều gì đã xảy ra. `Peering` giúp cluster xác định acting set hợp lệ và authoritative history. Recovery kéo các bản sao tụt hậu theo kịp. Backfill đưa dữ liệu sang vị trí placement mới. Rebalance là bức tranh toàn cục của quá trình hội tụ đó.
> Ceph tự chữa lành bằng cách trước hết xác lập lại sự thật của PG, rồi mới kéo dữ liệu về đúng vị trí và đúng mức dư thừa mong muốn.

### Những hiểu lầm phổ biến

- Hiểu lầm phổ biến nhất là nghĩ rằng peering xong thì dữ liệu đã hoàn toàn sạch và đồng bộ. Điều này sai. Ceph docs và RHCS docs đều nhấn mạnh rằng peering chỉ bảo đảm các OSD đồng ý về trạng thái của PG, chứ chưa chắc mọi replica đã có dữ liệu mới nhất. Chính vì vậy cluster còn cần recovery hoặc backfill sau peering.

- Hiểu lầm thứ hai là nghĩ rằng active đồng nghĩa với clean. Thực tế một PG có thể active+degraded: vẫn phục vụ I/O nhưng chưa đủ replica hoặc còn object/chunk cần khôi phục. Đây là một trong những chỗ quan trọng nhất khi đọc sức khỏe cluster.

- Hiểu lầm thứ ba là xem backfill và recovery như cùng một thứ. Dù trong thực tế chúng có thể đan xen và cùng tiêu tốn mạng/đĩa, về bản chất recovery thiên về kéo bản sao tụt hậu lên theo kịp lịch sử đúng, còn backfill thiên về đổ dữ liệu sang vị trí placement mới. Giữ được phân biệt này sẽ giúp bạn hiểu tốt hơn các trạng thái PG và hành vi khi thêm/xóa OSD.

> Ceph không “chữa lành” bằng một thao tác duy nhất. Nó đi theo chuỗi: phát hiện thay đổi → xác lập lại sự thật của PG → đồng bộ lại dữ liệu → đưa placement về trạng thái mới. Một khi bạn nhìn cluster theo chuỗi này, các trạng thái peering, degraded, recovering, backfilling, active+clean sẽ không còn là những nhãn rời rạc nữa.