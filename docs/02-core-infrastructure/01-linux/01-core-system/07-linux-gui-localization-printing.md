# Linux GUI, Localization Và Printing

## Tổng Quan

Trên server production, GUI thường không phải đường quản trị chính, nhưng vẫn có giá trị trong ba nhóm tình huống:

- workstation hoặc jump host nội bộ cần desktop environment;
- ứng dụng legacy cần X11/Wayland hoặc remote desktop;
- printer, locale, timezone và encoding ảnh hưởng trực tiếp tới output, report, log, batch job hoặc trải nghiệm người dùng.

Với hạ tầng cloud/devops, nguyên tắc là dùng CLI/automation cho vận hành thường ngày, chỉ bật GUI hoặc remote desktop khi có yêu cầu rõ ràng, có kiểm soát network, authentication, logging và patching.

## Mental Model GUI Trên Linux

GUI Linux là một stack nhiều lớp, không chỉ là "màn hình desktop".

| Lớp | Vai trò |
| --- | --- |
| Display server | Nhận request từ client GUI và giao tiếp với kernel/driver/display. Ví dụ: X.Org/X11, Wayland. |
| Compositor | Ghép window, layer, hiệu ứng và buffer thành frame hiển thị. |
| Window manager | Quản lý vị trí, focus, border, resize và hành vi window. |
| Display manager | Cung cấp màn hình login đồ họa và chọn session. Ví dụ: GDM, SDDM, LightDM, XDM. |
| Desktop environment | Bộ trải nghiệm người dùng hoàn chỉnh: panel, launcher, file manager, settings, notification, accessibility. |

X11 có client/server model lịch sử và có thể chạy qua network. Wayland thiết kế đơn giản hơn, giảm nhiều rủi ro bảo mật của X11, nhưng một số app legacy vẫn cần XWayland để chạy trong session Wayland.

Kiểm tra session đang dùng X11 hay Wayland:

```bash
echo "$WAYLAND_DISPLAY"
loginctl
loginctl show-session <SESSION_ID> -p Type
```

Với host không có GUI session, các lệnh trên có thể không trả thông tin hữu ích. Khi debug từ SSH, kiểm tra thêm user đang login vào seat nào và service display manager đang chạy hay không.

```bash
loginctl list-sessions
systemctl status gdm 2>/dev/null || systemctl status sddm 2>/dev/null || systemctl status lightdm 2>/dev/null
```

## X.Org Và Wayland Operations

X.Org có thể dùng auto-detection cho GPU, monitor, keyboard, mouse và input device. File cấu hình truyền thống là:

```text
/etc/X11/xorg.conf
/etc/X11/xorg.conf.d/*.conf
```

Không tạo hoặc sửa `xorg.conf` trên production desktop nếu chưa có console access và rollback, vì cấu hình sai có thể làm mất GUI login. Khi cần điều tra X11:

```bash
xdpyinfo
xwininfo
cat ~/.xsession-errors
journalctl -b | grep -Ei 'xorg|gdm|sddm|lightdm|wayland|mutter|kwin'
```

`xwininfo` cần tương tác với window X11 và có thể treo hoặc không hoạt động như mong đợi trong Wayland session. Nếu GUI lỗi chỉ xảy ra với Wayland, kiểm tra theo thứ tự:

1. Session type bằng `loginctl show-session`.
2. GPU driver có hỗ trợ Wayland tốt không.
3. Desktop environment có fallback X11 session không.
4. Log của display manager và compositor.
5. Có app legacy cần XWayland không.

Tạm thời tắt Wayland cho GNOME/GDM là thay đổi ảnh hưởng toàn bộ login GUI. Chỉ làm trong maintenance window hoặc workstation đã có rollback:

```text
/etc/gdm3/custom.conf
WaylandEnable=false
```

Sau thay đổi, validate bằng cách restart display manager hoặc reboot có kiểm soát. Restart display manager sẽ làm logout user GUI hiện tại.

## Desktop Environment Và Accessibility

Desktop environment phổ biến:

| Desktop environment | Thành phần thường gặp | Ghi chú vận hành |
| --- | --- | --- |
| GNOME Shell | GDM, Files/Nautilus, Mutter | Phổ biến trên Ubuntu/RHEL-family desktop; Wayland thường là default ở nhiều distro hiện đại. |
| KDE Plasma | SDDM, Dolphin, KWin | Nhiều tùy biến, phù hợp desktop/workstation. |
| Cinnamon | LightDM, Nemo, Muffin | Giao diện truyền thống, thường gặp trên Linux Mint. |
| MATE | LightDM, Caja, Marco | Nhẹ hơn GNOME Shell, quen với người dùng GNOME 2 cũ. |
| Xfce | LightDM, Thunar, Xfwm | Nhẹ, phù hợp máy yếu, VM desktop hoặc remote desktop đơn giản. |

Với workstation doanh nghiệp, cần tiêu chuẩn hóa desktop package set, display manager, screen lock, update policy và cách remote support. Không để mỗi máy tự cài desktop environment khác nhau nếu team phải hỗ trợ tập trung.

Accessibility không phải phần phụ. Với user cần hỗ trợ, kiểm tra các nhóm setting:

- visual: high contrast, large text, zoom, cursor size, screen reader, visual alert;
- keyboard: sticky keys, slow keys, repeat keys, bounce keys, screen keyboard;
- mouse: double-click delay, hover click, mouse keys, simulated secondary click;
- braille/text console: `brltty`, Orca hoặc thiết bị hỗ trợ tương ứng.

Nếu restart dịch vụ accessibility như `brltty`, xác nhận user bị ảnh hưởng và có kênh hỗ trợ thay thế trước khi thao tác:

```bash
systemctl status brltty
sudo systemctl restart brltty
journalctl -u brltty -b --no-pager
```

## Remote GUI Và Security

Remote GUI phải được xem như remote admin surface. Đừng expose trực tiếp ra Internet nếu không có VPN/bastion, MFA, logging, patching và network policy phù hợp.

### X11 Forwarding Qua SSH

Ưu tiên SSH X11 forwarding thay vì mở X11 raw TCP port:

```bash
ssh -X user@remote-host
```

Server SSH cần cho phép:

```text
X11Forwarding yes
```

Validate cấu hình trước khi reload SSH:

```bash
sudo sshd -t
sudo systemctl reload sshd
```

`ssh -Y` là trusted X11 forwarding. Nó nới lỏng kiểm soát bảo mật với remote host, chỉ dùng khi hiểu rõ rủi ro và tin cậy remote host. Tránh dùng `xhost +` hoặc mở X11 TCP `6000-6063` trong network production; nếu bắt buộc cho lab, giới hạn host cụ thể và gỡ quyền sau khi xong.

```bash
xhost +<trusted-host>
xhost -<trusted-host>
```

### Remote Desktop Protocols

| Công nghệ | Port mặc định | Đặc điểm | Guardrail |
| --- | --- | --- | --- |
| VNC/TigerVNC | `5900+n`, web client cũ có thể `5800+n` | Đơn giản, nhiều client, có thể dùng cho VM/desktop | Không mặc định mã hóa đủ mạnh; ưu tiên SSH tunnel/VPN; bảo vệ password file và firewall. |
| Xrdp | `3389/tcp` | Dùng RDP client, quen với user Windows | Kiểm tra TLS/security layer; không để `rdp` insecure trên network không tin cậy. |
| NX/X2Go | Thường qua SSH | Tốt hơn trên link latency cao, có compression/cache | Kiểm soát SSH access như admin surface. |
| SPICE | Tùy hypervisor/proxy | Phổ biến với KVM/libvirt/virtualization console | Dùng TLS/SASL nếu đi qua network không tin cậy; phân quyền console chặt. |

Ví dụ VNC nên đi qua SSH tunnel thay vì mở port rộng:

```bash
ssh -L 5901:127.0.0.1:5901 user@remote-host
vncviewer 127.0.0.1:1
```

Với Xrdp, kiểm tra cấu hình trước khi public service trong network nội bộ:

```bash
systemctl status xrdp
ss -tlnp | grep ':3389'
grep -Ei 'security_layer|certificate|key_file' /etc/xrdp/xrdp.ini
```

Nếu `security_layer=negotiate`, client và server sẽ thương lượng cơ chế bảo mật. Không dùng cấu hình hạ xuống RDP security cũ trên network không tin cậy vì dễ dính rủi ro man-in-the-middle.

## Locale, Encoding Và Timezone

Locale ảnh hưởng cách chương trình hiển thị/sắp xếp text, format số, tiền tệ, ngày giờ và message. Encoding ảnh hưởng khả năng đọc/ghi ký tự đa ngôn ngữ. Với server và container, mặc định an toàn thường là UTF-8 rõ ràng.

Kiểm tra locale:

```bash
locale
locale -ck LC_TIME
locale -ck LC_MONETARY
localectl
localectl list-locales | grep -i 'utf'
```

Thứ tự override thực tế:

| Biến | Vai trò |
| --- | --- |
| `LANG` | Default locale cho các category nếu không bị override. |
| `LC_*` | Override từng category như `LC_TIME`, `LC_NUMERIC`, `LC_COLLATE`. |
| `LC_ALL` | Override toàn bộ, ưu tiên cao; nên dùng tạm thời khi debug/script, không lạm dụng trong profile chung. |
| `TZ` | Override timezone cho process/session hiện tại. |

Ví dụ chạy một lệnh với locale ổn định để parse output:

```bash
LC_ALL=C sort input.txt
LANG=en_US.UTF-8 command
TZ=UTC date
```

Đổi locale hệ thống bằng `localectl` là thay đổi cấu hình host, cần phù hợp với policy image/fleet:

```bash
sudo localectl set-locale LANG=en_US.UTF-8
localectl
```

Chuyển encoding file:

```bash
file -i report.csv
iconv -f ISO-8859-1 -t UTF-8 report.csv > report.utf8.csv
```

Timezone là cách trình bày thời gian, không thay thế time synchronization. Với server production, ưu tiên log bằng UTC hoặc ghi rõ timezone trong RCA. Time sync/NTP chi tiết nằm ở [NTP And Time Synchronization](../../02-network/04-protocols-and-services/05-ntp-time-synchronization.md).

```bash
timedatectl status
timedatectl list-timezones | grep -i Ho_Chi_Minh
sudo timedatectl set-timezone Asia/Ho_Chi_Minh
```

Không chỉnh giờ thủ công trên node đang chạy workload nhạy thời gian nếu chưa có maintenance window. Nhảy thời gian có thể ảnh hưởng certificate, token, distributed lock, cron/timer, log correlation và database.

## Printing Với CUPS

CUPS cung cấp print spooler và print queue cho printer local hoặc network. Các thành phần chính:

| Thành phần | Vai trò |
| --- | --- |
| CUPS daemon | Nhận job, quản lý queue và giao tiếp printer. |
| Print queue | Hàng đợi logic, có thể gắn với một printer hoặc profile in cụ thể. |
| Driver/filter/Ghostscript | Chuyển document sang format printer hiểu được. |
| IPP/SMB | Protocol thường gặp cho network printer. |

Service và cấu hình thường gặp:

```bash
systemctl status cups
ss -tlnp | grep ':631'
ls -la /etc/cups
```

CUPS web interface thường ở:

```text
http://localhost:631/
```

Không expose CUPS admin interface ra network rộng nếu không cần. Nếu phải quản trị từ xa, ưu tiên SSH tunnel/VPN, xác thực mạnh và firewall giới hạn source.

Command line cơ bản:

```bash
lpstat -t
lpq -P <printer>
lpr -P <printer> test.txt
cancel <job-id>
cupsdisable <printer>
cupsenable <printer>
cupsreject <printer>
cupsaccept <printer>
```

Production guardrails:

- Xác nhận printer/queue đúng trước khi gửi job chứa dữ liệu nhạy cảm.
- Kiểm tra job queue trước khi disable/reject queue để tránh ảnh hưởng user.
- Không in log/report có secret, token, private key hoặc customer data ra printer dùng chung.
- Với printer network, kiểm tra IPP/SMB path, firewall, DNS, certificate và driver/filter trước khi kết luận lỗi application.

Troubleshooting nhanh:

```bash
lpstat -t
journalctl -u cups -b --no-pager
grep -Ei 'error|failed|filter|backend' /var/log/cups/error_log 2>/dev/null
```

## Production Checklist

- GUI/remote desktop có thật sự cần trên host đó không, hay có thể thay bằng CLI/API?
- Service GUI có được patch và harden như admin surface không?
- Port remote desktop có bị giới hạn bằng firewall/VPN/bastion không?
- Có dùng SSH tunnel hoặc TLS/SASL khi protocol mặc định không đủ bảo mật không?
- Locale/encoding/timezone có nhất quán giữa dev, CI, container image và production không?
- Log/RCA có ghi timezone rõ ràng không?
- CUPS/remote desktop có thể làm lộ dữ liệu nhạy cảm qua clipboard, drive mount, printer queue hoặc screenshot không?

## Related Pages

- [Linux Overview, Boot Process và Systemd](./01-linux-overview-boot-systemd.md)
- [SSH, JumpHost, LLDP, Bridge và Network Namespace](../02-storage-networking/05-ssh-jumphost-lldp-bridge-netns.md)
- [Linux Commands For Operations](../04-shell-automation-advanced/11-linux-commands-for-operations.md)
- [NTP And Time Synchronization](../../02-network/04-protocols-and-services/05-ntp-time-synchronization.md)
