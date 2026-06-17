# Open Source Governance And Compliance

## Overview

Open source governance là cách tổ chức kiểm soát việc dùng, đóng góp, phát hành và vận hành phần mềm mã nguồn mở mà không biến license/compliance thành việc xử lý thủ công ở cuối release. Trong môi trường production, đây là một phần của supply chain: dependency, source modification, artifact, hosted service, documentation, SLA và data processing đều phải có owner, policy và bằng chứng kiểm tra.

Điểm quan trọng: open source thường giảm license fee, nhưng không làm tổng chi phí vận hành bằng không. Chi phí chuyển sang review license, SCA/SBOM, security response, integration, support, community work, upstream contribution và trách nhiệm duy trì fork nếu tách khỏi upstream.

## Project And Release Governance

Open-source project vẫn cần release governance giống một sản phẩm production. Roadmap, milestone, issue tracker và changelog giúp cộng đồng hiểu hướng đi; release manager giúp biến thay đổi rời rạc thành phiên bản có thể hỗ trợ.

Các vai trò thường gặp:

| Vai trò | Trách nhiệm chính | Guardrail |
| --- | --- | --- |
| Project lead/maintainer | Quyết định hướng kỹ thuật, tiêu chuẩn merge, quyền committer và conflict quan trọng | Không dùng quyền maintainer để bỏ qua security/compliance gate |
| Release manager | Chốt scope release, theo dõi freeze, kiểm tra release candidate, publish artifact và changelog | Release phải trace được source commit, SBOM, test result, signature/digest nếu có |
| Committer/reviewer | Review patch, enforce coding standard, hướng dẫn contributor mới | Reject thay đổi bằng lý do kỹ thuật rõ, không để review thành cổng cá nhân |
| Community manager | Giữ giao tiếp xây dựng, xử lý abuse/dispute, điều phối event/forum | Code of Conduct phải có cách report và escalation thực tế |

Vòng đời release nên tách rõ:

| Trạng thái | Ý nghĩa vận hành |
| --- | --- |
| Alpha | Dùng để thử ý tưởng hoặc API chưa ổn định; không nên dùng production trừ môi trường lab có kiểm soát |
| Beta | Tính năng gần hoàn chỉnh hơn nhưng vẫn cần feedback rộng; cần ghi rõ breaking change và data migration risk |
| Release Candidate | Ứng viên stable; chỉ nhận bug fix/security fix trước khi publish |
| Stable | Có changelog, artifact, tag, documentation và upgrade path rõ |
| LTS | Nhánh được hỗ trợ lâu hơn, thường ưu tiên security/backport hơn feature mới |
| EOL | Hết support chính thức; dùng tiếp nghĩa là tổ chức phải tự nhận rủi ro patch/security/backport |

Semantic versioning là quy ước giao tiếp thay đổi: `MAJOR.MINOR.PATCH`. `MAJOR` thường báo breaking change, `MINOR` thêm tính năng tương thích ngược, `PATCH` sửa lỗi. Với version `0.x`, không nên giả định API đã ổn định trừ khi project nói rõ.

Trước khi dùng một bản release cho production:

1. Đọc changelog và migration note, đặc biệt breaking change, deprecated feature và security fix.
2. Kiểm tra release artifact có tag/source commit rõ, checksum/signature nếu project cung cấp.
3. Kiểm tra version có còn supported hay sắp EOL.
4. Test upgrade/rollback trên staging với dữ liệu gần production.
5. Ghi rõ owner chịu trách nhiệm nếu phải dùng bản EOL hoặc fork nội bộ.

Nếu buộc phải vận hành phần mềm đã EOL, không coi đó là "ổn vì vẫn chạy". Cần tạo risk acceptance có thời hạn, tự theo dõi CVE/upstream advisory, duy trì patch/backport hoặc kế hoạch thay thế. Rollback khi gặp lỗi EOL thường khó hơn vì upstream không còn cung cấp fix chính thức.

## Business And Operating Model

Các mô hình thường gặp:

| Mô hình | Giá trị bán ra | Guardrail vận hành |
| --- | --- | --- |
| Support subscription | Hỗ trợ, update, security advisory, response time | Cần SLO/SLA rõ, scope version rõ, escalation rõ |
| Hosted service/SaaS | Vận hành phần mềm thay khách hàng | Cần ToS, AUP, DPA, backup, data export, availability target |
| Self-hosted distribution | Khách hàng tự vận hành trên hạ tầng của họ | Cần install/upgrade/rollback docs, compatibility matrix, support boundary |
| Open core/freemium | Core mở, tính năng enterprise/proprietary tính phí | Cần boundary rõ để tránh làm community mất niềm tin |
| Dual licensing | Một codebase có license open source và commercial | Cần kiểm soát copyright ownership/CLA/assignment trước khi cấp license thương mại |
| Consulting/training/custom work | Kiến thức, triển khai, feature theo khách hàng | Cần quyết định phần custom có upstream lại hay giữ riêng |
| Hardware/appliance | Phần mềm mở đi kèm thiết bị hoặc product vật lý | Cần source offer, notice bundle, firmware/update policy và export/privacy review |

Hosted service thường hấp dẫn vì khách hàng không cần vận hành. Đổi lại, nhà cung cấp giữ trách nhiệm về availability, security, backup, incident response, privacy và data processing. Self-hosted phù hợp khi khách hàng cần kiểm soát dữ liệu, custom sâu hoặc tránh vendor lock-in, nhưng khách hàng phải trả chi phí vận hành, upgrade và scaling.

## Service Contract Guardrails

Khi cung cấp dịch vụ dựa trên open source, tách rõ các lớp hợp đồng:

- `ToS`: điều khoản sử dụng dịch vụ, billing, termination, acceptable behavior và quyền/nghĩa vụ chung.
- `AUP`: hành vi bị cấm như spam, abuse, fraud, crypto mining trái phép, malware, scan không được phép hoặc vi phạm policy.
- `SLO`: mục tiêu kỹ thuật nội bộ hoặc công khai, ví dụ availability, latency, support response, backup RPO/RTO.
- `SLA`: cam kết hợp đồng và remedy khi không đạt SLO, ví dụ service credit hoặc penalty.
- `DPA`: trách nhiệm giữa data controller và data processor khi xử lý dữ liệu cá nhân.

Pre-check trước khi ký SLA/DPA:

1. Xác định dữ liệu nào được xử lý, lưu ở region nào, ai có quyền truy cập và log/audit nào được giữ.
2. Xác định shared responsibility giữa provider và customer cho patching, backup, restore, access control và incident response.
3. Kiểm tra khả năng đo SLO bằng telemetry thực tế; không cam kết metric chưa đo được.
4. Kiểm tra backup/restore và data export trước khi bán cam kết availability hoặc exit path.
5. Kiểm tra open-source license của thành phần runtime, đặc biệt AGPL/network copyleft nếu service expose phần mềm qua network.

## Compliance Release Gate

Release có chứa open-source component nên đi qua gate tối thiểu:

| Gate | Câu hỏi cần trả lời |
| --- | --- |
| Inventory | Artifact/image/release chứa package, version, source URL và license nào? |
| License retention | License file, copyright notice và attribution có được giữ nguyên không? |
| Copyleft trigger | Có distribution, appliance, SDK, static linking, derivative work hoặc network copyleft không? |
| Source obligation | Có cần source offer/source bundle cho binary hoặc firmware không? |
| Patent/trademark | License có patent grant/termination không? Logo/name có trademark guideline không? |
| Security | Component có CVE, maintainer risk, stale upstream hoặc suspicious release không? |
| Provenance | Build có commit SHA, workflow, builder identity, digest và SBOM không? |
| Exception | Nếu policy bị vi phạm, exception có owner, expiry, scope và legal/security approval không? |

Không xóa license header hoặc upstream notice khỏi source vendored. Việc này vừa làm mất trace compliance, vừa có thể tạo rủi ro copyright/plagiarism.

## OSPO Operating Model

Open Source Program Office (OSPO) là function điều phối policy, training, tooling và community engagement cho open source. OSPO không nhất thiết là phòng ban lớn; trong tổ chức nhỏ, đó có thể là nhóm liên chức năng gồm engineering, security, legal/compliance và product.

Các trách nhiệm thực tế:

- Định nghĩa policy dùng open source: allowlist/denylist license, usage mode, exception process.
- Định nghĩa policy đóng góp upstream: ai được đại diện công ty, quy trình review, CLA/DCO, security disclosure.
- Chuẩn hóa tooling: SCA, SBOM, SPDX/CycloneDX, dependency review, secret scanning, provenance/signing.
- Lưu bằng chứng: SBOM theo artifact digest, license scan result, notice bundle, source bundle, exception record.
- Đào tạo developer và reviewer để không đưa compliance vào cuối release.
- Điều phối với legal/security khi có copyleft, patent, trademark, export, privacy hoặc M&A due diligence.

## Contribution Governance

Contribution không chỉ là code. Tài liệu, bug report, test case, translation, design, support forum, website, event và review đều là đóng góp có giá trị nếu project có cách tiếp nhận rõ.

Maintainer nên công khai tối thiểu:

- cách mở issue/bug report và thông tin cần có để tái hiện lỗi;
- coding style, test expectation và review process;
- tiêu chí nhận/reject contribution;
- quy trình security disclosure riêng cho vulnerability;
- Code of Conduct và cách báo cáo harassment/abuse;
- cách ghi nhận contributor ngoài code.

Trước khi nhân viên đóng góp upstream:

1. Xác định code có thuộc công ty, khách hàng hay dự án cá nhân không.
2. Kiểm tra contributor có quyền gửi code theo license của upstream không.
3. Kiểm tra CLA, DCO hoặc Copyright Assignment Agreement nếu dự án yêu cầu.
4. Không gửi secret, customer data, private hostname, internal IP, roadmap nhạy cảm hoặc workaround chưa được công bố.
5. Nếu contribution liên quan security fix, tuân theo disclosure process của upstream.

CLA cấp quyền rộng hơn cho project sử dụng contribution; DCO thường là xác nhận ngắn rằng contributor có quyền đóng góp. Copyright assignment chuyển quyền sở hữu nhiều hơn và cần legal review kỹ hơn.

## Communication And Collaboration Governance

Dự án open source thường phân tán theo múi giờ, ngôn ngữ, tổ chức và mức độ tham gia. Vì vậy công cụ giao tiếp không chỉ để nói chuyện; chúng giữ kiến thức, giảm bus factor và giúp contributor mới biết nên bắt đầu ở đâu.

| Kênh/công cụ | Phù hợp cho | Guardrail |
| --- | --- | --- |
| Synchronous chat/video | Trao đổi nhanh, xử lý xung đột, onboarding, quyết định cần tương tác trực tiếp | Ghi lại decision/action item sau họp để người không tham dự vẫn theo được |
| Asynchronous email/forum | Thảo luận thiết kế, quyết định dài hạn, review proposal qua nhiều múi giờ | Viết rõ context, tránh gửi secret/customer data; giả định nội dung có thể public/archived |
| Mailing list/newsletter | Thông báo release, security advisory, roadmap, thảo luận cộng đồng | Tách announcement khỏi discussion; cảnh báo archive công khai nếu có |
| Issue/bug tracker | Bug report, feature request, triage, ownership, backlog | Template cần có version, environment, reproduce steps, expected/actual result, log đã sanitize |
| Pull/Merge request | Review code/docs/config trước khi merge | Require CI, reviewer, security/compliance check khi chạm vùng nhạy cảm |
| Wiki/documentation site | Knowledge base, onboarding, meeting notes, user/admin/developer docs | Có owner, review định kỳ và phiên bản hóa khi docs gắn với release |
| CMS | Xuất bản website/product/community content | Phân quyền editor/publisher, review nội dung public và asset/license trước khi publish |
| DMS | Tài liệu nội bộ như hợp đồng, invoice, legal, HR, finance | Không trộn với public docs; kiểm soát retention, access và audit |

Bug report tốt giúp maintainer tái hiện lỗi thay vì đoán:

```text
version / commit / image tag
environment
steps to reproduce
expected result
actual result
logs or screenshots with secrets redacted
impact and workaround
```

Với communication platform, phân biệt ba mô hình:

- independent/self-hosted: cộng đồng kiểm soát dữ liệu và policy, nhưng phải tự vận hành backup, security và availability;
- federated/decentralized: nhiều server độc lập vẫn giao tiếp được với nhau, giảm phụ thuộc một nhà cung cấp;
- centralized/vendor-hosted: dễ tiếp cận nhiều người dùng nhưng dữ liệu, retention và ToS nằm dưới quyền nhà cung cấp.

Production/community guardrails:

- không paste secret, token, private hostname, customer data, internal IP hoặc exploit chưa disclosed vào mailing list, issue public, chat public hoặc AI/code-generation tool;
- nếu cần log/debug artifact, redact trước và dùng kênh private có retention phù hợp;
- decision quan trọng nên nằm ở issue/PR/design doc có link ổn định, không chỉ trong chat;
- notification policy cần giảm noise để contributor không bỏ lỡ security/release signal quan trọng;
- tài liệu nên tách audience: user docs, admin/operator docs, developer/architecture docs và release/migration notes.

## Fork Risk

Fork có thể hợp lý khi upstream không nhận patch, roadmap lệch nhu cầu, cần bản hardened riêng hoặc phải duy trì compatibility đặc biệt. Nhưng fork tạo nghĩa vụ vận hành dài hạn.

Rủi ro cần tính trước:

- phải backport security fix từ upstream,
- phải maintain CI, release, packaging và documentation riêng,
- dễ diverge khỏi ecosystem và plugin/API compatibility,
- khó tuyển người nếu fork quá khác upstream,
- dễ làm cộng đồng mất niềm tin nếu fork được dùng để né contribution hoặc đổi license bất ngờ.

Ưu tiên upstream-first khi có thể: giữ patch nhỏ, gửi sớm, theo coding standard của project, tham gia discussion trước khi viết feature lớn và tránh dùng tiền/tài trợ để ép roadmap.

## Incident Response

Khi phát hiện license/compliance issue sau release:

1. Freeze release line hoặc artifact bị ảnh hưởng nếu có rủi ro redistribution/legal exposure.
2. Xác định artifact/image digest, customer scope, usage mode và component liên quan.
3. Thu thập SBOM, license scan, source diff, build provenance và notice bundle hiện có.
4. Escalate legal/security/compliance nếu liên quan copyleft, patent, trademark, privacy, export hoặc customer contract.
5. Remediate bằng cách thay dependency, tách component, bổ sung notice/source bundle, publish fixed artifact hoặc thương lượng commercial license nếu phù hợp.
6. Sau remediation, cập nhật policy gate để lỗi tương tự không lặp lại.

## Related Pages

- [SBOM And Dependency Tracking](./SBOM%20&%20dependency%20tracking.md)
- [CI/CD Threat Model And Attack Surface](./04-ci-cd-threat-model-and-attack-surface.md)
- [Image Scanning And Registry Integrity](./01-Image%20scanning.md)
