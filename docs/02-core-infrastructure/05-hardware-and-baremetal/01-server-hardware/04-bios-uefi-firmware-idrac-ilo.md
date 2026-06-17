# BIOS, UEFI, Firmware, iDRAC Và iLO

## Physical Access Threat Model

Physical access có thể bypass nhiều control phần mềm. Nếu attacker chạm được vào máy, họ có thể:

- boot từ USB/live media để đọc hoặc sửa filesystem nếu storage không được mã hóa;
- thay disk, NIC, USB dongle hoặc gắn hardware keylogger;
- vào firmware setup để đổi boot order, tắt security feature hoặc bật management interface;
- dùng out-of-band management như iDRAC/iLO/IPMI nếu credential hoặc network bị lộ.

Production guardrails:

- Hạn chế access vật lý vào rack, console, KVM, iDRAC/iLO/IPMI và media mount.
- Tắt boot từ USB/network nếu không cần; khi cần rescue phải có change/approval.
- Dùng firmware/BIOS password theo policy và lưu trong password vault.
- Bật Secure Boot/TPM/FDE khi môi trường hỗ trợ và đã test rollback.
- Không coi disk encryption là đủ nếu máy đang bật, đã unlock hoặc attacker có admin/root runtime.

## Firmware And Boot Security

Firmware nằm trước OS trong boot chain. Lỗi firmware, bootloader hoặc option ROM có thể làm hỏng toàn bộ trust chain.

Checklist:

- Theo dõi firmware advisory cho BIOS/UEFI, RAID/HBA, NIC, BMC, disk/SSD và TPM.
- Test firmware update trên lab/canary trước khi rollout fleet.
- Có maintenance window, backup config, out-of-band access và rollback plan nếu vendor hỗ trợ.
- Sau update, validate boot mode, Secure Boot state, storage controller mode, NIC PXE/iSCSI setting và virtualization extension.

Secure Boot giúp chỉ load boot component đã ký/trust theo policy. Nó giảm rủi ro bootkit nhưng có thể ảnh hưởng custom kernel, driver hoặc appliance. Không bật rộng trên production nếu chưa test driver, initramfs, recovery media và kernel update flow.

## TPM And Trusted Computing

TPM là phần cứng lưu key/measurement an toàn hơn so với file thường trên disk. Use case phổ biến:

- measured boot và remote attestation;
- BitLocker/FDE unlock policy;
- bảo vệ key material khỏi bị copy trực tiếp khỏi filesystem;
- chứng minh thiết bị đang ở trạng thái boot tin cậy trước khi cấp access.

TPM không tự làm hệ thống an toàn. Nếu OS đã boot và attacker có quyền admin/root, dữ liệu đã decrypt vẫn có thể bị đọc. TPM cần đi cùng Secure Boot, patching, endpoint hardening, logging và physical access control.

## USB, Bluetooth And RFID Controls

Removable và wireless peripheral mở thêm attack path ngoài network thông thường:

| Công nghệ | Rủi ro chính | Guardrail |
|---|---|---|
| USB storage/HID | malware, data exfiltration, rogue keyboard, boot bypass | device control, disable autorun, restrict USB class, encrypt approved drives, log mount events |
| Bluetooth | insecure pairing, impersonation, eavesdropping gần thiết bị, data theft | tắt khi không dùng, enforce secure pairing, hạn chế discoverable mode, monitor corporate endpoint |
| RFID/NFC | skimming, cloning, unauthorized access badge/payment read | dùng encrypted/authenticated tag khi phù hợp, shield khi không dùng, monitor access anomaly |

Với môi trường nhạy cảm, policy nên định nghĩa rõ thiết bị nào được phép, ai phê duyệt, log nào được thu và cách xử lý thiết bị lạ cắm vào host.

## IoT And Smart Device Guardrails

IoT device thường yếu ở default credential, firmware cũ, cloud dependency và logging hạn chế. Khi đưa IoT vào mạng doanh nghiệp:

- đổi default password và tắt account/service không dùng;
- đặt vào VLAN/segment riêng, hạn chế east-west traffic;
- block outbound không cần thiết và log DNS/egress;
- theo dõi firmware lifecycle và EOL;
- không dùng chung network với server/admin workstation nếu không có policy rõ;
- inventory owner, model, serial, firmware, cloud account và physical location.
