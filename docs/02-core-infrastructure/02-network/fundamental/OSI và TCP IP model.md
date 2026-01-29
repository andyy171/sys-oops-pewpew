# **Mô hình OSI và TCP/IP**

## **Mô hình tham chiểu OSI**
### **Các khái niệm cơ bản:**

Mô hình OSI (Open Systems Interconnection) là một mô hình tham chiếu để mô tả cách mà các hệ thống mạng hoạt động. Nó phân chia quá trình giao tiếp mạng thành 7 tầng độc lập nhằm tăng tính tương thích và dễ quản lý. 

![image](https://user-images.githubusercontent.com/95491130/180395447-e8d22b82-6448-462b-96ae-3274d068799d.png)

Osi mô tả chức năng theo dạng phân tầng. Mỗi tầng có 1 vai trò riêng, mỗi vai trò có 1 tập chức năng chuyên biệt. Mỗi tầng chỉ tương tác với tầng trên và tầng dưới. Tầng applycation tương tác với user. Tầng physical tương tác với đường truyền vật lý.

![](./images/osi-model.avif)

### **Vai trò nhiệm vụ của từng tầng trong mô hình OSI:**
- **Tầng Application**: giao tiếp trực tiếp với user thông qua giao diện. Cung cấp các chức năng truyền thông đáp ứng yêu cầu của user.
- **Tầng Presentation**: mã hóa, định dạng các bản tin dữ liệu cho phù hợp.
- **Tầng Session:** quản lý các phiên truyền thông giữa 2
  máy tính từ khi bắt đầu diễn ra cho đến khi kết thúc
- **Tầng Transport**: điều khiển việc giao vận dữ liệu giữa các ứng dụng, đảm bảo dữ liệu chính xác, không bị mất mát và không trùng lặp (end-to-end)**.**
- **Tầng Network**: quy định địa chỉ của máy tính trong mạng, tìm đường đi và chuyển tiếp dữ liệu từ máy gửi đến máy nhận.
- **Tầng Data Link**: điều khiển việc truyền dữ liệu trên
  đường truyền vật lý giữa 2 máy tính, đảm bảo chính xác,
  không mất mát.
- **Tầng Physical**: Kết nối với đường truyền, biến đổi dữ
  liệu thành tín hiệu vật lý (xung điện, xung quang, sóng
  điện từ), thu và phát tín hiệu.

### **Tác dụng của mô hình:** 
- OSI cung cấp điểm tham chiếu để so sánh và hiểu về chức** năng của các thành phần trong hệ thống mạng
- Một tiêu chuẩn về mạng, một thiết bị phần cứng hoặc phần mềm thuộc tầng nào thì thực hiện chức năng của tầng đó.
  - Thành phần hoạt động tại tầng dưới: low-level
  - Thành phần hoạt động tại tầng giữa: Mid-level
  - Thành phần hoạt động tại tầng trên: High-level
## **Mô hình TCP/IP**
### **Khái niệm chung** 
- TCP/IP(Transmission Control Protocol/ Internet Protocol): Giao thức điều khiển truyền nhận/ Giao thức liên mạng), là một bộ giao thức trao đổi thông tin được sử dụng để truyền tải và kết nối các thiết bị trong mạng Internet. TCP/IP được phát triển để mạng được tin cậy hơn cùng với khả năng phục hồi tự động.

![image](https://user-images.githubusercontent.com/95491130/180395560-1aa7075d-9a60-4476-a073-c76f6bb5b961.png)

### **Vai trò của các tầng trong mô hình:**

![](./images/tcpip.avif)

- Tầng **Applycation:** đảm nhận vai trò giao tiếp dữ liệu giữa 2 máy khác nhau thông qua các dịch vụ mạng.
- Tầng **Transport:** xử lý vấn đề giao tiếp giữa các máy chủ trong cùng 1 hệ thống mạng hoặc hoặc các mạng khác nhau được kết nối qua bộ định tuyến. ( 2 giao thức chính trong tầng này là TCP và UDP)
- Tầng **Internet:** xử lý quá trình truyền gói tin trên mạng. Các giao thức gồm: IP, ICMP, IGMP. 
- Tầng **network Access:** bao gồm các thiệt bị mạng và các chương trình cung cấp các thông tin cần thiết cho hoạt động, truy nhập đường truyền vật lý qua các thiết bị mạng đó.

### **Cách thức hoạt động:**

- TCP/IP là sự kết hợp giữa 2 giao thức. Trong đó [IP](https://www.totolink.vn/article/74-ip-la-gi-cach-xac-dinh-dia-chi-ip-tren-may-tinh.html) (Giao thức liên mạng) cho phép các gói tin được gửi đến đích đã định sẵn, bằng cách thêm các thông tin dẫn đường vào các gói tin để các gói tin được đến đúng đích đã định sẵn ban đầu. Và giao thức TCP (Giao thức truyền vận) đóng vai trò kiểm tra và đảm bảo sự an toàn cho mỗi gói tin khi đi qua mỗi trạm. 

## **Mối tương quan giữa 2 mô hình.**
- Điểm chung: đều là mô hình phân tầng dùng để truyền dữ liệu giữa các đối tương trên hạ tầng hệ thống mạng có chung tầm netword và transport.
- Điểm khác nhau

|Tiêu chí|OSI|TCP/IP|
| :- | :- | :- |
|Sự tin cậy|Mô hình cũ nên ít được sử dụng|Là giao thức chuẩn mới hơn |
|Phương pháp tiếp cận|Theo chiều dọc|Theo chiều ngang|
|Thiết kế|Phát triển mô hình sau đó phát triển giao thức|Phát triển giao thức sau đó phát triển mô hình|
|Số tầng|7|4|
|Tính phụ thuộc|Giao thức độc lập|Phụ thuộc vào giao thức|


