# Go Runtime Integration, Metrics And Persistence

Khi Go tool bước ra khỏi prototype, phần khó nhất thường không phải HTTP route mà là integration với runtime, metrics và state store. Ba phần này quyết định tool có recover được sau restart, có debug được failure, và có tránh tạo duplicate workload hay không.

## Runtime Adapter

Worker không nên gọi Docker SDK trực tiếp ở mọi nơi. Tạo adapter để bọc runtime operation:

- create/start container;
- stop/remove container;
- inspect container state;
- resolve host port/container port;
- normalize error và runtime result.

Adapter giúp manager/worker loop đọc theo domain:

```text
result := runtime.Start(task)
if result.Error != nil {
    mark task failed with evidence
}
```

Sau này có thể đổi Docker SDK sang containerd, remote runtime, hoặc fake runtime trong test mà không đổi handler và scheduler.

## Docker SDK Boundary

Khi dùng Docker Go SDK, các operation thường cần client, context và config object. Pattern nên giữ:

```text
client from environment/config
context with timeout
runtime config from TaskSpec
operation result normalized into domain result
```

Các call như pull image, create container, start container, stop/remove container và inspect container có kiểu trả về khác nhau. Không nên để manager/worker loop xử lý từng kiểu SDK trực tiếp. Adapter nên normalize thành result của domain, ví dụ `RuntimeResult`, `InspectResult`, hoặc error có operation name.

Không hardcode secret env trong task mẫu. Nếu cần minh họa config, dùng placeholder như `<PASSWORD>` hoặc `<TOKEN>`.

## Context, Timeout Và Retry

Mọi network/runtime call nên có timeout. `context.Context` giúp propagate cancel khi process shutdown hoặc request hết hạn.

Retry chỉ nên dùng cho lỗi transient:

- worker API timeout ngắn;
- connection reset;
- runtime inspect lỗi tạm thời;
- metric endpoint chưa sẵn sàng.

Không retry vô hạn khi input sai, image name sai, permission denied, resource request không hợp lệ, hoặc state transition conflict. Retry vô hạn ở control plane có thể biến một bug nhỏ thành storm.

## Metrics Từ Linux

Một worker agent có thể đọc metric node từ Linux `/proc`:

- `/proc/stat`: CPU time, idle/non-idle delta;
- `/proc/meminfo`: memory total/available/used;
- `/proc/loadavg`: load average;
- filesystem stat: disk total/free/used.

Có thể dùng library để parse `/proc`, nhưng model vẫn nên tách thành struct riêng của tool:

```text
NodeStats
  CPU usage
  memory total/available/used
  disk total/free/used
  load average
  task count
```

Metric collector nên chạy theo interval riêng, ví dụ 15s, và cập nhật snapshot trong worker. API `/stats` chỉ nên trả snapshot gần nhất, không nên mỗi request lại đọc tất cả metric nếu việc đó có thể chậm hoặc block.

## Store Interface

Store interface nhỏ giúp tách control logic khỏi backend:

```text
Put(key, value)
Get(key)
List()
Count()
```

Với production, interface nên phân biệt rõ:

- key không tồn tại;
- serialization/deserialization lỗi;
- backend unavailable;
- transaction conflict;
- permission/file-system error.

Nếu `Get` chỉ trả `interface{}` và `error`, caller sẽ cần type assertion. Điều này chấp nhận được cho prototype, nhưng production code nên xem xét generic wrapper, typed repository, hoặc interface riêng cho từng aggregate quan trọng.

## Serialization Boundary

Khi store persistent lưu struct Go thành JSON, schema của struct trở thành contract. Thay đổi field name, kiểu dữ liệu, hoặc nested struct có thể làm dữ liệu cũ khó đọc lại.

Checklist khi thêm persistence:

- field nào là durable state, field nào chỉ là runtime cache?
- zero value có ý nghĩa hợp lệ không?
- timestamp dùng timezone/format nào?
- enum state có backward compatibility không?
- task/event/node có version field hoặc migration path không?

Với control-plane code, event log thường dễ audit hơn current-state-only store. Prototype có thể chỉ lưu state cuối, nhưng khi debug failure, event history giúp trả lời "ai đổi state, lúc nào, vì sao".

## In-Memory Store

In-memory store phù hợp để học và test:

- nhanh;
- không cần dependency;
- dễ fake failure;
- tốt cho unit test scheduler/worker loop.

Nhưng nó không phù hợp làm source of truth:

- mất state khi process restart;
- không share giữa manager replica;
- khó backup/restore;
- dễ data race nếu không có lock;
- không có audit/event history.

Dùng in-memory store để xây mental model, sau đó thêm persistent store trước khi nói đến recovery.

## BoltDB Và Embedded Persistence

Embedded key-value database như BoltDB hợp với prototype/control-plane nhỏ vì không cần database server riêng. Pattern cơ bản:

- mở DB file với file mode chặt, ví dụ `0600`;
- tạo bucket cho task/event/node;
- dùng read-only transaction cho `Get/List`;
- dùng read-write transaction cho `Put/Delete`;
- marshal struct thành JSON hoặc binary format;
- đóng DB khi process shutdown.

Cần cảnh giác:

- bucket đã tồn tại không nên làm service fail nếu đây là lần restart hợp lệ;
- JSON schema thay đổi cần migration hoặc backward compatibility;
- file corruption/permission lỗi cần message rõ;
- một file DB local không giải quyết HA manager;
- backup cần dùng cách nhất quán với transaction, không copy tùy tiện khi đang ghi.

## Health Check Và Runtime Inspect

Runtime inspect cho biết container/process state, nhưng chưa chắc ứng dụng khỏe. Health model nên có nhiều lớp:

- runtime state: container có tồn tại, đang running, exit code;
- application health: HTTP/TCP/exec probe theo contract của workload;
- node health: worker API, heartbeat, metric freshness;
- manager view: task-to-worker mapping, restart count, last transition.

Nếu health endpoint của app fail, manager có thể restart task trong giới hạn. Khi vượt restart limit, dừng retry tự động và surface evidence cho operator. Nếu worker API fail, cần phân biệt worker down, network split, và task down trước khi reschedule.

## Scheduler Integration

Scheduler nên nhận node stats đã được normalize, không tự đi gọi HTTP trong mỗi policy nếu có thể tránh. Một flow gọn:

```text
manager refresh node stats
scheduler filter candidate nodes
scheduler score candidates
scheduler pick best node
manager records task-to-worker mapping
manager sends intent to selected worker
```

Với stop/update existing task, manager phải dùng `task-to-worker` mapping để gọi đúng worker. Chọn lại worker bằng scheduler cho thao tác stop là bug nguy hiểm, vì request có thể đến node không chạy task.

## Production Checklist

- Runtime operation có timeout và context không?
- Adapter có che giấu secret trong error/log không?
- Metrics endpoint có trả snapshot và timestamp không?
- Store có phân biệt not found và backend error không?
- Persistent DB có backup/restore/migration story không?
- Worker restart có reconstruct được task/container state không?
- Manager restart có biết task nào ở worker nào không?
- Health check có restart limit và backoff không?
- Retry có giới hạn và chỉ áp dụng cho transient error không?
- Serialization schema có migration hoặc compatibility story không?
- Persistent state có phân biệt durable field và runtime cache không?

## Liên Quan

- [Go Programming](./overview.md)
- [Go HTTP API, CLI And Background Workers](./02-go-http-api-cli-and-background-workers.md)
- [Go Orchestrator Implementation Patterns](./04-go-orchestrator-implementation-patterns.md)
- [Orchestrator Internals From Scratch](../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/00-architecture/02-orchestrator-internals-from-scratch.md)
