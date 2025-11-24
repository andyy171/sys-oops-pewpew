# Mục lục
- [Access Control List (ACL) và Access Control Entry (ACE)](#access-control-list-acl-và-access-control-entry-ace)
    - [Access Control Entry (ACE)](#access-control-entry-ace)
    - [Access Control List (ACL)](#access-control-list-acl)
- [Phân Loại ACL Theo Chức Năng](#phân-loại-acl-theo-chức-năng)
    - [Discretionary Access Control List (DACL) – Kiểm soát Truy cập (Quyền hạn)](#discretionary-access-control-list-dacl--kiểm-soát-truy-cập-quyền-hạn)
    - [System Access Control List (SACL) – Giám sát Truy cập (Audit)](#system-access-control-list-sacl--giám-sát-truy-cập-audit)


---


# Access Control List (ACL) và Access Control Entry (ACE)
Mọi hệ thống kiểm soát truy cập đều dựa trên việc định nghĩa rõ ràng ai được phép làm gì với tài nguyên nào. Trong Windows, điều này được thực hiện thông qua các danh sách và mục nhập kiểm soát truy cập, giúp hệ thống đánh giá và quyết định quyền hạn một cách có hệ thống.

---

## Access Control Entry (ACE)
ACE là đơn vị nhỏ nhất và cơ bản nhất trong hệ thống kiểm soát truy cập. Hãy tưởng tượng ACE như một "quy tắc cá nhân hóa" – nó giống như một dòng lệnh chi tiết chỉ định quyền hạn cho một người dùng hoặc nhóm cụ thể. Mỗi ACE chứa bốn thông tin chính yếu, giúp hệ thống xác định chính xác cách xử lý yêu cầu truy cập.

- **Security Identifier (SID):** Đây là định danh duy nhất cho người dùng, nhóm người dùng, hoặc tài khoản dịch vụ. SID giống như một "chứng minh thư" kỹ thuật số, đảm bảo hệ thống nhận diện đúng đối tượng mà quy tắc áp dụng. Ví dụ, SID của một tài khoản người dùng cục bộ có thể trông như S-1-5-21-...-1001.

- **Access Mask:** Phần này mô tả cụ thể các quyền được cấp hoặc bị từ chối, dưới dạng một bit mask (một giá trị số đại diện cho các quyền). Các quyền phổ biến bao gồm đọc (READ), ghi (WRITE), thực thi (EXECUTE), xóa (DELETE), hoặc các quyền nâng cao như thay đổi quyền sở hữu. Access mask cho phép kết hợp nhiều quyền một cách linh hoạt, ví dụ: 0x000F0000 có thể đại diện cho quyền đọc và ghi.

- **ACE Type:** Xác định loại quy tắc mà ACE đại diện, chẳng hạn như cho phép truy cập (ACCESS_ALLOWED_ACE), từ chối truy cập (ACCESS_DENIED_ACE), hoặc dùng cho giám sát (SYSTEM_AUDIT_ACE). Loại này quyết định cách ACE được sử dụng – ví dụ, một ACE từ chối sẽ ưu tiên chặn quyền, trong khi ACE giám sát chỉ ghi log mà không ảnh hưởng đến truy cập.

- **Flags:** Các cờ này kiểm soát cách ACE được kế thừa (inheritance) bởi các đối tượng con, như thư mục con hoặc tệp con trong một thư mục. Ví dụ, flag CONTAINER_INHERIT_ACE cho phép quy tắc áp dụng cho các thư mục con, trong khi OBJECT_INHERIT_ACE áp dụng cho tệp. Điều này giúp tự động lan tỏa quyền hạn mà không cần thiết lập thủ công cho từng đối tượng.

> Bằng cách kết hợp các yếu tố này, ACE cung cấp một cơ chế linh hoạt để tùy chỉnh quyền truy cập, đảm bảo tính bảo mật và dễ quản lý.

## Access Control List (ACL)
- ACL là một danh sách có cấu trúc chứa từ zero đến nhiều ACE, hoạt động như một "danh sách kiểm tra" mà hệ thống tham chiếu khi có yêu cầu truy cập vào một đối tượng bảo mật. Khi một tiến trình hoặc người dùng cố gắng tương tác với một tài nguyên – ví dụ, mở một tệp – Windows sẽ quét qua ACL liên kết với tài nguyên đó. Thứ tự của các ACE trong ACL rất quan trọng: hệ thống kiểm tra chúng theo trình tự từ trên xuống dưới, dừng lại ngay khi tìm thấy quy tắc áp dụng đầy đủ cho yêu cầu. 

- Ví dụ, nếu một ACE từ chối xuất hiện trước, truy cập sẽ bị chặn ngay lập tức, ngay cả khi có ACE cho phép sau đó. Điều này nhấn mạnh tầm quan trọng của việc sắp xếp ACE một cách cẩn thận, thường ưu tiên các quy tắc từ chối trước để tránh lỗ hổng bảo mật. ACL được lưu trữ trong security descriptor của đối tượng, và bạn nên sử dụng các hàm API của Windows (như AddAce hoặc InitializeAcl) để thao tác với chúng, thay vì chỉnh sửa trực tiếp, để tránh lỗi cú pháp.

# Phân Loại ACL Theo Chức Năng
Trong Windows, ACL được chia thành hai loại chính dựa trên vai trò: một loại tập trung vào việc kiểm soát quyền truy cập thực tế (control), và loại kia dành cho giám sát và ghi log (audit). Sự phân biệt này cho phép quản trị viên không chỉ bảo vệ tài nguyên mà còn theo dõi hoạt động để phát hiện vấn đề.

## Discretionary Access Control List (DACL) – Kiểm soát Truy cập (Quyền hạn)

- **DACL** là danh sách các ACE quyết định ai được phép hoặc bị từ chối truy cập vào một đối tượng. Nó thực thi mô hình **Discretionary Access Control (DAC)**, nơi chủ sở hữu của đối tượng (hoặc người có quyền chỉnh sửa **DACL**) có thể tự do điều chỉnh quy tắc. Điều này mang lại sự linh hoạt, nhưng cũng đòi hỏi trách nhiệm cao để tránh cấp quyền sai.

- Các loại ACE chính trong DACL bao gồm `ACCESS_ALLOWED_ACE` (cho phép quyền) và `ACCESS_DENIED_ACE` (từ chối quyền). Quy trình kiểm tra truy cập diễn ra như sau: Khi có yêu cầu, hệ thống chuẩn bị một access mask đại diện cho các quyền cần thiết. Sau đó, nó quét DACL theo thứ tự, ưu tiên xử lý các ACE từ chối trước. Nếu tìm thấy ACE từ chối khớp với bất kỳ quyền nào, truy cập bị chặn ngay. Ngược lại, nếu tất cả quyền yêu cầu được bao phủ bởi các ACE cho phép mà không có từ chối, truy cập được cấp. Nếu DACL không cấp đủ quyền, yêu cầu sẽ thất bại.

- Một số lưu ý quan trọng về DACL:
+ Nếu đối tượng không có DACL nào (gọi là NULL DACL), hệ thống coi như không có bảo mật và cấp toàn quyền truy cập cho mọi người. Điều này rất nguy hiểm và nên tránh, vì nó mở cửa cho mọi rủi ro.
+ Nếu đối tượng có DACL nhưng DACL đó không chứa ACE nào (Empty DACL), hệ thống sẽ từ chối tất cả truy cập, ngay cả với chủ sở hữu. Đây là cách để khóa chặt tài nguyên, nhưng cần cẩn thận để không tự khóa mình ra ngoài.
+ Thứ tự ACE nên theo chuẩn: đặt deny trước allow, và ưu tiên các quy tắc cụ thể hơn chung chung để tránh kết quả bất ngờ.

> DACL là công cụ chính để bảo vệ tài nguyên hàng ngày, và hiểu rõ nó giúp quản trị viên thiết lập quyền hạn hiệu quả.

## System Access Control List (SACL) – Giám sát Truy cập (Audit)
- SACL tập trung vào việc giám sát thay vì kiểm soát trực tiếp. Nó chứa các ACE định nghĩa những sự kiện truy cập nào cần được ghi lại vào Security Event Log của Windows, hỗ trợ cho việc kiểm toán, phân tích pháp y, và tuân thủ quy định.

- Loại ACE chính ở đây là SYSTEM_AUDIT_ACE, có thể được cấu hình để ghi log khi truy cập thành công, thất bại, hoặc cả hai. Ví dụ, bạn có thể thiết lập SACL để ghi lại mọi nỗ lực đọc một tệp nhạy cảm bởi một nhóm người dùng cụ thể. Hệ thống sẽ tạo bản ghi audit dựa trên SID, access mask, và điều kiện thành công/thất bại trong ACE.
- Lưu ý quan trọng về SACL:

+ SACL không ảnh hưởng đến việc truy cập được cấp hay bị từ chối; đó là nhiệm vụ của DACL. Nó chỉ "quan sát" và ghi chép, giúp phát hiện hoạt động đáng ngờ mà không can thiệp.
+ Trong môi trường doanh nghiệp, SACL là yếu tố then chốt cho việc tuân thủ các tiêu chuẩn như GDPR hoặc HIPAA, bằng cách cung cấp lịch sử truy cập chi tiết để kiểm tra.
+ Để kích hoạt audit, bạn cần bật chính sách audit tương ứng trong Group Policy, vì SACL chỉ hoạt động khi hệ thống được cấu hình để ghi log.

> Tóm lại, SACL bổ sung cho DACL bằng cách cung cấp lớp giám sát, giúp hệ thống không chỉ an toàn mà còn minh bạch.