# Cơ bản về SSH

---

## Tổng quan về SSH
- Giao thức Secure Shell (SSH) là giao thức mạng bảo mật để vận hành các dịch vụ mạng một cách an toàn trên đường truyền mạng không bảo mật.

- Mặc định ssh service được expose trên port `22`

- Sử dụng lệnh: `systemctl status sshd`(kiểm tra trạng thái, port chạy ssh)

~[](./images/ssh-sample.png)

- Keystore directory: Default dir Windows `C:\Users\<username>\. ssh`, default dir in Linux: `/home/<username>\. ssh`

---
## SSH hoạt động như thế nào 
![](./images/ssh-mechanism.png)
1. Client gửi yêu cầu kết nối SSH
- Máy khách (client) khởi tạo một phiên kết nối SSH đến máy chủ (server).
- Trong yêu cầu này, client thông báo danh tính người dùng và yêu cầu xác thực.

2. Server gửi chuỗi thử thách (challenge)
- Máy chủ phản hồi bằng một chuỗi ngẫu nhiên (challenge string).
- Chuỗi này đóng vai trò như “bài toán” để kiểm chứng rằng client thật sự sở hữu **private key** tương ứng với public key đã được lưu trên server.

3. Client mã hóa chuỗi thử thách bằng private key
- Client sử dụng private key của mình để mã hóa chuỗi thử thách đó.
- Sau khi mã hóa, client gửi lại kết quả (chuỗi đã mã hóa) cho server.

4. Server xác thực bằng public key

- Server dùng public key (đã lưu sẵn trong file `~/.ssh/authorized_keys`) để giải mã chuỗi nhận được.
- Nếu giải mã thành công và nội dung khớp với chuỗi thử thách ban đầu, server xác nhận rằng client sở hữu private key hợp lệ → **xác thực thành công.**
- Sau đó, kết nối SSH được thiết lập an toàn và mã hóa toàn bộ dữ liệu truyền giữa hai bên.

> Bản chất là SSH sử dụng mã hóa bất đối xứng (asymmetric encryption) để xác thực và mã hóa đối xứng (symmetric encryption) để truyền dữ liệu sau khi kết nối được thiết lập. Điều này giúp đảm bảo dữ liệu truyền không bị đọc trộm , danh tính client được xác thực và toàn vẹn dữ liệu trong suốt phiên làm việc .

---

## SSH Prerequisites

- Cả client machine lẫn remote host phải có service sshd running
+ Cài đặt ssh và khởi động dịch vụ SSH trên ubuntu 
```bash
sudo apt-get install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh

# Check 
sudo systemctl status sshd # Linux
# netstat -an | find "22” // Windows

# Enable ssh
sudo systemctl enable ssh | sudo systemctl start ssh
```

- Thông mạng từ máy client tới remote host :
+ Kiểm tra kết nối bằng cách ping remote host với `ping <remote-host>` ( Trường hợp không ping được có thể do ICMP bị block)
+ `telnet <remote-host> 22` để kiểm tra kết nối đến port 22 của server 

- SSH thoogn quan username & password | ssh sử dụng keypair
+ **SSH bằng username&passwd:** Nhập chính xác username có tồn tại trên remote server và passwd
+ **SSH bằng key-pair:** Kiểm tra cặp key-pair (public | private key) phải là một cặp và pass phrase của key-pair nếu có

## Establish SSH connect 
- **Tạo cặp khóa SSH** `ssh-keygen` : Mặc định sẽ tạo ra một cặp khóa `id_rsa` và `id_rsa.pub`  
    + Common options: 
    `-f` “ ” : xác định tên file cho file key được tạo 
    `-N` “ ” : chỉ định pass phrase cho khóa được tạo 
    `-t` : Xác định loại khóa được tạo ( rsa, dsa, ecdsa) 
    `-b` : xác định số bit của khóa được tạo 
    `-p` : Thay đổi pass phrase cho khóa private có sẵn 
    `-i` : Chỉ định khóa SSH
- **Sử dụng cặp khóa SSH để thiết lập kết nối SSH đến remote server**
1. **Copy khóa SSH public lên server:** Để sử dụng xác thực khóa public, khóa public phải được sao chép vào máy chủ cần remote và được cài đặt trong file `authorized_keys`. Khi khóa public đã được định cấu hình trên máy chủ cần remote, máy chủ sẽ cho phép bất kỳ người dùng kết nối nào có khóa private đăng nhập: 
```bash
ssh-copy-id -i <ssh-public-key> user@remote-host
```

2. **Sử dụng khóa private để SSH lên remote server** `ssh -i <ssh-private-key> user@remote-host`
- **Lần đầu kết nối:** client sẽ hỏi tiếp tục connecting hay không và lưu thông tin về host và `private-key` vào file `known_hosts`

---
## SSH Configuration
### Khởi tạo phiên SSH
- Nếu đang sử dụng Linux hoặc Mac OS , kết nối **SSH** khá đơn giản bằng cách sử dụng **Terminal** . Nếu sử dụng Windows , cần thêm 1 chương trình khác để mở kết nối **SSH** . Trình kết nối SSH được sử dụng phổ biến nhất cho Windows là **PuTTY** .

- Với Mac OS và Linux , mở **Terminal** và gõ lệnh theo cấu trúc sau :  `ssh user@[host/IP]`
    + Trong đó :
        * `user` : user local trên máy cần ssh
        * `host/IP` : hostname ( VD : `www.xyzdomain.com` ) hoặc IP của máy cần kết nối SSH ( VD : `244.235.23.19 `)
Sau khi thực hiện lệnh , máy đầu xa sẽ yêu cầu password của user sử dụng SSH .

### Chỉnh sửa file cấu hình SSH
- Các file cấu hình cần lưu ý khi quản trị SSH :
+ `/etc/ssh/sshd_config` : file cấu hình SSH Server
+ `/etc/ssh/ssh_config` : file cấu hình SSH Client
+ `~/.ssh/` : thư mục chứa nội dung cấu hình SSH của user client trên Linux
+ `/etc/nologin` : nếu file này tồn tại , thì dịch vụ SSH Server trên Linux sẽ từ chối đăng nhập từ các user khác trên hệ thống ngoại trừ user root . File này thường dùng cho trường hợp khẩn cấp cần cách ly sớm hệ thống .
- Để chỉnh sửa file cấu hình SSH Server, ta dùng lệnh : # vi /etc/ssh/sshd_config :set nu

---
#### Thay đổi port SSH và giới hạn IP lắng nghe SSH
- Dịch vụ SSH mặc định hoạt động trên port 22 . Vì là port phổ biến , rất dễ bị kẻ xấu thực hiện các hoạt động dò tìm mật khẩu tự động đăng nhập SSH vào hệ thống .

- Để điều chỉnh port mặc định , xuống dòng 17 , chỉ định port mới , đồng thời bỏ dấu “#” ở đầu dòng :
![](./images/ssh-port-1.png)
- Nếu hệ thống có nhiều hơn 1 địa chỉ IP thì tốt nhất nên chỉ định rõ địa chỉ IP nào sẽ lắng nghe port SSH . Thực hiện sửa đổi ở dòng 19 , đồng thời bỏ dấu “#” ở đầu dòng ( 0.0.0.0 có nghĩa là mọi IP đều lắng nghe SSH ):
![](./images/ssh-port-2.png)

---
#### Cấu hình thời gian timeout khi user đăng nhập không thành công

- Khi 1 user đăng nhập SSH , nếu không chỉ định thông tin user từ đầu thì sẽ hiện ra 1 prompt yêu cầu nhập thông tin user . Sau đó là phần nhập mật khẩu nếu user đó đăng nhập bằng mật khẩu . Ta sẽ quy định thời gian 1 kết nối SSH đợi cho hoạt động đăng nhập user thành công , nếu sau khoảng thời gian này không đăng nhập được thì ngắt kết nối .

- Thay đổi tùy chọn này ở dòng `37 `( mặc định đã được cấu hình là `2 phút` ) : 
![](./images/ssh-port-3.png)

#### Không cho đăng nhập bằng user root
Nếu muốn sử dụng quyền `root` chỉ cần tạo 1 user khác rồi cấp quyền `sudo` cho các lệnh cần thực hiện và sử dụng => Bảo mật hệ thống hơn .

Để cấu hình , tìm đến dòng 38 , sửa “`yes`” thành “`no`” đồng thời bỏ dấu “`#`” ở đầu dòng : 
![](./images/ssh-port-4.png)

#### Chế độ “Strict Mode”

- Ta sẽ chỉ định dịch vụ SSH phải kiểm tra thông tin quyền của thư mục `$HomeUser` , thư mục `.ssh` và file `authorized_keys` chứa key SSH nếu dùng SSH key .

Nếu không sử dụng chế độ này ( `no` ) thì SSH sẽ **không kiểm tra cấu hình các quyền khi đăng nhập vào Server** . 
=> Ép người quản trị phải cấu hình đúng các phân quyền ( permissions ) cho các thư mục / key dùng để đăng nhập SSH .

Thay đổi tùy chọn này ở dòng `39` ( mặc định đã để `yes` ) :
![](./images/ssh-port-5.png)

#### Thiết lập số lần đăng nhập sai tối đa
Nếu đăng nhập sai số lần quy định sẽ ngắt kết nối của Client .
Thay đổi tùy chọn này ở dòng `40` ( mặc định là `6` ) :

![](./images/ssh-port-6.png)

#### Thiết lập số phiên đăng nhập SSH tối đa
- Thực hiện thay đổi ở dòng 41 ( mặc định là 10 ) :

#### Sử dụng chứng thực bằng SSH key , thay vì mật khẩu
- Mặc định , mỗi VPS/Cloud Server sẽ đăng nhập vào bằng user root hoặc user thường . Tuy nhiên việc sử dụng mật khẩu có 2 nguy cơ lớn là :
    + Mất toàn bộ hệ thống nếu để lộ mật khẩu
    + Hacker có thể dùng phương thức tấn công BruteForce để dò ra mật khẩu
=> Vì vậy nên dùng SSH Key để đăng nhập vào Server cũng như sử dụng nó để xác thực các kết nối từ bên ngoài vào cho an toàn hơn . Đồng thời , nếu có thể nên tắt cấu hình chứng thực mật khẩu .

Thực hiện thay đổi ở dòng `43` và `65` :
![](./images/ssh-config-1.png )
![](./images/ssh-config-2.png )

#### Tắt log đăng nhập lần cuối
Thực hiện sửa đổi ở dòng `106` , đồng thời bỏ dấu “#” ở đầu dòng :
![](./images/ssh-config-3.png )

#### Cấu hình thời gian ngắt kết nối SSH khi user không hoạt động
- Có thể quy định thời gian timeout mà 1 kết nối SSH đến Server Linux không nhận được bất kỳ hoạt động tương tác nào trên Terminal SSH . Lúc này nếu quá thời gian quy định thì SSH Server sẽ tự ngắt kết nối từ các user không tương tác .
- Thực hiện thay đổi ở dòng `112` và `113` , đồng thời bỏ dấu “`#`” ở đầu dòng :
![](./images/ssh-config-4.png )


####  Giới hạn User/Group sử dụng cho SSH
- Mặc định SSH Server cho phép tất cả các user local đăng nhập qua SSH . Nhưng đôi khi cần chặn không cho đăng nhập với 1 số user nhất định hoặc 1 nhóm cụ thể .

- Để cho phép user hoặc group được đăng nhập SSH , thực hiện thêm vào 1 số dòng sau vào cuối file :
![](./images/ssh-config-5.png )

- Để không cho phép user hoặc group được đăng nhập SSH , thực hiện thêm vào 1 số dòng sau vào cuối file :
![](./images/ssh-config-6.png )

### Kiểm tra lại file cấu hình
Thực hiện kiểm tra lại quá trình sửa đổi file `sshd_config` xem có sai không , nếu sai sẽ báo lỗi :  `sshd -t`
### Cho phép SSH qua Firewalld
```
# firewall-cmd --permanent --zone=public --add-port=22/tcp
# firewall-cmd --reload
```
hoặc
```
# firewall-cmd --permanent --zone=public --add-service=ssh
# firewall-cmd --reload
```
### Khởi động lại dịch vụ SSH
```
# systemctl restart sshd
# systemctl enable sshd
```

--- 

## Các lỗi thường gặp
1. Sai user, remove host IP | domain, password phrase, public-private key Solution: => Kiểm tra lại thông tin kết nối
2. Không có kết nối mạng đến remote host Solution:
=> Solution: 
- Kiểm tra lại kết nối đến remote host: `ping <remote-host>` , `telet <remote-host-ip> <port>`
- Kiểm tra bảng route: `ip route show`, `traceroute <remote-host>`
- Kiểm tra firewall service trên remote-host ( firewalld, iptable ), security group/security port vm khách
3. Quyền của file private-key không đảm bảo an toàn Detail:
=> Solution:
Set quyền lại cho file key: sử dụng lệnh: `chmod 0400 <key-file>` (Gắn quyền chỉ đọc cho user owner và không quyền cho các user khác)
4. Không dùng được private key do định danh `remote-host` bị trùng trong file knownhost

5. Service SSH không hoạt động trên máy khách or remote-host
**Detail:** `systemctl status ssh`

=> Solution: khởi động lại dịch vụ `ssh systemctl start ssh | systemctl enable ssh`

## Customer Issues solutions
- Yêu cầu khách mô tả lại lỗi, hiện tượng khách gặp phải ( Kèm theo ảnh )
- Kiểm tra lại hoạt động của sshd service, kiểm tra lại kết nối từ remote-host đến máy khách, firewall service, security group …

- **Checklist**

1. Kiểm tra lại user khách dùng có tồn tại trên remote-host hay không.
Hỏi khách dùng image gì để tạo VM? ⇒ user trên image đó
2. Yêu cầu khách kiểm tra lại remote-host IP hoặc domain khách muốn kết nối đến. Yêu cầu khách cung cập IP/domain của remote host.
3. Kiểm tra lại sshd service trên máy khách và remote-host
systemctl status ssh
4. Kiểm tra lại kết nối mạng từ máy khách đến remote-host, lỗi có thể gặp khi ssh:
- Máy khách cố gắng thiết lập kết nối mạng tới máy chủ SSH nhưng máy chủ không phản hồi trong khoảng thời gian chờ.
```
ssh: connect to host 10.0.0.10 port 22: Connection timed out
```
- Trên máy khách: `ping <remote-host>` trong trường hợp không ping được ⇒
- Trên máy khách: `telet <remote-host>` trong trường hợp không telnet được ⇒
- Trên máy khách: `traceroute <remote-host>`
5. Kiểm tra hoạt động của tường lửa
- Trên máy khách: `systemctl status iptables` → `sudo iptables -nL`
- Yêu cầu khách cung cấp thông tin VM ( IP, …) ⇒ kiểm tra cấu hình security group
```
ssh: connect to host 10.0.0.10 port 22: Connection Refused
```