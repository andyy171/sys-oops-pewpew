# Tổng quan về Cloud Computing ( Điện toán đám mây)
- Cloud Computing là một mô hình cho phép truy cập mạng mọi lúc, mọi nơi, thuận tiện và theo nhu cầu vào một kho tài nguyên điện toán chung có thể cấu hình được (ví dụ: mạng, máy chủ, lưu trữ, ứng dụng và dịch vụ). Những tài nguyên này có thể được thiết lập nhanh chóng và giải phóng với tối thiểu nỗ lực quản lý hoặc sự tương tác với nhà cung cấp dịch vụ.
- Các đặc điểm chính :
    - On-demand self-service (Tự phục vụ theo nhu cầu): Người dùng có thể tự thiết lập tài nguyên (như giờ chạy server, dung lượng lưu trữ) mà không cần gọi điện nhờ nhân viên kỹ thuật của nhà cung cấp can thiệp.
    - Broad network access (Truy cập mạng rộng rãi): Tài nguyên phải luôn sẵn sàng thông qua mạng Internet và sử dụng được trên nhiều thiết bị khác nhau (điện thoại, laptop, máy tính bảng).
    - Resource pooling (Dùng chung tài nguyên): Tài nguyên của nhà cung cấp được gom lại để phục vụ nhiều người dùng khác nhau. Bạn không biết chính xác dữ liệu mình nằm ở cái máy chủ vật lý nào, nhưng nó vẫn luôn ở đó cho bạn.
    - Rapid elasticity (Khả năng co giãn nhanh chóng): Có thể tăng hoặc giảm tài nguyên ngay lập tức tùy theo nhu cầu. Hệ thống có vẻ như "vô hạn" đối với người dùng.
    - Measured service (Dịch vụ định lượng): Việc sử dụng tài nguyên được giám sát, kiểm soát và báo cáo minh bạch. Bạn dùng bao nhiêu, hệ thống đo lường và tính tiền bấy nhiêu (giống như hóa đơn điện).

## Các mô hình dịch vụ
1. IaaS 
- Cung cấp cơ sở hạ tầng mạng, lưu trữ và máy chủ ảo. Khách hàng có toàn quyền kiểm soát và quản lý hệ điều hành, ứng dụng và dữ liệu của họ.

2. PaaS 
- Cung cấp một nền tảng để phát triển, chạy và quản lý ứng dụng mà không cần quản lý cơ sở hạ tầng.
> Khách hàng sử dụng nền tàng để có thể lập trình và chạy ứng dụng, nhà cung cấp không chỉ quản lý mã nguồn mà còn cả dữ liệu của ứng dụng 

3. SaaS 
- Cung cấp các ứng dụng phần mềm sẵn có thông qua internet, chẳng hạn như email hoặc CRM, cho phép người dùng truy cập và sử dụng mà không cần cài đặt hay quản lý. 
> Khách hàng chỉ sử dụng phần mềm , không cần quản lý kỹ thuật

## Các mô hình triển khai 

1. Public Cloud 
- Dịch vụ đám mây được cung cấp bởi bên thứ ba và chia sẻ cho nhiều người dùng qua internet.

2. Private Cloud 
- Dịch vụ đám mây dành riêng cho một tổ chức và được quản lý nội bộ hoặc bởi bên thứ ba.


3. Hybird Cloud 
- Kết hợp giữa đám mây công cộng và đám mây riêng, cho phép dữ liệu và ứng dụng được chia sẻ giữa chúng.


4. Community Cloud
- Hạ tầng đám mây được chia sẻ giữa nhiều tổ chức có cùng mối quan tâm chung như yêu cầu về bảo mật, tuân thủ, hoặc lĩnh vực hoạt động

# Key domains
## Compute 
- Compute là thành phần đại diện cho năng lực xử lý của toàn bộ hệ thống, đóng vai trò như bộ não thực hiện các phép tính và chạy logic của ứng dụng. Trong môi trường đám mây, Compute không đơn thuần là một chiếc máy chủ vật lý mà là một tập hợp các tài nguyên được ảo hóa linh hoạt. Khi bạn khởi tạo một thực thể tính toán, nhà cung cấp sẽ sử dụng công nghệ ảo hóa (Hypervisor) để phân tách một phần tài nguyên CPU và RAM từ các cụm máy chủ vật lý khổng lồ.


## Storage


## Database 


## Networking

