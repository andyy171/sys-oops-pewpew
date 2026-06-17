# Emerging ASM Risks: AI, Quantum And Edge

Attack surface tuong lai khong chi mo rong theo so luong server. No mo rong theo data pipeline, model, edge runtime, third-party intelligence, privacy requirement va crypto dependency. Note nay gom cac risk dang tang trong ASM de dung nhu watchlist va guardrail khi thiet ke chuong trinh security dai han.

## Mental Model

Emerging ASM risks co 3 dac diem:

- `dynamic`: asset xuat hien va bien mat nhanh hon inventory truyen thong.
- `interconnected`: AI, API, cloud, vendor, edge va data pipeline phu thuoc lan nhau.
- `hard to validate`: control co the nam trong model, provider, pipeline hoac algorithm nen kho kiem tra bang scan co dien.

ASM can chuyen tu "scan theo lich" sang "visibility + governance + feedback loop".

## AI And ML In ASM

AI/ML co the giup ASM:

- phat hien anomaly tren log, traffic, API va user behavior;
- reduce alert noise bang behavior baseline;
- enrich finding bang threat intelligence;
- uu tien alert theo risk score;
- ho tro threat hunting;
- tom tat incident va giai thich signal;
- goi y remediation hoac detection rule.

Nhung AI khong phai control tu dong dang tin tuyet doi. Can guardrails:

- khong paste secret, token, private key, customer data, PII, PHI, regulated data vao public AI tool;
- log prompt/output quan trong neu dung AI cho security decision;
- validate output bang evidence, khong tin hallucination;
- review model drift va data quality;
- co human approval cho action co blast radius cao;
- tach dev/test/prod cho AI workflow;
- document provider, retention, training-data policy va compliance impact.

## AI-Specific Attack Vectors

| Vector | Risk | Guardrail |
|---|---|---|
| Guardrail jailbreak | Model bo qua safety policy va sinh output nguy hiem | Prompt hardening, output filter, abuse monitoring, policy test |
| Prompt injection | Input dieu khien model lam ngoai y dinh | Treat prompt/user input as untrusted, context isolation, allowlist action |
| Information disclosure | Model lo training data, secret, system prompt hoac context nhay cam | Data minimization, redaction, retrieval filtering, output review |
| Content manipulation | Output sai co chu dich, poisoning hoac adversarial example | Model evaluation, trusted data source, human review cho decision quan trong |
| Denial of service | Inference/resource bi lam can kiet | Rate limit, quota, circuit breaker, cost monitoring |
| Training data leakage | Query co the trich xuat du lieu training nhay cam | Avoid sensitive raw data, privacy review, synthetic/anonymized data khi phu hop |
| Training data poisoning | Du lieu doc lam sai model behavior | Data provenance, validation, versioned dataset, approval pipeline |
| Weights disclosure | Lo model weights dan den clone, IP theft, reverse engineering | Access control, encryption, model registry audit, artifact signing |
| Architecture/layer disclosure | Attacker hieu cau truc de craft exploit | Limit debug metadata, secure model docs, restrict admin/control interface |

## AI Attack Surface

AI system co nhieu surface hon UI chat:

- `data ingestion`: external feed, internal repo, real-time stream, data label.
- `user interface`: prompt box, file upload, plugin/action connector.
- `API`: inference API, embedding API, admin API, batch job API.
- `training pipeline`: code, dataset, feature store, model build, evaluation, deployment.
- `pretrained model`: third-party model, hidden backdoor, bias, unknown training data.
- `storage`: training data, vector database, checkpoint, model artifact, operational log.
- `deployment environment`: GPU/accelerator, container, Kubernetes, serverless, edge node.
- `control interface`: admin console, model parameter, access policy, connector permission.

First checks:

- ai co quyen dua data vao training/retrieval/index;
- data nao duoc gui ra provider;
- model/action co the goi tool nao;
- prompt/output co log va redact khong;
- API co auth, rate limit, quota va abuse detection khong;
- model artifact co provenance, signature va access control khong;
- rollback model/prompt/config co duoc test khong.

## Quantum And Crypto-Agility

Quantum risk quan trong voi ASM vi no bien cryptography dependency thanh attack surface dai han. Rui ro lon nhat trong ngan han thuong la `harvest now, decrypt later`: attacker thu thap encrypted traffic/data hom nay de giai ma khi technology cho phep.

Thay vi doan chinh xac timeline, production team nen chuan bi crypto-agility:

1. Inventory cryptography dependency:
   - TLS endpoint;
   - certificate authority;
   - VPN;
   - SSH;
   - database encryption;
   - backup encryption;
   - object storage encryption;
   - signing key;
   - HSM/KMS;
   - embedded/IoT firmware.
2. Phan loai data theo retention va sensitivity.
3. Xac dinh system nao kho doi algorithm/protocol.
4. Thu nghiem post-quantum/hybrid approach trong noncritical path khi toolchain ho tro.
5. Tao crypto-agility plan: owner, dependency, test, rollout, rollback, vendor requirement.
6. Theo doi chuan post-quantum tu cac co quan tieu chuan va vendor chinh, khong tu invent algorithm.

Guardrail: khong thay cryptography production theo phong trao. Moi thay doi TLS, certificate, KMS/HSM, VPN, signing pipeline phai co compatibility test, canary, rollback va observability.

## Edge Computing

Edge computing dua compute/storage gan nguoi dung hoac data source. No giam latency nhung lam perimeter phan manh:

- edge function/API nam o nhieu region;
- workload ephemeral;
- resource nho khong chay duoc agent nang;
- deployment gan voi CI/CD hon la server operations;
- data co the xu ly ngoai data center/cloud region chinh;
- control plane va runtime nam o provider.

ASM cho edge nen focus vao pattern, khong chi tung node:

- IaC/pipeline policy truoc deploy;
- secret scanning va dependency scanning trong CI;
- lightweight runtime telemetry;
- API auth/rate limit;
- egress control;
- behavior-based detection;
- automated rollback/redeploy khi anomaly;
- inventory tu provider API va deployment metadata;
- data residency/compliance review theo region.

Canh bao: neu edge function bi loi, "terminate and redeploy" co the giam dwell time, nhung khong thay root-cause analysis cho secret leak, data exposure hoac supply-chain compromise.

## Collaboration And Shared Intelligence

Attack surface qua rong de moi to chuc tu hoc mot minh. Shared intelligence huu ich khi:

- duoc anonymize/sanitize;
- co governance ve data sharing;
- co legal/compliance review;
- co trust boundary ro;
- co incentive de dong gop signal chat luong;
- co process dua intelligence vao detection/remediation.

Nguon co the gom:

- industry ISAC/ISAO;
- vendor advisory;
- open-source security project;
- bug bounty/VDP;
- community detection rule;
- internal incident repository;
- cross-company tabletop neu co thoa thuan phu hop.

Khong chia se raw log, customer data, secret, token, exploit detail nhay cam hoac thong tin co the lam lo organization-specific weakness neu chua duoc phe duyet.

## Privacy, Insider Risk And Regulatory Pressure

Monitoring manh hon co the xung dot voi privacy neu khong co governance:

- log co the chua personal data;
- behavior analytics co the bi xem la employee surveillance;
- AI decision co the thieu transparency;
- third-party monitoring co the dua data ra ngoai boundary;
- right-to-erasure/retention policy co the xung dot voi forensic retention.

Guardrails:

- data minimization cho log;
- role-based access vao monitoring data;
- retention policy ro;
- legal/privacy review cho UEBA/employee monitoring;
- transparency ve muc dich monitoring;
- vendor privacy/security assessment;
- audit trail cho access vao sensitive telemetry.

Insider risk nen duoc xu ly bang control va culture, khong chi surveillance:

- least privilege;
- separation of duties;
- access review;
- anomaly detection co context;
- offboarding nhanh;
- secure reporting channel;
- fair investigation process.

## Continuous Learning

ASM doi hoi skill cap nhat lien tuc:

- attack simulation va tabletop exercise;
- cross-functional rotation giua security, platform, development, operations;
- secure coding va cloud/IaC training;
- threat modeling practice;
- community engagement va open-source contribution;
- prompt/AI security literacy;
- incident review va lessons learned repository.

Training tot phai tao ra thay doi trong control, detection, pipeline, policy hoac runbook. Neu chi la slide deck hang nam, no khong giam attack surface.

## Production Guardrails

- Khong dua AI vao security workflow neu chua co data-handling policy.
- Khong de AI/SOAR tu dong action high-blast-radius ma khong co approval, audit va rollback.
- Khong bo qua edge workload vi no ephemeral; inventory phai den tu deployment/control plane.
- Khong delay crypto inventory den khi vendor bat buoc migration.
- Khong chia se threat intel neu chua sanitize secret/customer/private data.
- Khong bien insider-risk monitoring thanh surveillance khong minh bach.

## Related Pages

- [Attack Surface Management](./05-attack-surface-management.md)
- [Attack Surface Categories And Exposure Patterns](./06-attack-surface-categories-and-exposure-patterns.md)
- [Continuous Monitoring And Adaptive ASM](./14-continuous-monitoring-and-adaptive-asm.md)
- [Attack Surface Minimization Strategies](./13-attack-surface-minimization-strategies.md)
- [Privacy, Compliance, Cryptography And Data Protection](./02-privacy-compliance-cryptography-and-data-protection.md)
- [Security Monitoring, SIEM And IoC](../04-security-operations/01-security-monitoring-siem-ioc-and-detection.md)
