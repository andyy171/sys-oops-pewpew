# Go Project Structure And Domain Modeling For Ops Tools

Một tool hạ tầng bằng Go nên bắt đầu từ domain model nhỏ và rõ trước khi thêm runtime SDK, HTTP API hay persistent database. Cách làm này giúp nhìn thấy state machine, boundary giữa component, và các nơi có thể thay backend mà không rewrite toàn bộ service.

Ví dụ với một orchestrator nhỏ, các package nên phân theo ownership thay vì phân theo technical layer quá sớm:

```text
cmd/              entrypoint và CLI command
internal/task/    task, event, state, validation
internal/node/    node model và node stats
internal/worker/  worker loop, local queue, runtime adapter
internal/manager/ manager loop, scheduler call, worker client
internal/schedule scheduler interface và implementation
internal/store/   in-memory store, persistent store
internal/runtime/ Docker/container runtime wrapper
```

Nếu project còn nhỏ, có thể bắt đầu phẳng hơn, nhưng vẫn nên giữ ý tưởng: domain model không phụ thuộc trực tiếp vào HTTP handler hay Docker SDK.

## Module Và Dependency Boundary

Với Go hiện đại, project nên có `go.mod` ở root để quản lý module path và dependency. Dependency bên ngoài như UUID, router, Docker SDK, queue library hoặc Cobra nên đi qua package boundary rõ ràng, thay vì được import rải rác ở domain model.

Một rule dễ dùng:

- domain package chỉ chứa type, validation và state transition;
- adapter package import thư viện ngoài như Docker SDK, HTTP client, BoltDB;
- command/API package chuyển input thành domain intent;
- manager/worker package phối hợp các interface.

Lợi ích là khi thay Docker SDK, đổi router, hoặc thay memory store bằng persistent store, domain model không bị kéo theo.

## Domain Model Trước

Hãy viết các object chính trước:

- `Task`: desired workload, image, resource request, port mapping, restart policy, state, runtime/container ID.
- `TaskEvent`: intent hoặc transition như submit, schedule, start, stop, complete, fail.
- `Node`: worker identity, address, role, resource capacity/usage, task count.
- `Worker`: queue, local task store, runtime adapter, stats.
- `Manager`: pending queue, task store, worker registry, task-to-worker mapping, scheduler.
- `Scheduler`: interface nhận task/node list và trả node được chọn.

Domain object cần thể hiện được câu hỏi vận hành: task đang ở trạng thái nào, ai đang sở hữu task, node nào đang chạy task, restart đã thử mấy lần, và last known state được cập nhật lúc nào.

## State Machine

Dùng typed enum cho state để code dễ đọc hơn string rời rạc. State transition nên được gom vào một nơi, vì đây là contract giữa API, manager, worker và store.

```go
type TaskState int

const (
    TaskPending TaskState = iota
    TaskScheduled
    TaskRunning
    TaskCompleted
    TaskFailed
)
```

Một state machine đơn giản cho task:

```text
Pending -> Scheduled -> Running -> Completed
                     \-> Failed
Running -> Failed
```

`Completed` và `Failed` thường là terminal state. Nếu muốn restart, dùng event mới hoặc tăng restart count rõ ràng, không âm thầm biến terminal state thành `Running`.

## ID, Map Và Queue

Dùng ID bất biến cho task/event/node. UUID phù hợp cho object sinh từ nhiều component, còn name có thể dùng cho node identity nếu được quản lý bởi operator.

In-memory `map[id]*Task` tốt cho học và prototype, nhưng phải coi nó là cache/state store có giới hạn:

- mất state khi process restart;
- không có transaction;
- dễ bị data race nếu nhiều goroutine đọc/ghi mà không có lock hoặc boundary rõ;
- pointer có thể bị mutate ngoài ý muốn.

Queue nên chứa intent cần xử lý, store nên chứa last known state. Nếu queue và store bị trộn làm một, service dễ rơi vào tình trạng handler đã "chấp nhận" request nhưng background loop không biết phải reconcile từ đâu.

## Pointer Hay Value

Go làm việc với struct pointer rất tiện, nhưng trong control-plane code cần cảnh giác với mutation ngoài ý muốn. Khi handler muốn enqueue desired state mới dựa trên task hiện có, nên tạo bản sao và thay đổi bản sao, thay vì mutate pointer đang nằm trong current-state store.

Tình huống dễ sai:

```text
current := store[id]       # trỏ vào current state
current.State = Stopping   # current state bị đổi trước khi worker thực sự stop
queue.Push(current)        # queue nhận intent, nhưng store đã mất evidence cũ
```

Hướng tốt hơn:

```text
current := store[id]
desired := copy(current)
desired.State = Stopping
queue.Push(desired)
```

Với code production, thêm test cho transition và cân nhắc immutable event log nếu state quan trọng.

## Interface Sớm, Abstraction Vừa Đủ

Interface có giá trị khi nó cắt dependency thật:

- `Store` cắt manager/worker khỏi backend memory, BoltDB, SQLite, Postgres, etcd.
- `Runtime` cắt worker khỏi Docker SDK/containerd.
- `Scheduler` cắt manager khỏi policy lập lịch.
- `WorkerClient` cắt manager khỏi chi tiết HTTP endpoint của worker.

Không cần tạo interface cho mọi struct. Hãy tạo khi có ít nhất một trong các nhu cầu: test bằng fake, đổi backend, hoặc tách ownership giữa package.

## Constructor Và Default

Khi struct bắt đầu có nhiều field như queue, store, scheduler, runtime adapter, stats snapshot hoặc worker map, nên tạo constructor thay vì để mọi caller tự build struct literal. Constructor giúp gom default và tránh quên field quan trọng.

```text
NewWorker(name, storeType, runtime) -> Worker
NewManager(storeType, scheduler, workers) -> Manager
NewScheduler(policy) -> Scheduler
```

Default nên rõ nhưng không giấu lỗi:

- nếu thiếu name, có thể sinh name tạm cho local lab;
- nếu thiếu store type, dùng `memory` cho học;
- nếu port/env/flag sai, fail fast;
- nếu scheduler policy không hợp lệ, trả lỗi thay vì fallback âm thầm.

## Vòng Lặp Phát Triển

Với Go tool hạ tầng, vòng lặp tốt là:

1. Định nghĩa model và state transition.
2. Viết in-memory store/queue để chạy được luồng cơ bản.
3. Thêm API/CLI rất mỏng để gửi intent.
4. Thêm background loop xử lý intent và cập nhật state.
5. Thêm runtime adapter và error handling.
6. Thêm persistence, retry, health check và metrics.

Dùng skeleton compile được sớm. Một binary chạy được với fake runtime thường giúp thấy design bug nhanh hơn việc viết đầy đủ Docker/API/database ngay từ đầu.

## Checklist

- State transition có được validate tập trung không?
- Handler có mutate current state trực tiếp không?
- Queue đang chứa intent hay chứa current state?
- Object ID có ổn định qua restart không?
- Manager có mapping task-to-worker để stop đúng node không?
- Runtime SDK có bị gọi trực tiếp từ handler không?
- Store có cách phân biệt not found và backend error không?
- Dependency bên ngoài có nằm sau adapter/interface không?
- Constructor có gom default và validate config không?

## Liên Quan

- [Go Programming](./overview.md)
- [Go HTTP API, CLI And Background Workers](./02-go-http-api-cli-and-background-workers.md)
- [Go Orchestrator Implementation Patterns](./04-go-orchestrator-implementation-patterns.md)
- [Orchestrator Internals From Scratch](../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/00-architecture/02-orchestrator-internals-from-scratch.md)
