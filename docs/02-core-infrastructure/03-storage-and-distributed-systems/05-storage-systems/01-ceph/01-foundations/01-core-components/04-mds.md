# MDS - Metadata Server

## 1. MDS là gì

MDS (Metadata Server) là daemon quản lý metadata cho CephFS. Ceph docs và glossary đều nói rất rõ: MDS chỉ cần khi cluster chạy Ceph File System, còn RBD và Object Storage không dùng MDS. Vai trò cốt lõi của MDS là giữ và điều phối metadata của hệ thống tệp, nhờ đó các thao tác kiểu POSIX như ls, find, tra cứu thư mục, quyền truy cập hay trạng thái inode không tạo gánh nặng quá lớn lên toàn bộ cụm lưu trữ.

## 2. MDS nằm ở đâu trong kiến trúc CephFS

CephFS tách metadata và file data thành hai lớp riêng. Metadata được lưu trong một RADOS pool riêng và được phục vụ bởi một cụm MDS có thể mở rộng; trong khi đó, client CephFS vẫn đọc và ghi các khối dữ liệu file trực tiếp xuống RADOS. Điều này rất quan trọng vì nó cho thấy MDS không phải là “cổng trung gian cho mọi I/O dữ liệu”, mà là thành phần điều phối metadata và trạng thái truy cập file. Chính nhờ cách tách này, CephFS có thể tăng thông lượng metadata bằng cách mở rộng MDS, trong khi luồng dữ liệu file vẫn tận dụng khả năng mở rộng của RADOS/OSD.
```
Minh họa vai trò của MDS trong CephFS
Ứng dụng / Client CephFS
        ↓
   Tra cứu metadata qua MDS
        ↓
Xác định vị trí và quyền truy cập file
        ↓
Client đọc/ghi dữ liệu file trực tiếp vào RADOS
```
## 3. MDS quản lý metadata như thế nào

- MDS đóng vai trò là nơi có thẩm quyền đối với trạng thái của bộ nhớ đệm metadata phân tán giữa client CephFS và chính các MDS. Ceph docs mô tả rằng MDS phối hợp một bộ nhớ đệm dùng chung để giảm độ trễ truy cập metadata và cho phép client thay đổi metadata một cách nhất quán, ví dụ như đổi quyền, đổi tên hoặc tạo đối tượng thư mục/tệp. Để làm được điều này, MDS phát hành capabilities và directory entry leases nhằm chỉ ra client được phép giữ phần metadata nào trong bộ nhớ đệm và được phép thực hiện loại thao tác nào.

- Một điểm rất quan trọng là MDS không lưu trạng thái metadata cục bộ như một nguồn chân lý riêng. Các thay đổi metadata được MDS gom lại thành các lần ghi hiệu quả vào journal trên RADOS, và metadata cuối cùng vẫn thuộc về hệ lưu trữ phân tán của Ceph chứ không bị “kẹt” trong máy cục bộ của MDS. Đây là lý do CephFS có thể giữ được tính nhất quán của metadata trong khi vẫn cho phép nhiều client cùng hoạt động trên một không gian tệp chung.

> Keynote: MDS không phải là “máy chủ trung gian cho mọi I/O file”, mà là máy chủ metadata cho CephFS. Điểm phải nhớ là CephFS vẫn để dữ liệu file đi xuống RADOS, còn MDS chủ yếu xử lý tên file, thư mục, quyền và trạng thái metadata. Khi hiểu đúng điều này, bạn sẽ thấy CephFS không phải hệ thống file truyền thống có một máy chủ trung gian ôm hết dữ liệu, mà là file interface đặt trên object backend, với MDS chỉ gánh phần metadata để hành vi kiểu POSIX còn khả thi.

## 4. MDS và khả năng mở rộng metadata

Một cụm CephFS có thể dùng resizable cluster of Metadata Servers, tức là cụm MDS có thể mở rộng để hỗ trợ tải metadata cao hơn. Điều này đặc biệt có ý nghĩa với workload có rất nhiều thao tác metadata như duyệt cây thư mục lớn, tạo/xóa file hàng loạt, hoặc các ứng dụng có cường độ gọi stat, readdir, lookup cao. Ceph docs nhấn mạnh rằng chính phần metadata mới là nơi MDS cần tập trung xử lý; còn dữ liệu file vẫn đi trực tiếp tới RADOS, nên mở rộng MDS chủ yếu giúp tăng năng lực xử lý metadata chứ không thay vai trò của OSD trong luồng dữ liệu file.

## 5. MDS cache và vì sao nó quan trọng

MDS sử dụng bộ nhớ đệm metadata để tăng tốc độ truy cập và phối hợp trạng thái với các client CephFS. Ceph docs về MDS Cache Configuration cho biết MDS điều phối bộ nhớ đệm phân tán giữa tất cả MDS và client CephFS; bộ nhớ đệm này giúp giảm độ trễ truy cập metadata và cho phép client thay đổi metadata một cách nhất quán. Khi bộ nhớ đệm quá lớn, MDS sẽ thu hồi dần trạng thái mà client đang giữ để các mục metadata không còn bị ghim có thể bị loại khỏi bộ nhớ đệm. Điều này cho thấy MDS không chỉ là “metadata server” theo nghĩa tĩnh, mà là thành phần actively quản lý bộ nhớ đệm metadata phân tán.

## 6. Khi nào MDS thực sự cần thiết

MDS là daemon bắt buộc khi bạn chạy CephFS. Ceph docs nói rõ cần có MDS để chạy Ceph File System clients, và troubleshooting guide của CephFS cũng cho thấy nếu MDS chậm hoặc bị lỗi, client có thể gặp lỗi mount hay truy cập file system bất thường; khi đó việc đầu tiên cần kiểm tra là có ít nhất một MDS đang hoạt động hay không. Điều này củng cố đúng phạm vi của MDS: nó không tham gia các giao diện block hay object thông thường, nhưng với CephFS thì nó là thành phần trọng yếu.

## 7. Những hiểu lầm phổ biến về MDS

- Hiểu lầm phổ biến nhất là nghĩ rằng MDS xử lý cả metadata lẫn dữ liệu file. Điều này sai. Trong CephFS, MDS xử lý metadata và điều phối trạng thái truy cập; còn client vẫn đọc và ghi file data trực tiếp xuống RADOS. Nếu không tách ranh giới này, rất dễ hình dung sai CephFS như một hệ thống file có máy chủ trung gian đứng chắn toàn bộ I/O.

- Hiểu lầm thứ hai là cho rằng mọi cụm Ceph đều cần MDS. Thực tế, MDS chỉ cần cho CephFS. Các workload dùng RBD hoặc Object Gateway không cần MDS để hoạt động. Đây là một điểm rất cơ bản nhưng hay bị nhầm khi người học mới thấy MDS nằm cạnh MON, MGR và OSD trong sơ đồ kiến trúc chung.

> MDS là thành phần chuyên trách cho metadata của CephFS. Nó giúp CephFS có hành vi giống một hệ thống file POSIX bằng cách quản lý metadata, điều phối bộ nhớ đệm metadata phân tán, cấp quyền cache qua capabilities và đưa các thay đổi metadata vào journal trên RADOS. MDS rất quan trọng với CephFS, nhưng không tham gia các giao diện block và object thông thường. Vì vậy, khi học Ceph ở mức tổng thể, nên xem MDS là thành phần chuyên biệt cho file system, chứ không phải lớp lõi chung cho mọi kiểu truy cập dữ liệu.