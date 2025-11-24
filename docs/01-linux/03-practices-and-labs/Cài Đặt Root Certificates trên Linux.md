# Mục lục

- [Cài Đặt Root Certificates trên Hệ Thống Dùng `update-ca-certificates`](#cài-đặt-root-certificates-trên-hệ-thống-dùng-update-ca-certificates)
- [Cài Đặt Root Certificates trên Hệ Thống Dùng `update-ca-trust`](#cài-đặt-root-certificates-trên-hệ-thống-dùng-update-ca-trust)
- [Cài Đặt Root Certificates trên Trình duyệt Chrome (Linux)](#cài-đặt-root-certificates-trên-trình-duyệt-chrome-linux)

>Việc cài đặt Root Certificates (Chứng chỉ gốc) là cần thiết để hệ thống của bạn tin tưởng các chứng chỉ SSL/TLS được cấp bởi CA (Certificate Authority) đó, đặc biệt là các CA nội bộ (corporate CA) hoặc CA bên thứ ba không có trong danh sách mặc định.

# Cài Đặt Root Certificates trên Hệ Thống Dùng `update-ca-certificates`

Nhóm hệ điều hành này bao gồm SUSE Linux Enterprise Server (SLES) và Debian/Ubuntu cùng các phiên bản phái sinh.

**Các bước cài đặt:**
1. Chuẩn bị File Certificate:

- Chứng chỉ phải ở định dạng **PEM (Privacy-Enhanced Mail).**
![](/01-linux/images/user-and-group-management/Linux_Certs003.png)
- **Đối với SLES:** File có thể có đuôi mở rộng bất kỳ, ví dụ: **.pem, .crt, .cert.**

- **Đối với Ubuntu:** File bắt buộc phải có đuôi mở rộng là **.crt.**

2. Sao chép Certificate vào Thư mục Phù hợp:

- **Đối với SLES (SUSE Linux Enterprise Server):**

```bash
sudo cp <ten_certificate>.pem /etc/pki/trust/anchors/
```
- **Đối với Ubuntu / Debian:**

```bash
sudo cp <ten_certificate>.crt /usr/local/share/ca-certificates/
```

3. Cập nhật Kho Chứng chỉ Tin cậy (Trusted Certificate Store):
![](/01-linux/images/user-and-group-management/Linux_Certs004.png)
- Chạy lệnh để hệ thống gom các chứng chỉ mới vào danh sách tin cậy chung (`/etc/ssl/certs/ca-certificates.crt`).

- Lệnh này hoạt động cho cả SLES và Ubuntu/Debian:

```bash
sudo update-ca-certificates
```
*Mô tả:* Lệnh này sẽ tạo/cập nhật danh sách tổng hợp các chứng chỉ tin cậy.

4. Kiểm tra và Xác minh:

- Kiểm tra xem chứng chỉ đã được thêm vào thư mục liên kết (symlink directory) chưa:

```bash
ls /etc/ssl/certs | grep <ten_certificate_hoac_keyword>
```
![](/01-linux/images/user-and-group-management/Linux_Certs006.png)
- Xác minh bằng cách kết nối tới một máy chủ sử dụng chứng chỉ được cấp bởi CA vừa cài đặt, sử dụng curl:

```bash
curl --verbose https://<webserver_cua_ban>
```
![](/01-linux/images/user-and-group-management/Linux_Certs007.png)

- Gỡ cài đặt (Deinstall):
Xóa file chứng chỉ đã sao chép ở Bước 2.
![](/01-linux/images/user-and-group-management/Linux_Certs015.png)
Chạy lại lệnh cập nhật:

```bash
sudo update-ca-certificates
```
![](/01-linux/images/user-and-group-management/Linux_Certs017.png)


# Cài Đặt Root Certificates trên Hệ Thống Dùng update-ca-trust
Nhóm hệ điều hành này bao gồm **Red Hat Linux Enterprise (RHEL)**, **Oracle Linux**, **CentOS**, **Fedora**cùng các phiên bản phái sinh (hiện đại).

1. **Sao chép Certificate vào Thư mục Phù hợp:**

- Chứng chỉ phải ở định dạng PEM hoặc DER.

- Sao chép chứng chỉ vào thư mục anchors:

```bash
sudo cp <ten_certificate> /etc/pki/ca-trust/source/anchors/
```

![](/01-linux/images/user-and-group-management/rhel_root_ca_001.png)
>Lưu ý: Nếu chứng chỉ của bạn ở định dạng "**extended BEGIN TRUSTED**" (có chứa metadata bổ sung), hãy đặt nó vào thư mục /etc/pki/ca-trust/source/ thay vì thư mục anchors/.

2. **Cập nhật Kho Chứng chỉ Tin cậy (Trusted Certificate Store):**

Chạy lệnh để hệ thống xử lý và cập nhật kho tin cậy:
```bash
sudo update-ca-trust
```
![](/01-linux/images/user-and-group-management/rhel_root_ca_002.png)
3. **Kiểm tra và Xác minh (Tùy chọn):**

- Sử dụng công cụ trust để kiểm tra chứng chỉ đã được coi là anchor (gốc) chưa:

```bash
trust list --filter=ca-anchors | grep <keyword_ten_ca> -i
```
![](/01-linux/images/user-and-group-management/rhel_root_ca_003.png)
- Xác minh bằng `curl` tương tự như trên.
![](/01-linux/images/user-and-group-management/rhel_root_ca_04.png)
- **Gỡ cài đặt (Deinstall):**
+ Xóa file chứng chỉ đã sao chép khỏi thư mục `/etc/pki/ca-trust/source/anchors/`.

+ Chạy lại lệnh cập nhật:

```bash
sudo update-ca-trust
```
![](/01-linux/images/user-and-group-management/rhel_root_ca_05.png)

![](/01-linux/images/user-and-group-management/rhel_root_ca_06.png)
# Cài Đặt Root Certificates trên Trình duyệt Chrome (Linux)

Đối với Chrome trên Linux, trình duyệt này thường sử dụng kho chứng chỉ riêng của mình thay vì dựa hoàn toàn vào kho chứng chỉ của hệ điều hành.
![](/01-linux/images/user-and-group-management/Linux_Certs008.png)
1. Mở trình duyệt Chrome.
2. Truy cập Settings (Cài đặt).
![](/01-linux/images/user-and-group-management/Linux_Certs009.png)
3. Vào mục **Privacy and security (Quyền riêng tư và bảo mật)** -> **Security (Bảo mật)** -> **Manage certificates (Quản lý chứng chỉ)** -> Chọn tab **Authorities (Cơ quan cấp chứng chỉ).**
![](/01-linux/images/user-and-group-management/Linux_Certs010.png)
4. Nhấp vào Import (Nhập) và chọn file Root Certificate mong muốn.
![](/01-linux/images/user-and-group-management/Linux_Certs011.png)
5. Chọn Trust settings (Cài đặt tin cậy) bạn muốn áp dụng cho CA đó (ví dụ: tin cậy để xác định trang web, tin cậy để xác định người dùng email).
![](/01-linux/images/user-and-group-management/Linux_Certs012.png)
6. Nhấp OK để hoàn tất.
![](/01-linux/images/user-and-group-management/Linux_Certs013.png)
![](/01-linux/images/user-and-group-management/Linux_Certs014.png)