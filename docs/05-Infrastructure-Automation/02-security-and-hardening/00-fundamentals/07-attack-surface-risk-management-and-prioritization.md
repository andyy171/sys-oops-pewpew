# Attack Surface Risk Management And Prioritization

Attack Surface Management chi co gia tri khi no giup to chuc ra quyet dinh uu tien dung. Biet asset nao ton tai la buoc dau; biet risk nao can xu ly truoc, xu ly bang cach nao, va giai thich duoc cho business la buoc bien ASM thanh nang luc thuc te.

## Mental Model

Risk trong ASM khong chi la `co vulnerability`. Mot risk co y nghia khi 4 thanh phan giao nhau:

- asset co gia tri voi business;
- asset co exposure thuc te;
- attacker co duong khai thac kha thi;
- tac dong cua su co du lon de can hanh dong.

Cong thuc don gian de suy nghi:

`risk = impact x likelihood`, nhung phai dat trong ngu canh cua business, ownership, va control dang co.

## Risk Treatment Options

Khong phai risk nao cung duoc giai bang patch. Cac cach xu ly pho bien:

- `avoid`: khong dung dich vu, feature, integration, hoac quy trinh do nua.
- `mitigate`: bo sung control de giam likelihood hoac impact.
- `accept`: chap nhan risk co owner, ly do, va thoi han review ro rang.
- `transfer`: chuyen mot phan risk qua insurance, managed service, hoac hop dong vendor.
- `share`: chia risk va trach nhiem qua partnership hoac joint operation.
- `enhance`: tang kha nang cua co hoi co loi neu day la risk theo nghia business upside.

Trong security practice, 3 lua chon dung nhieu nhat la `avoid`, `mitigate`, `accept`.

## Cac Yeu To Nen Danh Gia Truoc Khi Uu Tien

### Risk Appetite

Moi to chuc co muc chap nhan risk khac nhau. Muc nay anh huong truc tiep den viec:

- co chap nhan temporary exposure hay khong;
- co the tri hoan remediation hay khong;
- co duoc phep mo dich vu moi khi control chua day du hay khong.

Neu khong xac dinh risk appetite, backlog se bi chi phoi boi ai noi to hon, khong phai asset nao nguy hiem hon.

### Impact And Likelihood

2 cau hoi can tra loi:

- neu bi khai thac, business mat gi;
- kha nang bi khai thac co cao khong.

Impact can tinh den:

- doanh thu;
- nang suat van hanh;
- data sensitivity;
- compliance;
- uy tin va trust voi khach hang;
- blast radius sang he thong khac.

Likelihood can tinh den:

- asset co public khong;
- attacker co dang nham vao surface nay khong;
- exploit co san khong;
- control dang co manh den dau;
- asset co dang stale, misconfigured, hoac overprivileged khong.

### Cost-Benefit And Resource Availability

Khong phai luc nao chi phi mitigation cung hop ly. Mot control co the qua dat, qua cham, hoac gay operational friction lon hon risk dang can giam.

Nhung day khong dong nghia de acceptance tro thanh "de sau". Neu chon accept risk:

- phai co owner;
- phai co ly do business;
- phai co moc review lai;
- phai biet control bo tro nao dang giam blast radius.

### Strategic Goals And Compliance

Co risk duoc uu tien cao vi no can tro muc tieu chien luoc:

- mo rong cloud;
- M&A;
- dua san pham ra thi truong;
- dat audit requirement;
- giam downtime cho workload core.

Compliance cung co the ep team chon avoid hoac mitigate thay vi accept, nhat la voi PII, PHI, payment data, hoac privileged access.

## Qualitative, Quantitative, Hay Mixed

### Qualitative Risk Assessment

Phu hop khi:

- du lieu lich su it;
- moi truong doi nhanh;
- can quyet dinh nhanh;
- team muon co buc tranh risk thuc dung ma khong ton qua nhieu chi phi.

Dau vao thuong la:

- expert judgment;
- business context;
- muc do public exposure;
- asset criticality;
- threat trend.

Uu diem:

- nhanh;
- re hon;
- de giai thich;
- hop voi cloud, SaaS, hoac surface moi mo ra.

Nhuoc diem:

- de bi bias;
- kho so sanh neu tieu chi moi team moi khac;
- khong du chinh xac cho bai toan tai chinh chi tiet.

### Quantitative Risk Assessment

Phu hop khi:

- co du lieu lich su tin cay;
- can buoc risk vao tien, downtime, productivity, hoac ROI;
- can justify investment voi board, finance, hoac auditor.

Uu diem:

- so sanh duoc giua cac risk;
- de uu tien theo business impact that;
- de theo doi thay doi theo thoi gian.

Nhuoc diem:

- can data tot;
- can model va ky nang phan tich;
- ton CPU, cong cu, va nhan luc;
- de tao cam giac "chinh xac gia" neu input khong tot.

### Mixed Approach

Trong nhieu to chuc, `mixed` la lua chon dung nhat:

- qualitative de triage nhanh va thu hẹp danh sach;
- quantitative de phan tich sau cho nhom risk top tier hoac quyet dinh dau tu.

Dung mixed khi:

- stakeholder vua can narrative vua can con so;
- risk phuc tap va anh huong qua nhieu phong ban;
- can quyet dinh chi phi - hieu qua cua security control.

## Framework Fit Cho ASM

Framework khong thay ASM, nhung no tao khung de bien discovery thanh quyet dinh.

### NIST RMF

Phu hop voi:

- to chuc can compliance nghiem ngat;
- he thong lon, nhieu process, can artifact va bang chung ro;
- moi truong can control selection, assessment, authorization, continuous monitoring.

Trade-off:

- rat ton tai nguyen;
- de qua tai voi team nho;
- neu khong duy tri cap nhat, artifact se nhanh mat gia tri.

### ISO 31000

Phu hop voi:

- to chuc muon khung risk management rong, linh hoat, co the dung da quoc gia;
- doanh nghiep can lien ket risk voi governance va resilience.

Trade-off:

- tong quat nen can customization;
- van doi hoi ky nang va commitment lien tuc.

### ITIL v4

Phu hop voi:

- to chuc co IT service management la trung tam;
- data center, managed service, large IT operation;
- moi truong can gan risk vao lifecycle cua service.

Trade-off:

- de nang ve process;
- co the cham so voi moi truong doi qua nhanh neu khong adapt tot.

### COSO ERM

Phu hop voi:

- to chuc lon;
- muon gan risk voi strategy, governance, performance;
- can lan toa risk ownership qua nhieu bo phan.

Trade-off:

- kho trien khai dong bo;
- can stakeholder buy-in manh;
- qua suc voi team nho neu ap day du.

### OCTAVE

Phu hop voi:

- to chuc muon operational team tu tham gia danh gia risk;
- medium-size org co kha nang dau tu vao self-assessment.

Trade-off:

- ton thoi gian cua team van hanh;
- khong de scale neu to chuc rat lon hoac thay doi qua nhanh.

## Workflow Uu Tien Risk Trong ASM

1. Chot scope ASM theo business flow hoac attack surface domain.
2. Lap asset inventory co owner, criticality, data sensitivity, va exposure status.
3. Gom threat trend, finding, control gap, incident history.
4. Chon model danh gia:
   - qualitative cho triage ban dau;
   - quantitative cho risk top tier hoac investment decision;
   - mixed khi can ca hai.
5. Xep hang risk theo impact, likelihood, va business context.
6. Chot risk treatment: avoid, mitigate, accept, transfer.
7. Gan owner, due date, verification signal, va rollback plan neu co thay doi production.
8. Communicate lai cho stakeholder bang ngon ngu ho hieu va co action item cu the.
9. Review lai dinh ky hoac moi khi attack surface doi.

## Production Guardrails

### Truoc Khi Uu Tien

- Khong dung severity scanner la bien duy nhat.
- Khong gom tat ca internet-facing asset vao mot bucket chung; phai tach theo data va blast radius.
- Kiem tra xem finding co exploit path thuc te khong.

### Truoc Khi Chon Risk Acceptance

- Xac nhan ai la risk owner cap business.
- Document compensating control dang ton tai.
- Dat moc review lai, nhat la voi temporary exception.

### Truoc Khi Mitigate Trong Production

- Danh gia impact cua thay doi len auth, traffic, latency, deployment, hoac user flow.
- Co rollback ro rang neu thay doi lien quan IAM, network path, TLS, WAF, SSO, storage policy.
- Chuan bi signal verify sau thay doi: denied event, reduced exposure, health check, user flow test.

## Cach Noi Risk Bang Ngon Ngu Business

Noi `CVSS 8.8` thuong khong du. Stakeholder can hieu:

- chuyen gi se xay ra;
- he thong nao bi anh huong;
- du lieu nao co the lo;
- chi phi downtime hay compliance la gi;
- can quyet dinh gi ngay bay gio.

Hay doi tu:

- "co SQL injection CVSS cao"

thanh:

- "public web interface co the bi dung de doc hoac sua du lieu khach hang; neu xay ra co the gay gian doan giao dich va incident disclosure."

### Nguyen Tac Giao Tiep

- noi theo muc tieu cua nguoi nghe: revenue, uptime, compliance, customer trust, productivity;
- dung visual don gian: heatmap, ranking, dashboard, blast-radius sketch;
- luon kem recommendation co action;
- lap cadence de stakeholder khong chi nghe khi co su co.

### 6 Buoc Doi Technical Risk Thanh Business Language

1. Xac dinh risk ky thuat quan trong nhat.
2. Bo jargon khong can thiet.
3. Mo ta impact len business operation va du lieu.
4. Noi ro muc uu tien va vi sao.
5. Dua ra action de nghi.
6. Review lai voi nguoi khong technical de chac rang thong diep de hieu.

## Dau Hieu Quy Trinh Uu Tien Dang Sai

- moi finding deu bi gan `critical`;
- board nhan dashboard nhung khong biet can phe duyet gi;
- remediation backlog lon nhung van khong giam user impact;
- team security noi bang framework, CVSS, exploit chain, nhung business khong thay lien quan;
- decision acceptance duoc dua ra nhung khong co owner hoac review date.

## Related Pages

- [Attack Surface Management](./05-attack-surface-management.md)
- [Attack Surface Categories And Exposure Patterns](./06-attack-surface-categories-and-exposure-patterns.md)
- [Attack Surface Analysis And Mapping](./11-attack-surface-analysis-and-mapping.md)
- [ASM Remediation, Validation And Reporting](./12-asm-remediation-validation-and-reporting.md)
- [Asset Prioritization And Crown Jewel Analysis](./10-asset-prioritization-and-crown-jewel-analysis.md)
- [Threat Modeling, Vulnerability Management And Application Security](./04-threat-modeling-vulnerability-management-and-application-security.md)
- [Incident Response Overview](../incident-response-overview.md)
