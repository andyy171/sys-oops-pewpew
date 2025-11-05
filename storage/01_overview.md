# Tổng quan về Storage

Hệ thống lưu trữ trong công nghệ thông tin (CNTT) là một thành phần cốt lõi, đảm bảo dữ liệu được lưu trữ, truy cập và quản lý một cách hiệu quả. Nó được tổ chức theo cấu trúc phân cấp (hierarchy), giúp cân bằng giữa tốc độ, dung lượng và chi phí. Cấu trúc này bao gồm các cấp độ từ bộ nhớ nhanh nhất (như RAM) đến lưu trữ chậm hơn nhưng dung lượng lớn (như băng từ). Vai trò của các thành phần chính như sau:

- **Controller:** Là **bộ điều khiển lưu trữ, quản lý giao tiếp giữa hệ thống và thiết bị lưu trữ**. Nó xử lý các lệnh đọc/ghi, quản lý **RAID (Redundant Array of Independent Disks)** để tăng độ tin cậy và hiệu suất, và đôi khi tích hợp cache để tối ưu hóa tốc độ. Ví dụ, trong các hệ thống doanh nghiệp, controller có thể là một card HBA (Host Bus Adapter) hoặc tích hợp trong mainboard.
- **Disk:** **Thiết bị lưu trữ vật lý,** có thể là **HDD (Hard Disk Drive)** với đĩa từ quay cơ học hoặc **SSD (Solid State Drive)** sử dụng chip flash. Disk lưu trữ dữ liệu dưới dạng block (khối), thường là 4KB hoặc 512B mỗi block.
- **Cache:** Là **bộ nhớ tạm thời tốc độ cao** (thường là DRAM hoặc SRAM) để lưu trữ dữ liệu thường xuyên truy cập, giảm thời gian chờ đợi từ disk chậm hơn. Cache có thể nằm ở mức controller, OS, hoặc ứng dụng.

Quá trình ghi/đọc dữ liệu diễn ra theo chuỗi: Ứng dụng yêu cầu dữ liệu qua hệ điều hành (OS), OS chuyển lệnh đến file system (FS), FS ánh xạ thành block, và block được gửi đến disk qua controller. Trong quá trình đọc, nếu dữ liệu có trong cache, nó sẽ được trả về ngay lập tức (cache hit), ngược lại là cache miss và phải đọc từ disk. Quá trình ghi có thể là write-through (ghi ngay vào disk) hoặc write-back (ghi vào cache trước, sau đó flush vào disk để tăng tốc độ nhưng rủi ro mất dữ liệu nếu hệ thống crash).

## Phân biệt các loại lưu trữ

- **Lưu trữ cục bộ (Local Storage):** **Dữ liệu nằm trực tiếp trên máy tính hoặc server**, như ổ cứng nội bộ. 
+ Ưu điểm: Tốc độ cao, latency thấp.
+ Nhược điểm: Không chia sẻ dễ dàng, rủi ro mất dữ liệu nếu hardware hỏng.

- **Lưu trữ mạng (Network Storage):** **Dữ liệu được lưu trữ trên các máy chủ được kết nối với các mạng để có thể truy cập**, như NAS (Network Attached Storage) hoặc SAN (Storage Area Network). NAS dùng giao thức file-level (NFS, SMB), SAN dùng block-level (iSCSI, Fibre Channel). 
+ Ưu điểm: Chia sẻ dữ liệu giữa nhiều máy.
+ Nhược điểm: Latency cao hơn do mạng.

- **Lưu trữ phân tán (Distributed Storage):** Dữ liệu được phân bổ trên nhiều node, như trong cloud (AWS S3, Google Cloud Storage) hoặc hệ thống như Ceph, Hadoop HDFS. 
+ Ưu điểm: Scale horizontally, fault-tolerant.
+ Nhược điểm: Phức tạp quản lý, overhead đồng bộ hóa.

>Lưu ý: Trong thực tế, các loại lưu trữ thường kết hợp, ví dụ hybrid cloud với local cache cho distributed storage để giảm latency.
>

# Các Khái Niệm Chính
## Storage Layer (Physical – Logical – Application View)
- **Physical View:** Tập trung vào hardware thực tế, như disk, controller, cable. Ví dụ, một array disk trong RAID 5 với striping và parity để bảo vệ dữ liệu.
- **Logical View:** Ánh xạ logic qua phần mềm, như LVM (Logical Volume Manager) ở Linux, cho phép resize volume mà không thay đổi physical disk.
- **Application View:** Cách ứng dụng thấy dữ liệu, như qua API hoặc [file system](/storage/filesystem/01_overview_and_types.md). Ứng dụng không quan tâm physical mà chỉ thấy logical file hoặc object.

## Data I/O Path: Application → OS → FS → Block → Disk
Đây là đường dẫn I/O tiêu chuẩn:

1. **Application:** Gửi yêu cầu read/write qua syscall (như read() ở POSIX).
2. **OS:** Kernel xử lý, queue lệnh vào I/O scheduler (như CFQ hoặc deadline ở Linux) để ưu tiên.
3. **FS:** File system (ext4, NTFS) chuyển thành block address.
4. **Block:** Layer block device gửi đến driver.
5. **Disk:** Thiết bị thực hiện I/O.

>Lưu ý: Đường dẫn này có thể bị gián đoạn bởi cache (page cache ở OS) hoặc virtualization (hypervisor thêm layer).

## Interface Standards: SATA, SAS, NVMe
- **SATA (Serial ATA):** Phổ biến cho consumer, tốc độ lên đến 6Gb/s, hỗ trợ hot-swap hạn chế.**
- **SAS (Serial Attached SCSI):** Doanh nghiệp, tốc độ 12Gb/s, hỗ trợ multipath, expander cho nhiều device.
- **NVMe (Non-Volatile Memory Express):** Cho SSD, sử dụng PCIe bus, latency thấp (microseconds), parallel queues cho IOPS cao.

>NVMe vượt trội hơn SATA/SAS về hiệu suất, nhưng yêu cầu hardware tương thích; trong môi trường legacy, SAS vẫn được ưa chuộng vì backward compatibility.