# Mục lục 


---

# Tổng quan
Ceph cung cấp một nền tảng lưu trữ thống nhất thông qua nhiều giao diện (Interface) để đáp ứng các nhu cầu lưu trữ khác nhau.

- **Ceph Object Storage (RADOS Gateway - RGW)** cung cấp giao diện lưu trữ đối tượng tương thích với các chuẩn RESTful phổ biến như Amazon S3 và OpenStack Swift. Đây là giải pháp lý tưởng cho các ứng dụng điện toán đám mây, lưu trữ dữ liệu phi cấu trúc và nội dung số lớn.

- **Ceph Block Device (RBD)** cung cấp các block storage có khả năng mở rộng và hiệu suất cao. Giao diện này thường được dùng để cung cấp ổ đĩa ảo cho máy ảo trong các nền tảng như OpenStack hoặc KVM, và cho các cơ sở dữ liệu đòi hỏi độ trễ thấp.

- **Ceph File System (CephFS)** là một hệ thống tập tin phân tán, cung cấp một hệ thống file POSIX tương thích và có thể chia sẻ được. Nó phù hợp cho các workload truyền thống cần một không gian lưu trữ dùng chung, như home directories, kho lưu trữ hoặc dữ liệu cho các cụm máy tính hiệu năng cao (HPC).

Tất cả các giao diện này đều được xây dựng trên nền tảng RADOS vững chắc, cho phép chúng kế thừa các đặc tính về khả năng mở rộng, độ tin cậy và tính nhất quán của cụm Ceph.


# RBD – Ceph Block Device
- RBD hay Ceph Block Device là thành phần cung cấp giải pháp block storage trong Ceph, lưu trữ dữ liệu dạng khối với mở rộng, hiệu năng cao, chịu lỗi vượt trội. RBD thiết kế đáp ứng **lưu trữ phân tán, mạnh mẽ, mở rộng cao**, hỗ trợ exabyte, tương thích cao hệ thống ảo hóa phần cứng. RBD nổi bật ngành lưu trữ đám mây, giải pháp cho vấn đề cloud public private hybrid. Phần cứng quyết định hạ tầng, RBD đáp ứng, cung cấp block storage mạnh, tin cậy cao.

- RBD blocks chia thành nhiều obj, phân tán toàn Ceph cluser, cung cấp tính bảo đảm, hiệu năng cao. RBD hỗ trợ Linux kernel, và được tích hợp với Linux kernel, cung cấp tính năng snapshot tốc độ cao, nhẹ, copy-on-write cloning, and several others. Hỗ trợ in-memory caching, nâng cao hiệu năng.

- Nguyên tắc cơ bản RBD: 
+ Mở rộng thành phần, chịu lỗi cao.
+ Phần mềm mở, thích nghi cao, tương thích phần cứng. 

- Ceph RBD hỗ trợ image size tới 16EB. Image có thể là disk vật lý, máy ảo, … Các công nghệ KVM, Zen hỗ trợ đầy đẩy RBD, tăng tốc máy ảo. Ceph block hỗ trợ đầy đủ nền tảng ảo hóa mới OpenStack, CloudStack,..
+ Nền tảng RBD dựa object RADOS, tổ chức blocks objects. Dữ liệu block lưu object cluster. Block storage RBD giải pháp truyền thống, hạ tầng độc lập phần cứng. RBD quản lý object, nhân bản cluster, nâng bảo đảm. Block không đường dẫn vật lý, linh hoạt mở rộng petabyte-exabyte.

## RBD snapshots & cloning



## RBD mirroring (journal-based, snapshot-based)


## RBD exclusive-lock, object-map, fast-diff



## Thao tác cơ bản 
```bash
# Thin provisioning & dynamic resize
rbd create --size 1T --thick-provision pool/image
rbd resize --size 2T pool/image

# Snapshot & Clone
rbd snap create pool/image@snap1
rbd snap protect pool/image@snap1
rbd clone pool/image@snap1 pool/clone1
rbd flatten pool/clone1   # tách khỏi parent

# mirroring
rbd mirror pool enable pool snapshot
rbd mirror daemon status
```

### Các tính năng nâng cao hơn 
- Tăng tốc độ ghi 
```bash
rbd create --image-feature exclusive-lock,object-map,fast-diff,journaling pool/image
```
- `exclusive-lock`: Chỉ 1 client ghi cùng lúc
- `object-map`: Tăng tốc diff & clone (yêu cầu exclusive-lock)
- `fast-diff`: Tăng tốc rbd diff lên 100x
- deep-flatten, trash, trash purge schedule

- Erasure coding & NVMe-oF
```bash
rbd create --size 10T --data-pool ec62_pool pool/image
ceph orch apply iscsi pool --gateway-placement="3 host[6-8]"
```



![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/RBD.png)

## So sánh với block truyền thống 
- Block truyền thống không metadata thông minh. Metadata quyết định viết đọc. Cần trung tâm quản lý. Request tìm bảng metadata lớn, trễ cao hệ lớn. 
- RBD dùng CRUSH tính toán vị trí, cải thiện tốc độ. Phân tán node. CRUSH nhận thức hạ tầng disk pool node rack switch data center. Lỗi, lưu bản sao nhân rộng, data sẵn sàng. CRUSH tự quản trị sửa lỗi nhân rộng. Hơn 1 bản sao. Hạ tầng block đảm bảo. Sử dụng RBD tăng mở rộng.
RAID kết thúc: RAID ứng dụng lâu, thành công tái tạo chịu lỗi. Tới giới hạn. Dung lượng 4TB-6TB, tái tạo tốn giờ ngày tháng tài nguyên. Tăng TCO chi phí. Quan tâm disk size rpm. Hardware đắt RAID cards, không thêm dung lượng. RAID 5 chịu 1, RAID 6 2, nhiều khó khôi phục. Chỉ disk, không network hardware OS. RBD giải quyết, không phụ thuộc RAID, software-defined. Nhân bản config, định nghĩa bản sao tối ưu. Chịu lỗi nhiều hơn 2, khôi phục nhanh, không chính phụ. Lưu lượng lớn CRUSH maps.
RBD block storage: Block SAN, volumes block node. Lưu lớn đảm bảo hiệu năng. Volumes map OS filesystem. Ceph RBD bảo đảm phân phối hiệu năng block client. RBD chia obj phân tán cluster bảo đảm cao. Hỗ trợ kernel tích hợp snapshot nhanh copy-on-write cloning caching nâng hiệu năng. Image 16EB disk vật lý VM. KVM Xen hỗ trợ RBD tăng tốc VM. RBD hỗ trợ OpenStack CloudStack. RBD SAN doanh nghiệp thin provisioning copy-on-write snapshots clones revertible read-only hỗ trợ cloud.

>RBD dẫn đầu block mới. Vượt giới hạn. Mở software-defined tương thích. Giao diện linh hoạt. Mạnh RAID vượt giới hạn. Bảo đảm HA. Thống nhất toàn diện block. Phù hợp small big block không trục trặc. RBD phân tán client nhanh. Không truyền thống kỹ thuật mới tính toán động. Tăng hiệu năng. Dữ liệu tổ chức tự động. Không lo sự cố intelligent xử lý. Tự quản trị sửa lỗi. Vượt đảm bảo. Sửa disk node network rack data center geographies.
>

# CephFS – Ceph File System
- Ceph filesystem hay CephFS, là POSIX-compliant filesystem, được sử dụng trong Ceph storage cluster sử dụng để lưu trữ user data. CephFS hỗ trợ tốt Linux kernel driver, kiến CephFS tương thích tốt với các nền tảng Linux OS. CephFS lưu data và medata riêng biệt, cung cấp hiệu năng, tính bảo đảm cho app host nằm trên nó

Trong Ceph cluster, Ceph fs lib (libcephfs) chạy trên Rados library (librados) – giao thức thuộc Ceph storage - file, block, and object storage. Để sử dụng CephFS, cần ít nhất 1 Ceph metadata server (MDS) để chạy cluster nodes. Tuy nhiên, sẽ không tốt khi chỉ có 1 MDS server nó sẽ ảnh hưởng tính chịu lỗi Ceph. Khi cấu hình MDS, client có thể sử dụng CephFS theo nhiều cách. Để mount Cephfs, client cần sử dụng Linux kernel hoặc ceph-fuse (filesystem in user space) drivers provided by the Ceph community.

Bên cạnh, Client có thể sử dụng phần mềm thứ 3 như Ganesha for NFS and Samba for SMB/CIFS. Phần mềm cho phép tương tác với "libcephfs", bảo đảm lưu trữ user data phân tán trong Ceph storage cluster. CephFS có thể sử dụng cho Apache Hadoop File System (HDFS). Sử dụng libcephfs component to store data to the Ceph cluster. Để thực hiện, Ceph community cung cấp CephFS Java interface for Hadoop and Hadoop plugins. The libcephfs và librados components rất linh hoạt và ta có thể xây dựng phiên bản tùy chỉnh, tương tác với nó, xây dựng data bên dưới Ceph storage cluster.

![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/cephfs.png)

## **MDS (Metadata Server)**
- Quản lý metadata cho CephFS (file storage), như cấu trúc thư mục, quyền truy cập.
- Phân tán metadata qua nhiều MDS để chịu lỗi.

### MDS active/standby roles

### MDS failure & recovery


## Multiple filesystems support

## Data pool vs Metadata pool

## CephFS snapshots


# RGW – RADOS Gateway
Phương pháp lưu trữ data dạng object thay vì file, blocks truyền thống. Object-based storage nhận được nhiều sự chú ý trong storage industry.

Các tổ chức mong muốn giải pháp lưu trữ toàn diện cho lượng data khổng lồ, Ceph là giải pháp nổi bật vì nó là true object-based storage system. Ceph phân phối obj storage system, cung cấp object storage interface thông qua Ceph's object gateway, được biệt là RADOS gateway (radosgw).

RADOS gateway (radosgw) sử dụng librgw (the RADOS gateway library) và librados, cho phép app thiết lập kết nối với Ceph object storage. Ceph cung cấp giải pháp lưu trữ ổn định, và có thể truy cập thông qua RESTful API.

The RADOS gateway cung cấp RESTful interface để sử dụng cho application lưu trữ

data trên Ceph storage cluster. RADOS gateway interfaces gồm:

Swift compatibility: This is an object storage functionality for the OpenStack Swift API

S3 compatibility: This is an object storage functionality for the Amazon S3 API

Admin API: This is also known as the management API or native API, which can be used directly in the application to gain access to the storage system for management purposes

Để truy câp Ceph object storage system, ta có thể sử dụng RADOS gateway layer. librados software libraries cho phép user app truy tập trực tiếp đến Ceph = C, C++, Java, Python, and PHP. Ceph object storage has multisite capabilities, nó cung cấp giải pháp khi gặp sự cố. Các object storage configuration có thể thực hiện bởi Rados hoặc federated gateways.

![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/rgw.png)


## Multi-site replication (zones, zonegroups, realms)


## S3 vs Swift API


## Bucket policies & lifecycle


## RGW indexless buckets