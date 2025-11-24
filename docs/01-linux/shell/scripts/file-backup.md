# "Các lệnh tham khảo cho Backup File  "
---

# Backup file cơ bản 
```bash
#!/bin/bash
 backup_dir="/path/to/backup" 
 source_dir="/path/to/source"
 ## Create a timestamped backup of the source directory
 tar -czf "$backup_dir/backup_$(date +%Y%m%d_%H%M).tar.gz" "$source_dir"
```

# Backup file trên remote server 
```bash
#!/bin/bash 
source_dir="/path/to/source" remote_server="user@remote_server:/path/to/backup"

## Backup files/directories to a remote server using rsync
rsync -avz "$source_dir" "$remote_server" echo "Files backed up to remote server."
```

# Nén/Giải nén ( Compression/Decompression) file 
```bash
#!/bin/bash 
file_to_compress="/path/to/file.txt"
## Compress a file using gzip
gzip "$file_to_compress" echo "File compressed: $file_to_compress.gz"
## Decompress a file using gzip
gzip -d "$file_to_compress.gz" echo "File decompressed: $file_to_compress"
```

## Đồng bộ hóa Thư mục - Directory Synchronization
```bash
#!/bin/bash 
source_dir="/path/to/source" 
destination_dir="/path/to/destination"

## Synchronize directories using rsync
rsync -avz "$source_dir" "$destination_dir" echo "Directories synchronized successfully."
```

# Luân chuyển sao lưu - Backup Rotation
```bash
#!/bin/bash 
backup_dir="/path/to/backups" 
max_backups=5

## Rotate backups by deleting the oldest if more than max_backups
while [ $(ls -1 "$backup_dir" | wc -l) -gt "$max_backups" ]; do rm -r "$backup_dir/$(ls -1t "$backup_dir" | tail -n 1)" done echo "Backup rotation completed."
```

