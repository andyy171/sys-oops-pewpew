# Package, Process và Service Management

## 1. Package Management Overview

Package manager quản lý vòng đời phần mềm trên Linux:

- Install/remove/upgrade package.
- Resolve dependency.
- Quản lý repository, mirror và GPG key.
- Theo dõi file thuộc package nào.
- Chạy pre/post install script của package.

Package manager giúp hệ thống tránh kiểu cài thủ công rời rạc: binary một nơi, library một nơi, config không được theo dõi, và khi gỡ bỏ không biết file nào thuộc phần mềm nào. Với server production, ưu tiên package từ repository chính thức hoặc mirror nội bộ vì dependency, security update và rollback dễ kiểm soát hơn so với build source tùy tiện.

Ba family thường gặp:

| Family | Low-level tool | High-level tool |
| --- | --- | --- |
| Debian/Ubuntu | `dpkg` | `apt`, `apt-get` |
| RHEL/CentOS/Fedora | `rpm` | `yum`, `dnf` |
| SUSE/openSUSE | `rpm` | `zypper` |

## 2. RPM/YUM/DNF Family

Trên RHEL/CentOS/Fedora, `rpm` là công cụ low-level làm việc trực tiếp với package database và file `.rpm`; `dnf` là package manager cấp cao làm việc với repository, metadata và dependency. Khi có internet hoặc repository nội bộ, ưu tiên `dnf` thay vì cài file RPM thủ công.

```bash
# Query package
rpm -qa
rpm -qi <package>
rpm -ql <package>
rpm -qf /path/to/file
rpm -q <package>
rpm -qp package.rpm
rpm -qpl package.rpm

# Install/remove local RPM
sudo rpm -ivh package.rpm
sudo rpm -Uvh package.rpm
sudo rpm -e <package>

# Repository operations
sudo dnf search <name>
sudo dnf install <package>
sudo dnf remove <package>
sudo dnf update
sudo dnf upgrade <package>
sudo dnf upgrade-minimal --security
sudo dnf check
sudo dnf history
sudo dnf history undo <id>
dnf list installed
dnf list available <package>
dnf repoquery --whatprovides /path/to/file
dnf repoquery --requires <package>
```

Trên hệ cũ có thể dùng `yum`; trên RHEL/Fedora mới ưu tiên `dnf`.

Các pattern vận hành thường gặp:

| Nhu cầu | Lệnh ưu tiên |
| --- | --- |
| Kiểm tra package đã cài chưa | `rpm -q <package>` hoặc `dnf list installed <package>` |
| Xem file do package cài | `rpm -ql <package>` |
| Tìm package sở hữu file | `rpm -qf /path/to/file` hoặc `dnf repoquery --whatprovides /path/to/file` |
| Kiểm tra dependency hỏng | `sudo dnf check` |
| Cài local RPM nhưng vẫn giải dependency từ repo | `sudo dnf install ./package.rpm` |

Không dùng `rpm -i` cho package đã có version cũ vì có thể tạo song song nhiều version nếu package không được thiết kế như vậy. Với local RPM, `rpm -Uvh` thường an toàn hơn `rpm -ivh`, nhưng vẫn kém `dnf install ./package.rpm` vì `dnf` có thể xử lý dependency qua repository.

### Verify Và Reinstall Package

Package database không chỉ dùng để cài/gỡ, mà còn là baseline để kiểm tra file do package quản lý có bị mất hoặc lệch khỏi trạng thái mong đợi không.

```bash
rpm -V <package>
rpm -Va
sudo dnf reinstall <package>
sudo yum reinstall <package>
zypper verify
zypper ps -s
```

`rpm -V` im lặng khi không phát hiện khác biệt. Nếu có output, mỗi ký tự là một loại drift như checksum, size, owner, group, mode, timestamp, capability hoặc missing file. Không phải mọi drift đều là compromise: config file có thể thay đổi hợp lệ, timestamp có thể lệch sau chỉnh sửa, nhưng binary/library bị đổi checksum cần được điều tra kỹ hơn.

Guardrails:

- Chạy verify read-only trước khi reinstall hoặc remove.
- Lưu output verify vào ticket/RCA nếu đang xử lý incident.
- Với file config, so sánh diff và backup trước khi reinstall vì reinstall có thể khôi phục file package nhưng cũng làm mất chỉnh sửa thủ công nếu không kiểm soát.
- Sau upgrade/remove trên SUSE, `zypper ps -s` giúp phát hiện process còn giữ file đã bị xóa hoặc thay thế; cần restart đúng service thay vì reboot mù.

## 3. DEB/APT/DPKG Family

Trên Debian/Ubuntu, `dpkg` là công cụ low-level để thao tác package `.deb`; `apt`, `apt-get`, `apt-cache` là frontend làm việc với repository và dependency.

```bash
# Query package
dpkg -l
dpkg -L <package>
dpkg -S /path/to/file
apt list --installed
apt show <package>
apt search <keyword>
apt --names-only search <keyword>
apt policy <package>
apt-cache policy <package>

# Install/remove local DEB
sudo dpkg -i package.deb
sudo dpkg -r <package>

# Repository operations
sudo apt update
sudo apt install <package>
sudo apt remove <package>
sudo apt purge <package>
sudo apt autoremove
sudo apt upgrade
sudo apt full-upgrade
```

`apt update` chỉ cập nhật metadata từ repository, chưa nâng cấp package. `apt upgrade` nâng cấp package đã cài nhưng tránh gỡ package khi giải dependency. `apt full-upgrade` có thể gỡ/thêm package để hoàn tất dependency, nên cần đọc kỹ danh sách thay đổi trước khi xác nhận.

Một số khác biệt cần nhớ:

| Lệnh | Tín hiệu chính |
| --- | --- |
| `apt list --installed` | Liệt kê package đã cài |
| `apt show <package>` | Xem metadata package trong repository; không luôn chứng minh package đã cài |
| `apt search <keyword>` | Tìm cả tên và mô tả, kết quả có thể rộng |
| `apt --names-only search <keyword>` | Chỉ tìm theo tên package |
| `dpkg -L <package>` | Xem file đã được package cài vào hệ thống |
| `dpkg -S /absolute/path` | Tìm package sở hữu một file cụ thể |
| `apt remove <package>` | Gỡ package, thường giữ lại config |
| `apt purge <package>` | Gỡ package kèm config do package quản lý |
| `apt autoremove` | Dọn dependency từng được cài tự động và không còn package nào cần |

Khi `dpkg` bị interrupted:

```bash
sudo dpkg --configure -a
sudo apt -f install
```

Một số trạng thái `dpkg -l` cần đọc như tín hiệu vận hành, không chỉ là output dài:

| Trạng thái | Ý nghĩa vận hành |
| --- | --- |
| `ii` | package đã install và configure xong |
| `iU` | package đã unpack nhưng chưa configure, thường do dependency hoặc maintainer script lỗi |
| `rc` | package đã remove nhưng còn config file |

Khi cần sửa lại cấu hình package đã từng chạy wizard/configure, ưu tiên kiểm tra và reconfigure thay vì purge ngay:

```bash
sudo debconf-show <package>
sudo dpkg-reconfigure <package>
sudo debconf-show <package>
```

Ghi lại output trước/sau nếu thay đổi ảnh hưởng production. `dpkg -r <package>` thường giữ config; `dpkg -P <package>` purge cả config do package quản lý. Cẩn thận không nhầm `dpkg -p` với `dpkg -P`: chữ thường là query metadata, chữ hoa là purge.

## 4. SUSE/Zypper Family

```bash
zypper search <package>
sudo zypper install <package>
sudo zypper remove <package>
sudo zypper update
zypper repos
zypper info <package>
```

## 5. Arch/Pacman Family

Trên Arch Linux và các distro dùng pacman, package manager chính là `pacman`. Đây không phải family phổ biến nhất trong server enterprise, nhưng hay gặp trong workstation, lab hoặc môi trường cần rolling release.

```bash
# Tìm package theo tên/mô tả
pacman -Ss <keyword>

# Cài package
sudo pacman -S <package>

# Đồng bộ metadata và nâng toàn bộ hệ thống
sudo pacman -Syu

# Xem package đã cài
pacman -Q
pacman -Qi <package>
pacman -Ql <package>
```

Với rolling release, không nên chỉ nâng một package đơn lẻ trong thời gian dài vì dependency có thể lệch với phần còn lại của hệ thống. Trước khi dùng Arch/pacman cho workload quan trọng, cần có snapshot/backup và quy trình rollback rõ hơn so với distro LTS truyền thống.

## 6. Snap Package

Snap là định dạng package do Canonical phát triển và được `snapd` quản lý. Khác với package `.deb` hoặc `.rpm`, snap thường đóng gói nhiều dependency đi kèm và được mount/chạy theo cơ chế riêng, thường thấy dưới dạng squashfs.

```bash
snap version
snap list
snap find <keyword>
snap info <snap>
sudo snap install <snap>
sudo snap remove <snap>
sudo snap disable <snap>
sudo snap enable <snap>
```

Snap hữu ích khi ứng dụng phân phối chính qua Snap hoặc cần phiên bản ít phụ thuộc vào library của distro. Đổi lại, snap có thể tốn disk hơn, có lifecycle update riêng, và không phải lúc nào cũng phù hợp với server cần kiểm soát version chặt.

## 7. Flatpak Package

Flatpak đóng gói desktop application theo mô hình runtime/application riêng, thường dùng cho Linux desktop hơn là server headless. Trên server, chỉ cài Flatpak nếu có use case rõ, ví dụ môi trường workstation, jump desktop hoặc lab GUI.

```bash
sudo dnf install flatpak
flatpak remotes
flatpak search <app>
flatpak install flathub <app-id>
flatpak list
flatpak run <app-id>
flatpak uninstall <app-id>
```

Flathub là remote phổ biến, nhưng khi thêm remote ngoài distro cần đánh giá trust, lifecycle update và policy bảo mật giống như thêm repository phần mềm khác.

## 8. Cài Phần Mềm Từ Source

Build từ source chỉ nên dùng khi package không có trong repository, cần patch/version đặc biệt, hoặc đang làm môi trường lab/dev. Với production, cần ghi rõ source, version, checksum, dependency, prefix cài đặt và cách rollback.

Quy trình phổ biến với tarball:

```bash
tar -zxvf package.tar.gz
cd package-directory
./configure
make
sudo make install
```

Với file `.tar.xz`:

```bash
tar -Jxvf package.tar.xz
```

Các package build thường cần:

```bash
sudo apt install build-essential
```

Nếu project hỗ trợ, có thể gỡ bằng:

```bash
sudo make uninstall
```

Không phải project nào cũng có target `uninstall`. Đây là lý do package manager vẫn nên là lựa chọn mặc định cho hệ thống cần vận hành lâu dài.

## 9. Repository, Mirror và GPG Key

Repository định nghĩa nơi lấy package. GPG key dùng để xác thực package/repository metadata.

Debian/Ubuntu:

```bash
cat /etc/apt/sources.list
ls /etc/apt/sources.list.d/
ls /etc/apt/keyrings/
sudo apt update
```

Một dòng APT repository thường có dạng:

```text
deb <address> <distribution-codename> <component-list>
deb-src <address> <distribution-codename> <component-list>
```

Trong đó `deb` là binary package repository, `deb-src` là source package repository, codename có thể là `jammy`, `focal`, `bookworm`, và component có thể là `main`, `restricted`, `universe`, `multiverse` tùy distro.

RHEL/CentOS/Fedora:

```bash
ls /etc/yum.repos.d/
dnf repolist
dnf repolist --all
dnf config-manager --dump
```

Production notes:

- Dùng mirror nội bộ nếu môi trường cần kiểm soát version.
- Pin/lock version cho workload nhạy cảm.
- Không import GPG key không rõ nguồn.
- Ghi lại repository thêm thủ công để rollback.
- Với RHEL-family, file repository thường nằm trong `/etc/yum.repos.d/*.repo`; backup file repo trước khi sửa.

## 10. Package Troubleshooting

### Package Manager Lock

Triệu chứng: `Could not get lock`, `another process is using`.

```bash
ps aux | grep -E 'apt|dpkg|dnf|yum'
sudo lsof /var/lib/dpkg/lock-frontend
```

Cách xử lý an toàn:

1. Chờ process package hiện tại kết thúc nếu nó đang chạy thật.
2. Nếu process đã chết, chạy recovery:

```bash
sudo dpkg --configure -a
sudo apt update
```

### Repo/Mirror Error

```bash
sudo apt update
dnf repolist
curl -I <repo-url>
```

Kiểm tra DNS, proxy, certificate, mirror URL, distro codename và GPG key.

### Broken Dependencies Trên DNF/RPM

```bash
sudo dnf check
dnf repoquery --requires <package>
dnf repoquery --whatprovides 'libexample.so()(64bit)'
rpm -Va
```

Nếu dependency hỏng sau khi cài RPM thủ công, ưu tiên khôi phục repository đúng, sau đó để `dnf` giải dependency. Tránh ép cài bằng `rpm --nodeps` trên production vì package có thể cài được nhưng service fail lúc runtime.

## 11. Shared Library Loader, Cache Và `ldd`

Shared library là code dùng chung được dynamic linker nạp vào memory khi program start. Khi thiếu hoặc lệch library, package có thể cài thành công nhưng binary fail lúc chạy.

Mental model:

```text
executable
-> dynamic linker/loader
-> library search path
-> ld.so cache
-> shared object file
-> process runtime
```

Các lệnh quan sát an toàn:

```bash
ldd /usr/bin/<binary>
ldconfig -p | grep <library>
ldconfig -v 2>/dev/null | grep <library>
cat /etc/ld.so.conf
ls /etc/ld.so.conf.d/
```

Search path có thể đến từ `LD_LIBRARY_PATH`, config trong `/etc/ld.so.conf` và `/etc/ld.so.conf.d/`, sau đó là các thư mục chuẩn như `/lib*` và `/usr/lib*`. Thông thường:

- `/lib` và `/lib64` phục vụ library cần cho binary hệ thống sớm hoặc command nền tảng.
- `/usr/lib` và `/usr/lib64` phục vụ phần mềm user space/package bổ sung.
- package manager thường tự chạy `ldconfig`; build/copy library thủ công thì admin phải cập nhật cache.

Production guardrails:

- Không đặt `LD_LIBRARY_PATH` global cho service production nếu chưa kiểm soát rõ thứ tự search path; nó có thể khiến binary nạp nhầm library.
- Nếu thêm library custom, đặt file `.conf` rõ trong `/etc/ld.so.conf.d/`, chạy `sudo ldconfig`, rồi validate binary bằng `ldd`.
- Khi `ldd` báo `not found`, kiểm tra package sở hữu library bằng `dnf repoquery --whatprovides`, `rpm -qf`, `apt-file search` hoặc `dpkg -S` tùy distro.
- Nếu library A phụ thuộc library B, cần chạy `ldd` cả trên shared object liên quan, không chỉ binary đầu vào.

## 12. Process Concept: PID, PPID, State và Signal

Mỗi chương trình chạy tạo ra một hoặc nhiều process. Mỗi process có:

- PID: process ID.
- PPID: parent process ID.
- UID/GID owner.
- State: running, sleeping, stopped, zombie.
- Resource usage: CPU, memory, open files, socket.

Các loại process thường gặp:

| Loại | Mô tả |
| --- | --- |
| Foreground | Chiếm terminal hiện tại |
| Background | Chạy nền trong shell |
| Daemon | Service chạy nền lâu dài |
| Zombie | Đã exit nhưng parent chưa reap |
| Orphan | Parent chết, được PID 1 nhận |

Signal phổ biến:

| Signal | Ý nghĩa |
| --- | --- |
| `SIGTERM` 15 | Yêu cầu dừng an toàn |
| `SIGKILL` 9 | Dừng cưỡng bức, không cleanup |
| `SIGHUP` 1 | Reload trong nhiều daemon |
| `SIGSTOP` 19 | Pause process |
| `SIGCONT` 18 | Continue process |

Thứ tự xử lý process runaway nên là quan sát trước, terminate mềm sau, kill cưỡng bức cuối cùng:

```bash
ps -fp <pid>
lsof -p <pid>
kill -TERM <pid>
kill -HUP <pid>     # chỉ khi daemon hỗ trợ reload qua HUP
sudo kill -KILL <pid>
```

`SIGKILL` không cho process cleanup, flush buffer hoặc rollback logic ứng dụng. Với database, queue worker, backup job hoặc process đang ghi file, cần hiểu rủi ro trạng thái dở dang trước khi dùng `kill -9`.

## 13. `ps`, `top`, `pstree`, `kill`, `jobs`

```bash
# Snapshot process
ps aux
ps -ef
ps -fp <pid>
ps -eo pid,ppid,user,stat,%cpu,%mem,cmd --sort=-%cpu | head

# Realtime
top
htop

# Cây process
pstree -ap

# Signal
kill <pid>
kill -TERM <pid>
kill -KILL <pid>
killall <process-name>
pgrep -a <pattern>
pkill -TERM -u <user> <pattern>

# Job control trong shell
command &
jobs
fg %1
bg %1
nohup ./long_task.sh > long_task.log 2>&1 &
```

`command &` chạy background nhưng vẫn thuộc terminal/session hiện tại. `nohup` bỏ qua `SIGHUP` khi logout, nhưng với job quan trọng lâu dài nên ưu tiên systemd service/timer thay vì giữ process thủ công trong shell.

Với `pkill`, luôn test selector bằng `pgrep -a` trước. `killall` và `pkill` có blast radius lớn hơn `kill <pid>` vì chọn theo tên/pattern/user/terminal; nếu pattern quá rộng, có thể dừng nhiều process hợp lệ cùng lúc.

## 14. Service Management With systemd

Service là process/daemon được quản lý bởi `systemd`.

```bash
systemctl status <service>
systemctl start <service>
systemctl stop <service>
systemctl restart <service>
systemctl reload <service>
systemctl enable <service>
systemctl disable <service>
systemctl is-enabled <service>
systemctl is-active <service>
```

`reload` yêu cầu service hỗ trợ reload config. Nếu không chắc, kiểm tra unit hoặc documentation:

```bash
systemctl cat <service>
systemctl show <service> -p ExecReload
```

Unit file location:

| Path | Vai trò |
| --- | --- |
| `/usr/lib/systemd/system/` hoặc `/lib/systemd/system/` | Unit do package cung cấp |
| `/etc/systemd/system/` | Unit hoặc override do admin quản lý |
| `/run/systemd/system/` | Runtime unit |

Override unit:

```bash
sudo systemctl edit <service>
sudo systemctl daemon-reload
sudo systemctl restart <service>
```

Boot/service timing:

```bash
systemd-analyze blame
systemd-analyze critical-chain
systemd-analyze critical-chain <service>
```

## 15. Service Troubleshooting Checklist

```bash
systemctl status <service>
journalctl -u <service> -xe
journalctl -u <service> -b
systemctl cat <service>
systemctl list-dependencies <service>
systemctl show <service> -p ExecStart -p User -p Group -p WorkingDirectory
```

Checklist:

1. Service có failed không.
2. ExecStart path có tồn tại không.
3. User/group chạy service có quyền đọc config, ghi log, bind port không.
4. Environment file có thiếu biến không.
5. Config test có pass không, ví dụ `nginx -t`, `sshd -t`.
6. Port có bị chiếm không.
7. Dependency như network, mount, database đã sẵn sàng chưa.
8. SELinux/AppArmor có deny không.

Rollback:

```bash
sudo systemctl revert <service>
sudo systemctl daemon-reload
sudo systemctl restart <service>
```
