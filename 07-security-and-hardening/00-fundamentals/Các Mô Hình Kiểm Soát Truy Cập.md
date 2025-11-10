# Mục lục

- [Mô Hình Phân Quyền Tùy Ý (Discretionary Access Control - DAC)](#mô-hình-phân-quyền-tùy-ý-discretionary-access-control---dac)
- [Mô Hình Phân Quyền Bắt Buộc (Mandatory Access Control - MAC)](#mô-hình-phân-quyền-bắt-buộc-mandatory-access-control---mac)
- [Mô Hình Phân Quyền Dựa Trên Vai Trò (Role-Based Access Control - RBAC))](#mô-hình-phân-quyền-dựa-trên-vai-trò-role-based-access-control---rbac)
- [So Sánh Tổng Quan Các Mô Hình](#so-sánh-tổng-quan-các-mô-hình)


---

# Mô Hình Phân Quyền Tùy Ý (Discretionary Access Control - DAC)
- DAC là mô hình phổ biến nhất trong các hệ thống thông thường, nơi quyền quyết định nằm chủ yếu ở chủ sở hữu tài nguyên, mang lại sự linh hoạt cao nhưng cũng tiềm ẩn rủi ro bảo mật. Hãy tưởng tượng DAC như một hệ thống khóa cửa nơi chủ nhà có thể tự do phát chìa khóa cho bất kỳ ai họ muốn – tiện lợi nhưng dễ bị lạm dụng nếu không cẩn thận.
- **Định nghĩa:** DAC cho phép chủ sở hữu của một đối tượng (như tệp tin, thư mục, hoặc tài nguyên hệ thống) toàn quyền quyết định ai được truy cập và ở mức độ nào. Quyền hạn là "tùy ý" vì chủ sở hữu có thể chuyển giao quyền đó cho người dùng khác mà không cần phê duyệt trung ương. Điều này khác biệt với các mô hình nghiêm ngặt hơn, nơi quyền hạn được kiểm soát tập trung.
- **Cơ chế Phân quyền:** Quyền truy cập được thực thi thông qua Discretionary Access Control List (DACL), như đã thảo luận ở File 1. DACL liệt kê các Access Control Entry (ACE) cho phép hoặc từ chối quyền dựa trên định danh người dùng hoặc nhóm. Hệ thống kiểm tra DACL để quyết định truy cập, và chủ sở hữu có thể chỉnh sửa nó bất kỳ lúc nào.
+ **Ưu điểm:** DAC cung cấp tính linh hoạt cao, dễ dàng quản lý quyền ở cấp độ cục bộ, phù hợp cho môi trường cá nhân hoặc nhóm nhỏ nơi người dùng cần tự do chia sẻ tài nguyên.
+ **Nhược điểm:**
* Nguy cơ bảo mật cao vì người dùng có thể vô tình hoặc cố ý chia sẻ quyền quá mức, dẫn đến lỗ hổng như Trojan horse hoặc khai thác phần mềm lỗi.
* Quản lý tập trung trở nên phức tạp trong môi trường lớn, vì quyền hạn phân tán theo từng chủ sở hữu, khó theo dõi và kiểm soát toàn cục.

**Ví dụ:** Trong Linux, khi bạn tạo một tệp, bạn là chủ sở hữu và có thể dùng lệnh chmod để thay đổi quyền đọc, ghi, thực thi cho người khác. Tương tự, trong Windows, bạn có thể chỉnh sửa ACL qua giao diện Properties.

> Lưu ý quan trọng: DAC không ngăn chặn việc lan truyền quyền hạn, vì người dùng có quyền có thể chuyển giao cho người khác, làm tăng rủi ro thông tin nhạy cảm bị lộ. Trong tương tác với các mô hình khác, DAC có thể được mô phỏng trong RBAC bằng cách gán vai trò riêng cho từng đối tượng, nhưng điều này thường không hiệu quả do tốn tài nguyên.

# Mô Hình Phân Quyền Bắt Buộc (Mandatory Access Control - MAC)

- MAC đại diện cho cách tiếp cận nghiêm ngặt nhất, ưu tiên bảo mật cao bằng cách loại bỏ sự tùy ý của người dùng, thường được áp dụng trong môi trường nhạy cảm như quân sự hoặc chính phủ. Hãy nghĩ MAC như một hệ thống an ninh nơi mọi quy tắc được định sẵn bởi ban lãnh đạo, và không ai có thể thay đổi chúng một cách tùy tiện.

- **Định nghĩa:** MAC giới hạn quyền truy cập dựa trên quy tắc tập trung do quản trị viên cấp cao hoặc hệ thống thiết lập, không phụ thuộc vào chủ sở hữu đối tượng. Người dùng không thể tự thay đổi quyền hạn, đảm bảo tính toàn vẹn và bảo mật thông tin.

- **Cơ chế Phân quyền:**

+ **Gán Nhãn Bảo mật (Security Label):** **Mọi chủ thể (người dùng hoặc tiến trình) và đối tượng (tài nguyên) đều được gắn nhãn,** bao gồm **Mức độ Bảo mật** (ví dụ: Tuyệt Mật > Mật > Công khai) và **Danh mục Bảo mật** (ví dụ: Dự án A, Dự án B).
+ **Quy tắc:** Truy cập chỉ được cấp nếu **mức độ của chủ thể cao hơn hoặc bằng đối tượng**, và **phù hợp với danh mục**. Các quy tắc như Bell-LaPadula (cho bảo mật) hoặc Biba (cho toàn vẹn) được sử dụng để **ngăn chặn dòng thông tin không mong muốn**.

- **Ưu điểm:** Cung cấp mức bảo mật và tính toàn vẹn cao nhất, đảm bảo tuân thủ nghiêm ngặt, lý tưởng cho môi trường nơi thông tin nhạy cảm phải được bảo vệ khỏi rò rỉ.

- **Nhược điểm:**
+ Cứng nhắc và khó triển khai, đòi hỏi chi phí cao cho cấu hình ban đầu và quản lý nhãn.
+ Thiếu linh hoạt, có thể cản trở công việc hàng ngày trong môi trường không yêu cầu bảo mật cực cao.

**Ví dụ:** SELinux và AppArmor trên Linux thực thi MAC bằng cách sử dụng nhãn và quy tắc để kiểm soát truy cập, ngăn ứng dụng truy cập tài nguyên không được phép.

> **Lưu ý quan trọng:** MAC ngăn chặn việc chuyển giao quyền hạn, vì vậy nó chống lại các rủi ro như trong DAC, nhưng yêu cầu quản trị viên trung ương phải quản lý tất cả. Trong tương tác, MAC có thể được kết hợp với RBAC để thêm lớp bảo mật dựa trên vai trò, hoặc mô phỏng trong ABAC bằng thuộc tính nhãn.

# Mô Hình Phân Quyền Dựa Trên Vai Trò (Role-Based Access Control - RBAC)
- **RBAC** là mô hình hiện đại, cân bằng giữa linh hoạt và kiểm soát, được sử dụng rộng rãi trong doanh nghiệp để đơn giản hóa quản lý quyền hạn. Hãy hình dung RBAC như việc phân công vai trò trong một công ty: mỗi nhân viên được giao vai trò, và vai trò đó tự động mang theo các quyền cần thiết cho công việc.

- **Định nghĩa:** RBAC gán quyền không trực tiếp cho người dùng mà cho vai trò (roles). Người dùng được gán vai trò dựa trên trách nhiệm và trình độ, từ đó kế thừa quyền hạn. Điều này giúp tránh gán quyền cá nhân hóa phức tạp.

- **Cơ chế:**
+ **Quyền hạn (Permissions) được gán cho Vai trò** (ví dụ: Vai trò "Kế toán" có quyền ghi sổ cái).
+ **Vai trò được gán cho Người dùng** (ví dụ: Người dùng "An" được gán vai trò "Kế toán", tự động có quyền tương ứng).
+ **Hỗ trợ phân cấp vai trò** (hierarchy) và **ràng buộc như Separation of Duties (SOD)** để tránh xung đột lợi ích.

- **Ưu điểm:**
+ **Đơn giản hóa quản lý:** Khi người dùng thay đổi công việc, chỉ cần thay vai trò, không phải chỉnh sửa hàng loạt quyền.
+ **Dễ mở rộng** cho tổ chức lớn, và có thể mô phỏng DAC/MAC.

- **Nhược điểm:**
Có thể phức tạp khi thiết lập vai trò ban đầu, và không linh hoạt với các điều kiện động như thời gian hoặc vị trí.

**Ví dụ:** Trong **Active Directory (Windows)** hoặc **LDAP**, tạo nhóm vai trò và gán quyền cho nhóm, người dùng tham gia nhóm sẽ có quyền.
> **Lưu ý quan trọng:** RBAC hỗ trợ kế thừa vai trò (ví dụ: Quản lý kế thừa quyền từ Nhân viên), nhưng cần ràng buộc **SOD** để tránh lạm dụng. Nó tương tác tốt với DAC bằng cách cho phép vai trò tùy ý, và với MAC qua nhãn bảo mật trong vai trò.

# So Sánh Tổng Quan Các Mô Hình
Để hiểu rõ hơn, hãy so sánh các mô hình qua các khía cạnh chính, nhấn mạnh sự khác biệt và tương tác. **DAC ưu tiên linh hoạt với quyền quyết định ở chủ sở hữu**, **sử dụng DACL để kiểm soát,** phù hợp cho **môi trường cá nhân** nhưng **rủi ro cao do phân tán**. Ngược lại, **MAC tập trung quyền ở quản trị viên cấp cao**, dùng nhãn bảo mật để thực thi quy tắc nghiêm ngặt, lý tưởng cho **bảo mật cao nhưng cứng nhắc**. **RBAC cân bằng bằng cách dùng vai trò làm trung gian**, linh hoạt trung bình, **dễ quản lý cho doanh nghiệp lớn và có thể kết hợp DAC/MAC**.

- **Quyền quyết định: **
    + DAC ở chủ sở hữu; 
    + MAC ở quản trị viên/hệ thống
    + RBAC ở quản trị viên định nghĩa vai trò

- **Cơ chế chính: **
    + DAC dùng ACL
    + MAC dùng nhãn
    + RBAC dùng vai trò và quan hệ

- **Tính linh hoạt:** DAC cao; MAC thấp; RBAC trung bình đến cao.
**Ứng dụng:** DAC cho tệp hệ thống cơ bản; MAC cho quốc phòng; RBAC cho doanh nghiệp và ứng dụng web.
**Tương tác:** RBAC có thể mô phỏng DAC bằng vai trò tùy ý hoặc MAC bằng ràng buộc nhãn, làm cầu nối trong hệ thống lai.
