# Upgrade version minor với dashboard ceph


## 1. Mục tiêu

```
Upgrade Ceph cluster bằng Dashboard với target image cụ thể.Case test:```textSource version: 19.2.3 SquidTarget version: 20.2.1 TentacleTarget image: quay.io/ceph/ceph:v20.2.1
```

---

## 2. Pre-check trước upgrade

### 2.1 Check trạng thái cluster

```
ceph -s
ceph health detail
ceph versions
ceph orch upgrade status
```

Điều kiện nên đạt trước khi upgrade:

```
HEALTH_OKPG active+clean
Không recovery/backfill/degraded
Không có upgrade đang chạy
MON/MGR/OSD đang cùng version
```

---

### 2.2 Check version upgrade available

```
ceph orch upgrade ls
```

Ví dụ output hợp lệ có target:

```
20.2.1
20.2.0
20.1.1
20.1.0
19.2.3
19.2.2
19.2.1
19.2.0
```

Nếu version không có trong list, không nhập bừa image tag trên Dashboard.

Ví dụ:

```
Không có 19.2.4 → không upgrade 19.2.3 lên 19.2.4
```

---

### 2.3 Check pool safety

```
ceph osd pool ls detail
```

Cần đặc biệt chú ý:

```
size
min_size
pg_num
application
```

Mức an toàn tốt cho upgrade:

```
size = 3min_size = 2
```

Cần cẩn trọng nếu có nhiều pool:

```
size = 2, min_size = 1size = 1
```

---

### 2.4 Pull image trước trên toàn bộ node

Chạy trên từng node Ceph:

```
podman pull quay.io/ceph/ceph:v20.2.1
```

Hoặc từ một node SSH sang các node khác:

```
for h in ceph-node01 ceph-node02 ceph-node03; do  echo "===== $h ====="  ssh $h "podman pull quay.io/ceph/ceph:v20.2.1"done
```

Mục tiêu:

```
Image pull thành công trên tất cả nodeKhông có lỗi registry/network
```

---

## 3. Mở monitor trước khi start upgrade

### Terminal 1: monitor tổng thể

```
watch -n 2 'echo "===== DATE ====="dateechoecho "===== CEPH STATUS ====="ceph -sechoecho "===== UPGRADE STATUS ====="ceph orch upgrade statusechoecho "===== CEPH VERSIONS ====="ceph versions'
```

### Terminal 2: monitor cephadm event

```
ceph -W cephadm
```

### Terminal 3: dùng để chạy command kiểm tra nhanh

```
ceph orch ps --format plain
```

---

## 4. Thao tác trên Dashboard

Vào:

```
Dashboard→ Administration→ Upgrade
```

Chọn:

```
Use image
```

Nhập image:

```
quay.io/ceph/ceph:v20.2.1
```

Bấm:

```
Start Upgrade
```

---

## 5. Theo dõi trong lúc upgrade

Các trạng thái có thể xuất hiện tạm thời:

```
HEALTH_WARN
OSD down/degraded/undersized/peering
Reduced data availability
```

Nếu chỉ xuất hiện ngắn và tự hồi thì có thể chấp nhận.

Điểm cần quan sát kỹ:

```
OSD down bao lâu?Có nhiều OSD down cùng lúc không?PG có quay lại active+clean không?Upgrade có tiếp tục chạy không?Có daemon nào fail redeploy không?
```

---

## 6. Checkpoint sau từng phase

### 6.1 Check upgrade status

```
ceph orch upgrade status
```

Cần xem:

```
target_image
in_progress
services_complete
progress
message
is_paused
```

---

### 6.2 Check daemon version

```
ceph versions
```

Trong lúc upgrade có thể thấy mixed version:

```
19.2.320.2.1
```

Sau khi hoàn tất phải đồng nhất:

```
mon: 20.2.1mgr: 20.2.1osd: 20.2.1overall: 20.2.1
```

---

### 6.3 Check daemon status

```
ceph orch ps --format plain
```

Tập trung vào:

```
STATUS
VERSION
IMAGE ID
CONTAINER ID
```

Có thể lọc nhanh:

```
ceph orch ps --format plain | egrep "NAME|mgr|mon|osd|crash|ceph-exporter"
```

---

## 7. Điều kiện coi là upgrade thành công

Sau khi upgrade xong, cần đạt:

```
ceph -s
ceph health detail
ceph version
sceph orch upgrade statusceph pg stat
```

Kết quả mong muốn:

```
HEALTH_OK
PG active+clean
No upgrades in progress
MON/MGR/OSD cùng version mới
Không còn degraded/undersized/peering
```

Ví dụ case test thành công:

```
Version sau upgrade: 20.2.1
Health: HEALTH_OK
OSD: 16 up / 16 in
PG: 193 active+clean
Upgrade status: no upgrade in progress
```

---

## 8. Khi nào cần dừng / không tiếp tục

Cần dừng quan sát hoặc can thiệp nếu gặp:

```
OSD down lâu không lên lại
Nhiều OSD down cùng lúc
PG degraded/undersized kéo dài
Upgrade báo failed
Image pull failed
Daemon redeploy failed
MON mất quorum
MGR không có active daemon
```

Lệnh dừng upgrade:

```
ceph orch upgrade stop
```

Lưu ý:

```
stop chỉ dừng phần upgrade chưa chạy tiếp
không rollback daemon đã upgrade xong
```

---

## 9. Post-check sau upgrade

Chạy block tổng hợp:

```
echo "===== DATE ====="dateechoecho "===== CEPH VERSION ====="ceph -vechoecho "===== CEPH STATUS ====="ceph -sechoecho "===== HEALTH DETAIL ====="ceph health detailechoecho "===== CEPH VERSIONS ====="ceph versionsechoecho "===== UPGRADE STATUS ====="ceph orch upgrade statusechoecho "===== ORCH PS SUMMARY ====="ceph orch ps --format plainechoecho "===== PG STATES ====="ceph pg stat
```

---

## 10. Ghi nhận từ bài test thực tế

Trong bài test này:

```
19.2.3 → 20.2.1
```

Kết quả:

```
Upgrade completedHEALTH_OKAll MON/MGR/OSD upgraded to 20.2.1PG active+clean
```

Quan sát quan trọng:

```
Trong lúc upgrade OSD có thời điểm OSD down tạm thời
Cluster chuyển HEALTH_WARN
Có degraded/undersized/peering ngắn
Sau đó tự hồi về HEALTH_OK
```

Kết luận vận hành:

```
OSD down ngắn trong lúc upgrade có thể là expected behavior.
Điều quan trọng là PG phải hồi về active+clean và OSD phải lên lại nhanh.
```
