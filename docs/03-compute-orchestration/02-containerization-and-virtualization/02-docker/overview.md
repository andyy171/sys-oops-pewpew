# Tổng quan về Docker 
## Tại sao lại cần Docker 

- Vấn đề cốt lõi mà Docker giải quyết là sự phức tạp và xung đột khi phải chạy nhiều ứng dụng với các yêu cầu thư viện, phiên bản phần mềm, hoặc cấu hình hệ điều hành khác nhau trên cùng một máy chủ. Trước đây, việc này giống như việc cố gắng lắp nhiều bộ phận từ những cỗ máy khác nhau vào một khung duy nhất – chúng thường xung đột và không tương thích. Docker đã thay đổi hoàn toàn điều đó bằng công nghệ container. 
- Docker cho phép chúng ta đóng gói ứng dụng cùng với toàn bộ môi trường chạy ở tầng user-space của Linux, bao gồm runtime, thư viện và các công cụ cần thiết, thành một container. Container không chứa hệ điều hành hoàn chỉnh và không mang theo Linux kernel, mà luôn sử dụng kernel Linux do hệ thống bên dưới cung cấp. Trên máy Linux, container chạy trực tiếp trên kernel của host; còn trên macOS và Windows, Docker Desktop tạo sẵn một máy ảo Linux nhỏ để cung cấp kernel này, và các container được chạy bên trong máy ảo đó. Nhờ vậy, cùng một container Linux có thể chạy nhất quán trên các hệ điều hành khác nhau mà không phụ thuộc vào cấu hình môi trường của từng máy. Cách tiếp cận này loại bỏ sự khác biệt giữa môi trường phát triển, kiểm thử và production, đồng thời tối ưu tài nguyên và đơn giản hóa việc triển khai, khi toàn bộ môi trường ứng dụng có thể được khởi chạy chỉ bằng một lệnh `docker run`


## Cách Docker hoạt động 
- Docker hoạt động dựa trên nguyên lý **chia sẻ nhân hệ điều hành (kernel)** của máy chủ vật lý. Khác với máy ảo (Virtual Machine) phải chạy một hệ điều hành hoàn chỉnh bên trong, gây nặng nề và tốn tài nguyên, một **container** của Docker không chứa cả một hệ điều hành. Thay vào đó, nó chỉ **đóng gói ứng dụng, các thư viện và dependencies cần thiết để ứng dụng đó chạy**. Toàn bộ container này sẽ chia sẻ và giao tiếp trực tiếp với kernel của hệ điều hành host (ví dụ: Linux) thông qua Docker Engine. Điều này giải thích tại sao Docker lại nhẹ và khởi chạy nhanh đến vậy.

- Tuy nhiên, chính vì phụ thuộc vào kernel của host nên có một hạn chế: bạn không thể chạy một container được thiết kế cho kernel Windows trên một host đang chạy kernel Linux, và ngược lại. Đây là lý do tại sao bạn cần Docker trên Windows Server để chạy các container Windows. Tóm lại, Docker hoạt động như một lớp trung gian thông minh, giúp quản lý và phân lập các ứng dụng để chúng chạy độc lập trong khi vẫn tận dụng chung một nền tảng hệ điều hành cơ bản, từ đó đạt được hiệu quả tối ưu cả về tính nhất quán lẫn tài nguyên.

## Containers
Về bản chất, một **container** là một môi trường runtime nhẹ và độc lập, nơi một ứng dụng cụ thể được chạy. Bạn có thể hình dung nó như một căn phòng kín được trang bị đầy đủ nội thất và tiện nghi riêng (các thư viện, biến môi trường, file cấu hình) bên trong một tòa nhà lớn (máy chủ). Điều quan trọng là mọi container đều chia sẻ chung nền móng và hệ thống hạ tầng của tòa nhà (chính là kernel của hệ điều hành host), giúp chúng tiết kiệm tài nguyên hơn rất nhiều so với việc xây cả một tòa nhà riêng cho mỗi ứng dụng.

### Containers vs VMs
Sự khác biệt cốt lõi nằm ở kiến trúc. Một Máy ảo (VM) bao gồm cả một hệ điều hành khách (Guest OS) hoàn chỉnh chạy trên một lớp phần mềm gọi là hypervisor. Việc chạy nhiều bản sao OS như vậy rất tốn RAM, CPU và dung lượng lưu trữ. Trong khi đó, **container** không cần một OS riêng nào cả; chúng gói ứng dụng và các thành phần phụ thuộc lại và chia sẻ trực tiếp kernel của host, giúp chúng khởi chạy trong vài giây, nhẹ hơn hàng chục lần và hiệu suất gần như ngang bằng với việc chạy ứng dụng trực tiếp trên host.

### Containers vs Images
`image` là một khuôn mẫu (template) hoặc một bản thiết kế read-only (chỉ đọc) chứa tất cả các hướng dẫn để tạo ra một container. Nó bao gồm hệ điều hành thu gọn, mã ứng dụng, thư viện và các dependencies. Còn container là một thực thể (instance) đang chạy được khởi tạo từ image đó. Một image có thể dùng để tạo ra nhiều container giống hệt nhau. Khi container chạy, Docker tạo một lớp writable (có thể ghi) mỏng phía trên image để lưu mọi thay đổi trong phiên làm việc, trong khi bản thân image gốc vẫn luôn không thay đổi.

## Tại sao Docker quan trọng
Docker đóng vai trò như một chất xúc tác, phá vỡ rào cản giữa Development (phát triển) và Operations (vận hành) - hay còn gọi là DevOps. Sức mạnh của nó nằm ở khả năng chuẩn hóa môi trường chạy ứng dụng. Đối với developer, Docker loại bỏ hoàn toàn bài toán "nhưng trên máy tôi chạy được" bằng cách cho phép đóng gói ứng dụng cùng mọi thứ nó cần vào một image duy nhất. Image này trở thành một đơn vị thống nhất, có thể chạy y hệt trên bất kỳ máy tính nào có cài Docker, từ laptop của developer đến máy chủ testing, staging và production. Điều này tạo nên một pipeline CI/CD (Tích hợp liên tục/Triển khai liên tục) trơn tru và đáng tin cậy, where code is built into a container image once and then promoted through various environments with absolute consistency.

Trong kiến trúc hệ thống, Docker là nền tảng lý tưởng cho kiến trúc Microservices, nơi một ứng dụng lớn được tách thành nhiều dịch vụ nhỏ, độc lập. Mỗi microservice có thể được đóng gói và chạy trong container riêng của nó, cho phép các team phát triển độc lập, scale từng phần dịch vụ một cách linh hoạt và dễ dàng cập nhật hoặc rollback từng service mà không ảnh hưởng đến toàn bộ hệ thống. Ngoài ra, tính nhẹ và khởi động nhanh của container giúp tối ưu hóa tài nguyên server một cách tối đa, cho phép chạy mật độ service dày đặc hơn nhiều so với máy ảo truyền thống, từ đó tiết kiệm chi phí hạ tầng đáng kể. Tóm lại, Docker không chỉ là một công cụ đóng gói, mà là một công nghệ mang tính nền tảng giúp tự động hóa, đơn giản hóa và tăng tốc toàn bộ vòng đời phát triển phần mềm.


## Cài đặt Docker 
### MacOS
Tải bộ cài [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/) for MAC , chạy install như thường 

### Windows 

Đối với Windows ngoài việc tải bộ cài thì còn phải kích hoạt Hyper-V ( Ở chế độ này không cài được VirtualBox nữa )

- Lệnh PowerShell kích hoạt : 
```shell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

```

- Hoặc đơn giản có thể kích hoạt thông qua Windows features : App and Features => Programs and Features => Turn Windows Features on or off => Tích chọn Hyper-V



