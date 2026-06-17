# Orchestrator Internals From Scratch

## Overview

Một orchestrator tối thiểu không bắt đầu từ hàng trăm Kubernetes object. Nó bắt đầu từ vài vòng lặp rất cơ bản: nhận ý định chạy workload, lưu state, chọn node, gửi việc cho node agent, quan sát runtime thật và sửa lệch khi task không còn đúng trạng thái mong muốn.

Mental model này giúp đọc Kubernetes dễ hơn: `kube-apiserver`, scheduler, controller-manager, etcd và kubelet là phiên bản production-grade của các vai trò mà một orchestrator tự viết thường gọi là manager, scheduler, datastore và worker.

```text
User / CLI / API
  -> manager API
  -> task/event store
  -> scheduler
  -> worker API
  -> container runtime
  -> task status / metrics / health
  -> manager reconciliation loop
```

## Object Model Cốt Lõi

Một orchestrator đơn giản thường có các object sau:

| Object | Vai trò | Kubernetes tương đương gần đúng |
|---|---|---|
| Task | Đơn vị chạy nhỏ nhất, thường map 1-1 với container | Pod hoặc container trong Pod, tùy mức trừu tượng |
| Job | Nhóm task tạo thành một workload logic | Deployment, StatefulSet, DaemonSet, Job |
| Manager | Nhận request, lưu state, điều phối worker | Control plane/API server + controller logic |
| Scheduler | Chọn worker/node phù hợp cho task | kube-scheduler |
| Worker | Node agent chạy container, cập nhật status, expose metrics | kubelet + container runtime |
| Store | Lưu task, event, mapping task-node | etcd và các controller cache |
| CLI/API | Giao diện vận hành | `kubectl`, Kubernetes API |

Điểm quan trọng: tên gọi có thể khác nhau giữa Borg, Nomad, Mesos và Kubernetes, nhưng mẫu chung vẫn là **intent -> state store -> scheduling -> node execution -> observation -> reconciliation**.

## Task State Machine

Task nên có state machine rõ, vì orchestrator không chỉ "run container" mà còn phải biết trạng thái nào được phép chuyển sang trạng thái nào.

```text
Pending -> Scheduled -> Running -> Completed
                      -> Failed
```

Ý nghĩa vận hành:

- `Pending`: task mới được tạo, chưa chọn node.
- `Scheduled`: manager/scheduler đã chọn worker, nhưng runtime chưa chắc đã chạy container.
- `Running`: worker đã start container thành công.
- `Completed`: task dừng bình thường hoặc được user yêu cầu stop.
- `Failed`: start/runtime/health check thất bại.

Không nên cho phép chuyển state tùy tiện. Ví dụ `Running -> Scheduled` thường là dấu hiệu logic sai, vì task đang chạy không nên được coi như chưa start. Muốn reschedule cần một event rõ: stop task cũ, xác nhận trạng thái, rồi tạo placement mới.

## Manager Và Worker Loop

Một orchestrator nhỏ thường có hai vòng lặp chính.

Manager loop:

```text
read pending task/event
  -> update event store
  -> ask scheduler for candidate node
  -> send task event to worker API
  -> update task-node mapping
  -> poll workers for task status
  -> run health/restart logic
```

Worker loop:

```text
read task event from queue
  -> validate state transition
  -> call runtime start/stop
  -> persist task state
  -> inspect runtime periodically
  -> expose task list and node metrics
```

Trong Kubernetes, cùng pattern này được tách ra thành nhiều controller chuyên biệt. API server lưu object; scheduler chỉ bind Pod vào Node; kubelet mới kéo image, mount volume, chạy container và report status; controller-manager liên tục reconcile object cấp cao như Deployment, ReplicaSet, Job và Node.

## Scheduling Framework

Scheduling không có một thuật toán đúng cho mọi workload. Một framework tối thiểu nên tách thành ba bước:

```text
filter candidates -> score candidates -> pick best node
```

Ví dụ tiêu chí filter:

- node còn đủ disk để pull image;
- node còn đủ memory/CPU theo request;
- node có label, role hoặc capability phù hợp;
- node chưa bị đánh dấu unhealthy hoặc unreachable.

Ví dụ tiêu chí score:

- round-robin để phân phối đơn giản;
- bin-packing để dồn workload và tiết kiệm node;
- spreading để giảm blast radius;
- cost-based scoring dựa trên CPU, memory, disk, task count hoặc latency.

Kubernetes cũng dùng mô hình nhiều phase tương tự: filter plugin loại node không phù hợp, score plugin chấm điểm node còn lại, sau đó scheduler chọn node tốt nhất theo profile/config hiện hành.

### Resource Offer Model

Một số orchestrator như Mesos dùng mô hình ngược với Kubernetes scheduler quen thuộc: agent/slave báo tài nguyên còn trống lên master, master gửi **resource offer** cho framework scheduler, rồi framework quyết định nhận offer để chạy task hoặc từ chối.

Mental model:

```text
worker reports available CPU/memory/ports
-> master sends offer to framework scheduler
-> scheduler accepts or declines
-> master asks selected worker to launch task
-> executor/runtime starts workload
```

Mô hình này mạnh khi tổ chức có nhiều framework với logic placement riêng, ví dụ batch, long-running service, data locality hoặc custom executor. Tradeoff là scheduler/framework tự viết phải chịu trách nhiệm lớn hơn về correctness: tránh overcommit, xử lý offer stale, health check, retry, idempotency, cleanup và trạng thái task sau failure.

Production guardrails nếu dùng hoặc tự thiết kế kiểu resource offer:

- offer phải có version/ID và timeout, không dùng offer cũ sau khi tài nguyên đã đổi;
- task launch phải idempotent hoặc có deduplication để tránh duplicate khi retry;
- port/resource allocation cần release rõ khi task exit;
- framework bug có thể gây outage rộng, nên ưu tiên framework battle-tested nếu team không có năng lực vận hành scheduler riêng;
- node agent có quyền quản lý runtime thường cần quyền rất cao, tương tự mount Docker socket hoặc thao tác cgroup/namespace trên host.

## Metrics Và Node State

Scheduler cần dữ liệu thực tế của worker. Với một orchestrator nhỏ, worker có thể expose endpoint kiểu `/stats` để manager lấy:

- CPU usage hoặc load average;
- total/available memory;
- total/available disk;
- số task đang chạy;
- trạng thái worker API.

Trên Linux, các số liệu cơ bản thường đến từ `/proc/stat`, `/proc/meminfo`, `/proc/loadavg` và filesystem stats. Trong production, chỉ đọc số host-level là chưa đủ: cần phân biệt node capacity, allocatable, request đã đặt, usage thật, pressure signal, image filesystem, container filesystem và lỗi runtime.

Với Kubernetes, đây là lý do debug scheduling không nên chỉ nhìn `kubectl get pods`. Cần đi từ Pod request, Node allocatable, events, kubelet status, image pull, volume mount, node pressure và metrics pipeline.

## Failure And Recovery Model

Failure có nhiều tầng:

| Tầng lỗi | Ví dụ | Orchestrator có thể làm gì |
|---|---|---|
| Application startup | App không connect được DB khi khởi động | Retry/backoff trong app, startup/readiness probe, không restart vô hạn mù quáng |
| Application runtime | Bug làm process crash hoặc health check fail | Restart có giới hạn, rollout/rollback, log/evidence |
| Runtime | Container runtime/Docker/containerd lỗi | Worker report trạng thái, node health, có thể reschedule nếu chắc chắn an toàn |
| Worker process | Node agent crash nhưng container còn chạy | Không vội tạo duplicate; cần phân biệt agent down và task down |
| Worker machine | Node thật mất điện/reboot/network split | Mark node unhealthy, reschedule sau timeout, chú ý stateful workload |
| Manager/control plane | API/control loop down | Workload đang chạy có thể vẫn chạy; mất khả năng submit/update/reconcile |

Điểm dễ sai là nhầm **không gọi được worker API** với **task đã chết**. Nếu manager lập tức chạy bản sao task trên node khác trong khi task cũ vẫn sống, workload singleton hoặc stateful workload có thể bị duplicate writer. Kubernetes giải quyết phần này bằng Node condition, lease/heartbeat, graceful termination, controller ownership, Pod UID và storage semantics, nhưng vẫn cần thiết kế workload đúng.

## Health Check Và Restart

Health check nên là contract của workload, không phải suy đoán từ việc process còn tồn tại.

Một mô hình đơn giản:

```text
worker inspect runtime -> update task Running/Failed
manager call task health endpoint
  -> 200: keep running
  -> non-200/timeout: restart or mark failed
  -> restart count exceeded: stop automatic retry and surface evidence
```

Trong Kubernetes:

- `startupProbe` bảo vệ app khởi động chậm;
- `readinessProbe` quyết định Pod có vào Service endpoint hay không;
- `livenessProbe` quyết định kubelet có restart container hay không.

Restart không thay thế được fix application hoặc dependency. Nếu DB down, restart liên tục có thể chỉ tạo thêm load và che mất nguyên nhân thật.

## Persistent State

In-memory map đủ để học, nhưng không đủ để vận hành. Nếu manager restart và mất mapping task-node, nó không còn biết task nào đang chạy ở đâu. Nếu worker restart và mất local task state, nó không biết container nào thuộc quyền quản lý của mình.

Store tối thiểu nên hỗ trợ:

```text
Put(key, value)
Get(key)
List()
Count()
```

Tách code vận hành khỏi backend store bằng interface giúp đổi từ memory store sang persistent store mà không rewrite manager/worker loop. Production control plane cần đi xa hơn: transaction rõ, backup/restore, leader election, consistency, watch/event semantics, compaction và corruption recovery.

Trong Kubernetes, etcd là phần lưu cluster state. Vì vậy backup/restore etcd, API object size, event churn, watch latency và quorum health đều ảnh hưởng trực tiếp đến khả năng reconcile của cluster.

## API Và CLI Boundary

Nên tách rõ:

- worker API: manager gọi để start/stop task, lấy task list, lấy node metrics;
- manager API: user/CLI gọi để submit task, stop task, xem trạng thái hệ thống;
- CLI: wrapper ergonomic quanh manager API, không nên bypass state store hoặc worker khi không có lý do vận hành rõ.

Kubernetes cũng đi theo hướng này: người dùng nói chuyện với API server qua `kubectl` hoặc client; kubelet và controller giao tiếp qua API object/status thay vì người vận hành SSH vào từng node để start container thủ công.

## Go Implementation Layer

Nếu mục tiêu là học cách hiện thực hóa orchestrator bằng Go, hãy đọc chung với nhóm note [Go Programming](../../../../06-programming-languages/01-go/overview.md). Phần Kubernetes này giữ mental model control plane; phần Go giữ cách chia package, domain model, HTTP API, CLI, background loop, runtime adapter, metrics và persistent store.

## Production Caveats

Một orchestrator "from scratch" có thể dạy mental model rất tốt, nhưng còn thiếu nhiều phần production:

- authentication, authorization và audit;
- network/service discovery/load balancing;
- HA manager/control plane;
- consensus/leader election;
- secure secret handling;
- image supply chain và registry policy;
- rollout/rollback semantics;
- node drain/cordon;
- stateful workload safety;
- observability, alerting và debugging evidence.

Khi đọc Kubernetes, hãy luôn hỏi: object nào giữ desired state, controller nào reconcile, component nào chạy data plane thật, state nằm ở đâu, và failure nào có thể tạo duplicate, data loss hoặc traffic blackhole.

## Trang Liên Quan

- [Kubernetes Architecture](./overview.md)
- [Control Plane, Node Và Reconciliation](./01-control-plane-node-and-reconciliation.md)
- [Kubernetes Scheduling, Affinity, Taints, Topology Và Priority](../05-operations/03-scheduling-affinity-taints-topology-and-priority.md)
- [Kubernetes Operations, Resources Và Observability](../05-operations/overview.md)
- [Troubleshooting Symptom To Control Plane Debug Flow](../98-troubleshooting/01-symptom-to-control-plane-debug-flow.md)
- [Go Programming](../../../../06-programming-languages/01-go/overview.md)
