# 1. Độ Bền Mạng trong AWS - Network Resilience
Mạng trong AWS giống như hệ thống đường sá và giao thông trong một thành phố đám mây, đảm bảo ứng dụng của bạn luôn kết nối được với người dùng dù có sự cố. Hãy tưởng tượng bạn đang xây dựng một ứng dụng web (gọi là Cartogram) và muốn nó luôn online, bất kể một phần của AWS có vấn đề. Phần này sẽ giải thích cách đạt được độ bền ở hai cấp độ: cục bộ (trong một vùng như US-East-1) và toàn cầu (qua nhiều vùng).
## 1.1. Độ Bền Cục Bộ (Trong Một Vùng)
- Tổng quan: Một vùng AWS (region) như US-East-1 là một khu vực địa lý chứa nhiều Khu vực Khả dụng (Availability Zones - AZ), ví dụ AZ A (us-east-1a) và AZ B (us-east-1b). Mỗi AZ là một trung tâm dữ liệu độc lập với nguồn điện và mạng riêng, giúp giảm nguy cơ tất cả cùng hỏng một lúc. Bạn xây ứng dụng trong một Virtual Private Cloud (VPC) – như một khu đất riêng trong vùng, nơi bạn đặt các mạng con (subnets) (như các con phố) trong từng AZ, cùng các thành phần như VPC router (định tuyến nội bộ) và Internet Gateway (cửa ngõ ra internet).

- VPC và các cổng: VPC, VPC router và Internet Gateway được thiết kế để bền ở mức vùng. Nghĩa là chúng chỉ ngừng hoạt động nếu toàn bộ vùng hỏng – điều rất hiếm xảy ra (như một trận động đất lớn ảnh hưởng cả thành phố). Nếu chỉ một AZ hỏng (ví dụ, mất điện ở us-east-1a), các thành phần này vẫn hoạt động bình thường ở các AZ khác (như us-east-1b).
- Mạng con: Mỗi mạng con chỉ nằm trong một AZ. Ví dụ, nếu bạn tạo subnet 10.0.1.0/24 ở us-east-1a, nó chỉ thuộc AZ đó. Nếu AZ A hỏng, subnet và mọi tài nguyên trong đó (như máy chủ EC2) cũng không hoạt động.

- Giải pháp: Để ứng dụng như Cartogram không bị gián đoạn khi một AZ hỏng, sử dụng Application Load Balancer (ALB) hoặc Network Load Balancer (NLB), gọi chung là Elastic Load Balancer (ELB). ALB giống như một ngã tư thông minh, phân phối lưu lượng người dùng đến các máy chủ EC2 trong nhiều subnet/AZ. Khi cấu hình ALB trong AWS Console (EC2 > Load Balancers > Create Load Balancer), bạn chọn ít nhất hai subnet ở hai AZ khác nhau. ALB sẽ triển khai các node trong các subnet này, đảm bảo nếu AZ A hỏng, lưu lượng tự động chuyển sang AZ B. Người dùng chỉ gặp vấn đề nếu cả vùng (tất cả AZ) hỏng – một kịch bản rất khó xảy ra.
- Thực hành thực tế:

+ Trong AWS Console, vào VPC > Create VPC, đặt CIDR là 10.0.0.0/16, tên là CartogramVPC.
+ Tạo hai subnet: một ở us-east-1a (10.0.1.0/24) và một ở us-east-1b (10.0.2.0/24).
+ Chạy hai EC2 instance (t2.micro, dùng Amazon Linux 2 AMI) trong hai subnet này, cài web server đơn giản (như Nginx).
+ Tạo ALB (EC2 > Load Balancers > Create > Application Load Balancer), chọn cả hai subnet, thêm target group với hai EC2 instance.
+ Truy cập ALB DNS name trong trình duyệt. Dừng một EC2 instance trong us-east-1a; bạn sẽ thấy ALB tự động chuyển lưu lượng sang instance ở us-east-1b.

- Truy cập riêng tư vào dịch vụ công cộng: Nếu ứng dụng cần kết nối với dịch vụ như S3 mà không qua internet công cộng, bạn tạo VPC Interface Endpoints (VPC > Endpoints > Create Endpoint). Ví dụ, chọn dịch vụ com.amazonaws.us-east-1.s3 và liên kết với một subnet. Tuy nhiên, endpoint gắn với subnet, nên nếu AZ chứa subnet đó hỏng, endpoint cũng hỏng. Cách - khắc phục: Tạo endpoint ở mỗi AZ (ví dụ, một ở us-east-1a, một ở us-east-1b). Điều này đảm bảo ứng dụng vẫn kết nối được với S3 dù một AZ gặp sự cố.
- Ví dụ thực tế: Cartogram cần đọc file từ S3. Tạo hai endpoint S3 trong hai subnet. Nếu us-east-1a hỏng, endpoint ở us-east-1b vẫn hoạt động, giữ ứng dụng online.
## 1.2. Độ Bền Toàn Cầu (Qua Nhiều Vùng)
Tổng quan: Các vùng AWS (như us-east-1, eu-west-1, ap-southeast-2) là độc lập, như các thành phố cách xa nhau. Một ALB chỉ hoạt động trong một vùng, không thể gửi lưu lượng đến vùng khác. Điều này tạo ra các miền lỗi (fault domains) riêng biệt, giới hạn phạm vi ảnh hưởng (blast radius) nếu một vùng hỏng (như ap-southeast-2 gặp sự cố lớn).
Giải pháp: Sử dụng Amazon Route 53, một dịch vụ DNS toàn cầu, như một "hệ thống GPS" dẫn người dùng đến vùng đang hoạt động. Với Cartogram, bạn tạo một tên miền (như cartogram.com) trong Route 53 (Route 53 > Hosted Zones > Create Hosted Zone). Tên miền này trỏ đến các ALB ở nhiều vùng (ví dụ, một ALB ở us-east-1, một ở eu-west-1). Route 53 dùng health checks để kiểm tra xem ALB nào còn hoạt động. Nếu một vùng hỏng, Route 53 tự động chuyển lưu lượng sang vùng khác, đảm bảo người dùng không bị gián đoạn.
Thực hành thực tế:

Tạo một hosted zone trong Route 53 cho cartogram.com.
Thêm A record với latency-based routing hoặc failover routing, trỏ đến ALB ở us-east-1 và một ALB khác ở ap-southeast-2.
Cấu hình health checks (Route 53 > Health Checks) để kiểm tra trạng thái HTTP của ALB (ví dụ, kiểm tra path /health trả mã 200).
Mô phỏng sự cố bằng cách dừng ALB ở ap-southeast-2; kiểm tra xem Route 53 có chuyển lưu lượng sang us-east-1 không (dùng dig cartogram.com hoặc trình duyệt).

Bổ sung: Nếu ứng dụng cần liên kết VPC giữa các vùng (ví dụ, để EC2 ở us-east-1 giao tiếp với cơ sở dữ liệu ở eu-west-1), sử dụng AWS Transit Gateway (VPC > Transit Gateways > Create). Tuy nhiên, độ bền cốt lõi vẫn dựa vào sự cô lập vùng và định tuyến Route 53.
Tóm tắt: Ở mức cục bộ, dùng ALB để phân phối lưu lượng qua nhiều AZ. Ở mức toàn cầu, dùng Route 53 để chuyển hướng đến vùng hoạt động. Điều này giúp ứng dụng như Cartogram luôn online, từ sự cố nhỏ (AZ hỏng) đến lớn (vùng hỏng).

## 2. Độ Bền Lưu Trữ trong AWS - Storage Resilience
Lưu trữ trong AWS giống như các kho hàng, mỗi loại có mức độ bảo vệ khác nhau trước sự cố. Phần này giải thích cách các dịch vụ lưu trữ phản ứng với thất bại ở cấp độ máy chủ EC2, AZ hoặc vùng, sử dụng hai vùng ví dụ: us-east-1 và ap-southeast-2.
## 2.1. Các Loại Lưu Trữ và Độ Bền


Instance Store Volumes: Đây là lưu trữ tạm thời gắn trực tiếp với máy chủ vật lý của EC2 instance trong một AZ, như ổ SSD trong laptop của bạn. Nó nhanh nhưng cực kỳ dễ mất dữ liệu. Nếu ổ đĩa vật lý hỏng, máy chủ hỏng, hoặc AZ hỏng, dữ liệu biến mất. Không dùng cho dữ liệu quan trọng như cơ sở dữ liệu hay file khách hàng; chỉ dùng cho cache tạm thời hoặc dữ liệu có thể tái tạo.
- Ví dụ thực tế: Khi chọn EC2 instance type trong Console (EC2 > Instances > Launch Instance), một số loại như c5d cung cấp instance store. Nếu bạn lưu log tạm ở đây và AZ hỏng, log mất hết.


- Elastic Block Store (EBS): EBS là ổ cứng ảo cho EC2, như USB gắn ngoài. Khi tạo volume (EC2 > Volumes > Create Volume), bạn chọn AZ (như us-east-1a). Dữ liệu được sao chép giữa nhiều ổ đĩa vật lý trong AZ đó, nên chịu được hỏng ổ nhỏ. Nhưng nếu AZ hỏng, volume không truy cập được. EBS không thể trải rộng qua nhiều AZ hay vùng.
- Thực hành thực tế: Tạo EBS volume 10GB ở us-east-1a, gắn vào EC2 instance. Lưu file quan trọng (như config app). Tạo snapshot (EC2 > Volumes > Actions > Create Snapshot). Nếu us-east-1a hỏng, volume mất, nhưng snapshot an toàn trong S3.


- Simple Storage Service (S3): S3 là kho lưu trữ lớn, như Google Drive của AWS. Mặc định, dữ liệu được sao chép qua nhiều AZ trong vùng, nên chỉ hỏng nếu cả vùng down. Bạn có thể lưu EBS snapshot vào S3 để tăng độ bền (vì snapshot kế thừa độ bền của S3). S3 có nhiều lớp lưu trữ:

- Standard: Sao chép qua nhiều AZ, cực kỳ bền.
One Zone-IA: Chỉ ở một AZ, rẻ hơn nhưng rủi ro nếu AZ hỏng. Chỉ dùng cho dữ liệu không quá quan trọng.

- Thực hành thực tế: Upload file vào bucket S3 (S3 > Buckets > Create Bucket). Tạo snapshot EBS và lưu vào S3. Thử xóa volume gốc và khôi phục từ snapshot (S3 > Objects > Actions > Restore).


- Elastic File System (EFS): EFS giống như ổ mạng chia sẻ cho Linux instance, như Dropbox cho server. Khi tạo EFS (EFS > File Systems > Create), nó tự động sao chép qua tất cả AZ trong vùng, chịu được AZ hỏng. Chỉ vùng hỏng mới ảnh hưởng EFS.
- Thực hành thực tế: Tạo EFS ở us-east-1, gắn vào hai EC2 instance ở us-east-1a và us-east-1b (dùng CLI: sudo mount -t efs fs-12345678:/ /mnt/efs). Lưu file ở EFS; dừng instance ở us-east-1a, file vẫn truy cập được từ us-east-1b.


## 2.2. Độ Bền Toàn Cầu
Để bảo vệ dữ liệu trước sự cố vùng, sao chép dữ liệu giữa vùng. Với S3, dùng Cross-Region Replication (CRR) (S3 > Buckets > Management > Replication Rules) để copy bucket từ us-east-1 sang ap-southeast-2. Ví dụ, copy EBS snapshot từ us-east-1 sang ap-southeast-2, rồi khôi phục thành EBS volume mới và gắn vào EC2 instance ở vùng đó.
Thực hành thực tế:

Tạo bucket S3 ở us-east-1 (cartogram-data) và ap-southeast-2 (cartogram-data-backup).
Cấu hình CRR để tự động copy object từ bucket nguồn sang đích.
Upload EBS snapshot vào cartogram-data. Kiểm tra xem snapshot xuất hiện trong cartogram-data-backup.
Từ snapshot ở ap-southeast-2, tạo EBS volume và gắn vào EC2 instance (EC2 > Snapshots > Actions > Create Volume).

Bổ sung: AWS Glacier là lưu trữ lưu trữ giá rẻ, bền như S3 nhưng lấy dữ liệu chậm hơn (vài giờ). Dùng Glacier cho backup dài hạn bằng cách cấu hình lifecycle rule trong S3 (S3 > Management > Lifecycle Rules) để chuyển object sang Glacier sau X ngày.
Tóm tắt: Instance store cực kỳ rủi ro, chỉ dùng tạm thời. EBS tốt cho EC2 nhưng cần snapshot vào S3 để tăng độ bền. S3 và EFS bền ở mức vùng, phù hợp cho dữ liệu quan trọng. CRR giúp bảo vệ trước sự cố vùng. Hiểu rõ để chọn đúng loại lưu trữ khi thiết kế hệ thống hoặc trả lời câu hỏi thi.

## 3. Độ Bền Tính Toán trong AWS - Compute Resilience
Tính toán là "động cơ" chạy ứng dụng, như máy chủ EC2 hoặc hàm Lambda. Phần này tập trung vào độ bền trong một vùng (us-east-1), vì không có dịch vụ tính toán toàn cầu thực sự. Độ bền toàn cầu đạt được bằng cách sao chép hệ thống qua nhiều vùng và dùng Route 53 (đã đề cập ở phần mạng).
## 3.1. Các Dịch Vụ Tính Toán và Độ Bền


EC2 (Elastic Compute Cloud): Một instance EC2 chạy trên một máy chủ vật lý trong một AZ, dùng EBS volume làm lưu trữ. Nếu máy chủ hỏng (do lỗi phần cứng hoặc bảo trì), instance dừng. Bạn có thể khởi động lại trên máy chủ khác trong cùng AZ, và EBS (là ổ ngoài) gắn lại mà không mất dữ liệu. Nhưng nếu AZ hỏng, cả instance và EBS đều không truy cập được.
Giải pháp: Dùng Auto Scaling Group (ASG) để chạy instance trên nhiều AZ. ASG giống như đội ngũ dự phòng: nếu instance ở us-east-1a hỏng, ASG tạo instance mới ở us-east-1b dùng AMI và template đã định nghĩa. Lưu ý: Đây không phải di chuyển instance mà là tạo mới.
Thực hành thực tế:

Tạo AMI từ EC2 instance (EC2 > Instances > Actions > Create Image).
Tạo launch template (EC2 > Launch Templates > Create) với AMI, t2.micro, và subnets ở us-east-1a, us-east-1b.
Tạo ASG (EC2 > Auto Scaling Groups > Create) với min=2, max=4, chọn cả hai subnets.
Dừng instance ở us-east-1a; kiểm tra xem ASG có tạo instance mới ở us-east-1b không (EC2 > Instances).



Elastic Container Service (ECS): ECS chạy container (như Docker). Có hai chế độ:

EC2 mode: Container chạy trên EC2 instance, nên kế thừa rủi ro của EC2 – máy chủ hoặc AZ hỏng thì container hỏng.
Fargate mode: Serverless, AWS quản lý máy chủ. Container gắn vào subnet qua Elastic Network Interface (ENI), nên vẫn phụ thuộc AZ. Nếu AZ hỏng, container không hoạt động.

Giải pháp: Cấu hình ECS service (ECS > Clusters > Services > Create) để chạy task trên nhiều AZ. Nếu us-east-1a hỏng, ECS tạo task mới ở us-east-1b.
Thực hành thực tế: Tạo ECS cluster với Fargate, chọn subnets ở us-east-1a và us-east-1b. Tạo service với 2 task. Dùng CLI kiểm tra task placement (aws ecs list-tasks --cluster my-cluster).


Lambda: Lambda là serverless, không cần lo máy chủ. Mặc định chạy ở không gian công cộng AWS, chỉ hỏng nếu cả vùng down. Ở chế độ VPC (gắn subnet), Lambda dùng ENI nhưng dễ chuyển sang AZ khác nếu một AZ hỏng. Vì Lambda stateless (mỗi lần chạy độc lập), nó rất bền.
Thực hành thực tế: Tạo Lambda function (Lambda > Functions > Create) để xử lý S3 event (như file upload). Chọn không dùng VPC để tối đa resilience. Upload file vào S3 bucket, kiểm tra log Lambda trong CloudWatch (CloudWatch > Logs).


## 3.2. Độ Bền Toàn Cầu
Không có dịch vụ tính toán toàn cầu, nên bạn sao chép kiến trúc EC2/ECS/Lambda sang nhiều vùng (như us-east-1 và ap-southeast-2). Dùng Route 53 để phân phối lưu lượng đến vùng hoạt động, như đã mô tả ở phần mạng.
- Bổ sung: AWS Batch dùng cho xử lý hàng loạt, dựa trên EC2 hoặc Fargate, kế thừa độ bền của chúng. Cấu hình Batch environment (Batch > Compute Environments) với subnets ở nhiều AZ để tăng resilience.
- Tóm tắt: EC2 và ECS cần multi-AZ qua ASG hoặc service config để chịu AZ hỏng. Lambda tự nhiên bền, chỉ cần lo vùng hỏng. Sao chép qua vùng và dùng Route 53 để đạt DR toàn cầu.

- Kết Luận
Để xây dựng hệ thống AWS bền vững:

+ Mạng: Dùng ALB để phân tải multi-AZ và Route 53 để failover multi-region.
+ Lưu trữ: Tránh instance store cho dữ liệu quan trọng; dùng EBS với snapshot S3, S3/EFS cho độ bền vùng, và CRR cho bảo vệ toàn cầu.
+ Tính toán: Dùng ASG cho EC2, multi-AZ service cho ECS, và Lambda cho resilience cao. Sao chép qua vùng cho DR.

- Thực hành đề xuất:

+ Tạo VPC với 2 subnet, chạy EC2, cấu hình ALB và Route 53 như trên.
+ Tạo EBS volume, snapshot vào S3, thử CRR sang vùng khác.
+ Triển khai Lambda function và ECS service, kiểm tra multi-AZ behavior.
