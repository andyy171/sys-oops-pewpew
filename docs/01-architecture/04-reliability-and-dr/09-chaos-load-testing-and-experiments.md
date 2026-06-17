# Chaos Testing, Load Testing Và Experiments

## Overview

Chaos testing, load testing và experiments là ba cách học có kiểm soát từ hệ thống đang chạy:

- Chaos testing kiểm tra service phản ứng thế nào khi dependency, network, node hoặc runtime gặp lỗi bất thường nhưng plausible.
- Load testing kiểm tra performance, capacity và regression dưới tải thực tế hoặc tải dự báo.
- Experiments kiểm tra tác động của thay đổi lên user experience trước khi rollout rộng.

Điểm chung: trước khi thử nghiệm, hệ thống phải có observability, hypothesis, blast-radius limit và rollback/stop mechanism. Không có các điều kiện này thì experiment dễ biến thành outage không học được gì.

## Chaos Testing

Chaos testing đưa lỗi có chủ đích vào môi trường để quan sát failure mode:

- tăng latency hoặc packet loss giữa service;
- disconnect hoặc timeout dependency;
- kill Pod hoặc restart process;
- làm node unavailable;
- tạo storage/network lỗi trong phạm vi kiểm soát.

Mục tiêu không phải phá hệ thống cho vui. Mục tiêu là xác minh giả định resilience:

```text
hypothesis -> inject plausible failure -> observe steady state -> learn -> harden
```

Prerequisites:

- biết steady state/SLO của service;
- monitoring/logging/tracing đủ để thấy tác động;
- có owner trực trong lúc chạy;
- có scope rõ: namespace, service, region, percent traffic;
- có stop condition và rollback action;
- bắt đầu trong test/staging hoặc production blast radius rất nhỏ.

Chaos tốt mô phỏng lỗi có khả năng xảy ra. Nếu failure quá cực đoan và không gắn với risk model thật, effort hardening có thể không đáng chi phí.

## Communication Chaos

Một pattern dễ bắt đầu là đặt proxy giữa client và service để inject latency, timeout, disconnect hoặc error. Khi dùng Kubernetes, có thể triển khai proxy như một Deployment/Service trung gian hoặc dùng service mesh/chaos tooling.

Điều cần đo:

- request success rate;
- latency p95/p99;
- retry rate và timeout;
- queue depth/consumer lag nếu có async path;
- error budget burn;
- dependency saturation.

Nếu app không có timeout/circuit breaker/retry budget rõ, communication chaos thường làm lộ retry storm hoặc cascading failure.

## Operational Chaos

Các bài test hạ tầng thường gặp:

- xóa một Pod trong Deployment;
- xóa nhiều Pod theo label trong namespace;
- cordon/drain node trong staging;
- reboot node hoặc mô phỏng node failure;
- làm dependency tạm unreachable.

Với Kubernetes, xóa Pod managed by controller thường là test hợp lý vì controller sẽ recreate Pod. Nhưng node crash, volume detach, StatefulSet Pod force-delete hoặc network partition có blast radius lớn hơn nhiều và cần runbook riêng.

Tránh chạy destructive chaos trên production nếu chưa có:

- SLO và alert ổn định;
- PDB/readiness/probe đúng;
- capacity headroom;
- incident commander/owner;
- rollback hoặc disable switch;
- communication plan.

## Fuzz Testing

Fuzz testing đưa input hợp lệ về mặt protocol nhưng cực đoan hoặc bất thường vào app:

- JSON rất dài;
- field trùng;
- giá trị random;
- payload edge case;
- token/header bất thường.

Fuzzing hữu ích cho security và resiliency vì nó ép code đi qua nhánh hiếm, nơi dễ có crash, parsing bug hoặc validation bypass. Fuzzing có thể chạy ở unit test, API test hoặc service-level test, nhưng không nên dùng dữ liệu nhạy cảm thật.

## Load Testing

Load testing có hai mục tiêu chính:

- Capacity estimation: service chịu được bao nhiêu traffic với cấu hình hiện tại.
- Regression prevention: version mới có giữ được throughput/latency/error rate như version cũ không.

Predictive load testing dùng trend tăng trưởng để test trước tương lai:

```text
current peak traffic -> forecast +10/20/50% -> test -> capacity plan
```

Load test không thực tế sẽ tạo kết luận sai. Ví dụ chỉ request một user/resource có thể tạo cache hit rate quá đẹp và che bottleneck thật.

## Realistic Traffic

Có hai cách tạo traffic:

- Synthetic model: xây model dựa trên tỷ lệ read/write, endpoint mix, user journey, data size.
- Recorded traffic replay: dùng request thật đã ghi lại.

Replay traffic thật rất rủi ro:

- chứa PII, token, credential hoặc dữ liệu nhạy cảm;
- token có thể hết hạn hoặc không hợp lệ khi replay;
- request write có thể phá dữ liệu nếu trỏ nhầm production;
- behavior theo thời gian có thể lỗi thời.

Best practice là xây synthetic model từ production telemetry đã được sanitize. Nếu cần replay, phải dùng dataset đã scrub, storage clone/snapshot và network boundary tách khỏi production.

## Load Test Architecture

Large-scale load testing cũng là distributed system:

- một Pod load generator có thể không đủ network/CPU;
- nhiều generator cần phân phối đều qua load balancer;
- test trong cùng cluster đo backend path nhưng có thể bỏ qua edge LB/internet path;
- test ngoài cluster đo end-to-end path nhưng bị giới hạn bởi generator network/cost.

Nên chạy cả hai kiểu khi cần:

```text
inside-cluster load -> service/backend capacity
outside-cluster load -> edge/LB/DNS/TLS/end-to-end capacity
```

Kết quả load test nên gắn với resource tuning: replica count, CPU request/limit, memory, GC behavior, connection pool, DB capacity và cache hit rate. Đừng chỉ tăng replica nếu bottleneck thật là database, lock, queue hoặc downstream dependency.

## Experiments

Experiment khác chaos/load: mục tiêu là học tác động lên user experience. Một experiment tốt bắt đầu bằng hypothesis:

```text
Nếu thay đổi X cho nhóm user Y, metric Z sẽ cải thiện mà không làm SLO W xấu đi.
```

Cách triển khai:

- Feature flag trong cùng binary: đơn giản, nhanh, nhưng experimental code crash có thể ảnh hưởng production process.
- Separate deployment + traffic splitting: phức tạp hơn nhưng cô lập tốt hơn, rollback/iterate nhanh hơn.

Traffic splitting có thể dựa trên:

- percentage traffic;
- header/cookie/query parameter;
- user segment;
- region;
- service mesh/Gateway/progressive delivery controller.

Monitoring phải phân biệt control và experiment theo label/version/deployment. Nếu trộn metric chung, failure của experiment có thể bị che bởi traffic production khỏe.

## Runbook Template

Trước experiment:

```text
hypothesis:
scope:
blast radius:
steady-state metric:
expected impact:
stop condition:
rollback:
owner:
communication:
```

Trong experiment:

- theo dõi SLO/error budget;
- theo dõi metric phân tách theo version/segment;
- ghi timeline và config chính xác;
- không thay nhiều biến cùng lúc nếu mục tiêu là học nguyên nhân.

Sau experiment:

- ghi kết quả so với hypothesis;
- giữ dashboard/log/trace evidence;
- tạo action hardening/tuning;
- quyết định rollback, retry với scope khác, hoặc rollout rộng.

## Best Practices

- Không chạy chaos/load/experiment khi observability chưa đủ.
- Bắt đầu nhỏ rồi tăng scope theo mức học được.
- Luôn có stop condition và người chịu trách nhiệm.
- Dùng synthetic/sanitized data cho load test; không replay PII/token thật.
- Tách test capacity khỏi test user-experience experiment.
- Không coi staging là bằng production; nhưng cũng không dùng production làm nơi thử bừa.
- Với Kubernetes, kiểm tra PDB, readiness, autoscaling, quota và dependency capacity trước khi inject failure hoặc load.

## Related Pages

- [HA And Failover Patterns](./01-ha-and-failover-patterns.md)
- [Multi-Region Architecture](./04-multi-region-architecture.md)
- [RTO/RPO Design](./07-rto-rpo-design.md)
- [Blue/Green, Canary Và Rolling Deployment](../../05-infrastructure-automation/03-cicd-devops-integration/02-continuous-delivery-and-deployment/BlueGreen, Canary, Rolling.md)
- [Kubernetes Observability Logs, Metrics, Events Và Traces](../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/05-operations/02-observability-logs-metrics-events-and-traces.md)
