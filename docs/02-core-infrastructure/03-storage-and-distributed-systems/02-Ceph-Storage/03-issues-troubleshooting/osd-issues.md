# Tổng hợp các lỗi thường gặp với OSD

## Khi 1 OSD bị down 

- Khi 1 OSD bị down , đầu tiên ta cần xác định OSD bị down đó là OSD nào 
```bash
ceph osd tree
```
- Sau đó ta cần kiểm tra logs của OSD bị down đó . Để làm được vậy ta cần tìm được host chứa osd đó 
```bash
ceph osd find OSD_ID
```
Sau đó từ host của osd kiểm tra log của osd tại  `/var/log/ceph/ceph.log`
- Thử khởi động lại thủ công OSD 
```bash
systemctl restart ceph-osd@OSD_NUMBER
```
- Xác thực lại OSD đã lên : `ceph osd tree`