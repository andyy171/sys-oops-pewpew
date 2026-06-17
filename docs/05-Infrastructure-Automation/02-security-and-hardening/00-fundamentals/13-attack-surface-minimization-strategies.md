# Attack Surface Minimization Strategies

Minimizing attack surface la viec giam so diem attacker co the tim, truy cap, khai thac, di ngang hoac lay du lieu. Trong production, no can ket hop strategic controls dai han va tactical actions gan voi van hanh hang ngay.

## Mental Model

Co 2 lop hanh dong:

- `strategic`: policy, architecture, governance, identity model, zero trust, defense-in-depth, monitoring strategy.
- `tactical`: patch, close port, remove service, segment network, rotate token, tune SIEM, harden endpoint, decommission asset.

Strategic control tao san cho tactical action. Tactical action tao feedback de dieu chinh strategy.

Vi du: khi dang co attack, team co the isolate subnet nhanh hay khong phu thuoc vao viec truoc do da co segmentation, IAM, logging va incident response protocol hay chua.

## Strategic Methods

### Defense-In-Depth

Defense-in-depth dung nhieu lop control de tranh single point of failure:

- perimeter: firewall, WAF, DDoS protection, VPN restriction;
- identity: MFA, SSO, RBAC/ABAC, PAM/JIT;
- network: segmentation, micro-segmentation, egress control;
- endpoint: EDR, hardening baseline, patching, application control;
- data: encryption, DLP, tokenization, backup, retention;
- detection: SIEM, IDS/IPS, NDR, UEBA, threat hunting;
- recovery: backup/restore, IR playbook, DR/BCP.

Layered security khong co nghia them control vo han. Moi layer can co muc dich, owner, signal verify va maintenance path. Qua nhieu control chong cheo nhung khong ai van hanh se tao complexity va blind spot.

### Simplify Security Architecture

Complexity la attack surface. Giam complexity bang cach:

- chuan hoa baseline config;
- xoa legacy exception khong con ly do;
- consolidate tool khi overlap qua cao;
- dung platform policy thay vi manual config le;
- decommission asset khong owner;
- rut gon network path va identity trust relationship.

Don gian hoa phai co kiem soat: khong go bo control chi de "de van hanh" neu risk va compensating control chua ro.

### IAM And Least Privilege

IAM la diem trung tam de giam attack surface:

- SSO giam password sprawl va tap trung lifecycle;
- MFA giam rui ro credential theft;
- RBAC/ABAC gioi han permission theo role, resource, condition;
- OAuth/OIDC giup app khong giu password truc tiep;
- least privilege giam blast radius khi account bi compromise;
- deprovisioning nhanh xoa access cua user/service account khong con nhu cau.

Rui ro thuong gap:

- role qua nhieu va khong ai hieu;
- SSO/IdP thanh crown jewel nhung monitoring yeu;
- OAuth token luu khong an toan;
- session management yeu;
- service account co quyen rong va khong owner;
- access review lam hinh thuc.

### Zero Trust

Zero trust khong phai san pham don le. No la cach thiet ke: `never trust, always verify`.

Core controls:

- continuous verification cho user, device, workload;
- MFA va phishing-resistant MFA cho access quan trong;
- least privilege va JIT access;
- micro-segmentation;
- encryption at rest va in transit;
- policy enforcement engine;
- device posture va context-aware access;
- continuous monitoring va behavior analytics.

Implement zero trust theo giai doan:

1. Inventory user, device, workload, data va flow.
2. Bat MFA/SSO cho high-value app.
3. Review va thu gon privileged access.
4. Segment critical systems va enforce access policy.
5. Dua log identity/network/cloud/app vao monitoring.
6. Mo rong policy theo context va risk.

Khong nen rollout zero trust bang big-bang. Bat dau tu crown jewels va high-risk access path.

### Data Loss Prevention And Cloud Data Controls

Data loss prevention khong chi la DLP appliance. Can layer:

- data classification;
- IAM/RBAC va MFA;
- encryption at rest/in transit;
- DLP content/context inspection;
- CASB cho SaaS/cloud app;
- CSPM de bat cloud misconfiguration;
- DSPM hoac data discovery cho sensitive data exposure;
- behavior analytics de bat data access bat thuong.

Muc tieu la giam ca accidental exposure va malicious exfiltration. DLP rule qua rong se tao false positive va bi bypass; rule qua hep se bo sot leak.

### SIEM, ATP And Detection Strategy

SIEM va advanced threat protection giam attack surface gian tiep bang cach phat hien drift, misuse, exploit attempt va incident som.

Can co:

- log source map cho identity, endpoint, network, cloud, app;
- normalization va enrichment bang asset criticality;
- correlation rule gan voi attack path;
- dashboard co owner;
- tuning false positive;
- playbook cho alert quan trong;
- threat intel feed duoc filter theo context.

SIEM khong co playbook/owner chi tao backlog. ATP/EDR/NDR khong co analyst va response path thi chi la alert source.

### Training And Awareness

Con nguoi la surface that, nhat la phishing, social engineering, misuse access, shadow IT va weak reporting.

Training huu ich khi:

- gan voi threat thuc te cua to chuc;
- co phishing simulation co muc dich hoc tap;
- noi ro cach report incident;
- huong dan secure handling cho data, secret, SaaS, AI tool;
- lap lai theo cadence, khong chi lam mot lan.

## Tactical Techniques

### Network Segmentation

Segmentation gioi han blast radius va lam containment de hon.

Plan segmentation theo:

- asset criticality;
- data sensitivity;
- business function;
- trust boundary;
- admin path;
- vendor/remote access;
- traffic direction va protocol can thiet.

Production guardrails:

- bat dau bang traffic observation/read-only flow map;
- viet policy theo allowlist neu co the;
- test voi representative workload;
- canary mot segment truoc khi rollout rong;
- co rollback cho firewall, route, security group, ACL, network policy;
- monitor denied traffic sau change.

### Vulnerability Management As Surface Reduction

Vulnerability management giam surface khi no dua finding vao context:

- patch nhanh khi co exploit public va patch an toan;
- dung compensating control khi patch chua co hoac khong kha thi;
- monitor heightened khi khong the patch/compensate ngay;
- retest sau remediation;
- communicate bang impact thay vi chi CVSS.

Thach thuc thuong gap:

- thieu budget/personnel;
- vendor cham ra patch;
- moi truong legacy/IoT/ICS kho patch;
- scanner false positive/false negative;
- app owner khong hieu muc do khan cap;
- patch gay regression.

Cach giam rui ro:

- risk-based prioritization;
- automated scanning va patch orchestration;
- staging/canary;
- cross-functional remediation team;
- third-party assessment de validate blind spot;
- clear SLA theo asset tier.

### Endpoint Management

Endpoint management giam entry point va persistence surface:

- close unnecessary ports;
- remove unused service/process/package;
- disable insecure protocol;
- enforce host firewall;
- harden local admin;
- manage USB/removable media khi can;
- EDR/AV policy;
- configuration baseline va drift detection.

Config management can co:

- desired state;
- audit trail;
- approval;
- rollback;
- exception process;
- periodic review.

### Tactical Feedback To Strategy

Moi tactical action nen tao feedback:

- segmentation rule nao bi bypass?
- patch SLA nao hay miss?
- IAM exception nao lap lai?
- alert nao false positive qua nhieu?
- endpoint baseline nao gay breakage?
- team nao thieu owner hoac runbook?

Neu feedback khong quay lai strategy, to chuc se lap lai cung mot remediation moi quy.

## Production Guardrails

- Khong go bo service/port/process tren production neu chua biet dependency.
- Voi segmentation, firewall, IAM, SSO, DNS, route, endpoint hardening: co canary va rollback.
- Voi zero trust/IAM rollout: co break-glass account duoc kiem soat, log va test.
- Voi DLP/CASB: test false positive va user workflow truoc khi block mode.
- Voi SIEM/ATP: khong bat alert moi neu khong co owner va playbook.
- Voi training: khong dung blame-based phishing test; muc tieu la giam incident, khong tao so hai.

## Dau Hieu Minimization Dang Sai

- "zero trust" chi la mua tool, khong co inventory/policy.
- segmentation chi co tren diagram, firewall rule van allow all.
- DLP block qua nhieu lam user tim cach bypass.
- SIEM day alert nhung khong co triage capacity.
- IAM role tang lien tuc nhung khong review.
- patching nhanh nhung khong co rollback/validation.
- strategic roadmap xa voi kha nang van hanh cua tactical team.

## Related Pages

- [Attack Surface Management](./05-attack-surface-management.md)
- [Attack Surface Categories And Exposure Patterns](./06-attack-surface-categories-and-exposure-patterns.md)
- [Attack Surface Analysis And Mapping](./11-attack-surface-analysis-and-mapping.md)
- [ASM Remediation, Validation And Reporting](./12-asm-remediation-validation-and-reporting.md)
- [Continuous Monitoring And Adaptive ASM](./14-continuous-monitoring-and-adaptive-asm.md)
- [Identity, Authentication And Authorization](../01-access-control/01-identity-authentication-authorization.md)
- [Security Monitoring, SIEM And IoC](../04-security-operations/01-security-monitoring-siem-ioc-and-detection.md)
- [Network Monitoring And Packet Analysis](../02-os-and-network-security/network-monitoring-and-packet-analysis.md)
