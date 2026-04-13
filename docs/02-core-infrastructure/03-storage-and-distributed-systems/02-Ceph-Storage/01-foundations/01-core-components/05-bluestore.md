# BlueStore - Storage backend Ceph

## 1. BlueStore là gì
- BlueStore là back-end object store của các daemon OSD, và ghi object trực tiếp lên thiết bị khối thay vì đi qua một hệ thống tệp cục bộ như XFS. BlueStore là back-end lưu trữ được thiết kế riêng cho Ceph; BlueStore được giới thiệu từ Kraken, trở thành mặc định từ Luminous, và đến Reef thì FileStore không còn là back-end khả dụng nữa. RHCS 8 Administration Guide cũng nêu rất thẳng rằng BlueStore là back-end lưu trữ object cho OSD và đặt object trực tiếp lên block device.

- Điều này làm BlueStore trở thành một trong những thay đổi kiến trúc quan trọng nhất của Ceph hiện đại. Nếu ở thời FileStore, OSD còn phải đi qua một lớp hệ thống tệp cục bộ rồi mới tới block device, thì với BlueStore, Ceph bỏ qua lớp trung gian đó và quản lý lưu trữ ở mức thấp hơn. RHCS 5 Architecture Guide giải thích rằng BlueStore loại bỏ lớp gián tiếp kiểu “thư mục đại diện cho PG, file đại diện cho object và xattr đại diện cho metadata”, đồng thời loại bỏ hình phạt ghi hai lần của FileStore.

## 2. Vì sao BlueStore ra đời

- RHCS 5 Architecture Guide mô tả khá rõ bối cảnh ra đời của BlueStore: khi SSD và NVMe trở nên phổ biến, những giới hạn của FileStore bộc lộ rõ hơn, trong đó có chi phí tăng cao khi số lượng placement groups tăng và hiện tượng ghi hai lần. BlueStore được xây dựng như thế hệ lưu trữ kế tiếp cho Ceph để loại bỏ những lớp trung gian không cần thiết, tận dụng tốt hơn thiết bị khối hiện đại và giảm chi phí nội bộ của đường ghi.

- Điểm quan trọng ở đây không chỉ là “BlueStore nhanh hơn”, mà là BlueStore thay đổi cách OSD tương tác với thiết bị lưu trữ. **FileStore dựa vào filesystem cục bộ để biểu diễn object và metadata; BlueStore thì dùng thiết kế riêng của Ceph để lưu object data, metadata, nhật ký ghi trước và cơ chế kiểm tra toàn vẹn**. Nhờ đó, BlueStore không chỉ cải thiện hiệu năng mà còn làm kiến trúc OSD phù hợp hơn với bản chất object store phân tán của Ceph.

## 3. Kiến trúc cốt lõi của BlueStore

- BlueStore có thể được hiểu qua bốn khối chính:
    - dữ liệu object
    - metadata nội bộ
    - BlueFS
    - thiết bị khối chính và các thiết bị phụ

- Dữ liệu object được ghi trực tiếp lên raw block device. RHCS 5 Architecture Guide nói rõ object data trong BlueStore được lưu thành các khối trực tiếp trên raw block device và phần đó **không chứa filesystem**. Metadata nội bộ được quản lý bằng RocksDB, nơi giữ các ánh xạ từ object sang vị trí block, thông tin liên quan tới PG và metadata của object. BlueStore dùng một lớp filesystem rất nhẹ tên là BlueFS để lưu các file của RocksDB trên thiết bị nhỏ hơn hoặc nhanh hơn nếu có.

- Từ góc nhìn tư duy, BlueStore không phải là “filesystem mới của Linux”, mà là một **backend lưu trữ chuyên dụng cho OSD**. Nó vừa quản lý trực tiếp block device, vừa duy trì metadata qua RocksDB, vừa dựa vào BlueFS để chứa dữ liệu của RocksDB. Chính sự kết hợp này làm cho BlueStore khác hẳn FileStore: FileStore dựa vào một filesystem hiện hữu; BlueStore xây dựng mặt bằng lưu trữ của riêng mình, phù hợp hơn với object storage phân tán.

### Minh họa cấu trúc logic của BlueStore
```
OSD
 ↓
BlueStore
 ├─ Dữ liệu object trên block device chính
 ├─ Metadata nội bộ trong RocksDB
 └─ BlueFS lưu các file RocksDB trên block.db / block.wal nếu có
```

> Keynote : BlueStore không chỉ là một backend “nhanh hơn FileStore”, mà là một cách nghĩ khác hẳn về lưu trữ của OSD. Điểm mấu chốt là BlueStore bỏ lớp filesystem trung gian cho object data và để OSD làm việc gần block device hơn. Điều này không chỉ cải thiện hiệu năng, mà còn làm cho backend của Ceph phù hợp hơn với bản chất object store phân tán của nó. Một cách nhớ rất tốt là: BlueStore không chỉ tối ưu đường ghi, mà còn làm cho OSD bớt phải giả vờ rằng object là file.

## 4. BlueStore lưu dữ liệu như thế nào

- RHCS 8 Administration Guide liệt kê các đặc tính chính của BlueStore gồm:

    - quản lý trực tiếp thiết bị lưu trữ
    - quản lý metadata bằng RocksDB
    - kiểm tra toàn vẹn dữ liệu và metadata bằng checksum
    - nén dữ liệu nội tuyến
    - cơ chế copy-on-write hiệu quả
    - hỗ trợ nhiều thiết bị khối cho các lớp dữ liệu khác nhau
    - giảm nhu cầu ghi hai lần.

- Trong đó, hai điểm quan trọng nhất để hiểu kiến trúc là:

    - Object data nằm trực tiếp trên block device chính.
    - Metadata nội bộ như ánh xạ object → block locations nằm trong RocksDB.

- Điều này có nghĩa BlueStore chia trách nhiệm rất rõ:

    - phần dữ liệu lớn của object đi xuống block device chính
    - phần metadata và ánh xạ đi vào cơ sở dữ liệu khóa-giá trị
    - các file của cơ sở dữ liệu này có thể nằm trên thiết bị nhanh hơn nếu bạn cung cấp `block.db` hoặc `block.wal`

- Từ đó, khi phân tích hiệu năng hay sự cố OSD, bạn phải luôn tự hỏi vấn đề nằm ở:

    - thiết bị chứa object data
    - hay thiết bị chứa RocksDB / BlueFS
## 5. BlueFS và vai trò của nó

- RHCS 5 Architecture Guide nói rõ BlueStore dùng BlueFS, một filesystem rất nhẹ, trên một phân vùng nhỏ để chứa cơ sở dữ liệu khóa-giá trị của nó. Đây là một chi tiết rất dễ bị bỏ qua khi mới học BlueStore. BlueStore “không dùng filesystem” cho object data không có nghĩa là toàn bộ thế giới nội bộ của nó không có bất kỳ lớp file nào; đúng hơn là object data không nằm trên filesystem cục bộ kiểu XFS, còn các file RocksDB có thể được BlueFS quản lý trên thiết bị chuyên dụng hơn.

- Vai trò của BlueFS vì vậy là làm lớp rất nhẹ cho RocksDB và dữ liệu nội bộ liên quan, không phải là lớp lưu object data chung cho OSD. Giữ ranh giới này rõ rất quan trọng, vì nếu không người đọc rất dễ hiểu sai rằng “BlueStore vẫn dùng filesystem như cũ, chỉ đổi tên thôi”. Thực ra phần thay đổi căn bản là object data không còn nằm trong filesystem cục bộ như FileStore nữa.

> Keynote: Câu “BlueStore không dùng filesystem” cần hiểu cẩn thận. Đúng hơn phải nói: BlueStore không dùng filesystem cục bộ để lưu object data như FileStore, còn metadata nội bộ của chính BlueStore vẫn đi qua RocksDB và BlueFS. Nếu không phân biệt được điều này, người học rất dễ rơi vào hai cực đoan: hoặc nghĩ BlueStore hoàn toàn không có lớp file nào, hoặc nghĩ nó thực chất vẫn là filesystem cũ đổi tên. Cả hai đều sai. BlueStore là một thiết kế lưu trữ mới, trong đó object data nằm trực tiếp trên block device, còn metadata nội bộ vẫn dùng cơ sở dữ liệu khóa-giá trị và một lớp filesystem rất nhẹ để quản lý các file của cơ sở dữ liệu đó. Hiểu đúng điều này sẽ giúp bạn nắm được kiến trúc cốt lõi của BlueStore.

## 6. RocksDB trong BlueStore

- BlueStore dùng RocksDB để quản lý metadata nội bộ, ví dụ ánh xạ từ tên object tới vị trí block trên đĩa. RHCS 8 Administration Guide nói rõ BlueStore dùng RocksDB key-value database để quản lý metadata như `object-name-to-block-location` mapping. RHCS 5 Architecture Guide cũng mô tả block database giữ object semantics để bảo đảm tính nhất quán, với khóa là định danh duy nhất của object và giá trị gồm địa chỉ block, PG và metadata liên quan.

- Một điểm khác biệt đáng kể theo phiên bản là **RocksDB sharding**. BlueStore Configuration Reference của Pacific nêu rằng trước Pacific, toàn bộ dữ liệu key-value nằm trong một column family mặc định; từ Pacific trở đi, BlueStore có thể chia dữ liệu key-value thành nhiều column families, giúp bộ nhớ đệm tốt hơn và quá trình compaction chính xác hơn. Các OSD được triển khai mới từ Pacific trở lên dùng RocksDB sharding mặc định, nhưng OSD cũ được nâng cấp lên Pacific thì không tự bật sharding cho dữ liệu cũ. Đây là một khác biệt theo phiên bản đủ đáng kể để cần ghi nhớ.

## 7. Đường ghi của BlueStore ở mức khái niệm

- Một trong những ý hay nhất trong RHCS 8 Administration Guide là mô tả cơ chế “không ghi hai lần lớn” của BlueStore. Tài liệu giải thích rằng BlueStore trước hết ghi dữ liệu mới vào vùng chưa cấp phát trên block device, rồi mới xác nhận giao dịch trong RocksDB để cập nhật metadata object trỏ tới vùng đĩa mới đó. Chỉ khi thao tác ghi nhỏ hơn một ngưỡng có thể cấu hình, BlueStore mới quay về một mô hình kiểu ghi trước vào nhật ký. Điều này cho thấy BlueStore đã tái thiết kế write path để tránh kiểu “ghi vào journal rồi lại ghi vào filesystem data area” như FileStore trước kia.

Ở mức tư duy, có thể hình dung write path của BlueStore như sau:
```
Primary OSD / replica OSD nhận thao tác ghi
            ↓
BlueStore ghi dữ liệu object vào vùng block chưa cấp phát
            ↓
RocksDB cập nhật ánh xạ metadata trỏ tới vùng block mới
            ↓
Giao dịch được xác nhận hoàn tất
```
> Đây là một thay đổi cực quan trọng vì nó giải thích tại sao BlueStore giảm được hình phạt ghi hai lần và vì sao luồng ghi của OSD hiện đại không nên được mô tả bằng ngôn ngữ “journal trước, filesystem sau” như thời FileStore nữa.

## 8. `block`, `block.db`, `block.wal` là gì

- RHCS 5 Administration Guide nêu rất rõ các cấu hình thiết bị mà BlueStore OSD backend hỗ trợ:
    - một thiết bị block
    - block + block.wal
    - block + block.db
    - block + block.db + block.wal
- Ý nghĩa của từng thành phần
    - `block` là thiết bị chính chứa phần lớn dữ liệu object. Đây là thiết bị bắt buộc.
    - `block.db` là nơi có thể đặt RocksDB và dữ liệu metadata trên một thiết bị nhanh hơn, thường là SSD hoặc NVMe.
    - `block.wal` là nơi có thể đặt phần ghi trước của RocksDB hoặc phần ghi nhanh trên thiết bị độ trễ rất thấp hơn nữa. RHCS 8 docs mô tả ví dụ dùng HDD cho dữ liệu, SSD cho metadata và NVM/NVRAM cho WAL.

## 9. Checksum, nén dữ liệu và copy-on-write

- BlueStore không chỉ thay đổi đường ghi mà còn đưa nhiều tính năng toàn vẹn và tối ưu xuống ngay trong backend. RHCS 8 Administration Guide nói rõ mặc định mọi dữ liệu và metadata ghi vào BlueStore đều được bảo vệ bằng một hoặc nhiều checksum; không có dữ liệu hay metadata nào được đọc từ đĩa hoặc trả về cho người dùng mà không được kiểm tra. Điều này làm BlueStore trở thành một lớp rất quan trọng trong mô hình toàn vẹn dữ liệu của OSD.

- BlueStore cũng hỗ trợ nén dữ liệu nội tuyến. Pacific BlueStore Configuration Reference cho biết các thuộc tính nén có thể đặt theo mức toàn cục hoặc theo từng pool, bao gồm thuật toán nén, chế độ nén, tỷ lệ bắt buộc, kích thước blob tối thiểu và tối đa. Điều này cho thấy nén trong BlueStore không phải tính năng ngoài lề, mà là phần gắn trực tiếp với hành vi lưu trữ của backend.

- Ngoài ra, RHCS 8 Administration Guide nêu rằng snapshots của Ceph Block Device và Ceph File System dựa vào cơ chế copy-on-write clone được triển khai hiệu quả trong BlueStore. Đây là điểm rất quan trọng để hiểu rằng BlueStore không chỉ là tối ưu hiệu năng ghi, mà còn là nền cho một số hành vi nâng cao của hệ thống như snapshot và các cơ chế ghi hai pha hiệu quả trong một số trường hợp dùng erasure coding.

## 10. Tự động tinh chỉnh và ý nghĩa thực tế

RHCS 5 và RHCS 8 Administration Guides đều nêu rằng BlueStore mặc định được cấu hình theo hướng tự động tinh chỉnh. Red Hat còn khuyến nghị nếu bạn thấy môi trường của mình chạy tốt hơn với tinh chỉnh thủ công thì nên làm việc với hỗ trợ kỹ thuật thay vì coi việc tự tay chỉnh sâu là trạng thái chuẩn mặc định. Điều này rất đáng chú ý ở góc nhìn học tập: BlueStore có nhiều tùy chọn, nhưng triết lý tài liệu chính thống hiện nay là ưu tiên hành vi mặc định tự điều chỉnh trước, rồi mới cân nhắc tinh chỉnh sâu khi thật sự có lý do.

## 11. Những điểm cần phân biệt theo phiên bản

Với BlueStore, có một vài khác biệt theo phiên bản đáng để ghi riêng vì chúng ảnh hưởng trực tiếp tới cách hiểu hoặc cách vận hành:

### 11.1 BlueStore là mặc định, FileStore đã hết thời

Ceph glossary nêu rằng BlueStore trở thành mặc định từ Luminous, và từ Reef thì FileStore không còn là back-end khả dụng nữa. Điều này có nghĩa:

ở Pacific / RHCS 5, BlueStore đã là lựa chọn mặc định và được ưu tiên mạnh
ở Squid / RHCS 8, về thực tế bạn gần như đang sống trong một thế giới BlueStore-only đối với back-end OSD hiện đại.
### 11.2 RocksDB sharding là thay đổi quan trọng từ Pacific

Pacific BlueStore Configuration Reference nói rõ rằng từ Pacific trở đi, BlueStore có thể chia dữ liệu khóa-giá trị thành nhiều column families và OSD triển khai mới từ Pacific dùng sharding mặc định. Đây là khác biệt đủ lớn để cần ghi nhớ vì nó ảnh hưởng tới bộ nhớ đệm, compaction và hành vi của metadata store nội bộ.

Ngoài hai điểm này, phần lớn các docs RHCS 5, RHCS 8, Pacific và Squid đồng nhất nhau về bản chất kiến trúc của BlueStore: back-end trực tiếp trên block device, RocksDB cho metadata, BlueFS cho dữ liệu RocksDB, checksum, nén và copy-on-write. Vì vậy, không cần cố tách hai bài BlueStore riêng cho Pacific và Squid.

## 12. Những hiểu lầm phổ biến về BlueStore

- Hiểu lầm phổ biến nhất là cho rằng BlueStore chỉ là “FileStore nhưng nhanh hơn”. Điều này sai. BlueStore đổi cả mô hình lưu trữ nội bộ: object data nằm trực tiếp trên block device, metadata nằm trong RocksDB, BlueFS phục vụ RocksDB, và lớp filesystem trung gian kiểu XFS không còn đứng giữa object data và thiết bị nữa.

- Hiểu lầm thứ hai là câu “BlueStore không dùng filesystem” được hiểu quá tuyệt đối. Đúng hơn phải nói: BlueStore không dùng filesystem cục bộ để lưu object data như FileStore; còn với dữ liệu RocksDB, BlueStore vẫn dùng BlueFS như một lớp filesystem rất nhẹ để quản lý các file nội bộ đó. Nếu không phân biệt rõ hai lớp này, người đọc rất dễ hình dung sai kiến trúc.

- Hiểu lầm thứ ba là xem block.db hay block.wal như thành phần bắt buộc. Chúng không bắt buộc; cấu hình tối thiểu vẫn có thể chỉ dùng một thiết bị block. Tuy nhiên, việc tách block.db và block.wal ra thiết bị nhanh hơn có thể giúp metadata path và phần ghi trước có độ trễ thấp hơn.

- Hiểu lầm cuối cùng là đồng nhất BlueStore với OSD. BlueStore là backend của OSD, không phải là toàn bộ OSD. OSD còn chịu trách nhiệm placement, vai trò primary/secondary, peering, recovery, scrub và tương tác với cluster state. BlueStore chủ yếu giải quyết bài toán persistence, metadata nội bộ và tính toàn vẹn ở tầng backend.


> BlueStore là nền tảng lưu trữ hiện đại của OSD trong Ceph. Nó thay thế mô hình FileStore cũ bằng cách ghi object trực tiếp lên block device, quản lý metadata qua RocksDB, dùng BlueFS cho dữ liệu nội bộ của RocksDB, hỗ trợ checksum, nén dữ liệu, copy-on-write và nhiều cấu hình thiết bị như block, block.db, block.wal. Hiểu đúng BlueStore là hiểu phần “mặt đất” mà OSD đứng lên để thực thi mọi thao tác lưu trữ.
> BlueStore là lớp backend giúp OSD ghi dữ liệu theo đúng bản chất object store của Ceph, bỏ lớp filesystem trung gian kiểu cũ và đưa nhiều chức năng về hiệu năng lẫn toàn vẹn dữ liệu xuống gần thiết bị khối hơn.