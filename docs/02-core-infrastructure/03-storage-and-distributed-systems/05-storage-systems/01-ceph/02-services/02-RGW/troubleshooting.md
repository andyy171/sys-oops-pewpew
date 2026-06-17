# Troubleshooting RGW 

## Kiểm tra nhanh cơ bản 
```bash
ceph -s
ceph health detail
radosgw-admin user info --uid=<uid>
radosgw-admin bucket stats --bucket=<bucket>
```

## Lỗi xác thực: sai key, user bị khóa, request bị từ chối
- Khi ứng dụng báo kiểu “không xác thực được”, “không dùng được key cũ”, hoặc “trước đây dùng được mà giờ bị từ chối”, hướng nghĩ đầu tiên nên là: user có còn tồn tại không, có bị suspend không, và key hiện tại có đúng là key mà ứng dụng đang dùng không. radosgw-admin hỗ trợ trực tiếp các lệnh user info, user suspend, user enable, key create, key rm, nên đây là nhóm lệnh nên kiểm tra đầu tiên thay vì đoán mù ở phía ứng dụng.

- Các lệnh kiểm tra đầu tiên 
```bash
radosgw-admin user info --uid=<uid>
radosgw-admin user check --uid=<uid>
```
- Nếu usesr đang bị khóa thì cần mở lại :
```bash
radosgw-admin user enable --uid=<uid>
```
- Nếu nghi key cũ đã sai hoặc muốn xoay key, có thể tạo key mới:
```bash
radosgw-admin key create --uid=<uid> --key-type=s3 --gen-secret
```

## Bucket không thấy, owner sai, hoặc user nhìn không đúng bucket của mình
- Kiểm tra lại thông tin bucket, xem bucket có tồn tại không, bucket thuộc user nào, và user có nhìn thấy bucket đó không. Nếu bucket có tồn tại nhưng user không nhìn thấy, có thể do bucket bị link sai owner hoặc do lỗi index. Cần kiểm tra lại thông tin bucket và user để xác định nguyên nhân.
```bash
radosgw-admin bucket stats --bucket=<bucket>
radosgw-admin bucket list --uid=<uid>
radosgw-admin user info --uid=<uid>
```

## Bucket rất lớn, list chậm, hoặc cluster báo large omap objects
- Đây là nhóm lỗi RGW rất điển hình trong thực tế. Ceph health checks nói rất rõ rằng cảnh báo large omap objects có thể do RGW bucket index objects không bật resharding tự động, và khuyến nghị xem thêm phần RGW Dynamic Bucket Index Resharding. Điều này có nghĩa nếu bucket quá lớn hoặc ghi/xóa quá nhiều, bucket index có thể trở thành điểm nóng thật sự của hệ thống.

- Khi gặp triệu chứng kiểu:

    - aws s3 ls hoặc list bucket rất chậm
    - bucket có số object quá lớn
    - cluster log có dòng Large omap object found
    health detail báo large omap objects

- Kiểm tra lại thông tin bucket và index:
```bash
ceph health detail
radosgw-admin bucket stats --bucket=<bucket>
radosgw-admin bucket limit check --bucket=<bucket>
```

- Nếu xác định bucket index quá lớn, có thể đi theo luồng:

    - sao lưu bucket index
    - reshard
    - theo dõi trạng thái reshard

Ví dụ:
```bash
radosgw-admin bi list --bucket=<bucket> > <bucket>.bi.backup
radosgw-admin bucket reshard --bucket=<bucket> --num-shards=<so-shard>
radosgw-admin reshard status --bucket=<bucket>
```

## Bucket index sai, thống kê bucket sai, hoặc nghi có entry mồ côi
- Nếu bucket hiện object lạ, thống kê sai, hoặc sau nhiều lần ghi/xóa bạn nghi bucket index không còn phản ánh đúng object state, lệnh quan trọng nhất là bucket check. Man page của `radosgw-admin` mô tả bucket check là lệnh kiểm tra bucket index; tùy chọn `--fix` sẽ vừa kiểm tra vừa sửa; còn `--check-objects` sẽ dựng lại bucket index theo trạng thái object thật. RHCS 5 còn mô tả rõ hơn: `bucket check --fix` có thể xóa các entry mồ côi khỏi bucket index và ghi đè lại header stats bằng các giá trị vừa tính lại.

- Luồng an toàn thường là:
```bash
radosgw-admin bucket check --bucket=<bucket>
```
- Nếu kết quả cho thấy index có vấn đề hoặc thống kê sai, mới đi tiếp:
```bash
radosgw-admin bucket check --fix --bucket=<bucket>
```
- Nếu bạn nghi object state và index lệch nhau nhiều hơn, có thể cần tới:
```bash
radosgw-admin bucket check --check-objects --bucket=<bucket>
```

## Quota hoặc usage nhìn không khớp với thực tế

- Quota của RGW không phải lúc nào cũng cập nhật tức thời theo cảm giác người vận hành. Man page của radosgw-admin nói rõ user stats là số liệu được hệ quota của RGW ghi nhận, còn tùy chọn --sync-stats sẽ cập nhật user stats bằng số liệu hiện tại báo về từ bucket indexes của user đó. Điều này rất quan trọng: nếu bạn xem quota/usage mà chưa đồng bộ lại thống kê, con số có thể làm bạn hiểu sai tình trạng thật.

- Khi thấy user báo:

    - đã xóa bớt object nhưng quota vẫn như cũ
    - giao diện hiển thị usage lạ
    - bucket usage và user usage có vẻ không ăn khớp

- hãy chạy:
```bash     
radosgw-admin user stats --uid=<uid> --sync-stats
radosgw-admin user stats --uid=<uid>
radosgw-admin bucket stats --bucket=<bucket>
```