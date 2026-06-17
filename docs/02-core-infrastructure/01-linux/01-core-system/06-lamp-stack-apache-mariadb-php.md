# LAMP Stack: Apache, MariaDB/MySQL Và PHP

## Overview

LAMP là mô hình web stack truyền thống gồm Linux, Apache/httpd, MySQL hoặc MariaDB, và PHP. Trong vận hành hiện đại, LAMP vẫn hữu ích cho lab, ứng dụng PHP legacy, CMS, control panel hoặc service nội bộ nhỏ. Với production lớn, cần tách rõ web tier, database tier, backup, monitoring, TLS và hardening thay vì coi LAMP là một lệnh cài đặt duy nhất.

## Thành Phần

| Thành phần | Vai trò |
| --- | --- |
| Linux | OS, service manager, filesystem, network, firewall |
| Apache/httpd | Web server, virtual host, TLS termination hoặc reverse proxy |
| MariaDB/MySQL | Relational database cho application |
| PHP/PHP-FPM hoặc Apache module | Runtime xử lý code PHP |

Tên package và service khác nhau theo distro:

| Distro family | Web service thường gặp | Database service thường gặp | PHP integration |
| --- | --- | --- |
| Debian/Ubuntu | `apache2` | `mysql` hoặc `mariadb` | `libapache2-mod-php` hoặc `php-fpm` |
| RHEL/CentOS/Fedora | `httpd` | `mariadb` hoặc `mysqld` | `php-fpm` hoặc module tương ứng |
| Arch | `httpd` | `mariadb` | `php-fpm` hoặc Apache module |

## Workflow Cài Đặt An Toàn

Không nên copy lệnh cài đặt cũ từ internet rồi chạy thẳng trên production. Luồng an toàn hơn:

1. Chọn distro/version và repository chuẩn.
2. Cài từng lớp: web server, database, PHP runtime, extension cần thiết.
3. Kiểm tra service status và port listen.
4. Cấu hình virtual host/document root rõ ràng.
5. Bật TLS nếu expose ra network không tin cậy.
6. Hardening database account, xóa sample/default app không cần thiết.
7. Cấu hình backup database và backup file upload/application.
8. Thiết lập log rotation, monitoring và alert.

Ví dụ kiểm tra sau cài đặt:

```bash
systemctl status apache2 2>/dev/null || systemctl status httpd
systemctl status mariadb 2>/dev/null || systemctl status mysql 2>/dev/null || systemctl status mysqld
ss -lntup
curl -I http://127.0.0.1/
php -v
```

## Cấu Hình Và Log Quan Trọng

| Thành phần | Path/log thường gặp |
| --- | --- |
| Apache Debian/Ubuntu | `/etc/apache2/`, `/var/log/apache2/` |
| Apache RHEL-family | `/etc/httpd/`, `/var/log/httpd/` |
| Web root phổ biến | `/var/www/html` |
| PHP-FPM | `/etc/php/*/fpm/`, `/etc/php-fpm.d/`, service `php-fpm` |
| MariaDB/MySQL config | `/etc/mysql/`, `/etc/my.cnf`, `/etc/my.cnf.d/` |

Luôn chạy config test trước khi reload/restart web server:

```bash
apachectl configtest 2>/dev/null || httpd -t
sudo systemctl reload apache2 2>/dev/null || sudo systemctl reload httpd
```

## Rủi Ro Vận Hành

- Database local trên cùng host với web app đơn giản nhưng tạo single point of failure.
- File upload cần quota, permission và backup riêng.
- PHP extension/version lệch có thể làm app lỗi sau upgrade.
- Không expose `/server-status`, `phpinfo()` hoặc default page chứa thông tin nhạy cảm.
- Với SELinux enforcing, web root/custom path cần context đúng, ví dụ `httpd_sys_content_t`.
- Restart web/database có thể gây downtime; ưu tiên reload khi service hỗ trợ và test config trước.

## Troubleshooting Nhanh

```bash
systemctl status apache2 2>/dev/null || systemctl status httpd
journalctl -u apache2 -b 2>/dev/null || journalctl -u httpd -b
tail -100 /var/log/apache2/error.log 2>/dev/null
tail -100 /var/log/httpd/error_log 2>/dev/null
ss -lntup | grep -E ':80|:443|:3306'
curl -vk https://example.com/
```

Checklist:

- Web server có listen đúng IP/port không.
- Firewall/security group có mở port cần thiết không.
- Virtual host có match hostname/SNI không.
- PHP-FPM socket hoặc TCP upstream có đúng permission không.
- Database credential, schema và privilege có đúng không.
- Log web/PHP/database có cùng timestamp của request lỗi không.

## Trang Liên Quan

- [Package, Process và Service Management](./03-package-process-service.md)
- [IP, Route, DNS và Firewall](../02-storage-networking/04-ip-route-dns-firewall.md)
- [Logs, journald, rsyslog và logrotate](../03-security-logs-troubleshooting/01-logs-journald-rsyslog-logrotate.md)
- [SUID, SGID, SELinux, PAM, auditd và Hardening](../03-security-logs-troubleshooting/03-suid-sgid-selinux-pam-auditd-hardening.md)
