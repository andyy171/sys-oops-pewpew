# Recover Lost Partition After Accidental wipefs With TestDisk

## Mục Đích

Runbook này dùng khi chạy nhầm `wipefs` hoặc làm mất partition/filesystem signature khiến Linux không còn thấy partition cũ, ví dụ `/dev/sdb1` biến mất khỏi `lsblk` hoặc không mount được dữ liệu cũ.

Trọng tâm là bảo toàn dữ liệu trước, phục hồi metadata sau. Nếu data block chưa bị ghi đè, khả năng phục hồi partition table bằng TestDisk vẫn có thể tốt.

## Bản Chất Sự Cố

`wipefs` xóa chữ ký nhận dạng trên block device. Khi chạy sai, đặc biệt trên toàn bộ disk như `/dev/sdb`, nó có thể xóa dấu vết partition table, filesystem, RAID, LVM hoặc metadata khác. OS có thể coi disk như thiết bị trống dù payload dữ liệu bên trong chưa chắc đã mất.

| Khái niệm | Ý nghĩa vận hành |
|---|---|
| `/dev/sdb` | Toàn bộ disk hoặc cloud volume. Thao tác sai ở mức này có thể ảnh hưởng partition table. |
| `/dev/sdb1` | Một partition cụ thể. Nếu partition entry mất, device node này có thể biến mất. |
| Partition table | Bản đồ start/end sector của partition. Mất bảng này thì OS không biết partition nằm ở đâu. |
| Filesystem signature | Dấu hiệu nhận dạng ext4, xfs hoặc filesystem khác. |
| Data block | Vùng chứa nội dung file. Nếu chưa bị ghi đè, dữ liệu vẫn có khả năng cứu. |

Đừng nhầm "mất partition" với "mất toàn bộ dữ liệu". Recovery trong trường hợp này tập trung vào dựng lại bản đồ partition hoặc copy dữ liệu ra ngoài trước khi ghi thêm.

## Nguyên Tắc An Toàn

- Dừng ngay mọi tiến trình có thể ghi vào disk hoặc mount point liên quan.
- Không chạy `mkfs`, không tạo partition mới, không chạy `fsck` sửa tự động khi chưa xác minh.
- Không mount read-write trước khi kiểm tra dữ liệu.
- Xác định đúng disk bằng size, serial, mount point, VM/volume mapping và thông tin change gần nhất.
- Với production hoặc dữ liệu quan trọng, ưu tiên snapshot/clone/image disk trước rồi recovery trên bản copy.
- Với OpenStack/Cinder volume, snapshot hoặc clone volume rồi attach vào rescue VM. Nếu backend là Ceph RBD, tránh thao tác ghi trực tiếp trên image gốc khi chưa có đường rollback.

## Pre-Check Read-Only

```bash
lsblk -o NAME,SIZE,FSTYPE,TYPE,MOUNTPOINT,UUID,MODEL,SERIAL
sudo fdisk -l /dev/sdb
sudo blkid
findmnt
mount | grep -E 'sdb|/data' || true
dmesg -T | tail -n 50
```

Nếu thấy device đang được mount hoặc service vẫn ghi vào mount point cũ, dừng service hoặc detach volume theo quy trình an toàn trước khi recovery.

## Recovery Bằng TestDisk

Cài và chạy TestDisk trên đúng disk cần cứu:

```bash
sudo apt update
sudo apt install -y testdisk
sudo testdisk /dev/sdb
```

Các lựa chọn quan trọng:

| Màn hình / lựa chọn | Cách hiểu |
|---|---|
| Select a media | Chọn đúng disk/volume, kiểm tra size để tránh nhầm. |
| Intel | Dùng cho MBR/DOS partition table. |
| EFI GPT | Dùng cho GPT, thường gặp với disk lớn hoặc hệ thống UEFI. |
| Analyse | Quét cấu trúc partition và tìm partition đã mất. |
| Quick Search | Quét nhanh, nên thử trước. |
| Deeper Search | Quét sâu hơn khi Quick Search chưa thấy kết quả chắc chắn. |
| `P - list files` | Mở thử danh sách file trong partition tìm được. Đây là bước xác minh quan trọng. |
| Write | Ghi lại partition table. Chỉ dùng khi đã chắc partition đúng. |

Quy trình:

1. Chọn đúng disk, ví dụ `Disk /dev/sdb`.
2. Chọn đúng loại partition table: `Intel` cho MBR/DOS hoặc `EFI GPT` cho GPT.
3. Chọn `Analyse`, sau đó `Quick Search`.
4. Nếu tìm thấy partition nghi vấn, kiểm tra size, start sector, end sector và filesystem type.
5. Nhấn `P` để list file. Nếu thấy file/thư mục cũ, khả năng phục hồi cao hơn.
6. Chỉ chọn `Write` khi đã chắc partition đúng và dữ liệu đọc được.
7. Thoát TestDisk, yêu cầu kernel đọc lại partition table hoặc reboot nếu cần.

```bash
sudo partprobe /dev/sdb || true
sudo blockdev --rereadpt /dev/sdb || true
```

Nếu kernel báo device busy hoặc chưa nhận lại partition, reboot có kiểm soát thường an toàn hơn việc tiếp tục ghi thử.

## Mount Read-Only Và Xác Minh

Sau khi partition xuất hiện lại, mount read-only trước:

```bash
lsblk -f
sudo blkid /dev/sdb1
sudo mkdir -p /data
sudo mount -o ro /dev/sdb1 /data
findmnt /data
df -hT /data
ls -la /data
dmesg -T | tail -n 50
```

Nếu dữ liệu đọc được, backup/copy dữ liệu quan trọng sang nơi khác trước khi remount read-write hoặc đưa service chạy lại.

```bash
sudo umount /data
sudo mount /dev/sdb1 /data
```

## Cập Nhật fstab

Không phụ thuộc lâu dài vào tên device như `/dev/sdb1` vì thứ tự disk có thể đổi sau reboot. Dùng UUID và đúng filesystem type thực tế.

```bash
sudo blkid /dev/sdb1
sudo cp /etc/fstab /etc/fstab.bak.$(date +%F-%H%M)
sudo editor /etc/fstab
sudo mount -a
findmnt /data
df -hT /data
```

Ví dụ:

```text
UUID=<uuid> /data ext4 defaults,nofail 0 2
UUID=<uuid> /data xfs defaults,nofail 0 0
```

Không copy mù filesystem type. Nếu `blkid` báo `ext4` mà `fstab` ghi `xfs`, mount sẽ lỗi.

## Validation

- `lsblk` hoặc `fdisk` thấy lại partition đúng size.
- `blkid` nhận đúng filesystem type và UUID.
- Mount read-only thành công.
- `findmnt` và `df -hT` hiển thị đúng mount point.
- Có thể đọc danh sách thư mục và file mẫu.
- `dmesg` không có lỗi I/O nghiêm trọng mới.
- Dữ liệu quan trọng đã được backup sau khi mount lại.
- `fstab` dùng UUID và `mount -a` không báo lỗi.

## Lỗi Cần Tránh

| Lỗi | Hậu quả |
|---|---|
| Chạy `mkfs` vì thấy disk trống | Ghi filesystem mới lên vùng dữ liệu cũ, giảm mạnh khả năng cứu. |
| Tạo partition mới tùy tiện bằng `fdisk`/`parted` | Có thể ghi sai start/end sector. |
| Chạy `fsck` sửa tự động quá sớm | Có thể sửa sai trên metadata chưa xác minh. |
| Mount read-write quá sớm | App hoặc OS có thể ghi thêm dữ liệu trước khi kiểm tra xong. |
| `Write` trong TestDisk khi chưa list được file | Có thể ghi partition table sai. |
| Ghi `fstab` bằng `/dev/sdb1` và sai filesystem type | Sau reboot có thể mount fail hoặc mount nhầm disk. |
| Không snapshot/clone trước production recovery | Không có đường quay lại nếu thao tác làm tình hình xấu hơn. |

## OpenStack/Cinder Notes

Với volume của VM trong OpenStack, sự cố có thể xảy ra khi user hoặc script trong VM chạy nhầm `wipefs`, `fdisk` hoặc `mkfs` lên data disk. Nên ưu tiên:

- Snapshot hoặc clone volume trước khi recovery.
- Attach clone vào rescue VM để chạy TestDisk và kiểm tra dữ liệu.
- Nếu backend là Ceph RBD, tận dụng snapshot/clone ở tầng Cinder/Ceph tùy quyền vận hành.
- Sau khi cứu được dữ liệu, cân nhắc copy sang volume mới sạch nếu metadata cũ không còn đáng tin.
- Ghi lại tenant, VM, volume ID, thời điểm sự cố, lệnh đã chạy, trạng thái trước/sau và đường phục hồi đã chọn.

## Trang Liên Quan

- [Disk, Filesystem, Mount và Swap](../02-storage-networking/01-disk-filesystem-mount-swap.md)
- [Common Linux Troubleshooting Runbooks](./04-common-troubleshooting-runbooks.md)
- [Linux Incident Response Live Triage](./07-linux-incident-response-live-triage.md)
- [OpenStack Backup Recovery](../../../04-cloud-edge/02-cloud-ecosystem/openstack/02-operations/backup-recovery.md)
