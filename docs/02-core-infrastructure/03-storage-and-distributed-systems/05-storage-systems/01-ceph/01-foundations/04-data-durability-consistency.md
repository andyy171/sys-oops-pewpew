# Data Durability và Consistency trong Ceph
## 1. Mục tiêu và phạm vi của durability trong Ceph
### 1.1 Durability là gì và nó khác gì với consistency
Trong Ceph, **data durability** là khả năng giữ dữ liệu không bị mất khi một phần hạ tầng gặp lỗi, còn **consistency** là khả năng đảm bảo các bản sao hoặc các shard của dữ liệu vẫn phản ánh cùng một trạng thái logic hợp lệ theo mô hình của cluster. Hai khái niệm này liên quan chặt chẽ với nhau nhưng không hoàn toàn trùng nhau: một hệ thống có thể còn dữ liệu nhưng chưa ở trạng thái hoàn toàn `clean`, hoặc ngược lại một thao tác ghi có thể đã được xác nhận thành công theo chính sách hiện tại của pool nhưng cluster vẫn cần thêm các bước nền như peering, recovery hoặc scrub để quay về trạng thái khỏe mạnh nhất. Ceph architecture docs ở cả Pacific và Squid đều trình bày durability như một thuộc tính được thực hiện thông qua **replicas** hoặc **erasure code chunks**, còn integrity và consistency được hỗ trợ bởi cơ chế như **scrubbing**, **CRC/checksum**, **placement groups**, và trạng thái của cluster maps.

### 1.2 Vì sao Ceph phải cân bằng giữa an toàn dữ liệu, hiệu năng và chi phí
Một điểm cần nắm ngay từ đầu là Ceph luôn phải cân bằng giữa ba yếu tố: **an toàn dữ liệu**, **hiệu năng**, và **chi phí lưu trữ**. Replication đơn giản hơn và thường có độ trễ tốt hơn, nhưng tốn dung lượng thô nhiều hơn. Erasure coding tiết kiệm dung lượng hơn, nhưng tính toán và phục hồi phức tạp hơn. Scrubbing tăng độ tin cậy dữ liệu, nhưng nếu chạy dày có thể làm giảm hiệu năng. Vì vậy, “durability” trong Ceph không phải một nút bật/tắt, mà là kết quả của nhiều quyết định thiết kế ở cấp pool, CRUSH rule, failure domain và OSD behavior.
## 2. Hai cơ chế bảo vệ dữ liệu chính
Ceph có hai cơ chế bảo vệ dữ liệu cốt lõi: **replication** và **erasure coding**. Cả hai đều là cơ chế ở mức pool. RHCS 8 Architecture Guide nêu rất rõ rằng phương pháp data durability là **pool-wide** và không thay đổi sau khi tạo pool; client nhìn pool type như một chi tiết trong suốt, nhưng ở tầng cluster đây là quyết định cực quan trọng vì nó quyết định cách object được lưu, cách cluster chịu lỗi, và cách recovery diễn ra. 

### 2.1 Replication
- Với replicated pool, Ceph lưu nhiều bản sao hoàn chỉnh của cùng một object trên nhiều OSD khác nhau trong cùng Acting Set. RHCS 5 Architecture Guide mô tả rằng trong một write scenario điển hình, client dùng CRUSH để tính PG và primary OSD; primary OSD sau đó tính secondary OSDs của Acting Set và ghi object tới các secondary này. Khi primary nhận ACK từ các secondary và chính nó hoàn tất write local, nó mới ACK thành công lại cho client. Điều đó có nghĩa durability trong replicated model không chỉ là “copy thêm bản”, mà là **một giao thức ghi có primary điều phối và secondary xác nhận**. 

- Replication có ưu điểm là đơn giản để hiểu, hỗ trợ tốt cho nhiều workload cần latency thấp hoặc hành vi metadata đầy đủ, và thường là lựa chọn mặc định cho các data path nhạy với độ trễ. Khi nói `size = 3`, cần hiểu đây không phải “hai replica cộng một bản chính” theo nghĩa quá hình thức, mà là tổng số bản lưu của object trong placement hiện tại là ba. RHCS 5 Storage Strategies Guide cũng nhấn mạnh resilience của replicated pool chính là số lượng copies mong muốn của object. 

### 2.2 Erasure Coding
- Với erasure-coded pool, Ceph không tạo nhiều bản sao hoàn chỉnh mà chia mỗi object thành `K+M` chunks, gồm `K` data chunks và `M` coding chunks. Pacific architecture, RHCS 5 Architecture Guide và RHCS 8 Architecture Guide đều nhất quán về mô hình này: pool được cấu hình để có kích thước `K+M`, và mỗi chunk được đặt lên một OSD trong Acting Set. Primary OSD của Up Set vẫn là điểm vào của mọi write operations; điểm khác là thay vì gửi full replicas, primary điều phối việc tạo và ghi các data/coding chunks tới các OSD thích hợp. 
- Erasure coding tiết kiệm dung lượng thô hơn replication nhưng đổi lại phức tạp hơn về mặt tính toán, write path và recovery path. RHCS 5 Storage Strategies Guide nêu rõ EC pools giảm lượng disk space cần thiết để bảo đảm durability nhưng có chi phí tính toán cao hơn replication. Vì vậy, EC thường phù hợp hơn với dữ liệu lớn, dữ liệu lạnh, hoặc các workload ưu tiên efficiency của raw capacity hơn là write latency thấp.

### 2.3 Khi nào nên dùng replicated pool và khi nào nên dùng EC pool
Ở mức nguyên lý:

- **Replicated pool** phù hợp hơn với dữ liệu nóng, block storage, metadata-heavy workload, hoặc các trường hợp ưu tiên đơn giản hóa behavior của cluster.
- **Erasure-coded pool** phù hợp hơn với dữ liệu lớn, object storage dung lượng cao, archive, backup, hoặc các workload ưu tiên tiết kiệm dung lượng. 

### 2.4 Những giới hạn và trade-off của từng cơ chế
> Điểm cần nhớ là lựa chọn này không chỉ là bài toán dung lượng. Nó kéo theo sự khác biệt về write path, recovery path, loại failure mà cluster phải chịu, và cả kinh nghiệm vận hành. Trong các cluster lớn, chọn sai pool type cho sai workload có thể dẫn đến hoặc là lãng phí raw storage, hoặc là chấp nhận trade-off hiệu năng quá lớn.

#### Bảng so sánh nhanh

| Tiêu chí | Replication | Erasure Coding |
| --- | --- | --- |
| Cách bảo vệ dữ liệu | Nhiều bản sao hoàn chỉnh | Chia data chunks và coding chunks |
| Hiệu quả dung lượng | Thấp hơn | Cao hơn |
| Độ phức tạp write/recovery | Thấp hơn | Cao hơn |
| Điểm vào write | Primary OSD | Primary OSD |
| Workload phù hợp | Dữ liệu nóng, latency-sensitive | Dữ liệu lớn, capacity-oriented |  

## 3. Consistency model của Ceph
Consistency trong Ceph không phải là một khẩu hiệu trừu tượng, mà là kết quả của việc **mọi thao tác ghi đi qua primary OSD**, mọi replica/chunk placement được xác định bằng cluster map + CRUSH, và mọi PG phải có một trạng thái thống nhất đủ để tiếp tục nhận I/O. RHCS 5 Architecture Guide mô tả rất rõ primary-copy behavior trong replicated pools: primary OSD chịu trách nhiệm nhận object từ client, ghi local, gửi xuống secondary OSDs, và chỉ khi secondary ACK lại thì primary mới ACK thành công cho client. Mô hình này chính là lõi của write consistency trong Ceph.

### 3.1 Primary-copy model
Ceph dùng mô hình **primary-copy** cho cả replicated pools và erasure-coded pools. Điều này nghĩa là client không tự gửi ghi tới mọi replica hoặc mọi shard. Client chỉ nói chuyện với **primary OSD** của PG tương ứng; primary chịu trách nhiệm điều phối phần còn lại. RHCS 5 và RHCS 8 đều mô tả thống nhất rằng trong cả replicated lẫn erasure-coded pools, primary OSD của Up/Acting Set là nơi nhận write operations đầu tiên. 

### 3.2 Vai trò của primary OSD và replica OSD
Primary OSD giữ vai trò điều phối consistency cho PG đó. Secondary OSDs hoặc shard OSDs không phải là các đích ghi độc lập mà client thấy trực tiếp; chúng là thành phần thực thi durability policy mà primary điều phối. Cách thiết kế này giúp client path đơn giản hơn rất nhiều: client chỉ cần biết primary nào hiện đang có trách nhiệm cho PG, còn cluster tự lo phần sao chép hay EC placement. RHCS docs còn nhấn mạnh rằng cơ chế này giúp OSDs relieve clients from replication duty while ensuring high data availability and data safety. 

### 3.3 ACK path, commit path và điều kiện phản hồi thành công
ACK path là điểm rất quan trọng khi nói về durability. Trong tài liệu RHCS 5 architecture, write operation được xem là thành công sau khi primary OSD nhận ACK từ secondary OSDs và chính primary đã hoàn tất write local. Điều này cho thấy ACK thành công không phải là “một mình primary đã giữ dữ liệu”, mà là primary đã đưa write tới mức độ redundancy hiện hành theo policy của pool. Đồng thời, RHCS Administration Guide cũng nhấn mạnh một nuance quan trọng: sau khi client viết object vào primary OSD, PG có thể vẫn ở trạng thái `active+degraded` cho tới khi primary nhận đủ ACK xác nhận replicas đã được tạo thành công. Nói cách khác, durability và PG health có liên hệ chặt nhưng không hoàn toàn đồng bộ tức thời theo cảm nhận của client.

### 3.4 Read consistency và vai trò của primary trong đọc dữ liệu
Ở mức architecture tổng quát, client đọc từ **primary OSD** của PG hiện hành. Nếu primary cũ fail, một OSD khác trong [Up Set/Acting Set](./02-core-concepts.md#24-acting-set-up-set-và-primary-osd) sẽ trở thành primary mới và client, sau khi có map mới, sẽ đọc từ primary đó. Ví dụ object `foo` để cho thấy nếu OSD 5 fail thì client qua librados sẽ tự động lấy object từ OSD mới đang giữ vai trò primary. Điều này phản ánh rằng consistency của read path gắn chặt với cluster map và current acting primary, chứ không gắn với một OSD cố định.

## 4. Placement Group và vai trò của nó trong durability
- Durability của Ceph không vận hành ở mức “theo dõi từng object độc lập bằng metadata table trung tâm”. RHCS 5 Storage Strategies Guide giải thích rất rõ rằng tracking object placement on a per-object basis within a pool is computationally expensive at scale; để giải quyết điều đó, Ceph chia pool thành placement groups, gán object vào PG, rồi gán PG cho primary OSD. Đây là điểm rất quan trọng: Ceph bảo vệ, di chuyển, peer và scrub **ở cấp PG**, chứ không ở cấp một object độc lập theo cách đơn lẻ.

- PG vì vậy là đơn vị trung gian giúp durability có thể scale. Khi OSD fail hoặc cluster rebalance, Ceph có thể move hoặc replicate cả một PG, tức cả tập object bên trong PG, thay vì phải tính lại mọi object một cách riêng rẽ. Điều này không chỉ là tối ưu placement; nó còn là điều kiện để recovery và rebalancing diễn ra khả thi ở quy mô lớn.

### 4.1 Acting Set, Up Set và authoritative history

Durability và consistency của Ceph phụ thuộc vào việc PG biết **ai đang chịu trách nhiệm chính** và **ai đang giữ history có thẩm quyền**. Trong lúc cluster ổn định, Acting Set và Up Set thường đồng nhất với placement mong muốn. Khi OSD fail hoặc topology đổi, chúng có thể tạm thời lệch nhau, và cluster phải thực hiện peering để xác định primary mới, authoritative log và dữ liệu nào cần được phục hồi. Đây là lý do `active` chưa chắc đã `clean`, và cũng là lý do recovery có thể phải diễn ra trước khi cluster quay lại trạng thái redundancy đầy đủ. Ceph docs về placement groups, peering và RHCS health/state descriptions đều xoay quanh logic này. 

### 4.2 Vì sao peering là điều kiện để quay lại trạng thái nhất quán

Khi một OSD down rồi quay lại, nó có thể không còn giữ phiên bản object mới nhất. RHCS 8 Configuration Guide ghi rõ rằng khi OSD crash rồi trở lại, nó thường out of sync với các OSD khác đang giữ phiên bản mới hơn của object; vì vậy OSD phải peer với các OSD khác trước khi write operation có thể diễn ra. Điều đó cho thấy peering không chỉ là thủ tục phụ, mà là bước cần thiết để cluster xác lập lại consistency boundary của PG.

## 5. Data integrity theo thời gian: scrub và deep-scrub

Durability không chỉ là “có nhiều bản sao”. Ceph còn phải đảm bảo các bản sao đó thực sự khớp nhau và dữ liệu không bị silent corruption theo thời gian. Cơ chế nền cho việc này là **scrubbing**. Pacific Placement Groups docs mô tả khi scrub một PG, Ceph kiểm tra primary và replica nodes, tạo catalog của toàn bộ objects trong PG, so sánh để đảm bảo không có object nào bị thiếu hoặc mismatch, và xác nhận metadata liên quan tới snapshot cũng nhất quán. RHCS 5 và RHCS 8 Configuration Guides đều nói scrubbing đóng vai trò giống `fsck` ở object storage layer.

### 5.1 Light scrub

RHCS 5 và RHCS 8 Configuration Guides đều nêu rằng **light scrubbing** kiểm tra kích thước object và attributes. Đây là lớp kiểm tra thường xuyên hơn, với mục tiêu phát hiện sớm các mismatch logic hoặc metadata inconsistency mà không cần đọc toàn bộ dữ liệu object.

### 5.2 Deep-scrub

**Deep-scrub** đọc dữ liệu thực tế và dùng checksums để đảm bảo data integrity. RHCS 8 config guide ghi rõ deep scrubbing đọc data và dùng checksums để đảm bảo integrity; RHCS 5 config guide nói tương tự. Điều này rất quan trọng vì replication hay EC chỉ giúp cluster sống sót khi mất một phần dữ liệu, còn scrub/deep-scrub mới giúp phát hiện trường hợp “dữ liệu còn đó nhưng sai hoặc bị hỏng âm thầm”.

### 5.3 Khi scrub liên quan tới durability hơn là hiệu năng

Scrubbing có thể làm giảm hiệu năng, và docs RHCS 5/8 đều nhấn mạnh cần điều chỉnh tần suất nếu muốn giảm ảnh hưởng tới workload. Tuy nhiên, về mặt nguyên lý, scrub là một phần của **data integrity**, không phải tiện ích tùy chọn vô thưởng vô phạt. Một cluster không scrub hoặc deep-scrub đúng cách có thể vẫn chạy và vẫn trả dữ liệu, nhưng rủi ro silent corruption sẽ khó được phát hiện sớm. Vì vậy, trong bức tranh durability tổng thể, scrub là lớp “kiểm toán nền” cho dữ liệu. 

## 6. Khi cluster thay đổi: durability được giữ như thế nào

Durability trong Ceph chỉ thực sự được kiểm chứng khi cluster thay đổi: OSD down, host mất, rack lỗi, OSD mới được thêm vào, hoặc weight/thành phần placement đổi. RHCS 5 Architecture Guide mô tả rõ rằng khi một OSD fails, cluster tạm thời mất một replica hoặc một erasure-code chunk và cần tạo một copy khác; nếu primary fail thì OSD kế tiếp trong Acting Set trở thành primary và CRUSH tính ra OSD mới để chứa copy hoặc chunk bổ sung. Đây chính là self-healing behavior của Ceph ở mức placement. :contentReference
### 6.1 Degraded nhưng vẫn có thể active

Một PG có thể ở trạng thái `active+degraded`. RHCS Administration Guide giải thích rằng điều này xảy ra vì OSD có thể `active` dù chưa giữ đủ tất cả object cần thiết. Sau khi primary viết object vào storage, PG còn ở `degraded` cho tới khi primary nhận ACK từ replica OSDs rằng replicas đã được tạo thành công. Nếu một OSD down, Ceph đánh dấu các PG gán cho OSD đó là degraded; client vẫn có thể ghi object mới vào một PG degraded nếu nó vẫn `active`. Đây là điểm cực kỳ quan trọng để phân biệt giữa **dịch vụ còn hoạt động** và **độ an toàn của dữ liệu đã hoàn toàn phục hồi hay chưa**.

### 6.2 Recovery

Recovery là quá trình đưa OSD hoặc PG trở lại trạng thái đồng bộ sau khi một thành phần down rồi trở lại hoặc khi cluster phát hiện dữ liệu của một thành viên không còn cập nhật. RHCS 8 Configuration Guide mô tả rằng khi OSD crash rồi quay lại, nó thường out of sync với các OSD khác; vì vậy nó vào recovery mode để tìm latest copy of the data và cập nhật map của nó. Recovery có thể tốn thời gian và tài nguyên, nhất là nếu failure domain lớn như cả rack quay lại cùng lúc.

### 6.3 Backfill

Backfill là cơ chế di chuyển placement groups và các object của chúng tới hoặc khỏi OSDs khi cluster được rebalance do add/remove OSDs. RHCS 8 Configuration Guide mô tả rất rõ rằng khi thêm hoặc xóa OSDs, CRUSH rebalance cluster bằng cách moving placement groups to or from OSDs to restore balance; vì migration này có thể làm giảm hiệu năng đáng kể, Ceph dùng backfill để đặt các operations này ở priority thấp hơn client read/write requests. Điều này cho thấy backfill không chỉ là “copy dữ liệu”, mà là phần quan trọng trong việc khôi phục **durability policy đúng placement** sau thay đổi topology. 

### 6.4 Rebalancing

Rebalancing là bức tranh rộng hơn của việc phân phối lại dữ liệu khi cluster map thay đổi. Khi thêm OSD hoặc đổi weight, CRUSH recalculates placement; chỉ một phần PGs liên quan mới di chuyển, nhưng mục tiêu cuối cùng là cluster quay về trạng thái trong đó durability policy và balance policy cùng được đáp ứng. Vì vậy, rebalancing không chỉ là “chia đều dung lượng”, mà còn là cách để cluster hiện thực hóa lại durability placement sau mọi thay đổi cấu trúc. 

### Minh họa luồng self-healing

```text
OSD lỗi / OSD mới / topology đổi
        ↓
OSD Map và placement thay đổi
        ↓
PG bị degraded hoặc remapped
        ↓
Peering xác định primary và authoritative state
        ↓
Recovery / Backfill / Rebalancing
        ↓
PG quay lại trạng thái active+clean
```
## 7. Các tham số logic quan trọng ở mức khái niệm
### 7.1 `size`
- Với replicated pools, `size` là **số lượng copies mong muốn của object**. RHCS 5 Storage Strategies Guide mô tả replicated pool chính là *desired number of copies or replicas of an object*. Tăng size làm tăng mức chịu lỗi nhưng cũng tăng raw storage overhead và chi phí write path.

### 7.2 `min_size`
- `min_size` là ngưỡng tối thiểu để pool tiếp tục chấp nhận write an toàn theo policy hiện hành. Đây là một phần của mô hình “dịch vụ còn tiếp tục hay phải dừng để bảo toàn dữ liệu”. Trong các tài liệu RHCS và Ceph, `size` và `min_size` luôn đi liền khi nói về *replicated pool safety policy*.
### 7.3 Failure domain
- Nhiều bản sao hoặc nhiều EC chunks thôi chưa đủ cho HA nếu chúng rơi vào cùng failure domain. CRUSH placement policies phải tách replicas hoặc EC chunks qua các failure domains khác nhau. Điều này khiến failure domain trở thành một phần cốt lõi của tính chất durability.
### 7.4 `nearfull`, `full`, `backfillfull`

Khi cluster gần đầy, durability không còn chỉ là chuyện “còn replicas hay không”, mà còn là chuyện cluster còn đủ không gian để tiếp tục duy trì và khôi phục redundancy hay không. RHCS 5 Configuration Guide cảnh báo rằng khi cluster đến gần `mon_osd_full_ratio`, Ceph ngăn đọc và ghi lên OSDs như một biện pháp an toàn để loại trừ việc mất mát dữ liệu; docs cũng lưu ý để cluster chạm full ratio sẽ hy sinh tính HA của chính nó. 
=> Đây là điểm rất quan trọng: một cluster còn đang chạy chưa chắc còn đang ở tình trạng an toàn để tự chữa lành khi có lỗi mới.
### 7.5 Vì sao một cluster “vẫn chạy” chưa chắc đã “vẫn an toàn”

- Từ các trạng thái như `active+degraded`, từ tình trạng khi cluster gần full, và từ việc recovery/backfill có thể kéo dài, có thể rút ra một nguyên tắc cốt lõi:  cụm vẫn hoạt động không đồng nghĩa với durability đã được phục hồi hoàn toàn. Đây là lý do tại sao nhìn `ceph -s` chỉ để thấy client I/O còn đi được là chưa đủ; phải nhìn cả PG health, redundancy state và khả năng cluster còn room để self-heal hay không.

> Keynote: Trong Ceph, còn hoạt động được không đồng nghĩa với đã an toàn trở lại. Một PG có thể active nhưng vẫn degraded; client vẫn có thể đọc hoặc ghi, nhưng mức dư thừa dữ liệu chưa được phục hồi hoàn toàn. Đây là điểm rất quan trọng để hiểu durability: Ceph phân biệt rõ giữa dịch vụ còn chạy và dữ liệu đã quay về trạng thái an toàn tối ưu. Vì vậy, khi nhìn tình trạng cluster, không được dừng ở câu hỏi “có phục vụ I/O không”, mà phải nhìn tiếp “độ dư thừa đã đủ chưa, scrub có sạch chưa, recovery đã xong chưa”.
## 8. So sánh Pacific / RHCS 5 và Squid / RHCS 8
Về bản chất, durability model của Ceph không thay đổi giữa Pacific và Squid:
- replicated pools vẫn dựa trên primary-copy model
- erasure-coded pools vẫn chia object thành K+M chunks
- primary OSD vẫn là điểm vào của write path
- PG vẫn là đơn vị trung gian để placement, recovery và scrub
- scrub/deep-scrub vẫn là cơ chế integrity nền.

Điểm thay đổi chủ yếu nằm ở cách docs diễn giải và đóng gói. Squid docs và RHCS 8 docs thường nhấn mạnh rõ hơn:

- data integrity by scrubbing or CRC checks
- sự phân biệt giữa backfill và recovery
- việc peering phải hoàn tất trước khi write operation có thể tiếp tục
- vai trò của full ratios và các guardrails khi cluster gần hết dung lượng.

Nói cách khác, với file kiến thức cá nhân, bạn nên xem Pacific/RHCS 5 là nền diễn giải “kinh điển” và Squid/RHCS 8 là lớp diễn giải mới rõ hơn ở một số chủ đề. Không nên hiểu sự khác biệt này là “Ceph đổi hẳn durability model”, vì phần lõi vẫn giữ nguyên.

### Bảng phân biệt ngắn
| Chủ đề                       | Pacific / RHCS 5                                          | Squid / RHCS 8                                                 | Kết luận                              |
| ---------------------------- | --------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------- |
| Replicated write path        | Primary OSD nhận write, secondary ACK, primary ACK client | Giữ nguyên                                                     | Không đổi bản chất                    |
| Erasure coding               | `K+M` chunks, primary nhận mọi write                      | Giữ nguyên                                                     | Không đổi bản chất                    |
| Scrub / deep-scrub           | Có, nhưng thường đọc như OSD config feature               | Nhấn mạnh rõ hơn như một phần của integrity                    | Docs mới diễn giải rõ hơn             |
| Recovery / backfill          | Có đầy đủ                                                 | Giải thích rõ hơn về peering trước write và tác động hiệu năng | Không đổi bản chất, rõ hơn ở docs mới |
| ([Red Hat Documentation][1]) |                                                           |                                                                |                                       |

[1]: https://docs.redhat.com/en/documentation/red_hat_ceph_storage/5/html-single/architecture_guide "Architecture Guide | Red Hat Ceph Storage | 5"

## 9. Những hiểu lầm phổ biến
### 9.1 Replication không chỉ là “copy nhiều bản”
Một hiểu lầm phổ biến là cho rằng replication chỉ đơn giản là “copy nhiều bản ra nhiều OSD”. Cách hiểu đó quá nông. Replication trong Ceph là một write protocol có primary điều phối, có ACK path, có PG state, có acting set, và có failure domains do CRUSH quyết định. Nếu chỉ hiểu replication như “copy file”, người đọc sẽ bỏ qua logic consistency của PG và vai trò của primary OSD.
### 9.2 EC không chỉ là “RAID phân tán”
Hiểu lầm thứ hai là xem erasure coding như “RAID phân tán”. EC đúng là có điểm tương tự RAID ở chỗ dùng parity/coding chunks, nhưng trong Ceph nó là một pool-level durability model gắn chặt với CRUSH, PG, acting set và failure domains. EC trong Ceph không phải chỉ là parity trong một enclosure hay một host, mà là placement-aware coding trên toàn cluster.
### 9.3 `active` không đồng nghĩa với clean
Hiểu lầm thứ ba là cho rằng một PG `active` tức là đã hoàn toàn an toàn. RHCS docs chỉ rõ PG có thể `active+degraded`; client vẫn có thể I/O, nhưng redundancy chưa đủ hoặc chưa được xác nhận hoàn toàn. `active` vì vậy phản ánh khả năng phục vụ I/O, còn clean mới phản ánh trạng thái fully synchronized theo policy hiện hành.
### 9.4 ACK thành công không nên hiểu quá đơn giản là “mọi thứ đã hoàn hảo vĩnh viễn”
Hiểu lầm cuối cùng là xem scrub là việc “nên có thì bật”. Thực ra scrub/deep-scrub là lớp bảo vệ integrity rất quan trọng, tương tự fsck ở object layer. Không có scrub đúng cách, cluster có thể vẫn có nhiều copies nhưng không phát hiện sớm object mismatch hoặc corruption âm thầm.


> Data durability trong Ceph được xây dựng từ nhiều lớp phối hợp: pool type quyết định replicated hay erasure-coded, primary OSD điều phối write path, PG cung cấp lớp trung gian để placement và recovery có thể scale, CRUSH tách replicas hoặc shards qua các failure domains, còn scrub/deep-scrub bảo vệ integrity theo thời gian. Đây không phải là một “feature” đơn lẻ, mà là kết quả của cả một kiến trúc object storage phân tán.