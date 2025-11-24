# - Lý Thuyết Ứng Dụng 12 Yếu Tố (The Twelve-Factor App)

## Tổng Quan

**12-Factor App** là một bộ nguyên tắc và phương pháp luận để xây dựng các ứng dụng phần mềm hiện đại. Được đúc kết từ kinh nghiệm thực tế của đội ngũ kỹ sư tại **Heroku**, bộ nguyên tắc này cung cấp một khuôn mẫu để tạo ra các ứng dụng có:

*   **Khả năng mở rộng (Scalable)** dễ dàng.
*   **Tính di động (Portable)** cao, dễ dàng triển khai trên các môi trường khác nhau.
*   **Khả năng bảo trì (Maintainable)** và phát triển liên tục.
*   **Độ tin cậy (Reliability)** và ổn định trong môi trường Production.
*   **Tự động hóa (Automation)** trong quy trình triển khai và vận hành.

Mặc dù sinh ra cho mô hình SaaS, các nguyên tắc này ngày nay áp dụng cho hầu hết mọi loại ứng dụng web hiện đại, đặc biệt là những ứng dụng chạy trên nền tảng điện toán đám mây và theo kiến trúc Microservices.

---

## Yếu tố đầu tiên:  Codebase
**Một codebase được quản lý bằng hệ thống quản lý phiên bản (VCS), nhiều lần triển khai.**

*   **Ý nghĩa:** Một ứng dụng chỉ có một kho mã nguồn duy nhất (một repository Git). Từ kho mã nguồn này, bạn có thể triển khai thành nhiều môi trường khác nhau (development, staging, production). Nếu có nhiều codebase, đó là một hệ thống phân tán (distributed system); nếu nhiều ứng dụng chia sẻ một codebase, đó là một kiến trúc monolith.
*   **Ví dụ:** Ứng dụng của bạn có một repo Git chính. Bạn có thể triển khai các branch khác nhau của repo này lên server staging và production. Tất cả đều xuất phát từ một nguồn duy nhất.
*   **Lợi ích:** Đảm bảo tính nhất quán, dễ dàng theo dõi lịch sử thay đổi và quản lý phiên bản.

---
## Yếu tố thứ 2: Dependencies
**Khai báo và cô lập một cách rõ ràng các phần phụ thuộc.**

*   **Ý nghĩa:** Ứng dụng phải khai báo rõ ràng tất cả các thư viện, công cụ bên ngoài mà nó cần thông qua một file manifest (ví dụ: `package.json`, `pom.xml`, `requirements.txt`). Tuyệt đối không ngầm định dựa vào sự có sẵn của các công cụ trong môi trường hệ thống.
*   **Ví dụ:** Trong Node.js, sử dụng `package.json` để liệt kê mọi thư viện và sử dụng `npm install` để cài đặt chúng một cách nhất quán. Sử dụng Docker để tạo một môi trường cô lập chứa tất cả dependencies.
*   **Lợi ích:** Loại bỏ hiện tượng "nhưng chạy trên máy tôi thì được", đảm bảo môi trường phát triển và production giống hệt nhau.

---
## Yếu tố thứ 3: Config
**Lưu trữ cấu hình trong môi trường (environment).**

*   **Ý nghĩa:** Mọi thứ có thể thay đổi giữa các môi trường triển khai (như database URL, API keys, secret keys, hostname,...) đều phải được tách ra khỏi code và lưu trữ trong **biến môi trường (environment variables)**.
*   **Ví dụ:** Thay vì hardcode `const dbUrl = 'localhost:5432';` trong code, hãy đọc giá trị từ biến môi trường: `const dbUrl = process.env.DATABASE_URL;`. Các giá trị này được inject vào khi khởi chạy ứng dụng (thông qua file `.env` ở local hoặc công cụ quản lý cấu hình trên cloud).
*   **Lợi ích:** Bảo mật thông tin nhạy cảm (không lưu secret trong code), dễ dàng thay đổi cấu hình giữa các môi trường mà không cần build lại code.

---
## Yếu tố thứ 4: Backing Services
**Coi các dịch vụ hỗ trợ như tài nguyên được kết nối.**

*   **Ý nghĩa:** Các dịch vụ bên ngoài mà ứng dụng sử dụng (database, queue, cache, SMTP service, API bên thứ 3) đều được coi là *tài nguyên*. Ứng dụng không nên quan tâm các dịch vụ này được đặt ở đâu mà chỉ cần kết nối đến chúng thông qua một **URL** hoặc thông tin kết nối được cấu hình (thường thông qua Config - Yếu tố III).
*   **Ví dụ:** Dịch vụ MySQL có thể chạy trên localhost, trên một server riêng, hoặc là một service managed trên AWS RDS. Ứng dụng chỉ cần kết nối đến địa chỉ được khai báo trong `DATABASE_URL`. Việc thay đổi từ database local sang RDS chỉ cần thay đổi giá trị URL này.
*   **Lợi ích:** Giảm sự phụ thuộc vào cơ sở hạ tầng, tăng tính linh hoạt và dễ dàng thay thế các service.

---
## Yếu tố thứ 5: Build, Release, Run
**Tách biệt rõ ràng các giai đoạn build và run.**

*   **Ý nghĩa:** Quy trình triển khai phải được tách thành 3 giai đoạn riêng biệt:
    1.  **Build:** Chuyển đổi code thành một gói thực thi (executable bundle). Đây là bước biên dịch code, cài đặt dependencies, tạo file thực thi.
    2.  **Release:** Kết hợp gói đã build với config cụ thể của môi trường để tạo ra một bản release. Mỗi bản release phải có một ID duy nhất (ví dụ: timestamp, version) và không thể thay đổi.
    3.  **Run:** Khởi chạy bản release trong môi trường thực thi.
*   **Ví dụ:** CI/CD pipeline (Jenkins, GitLab CI, GitHub Actions) thực hiện bước **build** tạo ra Docker image. Pipeline này lấy image đó và kết hợp với config từ Vault hoặc file env để **release** một container. Cuối cùng, container được **run** trên Kubernetes hoặc Docker Swarm.
*   **Lợi ích:** Cho phép rollback nhanh chóng về bản release trước đó, đảm bảo tính nhất quán tuyệt đối giữa các lần triển khai.

---
## Yếu tố thứ 6: Processes
**Thực thi ứng dụng như một hoặc nhiều tiến trình không trạng thái (stateless).**

*   **Ý nghĩa:** Ứng dụng chạy như một hoặc nhiều process. Các process này **không được lưu trữ trạng thái (state)** của phiên làm việc (session) hoặc dữ liệu người dùng trong bộ nhớ hoặc trên disk cục bộ. Mọi dữ liệu quan trọng phải được lưu vào một **backing service** có tính bền vững (persistent) như database hoặc distributed cache.
*   **Ví dụ:** Trong một hệ thống scale ngang, request tiếp theo của user có thể được xử lý bởi một process hoàn toàn khác. Nếu session được lưu trên RAM của server A, user tiếp tục sang server B sẽ bị mất session. Do đó, session phải được lưu vào Redis hoặc database.
*   **Lợi ích:** Cho phép mở rộng ứng dụng dễ dàng bằng cách thêm hoặc bớt các process, tăng độ tin cậy và khả năng chịu lỗi.

---
## Yếu tố thứ 7: Port Binding
**Xuất dịch vụ qua cổng (port binding).**

*   **Ý nghĩa:** Ứng dụng phải **tự chứa (self-contained)** và có khả năng tự khởi động một webserver và lắng nghe trên một **cổng (port)** cụ thể.
*   **Ví dụ:** Một ứng dụng Node.js sử dụng Express.js sẽ tự bind vào `port 3000`. Một ứng dụng Java Spring Boot nhúng Tomcat sẽ chạy trên `port 8080`. Ở môi trường production, một reverse proxy (như Nginx, Apache) có thể được đặt phía trước để route request vào cổng này.
*   **Lợi ích:** Ứng dụng trở nên độc lập với webserver, có thể chạy ở bất kỳ đâu và dễ dàng được deploy như một service độc lập trong kiến trúc microservices.

---
## Yếu tố thứ 8: Concurrency
**Mở rộng thông qua mô hình processes.**

*   **Ý nghĩa:** Khi cần mở rộng để xử lý nhiều tác vụ hơn, thay vì chạy một process "lớn" và "mạnh" duy nhất, hãy chạy **nhiều process nhỏ** của cùng một ứng dụng (scale out). Các loại công việc khác nhau (ví dụ: xử lý web request và xử lý job background) có thể được chia thành các **process type** khác nhau.
*   **Ví dụ:** Bạn có thể chạy nhiều instance (process) của ứng dụng web để xử lý nhi HTTP request hơn. Đồng thời, bạn có thể chạy riêng các process cho worker xử lý queue. Công cụ như PM2 (Node.js) hay Celery (Python) giúp quản lý điều này.
*   **Lợi ích:** Cho phép mở rộng quy mô một cách linh hoạt, tận dụng tài nguyên của các máy chủ nhỏ hơn, rẻ hơn.

---
## Yếu tố thứ 9: Disposability
**Tối đa hóa độ tin cậy với tính khởi động nhanh và shutdown một cách duyên dáng.**

*   **Ý nghĩa:** Các process phải có khả năng **khởi động nhanh** để có thể mở rộng nhanh chóng và phục hồi từ sự cố. Chúng cũng phải **tắt máy một cách duyên dáng (graceful shutdown)** khi nhận được tín hiệu (ví dụ: `SIGTERM`), hoàn thành các request đang xử lý và trả lại tài nguyên.
*   **Ví dụ:** Ứng dụng cần lắng nghe tín hiệu `SIGTERM` từ hệ điều hành. Khi nhận được tín hiệu (ví dụ lúc triển khai bản mới), nó ngừng nhận request mới, hoàn tất các request đang dở, đóng kết nối database, và sau đó mới tắt.
*   **Lợi ích:** Giảm thiểu thời gian downtime, cho phép triển khai liên tục và khôi phục sự cố nhanh chóng.

---
## Yếu tố thứ 10: Dev/Prod Parity
**Giữ cho các môi trường phát triển, staging và production càng giống nhau càng tốt.**

*   **Ý nghĩa:** Tránh sự khác biệt lớn giữa môi trường development và production về các mặt: **thời gian** (deploy thường xuyên), **con người** (dev cũng tham gia deploy), **công cụ** (dùng cùng OS, database, versions).
*   **Ví dụ:** Sử dụng Docker và Docker Compose để mô phỏng toàn bộ hệ thống (app, database, cache) trên local, giống hệt với cách chúng chạy trên production. Sử dụng cùng một hệ quản trị cơ sở dữ liệu (PostgreSQL cả local lẫn prod, thay vì SQLite trên local và PostgreSQL trên prod).
*   **Lợi ích:** Giảm thiểu các lỗi "chỉ xảy ra trên production", tăng tốc độ phát triển và debug.

---
## Yếu tố thứ 11: Logs
**Xem logs như một luồng sự kiện (stream).**

*   **Ý nghĩa:** Ứng dụng **không nên quan tâm** đến việc định dạng, lưu trữ hoặc xử lý file log. Nó chỉ cần ghi log ra **luồng stdout** (standard output). Môi trường thực thi hoặc các công cụ khác sẽ đảm nhận việc thu thập, tập trung, lưu trữ và phân tích các luồng sự kiện này.
*   **Ví dụ:** Ứng dụng chỉ cần `console.log()` hoặc ghi vào `stdout`. Trên môi trường production, một log router (như Fluentd, Logstash) sẽ thu thập log từ tất cả các process và đẩy đến một hệ thống tập trung như ELK Stack, Datadog hoặc Splunk.
*   **Lợi ích:** Giữ cho code ứng dụng gọn nhẹ, cho phép phân tích log tập trung và mạnh mẽ từ nhiều nguồn.

---
## Yếu tố thứ 12: Admin Processes
**Chạy các tác vụ quản trị/quản lý như một tiến trình một lần (one-off processes).**

*   **Ý nghĩa:** Các tác vụ chạy một lần (one-off) để bảo trì (database migration, chạy script console để sửa dữ liệu) phải được chạy trong **cùng một môi trường** và sử dụng **cùng một codebase và config** như các process thông thường của ứng dụng. Tránh chạy các tác vụ này bằng SSH vào server.
*   **Ví dụ:** Sử dụng công cụ để chạy migration trong cùng container environment. Ví dụ: `docker-compose run web python manage.py migrate` (Django) hoặc `kubectl run --rm -i migration --image=my-app --command -- python manage.py migrate` (Kubernetes).
*   **Lợi ích:** Đảm bảo tính nhất quán, tránh các vấn đề xảy ra do khác biệt môi trường khi chạy script quản trị.

---

## Kết Luận
> 12-Factor App không phải là một khuôn mẫu cứng nhắc mà là một **triết lý và tập hợp các best practices**. Việc áp dụng các nguyên tắc này sẽ giúp nhóm phát triển xây dựng các ứng dụng **mạnh mẽ, linh hoạt và dễ dàng vận hành** trong thời đại điện toán đám mây. Hãy bắt đầu bằng những yếu tố mang lại lợi ích lớn nhất cho dự án của bạn (thường là I, II, III, VI, XI) và dần dần áp dụng các yếu tố còn lại.

## Tài Liệu Tham Khảo
*   [The Twelve-Factor App (Trang chủ, tiếng Anh)](https://12factor.net/)
*   Heroku Developer Center