
---

## RGW quản lý những gì ? 

RGW nằm trên RADOS và cung cấp giao diện S3/Swift.  
  
Các nhóm cần quản lý:  
  
- RGW daemon/service  
- Realm / Zonegroup / Zone  
- RGW pools  
- User / access key / secret key  
- Bucket  
- Bucket index  
- Quota  
- Usage/log  
- Multisite/sync nếu có  
- Các cảnh báo phổ biến: large omap, bucket index lớn, slow RGW, auth lỗi

---

# Kiểm tra trạng thái RGW

```bash  
ceph -s  
ceph health detail  
  
ceph rgw realm ls  
ceph rgw zonegroup ls  
ceph rgw zone ls  
  
ceph rgw realm get <realm>  
ceph rgw zonegroup get <zonegroup>  
ceph rgw zone get <zone>
```


---
## Kiểm tra RGW daemon
- Nếu sử dụng systemd
```
systemctl status ceph-radosgw@rgw.<name>
systemctl restart ceph-radosgw@rgw.<name>
journalctl -u ceph-radosgw@rgw.<name> -f
```
- Nếu dùng container/cephadm 
```
ceph orch ps --daemon_type rgw
ceph orch restart rgw.<service-name>
```

---
## Quản lý RGW pools
#### Kiểm tra pool liên quan RGW:
```
ceph osd pool ls detail | grep rgw
ceph df detail
rados df
```
#### Kiểm tra application tag:
```
ceph osd pool application get <pool>

# Enable ag nếu thiếu
ceph osd pool application enable <pool> rgw
```
#### Các pool RGW thường gặp:
```
.rgw.root
default.rgw.control
default.rgw.meta
default.rgw.log
default.rgw.buckets.index
default.rgw.buckets.data
default.rgw.buckets.non-ec
```
Trong đó :
- `buckets.data`: chứa object data.
- `buckets.index`: chứa bucket index, dễ sinh large omap.
- `meta/log/control`: nhỏ hơn nhưng quan trọng cho control-plane của RGW.
---
## Quản lý user

List user:
```
radosgw-admin user list
```

Xem user:
```
radosgw-admin user info --uid=<uid>
```

Tạo user:
```
radosgw-admin user create --uid=<uid> --display-name="<display-name>"
```

Tạo key mới:
```
radosgw-admin key create --uid=<uid> --key-type=s3 --gen-access-key --gen-secret
```

Xóa key:
```
radosgw-admin key rm \  --uid=<uid> \  --access-key=<access-key>
```

Suspend user - Tạm dừng sử dụng user :
```
radosgw-admin user suspend --uid=<uid>
```

Enable lại user:
```
radosgw-admin user enable --uid=<uid>
```


---
## ## Quản lý bucket
List bucket:
```
radosgw-admin bucket list
```

Xem thông tin bucket:
```
radosgw-admin bucket stats --bucket=<bucket>
```

Xem bucket gắn với user nào:
```
radosgw-admin bucket stats --bucket=<bucket> | jq '.owner'
```

Link bucket sang user khác:
```
radosgw-admin bucket link --bucket=<bucket> --uid=<uid>
```

Unlink bucket:
```
radosgw-admin bucket unlink --bucket=<bucket> --uid=<uid>
```

Xóa bucket rỗng:
```
radosgw-admin bucket rm --bucket=<bucket>
```

Xóa bucket có object:
```
radosgw-admin bucket rm --bucket=<bucket> --purge-objects
```
> Lưu ý: `--purge-objects` là thao tác phá hủy dữ liệu.
---
## ## Bucket index và large omap
Kiểm tra bucket stats:

```
radosgw-admin bucket stats --bucket=<bucket>
```

Kiểm tra bucket index:

```
radosgw-admin bi list --bucket=<bucket>
```

Check bucket index:

```
radosgw-admin bucket check --bucket=<bucket>
```

Fix bucket index nếu đã xác định lỗi:

```
radosgw-admin bucket check --bucket=<bucket> --fix
```

>Ghi chú vận hành:
>- Large omap thường liên quan `default.rgw.buckets.index`.
>- Cần trace từ health warning → PG → object → bucket index object → bucket.
>- Không repair/fix bừa nếu chưa xác định bucket.
---
## Kiểm soát Quota
Xem quota user:
```
radosgw-admin quota get --uid=<uid>
```
Set quota user:
```
radosgw-admin quota set --uid=<uid> --quota-scope=user --max-size=<size> --max-objects=<count>
```
Enable quota user:
```
radosgw-admin quota enable --uid=<uid> --quota-scope=user
```

Disable quota user:
```
radosgw-admin quota disable --uid=<uid> --quota-scope=user
```

Bucket quota:
```
radosgw-admin quota set --uid=<uid> --quota-scope=bucket --max-size=<size> --max-objects=<count>radosgw-admin quota enable --uid=<uid> --quota-scope=bucket
```

---
## Quản lý Usage/log
Xem usage:
```
radosgw-admin usage show --uid=<uid>
```

Xem usage theo thời gian:
```
radosgw-admin usage show --uid=<uid> --start-date="YYYY-MM-DD HH:MM:SS" -end-date="YYYY-MM-DD HH:MM:SS"
```

Trim usage:
```
radosgw-admin usage trim --uid=<uid> --start-date="YYYY-MM-DD HH:MM:SS" \  --end-date="YYYY-MM-DD HH:MM:SS"
```

---
## Multisite
Check sync status:

```
radosgw-admin sync status
```

Check realm/zone/period:

```
radosgw-admin realm listradosgw-admin zonegroup listradosgw-admin zone listradosgw-admin period get
```

Update period sau thay đổi cấu hình multisite:

```
radosgw-admin period update --commit
```