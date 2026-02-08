---
id: INC-2026-02-10-001
title: "Cinder backup double size — ClusterA"
date: 2026-02-10
---

## Metadata (quick view)

| Field    | Value |
|---------:|:------|
| ID       | INC-2026-0210-001 |
| Date     | 2026-02-10 |
| Systems  | OpenStack, Ceph |
| Severity | P2 |
| Status   | investigating |
| Owner    | team-storage |

---

## 1) Summary
Ngắn gọn (1-2 câu): Backup volume 150GB xuất ra tệp backup ~300GB; nghi vấn sparse-map / cinder fallback.

## 2) Impact
- Affected clusters: ClusterA
- Users: backup jobs của tenant X
- Pager/alerts: backup-size-alert@pager

## 3) Timeline (UTC+7)
- 2026-02-10 08:12 — Alert: backup-size > threshold
- 2026-02-10 08:15 — Triage: chạy `rbd du ...`
- 2026-02-10 08:30 — Collected logs: `cinder-volume` + `rbd info`

## 4) Evidence (extracts & links)
- `rbd du` output: `<snippet>`
- cinder log excerpt: `<snippet>`
- Full artifacts: `artifacts/INC-2026-0210-001/`

## 5) Triage steps executed (commands + output snippets)
- `rbd info pool/vol` → ...
- `cinder-manage backup` → ...

## 6) Root cause analysis
(Đặt kết luận ở đây, chứng minh bằng evidence).

## 7) Fix / Mitigation
(Đã làm gì, rollback, temporary mitigation)

## 8) Postmortem & Action items
- [ ] Add detection rule (owner: devops) — due: 2026-02-20
- [ ] Update pattern PAT-001 with new variant — owner: storage-eng

## 9) References
- Pattern: `patterns/PAT-001-rbd-sparse-map-unavailable.md`
- Ceph doc: `../../02-core-infrastructure/.../02-Ceph-Storage/02-operations.md`

