


Ceph hỗ trợ ba loại lưu trữ chính, mỗi loại phục vụ mục đích khác nhau nhưng đều dựa trên nền tảng RADOS. 

- **Object Storage (Lưu Trữ Đối Tượng)**:
    
    Dữ liệu được lưu dưới dạng **đối tượng (objects)**, mỗi đối tượng là một "hộp" chứa dữ liệu và metadata (như kích thước, ngày tạo). Không có cấu trúc thư mục như hệ thống file thông thường. Dữ liệu được phân mảnh và sao chép để đảm bảo an toàn, phù hợp cho dữ liệu lớn như ảnh, video trên cloud (hỗ trợ S3 API).
    
    <aside>
    ❕Chỉ đọc/ghi toàn bộ object, không hỗ trợ truy cập ngẫu nhiên.
    
    </aside>

    <details>
    <summary> Chi tiết  </summary>
    Object (Đối tượng) gồm thành phần data và metadata được đóng gói => cung cấp 1 thuộc tính định danh (globally unique identifier). Định danh riêng bảo đảm object sẽ độc nhất trong storage cluster.

    Khác file-based storage bị gói hạn size. Object có thể có size to và có thể thay đôi metadata. Data được lưu với nhiều metadata, các thông tin về nội dung data. Metadata trong object storage cho phép user quản lý và truy cập data không có cấu trúc.
    ![](/08-storage-and-distributed-systems/02-Ceph-Storage/images/theory/ceph-in-1.png)

    > Object không giới hạn loại và số lượng metadata, cho phép thêm custom type trong metadata, vì thế ta có full quyền đối với data.
    >

    Ceph không lưu trữ dạng cây phân cấp, obj được lưu trên không gian địa chỉ với hàng ngàn obj , theo quy tắc tổ chức rõ ràng. Obj có thể đc lưu cục bộ, hoặc lưu tách biệt với mặt vật lý trong flat-address space trong không gian lưu trữ liền kề.

    Kỹ thuật hỗ trợ obj có định danh độc nhất trên toàn cluster, bất kỳ app đều có thể lấy data từ object dựa vào OID (sử dụng RESTful API calls). Obj được lưu trong Object-based Storage Device (OSDs), theo pp nhân bản bản. Cung cấp tính HA. Khi Ceph storage cluster nhận yêu cầu ghi từ client, nó lưu data như obj. Tiền trình OSD ghi data tới file trong OSD file system.

    <h3>Định vị Object - Locating objects</h3>

    - Mỗi đơn vị data trong Ceph được lưu dưới dạng obj trong pool.
    - Ceph poop là logical partition sử dụng lưu trữ obj, cung cấp pp tổ chức storage.
    - obj là đơn vị nhỏ nhất trong data storage tại Ceoh. Khi Ceph cluster được triển khai, nó tạo 1 số storage pool mặc định như data, metadata, and RBD pools.
    - Sau khi MDS triển khai trên 1 Ceph node, nó tạo obj trong metadata pool đồng thời yêu cầu  CephFS để cung cấp tính năng.

    </details>
    
- **Block Storage (Lưu Trữ Khối)**:
    
    Dữ liệu được chia thành các **khối (blocks)** cố định (như 4KB), hoạt động như ổ cứng ảo. Sử dụng RBD (RADOS Block Device) images, có thể mount như ổ đĩa cho máy ảo (VM). Dữ liệu được phân tán qua cluster để chịu lỗi. 
    
    <aside>
    ❕Tối ưu cho ứng dụng cần truy cập ngẫu nhiên (như database), khác với object vì không có metadata phong phú.
    
    </aside>
    
- **File Storage (Lưu Trữ Tệp)**:
    
    Cung cấp hệ thống file với cấu trúc thư mục và file, tương tự ext4. Sử dụng CephFS, dữ liệu file được phân mảnh thành objects, metadata được quản lý bởi MDS (Metadata Server). 
    
    <aside>
    ❕Hỗ trợ cấu trúc cây thư mục, phù hợp cho chia sẻ file nhóm, phức tạp hơn block do cần quản lý metadata.
    
    </aside>