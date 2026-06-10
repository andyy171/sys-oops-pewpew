# CA Certificates, GRUB và Boot Security

## 1. Certificate Trust Store Overview

Root CA trust store quyết định hệ thống tin cậy CA nào khi kiểm tra TLS certificate. Use case thường gặp:

- Cài internal CA cho proxy, registry, Git server, object storage, private PKI.
- Sửa lỗi TLS khi app/CLI không trust certificate chain.
- Chuẩn hóa trust store cho server fleet.

Không import CA không rõ nguồn. CA được trust có thể ký certificate cho nhiều service.

## 2. Debian/Ubuntu: `update-ca-certificates`

Copy CA dạng PEM/CRT vào:

```bash
sudo cp internal-ca.crt /usr/local/share/ca-certificates/internal-ca.crt
sudo update-ca-certificates
```

Kiểm tra:

```bash
ls /etc/ssl/certs | grep internal
openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt server.crt
```

## 3. RHEL/CentOS/Fedora: `update-ca-trust`

```bash
sudo cp internal-ca.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust extract
```

Kiểm tra:

```bash
trust list | grep -i internal
openssl verify -CAfile /etc/pki/tls/certs/ca-bundle.crt server.crt
```

## 4. Application-specific Trust Store

Một số runtime không dùng OS trust store trực tiếp:

- Java: `cacerts` hoặc truststore riêng.
- Python/requests: có thể dùng `certifi`.
- Container image: cần cài CA trong image.
- Browser: Chrome/Firefox có policy/store riêng tùy OS.

Ví dụ Java:

```bash
keytool -importcert \
  -alias internal-ca \
  -file internal-ca.crt \
  -keystore truststore.jks
```

## 5. Boot/GRUB Security Overview

GRUB cho phép chỉnh kernel parameter khi boot. Điều này hữu ích khi rescue hệ thống, nhưng cũng là rủi ro nếu attacker có console access.

Biện pháp hardening:

- Bật disk encryption cho dữ liệu nhạy cảm.
- Kiểm soát console/IPMI/iDRAC/iLO access.
- Đặt GRUB password nếu policy yêu cầu.
- Bật Secure Boot nếu môi trường hỗ trợ và quy trình vận hành rõ.
- Giới hạn boot từ USB/network trong firmware.

## 6. Reset Root Password Qua GRUB

Cảnh báo:

- Chỉ thực hiện khi bạn có quyền console hợp lệ.
- Trên hệ có full disk encryption, Secure Boot hoặc policy nội bộ, quy trình có thể khác.
- Đây là thao tác rescue/admin, không phải cách bypass kiểm soát truy cập.

High-level flow:

1. Vào GRUB edit mode.
2. Thêm kernel parameter rescue phù hợp distro.
3. Boot vào rescue shell.
4. Remount root filesystem read-write.
5. Đổi password hoặc sửa config.
6. Relabel SELinux nếu cần.
7. Reboot và kiểm tra login.

RHEL/CentOS thường dùng:

```text
rd.break
```

Trong rescue shell:

```bash
mount -o remount,rw /sysroot
chroot /sysroot
passwd root
touch /.autorelabel
exit
reboot
```

Ubuntu/Debian thường dùng recovery mode hoặc init shell tùy version. Cần theo tài liệu distro đang vận hành.

## 7. GRUB Password

Tạo password hash:

```bash
grub2-mkpasswd-pbkdf2
```

Ví dụ custom config RHEL-family có thể đặt dưới `/etc/grub.d/01_users` hoặc file tương ứng theo distro:

```text
set superusers="admin"
password_pbkdf2 admin <hash>
```

Regenerate GRUB config:

Đường dẫn GRUB khác nhau theo BIOS/UEFI và distro. Trước khi ghi file config, kiểm tra boot mode, mount `/boot`/`/boot/efi` và tài liệu distro đang vận hành.

```bash
# RHEL/CentOS BIOS
sudo grub2-mkconfig -o /boot/grub2/grub.cfg

# RHEL/CentOS UEFI, kiểm tra vendor path thực tế trước
sudo grub2-mkconfig -o /boot/efi/EFI/<vendor>/grub.cfg

# Debian/Ubuntu
sudo update-grub
```

Production notes:

- Test trên lab trước.
- Lưu credential trong password vault.
- Có out-of-band recovery plan nếu GRUB config lỗi.

## 8. Troubleshooting TLS Trust

```bash
openssl s_client -connect server.example.com:443 -servername server.example.com -showcerts
curl -v https://server.example.com
python -c "import ssl; print(ssl.get_default_verify_paths())"
```

Checklist:

- Certificate chain đầy đủ chưa.
- Hostname/SAN đúng chưa.
- Root/intermediate CA đã import đúng store chưa.
- App có dùng trust store riêng không.
- Container image có CA bundle mới không.
