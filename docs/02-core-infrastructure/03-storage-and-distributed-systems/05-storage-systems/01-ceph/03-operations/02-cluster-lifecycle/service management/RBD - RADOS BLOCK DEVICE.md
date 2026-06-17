# RBD   RADOS BLOCK DEVICE


## RBD quản lý những gì?  
  
RBD là block device layer trên RADOS.  
  
Các nhóm cần quản lý:  
  
- RBD pool  
- RBD image  
- Image size/features  
- Snapshot  
- Clone/flatten  
- Map/unmap trên Linux host  
- Export/import  
- Diff backup  
- Watcher/lock  
- Tích hợp OpenStack Cinder/Nova nếu dùng
---
## Tạo RBD pool

Workflow cơ bản đang có trong note cũ: tạo pool, `set size/min_size`, `enable application tag` và `rbd pool init`.
```bash
ceph osd pool create <pool> <pg_num> <pgp_num> replicated
ceph osd pool set <pool> size <n>
ceph osd pool set <pool> min_size <n>
ceph osd pool application enable <pool> rbd
rbd pool init <pool>
````

Verify:

```
ceph osd pool get <pool> all
ceph osd pool application get <pool>
ceph df detail
rbd ls -p <pool>
```
---
## Liệt kê và kiểm tra image
List image:

```
rbd ls -p <pool>
```

Xem thông tin image:

```
rbd info <pool>/<image>
```

Xem dung lượng thực dùng:

```
rbd du <pool>/<image>
```

Xem toàn bộ mapped image trên host:

```
rbd showmapped
```
---
## ## Tạo, resize, xóa image

Tạo image:

```
rbd create <pool>/<image> --size <size-in-MiB>
```

Resize image:

```
rbd resize <pool>/<image> --size <size-in-MiB>
```

Cảnh báo:
- Tăng size thường an toàn hơn.
- Giảm size rất nguy hiểm nếu filesystem/partition bên trong chưa được shrink đúng cách.

Xóa image:

```
rbd rm <pool>/<image>
```

Trước khi xóa nên kiểm tra:

```
rbd info <pool>/<image>rbd snap ls <pool>/<image>rbd children <pool>/<image>@<snap>rbd status <pool>/<image>
```
---
## ## Map/unmap image vào Linux host

Map:

```
rbd map <pool>/<image>
```

Xem device:

```
rbd showmappedlsblk
```

Unmap:

```
rbd unmap /dev/rbdX
```

Nếu unmap lỗi vì busy:

```
lsof /dev/rbdX
fuser -vm /dev/rbdX
mount | grep rbd
```

---
#### Clone và flatten

Protect snapshot:

```
rbd snap protect <pool>/<image>@<snap>
```

Clone:

```
rbd clone <pool>/<image>@<snap> <pool>/<clone-image>
```

Xem clone phụ thuộc snapshot:

```
rbd children <pool>/<image>@<snap>
```

Flatten clone:

```
rbd flatten <pool>/<clone-image>
```

Unprotect snapshot:

```
rbd snap unprotect <pool>/<image>@<snap>
```
---

## ## Export/import image

Export full image:

```
rbd export <pool>/<image> <file>
```

Import image:

```
rbd import <file> <pool>/<image>
```

Export diff:

```
rbd export-diff <pool>/<image>@<snap> <file>
```

Import diff:

```
rbd import-diff <file> <pool>/<image>
```

Ghi chú:

- `export` full image có thể rất nặng.
- `export-diff/import-diff` phù hợp hơn cho backup/migration theo delta nếu có snapshot chain rõ ràng.
---
## ## Watcher/lock/status

Kiểm tra image đang được client nào dùng:

```
rbd status <pool>/<image>
```

Nếu image đang có watcher thì không nên xóa/rollback bừa.

Với OpenStack:

- Watcher thường là compute/libvirt/qemu đang dùng volume/disk.
- Cần đối chiếu với Nova/Cinder trước khi thao tác trực tiếp bằng Ceph.

## ## RBD trong OpenStack

Mapping thường gặp:

```
Cinder volume:volumes/volume-<volume-uuid>Nova ephemeral/root disk nếu dùng pool vms:vms/<instance-disk-id>Glance image nếu dùng pool images:images/<image-id>
```

Kiểm tra volume trong Ceph:

```
rbd info volumes/volume-<uuid>rbd du volumes/volume-<uuid>rbd snap ls volumes/volume-<uuid>rbd status volumes/volume-<uuid>
```

Nguyên tắc:

- Không xóa `volume-<uuid>` trực tiếp bằng `rbd rm` nếu Cinder DB vẫn còn volume.
- Không rollback volume đang attach/running nếu chưa freeze/shutdown VM.
- Nếu cần can thiệp Ceph-native, phải đối chiếu OpenStack state trước.

