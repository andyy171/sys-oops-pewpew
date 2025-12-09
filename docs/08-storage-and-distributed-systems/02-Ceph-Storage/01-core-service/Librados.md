Librados – Thư Viện Cốt Lõi Cho Truy Cập Trực Tiếp Vào RADOS
- Librados là thư viện C++ cung cấp khả năng truy cập trực tiếp vào lớp RADOS của Ceph Storage Cluster, cho phép ứng dụng lưu trữ và lấy object mà không qua giao diện cấp cao. Librados xây dựng nền tảng mạnh mẽ, mở rộng cao, hiệu năng cao, tận dụng RADOS mà không giảm tốc độ. 
- Xuất phát từ mục tiêu lưu trữ phân tán, librados hỗ trợ mở rộng tới exabyte, tương thích cao với C, C++, Python, Java, PHP. Nó nổi bật trong ngành lưu trữ, giải pháp cho vấn đề tăng trưởng dữ liệu. 
+ Nguyên tắc cơ bản: mở rộng thành phần, chịu lỗi cao, dựa trên phần mềm mở, thích nghi cao. Librados quản lý object, nhân bản toàn cluster, nâng cao bảo đảm. Object không có đường dẫn vật lý, linh hoạt mở rộng tới petabyte-exabyte.
>Librados và tương lai lưu trữ: Khối lượng dữ liệu tăng 40-60% hàng năm, sinh vấn đề thống nhất, phân tán, hiệu năng.
>
=> Librados giải pháp nổi bật với thống nhất, phân phối, chi phí hợp lý. Tích hợp kernel, vượt trội hơn giải pháp hiện tại. 
- Librados – Giải pháp cloud: Truy cập cloud cần lưu trữ, librados giải quyết giới hạn truyền thống, hỗ trợ OpenStack, Kubernetes. Đội ngũ Canonical, Red Hat, SUSE hoàn thiện librados, tương thích Linux cao. 
- Librados – Software-defined: Tiết kiệm chi phí, hỗ trợ phần cứng đa dạng, lợi thế low cost, reliability, scalability. 
- Librados – Truy cập thống nhất: Object-based access duy nhất, đáp ứng tăng trưởng dữ liệu. Xây dựng unified access, hỗ trợ luồng dữ liệu lớn. Quản lý object, hỗ trợ mở rộng không giới hạn bằng CRUSH.

- Kiến trúc mới: Không dùng metadata trung tâm, thay bằng CRUSH tính toán vị trí data, cải thiện tốc độ, phân tán node. CRUSH nhận thức hạ tầng (disk, pool, node, rack, data center), tự sửa lỗi, nhân bản data. Tạo hạ tầng đảm bảo, đáng tin cậy. Hỗ trợ atomic transaction, interclient communication. Tăng performance, reliability cho PaaS/SaaS. 

>Librados dẫn đầu công nghệ access mới, vượt giới hạn, mở, software-defined, linh hoạt. Thống nhất object access, phù hợp small/big data. Tự quản trị, sửa lỗi disk, node, network, rack, data center.
>