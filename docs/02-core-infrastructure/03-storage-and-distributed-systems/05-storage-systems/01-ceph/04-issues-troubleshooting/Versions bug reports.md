# Các bug ghi nhận trên Ceph 16.x
## Nhóm bug liên quan đến BlueStore Onode / OnodeSpace
- Đây là một nhóm lỗi nằm trong đường quản lý vòng đời Onode của BlueStore, tức lớp metadata object được giữ trong cache RAM của OSD. Khi OSD chịu tải cao, đặc biệt trong các giai đoạn recovery / backfill / peering hoặc lúc cache trim/evict diễn ra mạnh, các lỗi liên quan đến onode release quá sớm, nref (reference count) không nhất quán, hoặc logic pinned entry sai có thể làm OSD crash ở các hàm như BlueStore::Onode::put(), OnodeSpace::_remove() hoặc các nhánh LRU/cache liên quan. Trong Pacific, Ceph đã backport nhiều patch theo từng đợt để vá dần nhóm lỗi này, chứ không phải chỉ có một bản vá đơn lẻ.

- Các bản Pacific ghi nhận trực tiếp nhóm fix Onode
    - `v16.2.8`: `os/bluestore: avoid premature onode release` — PR **#44723**. Đây là patch cho nhánh lỗi “release Onode quá sớm”, tức object metadata có thể bị thả khỏi vòng đời sử dụng sớm hơn mong muốn.
    - `v16.2.11`: `os/bluestore: fix AU accounting in bluestore_cache_other mempool` — PR **#47337**. Patch này không ghi chữ “onode” ngay trong tên hàm, nhưng nằm đúng vùng cache/mempool của BlueStore và thường được xem là một phần của nhóm fix giảm điều kiện gây lộ bug ở Onode cache path.
    - `v16.2.11`: `os/bluestore: get rid of fake onode nref increment for pinned entry` — PR **#47556**. Đây là patch rất quan trọng vì nó động thẳng vào logic nref của onode đối với pinned entry, tức đúng vùng dễ dẫn đến sai lệch reference counting.
    - `v16.2.13`: `os/bluestore: fix onode ref counting` — PR **#50072**. Đây là mục release note rõ ràng nhất, xác nhận nhánh Pacific còn có thêm một fix riêng cho onode ref counting sau 16.2.11.

- Nhóm lỗi này là các vấn đề xuyên suốt vòng đời Onode :
    - **Release sớm:** Onode có thể bị giải phóng sớm hơn thời điểm an toàn. Đây là nhánh được nhắc trực tiếp trong avoid premature onode release ở 16.2.8.
    - **Reference count sai:** Sau đó Pacific tiếp tục vá các lỗi ở nref, gồm cả chuyện “fake increment” cho pinned entry và fix ref counting tổng thể ở 16.2.11 và 16.2.13. Điều này cho thấy upstream/backport maintainer không coi vấn đề đã xử xong chỉ với một patch ban đầu, mà phải vá thêm các biến thể liên quan đến quản lý refcount.
    - **Cache/mempool path liên quan:** Patch về bluestore_cache_other mempool ở 16.2.11 cho thấy ngoài refcount thuần túy, điều kiện bộ nhớ/cache cũng là một phần của bài toán. Vì Onode tồn tại trong cache path, lỗi accounting/mempool có thể làm tăng khả năng đụng các đường code dễ crash khi trim/evict diễn ra mạnh.
- Dấu hiệu nhận biết ngoài thực tế
    - OSD crash với backtrace rơi vào các hàm như `BlueStore::Onode::put()`, `OnodeSpace::_remove()`, `LruOnodeCacheShard::_trim_to()` hoặc các nhánh`get_onode()`, `queue_transactions()`.
    - Sự cố thường dễ lộ ra hơn trong lúc cluster đang **degraded, recovery mạnh, peering nhiều,** hoặc có **slow heartbeat** trên front/back network.
    - Có thể thấy hiện tượng **OSD down** rồi tự lên lại nếu systemd auto-restart service, khiến người vận hành dễ nhầm là lỗi mạng/heartbeat đơn thuần, trong khi bản chất có thể là process đã crash cục bộ trước đó.
- Giải pháp / cách xử lý
    - Ngắn hạn khi sự cố vừa xảy ra
        - Xác định OSD nào crash bằng ceph crash ls, ceph crash info, journalctl -u ceph-osd@<id> và ceph -s.
        - Nếu xác nhận chỉ là crash process và không có dấu hiệu lỗi phần cứng/I/O, có thể restart OSD trên đúng host chứa OSD đó rồi theo dõi cluster recovery.
        - Không nên restart hàng loạt nhiều OSD cùng lúc khi cluster đang peering/recovery mạnh.
        - Nếu OSD lên lại nhưng cluster chưa nhận up, cần phân biệt rõ giữa service đang chạy trên host và OSD đã rejoin cluster thành công.
    - Trung hạn để giảm rủi ro tái phát
        - Hạn chế tạo thêm thay đổi lớn trong lúc cluster đang recovery mạnh.
        - Theo dõi slow heartbeat, pg down/inactive, recovery rate, và các OSD có dấu hiệu slow ops.
        - Nếu cần, có thể giảm mức độ hung hãn của recovery để tránh làm cluster stress hơn.
    - Dài hạn / giải pháp bền vững
        - Nâng cấp khỏi 16.2.10 lên ít nhất Pacific 16.2.15 nếu vẫn phải ở nhánh Pacific, vì 16.2.15 là bản Pacific cuối cùng và sẽ kế thừa các fix onode-related đã vào 16.2.11 và 16.2.13. Pacific hiện là nhánh đã archived/EOL và 16.2.15 là bản cuối của nhánh này.
        - Nếu có điều kiện bảo trì lớn hơn, nên lập kế hoạch lên nhánh mới hơn thay vì tiếp tục giữ cluster lâu dài ở Pacific đã EOL.

## Các bug ghi nhận trên Ceph 17.x


## Các bug ghi nhận trên Ceph 18.x


