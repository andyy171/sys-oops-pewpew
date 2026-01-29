# Giới thiệu
Shell là một chương trình cung cấp giao diện dòng lệnh (text-only interface) cho hệ điều hành Unix-like. Nó cho phép người dùng nhập lệnh và thực thi chúng.  

---
## Các loại shell trong Linux
### Interactive vs Non-Interactive Shell
- **Interactive shell:** hiển thị prompt để người dùng nhập lệnh, có thể yêu cầu thêm input. Ví dụ: đăng nhập SSH, mở terminal.
- **Non-interactive shell:** không cần sự tương tác trực tiếp, thường được dùng để chạy script. Script chạy trong subshell và kết thúc khi thực thi xong.

---

### Login vs Non-Login Shell
- **Login shell:**
  - Được khởi tạo sau khi đăng nhập hệ thống thành công (ví dụ SSH).
  - Có thể tạo login shell bằng:  
    ```bash
    su - [username]
    su -l [username]
    su --login [username]
    sudo -i
    ```
  - Kiểm tra login shell bằng:
    ```bash
    echo $0
    ```
    Nếu tên shell bắt đầu bằng dấu `-` (ví dụ `-bash`) thì đó là login shell.
  - Khi thoát login shell, `~/.bash_logout` sẽ được thực thi.

- **Non-login shell:**
  - Bắt đầu khi mở một terminal mới trong môi trường đã đăng nhập sẵn.
  - Có thể tạo bằng cách gọi trực tiếp shell:
    ```bash
    bash
    ```
  - Thường được dùng khi đã có login session.
  - `su` không kèm `-` cũng tạo non-login shell.

---

### Startup Files: Sự khác biệt quan trọng
- **Login shell đọc:**
  1. `/etc/profile`
  2. `~/.bash_profile`, `~/.bash_login`, hoặc `~/.profile` (cái nào có thì dùng trước).
- **Non-login interactive shell đọc:**
  - `~/.bashrc`
- **Non-interactive no-login shell (script):**
  - Không đọc file startup, chỉ kế thừa environment từ parent shell.

Thông thường, trong `~/.bash_profile` sẽ có dòng:
```bash
if [ -f ~/.bashrc ]; then . ~/.bashrc; fi
