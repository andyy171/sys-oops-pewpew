# MGR (Ceph Manager)

## 1. MGR là gì và vì sao Ceph cần thêm MGR bên cạnh MON

**MGR (Ceph Manager)** là daemon bổ sung cho Ceph, chạy song song với các daemon `MON`, nhằm cung cấp thêm khả năng giám sát, tổng hợp thông tin và tạo các giao diện để tích hợp với hệ thống quản lý hoặc quan sát bên ngoài. Từ bản Ceph Luminous trở đi, `ceph-mgr` đã trở thành thành phần **bắt buộc** cho hoạt động bình thường của cluster; nếu không có MGR đang chạy, Ceph sẽ phát cảnh báo sức khỏe, và một phần thông tin trong `ceph status` sẽ bị thiếu hoặc lỗi thời. Điều này cho thấy MGR không phải là thành phần “phụ cho đẹp”, mà đã trở thành một phần của mặt điều khiển hiện đại của Ceph. :contentReference[oaicite:0]{index=0}

Nếu `MON` là nơi giữ **nguồn chân lý** về trạng thái cụm và duy trì **sự đồng thuận** giữa các monitor, thì MGR là lớp giúp Ceph **khai thác**, **trình bày** và **phân phối** khối trạng thái đó ra ngoài một cách hiệu quả hơn. RHCS 5 và RHCS 8 Architecture Guides đều mô tả rằng Ceph Manager duy trì thông tin chi tiết về **placement groups**, **metadata của tiến trình** và **metadata của máy chủ**, nhờ đó giảm gánh cho `MON` và cải thiện hiệu năng ở quy mô lớn. MGR còn thực thi nhiều truy vấn chỉ đọc của dòng lệnh Ceph, như thống kê placement groups, và cung cấp các giao diện giám sát kiểu RESTful. :contentReference[oaicite:1]{index=1}

Vì vậy, nếu nhìn Ceph theo lớp chức năng, có thể hiểu:
- `MON` giữ trạng thái cốt lõi và sự đồng thuận
- `OSD` giữ dữ liệu và xử lý luồng dữ liệu đi
- `MGR` giữ lớp quan sát, tổng hợp, giao diện và tích hợp quản trị ở phía trên

Cách chia vai này rất quan trọng. Nếu không có MGR, cluster vẫn không mất ngay vai trò lưu trữ dữ liệu như khi mất OSD, nhưng nhiều khả năng giám sát, quản trị, truy vấn trạng thái và module tích hợp sẽ bị suy giảm rõ rệt. :contentReference[oaicite:2]{index=2}

## 2. Vai trò cốt lõi của MGR trong kiến trúc Ceph

MGR tồn tại vì `MON` không nên phải ôm toàn bộ gánh nặng của các truy vấn trạng thái chi tiết khi cluster lớn dần. RHCS 5 và RHCS 8 cùng nhấn mạnh rằng MGR giữ nhiều thông tin chi tiết về placement groups, metadata tiến trình và metadata máy chủ **thay cho** `MON`, nhờ đó cải thiện hiệu năng ở quy mô lớn. Đây là vai trò kiến trúc quan trọng nhất của MGR: nó giúp tách phần **nguồn chân lý cần sự đồng thuận mạnh** ra khỏi phần **tổng hợp và phục vụ thông tin quan sát** vốn thay đổi thường xuyên hơn. :contentReference[oaicite:3]{index=3}

Vai trò thứ hai của MGR là thực thi nhiều truy vấn chỉ đọc của Ceph CLI. Điều này làm cho người quản trị có thể xem các thông tin như thống kê PG, trạng thái cụm, hoặc dữ liệu quan sát mà không buộc `MON` phải trực tiếp xử lý toàn bộ phần đọc trạng thái chi tiết đó. Ở góc nhìn thực tế, MGR là nơi giúp Ceph “thở” tốt hơn khi quy mô cluster tăng, vì nó hấp thụ phần truy vấn giám sát vốn rất dễ phình ra theo số OSD, số PG và số host. :contentReference[oaicite:4]{index=4}

Vai trò thứ ba của MGR là cung cấp **nền module** cho rất nhiều khả năng quản trị và quan sát hiện đại. Trong Ceph Pacific và Squid, trang tài liệu của Ceph Manager liệt kê nhiều module chạy trong MGR như `Dashboard`, `Prometheus`, `Telemetry`, `Alerts`, `Crash`, `Orchestrator`, `NFS`, `RGW`, `MDS Autoscaler`, và nhiều module khác. Điều này cho thấy MGR không chỉ là “một daemon xem trạng thái”, mà là một **nền chạy module quản trị** của Ceph. :contentReference[oaicite:5]{index=5}

### Tóm tắt ngắn về ba vai trò lớn của MGR

- Giảm tải cho `MON` bằng cách giữ và phục vụ khối trạng thái chi tiết hơn. :contentReference[oaicite:6]{index=6}
- Thực thi nhiều truy vấn chỉ đọc của CLI và cung cấp API giám sát. :contentReference[oaicite:7]{index=7}
- Là nền cho hệ sinh thái module quản trị và tích hợp của Ceph. :contentReference[oaicite:8]{index=8}

## 3. MGR không thay thế MON và cũng không thay thế OSD

Một điểm rất dễ hiểu sai là tưởng rằng khi MGR giữ nhiều thông tin chi tiết, nó đã “thay thế” vai trò của `MON`. Điều này không đúng. `MON` vẫn là nơi giữ bản sao chủ của `Cluster Map`, duy trì sự đồng thuận bằng Paxos và quyết định trạng thái logic chính thức của cluster. MGR chỉ lấy, giữ và phục vụ thêm các lớp thông tin phục vụ quan sát và quản trị. Nói ngắn gọn: `MON` giữ **đúng sai chính thức** của cluster, còn `MGR` giúp cluster **nhìn thấy chính nó rõ hơn**. :contentReference[oaicite:9]{index=9}

Tương tự, MGR cũng không thay thế `OSD`. MGR không nằm trong luồng dữ liệu đi của từng lần đọc hoặc ghi object. Dữ liệu thực sự vẫn đi từ client tới `OSD` sau khi client có đủ `Cluster Map` để tính placement. MGR có thể cung cấp thông tin trạng thái, thống kê, bảng điều khiển web, số liệu Prometheus, nhưng MGR không phải là điểm mà mọi lệnh đọc/ghi dữ liệu đều phải đi qua. Đây là ranh giới kiến trúc rất quan trọng để tránh nhầm `MGR` với một bộ điều phối dữ liệu trung tâm. :contentReference[oaicite:10]{index=10}

## 4. MGR làm việc với trạng thái cluster như thế nào

Một điểm rất hay của tài liệu developer guide cho `ceph-mgr` là nó cho thấy vì sao MGR có thể phục vụ tốt vai trò giám sát và quản trị. Các module của MGR có quyền truy cập vào **bản sao trạng thái của cluster đang nằm trong bộ nhớ mà MGR giữ**, và chúng có thể nhận thông báo khi các phần quan trọng của trạng thái cluster thay đổi, như `osd_map`, `mon_map`, `fs_map`, `health`, `pg_summary` hay `service_map`. Điều này cho phép module phản ứng nhanh với thay đổi của cluster mà không phải liên tục gọi vòng ra bên ngoài như một ứng dụng độc lập. :contentReference[oaicite:11]{index=11}

Điểm này giải thích vì sao MGR phù hợp để làm nơi chạy `Dashboard`, `Prometheus module`, `Alerts module` hoặc các plugin quản trị khác. Nó đã có sẵn một lớp truy cập tới trạng thái trong bộ nhớ của cluster và có cơ chế thông báo khi dữ liệu thay đổi. Nếu các tính năng đó phải tự đi lấy dữ liệu qua nhiều tầng API bên ngoài thì chi phí sẽ lớn hơn, độ trễ cao hơn và độ phức tạp cũng tăng lên. :contentReference[oaicite:12]{index=12}

### Minh họa vai trò của MGR với trạng thái cluster

```text
MON giữ trạng thái chính thức của cluster
            ↓
      MGR nhận và duy trì
 bản sao trạng thái chi tiết hơn
            ↓
   Các module trong MGR khai thác:
   - thống kê PG
   - metadata daemon
   - metadata host
   - sức khỏe cluster
   - dữ liệu hiệu năng
            ↓
 Dashboard / Prometheus / API / CLI chỉ đọc
```

> Keynote: MGR tồn tại để Ceph quan sát được chính nó và mở rộng được về mặt quản trị, chứ không phải để thay MON hay OSD. Điểm giá trị nhất khi hiểu MGR là nhận ra Ceph đã tách riêng rất rõ: MON giữ trạng thái cốt lõi cần sự đồng thuận, OSD giữ dữ liệu và xử lý luồng dữ liệu đi, còn MGR giữ lớp tổng hợp, thống kê, bảng điều khiển và các module quản trị. Nhờ vậy, cluster có thể lớn lên mà phần trạng thái chi tiết và phần tích hợp giám sát không đè quá nặng lên MON.
## 5. MGR và các module: vì sao đây là điểm mạnh của Ceph hiện đại

Kiến trúc module là thứ làm MGR trở thành một trong những thành phần thú vị nhất của Ceph hiện đại. Tài liệu Pacific và Squid về Ceph Manager cho thấy một danh sách khá dài các module có thể chạy trong MGR, từ Dashboard, Prometheus, Telemetry, Alerts, Crash, Insights, NFS, RGW module, đến Orchestrator module. Điều này có nghĩa M**GR là nền mở rộng chức năng quản trị chứ không phải chỉ là “dịch vụ hiển thị trạng thái”.**

### 5.1 Dashboard module

Ceph Dashboard là ứng dụng web tích hợp sẵn để giám sát và quản trị cluster. Cả Pacific và Squid docs đều khẳng định Dashboard được triển khai như một module của Ceph Manager Daemon. Ở Squid, tài liệu còn mô tả rõ hơn rằng phần giao diện đồ họa và máy chủ web của Dashboard được lưu trú trong ceph-mgr. Điều này cho thấy Dashboard không phải sản phẩm ngoài lề gắn thêm vào Ceph, mà là một phần tự nhiên của hệ module trong MGR.

### 5.2 Prometheus module

Prometheus module biến MGR thành điểm xuất số liệu cho Prometheus. Tài liệu Ceph nêu rõ module này xuất các bộ đếm hiệu năng của Ceph từ điểm tập hợp trong Manager. Manager nhận các bản tin MMgrReport từ những tiến trình thuộc nhóm MgrClient, bao gồm cả MON và OSD, giữ một bộ đệm vòng của các mẫu gần nhất, rồi mở một đầu cuối HTTP để Prometheus truy vấn. Điều này giải thích rất rõ vì sao MGR lại thích hợp cho vai trò “điểm tập trung số liệu”: nó đã đứng đúng chỗ giữa nhiều daemon và trạng thái cluster.

### 5.3 Orchestrator module

Tài liệu về orchestrator modules cho thấy một orchestrator module thực chất là một module của `ceph-mgr` triển khai các thao tác quản lý chung bằng một bộ điều phối cụ thể. Mục đích của lớp giao diện chung này là để các mã giao diện dùng chung, như Dashboard, có thể làm việc với nhiều backend khác nhau. Điều này rất đáng chú ý vì nó cho thấy MGR không chỉ quan sát cluster, mà còn có thể trở thành cửa ngõ điều phối quản trị trong các triển khai hiện đại.


## 6. MGR và tính sẵn sàng cao

Khác với MON, các daemon **MGR không cần một cơ chế quorum riêng giữa chúng**. Tài liệu RHCS 5 Operations Guide nói rất rõ: *khi có nhiều ceph-mgr, instance nào khởi động trước sẽ được MON chọn làm MGR hoạt động chính, các daemon còn lại là MGR chờ thay thế*; **không có yêu cầu phải có quorum giữa các ceph-mgr**. Nếu MGR chính không gửi tín hiệu sống (beacon) cho MON quá thời gian mon mgr beacon grace, nó sẽ bị thay bằng một MGR chờ.

Điều này cho thấy mô hình sẵn sàng cao của MGR khác với MON:

- MON cần đa số để giữ sự đồng thuận
- MGR chỉ cần một daemon hoạt động chính và một hay nhiều daemon chờ thay thế

> Nói cách khác, MGR có tính sẵn sàng cao kiểu chủ động/chờ thay thế, còn MON có tính sẵn sàng cao kiểu đa số đồng thuận. Đây là một phân biệt rất quan trọng trong kiến trúc Ceph, vì nhiều người mới dễ suy diễn rằng mọi daemon lõi đều phải có quorum như nhau.

RHCS 5 Operations Guide còn khuyên nên triển khai MGR trên mỗi host đang chạy MON để đạt mức sẵn sàng cao tương đương. Đây là khuyến nghị thực dụng: tuy MGR không cần quorum, nhưng nếu mất luôn daemon hoạt động chính mà không có daemon chờ phù hợp thì Dashboard, một số API giám sát và nhiều tính năng module sẽ bị gián đoạn.

## 7. MGR trong vận hành hiện đại: vai trò với Cephadm và Orchestrator

- Trong triển khai hiện đại dùng Cephadm, MGR còn đóng một vai trò thực dụng hơn: nó trở thành nơi gắn với Ceph Orchestrator. RHCS 5 Operations Guide mô tả rằng khi dùng Cephadm Orchestrator, ý tưởng là cung cấp cho manager daemon quyền truy cập SSH và cấu hình cần thiết để kết nối tới các node trong cluster, từ đó thực hiện các thao tác quản lý như tạo danh mục thiết bị lưu trữ, triển khai hoặc thay thế OSD, hay khởi động và dừng các daemon Ceph.

- Điểm này rất quan trọng nhưng cần đặt đúng chỗ trong tư duy. Nó không làm thay đổi bản chất của MGR như một thành phần quản trị và giám sát. Nó chỉ cho thấy trong Ceph hiện đại, MGR đã trở thành nền hợp lý để gắn các lớp điều phối vận hành. Vì file này tập trung vào vai trò cốt lõi của component, chúng ta chỉ nhấn mạnh rằng MGR là nơi rất phù hợp để đặt lớp điều phối đó, còn chi tiết về Cephadm hay day-2 operations nên quay lại ở nhánh operations.

## 8. Pacific / RHCS 5 và Squid / RHCS 8: những gì giữ nguyên và những gì rõ hơn

Về bản chất, vai trò của MGR gần như không đổi giữa Pacific và Squid, cũng như giữa RHCS 5 và RHCS 8:

- MGR chạy cùng lớp với MON
- MGR là thành phần bắt buộc cho hoạt động bình thường
- MGR giảm tải cho MON bằng cách giữ thông tin chi tiết hơn
- MGR thực thi nhiều truy vấn chỉ đọc
- MGR là nơi chạy các module quản trị và giám sát như Dashboard hay Prometheus.

## 9. Những hiểu lầm phổ biến về MGR

- Hiểu lầm phổ biến nhất là nghĩ rằng MGR là nơi mọi lệnh đọc/ghi dữ liệu phải đi qua. Điều này sai. MGR không nằm trong luồng dữ liệu đi của từng thao tác I/O. Dữ liệu thực sự vẫn đi giữa client và OSD sau khi placement đã được tính từ Cluster Map. MGR chủ yếu phục vụ quan sát, API, tổng hợp trạng thái và các module quản trị.

- Hiểu lầm thứ hai là cho rằng MGR thay thế MON. Điều này cũng sai. MON vẫn là nơi giữ trạng thái chính thức của cluster và duy trì sự đồng thuận. MGR chỉ giữ thông tin chi tiết hơn để phục vụ truy vấn và module. Có thể hiểu MGR là lớp bổ trợ cho control plane, chứ không phải lớp thay thế control plane gốc.

- Hiểu lầm thứ ba là tưởng rằng các ceph-mgr cũng cần quorum như MON. Trên thực tế, tài liệu RHCS 5 nói rõ không có yêu cầu quorum giữa các MGR. Chúng hoạt động theo mô hình một daemon hoạt động chính và các daemon chờ thay thế. Nếu nhầm điểm này, bạn sẽ dễ thiết kế sai hoặc diễn giải sai vai trò sẵn sàng cao của MGR.

- Hiểu lầm cuối cùng là xem Dashboard hay Prometheus như các hệ thống hoàn toàn đứng ngoài Ceph. Cả hai đều có thể được triển khai như module của MGR. Điều đó cho thấy MGR là hạt nhân rất quan trọng của lớp quản trị Ceph hiện đại.

## 10. Kết luận

MGR là lớp giám sát, tổng hợp và mở rộng quản trị của Ceph. Nó giúp giảm tải cho MON, giữ thông tin chi tiết hơn về placement groups, daemon và host, thực thi nhiều truy vấn chỉ đọc, và cung cấp nền để chạy các module như Dashboard, Prometheus hay Orchestrator. Vì vậy, MGR không phải là nơi lưu dữ liệu như OSD, cũng không phải nơi giữ sự đồng thuận như MON, mà là lớp làm cho cluster quan sát được, quản trị được và mở rộng được về mặt chức năng.

> MGR là thành phần giúp Ceph nhìn thấy chính nó rõ hơn và giao tiếp tốt hơn với thế giới quản trị bên ngoài, trong khi MON vẫn giữ sự thật logic của cluster và OSD vẫn giữ dữ liệu.