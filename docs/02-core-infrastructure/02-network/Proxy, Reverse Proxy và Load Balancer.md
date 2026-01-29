# Proxy – “Người trung gian” bảo vệ người dùng

- Proxy được ví như trợ lý cá nhân giúp bạn đặt bàn ăn mà không trực tiếp nói chuyện với nhân viên nhà hàng.
Trong thế giới mạng, proxy là lớp trung gian giữa mạng nội bộ (private network) và Internet (public network).

- Proxy nhận yêu cầu từ máy tính người dùng, gửi chúng ra Internet, sau đó lọc và kiểm tra phản hồi trước khi trả lại kết quả. Điều này giúp bảo vệ máy người dùng khỏi mã độc, website độc hại hay nội dung không mong muốn.

+ Trong môi trường doanh nghiệp, tất cả lưu lượng từ máy nhân viên đều được buộc đi qua proxy.
+ Proxy cho phép quản trị viên kiểm soát và giám sát hoạt động Internet của nhân viên, đồng thời có thể chặn truy cập đến các website cụ thể.

- Một chức năng quan trọng khác là caching. Khi một nhân viên truy cập một video hướng dẫn, proxy sẽ lưu bản sao cục bộ. Những người khác xem cùng video sau đó sẽ được phục vụ từ cache thay vì tải lại từ Internet, giúp tiết kiệm băng thông và tăng tốc độ truy cập.

Proxy loại này còn gọi là **forward proxy** – nằm ở phía người dùng, bảo vệ mạng nội bộ.

## Reverse Proxy – “Lễ tân” của máy chủ

- Reverse proxy được ví như lễ tân nhà hàng – người tiếp đón khách và dẫn họ đến bàn phù hợp thay vì để họ tự đi tìm chỗ ngồi.

+ Reverse proxy hoạt động ở phía máy chủ, tiếp nhận yêu cầu từ Internet và phân phối đến các máy chủ nội bộ thích hợp.
Chức năng phân phối này gọi là load balancing, giúp các yêu cầu được chia đều, tránh tình trạng máy chủ quá tải.

+ Tuy nhiên, reverse proxy không chỉ làm nhiệm vụ cân bằng tải.
Nó còn thực hiện các vai trò khác tương tự forward proxy như:

+ Bảo mật: che giấu toàn bộ hệ thống máy chủ thật, ngăn truy cập trực tiếp từ Internet.

+ Mã hóa và kiểm tra lưu lượng: hỗ trợ SSL/TLS termination, đảm bảo truyền thông an toàn.

+ Caching phản hồi để tăng tốc độ truy cập.

+ Ghi log phục vụ việc giám sát và xử lý sự cố.

Một ví dụ phổ biến của reverse proxy là NGINX, có thể dùng làm web server, reverse proxy và load balancer cùng lúc.

# Load Balancer – “Người điều phối khách”

Load balancer là tính năng của reverse proxy, chịu trách nhiệm phân phối yêu cầu đồng đều đến các máy chủ.
Khi ứng dụng chạy trên nhiều máy chủ, load balancer đảm bảo không có máy nào bị quá tải trong khi máy khác rảnh rỗi.

Tuy nhiên, video cũng giải thích rằng trong thực tế hiện đại, load balancer của cloud (AWS, Azure, GCP, v.v.) và reverse proxy nội bộ thường hoạt động song song.

Cloud load balancer nằm bên ngoài hệ thống, chịu trách nhiệm phân phối lưu lượng từ Internet vào cụm máy chủ, còn reverse proxy bên trong xử lý điều phối chi tiết và logic hơn giữa các dịch vụ nội bộ.

Lớp bảo vệ kép này giúp hệ thống vừa an toàn hơn, vừa mở rộng linh hoạt hơn.

Reverse proxy có thể định tuyến thông minh dựa trên header, cookie, session hoặc đường dẫn (URL).
Ví dụ, mọi yêu cầu từ cùng một người dùng luôn được gửi đến cùng một web server để giữ phiên làm việc ổn định, hoặc trong hệ thống microservices, proxy có thể định tuyến đến đúng microservice dựa trên đường dẫn request.

# Mô hình kết hợp trong thực tế

- Cách bố trí phổ biến trong môi trường Kubernetes là sử dụng Ingress Controller – một loại reverse proxy chuyên dụng để định tuyến nội bộ giữa các dịch vụ.
Bên ngoài cụm Kubernetes là cloud load balancer, đảm nhận nhiệm vụ nhận và lọc lưu lượng Internet trước khi vào cụm.

- Điều này tạo thành kiến trúc nhiều lớp:
Cloud Load Balancer → Ingress Controller (Reverse Proxy) → Microservices

- Proxy trong ứng dụng Node.js và Java

Khi chạy ứng dụng Node.js hoặc Java, ta thường thấy một “server” tự khởi động.
Đây không phải reverse proxy hoàn chỉnh mà chỉ là HTTP server nhẹ, ví dụ như Express.js trong Node.js.

Express.js là framework để xây dựng web API và xử lý logic động, nhưng không được tối ưu cho phục vụ file tĩnh hay cân bằng tải.
Vì vậy trong môi trường production, người ta thường đặt NGINX phía trước Express.js.

NGINX đảm nhận vai trò reverse proxy, phục vụ file tĩnh, mã hóa SSL, cân bằng tải và bảo mật.
Còn Express.js chỉ tập trung xử lý nội dung động (logic ứng dụng, API, session…).

# Tổng kết

Proxy, reverse proxy và load balancer là ba lớp bảo vệ và điều phối quan trọng trong kiến trúc web hiện đại.
Forward proxy bảo vệ người dùng nội bộ, reverse proxy bảo vệ và tối ưu máy chủ, còn load balancer giữ cho toàn hệ thống hoạt động ổn định, phân phối hợp lý và mở rộng linh hoạt.

Sự kết hợp của chúng – đặc biệt là giữa cloud load balancer và reverse proxy nội bộ – là nền tảng cho các hệ thống lớn, an toàn và hiệu năng cao như các website toàn cầu vẫn vận hành mỗi ngày.