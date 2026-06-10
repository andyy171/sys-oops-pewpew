# Package, Process và Service Management

## 1. Package Management Overview

Package manager quản lý vòng đời phần mềm trên Linux:

- Install/remove/upgrade package.
- Resolve dependency.
- Quản lý repository, mirror và GPG key.
- Theo dõi file thuộc package nào.
- Chạy pre/post install script của package.

Ba family thường gặp:

| Family | Low-level tool | High-level tool |
| --- | --- | --- |
| Debian/Ubuntu | `dpkg` | `apt`, `apt-get` |
| RHEL/CentOS/Fedora | `rpm` | `yum`, `dnf` |
| SUSE/openSUSE | `rpm` | `zypper` |

## 2. RPM/YUM/DNF Family

```bash
# Query package
rpm -qa
rpm -qi <package>
rpm -ql <package>
rpm -qf /path/to/file

# Install/remove local RPM
sudo rpm -ivh package.rpm
sudo rpm -Uvh package.rpm
sudo rpm -e <package>

# Repository operations
sudo dnf search <name>
sudo dnf install <package>
sudo dnf remove <package>
sudo dnf update
sudo dnf history
sudo dnf history undo <id>
dnf repoquery --whatprovides /path/to/file
dnf repoquery --requires <package>
```

Trên hệ cũ có thể dùng `yum`; trên RHEL/Fedora mới ưu tiên `dnf`.

## 3. DEB/APT/DPKG Family

```bash
# Query package
dpkg -l
dpkg -L <package>
dpkg -S /path/to/file
apt show <package>
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
```

Khi `dpkg` bị interrupted:

```bash
sudo dpkg --configure -a
sudo apt -f install
```

## 4. SUSE/Zypper Family

```bash
zypper search <package>
sudo zypper install <package>
sudo zypper remove <package>
sudo zypper update
zypper repos
zypper info <package>
```

## 5. Repository, Mirror và GPG Key

Repository định nghĩa nơi lấy package. GPG key dùng để xác thực package/repository metadata.

Debian/Ubuntu:

```bash
cat /etc/apt/sources.list
ls /etc/apt/sources.list.d/
ls /etc/apt/keyrings/
sudo apt update
```

RHEL/CentOS/Fedora:

```bash
ls /etc/yum.repos.d/
dnf repolist
dnf config-manager --dump
```

Production notes:

- Dùng mirror nội bộ nếu môi trường cần kiểm soát version.
- Pin/lock version cho workload nhạy cảm.
- Không import GPG key không rõ nguồn.
- Ghi lại repository thêm thủ công để rollback.

## 6. Package Troubleshooting

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

## 7. Process Concept: PID, PPID, State và Signal

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

## 8. `ps`, `top`, `pstree`, `kill`, `jobs`

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

# Job control trong shell
command &
jobs
fg %1
bg %1
```

## 9. Service Management With systemd

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

## 10. Service Troubleshooting Checklist

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
