---
title : Thao tác vận hành cụm ceph hằng ngày 

---

# Kiểm tra thông số của cluster 
```bash
ceph -s                 # Kiểm tra trạng thái tổng quan của cả cụm
ceph osd tree           # Kiểm tra trạng thái các osd 
ceph osd df             # Kiểm tra mức độ sử dụng dung lượng của các osd
ceph df                 # Kiểm tra mức độ sử dụng dung lượng của cụm và các pools
ceph osd lspools        # Liệt kê toàn bộ pool với ID

```

# Quản lý các Ceph Service
```bash
# MON
systemctl start ceph-mon@NODE_NAME
systemctl stop ceph-mon@NODE_NAME
systemctl restart ceph-mon@NODE_NAME

# MGR
systemctl start ceph-mgr@NODE_NAME
systemctl stop ceph-mgr@NODE_NAME
systemctl restart ceph-mgr@NODE_NAME
ceph mgr MODULE_NAME enable MODULE
ceph mgr MODULE_NAME disable MODULE


# OSD
ceph osd find OSD.ID
systemctl start ceph-osd@OSD_NAME
systemctl stop ceph-osd@OSD_NAME
systemctl restart ceph-osd@OSD_NAME


```

# Quản lý pool
```bash
ceph df detail    # Dung lượng sử dụng của cụm và các pool


```


# Quản lý OSD 
```bash

```

## Trường hợp dữ liệu đang bị lệch giữa các osd 
```bash
# Sample
osd df

ID CLASS WEIGHT  REWEIGHT SIZE    RAW USE DATA    OMAP     META    AVAIL   %USE  VAR  PGS STATUS
 1   ssd 3.49219  1.00000 3.5 TiB 2.1 TiB 2.1 TiB  6.3 MiB 3.9 GiB 1.4 TiB 60.81 1.06  57     up
 4   ssd 3.49219  1.00000 3.5 TiB 2.0 TiB 2.0 TiB  133 KiB 3.7 GiB 1.5 TiB 57.58 1.01  56     up
 5   ssd 3.49219  1.00000 3.5 TiB 2.1 TiB 2.1 TiB  195 KiB 3.5 GiB 1.4 TiB 61.33 1.07  49     up
 6   ssd 3.49219  1.00000 3.5 TiB 1.2 TiB 1.2 TiB  321 KiB 2.4 GiB 2.3 TiB 33.90 0.59  40     up
 7   ssd 3.49219  1.00000 3.5 TiB 1.5 TiB 1.5 TiB 1012 KiB 2.9 GiB 2.0 TiB 43.03 0.75  39     up
 8   ssd 3.49219  1.00000 3.5 TiB 1.7 TiB 1.7 TiB  194 KiB 4.0 GiB 1.8 TiB 47.96 0.84  47     up
 0   ssd 3.49219  1.00000 3.5 TiB 2.8 TiB 2.8 TiB  485 KiB 5.2 GiB 696 GiB 80.53 1.41  75     up
 9   ssd 3.49219  1.00000 3.5 TiB 3.3 TiB 3.3 TiB  642 KiB 6.1 GiB 173 GiB 95.17 1.67  67     up 
10   ssd 3.49219  1.00000 3.5 TiB 1.7 TiB 1.7 TiB  6.7 MiB 3.1 GiB 1.8 TiB 47.74 0.84  68     up
11   ssd 3.49219  1.00000 3.5 TiB 2.8 TiB 2.8 TiB  1.1 MiB 5.4 GiB 675 GiB 81.14 1.42  78     up
 2   ssd 3.49219  1.00000 3.5 TiB 2.2 TiB 2.2 TiB   27 KiB 4.0 GiB 1.3 TiB 62.14 1.09  40     up
 3   ssd 3.49219  1.00000 3.5 TiB 2.3 TiB 2.3 TiB  445 KiB 4.4 GiB 1.2 TiB 65.90 1.15  55     up
12   ssd 3.49219  1.00000 3.5 TiB 541 GiB 540 GiB 1006 KiB 1.3 GiB 3.0 TiB 15.14 0.27  48     up
13   ssd 3.49219  1.00000 3.5 TiB 2.6 TiB 2.6 TiB  176 KiB 4.9 GiB 895 GiB 74.96 1.31  56     up
14   ssd 3.49219  1.00000 3.5 TiB 1.8 TiB 1.8 TiB  6.4 MiB 3.3 GiB 1.7 TiB 52.03 0.91  48     up
15   ssd 3.49219  1.00000 3.5 TiB 1.2 TiB 1.2 TiB  179 KiB 2.5 GiB 2.3 TiB 34.44 0.60  41     up
```
Như ví dụ trên thì % Sử dụng của osd.9 đang >90% mà trong khi đó lại có 1 số osd khác sử dụng chưa đến 20% .  Ta cần sử dụng lệnh để Ceph chuyển 1 lượng dữ liệu ra khỏi osd.9
```bash
 ceph osd reweight osd.9 0.80
# Lệnh này yêu cầu cho Ceph rằng osd.9 này bây giờ chỉ có thể giữ được lượng dữ liệu tương đương 80% không gian lưu trữ của nó 

# Kết quả sau khi reweight 
ID CLASS WEIGHT  REWEIGHT SIZE    RAW USE DATA    OMAP     META    AVAIL   %USE  VAR  PGS STATUS
 1   ssd 3.49219  1.00000 3.5 TiB 2.1 TiB 2.1 TiB  7.1 MiB 4.7 GiB 1.4 TiB 60.91 1.07  57     up
 4   ssd 3.49219  1.00000 3.5 TiB 2.0 TiB 2.0 TiB  137 KiB 3.7 GiB 1.5 TiB 57.65 1.01  56     up
 5   ssd 3.49219  1.00000 3.5 TiB 2.1 TiB 2.1 TiB  207 KiB 4.0 GiB 1.3 TiB 61.42 1.07  49     up
 6   ssd 3.49219  1.00000 3.5 TiB 1.2 TiB 1.2 TiB  293 KiB 2.4 GiB 2.3 TiB 33.94 0.59  40     up
 7   ssd 3.49219  1.00000 3.5 TiB 1.5 TiB 1.5 TiB 1012 KiB 2.9 GiB 2.0 TiB 43.08 0.75  39     up
 8   ssd 3.49219  1.00000 3.5 TiB 1.7 TiB 1.7 TiB  198 KiB 3.1 GiB 1.8 TiB 48.00 0.84  47     up
 0   ssd 3.49219  1.00000 3.5 TiB 3.0 TiB 3.0 TiB  497 KiB 5.5 GiB 522 GiB 85.40 1.49  80     up
 9   ssd 3.49219  0.79999 3.5 TiB 2.8 TiB 2.8 TiB  650 KiB 6.1 GiB 687 GiB 80.80 1.41  51     up
10   ssd 3.49219  1.00000 3.5 TiB 2.0 TiB 2.0 TiB  7.2 MiB 3.6 GiB 1.5 TiB 57.35 1.00  75     up
11   ssd 3.49219  1.00000 3.5 TiB 2.8 TiB 2.8 TiB  1.1 MiB 5.3 GiB 664 GiB 81.43 1.42  82     up
 2   ssd 3.49219  1.00000 3.5 TiB 2.2 TiB 2.2 TiB   31 KiB 4.0 GiB 1.3 TiB 62.22 1.09  40     up
 3   ssd 3.49219  1.00000 3.5 TiB 2.3 TiB 2.3 TiB  457 KiB 4.2 GiB 1.2 TiB 65.98 1.15  55     up
12   ssd 3.49219  1.00000 3.5 TiB 542 GiB 541 GiB  990 KiB 1.3 GiB 3.0 TiB 15.16 0.27  48     up
13   ssd 3.49219  1.00000 3.5 TiB 2.6 TiB 2.6 TiB  196 KiB 4.9 GiB 892 GiB 75.05 1.31  56     up
14   ssd 3.49219  1.00000 3.5 TiB 1.8 TiB 1.8 TiB  7.1 MiB 3.3 GiB 1.7 TiB 52.10 0.91  48     up
15   ssd 3.49219  1.00000 3.5 TiB 1.2 TiB 1.2 TiB  171 KiB 2.7 GiB 2.3 TiB 34.48 0.60  41     up
                    TOTAL  56 TiB  32 TiB  32 TiB   27 MiB  62 GiB  24 TiB 57.19
MIN/MAX VAR: 0.27/1.49  STDDEV: 18.51
```

# Kiểm soát danh sách các lỗi 
```bash
ceph crash ls              # Liệt kê tất cả các ID lỗi đã ghi nhận
ceph crash ls-new          # Chỉ liệt kê các lỗi mới (chưa archive)
ceph crash info <id>       # Xem chi tiết metadata và stack trace của 1 lỗi
ceph crash stat            # Xem bảng thống kê tóm tắt các vụ crash
ceph crash post -i <file>  # Thủ công gửi một tệp crash lên cluster (debug)
ceph crash archive <id>    # Xác nhận và lưu trữ 1 lỗi (để ẩn cảnh báo)
ceph crash archive-all     # Lưu trữ toàn bộ lỗi để xóa cảnh báo RECENT_CRASH
ceph crash rm <id>         # Xóa hoàn toàn bản ghi của một lỗi cụ thể
ceph crash prune <keep>    # Xóa các bản ghi cũ, chỉ giữ lại <keep> ngày gần nhất
ceph crash json_report <h> # Xuất báo cáo crash trong <h> giờ qua dạng JSON
```

