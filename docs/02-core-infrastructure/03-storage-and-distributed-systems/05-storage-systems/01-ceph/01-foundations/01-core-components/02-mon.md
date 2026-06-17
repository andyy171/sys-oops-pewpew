# MON (Ceph Monitor)

## 1. MON là gì và vì sao MON là nền của control plane trong Ceph

Trong Ceph, **MON (Ceph Monitor)** là daemon giữ vai trò nền tảng của **control plane**. Nếu OSD là nơi dữ liệu thực sự được đọc, ghi và nhân bản, thì MON là nơi cluster duy trì **nguồn chân lý** về trạng thái toàn cục: thành viên nào đang tồn tại, map nào đang có hiệu lực, cluster có quorum hay không, và đâu là phiên bản mới nhất của trạng thái cluster. Ceph docs mô tả monitor là tiến trình duy trì **cluster membership, configuration và state** với tính bền vững và độ tin cậy rất cao; các monitor cùng nhau tạo thành một cụm đồng thuận dựa trên Paxos. 

Điều quan trọng nhất cần hiểu là MON **không nằm trên data path của từng lần I/O**. Client không gửi mọi thao tác đọc ghi qua MON. Thay vào đó, MON giữ và phân phối **cluster maps**, còn client và daemon khác dùng các map đó để tự tính placement và nói chuyện trực tiếp với OSD phù hợp. Chính vì vậy, MON vừa rất quan trọng, vừa không phải là bottleneck data path nếu cluster vận hành đúng. Ceph docs về monitor và architecture đều nhấn mạnh monitor là **single source of truth for the cluster map**, còn client sau khi có map sẽ tự tính object location. 

Về mặt tư duy kiến trúc, MON là thành phần giúp Ceph giải quyết bài toán khó nhất của hệ phân tán: **cùng nhìn thấy một trạng thái logic nhất quán về cluster**, trong khi data path vẫn được phân tán tối đa. Đây là lý do mọi tài liệu nghiêm túc về Ceph đều đặt MON vào vùng lõi của kiến trúc, ngay cạnh OSD, dù MON không lưu dữ liệu người dùng như OSD. 

## 2. Vai trò cốt lõi của MON trong cluster

MON có ba vai trò nền tảng.

Thứ nhất, MON giữ **bản sao chủ của cluster maps**. Ceph docs về monitor configuration và add/remove monitors đều nói rõ monitor giữ master copy của cluster map và là single source of truth cho cluster map. Khi cluster state thay đổi, monitors là nơi đồng thuận về phiên bản map mới. 

Thứ hai, MON duy trì **quorum và consensus**. Khi cluster có nhiều monitors, chúng dùng một biến thể của Paxos để thống nhất về maps và các thông tin quan trọng khác. Điều này đảm bảo rằng cluster không rơi vào tình trạng mỗi daemon nhìn thấy một “sự thật” khác nhau về membership hay placement. RHCS 5 và RHCS 8 đều mô tả rất rõ: để có consensus cần **đa số monitors chạy và reachable**, ví dụ 2/3 hoặc 3/5. 

Thứ ba, MON quản lý **configuration database** của cluster trong các bản hiện đại. RHCS 5 và RHCS 8 Configuration Guides đều nêu rằng Ceph Monitor quản lý cơ sở dữ liệu cấu hình tập trung của Ceph, nơi lưu các option cấu hình cho toàn cluster; thứ tự ưu tiên option đặt cluster configuration database cao hơn local `ceph.conf`. Đây là điểm rất quan trọng khi học Ceph hiện đại, vì nó cho thấy MON không chỉ là nơi giữ map, mà còn là nơi tập trung một phần lớn trạng thái cấu hình runtime của cluster. :contentReference[oaicite:5]{index=5}

### Tóm tắt vai trò của MON

- Giữ **cluster maps** và đồng thuận về phiên bản mới nhất của chúng. 
- Thiết lập **quorum** và **consensus** bằng Paxos. 
- Là nơi quản lý **configuration database** của cluster trong Ceph hiện đại. 
- Cung cấp nền control plane để client và daemon khác biết cluster đang ở trạng thái nào. 

## 3. MON và cluster maps

MON gắn với cluster maps chặt đến mức gần như không thể giải thích MON mà tách khỏi cluster map. Trong Ceph, maps không phải là dữ liệu trang trí; chúng là mô hình vận hành của cluster. Khi MON giữ bản sao chủ của maps, điều đó có nghĩa MON giữ **trạng thái logic mà mọi thành phần khác phải dựa vào** để hoạt động nhất quán. Ceph monitor docs ghi rõ các update tới monitor map hay các map khác đều đi qua consensus, và strict consistency cũng áp dụng cho các update đó. 

Trong thực tế, MON liên quan trực tiếp hoặc gián tiếp tới các map sau:
- **Monitor Map**
- **OSD Map**
- **PG Map**
- **CRUSH Map**
- và trong bức tranh đầy đủ của Ceph còn có các map/service state khác như MDS-related state khi dùng CephFS. Ceph glossary và architecture docs upstream vẫn xem cluster map như tập hợp nhiều map thành phần, trong khi một số RHCS docs về cấu hình nhấn mạnh nhiều hơn vào monitor map, OSD map và PG map ở góc nhìn quản trị. Đây là khác biệt về cách đóng gói tài liệu, không phải thay đổi bản chất kiến trúc.

Điểm cần nhớ là MON **không giữ vị trí từng object như một metadata lookup server cho mỗi I/O**. MON giữ maps; còn object placement được client/OSD tính ra từ maps và CRUSH. Vì vậy, MON là trung tâm của “state truth”, không phải trung gian cho “mọi data request”. Đây là ranh giới cực kỳ quan trọng giữa control plane và data plane trong Ceph.
### Minh họa luồng MON với cluster maps

```text
OSDs / MGR / Clients / other daemons
              ↓
        Ceph Monitors
              ↓
  Consensus về cluster state và map epoch
              ↓
   Cluster maps mới nhất được công bố
              ↓
 Clients và daemons khác dùng map để hành động
```

> Keynote: MON không lưu dữ liệu người dùng, nhưng lại giữ thứ có thể gọi là sự thật chính thức của cluster. Điểm phải ghi nhớ là: Ceph không cần MON để chở dữ liệu đi, nhưng cần MON để mọi thành phần còn lại cùng biết cluster đang ở trạng thái nào. Nói đơn giản, MON không phải là “máy chủ lưu trữ”, mà là nơi cluster đồng ý với chính nó. Nếu OSD là cơ bắp dữ liệu, thì MON là phần giữ cho toàn hệ thống không rơi vào tình trạng mỗi thành phần tin vào một phiên bản sự thật khác nhau.

## 4. Quorum và Paxos: vì sao MON cần số lẻ và cần đa số

- Quorum là khái niệm trung tâm khi nói về MON. Khi cluster có nhiều monitors, chúng dùng Paxos để đạt đồng thuận về master cluster map, và muốn có sự đồng thuận thì phải có đa số monitors đang chạy và nhìn thấy nhau. Điều này giải thích vì sao cấu hình production điển hình luôn là 3 hoặc 5 monitors, thay vì 2. Với 2 monitors, mất 1 monitor là mất luôn đa số; với 3 monitors, cluster vẫn giữ được quorum khi mất 1 monitor.

- Ceph docs về add/remove monitors và common settings còn khuyến nghị rõ rằng production cluster nên có ít nhất 3 monitors. RHCS Operations Guide cũng yêu cầu ít nhất 3 monitors trên các host tách biệt để có support production, và health checks của upstream docs còn cảnh báo việc colocate nhiều monitors trên cùng node làm tăng rủi ro mất quorum khi host, rack hoặc network failure xảy ra. Điều này cho thấy quorum không chỉ là bài toán số học, mà còn là bài toán failure domain của chính control plane.

- Paxos trong Ceph giải quyết một việc rất thực tế: mọi monitor trong quorum phải đồng ý về cùng một phiên bản của map và trạng thái cluster. Ceph docs nhấn mạnh *strict consistency applies to updates to the monmap*, và mọi thay đổi như thêm hoặc xóa monitor đều phải được tất cả monitors trong quorum nhìn giống nhau. Đây là nền khiến MON trở thành nguồn chân lý đáng tin cậy của cluster.

    - Dưới 2 MON thì không thể chịu lỗi được nếu mất mon nào đó, vì mất 1 là mất luôn quorum. Với 3 MON thì chịu lỗi được 1 MON vẫn giữ được quorum , với 5 MON thì chịu lỗi được 2 MON vẫn giữ được quorum. Tương tự cứ tăng 2 MON thì tăng số MON chiu lỗi được thêm 1.

## 5. MON và client flow

- Client cần MON trước khi có thể làm việc đúng với cluster: client phải biết endpoints của monitors, sau đó lấy cluster map hiện tại để biết cluster đang có trạng thái gì. Tuy nhiên, sau bước đó client không cần tiếp tục đi qua MON cho từng read/write. Client dùng map để tự tính placement và kết nối trực tiếp tới OSD tương ứng. Đây là một điểm quan trọng để tránh hiểu lầm rằng MON là API gateway của Ceph.

- Từ góc nhìn vận hành, điều này dẫn tới một nguyên tắc đơn giản nhưng quan trọng: MON phải khỏe trước khi cluster data path được tin cậy đầy đủ. RHCS administration docs từ các bản trước đã nhấn mạnh rằng cần kiểm tra monitor quorum sau khi khởi động cluster và trước khi đọc/ghi dữ liệu. Lý do không phải vì MON nằm trên mọi I/O, mà vì không có quorum thì cluster không còn nguồn chân lý đáng tin cậy về state, map epoch và authority. Nếu MON không khỏe, client có thể lấy map lỗi thời hoặc không lấy được map nào, dẫn tới read/write failures hoặc thậm chí data loss nếu client tính placement sai. Đây là lý do tại sao health checks của Ceph luôn kiểm tra monitor quorum và monitor status như một trong những chỉ số đầu tiên về sức khỏe cluster.


### Minh họa MON trong client flow

```
Client
  ↓
Kết nối một MON
  ↓
Nhận cluster map hiện hành
  ↓
Tự tính object/PG placement
  ↓
Kết nối trực tiếp tới OSD phù hợp
```
## 6. MON và authentication / bootstrap trust

- MON cũng nằm ở tâm của trust bootstrap trong cluster. Muốn client hoặc daemon khác làm việc an toàn với cluster, trước hết chúng phải biết đang nói chuyện với đúng cluster nào, đúng monitor nào, và dùng credential nào. RHCS Operations Guide và Configuration Guides đều nhắc tới việc phân phối client.admin keyring, cấu hình _admin label trong môi trường cephadm, và vai trò của monitor trong việc quản lý configuration state và các keyring/cluster identity đi kèm.

- Ở mức conceptual, MON là nơi giúp cluster trả lời ba câu hỏi:

    - đây có phải đúng cluster không
    - trạng thái cluster hiện tại là gì
    - cấu hình nào đang có hiệu lực để các daemon khác cùng hiểu giống nhau

> MON là một phần quan trọng của bootstrap trust: không có monitor endpoints hợp lệ và cluster identity hợp lệ, client không thể lấy map đúng để tiếp tục data path một cách an toàn.



## 7. MON và configuration database

Một điểm rất quan trọng ở Ceph hiện đại là **MON quản lý configuration database**. RHCS 5 và RHCS 8 Configuration Guides nêu rất rõ rằng *Ceph Monitor manages a configuration database of Ceph options, centralizing configuration management for the entire cluster*. Hai bản guide này cũng cho biết thứ tự ưu tiên option đặt **cluster configuration database cao hơn local ceph.conf**. Điều đó có nghĩa MON không chỉ giữ map, mà còn giữ một phần lớn “sự thật cấu hình” của cluster.

> Đây là khác biệt lớn trong cách người học nên nhìn MON ở thời Ceph hiện đại. Trong các tài liệu cũ hơn hoặc trong kinh nghiệm cũ, nhiều người quen nghĩ ceph.conf là trung tâm cấu hình. Nhưng trong RHCS 5 và RHCS 8, cấu hình tập trung qua monitor-backed config database đã trở thành cách hiểu đúng hơn về runtime configuration. Điều này không làm MON biến thành service cấu hình thuần túy; đúng hơn, nó làm MON trở thành nút neo của cả state lẫn config authority.

## 8. Monitor Map và election

- Monitor map, hay monmap, là map mô tả chính các monitors trong cluster: danh tính, địa chỉ, cổng, epoch và metadata liên quan. Ceph docs nhấn mạnh rằng update tới monmap cũng phải đi qua Paxos giống như các update monitor state khác. Điều này giúp toàn bộ quorum luôn nhìn thấy cùng một tập monitors hợp lệ.

- Khi cluster cần elect leader hoặc xử lý network split, monitors dùng election strategy để đi đến một leader hợp lệ. RHCS 5 Operations Guide nhắc rõ có thể cấu hình monitor election strategy, còn upstream Ceph có docs riêng về monitor elections và thuật toán election. 
> Chỉ cần hiểu rằng election là lớp điều phối nội bộ của monitor quorum để cluster vẫn có một hướng quyết định nhất quán khi trạng thái mạng hoặc thành viên thay đổi. Không cần đi sâu vào thuật toán election order ở đây.

## 9. Khi MON fail, chuyện gì xảy ra

- Vì MON là control plane authority, failure của MON được đánh giá theo góc quorum chứ không theo dung lượng dữ liệu. Nếu cluster có 3 MON và mất 1 MON, cluster thường vẫn tiếp tục hoạt động bình thường về mặt đồng thuận vì còn 2/3. Nếu mất quá số MON mà quorum yêu cầu, cluster có thể bị stall ở các thao tác cần authoritative cluster state. Upstream docs và RHCS docs đều khuyến nghị số lẻ monitors và tối thiểu 3 monitors cho production chính là để kiểm soát failure mode này.

=> Điều này cũng giải thích vì sao MON phải được đặt trên failure domains hợp lý. Upstream health checks cảnh báo *colocating multiple monitors on the same node or same IP increases the risk that a single host or network failure prevents quorum*. Từ góc nhìn thiết kế, MON cần phân tán không phải vì tải CPU/memory quá lớn, mà vì mất quorum control plane có thể stall cluster operations. 

> Tóm lại các Mon nên cài trên các host tách biệt, tốt nhất là trên các rack tách biệt, để giảm rủi ro mất quorum do failure của host hoặc network.



## 10. MON trong Pacific / RHCS 5 và Squid / RHCS 8

- Về bản chất, vai trò của MON không thay đổi giữa Pacific và Squid hay RHCS 5 và RHCS 8. Cả hai thế hệ tài liệu đều mô tả MON là:

    - nguồn chân lý của cluster map
    - thành phần dùng Paxos để đạt consensus
    - daemon cần quorum theo đa số
    - nền cho high availability của control plane.

- Điểm thay đổi hoặc được nhấn mạnh rõ hơn nằm ở cách docs hiện đại diễn giải hai vấn đề.

    - Thứ nhất là configuration database. RHCS 5 đã nói rõ monitor manages config database, và RHCS 8 tiếp tục nhấn mạnh mạnh hơn, phản ánh cách Ceph hiện đại vận hành với config store tập trung thay vì dựa chủ yếu vào `ceph.conf`.

    - Thứ hai là cephadm / orchestrator context. RHCS 5 và RHCS 8 Operations Guides đều đặt việc triển khai và quản trị cluster hiện đại trong bối cảnh cephadm, nơi manager daemon và orchestrator làm rất nhiều việc day-2. Tuy nhiên, điều này không thay đổi bản chất của MON. MON vẫn là monitor quorum của cluster; chỉ là cách daemon được deploy, quản trị và phối hợp với hệ sinh thái xung quanh hiện đại hơn.

## 11. Những hiểu lầm phổ biến về MON

- Hiểu lầm phổ biến nhất là nghĩ rằng MON là nơi mọi read/write phải đi qua. Điều này sai. MON giữ cluster maps và consensus; data path thực sự đi từ client tới OSD sau khi client đã có map đúng. Nếu không tách control plane khỏi data plane, rất dễ hiểu sai toàn bộ kiến trúc Ceph.

- Hiểu lầm thứ hai là nghĩ “nhiều MON hơn luôn tốt hơn”. Thực tế, MON cần đủ để có quorum bền vững, thường là 3 hoặc 5. Tăng MON mà không có lý do rõ ràng có thể làm control plane phức tạp hơn mà không mang lại lợi ích tương xứng. Các docs chính thống nhất quán ở việc khuyến nghị ít nhất 3 cho production, chứ không phải càng nhiều càng tốt.

- Hiểu lầm thứ ba là xem MON như nơi “lưu dữ liệu cluster” giống OSD. MON đúng là lưu state, membership, configuration và maps một cách durable, nhưng nó không lưu dữ liệu object của người dùng theo nghĩa data plane. Đây là ranh giới quan trọng giữa MON và OSD.

- Hiểu lầm cuối cùng là tiếp tục coi `ceph.conf` là trung tâm cấu hình duy nhất trong cluster hiện đại. RHCS 5 và 8 đều chỉ ra cluster configuration database do MON quản lý mới là điểm neo quan trọng của runtime configuration. Nếu không cập nhật cách hiểu này, rất dễ viết tài liệu hoặc vận hành cluster theo mô hình cũ.