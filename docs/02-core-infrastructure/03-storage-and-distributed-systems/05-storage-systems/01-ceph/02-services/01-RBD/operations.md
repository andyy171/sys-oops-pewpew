# Vận hành RBD
## 1. Nguyên tắc vận hành

- Khi làm việc với RBD, sai lầm phổ biến nhất không phải là gõ sai lệnh, mà là đụng vào image khi chưa biết image đó đang ở trạng thái nào. Trước mọi thao tác như `resize`, `snapshot`, `clone`, `flatten`, `mirror` hay `migration`, nên nhìn ít nhất bốn thứ: cluster có đang khỏe không, image có đang bị client nào giữ không, image có snapshot hoặc clone phụ thuộc không, và feature hiện tại của image có phù hợp với việc sắp làm không. Đây là nguyên tắc giúp tránh phần lớn lỗi tự gây ra trong vận hành RBD.

- Bộ kiểm tra nhanh nên thành phản xạ trước mỗi change là:
```bash
ceph -s
ceph health detail
rbd info <pool>/<image>
rbd status <pool>/<image>
```
- `ceph -s` và `ceph health detail` cho bạn biết cluster có đang degraded, recovering hay có vấn đề OSD/PG không. `rbd info` cho biết image đang ở pool nào, có feature gì, kích thước logic bao nhiêu. rbd status cho biết image có `watcher` hoặc `lock` đang hoạt động hay không. Nếu bỏ qua một trong bốn lệnh này, rất dễ chạy đúng lệnh trên đúng image nhưng lại ở sai thời điểm.

-  Một cách nghĩ rất nên giữ là: mọi thao tác RBD đều đi theo ba bước. 
    1. kiểm tra trước. 
    2. thao tác. 
    3. xác nhận sau. 
    Ví dụ, sau khi `create` thì phải `rbd info`; sau khi `snapshot` thì phải `rbd snap ls`; sau khi `clone` thì phải nhìn lại `parent-child`; sau khi `mirror` `failover` thì phải xem lại `rbd mirror image status`. RBD không phải loại storage nên vận hành theo kiểu “lệnh không báo lỗi là xong”.

- Về mức độ cẩn thận, có thể nhớ rất đơn giản như sau. 
    - Tương đối an toàn: `rbd info`, `rbd status`, `rbd du`, `rbd snap ls`, `rbd children`. 
    - Cần cẩn thận hơn: `rbd resize`, `rbd feature enable/disable`, `rbd flatten`, `rbd mirror image promote/demote`, `rbd migration` .... 
    - Dễ gây hậu quả nếu làm ẩu: xóa image, xóa snapshot khi còn clone phụ thuộc, failover mirror khi chưa xem lag/trạng thái, commit migration khi chưa chắc image đích đã ổn. 
    Đây không phải phân loại chính thức của docs, mà là cách vận hành thực tế rút ra từ chính bản chất các workflow mà docs mô tả.

## 2. Các thao tác với image
### Tạo image mới

- **Khi nào dùng:** khi cần một block device mới cho VM, host Linux, test volume hoặc một image đích cho migration/clone workflow. Kiểm tra trước: **pool đã tồn tại chưa**, **pool đã gắn application rbd chưa**, **cluster có đủ dung lượng và không đang ở trạng thái xấu không**. Ceph docs khuyến nghị pool dùng cho RBD nên được application enable rbd và rbd pool init từ trước.
```bash
rbd create volumes/vm-001 --size 100G
rbd info volumes/vm-001
```
- Kiểm tra sau: luôn xem lại `rbd info` để xác nhận đúng tên image, đúng pool, đúng kích thước và đúng feature set đang bật. Dễ sai: tạo đúng image nhưng trong nhầm pool, hoặc tạo xong rồi quên kiểm tra feature nên tới lúc cần clone/diff/mirror mới phát hiện image không đúng “chuẩn” mình muốn. rbd(8) là nguồn chuẩn cho create và info.

### Kiểm tra thông tin image

- Đây là thao tác bạn sẽ dùng nhiều nhất trong đời thực. Khi nào dùng: trước mọi thay đổi và sau mọi thay đổi. `rbd info` cho biết hình học của image, format, size, feature; `rbd status` cho biết watcher/lock state; `rbd du` cho biết actual used space ở tầng image/backend; `rbd showmapped` cho biết host hiện tại đang map image nào. Những lệnh này không “đẹp” bằng create hoặc snapshot, nhưng chúng mới là thứ giữ người vận hành khỏi lao mù vào image.
```bash
rbd info volumes/vm-001
rbd status volumes/vm-001
rbd du volumes/vm-001
rbd showmapped
```
> `rbd du` không phải “dung lượng mà guest đang dùng”, mà là dung lượng thực ở tầng RBD/backend. Nếu image có `fast-diff` và `object-map`, việc tính `du` sẽ nhanh và hiệu quả hơn nhiều. Vì vậy `rbd du` vừa là lệnh capacity, vừa là lệnh gợi ý xem feature set của image đã đủ tốt cho workload backup/audit hay chưa.

### Map và unmap image

- Khi nào dùng: khi cần gắn image thành block device ở host Linux. rbd map sẽ tạo thiết bị block ở client; rbd unmap sẽ tháo nó ra. Ceph docs cũng ghi rõ rbd là utility được Linux rbd driver và QEMU/KVM dùng để thao tác với images.
```bash
rbd map volumes/vm-001
rbd showmapped
rbd unmap /dev/rbd0
```
- Kiểm tra trước: image có đang được map ở đâu khác không, có watcher/lock bất thường không. 
- Kiểm tra sau: sau map, dùng rbd showmapped; sau unmap, dùng lại rbd showmapped và nếu cần `rbd status` để chắc image không còn session cũ. 

- Điểm dễ sai: unmap xong là coi như sạch, nhưng thực tế nếu client path chết bẩn hoặc ứng dụng chưa nhả đúng cách, watcher/lock có thể vẫn còn. Vì vậy, cần kiểm tra `rbd status` khi thấy gì đó không bình thường.

### Resize image

- Khi nào dùng: khi cần tăng kích thước logic của volume. rbd resize là lệnh chuẩn cho việc này. QEMU cũng hỗ trợ qemu-img resize trực tiếp trên URI rbd:{pool}/{image}.
```bash
rbd resize volumes/vm-001 --size 200G
rbd info volumes/vm-001
```
Hoặc nếu đi qua hypervisor toolchain:
```bash
qemu-img info rbd:volumes/vm-001
qemu-img resize rbd:volumes/vm-001 200G
```
- Kiểm tra sau: rbd info ở tầng image, rồi kiểm tra tiếp partition/filesystem bên trong guest nếu volume đang dùng thực tế. 
- Thực tế dễ sai là tưởng resize xong ở RBD là guest tự thấy dung lượng mới. Tuy nhiên, RBD chỉ đổi block device logic; phần bên trong guest là một tầng khác.

### Snapshot image
- Khi nào dùng: khi cần chốt trạng thái image ở một thời điểm, làm mốc để rollback, clone hoặc backup/diff workflow. Ceph docs nhấn mạnh snapshot là read-only logical copy của image tại một thời điểm và được quản lý bằng rbd hoặc các tầng cao hơn như QEMU, libvirt, OpenStack. Docs cũng cảnh báo rằng snapshot chỉ crash-consistent nếu không phối hợp quiesce I/O trong guest.
```bash
rbd snap create volumes/vm-001@snap-2026-04-14
rbd snap ls volumes/vm-001
```
- Kiểm tra trước: image có đang ghi mạnh không, ứng dụng/guest có cần freeze I/O không. 
- Kiểm tra sau: rbd snap ls để xác nhận snapshot đã có. Dễ sai: coi snapshot như “backup an toàn hoàn chỉnh” mà quên rằng nếu không quiesce filesystem thì snapshot chỉ là crash-consistent, không chắc application-consistent. Đây là điểm junior rất dễ bỏ qua.

### Clone image từ snapshot
- Khi nào dùng: khi cần tạo image mới rất nhanh từ một snapshot gốc, ví dụ từ golden image cho VM templates. Ceph docs mô tả snapshot layering cho phép clone images nhanh và dễ bằng cơ chế copy-on-write.

Luồng đúng nên là:
```bash
rbd snap protect volumes/vm-001@snap-2026-04-14
rbd clone volumes/vm-001@snap-2026-04-14 volumes/vm-001-clone
rbd info volumes/vm-001-clone
rbd children volumes/vm-001@snap-2026-04-14
```
- Kiểm tra trước: snapshot đã tồn tại chưa, snapshot đã protect chưa. 
- Kiểm tra sau: rbd info image con và rbd children để thấy quan hệ phụ thuộc. 
- Thực tế dễ sai: clone xong tưởng image con đã hoàn toàn độc lập. Thực tế clone lúc này vẫn đang phụ thuộc snapshot cha. Đó là lý do phần dọn lineage rất quan trọng.

### Protect / unprotect snapshot
- Khi nào dùng: snapshot nào được dùng làm cha cho clone thì phải protect; snapshot muốn xóa về sau thường phải unprotect trước. Ceph docs snapshot nói rất rõ rằng clone phụ thuộc snapshot, nên snapshot phải được protect trước khi clone.
```bash
rbd snap protect volumes/vm-001@snap-2026-04-14
rbd snap unprotect volumes/vm-001@snap-2026-04-14
```
- Kiểm tra trước: nếu sắp unprotect, luôn chạy rbd children trước để xem còn clone con phụ thuộc không. 
- Thực tế dễ sai: chạy unprotect rồi thấy báo lỗi, tưởng cluster lỗi. Nhiều trường hợp không phải lỗi mà chỉ vì clone con vẫn còn tồn tại.

### Flatten và dọn lineage
- Khi nào dùng: khi muốn clone bớt phụ thuộc parent, hoặc khi cần dọn parent/snapshot lineage để xóa sạch về sau. Flatten sẽ làm image con độc lập hơn bằng cách sao chép dữ liệu phụ thuộc từ parent. Docs snapshot của Ceph và man page của rbd đều mô tả flatten là một lệnh lifecycle rất quan trọng của clone images.
```bash
rbd flatten volumes/vm-001-clone
```
- Kiểm tra trước: image con lớn tới đâu, cluster đang khỏe không, có đang recovery/backfill không. 
- Kiểm tra sau: nhìn lại `rbd info` và kiểm tra dependency chain bằng `rbd children` từ phía parent. 
- Thực tế dễ sai là coi flatten là lệnh “dọn dẹp nhẹ”. Tuy nhiên, Flatten có thể rất nặng nếu image lớn hoặc lineage sâu. **Chỉ chạy khi bạn thật sự cần cắt dependency.**

### Kiểm tra dung lượng thật của image

- Đây là chỗ junior rất hay bị rối. Nên dùng khi cần xem image đang chiếm bao nhiêu backend space, audit capacity, hoặc điều tra vì sao guest dùng ít nhưng backend ghi nhận nhiều. `rbd du` là lệnh chính. `fast-diff` và `object-map` giúp phép tính này nhanh hơn đáng kể.
```bash
rbd du volumes/vm-001
```
> Điểm phải nhớ: rbd du không đại diện cho “Used Space” trong guest OS. Nó đại diện cho actual used space ở tầng RBD/object-backed image. Nếu đem so hai số này mà không tách tầng, rất dễ tự kết luận sai rằng Ceph đang “tính nhầm dung lượng”.

### Quản lý feature của image

- Khi nào dùng: khi chuẩn hóa image cho clone/diff/mirror workflows, hoặc khi cần chỉnh image để phù hợp client path. rbd cho phép bật/tắt feature, nhưng không nên làm theo kiểu “cứ bật hết”. Các feature như layering, exclusive-lock, object-map, fast-diff, deep-flatten, journaling có dependency và ý nghĩa khác nhau.
```bash
rbd info volumes/vm-001
rbd feature enable volumes/vm-001 object-map fast-diff
rbd feature disable volumes/vm-001 fast-diff
```
- **Kiểm tra trước:** image đang phục vụ workload gì, client path là krbd hay librbd, feature định bật có phụ thuộc feature khác không. 
- **Dễ sai:** bật feature theo cảm tính rồi sau đó gặp incompatibility hoặc behavior khó hiểu. Với junior, quy tắc an toàn là: không đổi feature nếu chưa hiểu rõ lý do phải đổi.

### Xóa image và dọn image an toàn

- Khi nào dùng: khi image không còn được sử dụng. Kiểm tra trước: image có watcher/lock không, có snapshot không, snapshot đó có clone con không. Nhiều trường hợp xóa image không được không phải vì image “lỗi”, mà vì lifecycle của nó chưa sạch. `rbd info`, `rbd status`, `rbd snap ls`, `rbd children` là bốn lệnh nên nhìn trước khi nghĩ tới rm.
```bash
rbd status volumes/vm-001
rbd snap ls volumes/vm-001
rbd rm volumes/vm-001
```
Nếu workflow của bạn cần an toàn hơn xóa thẳng, RHCS block device guide có phần riêng cho RBD trash, cho phép chuyển image vào trash thay vì xóa ngay. Đây là cách tốt hơn trong nhiều môi trường production vì cho đội vận hành thêm một lớp bảo vệ trước thao tác nhầm.

## 3. Mirroring trong vận hành thực tế

- Mirroring dùng khi bạn cần DR giữa hai cluster Ceph, không phải khi bạn chỉ cần backup thông thường. Tài liệu RHCS 5 mô tả RBD mirroring là asynchronous replication giữa hai hoặc nhiều Ceph clusters, và `rbd-mirror daemon` là thành phần kéo thay đổi từ cluster peer về cluster cục bộ. Nghĩa là trong vận hành, mirror phải được coi như một hệ replication liên cluster có trạng thái riêng, không phải chỉ là một cờ của image.

- Khi nào dùng: khi bạn cần site dự phòng, cần failover volume/image sang cluster khác, hoặc cần giảm mất mát dữ liệu khi site chính gặp sự cố. Kiểm tra trước: hai cluster đều khỏe, kết nối mạng giữa hai bên ổn, pool/image đã bật đúng mirror mode, và daemon rbd-mirror hoạt động bình thường. Nếu các điều kiện này chưa rõ, đừng vội làm planned failover.

### Kiểm tra trạng thái mirroring

- Đây là bước quan trọng nhất của vận hành mirror. Trước khi promote, demote, failover hay failback, phải nhìn trạng thái pool và image.
```bash
rbd mirror pool status volumes
rbd mirror image status volumes/vm-001
```
Điều cần nhìn: image nào đang là primary, image có đang replay tốt không, có lag rõ rệt không, trạng thái có đang báo error hay warning không. Về mặt vận hành, nếu chưa trả lời được ba câu đó thì chưa nên promote/demote.

- Các thao tác cơ bản với peer, image và pool

    - Bật mirror ở pool level:
    ```bash
    rbd mirror pool enable volumes pool
    # hoặc
    rbd mirror pool enable volumes image
    ```
    - Thiết lập peer bằng bootstrap token:
    ```bash
    rbd mirror pool peer bootstrap create volumes > token.txt
    rbd mirror pool peer bootstrap import volumes token.txt
    ```
- Các docs Ceph hiện hành và RHCS 5 đều mô tả mirror được cấu hình theo per-pool và có thể áp trên một tập con image hoặc toàn bộ image trong pool, tùy mode. Đây là lý do bạn phải chọn mode cho đúng mục tiêu vận hành ngay từ đầu.

### Promote / demote / failover / failback

- Planned failover về mặt thao tác thường xoay quanh `demote` và `promote`. Ý nghĩ rất đơn giản: bên cũ nhường quyền ghi, rồi bên mới nhận quyền ghi. Với image cụ thể:
```bash
rbd mirror image demote volumes/vm-001
rbd mirror image promote volumes/vm-001
```
Điểm phải nhớ: đừng nhìn đây như hai lệnh CLI rời rạc. Đây là hai bước chuyển authority giữa hai cluster. Nếu làm ngược thứ tự hoặc làm khi chưa biết lag/trạng thái thật, bạn rất dễ chạm vào vùng split-brain hoặc mất dữ liệu logic chưa replicate xong. Đó là lý do trước khi promote, bạn phải nhìn `rbd mirror image status` để xác nhận image nào đang là primary, replication đang diễn ra tốt, và không có error nào đáng lo ngại. Nếu chưa trả lời được những câu đó, đừng vội promote.

### Những điểm cần kiểm tra trước và sau mỗi thao tác mirror

- Trước khi đụng vào mirror: nhìn `rbd mirror image status`, xác nhận image nào đang là bên chính, xác nhận không có error rõ ràng, và xác nhận mục tiêu của bạn là failover có kế hoạch hay failover cưỡng bức. Sau khi thao tác: nhìn lại `rbd mirror image status`, xác nhận authority đã đổi đúng, `replication`/`resync` đang diễn ra đúng như mong đợi. Nếu sau `promote`/`demote` mà không kiểm tra lại, bạn chỉ mới “gõ lệnh”, chưa thật sự “vận hành xong”.

## 4. Migration trong vận hành thực tế
- **Khi nào cần migration:** Migration nên dùng khi bạn muốn đổi pool, đổi layout/format, hoặc chuyển image từ một nguồn khác vào RBD mà vẫn giữ được một workflow có trạng thái rõ ràng. Tài liệu Ceph mô tả **image live-migration có thể thực hiện giữa các pool trong cùng cluster**, giữa các image formats/layouts khác nhau, hoặc từ external data sources; khi bắt đầu, source sẽ được deep-copy sang image đích và cố gắng giữ sparse allocation nếu có thể. Điều đó cho thấy migration không chỉ là “copy image”, mà là một công cụ để thay đổi cấu trúc của image một cách có kiểm soát.

- **Điều cần hiểu đúng về migration:** Đừng nhìn migration như một lệnh đơn phát. Hãy nhìn nó như một workflow có trạng thái. Chính vì có trạng thái, migration mới có các pha như `prepare`, `execute`, `commit` và `abort`. Điều này rất quan trọng về mặt vận hành: khi image đang ở giữa migration, bạn không được cư xử với nó như một image “bình thường” và cũng không được xóa source hay destination chỉ vì thấy dữ liệu “có vẻ đã copy xong”.

- Luồng thao tác nên nhớ: Chuẩn bị migration, theo dõi trạng thái, chỉ commit khi đã chắc image đích đúng như mong muốn, và chỉ abort khi bạn hiểu rõ mình đang quay lại phía nào. 
    - Mục tiêu không phải là thuộc lòng tất cả cú pháp, mà là luôn trả lời được ba câu hỏi: image nguồn là gì, image đích là gì, trạng thái hiện tại của migration là gì. Với junior, đây là phần quan trọng hơn cả việc nhớ từng subcommand.

- Điều phải kiểm tra trước khi migration. Trước khi đụng vào migration, hãy kiểm tra cluster có đang khỏe không, pool đích có đúng policy không, image nguồn có snapshot/clone lineage gì đặc biệt không, và image có đang bị client sử dụng không. Tối thiểu nên nhìn lại:
```bash
ceph -s
ceph health detail
rbd info <pool>/<image>
rbd status <pool>/<image>
```
- `ceph -s` và `ceph health detail` giúp bạn tránh bắt đầu migration trong lúc cluster đang `degraded`, `full` hoặc có vấn đề write availability; `rbd info` và `rbd status` giúp xác định image hiện tại có `feature`, `watcher` hoặc trạng thái nào khiến migration rủi ro hơn bình thường.

- Điểm dễ sai nhất là coi migration như “copy xong là xóa nguồn”. Với RBD, đó là cách làm nguy hiểm. Migration tồn tại để bạn không phải làm kiểu copy thô thiếu trạng thái. Vì vậy, rule an toàn là: chưa rõ trạng thái thì chưa commit, chưa chắc rollback path thì chưa abort, và chưa rõ authority thì không xóa gì cả.

## 5. Cache và client-side behavior trong vận hành

### Khi nào cần quan tâm tới cache phía client. 
- Bạn chỉ cần quan tâm mạnh tới phần này khi image đi qua `librbd` path, đặc biệt trong các môi trường VM hoặc ứng dụng user-space có nhu cầu tối ưu latency và throughput. Ceph config reference cho biết `librbd` cache được bật mặc định và hỗ trợ các chính sách như `write-around`, `write-back` và `write-through`; trong đó với `write-around` và `write-back`, các ghi có thể trả về sớm trước khi toàn bộ dữ liệu được đẩy xuống cluster, trừ khi số byte bẩn vượt ngưỡng cấu hình. 
> Điều này có nghĩa cache không chỉ là tối ưu hiệu năng, mà còn là thay đổi cách ghi được cảm nhận ở phía client.

- Persistent write-back cache phải được nhìn như một feature vận hành nâng cao. Tài liệu Pacific nói rõ persistent write-back cache quản lý dữ liệu cache trên một thiết bị bền vững cục bộ, và nó không thể bật nếu không có exclusive-lock; cache chỉ cố được bật khi exclusive lock đã được acquire. Điều này rất quan trọng trong vận hành vì nó cho thấy cache không đứng riêng lẻ: nó phụ thuộc vào feature semantics của image. Nếu junior chỉ nhớ “bật cache cho nhanh” mà không biết lock semantics bên dưới, rất dễ đi sai hướng ngay từ đầu.

### Khi nào nên thận trọng hoặc tránh bật cache. 
- Nếu môi trường client không ổn định, nguồn điện không tốt, hoặc đội vận hành chưa quen với các failure mode phía client, thì cache write-back không nên là lựa chọn mặc định. Docs mới hơn về PWL còn giải thích rõ rằng đây là một persistent, fault-tolerant write-back cache cho librbd-based clients; nó dùng thiết kế log-ordered, duy trì checkpoints nội bộ và dù mất hoàn toàn client cache thì disk image vẫn nhất quán, nhưng dữ liệu có thể trông stale. Chỉ riêng cách mô tả đó đã đủ cho thấy cache phía client là một tính năng mạnh nhưng không phải nút “bật là tốt hơn”.

### Điều nên làm trong vận hành thường ngày. 
- Với junior, cách an toàn nhất là: đừng chủ động thay đổi cache policy hoặc bật persistent cache chỉ để “test xem có nhanh hơn không”. Trước khi đụng vào cache, phải trả lời được ba câu hỏi: client đang đi librbd hay krbd, image có exclusive-lock không, và nếu client crash thì đội vận hành có biết mình sẽ kiểm tra cái gì không. Nếu chưa trả lời được ba câu đó, tốt hơn hết là giữ behavior mặc định. 