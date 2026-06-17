# Operations
## Nguyên tắc vận hành 
Với RGW, sai lầm phổ biến nhất không phải là gõ sai lệnh, mà là động vào sai tầng. Có lúc bạn nghĩ mình đang xử lý “lỗi object”, nhưng thực ra lại là lỗi user, bucket policy, bucket index, quota, garbage collection hoặc multisite sync. Vì vậy, trước mọi thay đổi, nên tự hỏi trước: tôi đang đụng vào user, bucket, placement, index hay multisite. Nếu không tách được tầng, rất dễ chạy lệnh đúng nhưng xử lý sai vấn đề.

### Các lệnh kiểm tra tổng quan
```bash
ceph -s
ceph health detail
radosgw-admin user info --uid=<uid>
radosgw-admin bucket stats --bucket=<bucket>
```

## Các thao tác với user và khóa truy cập
### Tạo user mới
```bash
radosgw-admin user create --uid=app01 --display-name="Application 01" --email=app01@example.com

# Kiểm tra 
radosgw-admin user info --uid=app01
```


### Sửa user, khóa user, mở khóa user
```bash
radosgw-admin user modify --uid=app01 --display-name="Application 01 - Prod"
radosgw-admin user suspend --uid=app01
radosgw-admin user enable --uid=app01
```

- Khi user được tạo ra sẽ được enable sẵn để sử dụng , có trường hợp tự bị khóa thì phải mở khóa bằng `user enable`. Nếu muốn khóa user thì dùng `user suspend`. Khi user bị khóa sẽ không thể truy cập vào bucket nào của user đó nữa.
- Kiểm tra lại :
```bash
radosgw-admin user info --uid=app01
```

### Xóa user
```bash
radosgw-admin user rm --uid=app01

# Nếu cần dọn cả dữ liệu 
radosgw-admin user rm --uid=app01 --purge-data
## Lưu ý : Mức độ của lệnh này là S1 : có thể ảnh hưởng toàn bộ data của user này nên cần cân nhắc kỹ trước khi chạy
```

## Các thao tác với bucket
### Xem bucket và thống kê bucket
```bash
radosgw-admin bucket stats --bucket=data
radosgw-admin bucket list --uid=app01
```

### Đổi chủ sở hữu bucket
```bash
radosgw-admin bucket link --uid=user2 --bucket=data
radosgw-admin bucket list --uid=user2
radosgw-admin bucket chown --uid=user2 --bucket=data
radosgw-admin bucket list --uid=user2
```
> Với bucket của tenant, cú pháp còn khác thêm vì có tiền tố tenant trong tên bucket và user.
### Quota cho user và bucket
- RGW hỗ trợ quota ở hai phạm vi chính: user quota và bucket quota. Tài liệu Ceph Pacific ghi rất rõ:
    - quota của user: `radosgw-admin quota set --quota-scope=user --uid=<uid> ...`
    - quota của bucket: `radosgw-admin quota set --quota-scope=bucket --uid=<uid> ...`
    Sau khi đặt quota, bạn còn phải bật quota bằng `radosgw-admin quota enable`, nếu không quota chưa có hiệu lực.
```bash
radosgw-admin quota set --quota-scope=user --uid=app01 --max-objects=100000 --max-size=500G
radosgw-admin quota enable --quota-scope=user --uid=app01

radosgw-admin quota set --quota-scope=bucket --uid=app01 --max-objects=50000 --max-size=200G
radosgw-admin quota enable --quota-scope=bucket --uid=app01
```
- Thống kê quota được cập nhật bất đồng bộ vậy nên cập cập nhật lại số liệu bằng lệnh `radosgw-admin user stats --uid=<uid> --sync-stats` trước khi tin vào con số đang thấy . Với môi trường có nhiều RGW instance, quota còn chịu ảnh hưởng bởi cache quota trên từng instance, nên không phải lúc nào cũng “ăn ngay” theo nghĩa tuyệt đối.
    - ví dụ : 
    ```bash
    radosgw-admin user stats --uid=app01 --sync-stats
    radosgw-admin user stats --uid=app01
    ```
### Placement, storage policy và thao tác với dữ liệu bucket
- RGW không lưu bucket và object “vào đâu cũng được”. Tài liệu RHCS 5 nói rõ RGW xác định placement targets rồi mới đặt bucket và object vào các pool gắn với placement đó; nếu bạn không cấu hình placement targets và ánh xạ chúng vào pool trong zone configuration, RGW sẽ dùng default_placement cùng các pool mặc định tương ứng. Điều này có nghĩa thao tác tạo bucket của người dùng và quyết định lưu dữ liệu ở đâu là hai tầng khác nhau.
- Khi vận hành, quan trọng nhất là **đừng coi bucket là pool**. Khi bạn đang điều chỉnh storage policy hoặc placement, bạn đang đụng vào tầng mà RGW dùng để nối bucket logic với pool thật của Ceph. Đây là vùng cần rất cẩn thận vì thay đổi sai có thể làm các bucket mới hoặc object mới đi vào sai nơi lưu trữ.

- Nếu cần kiểm tra bucket đang thế nào về mặt thống kê hoặc layout, hãy bắt đầu bằng:
```bash
radosgw-admin bucket stats --bucket=<bucket>
```

### Bucket index, bucket check và resharding
- Bucket index là một phần cực kỳ quan trọng của RGW. Khi bucket rất lơn, listing nặng hay có số object tăng cao hay nghi index không khỏe thì cần vận hành theo luồng gợi ý sau :
    1. kiểm tra bucket
    2. sao lưu bucket index
    3. reshard
    4. theo dõi lại trạng thái sau resharding.

Ví dụ:
```bash
radosgw-admin bi list --bucket=data > data.list.backup
radosgw-admin bucket reshard --bucket=data --num-shards=100
radosgw-admin bucket stats --bucket=data
```

> Đối với bucket lớn , luôn phải sao lưu bucket index trước khi resharding, vì nếu resharding có vấn đề thì có thể khôi phục lại bằng index backup. Resharding là một thao tác nặng và có thể ảnh hưởng đến hiệu năng, nên cần theo dõi sát sao sau khi thực hiện.

## Garbage collection và thu hồi dung lượng
- RGW có một điểm rất quan trọng về vận hành: xóa object khỏi bucket index và thu hồi hẳn không gian lưu trữ đã dùng không phải lúc nào cũng xảy ra cùng một lúc. RHCS 5 mô tả rất rõ: khi object bị xóa hoặc bị ghi đè, RGW xóa object đó khỏi bucket index trước; sau đó, một thời gian sau mới thu hồi không gian lưu trữ qua garbage collection (GC). Theo mặc định, GC chạy nền liên tục.
- Điều này có nghĩa là sau khi xóa object, bạn có thể thấy nó đã biến mất khỏi bucket index nhưng không gian lưu trữ vẫn chưa được thu hồi ngay. Nếu cần thu hồi nhanh, bạn có thể kích hoạt GC thủ công:
```bash

radosgw-admin gc process

# Kiểm tra hàng đợi gc 
radosgw-admin gc list
```

## Multisite trong vận hành thực tế
- Multisite là vùng vận hành khó hơn hẳn phần user/bucket thường ngày, vì bạn đang đụng vào cấu hình toàn cục của object gateway trên nhiều site. RHCS 8 mô tả rất rõ rằng một cấu hình multisite tối thiểu cần ít nhất hai cụm Ceph storage và ít nhất hai Ceph Object Gateway instances, mỗi bên phục vụ một cụm. Đồng thời, một zonegroup có thể có nhiều zone, và mỗi zone có thể tiếp nhận ghi trong các cấu hình phù hợp.

- Việc nên làm đầu tiên trong multisite operations không phải là sửa zone hay period ngay, mà là xác nhận mình đang đứng ở realm, zonegroup và zone nào. Các lệnh kiểm tra cơ bản nên thuộc lòng là:
```bash
radosgw-admin realm list
radosgw-admin zonegroup list
radosgw-admin zone list
radosgw-admin sync status
```
Lưu ý , rất nhiều thay đổi cấu hình chỉ thật sự thay đổi khi được commit :
```bash
radosgw-admin period update --commit
```