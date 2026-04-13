# OSD (Object Storage Daemon)

## 1. OSD là gì và vì sao OSD là trung tâm của Ceph

Trong Ceph, **OSD (Object Storage Daemon)** là thành phần chịu trách nhiệm trực tiếp đối với dữ liệu người dùng. Ceph architecture docs mô tả rất rõ rằng mọi dữ liệu đi vào cluster cuối cùng đều được lưu dưới dạng **RADOS objects**, và mỗi object được đặt trên một Object Storage Device; các Ceph OSD Daemons xử lý **read, write và replication operations** trên các storage drives đó. Vì vậy, nếu MON là nơi giữ trạng thái logic của cluster, thì OSD là nơi biến trạng thái đó thành I/O thực tế trên đĩa. :contentReference[oaicite:0]{index=0}

OSD không chỉ là “một tiến trình gắn với một ổ đĩa”. Ở mức kiến trúc, OSD là điểm giao nhau của nhiều luồng quan trọng nhất trong Ceph: data path của client, placement qua PG và CRUSH, durability thông qua replication hoặc erasure coding, integrity thông qua scrub/deep-scrub, và self-healing thông qua peering, recovery và backfill. Đây là lý do file OSD phải đứng đầu nhánh `01-core-components`: hiểu OSD trước thì mới hiểu MON/MGR/BlueStore đúng vai trò của chúng trong bức tranh lớn. :contentReference[oaicite:1]{index=1}

Về mặt phiên bản, vai trò cốt lõi của OSD **không thay đổi** giữa Ceph Pacific và Squid, cũng như giữa RHCS 5 và RHCS 8. Những khác biệt chủ yếu nằm ở cách docs mới nhấn mạnh rõ hơn về BlueStore là backend mặc định, về configuration database thay cho `ceph.conf`, và về một số cách diễn giải xung quanh state/reporting, nhưng mô hình “OSD là daemon lưu dữ liệu, xử lý read/write/replication, và tham gia recovery/scrub” vẫn giữ nguyên. :contentReference[oaicite:2]{index=2}

## 2. OSD trong data path của Ceph
- Từ góc nhìn client, **OSD là nơi client cuối cùng phải nói chuyện để đọc hoặc ghi dữ liệu**. RHCS 8 Architecture Guide nêu rằng client interfaces đọc và ghi dữ liệu vào Ceph cluster, còn để giao tiếp được với cluster thì client cần biết configuration, pool name, user name và secret key; sau đó client dùng cluster map để tính placement và kết nối trực tiếp tới OSD phù hợp. Điều này có nghĩa data path thực tế của Ceph không đi qua MON hay MGR ở mỗi lần I/O, mà đi trực tiếp tới OSD sau khi placement đã được tính toán.
    - Với write path, OSD đầu tiên mà client chạm vào là **primary OSD** của placement group tương ứng. RHCS 5 và RHCS 8 architecture guides cùng mô tả rằng *primary OSD nhận write request, sau đó điều phối việc ghi local và ghi sang các secondary OSDs hoặc các OSD giữ EC shards*. Như vậy, OSD không chỉ là nơi “lưu block/object”, mà còn là **thành phần thi hành giao thức durability của Ceph**. 
    - Với read path, client cũng dựa vào cluster map và placement calculation để tìm primary OSD hiện hành của PG chứa object cần đọc. Nếu primary thay đổi vì OSD fail hoặc cluster remap, client chỉ cần map mới để đi tới primary mới. OSD vì vậy là điểm cuối trực tiếp của read path, nhưng đồng thời cũng là thành phần mà cluster có thể thay đổi vai trò linh hoạt khi topology hoặc health thay đổi. 
### Luồng tổng quát của OSD trong data path

```text
Client
  ↓
Cluster map + CRUSH + PG calculation
  ↓
Primary OSD
  ↓
Replica OSDs hoặc EC shard OSDs
  ↓
Local persistence trên backend của OSD
```

## 3. OSD và placement

OSD không tự quyết định dữ liệu nào thuộc về nó một cách tùy ý. Placement trong Ceph là kết quả của pool policy, PG calculation, OSD map và CRUSH map. Tuy nhiên, khi placement đã được tính ra, OSD trở thành đơn vị thực thi cuối cùng. Pacific architecture docs và RHCS architecture guides đều cho thấy object được ánh xạ vào PG, rồi PG được ánh xạ tới một tập OSD; một OSD trong tập đó đóng vai trò primary, các OSD còn lại đóng vai trò replica hoặc shard members.

Điều này dẫn tới một nguyên tắc rất quan trọng: OSD luôn phải được hiểu trong quan hệ với PG chứ không nên hiểu như “một daemon giữ một danh sách object độc lập”. Ceph không quản trị durability và recovery ở mức từng object một cách rời rạc; thay vào đó, OSD nhận trách nhiệm cho các placement groups. Việc thêm hay xóa OSD làm thay đổi placement của các PG, và từ đó kéo theo rebalancing, backfill hoặc recovery. Chính mối liên hệ giữa OSD và PG làm cho Ceph có thể scale mà không cần metadata table trung tâm cho từng object.

### 3.1. OSD, Acting Set, Up Set và primary OSD

Mỗi PG tại một thời điểm gắn với một nhóm OSD. Trong nhóm đó, primary OSD là đầu mối nhận read/write từ client. Các OSD còn lại là secondary replicas hoặc shard holders. Khi cluster ổn định, tập OSD “nên” giữ PG và tập OSD “đang” giữ PG thường trùng nhau; khi có failure hoặc remap, chúng có thể tạm thời khác nhau, và cluster phải peer để đưa state về một hình thái nhất quán hơn. OSD vì vậy không chỉ là storage endpoint, mà còn là thành phần phải biết mình đang giữ vai trò gì trong PG hiện tại.

### 3.2. Vì sao client nói chuyện trực tiếp với OSD

Một trong những lý do Ceph mở rộng tốt là client không cần gửi mọi I/O qua một controller trung tâm. Sau khi có cluster map, client tự tính ra object location và nói chuyện trực tiếp với primary OSD. Điều này làm giảm bottleneck ở control plane và biến OSD thành nơi data path thực sự diễn ra. Từ góc nhìn học tập, đây là chìa khóa để hiểu vì sao OSD phải gánh nhiều trách nhiệm như vậy: nó không chỉ “nhận dữ liệu”, mà còn phải giữ consistency, report state, participate in peering, scrub dữ liệu và phối hợp với monitors.

## 4. OSD và durability

Nếu chỉ nhìn OSD như một daemon ghi object xuống ổ đĩa thì sẽ bỏ sót phần quan trọng nhất của nó: durability. Trong Ceph, durability không nằm ở mỗi bản sao riêng lẻ, mà nằm ở việc OSDs phối hợp theo đúng pool policy để đưa dữ liệu tới mức redundancy mong muốn. OSD là nơi hiện thực hóa replicated pool hoặc erasure-coded pool thành hành động cụ thể.

### 4.1 OSD trong replicated pools

Trong replicated pools, primary OSD nhận object từ client, ghi local và chuyển object tới các secondary OSDs của PG. Chỉ khi primary nhận đủ acknowledgments từ secondaries và tự nó hoàn tất phần ghi của mình, write mới được xem là thành công từ góc nhìn client. Điều này có nghĩa OSD chính là thành phần biến “replication factor” từ một con số cấu hình thành một chuỗi hành động cụ thể trong cluster.

### 4.2 OSD trong erasure-coded pools

Trong erasure-coded pools, primary OSD vẫn là entry point của write path, nhưng thay vì gửi full replicas, nó điều phối việc chia object thành data chunks và coding chunks, sau đó đặt từng chunk lên các OSD phù hợp. Tức là ở cả replicated lẫn EC pools, OSD vẫn là đơn vị thực thi durability policy; khác biệt nằm ở hình thức dữ liệu được phân phối, chứ không ở vai trò cốt lõi của primary OSD.

### 4.3 ACK path và ý nghĩa của nó

ACK path là một phần rất quan trọng để hiểu “write đã an toàn đến mức nào”. Trong replicated model, primary OSD không trả thành công cho client ngay khi chỉ mới nhận request, mà sau khi write đã đạt mức xác nhận phù hợp từ các OSD tham gia placement. Điều này không có nghĩa cluster ngay lập tức ở trạng thái clean trong mọi trường hợp, nhưng nó có nghĩa write đã được đưa tới mức durability theo policy hiện hành của pool. Nhìn từ vai trò OSD, ACK path là ranh giới giữa “I/O đã tới cluster” và “cluster đã chấp nhận chịu trách nhiệm cho I/O đó”.

### Bảng tóm tắt vai trò của OSD theo loại pool
| Kiểu pool                    | Vai trò của primary OSD                                | Vai trò của secondary OSDs                    |
| ---------------------------- | ------------------------------------------------------ | --------------------------------------------- |
| Replicated                   | Nhận write, ghi local, gửi replicas, tổng hợp ACK      | Lưu replica và xác nhận về primary            |
| Erasure-coded                | Nhận write, điều phối chunking/placement, tổng hợp ACK | Lưu data/coding chunks và xác nhận về primary |
| ([Red Hat Documentation][1]) |                                                        |                                               |

[1]: https://docs.redhat.com/en/documentation/red_hat_ceph_storage/5/html-single/architecture_guide/index "Architecture Guide | Red Hat Ceph Storage | 5 | Red Hat Documentation"


## 5. OSD và cluster state
OSD là daemon vừa tham gia data path, vừa tham gia state path của cluster. RHCS 5 Configuration Guide dành hẳn một chương cho tương tác giữa Monitor và OSD, trong đó liệt kê các chủ đề như OSD heartbeat, reporting an OSD as down, reporting a peering failure và OSD reporting status. Chỉ riêng điều này cũng cho thấy OSD không phải storage process thuần túy, mà là một daemon phải liên tục “nói chuyện” với phần control plane của cluster.

### 5.1 Heartbeat
Ceph dựa vào heartbeat giữa OSDs để phát hiện liveness và network health ở tầng data path. Ceph là distributed storage system và phụ thuộc vào mạng cho OSD peering, replication, recovery from faults và periodic heartbeats; networking issues có thể dẫn tới OSD latency và flapping OSDs. Điều đó có nghĩa **heartbeat không phải cơ chế phụ trợ, mà là một phần nền của state control trong OSD layer.**

### 5.2 OSDMap updates
Khi OSD `up`, `down`, `in`, `out`, cluster map thay đổi. MON giữ master copy của cluster state, nhưng OSD là nguồn phát sinh phần lớn các thay đổi thực tế liên quan tới data path: OSD chết, OSD quay lại, peering fail, network flap, full ratio impact, tất cả đều làm OSDMap và PG state thay đổi. Nói cách khác, OSD vừa chịu tác động của map, vừa là tác nhân làm map phải tăng epoch.

### 5.3 OSD khi peer, recover và backfill
Khi cluster thay đổi, OSD không ngồi yên chờ placement “tự ổn định”. Chúng phải peer để xác định *authoritative history* của PG, recover khi một thành viên quay lại out-of-sync, và backfill khi PG remap sang OSD mới hoặc placement mới. OSD là đơn vị trực tiếp tham gia các cơ chế đó chứ không chỉ “chịu kết quả của chúng”.

## 6. OSD internals
OSD có thể được hiểu như một daemon gồm bốn lớp trách nhiệm chồng lên nhau:

- **storage responsibility:** lưu object xuống backend
- **placement responsibility:** giữ các PG được gán cho nó
- **durability responsibility:** phối hợp với primary/secondary peers
- **state responsibility:** báo cáo health, tham gia peering, scrub, recovery

> Cách nhìn này giúp tránh việc đồng nhất OSD với một “process ghi file”. OSD là daemon lưu trữ phân tán thông minh, nằm đúng ý “intelligent storage nodes” mà RHCS architecture guides muốn nhấn mạnh khi mô tả Ceph.

### 6.1 Object store backend

Reef architecture docs nêu rằng backend mặc định hiện nay là BlueStore, và BlueStore stores objects in a monolithic, database-like fashion. Đồng thời, Ceph OSD Daemons store data as objects in a flat namespace, nghĩa là object không được lưu như một cây thư mục kiểu filesystem thông thường. Đây là điểm cần giữ đúng ngữ cảnh: OSD là daemon quản lý object logic, còn backend quyết định cách object đó được persist xuống thiết bị vật lý.

### 6.2 PG log và update history

Muốn OSDs peer, recover và xác định authoritative state, chúng không thể chỉ nhìn “đĩa hiện có gì” theo kiểu thô sơ. OSD còn duy trì lịch sử cập nhật của các PG ở mức đủ để hỗ trợ peering và recovery. Trong file này, bạn chỉ cần hiểu rằng PG log là một lớp ghi nhận update history cần thiết để replicas hội tụ lại sau lỗi và để cluster phân biệt object nào là mới nhất khi có divergence tạm thời. Phần rất sâu của log-based PG sẽ quay lại ở file peering/recovery.

### 6.3 Transaction path

OSD không chỉ “ghi object xong là xong”. Write path bên trong OSD bao gồm tiếp nhận operation, áp dụng thứ tự của update cho PG, tương tác với backend persistence, và chỉ sau đó mới tới bước ACK hợp lệ. Trong các release hiện đại, cách triển khai cụ thể phụ thuộc mạnh vào BlueStore; vì vậy file này chỉ giữ transaction path ở mức khái niệm, còn phần backend persistence chi tiết để sang 06-bluestore.md.

### 6.4 Logging / journaling nên hiểu thế nào trong file OSD này
- Pacific OSD Config Reference vẫn còn nhắc tới osd journal size cho Filestore, cho thấy tài liệu cũ vẫn mang dấu vết của thời Filestore. Tuy nhiên, ở các release hiện đại, backend mặc định là BlueStore. Vì vậy, khi nói “logging/journaling flow” trong ngữ cảnh hiện tại, không nên đóng khung theo cách hiểu cũ về Filestore journal. Đúng hơn, trong file OSD này nên hiểu nó là:
    - lớp ghi nhận update history của PG
    - lớp persistence / transaction path bên trong OSD
    - quan hệ giữa write ordering và backend commit semantics

> Keynote: OSD không chỉ là “một tiến trình gắn với một ổ đĩa”, mà là nơi Ceph biến toàn bộ logic trừu tượng của cluster thành hành động thật trên dữ liệu. Tất cả những gì bạn học ở tầng trên như pool, PG, CRUSH, replication, erasure coding, scrub, recovery, backfill… cuối cùng đều phải đi qua OSD để trở thành hiện thực. Vì vậy, OSD là nơi giao nhau của ba thế giới: luồng dữ liệu đi, durability, và trạng thái cluster. Ai hiểu OSD đúng thì sẽ ngừng nhìn Ceph như một đống daemon rời rạc, mà bắt đầu thấy nó như một hệ thống sống thống nhất.


## 7. OSD và BlueStore

- BlueStore là backend mặc định của OSD trong các bản Ceph hiện đại. Reef architecture docs ghi rõ điều đó, và cách diễn giải này phản ánh đúng tinh thần từ Pacific trở đi: **BlueStore không phải là một service độc lập song song với OSD, mà là object store backend của OSD.** Vì vậy, khi học OSD cần hiểu ngay rằng OSD và BlueStore có quan hệ “daemon ↔ backend”, không phải “service ↔ service”.

- OSD chịu trách nhiệm logic của I/O, placement, consistency và state; BlueStore chịu trách nhiệm chính về cách dữ liệu và metadata được persist xuống thiết bị vật lý. Việc tách hai tầng này rất quan trọng vì nếu không, người đọc sẽ dễ lẫn giữa:

    - việc OSD quyết định object nên đi đâu
    - và việc BlueStore ghi object đó xuống block device như thế nào

> BlueStore là backend mặc định và là nền persistence của OSD.

[*Chi tiết hơn về BluesStore*](./05-bluestore.md)


## 8. OSD trong vận hành thực tế

- Một OSD có thể hiện diện trong nhiều trạng thái khác nhau mà người vận hành phải hiểu theo đúng nghĩa.

    - up / down phản ánh daemon còn sống và còn giao tiếp được hay không
    - in / out phản ánh OSD còn tham gia placement hay đã bị loại khỏi CRUSH placement hiện hành
    - active / degraded / clean là trạng thái của PGs liên quan, không phải trạng thái đơn lẻ của OSD

- Những cặp khái niệm này không đồng nghĩa với nhau, và việc nhầm lẫn giữa chúng là một trong những nguyên nhân phổ biến khiến người mới đọc `ceph -s` nhưng hiểu sai cluster state. 
    - Ví dụ, một OSD có thể đang `up` nhưng `out`, nghĩa là nó vẫn còn chạy và có thể giao tiếp, nhưng đã bị loại khỏi placement hiện hành nên không nhận thêm dữ liệu mới. Hoặc một OSD có thể đang `down` nhưng `in`, nghĩa là nó đã chết nhưng cluster chưa kịp remap PGs sang OSD khác nên vẫn coi nó là thành viên của placement hiện tại.

### 8.1 Khi một OSD fail

- Khi một OSD fail, cluster có thể:

    - đổi primary của các PG liên quan
    - đánh dấu các PG tương ứng là degraded
    - tính lại placement qua CRUSH/OSDMap
    - thực hiện recovery hoặc backfill để khôi phục redundancy mong muốn

- Tuy nhiên, không phải mọi dữ liệu đều “mất truy cập”. Pacific monitoring docs nhấn mạnh rằng *fault in one part of the cluster might prevent access to a particular object, but it does not mean access to all objects is lost*; Ceph là self-repairing trong nhiều trường hợp. Điều này phản ánh đúng bản chất phân tán của OSD layer.

### 8.2 Khi thêm OSD mới

Khi thêm OSD mới, cluster map thay đổi và placement của một số PG được remap sang OSD đó. Kết quả là backfill/rebalancing diễn ra để phân phối lại dữ liệu. OSD mới không chỉ đơn giản “đứng đó chờ có object mới”, mà sẽ được đưa vào placement hiện hành của cluster và dần nhận PGs hoặc object/chunks theo CRUSH outcome mới.

### 8.3 Một OSD thường gắn với một storage drive

RHCS 5 Operations Guide nêu rằng một Ceph OSD generally consists of one ceph-osd daemon for one storage drive and its associated journal within a node; nếu một node có nhiều storage drives thì thường map một ceph-osd daemon cho mỗi drive. Với RHCS 8 container-based recommendations, Red Hat cũng ghi rõ minimum guidance là 1 storage drive per OSD container. Đây là một điểm thực hành quan trọng vì nó phản ánh đúng mô hình scale-out của Ceph: thêm đĩa thường đồng nghĩa thêm OSD.

## 9. Pacific / RHCS 5 và Squid / RHCS 8: những gì giữ nguyên và những gì rõ hơn

- Về bản chất, vai trò của OSD giữ nguyên từ Pacific/RHCS 5 sang Squid/RHCS 8:

    - OSD vẫn là daemon lưu dữ liệu thực tế
    - OSD vẫn xử lý read, write, replication
    - OSD vẫn scrub dữ liệu trong PGs
    - OSD vẫn tham gia peering, heartbeat, recovery và backfill
    - client vẫn đi trực tiếp tới OSD sau khi tính placement


- Điểm docs mới nhấn mạnh rõ hơn là:

    - BlueStore là default backend và object được lưu trong flat namespace, database-like backend
    - configuration hiện đại ưu tiên central config store
    - ceph.conf bị deprecate trong RHCS 5 như nguồn cấu hình trung tâm
    - connection mode / encryption options được nói rõ hơn trong các guide mới

## 10. Những hiểu lầm phổ biến về OSD

- Hiểu lầm phổ biến nhất là xem OSD như “một process gắn với một ổ đĩa”. Điều đó chỉ đúng ở lớp triển khai rất nông. Về bản chất, OSD là daemon vừa lưu dữ liệu, vừa tham gia placement, vừa giữ consistency, vừa báo cáo state và tham gia self-healing. Nếu chỉ nhìn OSD như storage process, bạn sẽ không hiểu vì sao heartbeat, peering, scrub và recovery lại đều gắn chặt với nó.

- Hiểu lầm thứ hai là nghĩ client ghi trực tiếp vào mọi replica OSD. Trong Ceph, client nói chuyện với primary OSD, còn primary mới điều phối các secondarys hoặc shards. Điều này là nền của primary-copy model và là lý do client path của Ceph tương đối đơn giản so với phần phức tạp phía sau trong cluster.

- Hiểu lầm thứ ba là đồng nhất OSD với BlueStore. BlueStore là backend mặc định của OSD, nhưng không thay thế vai trò logic của OSD. OSD quyết định write/placement/state semantics; BlueStore quyết định persistence semantics ở tầng backend. Giữ ranh giới này rõ sẽ giúp bạn viết các file 01-osd.md và 06-bluestore.md không bị trùng hoặc loạn phạm vi.

- Hiểu lầm cuối cùng là xem scrub như một “task bảo trì ngoài lề”. RHCS architecture guides nêu rõ OSDs can scrub objects within placement groups và deep scrub so sánh data bit-for-bit để tìm bad sectors không lộ ra ở light scrub. Điều đó cho thấy scrub là một phần của integrity model, không chỉ là công việc housekeeping.

## 11. Kết luận

- OSD là trung tâm thực sự của Ceph ở mặt dữ liệu. Mọi object cuối cùng đều nằm trên OSD; mọi read/write cuối cùng đều đi tới OSD; mọi durability policy cuối cùng đều được OSD thực thi; và phần lớn các cơ chế self-healing, integrity checking và state propagation trong data path cũng đều xoay quanh OSD. Hiểu đúng OSD là hiểu được nơi Ceph biến cluster maps, CRUSH rules và pool policies thành hành vi lưu trữ thực tế.