# Triển khai RGW Service bằng Dashboard


## 1. Baseline check
```bash
ceph -sceph orch ps --daemon-type rgwradosgw-admin realm listradosgw-admin zonegroup listradosgw-admin zone listceph osd pool ls | grep rgw
```

Kỳ vọng trước deploy:

```
HEALTH_OK
No RGW daemonNo realm / zonegroup / zone
Only .rgw.root exists
```

---

## 2. Pre-setup RGW metadata

### 2.1 Tạo realm

```
radosgw-admin realm create --rgw-realm=hanoiradosgw-admin realm default --rgw-realm=hanoi
```

### 2.2 Tạo system user

```
radosgw-admin user create \  --uid="sync-user" \  --display-name="Synchronization User" \  --system
```

Lưu lại:

```
access_keysecret_key
```

### 2.3 Tạo zonegroup

```
radosgw-admin zonegroup create \  --rgw-zonegroup=hanoi-1 \  --master \  --default
```

### 2.4 Tạo zone

```
radosgw-admin zone create \  --rgw-zonegroup=hanoi-1 \  --rgw-zone=hanoi-zone1 \  --master \  --default
```

### 2.5 Gắn system key vào zone

```
radosgw-admin zone modify \  --rgw-zone=hanoi-zone1 \  --access-key=<sync-user-access-key> \  --secret=<sync-user-secret-key>
```

### 2.6 Commit period

```
radosgw-admin period update --commit
```

Check nhanh:

```
radosgw-admin period get-current | egrep "master_zonegroup|master_zone|default-placement"
```

Kỳ vọng:

```
master_zonegroup: hanoi-1master_zone: hanoi-zone1default-placement
```

---

## 3. Tạo RGW service trên Dashboard

Vào:

```
Dashboard → Services → Create → RGW
```

Điền:

```
Service ID: prodRealm: hanoiZonegroup: hanoi-1Zone: hanoi-zone1Placement: ceph-node01, ceph-node02, ceph-node03Port: 8080SSL: disabledUnmanaged: off
```

Kỳ vọng:

```
rgw.prod3 daemons1 daemon / node
```

---

## 4. Monitor sau khi tạo service

```
watch -n 2 'ceph -sechoceph orch ls | grep rgwechoceph orch ps --daemon-type rgwechoceph osd pool ls | grep rgw'
```

Kỳ vọng:

```
HEALTH_OKrgw: 3 daemons active3 hosts1 zone
```

---

## 5. Test RGW endpoint

```
curl -I http://10.10.30.21:8080curl -I http://10.10.30.22:8080curl -I http://10.10.30.23:8080
```

Kỳ vọng:

```
Có HTTP response từ Ceph Object Gateway403 cũng OK nếu chưa auth
```

---

## 6. Tạo S3 user test

```
radosgw-admin user create \  --uid=test-user \  --display-name="Test User"
```

Export key:

```
export AWS_ACCESS_KEY_ID="<test-user-access-key>"export AWS_SECRET_ACCESS_KEY="<test-user-secret-key>"
```

---

## 7. Test bucket/object

```
aws --endpoint-url http://10.10.30.21:8080 \  s3 mb s3://test-bucketecho hello > hello.txtaws --endpoint-url http://10.10.30.21:8080 \  s3 cp hello.txt s3://test-bucket/aws --endpoint-url http://10.10.30.21:8080 \  s3 ls s3://test-bucket
```

Check bucket:

```
radosgw-admin bucket stats --bucket=test-bucket
```

Kỳ vọng:

```
owner: test-usernum_objects >= 1placement_rule: default-placement
```

---

## 8. Check pool RGW

```
ceph dfceph osd pool ls | grep rgwceph osd pool autoscale-status | grep rgw
```

Ghi nhớ nhanh:

```
meta/control/log pool xuất hiện sớmbuckets.index/buckets.data thường xuất hiện sau bucket/object operationbuckets.data có thể được cấp PG lớn do BULK=True
```

Trong bài test:

```
hanoi-zone1.rgw.buckets.index: 32 PGhanoi-zone1.rgw.buckets.data: 512 PG, BULK=True
```

---

## 9. Test HA RGW daemon

Stop 1 daemon:

```
ceph orch daemon stop --force rgw.prod.ceph-node02.mjpfny
```

Check:

```
ceph -sceph health detailceph orch ps --daemon-type rgw
```

Kỳ vọng:

```
HEALTH_WARN: CEPHADM_FAILED_DAEMONrgw còn 2 daemons activeOSD vẫn up/inPG vẫn active+clean
```

Start lại:

```
ceph orch daemon start rgw.prod.ceph-node02.mjpfny
```

Check:

```
ceph -s
```

Kỳ vọng:

```
HEALTH_OKrgw: 3 daemons active
```

---

## 10. Test reshard nhanh

Check bucket:

```
radosgw-admin bucket stats --bucket=test-bucket | egrep '"num_shards"|"index_generation"'
```

Add reshard:

```
radosgw-admin reshard add \  --bucket=test-bucket \  --num-shards=31
```

Theo dõi:

```
radosgw-admin reshard listradosgw-admin reshard status --bucket=test-bucketradosgw-admin bucket stats --bucket=test-bucket | egrep '"num_shards"|"index_generation"'
```

Nếu muốn xử lý queue sớm hơn:

```
radosgw-admin reshard process
```

Kỳ vọng sau khi xong:

```
num_shards đổi sang số mớiindex_generation tăngreshard list không còn task đó
```

---

## 11. Kết luận bài test

```
RGW deploy bằng Dashboard: PASS3 RGW daemon / 3 node: PASSS3 user/bucket/object: PASSPool RGW auto-create: PASSAutoscaler RGW pool: PASSStop/start 1 RGW daemon: PASSBucket reshard async: PASS
```

---

## 12. Ghi nhớ khi làm production

```
Chốt naming realm/zonegroup/zone trước khi làmKhông tạo thử nhiều realm/zone lung tungKhông public endpoint khi chưa có LB/VIP/SSL/DNSSau deploy phải test bucket/object thậtReview PG/autoscaler ngay sau khi buckets.data/index xuất hiệnReshard bucket lớn nên chạy ngoài giờ cao điểm
```
