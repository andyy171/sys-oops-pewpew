# Go Orchestrator Implementation Patterns

Note này gom các pattern Go quan trọng khi hiện thực một orchestrator nhỏ: manager, worker, scheduler, queue, store, runtime adapter, HTTP API và CLI. Nội dung được rút từ `_inbox/build-an-orchestrator-in-go-from-scratch.md`, nhưng được tổ chức lại theo concept bền vững thay vì theo chapter.

## Mental Model Tổng Thể

Orchestrator trong source tiến hóa theo một trục rất rõ: bắt đầu từ domain model compile được, thêm runtime adapter, thêm worker queue, expose worker API, thêm metrics, thêm manager API, rồi refactor scheduler/store/CLI. Nếu nhìn bằng Go design, đây là bài học về cách biến mental model thành package boundary.

```mermaid
flowchart LR
    User[User hoặc CLI] --> ManagerAPI[Manager API]
    ManagerAPI --> Pending[Manager Pending Queue]
    Pending --> ManagerLoop[Manager ProcessTasks Loop]
    ManagerLoop --> Scheduler[Scheduler Interface]
    Scheduler --> WorkerClient[Worker HTTP Client]
    WorkerClient --> WorkerAPI[Worker API]
    WorkerAPI --> WorkerQueue[Worker Task Queue]
    WorkerQueue --> WorkerLoop[Worker RunTasks Loop]
    WorkerLoop --> Runtime[Runtime Adapter]
    Runtime --> Docker[Docker Daemon]
    WorkerLoop --> WorkerStore[Worker Store]
    ManagerLoop --> ManagerStore[Manager Store]
    WorkerLoop --> Metrics[Stats Collector]
    Metrics --> WorkerAPI
    ManagerLoop --> WorkerAPI
```

Điểm quan trọng: manager và worker đều là service có state riêng. API chỉ là boundary nhận request; loop mới là nơi reconcile intent thành hành động thật.

## Package Boundary

Một layout tốt không chỉ là chia folder cho đẹp. Nó phải thể hiện ai sở hữu behavior nào:

```text
task/       Task, TaskEvent, State, transition validation
worker/     queue, RunTasks, StartTask, StopTask, UpdateTasks, CollectStats
manager/    pending queue, SendWork, UpdateTasks, DoHealthChecks
scheduler/  Scheduler interface, RoundRobin, E-PVM
node/       worker node identity, stats client
store/      Store interface, memory store, persistent store
runtime/    Docker SDK wrapper hoặc container runtime adapter
cmd/        Cobra command, flags, process entrypoint
```

Nếu package `manager` phải biết chi tiết `bolt.Tx`, `docker.ContainerCreate`, hoặc cách parse `/proc/stat`, boundary đã bị thủng. Những chi tiết đó nên nằm sau `store`, `runtime`, `node` hoặc `stats`.

## Task Lifecycle

Source dùng 5 state chính: `Pending`, `Scheduled`, `Running`, `Completed`, `Failed`. Đây không chỉ là enum; nó là contract giữa API, manager, worker, store và runtime.

```mermaid
stateDiagram-v2
    [*] --> Pending: user submit
    Pending --> Scheduled: manager picks worker
    Scheduled --> Running: worker starts container
    Scheduled --> Failed: runtime start error
    Running --> Completed: user stop or normal completion
    Running --> Failed: runtime/app failure
    Completed --> [*]
    Failed --> [*]
```

Prototype có thể hard-code transition bằng `map[State][]State`. Production code nên có error rõ cho invalid transition và nên test state machine độc lập.

## Desired State Và Current State

Trong source, queue được dùng như desired state, còn DB/store là current known state. Đây là một chi tiết rất dễ bỏ qua nhưng cực kỳ quan trọng.

```mermaid
flowchart TD
    Request[HTTP request hoặc CLI command] --> Event[TaskEvent: desired transition]
    Event --> Queue[Queue]
    Queue --> Loop[Worker hoặc Manager loop]
    Loop --> Current[Read current state from Store]
    Current --> Validate[Validate transition]
    Validate --> Action[Runtime/API action]
    Action --> Persist[Persist observed state]
    Persist --> Status[Status endpoint reads Store]
```

Không nên để handler mutate store như thể hành động đã hoàn tất. Handler chỉ nên nói "đã nhận intent". Trạng thái thật phải đến từ loop sau khi runtime/API call trả kết quả.

## Worker Internal Flow

Worker là node agent của orchestrator. Nó nhận task từ manager, queue lại, chạy container qua runtime adapter, lưu state và expose status/metrics.

```mermaid
sequenceDiagram
    participant M as Manager
    participant A as Worker API
    participant Q as Worker Queue
    participant L as RunTasks Loop
    participant S as Worker Store
    participant R as Runtime Adapter
    participant D as Docker

    M->>A: POST /tasks TaskEvent
    A->>Q: enqueue desired Task
    A-->>M: 201 Created
    L->>Q: Dequeue
    L->>S: Get current task
    L->>L: ValidStateTransition
    L->>R: StartTask or StopTask
    R->>D: ContainerCreate/Start/Stop/Remove
    D-->>R: container ID or error
    R-->>L: RuntimeResult
    L->>S: Put Running/Completed/Failed
```

Source bắt đầu bằng `map[uuid]*Task`, nhưng sau đó refactor sang `Store` interface. Bài học Go ở đây là: cứ prototype bằng map để học flow, nhưng đừng để manager/worker phụ thuộc vĩnh viễn vào map.

## Manager Internal Flow

Manager là control-plane service. Nó nhận request từ user/CLI, quyết định worker, gọi worker API, rồi poll worker để cập nhật view của mình.

```mermaid
sequenceDiagram
    participant CLI as CLI/User
    participant MA as Manager API
    participant MQ as Pending Queue
    participant ML as Manager Loop
    participant SCH as Scheduler
    participant WS as Worker API
    participant MS as Manager Store

    CLI->>MA: POST /tasks
    MA->>MQ: enqueue TaskEvent
    MA-->>CLI: 201 Created / accepted task
    ML->>MQ: Dequeue
    ML->>SCH: SelectCandidateNodes -> Score -> Pick
    SCH-->>ML: selected worker
    ML->>MS: Put Task and TaskEvent
    ML->>WS: POST /tasks
    WS-->>ML: accepted
    ML->>MS: record task-to-worker mapping
```

Một điểm sâu trong source: `GET /tasks` từ manager có thể chưa thấy `ContainerID` ngay sau `POST /tasks`, vì manager update view bằng vòng `UpdateTasks` polling worker. Đây là eventual consistency ở mức rất nhỏ.

## Stop Task Bug Khi Có Nhiều Worker

Khi chỉ có một worker, stop task có vẻ chạy đúng. Khi có ba worker, nếu manager gọi scheduler lại cho event stop, xác suất chọn nhầm worker tăng lên. Source chỉ ra bug này rất hay: stop/update existing task không phải scheduling decision mới.

```mermaid
flowchart TD
    StopEvent[Stop TaskEvent] --> Known{TaskWorkerMap có task?}
    Known -- Không --> Reject[Reject hoặc task not found]
    Known -- Có --> ExistingWorker[Use existing worker]
    ExistingWorker --> Validate[Validate Running -> Completed]
    Validate --> Delete[DELETE worker /tasks/taskID]
    Delete --> Store[Update manager state]

    StopEvent -. sai .-> Scheduler[Call scheduler again]
    Scheduler -. có thể chọn nhầm .-> WrongWorker[Worker không chạy task]
```

Rule: create/start task dùng scheduler; stop/restart/update task đang tồn tại dùng mapping hiện có, trừ khi có logic reschedule rõ ràng.

## Scheduler Interface

Source refactor scheduler thành ba phase: filter, score, pick. Đây là một interface tốt vì nó mô tả đúng domain, không leak implementation.

```mermaid
flowchart LR
    Task[Task request] --> Filter[SelectCandidateNodes]
    Nodes[Worker nodes] --> Filter
    Filter --> Candidates[Candidate nodes]
    Candidates --> Score[Score]
    Task --> Score
    Score --> Scores[map node -> score]
    Scores --> Pick[Pick]
    Candidates --> Pick
    Pick --> Selected[Selected node]
```

Round-robin chỉ cần policy đơn giản: node tiếp theo được score tốt nhất. E-PVM-style scheduler dùng resource view: disk filter trước, sau đó tính cost dựa trên CPU/memory/task count. Điểm học Go là interface cho phép manager giữ nguyên flow, còn policy thay đổi bằng implementation khác.

## Node Stats Không Nên Nằm Trong Scheduler

Source ban đầu có helper lấy `/stats` trong scheduler, sau đó refactor sang `Node.GetStats()`. Đây là một boundary rất đáng nhớ:

```mermaid
flowchart TD
    Scheduler[Scheduler policy] --> Node[Node object]
    Node --> Retry[HTTPWithRetry]
    Retry --> WorkerStats[GET worker /stats]
    WorkerStats --> NodeStats[Update node stats]
    NodeStats --> Scheduler
```

Scheduler nên nhận node đã có stats hoặc gọi method của node; nó không nên tự biết URL endpoint, decode JSON, retry HTTP. Nếu không, policy scheduling bị trộn với network client.

## Worker Metrics Flow

Worker metrics trong source đi từ Linux `/proc` và disk stat vào một `Stats` struct, sau đó expose qua `/stats`.

```mermaid
flowchart LR
    ProcStat[/proc/stat] --> StatsCollector[CollectStats Loop]
    MemInfo[/proc/meminfo] --> StatsCollector
    LoadAvg[/proc/loadavg] --> StatsCollector
    Disk[Filesystem Stat] --> StatsCollector
    StatsCollector --> Snapshot[Worker.Stats Snapshot]
    Snapshot --> StatsAPI[GET /stats]
    StatsAPI --> Manager[Manager/Scheduler]
```

Điểm học Go: collector chạy nền cập nhật snapshot; HTTP handler chỉ encode snapshot. Handler không nên đọc `/proc` trực tiếp trên mỗi request nếu có thể tránh.

## Health Check Và Restart Flow

Source tách health thành hai lớp:

- worker inspect container bằng Docker API để biết runtime state;
- manager gọi health endpoint của app để biết application health.

```mermaid
sequenceDiagram
    participant WL as Worker UpdateTasks
    participant D as Docker
    participant WS as Worker Store
    participant ML as Manager DoHealthChecks
    participant APP as Task Health Endpoint
    participant WA as Worker API

    WL->>D: ContainerInspect(containerID)
    D-->>WL: running/exited/missing + ports
    WL->>WS: Put Running or Failed, HostPorts
    ML->>APP: GET /health via worker host port
    APP-->>ML: 200 or non-200/error
    alt unhealthy and restartCount < limit
        ML->>WA: POST /tasks restart event
        ML->>ML: increment RestartCount
    else limit exceeded
        ML->>ML: stop automatic retry, surface evidence
    end
```

Không gọi được worker API, container exit, app health fail và manager mất state là bốn failure khác nhau. Nếu gom hết thành "task chết", orchestrator dễ tạo duplicate hoặc restart sai nơi.

## Store Interface Và Persistence

Source refactor store theo cùng chiến lược với scheduler: tạo interface trước, rồi có memory implementation và persistent implementation.

```mermaid
flowchart TD
    Manager[Manager] --> StoreI[Store Interface]
    Worker[Worker] --> StoreI
    StoreI --> Mem[InMemoryTaskStore]
    StoreI --> Bolt[TaskStore / BoltDB]
    Mem --> Map[Go map]
    Bolt --> File[DB file]
```

Interface tối thiểu:

```text
Put(key, value)
Get(key)
List()
Count()
```

Source cố ý không có `Delete` vì store cũng là lịch sử task/event. Production có thể cần delete/compact, nhưng khi đó phải có retention policy.

## BoltDB Boundary

Persistent store trong source dùng embedded key-value database. Pattern tổng quát:

```mermaid
flowchart LR
    Open[Open DB file] --> Bucket[Create/Open bucket]
    Bucket --> Put[Put: Update transaction]
    Bucket --> Get[Get/List/Count: View transaction]
    Put --> Marshal[json.Marshal domain object]
    Get --> Unmarshal[json.Unmarshal domain object]
    Marshal --> KV[Key/Value bytes]
    KV --> File[DB file]
```

Điểm học Go:

- `View` dùng cho read-only transaction;
- `Update` dùng cho write transaction;
- domain object phải được serialize, source dùng JSON;
- `Close()` cần tồn tại vì store giữ file handle;
- bucket đã tồn tại khi restart không nên được coi như lỗi chết người;
- persistent local file giúp restart không mất state, nhưng không giải quyết HA manager.

## CLI Boundary

Cobra trong source không chỉ để "cho đẹp CLI". Nó tách process mode thành command rõ ràng:

```mermaid
flowchart TD
    Main[main.go] --> Execute[cmd.Execute]
    Execute --> Root[root command]
    Root --> WorkerCmd[worker: start worker service]
    Root --> ManagerCmd[manager: start manager service]
    Root --> RunCmd[run: POST manager /tasks]
    Root --> StopCmd[stop: DELETE manager /tasks/id]
    Root --> StatusCmd[status: GET manager /tasks/id]
    Root --> NodeCmd[node: GET manager nodes/stats]
```

Có hai nhóm command:

- service command: `worker`, `manager` chạy process dài hạn, mở API, start goroutine;
- client command: `run`, `stop`, `status`, `node` gọi manager API rồi thoát.

CLI phải đi qua manager API để giữ source of truth. Nếu CLI ghi thẳng vào store hoặc gọi worker để start task, nó bypass scheduling, audit, task-to-worker mapping và state machine.

## Deep Lessons Từ Source

Các bài học Go quan trọng hơn bản thân orchestrator:

- Skeleton compile được giúp validate mental model sớm.
- `TaskEvent` là object nội bộ để chuyển state, không chỉ là request body.
- Queue và store không thay thế nhau: queue là intent, store là evidence.
- API handler nên làm ít việc: decode, validate, enqueue, response.
- Long-running loop cần lifecycle: context, timeout, backoff, shutdown.
- Interface có ích khi nó cắt dependency thật: scheduler, store, runtime, worker client.
- Dùng `interface{}` trong Store prototype làm code linh hoạt nhưng kéo theo type assertion và lỗi runtime; production nên cân nhắc typed repository hoặc generics.
- Metrics nên được snapshot bởi background loop, không đọc trực tiếp trong handler.
- Retry HTTP nên nằm ở client/node layer, không rải trong scheduler.
- Health check cần phân biệt runtime state, app state, node reachability và manager state.
- CLI là UX của control plane, không phải đường tắt quanh control plane.

## Checklist Thiết Kế

- Handler có chỉ nhận intent và trả response không?
- Background loop có context/timeout/shutdown path không?
- Runtime SDK có được bọc sau interface/adapter không?
- Store có thể đổi backend mà không sửa manager/worker logic không?
- Stop/update task có dùng mapping hiện có không?
- Health check có tách runtime state, app health và worker reachability không?
- Scheduler có tách filter, score, pick không?
- Metrics client có nằm ở node/client layer thay vì scheduler policy không?
- CLI có đi qua manager API thay vì bypass store/worker không?

## Liên Quan

- [Go Programming](./overview.md)
- [Go Project Structure And Domain Modeling For Ops Tools](./01-go-project-structure-and-domain-modeling.md)
- [Go HTTP API, CLI And Background Workers](./02-go-http-api-cli-and-background-workers.md)
- [Go Runtime Integration, Metrics And Persistence](./03-go-runtime-integration-metrics-and-persistence.md)
- [Orchestrator Internals From Scratch](../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/00-architecture/02-orchestrator-internals-from-scratch.md)
