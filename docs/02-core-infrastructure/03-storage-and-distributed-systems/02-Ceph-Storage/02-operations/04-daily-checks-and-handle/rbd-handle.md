Title : Làm việc với Ceph Block - RBD


# Làm việc với Ceph Block - rbd
```bash
rbd -p POOL_NAME ls -l #Liệt kê các block device của pool cụ thể 
rbd create -p POOL_NAME VOLUME_NAME -size SIZE # Tạo 1 block device 
rbd showmapped # Xem mapping của các device




```