# Rados Gateway (RGW)
Rados Gateway (RGW) là một thành phần quan trọng của Ceph Storage Cluster, cung cấp giao diện RESTful tương thích hoàn toàn với Amazon S3 và OpenStack Swift. RGW là giải pháp lý tưởng cho việc lưu trữ dữ liệu phi cấu trúc, media, backup, cloud-native applications và đặc biệt là multi-site replication. RGW sử dụng librgw kết hợp với librados để cho phép ứng dụng kết nối trực tiếp với Ceph cluster. Nó cung cấp ba loại interface chính: S3 compatibility, Swift compatibility và Admin API. Nhờ kiến trúc true object-based storage, RGW không cần filesystem hay block layer trung gian.



## Triển khai cụm RADOS Gateway (RGW) 
RADOS Gateway (RGW) là một thành phần quan trọng của Ceph, cung cấp giao diện Object Storage tương thích với S3 và Swift. Việc triển khai RGW yêu cầu kế hoạch cẩn thận về tài nguyên và cấu hình để đảm bảo hiệu suất và khả năng mở rộng.

### Quy trình tổng quan 
1. Cài đặt RGW
2. Cấu hình RGW
3. Kết nối đến Keystone 
4. Thiết lập Policy 
5. Kết nối các service khác ( glance , cinder backups)

### 1. Cài đặt RGW
```bash
# Đảm bảo ceph-common đã được cài đặt trước đó
sudo apt update
sudo apt install ceph-common radosgw

sudo ceph auth get-or-create client.${RGW_INSTANCE_NAME} osd 'allow rwx' mon 'allow rw' -o /etc/ceph/ceph.client.${RGW_INSTANCE_NAME}.keyring
# Set the right permissions
sudo chown ceph:ceph /etc/ceph/ceph.client.${RGW_INSTANCE_NAME}.keyring
sudo chmod 640 /etc/ceph/ceph.client.${RGW_INSTANCE_NAME}.keyring
```

### 2. Cấu hình RGW ( `ceph.conf`)
```bash
# /etc/ceph/ceph.conf
[client.${RGW_INSTANCE_NAME}]
host = ${HOSTNAME}  # Or the specific hostname where this instance runs
keyring = /etc/ceph/ceph.client.${RGW_INSTANCE_NAME}.keyring
rgw_frontends = "beast endpoint=0.0.0.0:7480" # Beast frontend listening on port 7480 (HTTP)
# For production, consider using HTTPS: "beast endpoint=0.0.0.0:7443 ssl_certificate=/path/to/cert.pem ssl_private_key=/path/to/key.pem"
rgw_data = /var/lib/ceph/radosgw/ceph-${RGW_INSTANCE_NAME} # Optional: Where RGW keeps its data
log_file = /var/log/ceph/ceph-rgw-${RGW_INSTANCE_NAME}.log


# Keystone settings 

```
- `rgw_frontends`: Cấu hình giao diện frontend cho RGW. Trong ví dụ này, RGW sẽ lắng nghe trên tất cả các địa chỉ IP của máy chủ tại cổng 7480 sử dụng giao thức HTTP. Đối với môi trường sản xuất, nên sử dụng HTTPS để bảo mật giao tiếp.
- `rgw_data`: Tùy chọn chỉ định nơi RGW lưu trữ dữ liệu tạm thời và metadata. Mặc định, RGW sẽ lưu trữ dữ liệu này trong thư mục `/var/lib/ceph/radosgw/ceph-${RGW_INSTANCE_NAME}`.
- `log_file`: Chỉ định nơi lưu trữ log của RGW để dễ dàng theo dõi và gỡ lỗi.
- ${HOSTNAME} cần đảm bảo rằng nó là hostname thực sự của server chạy RGW , khớp với ${RGW_INSTANCE_NAME} bạn dùng để tạo keyring ở bước 1.

- Khởi động RGW service
```bash
sudo systemctl enable ceph-radosgw@${RGW_INSTANCE_NAME}
sudo systemctl start ceph-radosgw@${RGW_INSTANCE_NAME}
# Check if it's running
sudo systemctl status ceph-radosgw@${RGW_INSTANCE_NAME}
sudo ceph -s # Check overall Ceph cluster health, look for RGW status
```

### 3. Kết nối đến Keystone
Để tích hợp RGW với OpenStack Keystone, bạn cần tạo một service user trong Keystone và cấp quyền phù hợp. Dưới đây là các bước cơ bản:

- Tạo Keystone service và endpoint
```bash
# We'll use the 'swift' service type so it works well with Swift tools
openstack service create --name swift --description "OpenStack Object Storage (Ceph RGW)" object-store

openstack endpoint create --region RegionOne object-store public ${RGW_PUBLIC_URL}/swift/v1

# You might also want internal/admin URLs depending on your network
openstack endpoint create --region RegionOne object-store internal ${RGW_INTERNAL_URL}/swift/v1

openstack endpoint create --region RegionOne object-store admin ${RGW_ADMIN_URL}/swift/v1

# You could also register it with the 's3' type if you prefer
# openstack service create --name s3 --description "S3 Object Storage (Ceph RGW)" s3
# openstack endpoint create --region RegionOne s3 public ${RGW_PUBLIC_URL}
```

- Cấu hình RGW cho Keystone Authentication : Chỉnh sửa cài đặt RGW trong `/etc/ceph/ceph.conf` để thêm phần cấu hình Keystone Authentication. Ví dụ:
```bash
[client.${RGW_INSTANCE_NAME}]
# ... other settings from above ...

# Keystone Settings
rgw_keystone_url = http://keystone.example.com:5000 # Address of your Keystone Admin endpoint
rgw_keystone_api_version = 3
rgw_keystone_accepted_roles = member, _member_, admin # Which OpenStack roles can use RGW?
rgw_keystone_token_cache_size = 500 # How many tokens RGW should remember (cache)
rgw_keystone_revocation_interval = 600 # How often RGW checks if tokens were cancelled (seconds)
rgw_keystone_implicit_tenants = true # Automatically maps Keystone projects to RGW tenants (Recommended)

# RGW needs to talk to Keystone to check user tokens. It needs credentials for this.
# !! Security Warning: Don't put passwords directly in ceph.conf if you can avoid it !!
# Option 1: Dedicated OpenStack User (Better Security)
# Create a user in OpenStack (like 'rgw-checker') in a project (like 'service')
# Give it a role that can validate tokens (like 'service' or 'admin').
rgw_keystone_admin_user = rgw-checker
rgw_keystone_admin_project = service
rgw_keystone_admin_password = YOUR_RGW_KEYSTONE_USER_PASSWORD # Keep this password safe! Use Ceph secrets or a protected file if possible.

# Option 2 (Not Ideal): Use the main admin user
# rgw_keystone_admin_user = admin
# rgw_keystone_admin_project = admin
# rgw_keystone_admin_password = YOUR_ADMIN_PASSWORD
```
- **Lưu ý về bảo mật :** Việc đặt password trực tiếp vào file plain text khá rủi ro . Nên xem xét lưu trữ password ở trong các file độc lập (`rgw_keystone_admin_password_file=/path/to/secure/file`) hoặc sử dụng Ceph secrets để bảo vệ thông tin nhạy cảm này.
    - rgw_keystone_accepted_roles : Đây là danh sách các vai trò (roles) trong OpenStack mà RGW sẽ chấp nhận để xác thực người dùng. Thông thường, bạn sẽ muốn bao gồm các vai trò như `member`, `_member_`, và `admin` để đảm bảo rằng người dùng có quyền truy cập phù hợp vào RGW.
    - rgw_keystone_implicit_tenants : Khi được bật, RGW sẽ tự động ánh xạ các dự án (tenants) trong Keystone thành các tenants trong RGW. Điều này giúp đơn giản hóa việc quản lý người dùng và quyền truy cập, vì bạn không cần phải tạo tenants riêng biệt trong RGW cho mỗi dự án trong Keystone.
- Sau khi cấu hình xong, khởi động lại RGW để áp dụng các thay đổi:
```bash
sudo systemctl restart ceph-radosgw@${RGW_INSTANCE_NAME}
```

### 4. Thiết lập Policy
- Để kiểm soát quyền truy cập vào RGW, bạn có thể thiết lập các policy trong Keystone. Ví dụ, bạn có thể tạo một role mới (như `object-store-user`) và gán nó cho các người dùng cần truy cập RGW. Sau đó, bạn có thể cấu hình RGW để chỉ chấp nhận các token từ những người dùng có role này.
Ví dụ:
```bash
openstack role create object-store-user
openstack role add --project demo --user demo object-store-user
```

- Bạn cũng có thể kiểm soát quota và giới hạn bằng cách chỉnh sửa file `ceph.conf`
```bash
[client.${RGW_INSTANCE_NAME}]
# ... các cài đặt khác ...
rgw_user_quota_bucket_sync_interval = 180               # Thời gian giữa mỗi lần RGW đồng bộ thông tin quota của người dùng với bucket (seconds)
rgw_user_quota_sync_interval = 600         # Thời gian giữa mỗi lần RGW cập nhật tổng quota người dùng (giây)
rgw_bucket_quota_ttl = 600                 # Thời gian RGW lưu trữ thông tin quota bucket (giây)
# Bạn có thể cài đặt mặc định cho toàn cụm - global (optional):
# rgw_max_put_size = 5368709120           # Example: 5 GiB max object size
# rgw_bucket_default_quota_max_objects = 1000000 # Ví dụ mặc định số lượng object tối đa mỗi bucket nhưng thường là không đặt trên prod 
# rgw_bucket_default_quota_max_size = 1099511627776 # Ví dụ dung lượng mặc định mỗi bucket (1 TiB)
```

- Cài quota trực tiếp cho người dùng hoặc bucket cụ thể với `radosgw-admin`:
```bash
# Set quota for a specific user (using their Keystone Project ID)
# Limit their total storage to 1 TB and 2 million objects across all their buckets
radosgw-admin quota set --quota-scope=user --uid='{KEYSTONE_PROJECT_ID}' --max-size=1T --max-objects=2000000
radosgw-admin quota enable --quota-scope=user --uid='{KEYSTONE_PROJECT_ID}' # Turn the quota on

# Set quota for just one specific bucket owned by that user
# Limit this bucket to 100,000 objects
radosgw-admin quota set --quota-scope=bucket --bucket='{BUCKET_NAME}' --max-objects=100000 --uid='{KEYSTONE_PROJECT_ID}'
radosgw-admin quota enable --quota-scope=bucket --bucket='{BUCKET_NAME}' --uid='{KEYSTONE_PROJECT_ID}'

# See the current quotas
radosgw-admin quota get --quota-scope=user --uid='{KEYSTONE_PROJECT_ID}'
radosgw-admin quota get --quota-scope=bucket --bucket='{BUCKET_NAME}' --uid='{KEYSTONE_PROJECT_ID}'
```


- Kiểm tra mức độ sử dụng cho từng người dùng ( projectID) :
```bash
# Tổng quan mức độ sử dụng 
radosgw-admin usage show --uid='{KEYSTONE_PROJECT_ID}'

# Mức độ sử dụng chi tiết cho một khoảng thời gian cực kỳ cụ thể (ví dụ: từ 1 tháng trước đến bây giờ)
radosgw-admin usage show --uid='{KEYSTONE_PROJECT_ID}' --start-date='2024-01-01T00:00:00Z' --end-date='2024-12-31T23:59:59Z'
```

### 5. Kết nối các service khác ( glance , cinder backups)
#### 5.1 Glance
- Để tích hợp RGW với Glance (dịch vụ quản lý image của OpenStack), bạn cần cấu hình Glance để sử dụng RGW làm backend lưu trữ cho images. Điều này thường được thực hiện bằng cách chỉnh sửa file cấu hình của Glance (`glance-api.conf`) để chỉ định RGW là backend cho images.

- Tạo 1 glance bucket
```bash
radosgw-admin bucket create --bucket=glance --uid='{GLANCE_SERVICE_PROJECT_ID}'
## Nên đặt quyền hạn ACLs phù hợp phụ thuộc vào cài đặt
```

- Cấu hình file glance-api.conf:
```bash
[glance_store]
stores = swift, http, file  # Add 'swift' to the list of storage options
default_store = swift      # Make RGW (via Swift API) the default place to store images
swift_store_auth_version = 3
swift_store_auth_address = http://keystone.example.com:5000/v3 # Your Keystone v3 address
swift_store_user = service:glance # Format: {project_name}:{user_name} OR {project_id}:{user_id}
swift_store_key = YOUR_GLANCE_SERVICE_PASSWORD
swift_store_container = glance # The bucket name we just created
swift_store_create_container_on_put = false # Good idea to create the bucket beforehand
# swift_store_endpoint_type = publicURL # Or internalURL, adminURL - depends on your network

# Glance Image Cache Settings (Optional but helpful)
# Check your Glance version docs for where these go ([DEFAULT] or [glance_store])
image_cache_dir = /var/lib/glance/image-cache/
image_cache_stall_time = 86400 # 1 day
image_cache_max_size = 10737418240 # 10 GiB
```

> Đảm bảo rằng bạn có một user trong Keystone (ví dụ: `service:glance`) với quyền truy cập vào RGW và rằng bạn đã tạo bucket `glance` trong RGW để lưu trữ images. Đồng thời user này cũng cần một quyền hạn ( ví dụ như admin hay service ) để có thể xác thực và sử dụng RGW thông qua Keystone.

- Sau khi cấu hình xong, khởi động lại dịch vụ Glance để áp dụng các thay đổi:
```bash
sudo systemctl restart glance-api
sudo systemctl restart openstack-glance-registry # Nếu bạn đang sử dụng registry, nếu không thì chỉ cần restart glance-api
```

#### 5.2 Cinder Backups
- Tương tự như Glance, bạn có thể cấu hình Cinder để sử dụng RGW làm backend lưu trữ cho các bản backup của volume. Điều này được thực hiện bằng cách chỉnh sửa file cấu hình của Cinder (`cinder.conf`) để chỉ định RGW là backend cho backups.

- Cấu hình file cinder.conf:
```bash
# Tạo bucket trước 
radosgw-admin bucket create --bucket=cinder-backups --uid='{CINDER_SERVICE_PROJECT_ID}'


# /etc/cinder/cinder.conf
[DEFAULT]
backup_driver = cinder.backup.drivers.swift.SwiftBackupDriver
backup_swift_url = ${RGW_PUBLIC_URL}/swift/v1 # Your RGW Swift endpoint address
backup_swift_auth_url = http://keystone.example.com:5000/v3
backup_swift_user = service:cinder # Format: {project_name}:{user_name}
backup_swift_key = YOUR_CINDER_SERVICE_PASSWORD
backup_swift_container = cinder-backups
backup_swift_auth_version = 3
# backup_swift_endpoint_type = publicURL # Or internalURL
backup_swift_create_container_on_put = false

# Khởi động lại 
sudo systemctl restart openstack-cinder-backup # Tên service có thể khác tùy vào distro và cách bạn cài đặt Cinder
sudo systemctl restart openstack-cinder-volume
# Kiểm tra logs của Cinder Backup để đảm bảo rằng nó có thể kết nối và sử dụng RGW làm backend cho backups
```

#### 5.3 Cấu hình Nova Ephemeral Storage sử dụng RBD chứ không phải RGW(Optional)
- Đầu tiên phải đảm bảo đã tạo pool RBD riêng : ví dụ như pool Ceph cho VM ( như `vms`)
```bash
sudo ceph osd pool create vms 64 64 # Điều chỉnh số lượng PGs phù hợp với kích thước cluster của bạn
sudo rbd pool init vms
```
- Cấu hình file nova.conf để sử dụng RBD pool này cho ephemeral storage thay vì RGW:
```bash
# /etc/nova/nova.conf
[libvirt]
images_type = rbd
images_rbd_pool = vms
images_rbd_ceph_conf = /etc/ceph/ceph.conf
# If using Ceph authentication (recommended):
images_rbd_ceph_user = cinder # Or maybe a specific 'nova' user
images_rbd_ceph_secret_uuid = ${UUID_of_secret_in_libvirt} # Needs setup in libvirt
rbd_user = cinder # Same user as above
rbd_secret_uuid = ${UUID_of_secret_in_libvirt}
```
- Phần này cần thêm 1 bước là phải tạo Ceph credentials cho Nova/Cinder ( ví dụ như client.cinder hay client.nova) và yêu cầu libvirt sử dụng chúng qua secret. Đây là một bước quan trọng để đảm bảo rằng Nova có thể truy cập pool RBD một cách an toàn mà không cần phải đặt password trực tiếp trong file cấu hình.

- Restart dịch vụ Nova sau khi cấu hình xong:
```bash
sudo systemctl restart openstack-nova-compute # Service name might vary
```



## Vận hành RGW
```bash
ceph service dump


radosgw-admin user info --uid TEST_USER
<!-- Example
{
    "user_id": "test_user",
    "display_name": "test_user",
    "email": "",
    "suspended": 0,
    "max_buckets": 1000,
    "subusers": [],  <<-- Any users created and maintained by this user
    "keys": [
        {
            "user": "test_user",
            "access_key": "QEA6PG8VDSJ41JR4C6GZ",  <<-- Random key unique to this user and system
            "secret_key": "SzNCqWwZ7XlGZ1tdtuVdhLTno48ugthx5YwCF6E8" <<-- Random key unique to this user and system
        }
    ],
    "swift_keys": [],
    "caps": [],
    "op_mask": "read, write, delete",
    "default_placement": "",
    "default_storage_class": "",
    "placement_tags": [],
    "bucket_quota": {
        "enabled": false,
        "check_on_raw": false,
        "max_size": -1,
        "max_size_kb": 0,
        "max_objects": -1
    },
    "user_quota": {
        "enabled": false,
        "check_on_raw": false,
        "max_size": -1,
        "max_size_kb": 0,
        "max_objects": -1
    },
    "temp_url_keys": [],
    "type": "rgw",
    "mfa_ids": []
}

-->

radosgw-admin bucket list                           # Liệt kê danh sách các bucket
radosgw-admin bucket rm --bucket-name BUCKET_NAME   # Xóa bucket



```


## RGW Troubleshooting

### Lỗi Đồng Bộ Versioned Objects (Multi-site)
- Mô tả : Khi bạn bật tính năng Versioning (lưu nhiều phiên bản của 1 file) và chạy Multi-site (đồng bộ giữa 2 cụm Ceph).
- Nguyên nhân dự đoán : Một số phiên bản cũ của file ở Site A không được đồng bộ sang Site B, hoặc tệ hơn là Site B ghi đè phiên bản mới lên phiên bản cũ của Site A do sai lệch về timestamp.
- Xử lý : bản Reef, Ceph đã cải thiện rgw_sync_log. Nếu gặp lỗi này ở Pacific/Quincy, bạn cần kiểm tra radosgw-admin sync status và đôi khi phải chạy sync error list để tìm các object bị lỗi và "touch" lại chúng để kích hoạt đồng bộ lại.

### Lỗi "LifeCycle Policy" (LC) Stalls
- Mô tả : Tính năng tự động xóa hoặc chuyển vùng dữ liệu (Tiering) sau một số ngày nhất định.
- Nguyên nhân dự đoán : Khi số lượng object lên tới hàng trăm triệu, tiến trình LC (LifeCycle) có thể bị rơi vào vòng lặp vô tận hoặc bỏ sót các bucket lớn. Đặc biệt ở bản Pacific, LC có thể tiêu tốn 100% CPU của Gateway.
- Cách Xử lý: 
    - Tách biệt các Gateway chuyên dụng chỉ để chạy LC (rgw_enable_lc = true chỉ trên 1-2 node).

    - Ở bản Reef/Squid, sử dụng tính năng lc_sharding để chia nhỏ hàng đợi LC, tránh việc một tiến trình duy nhất bị nghẽn.

### Lỗi Tích Hợp SSE-KMS (Mã hóa dữ liệu với Vault)
- Mô tả: RGW hỗ trợ mã hóa dữ liệu đầu cuối bằng khóa từ HashiCorp Vault.
- Nguyên nhân dự đoán : Khi xoay vòng khóa (Key Rotation) trên Vault, RGW đôi khi không cập nhật kịp thời thông tin khóa mới, dẫn đến việc các Object cũ không thể giải mã được (Lỗi 403 hoặc 500).
- Cách xử lý : Đảm bảo cấu hình rgw_crypt_sse_s3_backend = vault và kiểm tra độ trễ mạng giữa RGW và Vault. Trong các bản Squid, việc quản lý token Vault đã được cải thiện để tự động gia hạn (renew) tránh hết hạn giữa chừng.

### Lỗi Hệ Thống "Account" mới
- Mô tả : Ceph Reef giới thiệu hệ thống Account (tương tự AWS Account) để quản lý nhiều User.
- Nguyên nhân dự đoán : Việc phân quyền IAM Policy trở nên cực kỳ phức tạp. Một sai sót nhỏ trong JSON Policy có thể khiến toàn bộ các User trong Account đó mất quyền truy cập (Access Denied) mà không có log rõ ràng.
- Cách xử lý : Sử dụng công cụ radosgw-admin policy để kiểm tra cú pháp trước khi apply. Luôn giữ lại một User có quyền caps cao nhất nằm ngoài hệ thống Account để cứu hộ.

### Lỗi "Multipart Upload" ETag Mismatch
- Mô tả: Khi upload các file lớn (>5GB) được chia nhỏ thành nhiều phần.

- Nguyên nhân dự đoán : Sau khi kết hợp (Complete Multipart), mã ETag trả về không khớp với mã MD5 của file gốc. Điều này gây lỗi cho các ứng dụng kiểm tra tính toàn vẹn khắt khe.

- Cách Xử lý: Lỗi này chủ yếu do cơ chế nén dữ liệu (compression) của RGW. Nếu độ chính xác của ETag là tiên quyết, hãy tắt nén cho các bucket đó: radosgw-admin bucket encryption get và cấu hình nén về none.


## Lỗi LARGE_OMAP_OBJECTS trong Ceph RGW - S3
- OMAP (Object Map) là phần metadata được lưu trữ dưới dạng Key-Value trong RocksDB của OSD.Khi một object có quá nhiều keys (mặc định > 200,000) hoặc dung lượng quá lớn, các tiến trình như Deep Scrub, Recovery, hoặc Backfill sẽ gây nghẽn I/O, làm chậm phản hồi OSD, thậm chí gây sập OSD (Timeout).

- Thông thường có 3 nhóm nguyên nhân phổ biến gây cảnh báo large omap object: 
1. **Index bucket quá lớn (RGW bucket index)**:
    Khi một bucket có quá nhiều key/entries trong omap index (ví dụ bucket chứa hàng trăm nghìn object/version) → kích thước omap lớn vượt thresholds. Điều này xảy ra thường khi:
    - Bucket chưa reshard tốt hoặc dynamic resharding không kịp. Bucket đang có quá nhiều object/version gây nên một shard chứa quá nhiều entries. Hoặc một nguyên nhân cũng do shards là số lượng shards thấp khiến mỗi shards chứa lượng entries quá lớn .
    - Bucket có rất nhiều phiên bản (versioning) → mỗi phiên bản tạo dấu entry trong omap → dồn vào 1 shard.

> Đây là nguyên nhân phổ biến trên cả single-site và multisite nếu bucket lớn hoặc versioned 

2. **Versioning / multipart / nhiều bản ghi nhỏ liên tục**
Mỗi version/part dữ liệu lại tạo entry metadata → cộng dồn gây đầy

3. **Tombstones / GC chưa chạy**
Xóa/ Tạo markers chưa được thu gom → giữ nhiều key

4. **Stale bucket index trong môi trường multisite**
- Deleted bucket index vẫn còn tồn tại trong stale instances do sync chưa hoàn tất, không bị xóa tự động.
=> Điều này tạo ra một object .dir.<bucketID>… trong pool rgw.buckets.index có omap rất lớn → deep-scrub sẽ cảnh báo.

> Đặc trưng ở RGW Multisite, nhất là khi delete bucket ở 1 site nhưng chưa sync sạch sang site kia.

5. **Sync/log/usage omap lớn (log pool / usage entries)**
Một số trường hợp large omap có thể xảy ra không phải index pool mà ở:
- pool `rgw.log` do sync error logs chưa được trim.
- pool `rgw.usage` chứa usage statistics.
=> Các trường hợp này cũng gọi là large omap nhưng nguyên nhân khác hoàn toàn với index bucket 

### Xác định nguyên nhân
#### Bước 1: Xác đinh các thông tin 
```bash
ceph -s # Trạng thái tổng quan để xác nhận lỗi large omap 
ceph health detail # Xem chi tiết osd bị LARGE OMAP OBJECTS 
grep -i "Large omap object found" /var/log/ceph/ceph.log # Xem thử log

# Map object bị large omap
## nếu object tên chứa bucket-id (.dir.<bucket-id>...), lấy bucket-id
radosgw-admin metadata list --metadata-key bucket.instance | grep <bucket-id>
## hoặc liệt kê bucket instance entries
radosgw-admin metadata list --metadata-key bucket

# bucket stats
radosgw-admin bucket stats --bucket=<bucket-name>
## xem num_objects, size, num_shards, versioning flag

# Đếm keys trong omap object (read)
rados -p <pool-name> listomapkeys <object-name> | wc -l
## hoặc lấy vài dòng đầu để kiểm tra dạng key:
rados -p <pool-name> listomapkeys <object-name> | head -n 20

# Xem PG info 
ceph pg <pgid> query

# Check bilog / reshard queue / sync status
## Multisite 
radosgw-admin sync status và radosgw-admin bucket sync status --bucket=<bucket>.

#Reshard queue 
radosgw-admin reshard list / radosgw-admin reshard status --bucket=<bucket>.
```
Từ đây xác định được :
- Pool nào bị (rgw.buckets.index / rgw.log / rgw.usage)?
- Object name (thường `.dir.<bucket-id>...` cho bucket index) — có thể map về bucket-id? Key count & size lớn cỡ nào?
- PG chứa object (PGID) — để giới hạn scope deep-scrub.
- Kiểm tra xem RGW đang là singlesite hay multisite 

Khi đã xác định được pool type thì có thể giới hạn được vấn đề : 
- Nếu pool là `rgw.buckets.index` → bucket index case. Lỗi do Bucket quá lớn hoặc Versioning quá nhiều. (Chiếm 90% trường hợp).
- Nếu pool là `rgw.log` / `rgw.usage` → xử lý log/usage case. Lỗi do log hệ thống hoặc thống kê sử dụng tích tụ lâu ngày.
- Nếu pool là `rgw.otp` / `rgw.meta` → Lỗi metadata hệ thống

#### Bước 2 : Xử lý theo từng trường hợp 
##### 2.1 CASE A — Bucket index quá lớn (single big bucket)
**Dấu hiệu:** object là `.dir.<id>`, `key count >> threshold` (ví dụ >200k hoặc >1GB tuỳ config), bucket stats cho thấy `num_objects` rất lớn, `num_shards` thấp.
- **Kiểm tra thông tin:** 
```bash
# Lấy ID từ tên object tìm được ở Bước 1 và map ra tên bucket
radosgw-admin metadata get bucket.instance:<id> | grep '"bucket":'

# Kiểm tra chỉ số phân mảnh hiện tại
radosgw-admin bucket stats --bucket=<bucket_name> | grep num_shards
```
- **Các bước xử lý gợi ý:**
    - **Bật/khởi chạy dynamic resharding (nếu chưa bật / phiên bản hỗ trợ):** dynamic sẽ tự phân tách index background. Theo docs, dynamic resharding có từ Luminous trở đi. Giám sát queue.

    - **Reshard thủ công (có thể làm online):** thêm reshard task vào queue hoặc chạy `radosgw-admin bucket reshard --bucket=<bucket> --num-shards=<N>` hoặc `radosgw-admin reshard add ...` rồi `radosgw-admin reshard process`. Đây là thao tác metadata nhưng được thiết kế để thực hiện online (không cần dừng RGW). Chọn số shards hợp lý (thường chọn số lớn / prime numbers). Lưu ý là quá trình này sẽ khóa (lock) các thao tác ghi vào bucket trong khi thực hiện. Nên khuyến khích thực hiện vào giờ thấp điểm  

    - **Sau resharding:** chạy deep-scrub chỉ PG bị ảnh hưởng (`ceph osd pg deep-scrub <pgid>`) để clear health warning.

> **Rủi ro / lưu ý:** resharding tạo I/O background; manual reshard vẫn là thay đổi metadata — test trên staging nếu lần đầu. Khi resharding hoàn tất có thể cần chạy `radosgw-admin lc reshard fix` nếu lifecycle policies bị ảnh hưởng (các phiên bản cũ hơn cần)

##### 2.2 CASE B — Tombstones / GC chưa chạy (single-site)
- **Dấu hiệu:** bucket stats cho thấy num_objects nhỏ, nhưng listomapkeys lại trả về con số khổng lồ. Đây là các "dấu vết" (tombstones) chưa được Garbage Collection (GC) quét sạch.`radosgw-admin gc list` c
- **Thông tin cần check:** 
    - Kiểm tra danh sách GC còn tồn đọng: `radosgw-admin gc list --include-all.`
    - Xem log RGW để tìm các lỗi liên quan đến GC bị nghẽn.
- **Các cách xử lý gợi ý:**
    - Chạy GC/expire policies theo cách an toàn (thực hiện từng bước, giới hạn phạm vi nếu tool cho phép).
    - Tăng tốc độ xử lý GC bằng cách điều chỉnh `rgw_gc_max_objs` và `rgw_gc_processor_period`
    - Chạy thủ công tiến trình dọn dẹp nếu cần (cần cẩn trọng với I/O)
> Rủi ro: GC xóa metadata/data — đảm bảo retention policy và backup trước nếu nhạy cảm.

##### 2.3 CASE C — Phình to Log Pool(rgw.usage / rgw.log)
- **Dấu hiệu:** Cảnh báo Large OMAP xuất hiện ở các pool hệ thống (rgw.usage, rgw.log) thay vì pool index dữ liệu.

- **Thông tin cần check:** l
    - Liệt kê object trong pool bị báo lỗi: rados -p rgw.log ls.
    - Đếm key của các object log bị cảnh báo.

- **Các bước xử lý gợi ý:**
    1. Sử dụng lệnh Trim: ví dụ `radosgw-admin usage trim --start-date=YYYY-MM-DD --end-date=YYYY-MM-DD` hoặc `radosgw-admin bilog trim --bucket=...` để prune logs. Sau đó deep-scrub PG.
        - Với log đồng bộ: radosgw-admin log trim --end-date=...
    2. Throttle trim / chạy theo batches để không spike I/O.
> Rủi ro: Trim thay đổi metadata/history; kiểm tra backup/retention.

##### 2.4 CASE D — Lỗi Logic Multisite (Stale Instances / Sync Stuck)
- **Dấu hiệu:** 
    - bucket-id xuất hiện ở stale instances, `radosgw-admin sync status` cho thấy sync stuck; Red Hat paper đề cập `bilogs not trimmed → large omap`.
    - Object .dir.<id> bị báo lỗi nhưng khi tra cứu ID bằng metadata get thì trả về lỗi 404 (không tồn tại bucket).

- **Thông tin cần check:** 
    - `radosgw-admin metadata list --metadata-key bucket.instance`
    - `radosgw-admin bilog list --bucket=<bucket>`
    - `radosgw-admin sync status`.

- **Các bước xử lý gợi ý:**
    1. Không chạy destructive ngay. Trước hết: check why sync stuck (network, credentials, replication policy).
    2. Nếu chắc chắn stale và quyết định cleanup: **trim bilog** via r`adosgw-admin bilog trim --bucket="..." --bucket-id="..."` (dùng cautiously) — Red Hat khuyến nghị các bước trim & sau đó deep-scrub.
    3. Nếu bạn muốn tránh data loss: tạm disable bucket sync (`radosgw-admin bucket sync disable --bucket=<bucket>`) để ngăn thêm thay đổi cross-site trước khi trim — nhưng thao tác này thay đổi sync state (thực hiện cẩn trọng).
> Rủi ro: trim bilog là thao tác chỉnh sửa metadata; sai thao tác có thể làm mất dữ liệu replication state — test trên staging; ideally thực hiện trên một site duy nhất (cleanup stale instances chỉ làm trên single site cluster).

##### 2.5 CASE E - Artifacts sau Reshard hoặc lỗi do old verison
- **Dấu hiệu:** 
    - Đã reshard nhưng vẫn có large omap; mailing lists cho biết có trường hợp bilogs/retired shards phải remove thủ công.
    - Bucket đã có số Shard mới, dữ liệu đã chia nhỏ, nhưng OSD vẫn báo lỗi ở các tên Object Shard cũ.
- **Các cách xử lý gợi ý:** 
    - kiểm tra changelog/bugfix cho phiên bản Ceph; nếu cần, áp patch/upgrade (lên phiên bản hỗ trợ dynamic reshard fixes) trong maintenance window.
    - Ép hệ thống quét lại metadata: `ceph osd pg deep-scrub <pg_id>` (cần map các bucket lớn đó với các bucket báo lỗi )
        - Nếu Object bị báo lỗi là Shard cũ (đã được thay thế), hãy xóa nó thủ công sau khi kiểm tra kỹ bằng listomapkeys thấy rỗng hoặc dữ liệu đã cũ.


#### Bước 3: Kiểm tra và xác thực 
1. Sau reshard/trim/GC: `ceph health detail` và grep log để kiểm tra message đã biến mất.
2. Chạy `ceph osd pool stats` hoặc `ceph osd df` để xem I/O impact.
3. Kiểm tra RGW bucket stats, và reshard status: `radosgw-admin reshard status --bucket=<bucket>`.

- Kiểm tra và check thông tin 
```bash
grep -i "Large omap object found" /var/log/ceph/ceph.log
rados -p <pool> listomapkeys <object> | wc -l
radosgw-admin metadata list --metadata-key bucket.instance
radosgw-admin bucket stats --bucket=<bucket>
ceph pg <pgid> query
ceph health detail
radosgw-admin sync status
radosgw-admin reshard list
```

- Các lệnh thực thi ( có ảnh hưởng cụm , khuyến nghị test lab hoặc backup trước)
```bash
# Manual immediate reshard (online)
radosgw-admin bucket reshard --bucket=<bucket> --num-shards=<N>
# or schedule and process
radosgw-admin reshard add --bucket=<bucket> --num-shards=<N>
radosgw-admin reshard process
# Trim bilog (multi-site/stale) — rất cẩn trọng
radosgw-admin bilog trim --bucket="<bucket-name>" --bucket-id="<bucket-id>"
# Trim usage (logs)
radosgw-admin usage trim --start-date=YYYY-MM-DD --end-date=YYYY-MM-DD
# Deep-scrub specific PG
ceph osd pg deep-scrub <pgid>
# Disable bucket sync (if needed, impacts replication)
radosgw-admin bucket sync disable --bucket=<bucket>
```