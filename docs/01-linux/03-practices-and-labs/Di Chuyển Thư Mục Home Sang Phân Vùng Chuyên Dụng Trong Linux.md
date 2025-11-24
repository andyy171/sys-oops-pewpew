# Mục lục

- [Tạo Một Phân Vùng Mới](#tạo-một-phân-vùng-mới)
    - [Kiểm tra và Chuẩn bị Ổ đĩa](#kiểm-tra-và-chuẩn-bị-ổ-đĩa)
    - [Tạo Phân vùng và Hệ thống tệp (Filesystem)](#tạo-phân-vùng-và-hệ-thống-tệp-filesystem)
- [Di chuyển thư mục Home](#di-chuyển-thư-mục-home)

- [Phân biệt Các loại Phân vùng (MBR vs GPT)](#phân-biệt-các-loại-phân-vùng-mbr-vs-gpt)

---

Việc di chuyển thư mục Home của người dùng sang một ổ đĩa hoặc phân vùng riêng biệt( dedicated drive/partition) giúp tăng tính bảo mật, dễ dàng nâng cấp hệ điều hành và quản lý dung lượng tốt hơn.

Quá trình này được chia thành hai phần chính: **Tạo Phân vùng mới (nếu chưa có)** và **Di chuyển thư mục Home.**
---
# Tạo Một Phân Vùng Mới
## Kiểm tra và Chuẩn bị Ổ đĩa
1. Kiểm tra các ổ đĩa đã kết nối:

Sử dụng lệnh `parted -l` để liệt kê tất cả các thiết bị lưu trữ đang được hệ thống nhận diện.

```
parted -l
```
![](/01-linux/images/practices/ubuntu_partition001.png)

> Lưu ý: Tên thiết bị như `/dev/sda` hoặc `/dev/sdb` có thể thay đổi ngẫu nhiên sau mỗi lần khởi động. Sự thay đổi này xảy ra do hệ thống có nhiều bộ điều khiển đĩa (IDE, SCSI/SATA) hoặc thiết bị lưu trữ gắn ngoài (USB/Firewire) được phát hiện theo thứ tự không xác định.
> Việc sử dụng **Persistent Naming (Đặt tên bền vững)** thông qua **UUID (Universally Unique Identifier)** hoặc **Labels** là cần thiết để khắc phục vấn đề này và đảm bảo hệ thống luôn gắn đúng phân vùng.

2. Khởi động `parted` để chỉnh sửa ổ đĩa:

- Khởi chạy `parted` với thiết bị bạn muốn thao tác (ví dụ: `/dev/sda`):

```
parted /dev/sda
```

3. Đặt Kiểu Bảng Phân vùng (Partition Table Type):

- Tùy thuộc vào yêu cầu và kích thước ổ đĩa, bạn chọn kiểu bảng phân vùng.

```
(parted) mklabel gpt 
# khuyến nghị sử dụng GPT cho các đĩa hiện đại

(parted) mklabel msdos 
# dùng cho kiểu MBR cũ
```

---

## Tạo Phân vùng và Hệ thống tệp (Filesystem)

1. Tạo Phân vùng mới:
```
(parted) mkpart ext4 0% 100%
```
Mô tả: Lệnh này chỉ tạo một phân vùng mới và chuẩn bị nó cho một loại hệ thống tệp cụ thể (ví dụ: ext4), nhưng KHÔNG TẠO ra filesystem đó. Lệnh này hữu ích khi tạo phân vùng cho các hệ thống tệp mà Parted không hỗ trợ trực tiếp (hoặc cho LVM).

> Phải sử dụng lệnh mkfs (như # mkfs.ext4) ở bước tiếp theo để định dạng phân vùng.
> Lưu ý: Với bảng phân vùng**msdos (MBR)**, bạn cần chỉ định loại phân vùng (`primary`, `extended`, hoặc `logical`).
(ví dụ: `mkpart primary ext4 0% 100%`). Với bảng phân vùng GPT, bạn cần chỉ định tên cho phân vùng, nhưng không cần chỉ định loại.

2. Tạo Hệ thống Tệp (Filesystem):

- Lệnh `mkpart` chỉ chuẩn bị phân vùng, chưa tạo filesystem. Sử dụng `mkfs.ext4` để tạo filesystem trên phân vùng vừa tạo (giả sử phân vùng mới là `/dev/sdb1`).

```
mkfs.ext4 /dev/sdb1
```
![](/01-linux/images/practices/ubuntu_partition002.png)
3. Gắn tạm thời (Mount) Phân vùng mới:

- Tạo thư mục làm điểm gắn kết (mount point): 
```
mkdir /media/home
```
- **Xác định UUID** của phân vùng mới bằng lện `blkid`
![](/01-linux/images/practices/ubuntu_partition004.png)
- Chỉnh sửa tệp `/etc/fstab` để thêm thông tin phân vùng, sử dụng UUID để đảm bảo việc gắn kết là cố định:
```
UUID=<UUID_của_phân_vùng>  /media/home ext4 defaults 0 0
```
![](/01-linux/images/practices/ubuntu_partition003.png)
- Gắn kết ngay lập tức mà không cần khởi động lại:  `mount -a`

- Kiểm tra phân vùng đã được gắn vào` /media/home` chưa bằng lệnh `df -h` hoặc  `lsblk`

+ `df -h`
![](/01-linux/images/practices/ubuntu_partition007.png)
+ `lsblk`: Hiển thị danh sách các thiết bị khối (block devices) và điểm gắn kết (mount points). Các thiết bị khối có đặc điểm là truy cập dữ liệu ngẫu nhiên, tổ chức theo các khối kích thước cố định (ổ cứng, CD-ROM, RAM disk, v.v.).
![](/01-linux/images/practices/ubuntu_partition005.png)
+ pydf
![](/01-linux/images/practices/ubuntu_partition006.png)
+ `findmnt`: Liệt kê tất cả các hệ thống tệp đã được gắn hoặc tìm kiếm một filesystem cụ thể. Lệnh này tìm kiếm trong `/etc/fstab`, `/etc/mtab`, hoặc `/proc/self/`mountinfo.
![](/01-linux/images/practices/ubuntu_partition008.png)
+ `/proc/mounts`: Tệp giả lập (pseudo-file) trong hệ thống tệp tiến trình (`/proc`) chứa thông tin về tất cả các thiết bị hiện đang được gắn trên hệ thống.
![](/01-linux/images/practices/ubuntu_partition009.png)
---
# Di Chuyển Thư Mục Home
Sau khi phân vùng mới được tạo và gắn tạm thời tại `/media/home`, chúng ta tiến hành di chuyển dữ liệu.

1. Sao chép Dữ liệu Home Hiện có:

Sử dụng lệnh `rsync` để sao chép toàn bộ dữ liệu từ thư mục `/home` cũ sang `/media/home `(điểm gắn kết của phân vùng mới), đảm bảo bảo toàn tất cả quyền (permissions) và thuộc tính (attributes).

``` 
sudo rsync -aXS --progress /home/. /media/home/.

Các cờ (Flags):

-a: archive mode (bảo toàn quyền, liên kết tượng trưng, thời gian sửa đổi,...).

-X: preserve extended attributes (bảo toàn thuộc tính mở rộng).

-S: handle sparse files efficiently (xử lý hiệu quả các tệp thưa thớt).

--progress: Hiển thị tiến trình sao chép.
```
2. Đổi tên và Tạo lại Thư mục Home:

- Đổi tên thư mục `/home` gốc thành `home_old` để dự phòng (backup).
```
mv /home /home_old
```

- Tạo lại thư mục /home mới (sẽ là điểm gắn kết cuối cùng).
```
mkdir /home
``` 

3. Cập nhật `/etc/fstab` và Gắn kết Cuối cùng:

- Chỉnh sửa lại tệp `/etc/fstab`.
![](/01-linux/images/practices/ubuntu_partition010.png)
- Thay đổi điểm gắn kết (mount point) của phân vùng mới từ `/media/home` thành `/home.`
![](/01-linux/images/practices/ubuntu_partition011.png)
+ Trước: `UUID=... /media/home ext4 defaults 0 0`

+ Sau: `UUID=... /home ext4 defaults 0 0`

- Gắn kết phân vùng mới vào điểm /home vừa tạo:

```
mount -a
```

4. Hoàn tất và Xác minh:

- Phân vùng mới chứa dữ liệu Home đã được gắn thành công tại `/home`.

- Kiểm tra lại bằng lệnh `df -h` hoặc `lsblk` để xác nhận phân vùng mới đang gắn tại `/home`.

- Bạn có thể xóa thư mục `/home_old` sau khi xác nhận mọi thứ hoạt động ổn định.

---
# Phân biệt Các loại Phân vùng (MBR vs GPT)
Sự khác biệt giữa **Primary Partition**, **Logical Partition**, **Extended Partition** chỉ áp dụng khi sử dụng bảng phân vùng **Master Boot Record (MBR)**.

- **MBR:** Giới hạn tối đa 4 phân vùng chính (Primary). Để vượt qua giới hạn này, bạn phải sử dụng tối đa 3 Primary và 1 Extended Partition.

+ **Extended Partition:** Là một vùng chứa, bên trong nó có thể chứa nhiều Logical **Partition (Phân vùng Logic)**.

+ Chỉ một **Primary Partition** mới có thể được đánh dấu là Active Partition (Phân vùng Khởi động) để chứa Boot Loader.

- **GUID Partition Table (GPT):** Là lược đồ phân vùng hiện đại.

+ **Không có giới hạn** về Phân vùng Chính (tất cả đều là Primary Partition, thường là tối đa 128) và không cần dùng đến Extended/Logical Partition.

+ GPT là tiêu chuẩn được khuyến nghị cho các hệ thống hiện đại.