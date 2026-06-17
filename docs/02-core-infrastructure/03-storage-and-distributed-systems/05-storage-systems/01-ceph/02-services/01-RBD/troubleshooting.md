# Troubleshooting
Khi gặp lỗi với RBD, đừng bắt đầu bằng câu hỏi “lệnh nào để sửa ngay”, mà hãy bắt đầu bằng câu hỏi lỗi đang nằm ở tầng nào. Với RBD, thường có bốn tầng dễ chồng lên nhau: tầng image, tầng client path, tầng pool/PG/OSD của cluster, và tầng ứng dụng hoặc guest OS. Một volume của VM có thể nhìn như lỗi block device, nhưng gốc lại nằm ở watcher/lock, snapshot lineage, cluster full, PG degraded hoặc thậm chí cache phía client. Vì vậy, troubleshooting RBD tốt luôn là troubleshooting theo tầng, không phải chỉ nhìn một lệnh rbd rồi kết luận.

- Kiểm tra trước tiên :
```bash
ceph -s
ceph health detail
rbd info <pool>/<image>
rbd status <pool>/<image>
```
- Trong đó :
    - `ceph -s` và `ceph health detail` giúp bạn biết cluster có đang `degraded`, full hay `blocked writes` không. 
    - `rbd info` cho biết image đang có `feature` gì, kích thước thế nào. 
    - `rbd status` giúp nhìn trạng thái `image`, và với các cơ chế `cache` bền vững phía client thì đây cũng là nơi Ceph hiển thị `cache status`.


## Image không map được, attach lỗi, hoặc VM treo I/O
- Nếu image không map được hoặc VM bị treo I/O, hướng nghĩ đầu tiên nên là: image đang bị client khác giữ hay cluster đang có vấn đề write/read path. RBD có cơ chế exclusive-lock để ngăn nhiều tiến trình ghi vào cùng một image theo kiểu không phối hợp. Ceph docs mô tả rõ exclusive locks được dùng nhiều trong virtualization để tránh các VM ghi đè lên nhau, và cũng là điều kiện cho một số feature như journaling và diff nhanh. Điều đó nghĩa là lock không phải mặc định là lỗi, nhưng nếu lock không được nhả đúng thì nó sẽ trở thành nguyên nhân của rất nhiều case attach/map thất bại.

```bash
rbd status <pool>/<image>
rbd showmapped
```
- Nếu image đang có watcher/lock mà bạn không mong đợi, đừng vội gỡ tay. Trước hết phải trả lời được: client cũ còn sống không, host nào đang map image này, đây là stale state hay đang có client thật đang dùng. Với các client có persistent cache, rbd status còn hiển thị thêm trạng thái cache; điều đó rất hữu ích để phân biệt lỗi attach/map thông thường với lỗi đi kèm cache path.
- Nếu image map bình thường nhưng VM vẫn treo I/O, hãy quay xuống cluster ngay. `ceph -s`, `ceph health detail`, `ceph osd perf` và nếu cần thì `ceph pg stat` là nơi phải nhìn tiếp. 
    - Nhiều case “RBD treo” thực ra chỉ là biểu hiện bên trên của việc cluster đang `OSD_FULL`, `degraded`, hoặc write path đang bị kẹt. Ceph docs về health checks nói rất rõ khi một hoặc nhiều OSD vượt ngưỡng full, cluster sẽ ngăn servicing writes để bảo vệ dữ liệu. Với VM, điều đó rất dễ biểu hiện thành I/O hang hoặc guest filesystem phản ứng xấu.
    > Nếu chưa chắc lock/watcher là stale, đừng gỡ mù. Nếu cluster đang full hoặc degraded nặng, đừng cố chữa ở tầng image trước. Với junior, quy tắc an toàn là: attach/map lỗi thì nhìn `rbd status` trước, I/O treo thì nhìn `ceph health detail` ngay sau đó.

## Snapshot không xóa được, unprotect không được, clone/flatten có vấn đề
- Đây là nhóm lỗi RBD gặp rất nhiều trong đời thực, đặc biệt ở môi trường clone từ golden image hoặc snapshot tích lũy lâu ngày. Ceph docs nói rất rõ rằng bạn không thể unprotect rồi xóa một snapshot nếu snapshot đó còn clone con phụ thuộc vào nó. Muốn unprotect, phải flatten hoặc xóa từng clone trước. Ngoài ra, thời gian flatten tăng theo kích thước snapshot và mức phụ thuộc của clone. Đây không phải bug; đây là behavior đúng của lineage trong RBD.
- Khi gặp lỗi kiểu:
    - Cannot unprotect: Still in use
    - snapshot không xóa được
    - parent image không xóa được
    - flatten quá lâu

hãy đi theo thứ tự này:
```bash
rbd snap ls <pool>/<image>
rbd children <pool>/<image>@<snap>
rbd info <pool>/<clone>
```
- Nếu `rbd children` còn trả ra clone con, đó là lý do snapshot chưa thể unprotect. Khi cần cắt phụ thuộc, bạn có thể flatten image con:
```bash
rbd flatten <pool>/<clone>
```
- Sau khi flatten xong hoặc đã xóa clone con, mới quay lại:
```bash
rbd snap unprotect <pool>/<image>@<snap>
rbd snap rm <pool>/<image>@<snap>
```


## Dung lượng không giảm, rbd du lớn bất thường, hoặc pool tiến gần full

- Đây là nhóm lỗi rất hay gây tranh cãi giữa khách hàng, ứng dụng và đội storage. Điều đầu tiên phải chốt là: dung lượng guest filesystem dùng và dung lượng backend của RBD không phải lúc nào cũng trùng. `rbd du` được dùng để tính provisioned và actual disk usage của image và snapshots; nếu `fast-diff` không bật thì thao tác này có thể phải hỏi OSD cho từng object có khả năng tồn tại trong image. Ceph docs cũng nói rõ `fast-diff` giúp việc tính rbd du nhanh hơn rất nhiều, và phụ thuộc vào `object-map` cùng `exclusive-lock`.

- Khi thấy “guest đã xóa file nhưng backend không giảm”, đừng bắt đầu bằng việc nói Ceph tính sai. Hãy tách ba khả năng:

    - guest chỉ xóa file ở tầng filesystem nhưng backend block/object vẫn còn extents đã được ghi,
    - image có snapshot/clone lineage đang giữ lại dữ liệu,
    - hoặc bạn đang nhìn một image/pool thật sự tiến gần full vì cluster chưa reclaim được như kỳ vọng.

- Lệnh đầu tiên nên nhìn là:
```bash
rbd du <pool>/<image>
rbd snap ls <pool>/<image>
rbd children <pool>/<image>@<snap>
ceph df
ceph health detail
```
- Nếu image có nhiều snapshot/clone phụ thuộc, lineage có thể giữ lại dữ liệu backend dù guest đã thay đổi dữ liệu ở head image. Nếu cluster báo `OSD_NEARFULL`, `OSD_BACKFILLFULL` hoặc `OSD_FULL`, phải xử lý theo hướng capacity trước, vì khi `OSD_FULL` xảy ra thì Ceph sẽ chặn ghi để bảo vệ dữ liệu. Đây là health check chính thức của Ceph, không phải behavior bất thường.

- Một lệnh đôi khi hữu ích là `rbd sparsify`, nhưng phải hiểu đúng nó. Man page của rbd nói rõ `sparsify` chỉ reclaim space for zeroed image extents. Điều đó nghĩa là nó không phải cây đũa thần cho mọi case “dung lượng không giảm”; nó chỉ có tác dụng khi extents thực sự là zeroed extents. Nếu dữ liệu cũ vẫn còn ở tầng block/object theo cách không phải zero extents, `sparsify` có thể gần như không giúp gì.

> Với nhóm lỗi dung lượng, đừng hỏi ngay “khách còn bao nhiêu file”. Hãy hỏi trước: tôi đang nhìn số liệu ở tầng guest hay ở tầng image/backend. Chỉ cần nhầm tầng là cả buổi debug sẽ lệch hướng.

## Mirroring lỗi, lag cao, promote/demote không như mong đợi
- Ceph docs về RBD mirroring nói rõ trạng thái replication của image được lưu cho mỗi primary mirrored image và có thể xem bằng rbd mirror image status hoặc rbd mirror pool status. Đây luôn là điểm bắt đầu đúng cho mọi case mirror lag, image không đồng bộ, hoặc failover/failback có hành vi bất thường. Nếu không nhìn status trước, bạn gần như đang làm DR bằng cảm giác.

- Lệnh nên chạy đầu tiên là:
```bash
rbd mirror image status <pool>/<image>
rbd mirror pool status <pool>
```
- Nếu image đang báo lỗi hoặc lag tăng cao, hãy phân tầng nguyên nhân:

    - phía mirror daemon hoặc connectivity giữa hai cluster,
    - phía image feature/journaling,
    - hoặc phía thao tác failover/failback trước đó làm state của hai bên lệch nhau.
- Ceph docs còn nêu rất rõ rằng forced promotion được dùng khi không thể propagate demotion sang peer cluster, ví dụ cluster lỗi hoặc communication outage, và điều đó có thể dẫn tới split-brain cho đến khi force resync được phát hành. Đây là thông tin cực kỳ quan trọng cho troubleshooting vì nó giải thích tại sao “promote thành công” chưa chắc là “mọi thứ ổn”.

- Nếu bạn buộc phải promote bằng --force, hãy ngay lập tức coi image đó là nghi ngờ split-brain cho tới khi resync xong và status quay lại tốt.

## Hiệu năng RBD chậm hoặc thất thường
- Khi người dùng nói “RBD chậm”, đừng vội nhìn mỗi image. Trước hết phải phân biệt xem chậm ở đâu:

    - cluster đang chậm vì OSD/PG/capacity,
    - image đang bị lineage hoặc feature path làm nặng,
    - hay client path/cache đang tạo behavior thất thường.
    Ví dụ, fast-diff giúp rbd du và diff nhanh hơn rất nhiều; nếu image không có nó thì các thao tác liên quan diff/usage có thể nặng hơn hẳn. Tương tự, persistent write-back/PWL cache chỉ hoạt động khi exclusive lock được acquire và có thể xem status qua rbd status. Những điều này cho thấy performance behavior của RBD không nằm ở một chỗ duy nhất.

```bash
ceph -s
ceph health detail
ceph osd perf
rbd info <pool>/<image>
rbd status <pool>/<image>
```
- Nếu cluster báo nearfull, backfillfull hoặc full, hoặc OSD perf xấu, thì vấn đề gần như không còn là “một image RBD chậm” nữa. Ngược lại, nếu cluster khỏe mà image đang có lineage sâu, mirror đang replay nặng, hoặc cache path bất thường, thì hướng phân tích nên đi theo image/client path nhiều hơn

> RBD performance gần như luôn là câu chuyện đa tầng. Nếu chỉ nhìn guest OS hoặc chỉ nhìn rbd info, bạn sẽ bỏ lỡ nửa còn lại của vấn đề. Với junior, quy tắc an toàn là: chậm thì nhìn cluster trước, rồi mới nhìn image.