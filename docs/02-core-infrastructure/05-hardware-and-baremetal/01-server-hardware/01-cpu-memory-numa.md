# CPU, Memory Và NUMA

## Security Mental Model

CPU và RAM không chỉ là capacity. Chúng cũng là security boundary ở mức phần cứng:

- CPU chạy instruction của kernel, hypervisor và workload; lỗi microcode hoặc side-channel có thể làm lộ dữ liệu giữa process, VM hoặc tenant.
- RAM giữ secret tạm thời như session key, decrypted data, credential cache và process memory; dữ liệu có thể còn tồn tại rất ngắn sau power-off hoặc suspend.
- NUMA ảnh hưởng latency và placement; workload nhạy cảm về performance hoặc isolation cần hiểu CPU/socket/memory locality.

## CPU Security

Rủi ro thường gặp:

- Side-channel: attacker suy luận secret qua cache timing, branch prediction hoặc shared execution resource.
- Microcode/firmware flaw: lỗi ở CPU hoặc platform firmware cần vendor update, không chỉ OS patch.
- Overcommit không kiểm soát: trong virtualization, noisy neighbor hoặc workload không tin cậy chia sẻ CPU cache/thread có thể tăng rủi ro leakage và performance jitter.

Guardrails:

- Theo dõi firmware/microcode advisory từ vendor phần cứng, OS và hypervisor.
- Áp dụng mitigation theo risk của môi trường; một số mitigation có cost performance.
- Với workload multi-tenant hoặc regulated, cân nhắc CPU pinning, SMT policy, isolation pool hoặc dedicated host khi threat model yêu cầu.

## Memory Security

Rủi ro thường gặp:

- Cold boot hoặc physical attack có thể cố lấy dữ liệu còn lại trong RAM sau shutdown/suspend.
- Swap, crash dump, core dump hoặc hibernation file có thể ghi secret từ memory xuống disk.
- Memory pressure có thể làm workload nhạy cảm swap dữ liệu ra storage không mã hóa.

Guardrails:

- Bật full-disk encryption cho laptop/admin workstation và host có dữ liệu nhạy cảm.
- Kiểm soát core dump/crash dump trên production; không để dump chứa secret vào bucket/share rộng.
- Với server nhạy cảm, review swap encryption, hibernation policy, out-of-band console access và physical access.
- Dùng ECC RAM cho server production để giảm silent corruption, nhưng ECC không thay thế backup, checksum hoặc application-level integrity.

## Operations Checklist

- Firmware/microcode version có nằm trong baseline được phê duyệt không?
- SMT/NUMA/pinning policy có phù hợp workload không?
- Swap/dump/hibernation có thể làm lộ secret không?
- Host có FDE hoặc storage encryption nếu có rủi ro mất/tháo thiết bị không?
- Monitoring có theo dõi CPU throttling, thermal event, memory error và NUMA imbalance không?
