# Incident Response Overview

Incident response là năng lực phát hiện, phân tích, cô lập, xử lý và phục hồi sau sự cố bảo mật. Note này chuyển hóa các note rời rạc trong `_inbox/Base/security-incidents.md`, `_inbox/Base/log-collection-and-management.md`, `_inbox/Security Tools & Technologies/playbooks.md` và `documentations.md`.

Một chương trình IR tốt cần kết nối với `ISMS`: asset inventory, data classification, access policy, logging standard, backup/DR, legal/privacy contact và communication plan. Nếu các phần này không có trước incident, đội phản ứng sẽ mất thời gian xác định owner, phạm vi dữ liệu, quyền được phép thao tác và nghĩa vụ báo cáo.

## Event Vs Incident

| Khái niệm | Ý nghĩa |
|---|---|
| Event | hoạt động bình thường hoặc bất thường được ghi nhận, ví dụ login, request reset password, process start |
| Alert | tín hiệu được rule/tool đánh dấu cần xem xét |
| Incident | sự kiện đã được xác nhận có ảnh hưởng bảo mật hoặc có khả năng ảnh hưởng nghiêm trọng |

Không phải alert nào cũng là incident. Nhiệm vụ của triage là biến alert thô thành quyết định: bỏ qua, tune rule, theo dõi, escalate hoặc mở incident.

## Incident Lifecycle

```text
prepare -> detect -> triage -> contain -> eradicate -> recover -> lessons learned
```

Trong môi trường vận hành thật, các phase có thể chồng lên nhau. Ví dụ vừa contain host, vừa thu evidence, vừa cập nhật rule để tìm host khác.

`ISIRT` hoặc đội phản ứng sự cố không chỉ gồm kỹ thuật. Tùy mức độ incident, cần có security analyst, system/network/platform engineer, business owner, legal/privacy, communications và management escalation. Vai trò này giúp containment không phá business flow ngoài ý muốn, còn thông tin ra ngoài không vượt quá bằng chứng đã xác nhận.

## Triage Alert

Triage nên trả lời:

1. Alert đến từ nguồn nào: SIEM, IDS, EDR, cloud finding, user report?
2. Có false positive rõ ràng không?
3. Asset bị ảnh hưởng có critical không?
4. Tài khoản nào liên quan, quyền của tài khoản đó ra sao?
5. Có evidence của compromise chưa?
6. Functional impact là gì?
7. Information impact là gì?
8. Recoverability có khó không?

Ma trận ưu tiên tối giản:

| Severity | Khi nào |
|---|---|
| Critical | có compromise trên hệ thống critical, data exfiltration, ransomware, privilege escalation diện rộng |
| High | dấu hiệu attacker active, credential bị lạm dụng, malware trên server quan trọng |
| Medium | suspicious behavior cần điều tra, scope hẹp, chưa có impact rõ |
| Low | false positive tiềm năng, policy violation nhẹ, cần tuning hoặc theo dõi |

## Detection And Analysis

Detection tốt cần cả tool và analyst:

- IDS/IPS phát hiện network signature hoặc behavior.
- EDR phát hiện endpoint process/file/memory/command line.
- SIEM correlate log từ nhiều nguồn.
- Threat hunting tìm threat chưa có alert rõ.
- Threat intelligence thêm context cho IoC/TTP.
- Honeypot/canary giúp tạo tín hiệu có độ tin cậy cao.

Khi phân tích, luôn dựng timeline. Timeline giúp tránh nhìn từng log rời rạc và bỏ lỡ causal chain.

## Evidence Collection

Evidence thường cần:

- alert gốc và rule name;
- affected host/IP/user/service account;
- process tree, command line, parent process;
- network connection, DNS, proxy, firewall log;
- authentication log và privilege change;
- file hash, path, timestamp;
- cloud API activity nếu liên quan;
- screenshot/report chỉ khi cần và không chứa secret.

Không paste token, password, private key, cookie, customer data hoặc PII vào ticket. Dùng placeholder và lưu evidence nhạy cảm ở kho phù hợp.

Nếu incident liên quan hệ thống đang chạy, ưu tiên preserve evidence trước hành động phá hủy trạng thái như reboot, cleanup malware, xóa account hoặc restore đè dữ liệu. Khi cần forensic sâu, ghi chain of custody: ai thu evidence, lúc nào, từ host nào, hash gì, lưu ở đâu và ai được quyền truy cập.

## Containment, Eradication, Recovery

Containment:

- isolate endpoint hoặc subnet nếu cần;
- disable/revoke credential bị nghi compromise;
- block IoC tạm thời ở firewall/WAF/proxy/EDR;
- giữ evidence trước khi kill process nếu cần forensic.

Eradication:

- remove malware/persistence;
- patch vulnerability/root cause;
- rotate key/token/password;
- fix misconfiguration;
- review lateral movement.

Recovery:

- restore service từ backup sạch;
- verify integrity;
- monitor heightened logging;
- rollback temporary block nếu không còn cần;
- xác nhận business owner.

Với takeover database hoặc hệ thống chứa dữ liệu nhạy cảm, trình tự an toàn thường là: cô lập đường truy cập nghi bị lạm dụng, giữ bằng chứng, xác định account/host bị ảnh hưởng, kiểm tra integrity, dựng môi trường sạch khi cần, restore từ backup đã xác minh và rotate credential trước khi mở lại traffic. Không tiếp tục dùng email/chat/host nghi compromise để điều phối incident nhạy cảm.

## Playbooks

Playbook giúp incident không phụ thuộc trí nhớ của một cá nhân.

| Loại | Mô tả |
|---|---|
| Manual playbook | analyst làm từng bước, phù hợp incident phức tạp |
| Automated playbook | SOAR/script tự thu evidence, enrich IoC, phân loại severity |
| Semi-automated playbook | tự động phần lặp lại, human phê duyệt bước rủi ro |

Playbook tối thiểu nên có:

- trigger;
- scope;
- owner/escalation;
- read-only checks;
- containment step;
- rollback;
- evidence cần giữ;
- communication template;
- closure criteria;
- post-incident review.

## Documentation

Tài liệu incident tốt cần:

- rõ audience: analyst, manager, legal, executive hay engineering;
- ngắn gọn nhưng đủ evidence;
- ghi lại lý do ra quyết định, không chỉ ghi hành động;
- có timeline;
- có chain of custody khi evidence phục vụ pháp lý/compliance;
- có lesson learned và action item có owner.

Tài liệu không chỉ để "ghi cho xong"; nó là input cho audit, training, detection improvement và runbook update.

## Business Continuity

Sự cố bảo mật có thể gây downtime hoặc mất dữ liệu như một disaster. `BCP` tập trung duy trì chức năng kinh doanh trong khi `DR` tập trung phục hồi hệ thống sau gián đoạn lớn.

| Site | Đặc điểm |
|---|---|
| Hot site | sẵn sàng gần như ngay, chi phí cao |
| Warm site | đã có hạ tầng/cấu hình chính, cần kích hoạt thêm |
| Cold site | có địa điểm/hạ tầng tối thiểu, cần setup nhiều |

Với ransomware hoặc incident critical infrastructure, incident response phải nối với backup, DR, business owner, legal/compliance và communication plan.

## Post-Incident Review

Sau khi đóng incident:

1. Root cause là gì?
2. Detection nào hoạt động, detection nào thiếu?
3. Control nào fail hoặc bị bypass?
4. Playbook có bước nào gây chậm?
5. Evidence có đủ không?
6. Cần patch, hardening, training hay architecture change?
7. Action item có owner và deadline không?

## Related Pages

- [Security Monitoring, SIEM And IoC](./04-security-operations/01-security-monitoring-siem-ioc-and-detection.md)
- [Threat Actors, Malware And Attack Patterns](./00-fundamentals/03-threat-actors-malware-and-attack-patterns.md)
- [Network Monitoring And Packet Analysis](./02-os-and-network-security/network-monitoring-and-packet-analysis.md)
- [Linux Incident Response Live Triage](../../02-core-infrastructure/01-linux/03-security-logs-troubleshooting/07-linux-incident-response-live-triage.md)
