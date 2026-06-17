# Go HTTP API, CLI And Background Workers

Nhiều infrastructure tool Go có cùng một hình dạng: API nhận intent, background worker thực hiện công việc, store giữ state, CLI gọi API cho operator. Nếu giữ boundary này sạch, tool dễ debug hơn và ít tạo ra state nửa vời khi có failure.

## API Boundary

`net/http` đủ để viết API nhỏ. Khi cần route có path parameter như `/tasks/{taskID}`, dùng router nhẹ như `chi` giúp handler gọn hơn.

Handler nên:

- validate method, route parameter, JSON body và required field;
- trả đúng status code;
- không làm việc lâu trong request path nếu có thể enqueue intent;
- không gọi Docker/runtime SDK trực tiếp;
- không mutate current-state store trước khi background loop chấp nhận xử lý.

Mẫu handler nên đi theo flow:

```text
decode request JSON
validate unknown fields and required fields
create intent/event
enqueue or persist accepted intent
return response with task ID/status
```

## JSON Decode Và Response

Với API nội bộ, dùng `json.Decoder` và bật unknown field để tránh client gửi sai schema mà server im lặng bỏ qua.

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
```

Status code nên có ý nghĩa vận hành:

- `201 Created`: manager/worker đã chấp nhận intent tạo/chạy task.
- `200 OK`: đọc state hoặc trả resource.
- `204 No Content`: đã chấp nhận stop/delete intent và không cần body.
- `400 Bad Request`: JSON sai, UUID sai, field không hợp lệ.
- `404 Not Found`: task/node không tồn tại trong store.
- `409 Conflict`: state transition không hợp lệ hoặc task đang ở terminal state.
- `500 Internal Server Error`: backend/store/runtime lỗi bất ngờ.

Lưu ý: `201 Created` không có nghĩa container đã chạy thành công. Nó chỉ nên có nghĩa API đã chấp nhận intent. State thật phải xem qua status endpoint.

## Manager API Và Worker API

Tách hai API:

- manager API: user/CLI gọi để submit, stop, status, list node/task;
- worker API: manager gọi để start/stop task, lấy task list, lấy node stats/health.

Operator không nên bypass manager để gọi worker trong luồng bình thường, vì manager cần giữ mapping task-to-worker và global state. Bypass chỉ nên là thao tác break-glass có log và quy trình riêng.

## Background Loop

Background loop là nơi reconcile intent thành hành động thật. Trong Go, có thể bắt đầu bằng goroutine đơn giản:

```text
start API server
start worker loop in goroutine
start metrics loop in goroutine
block until process exits
```

Worker loop nên:

- pop intent từ queue;
- đọc current state từ store;
- validate transition;
- gọi runtime adapter;
- ghi state mới vào store;
- log evidence nếu lỗi.

Loop không nên busy-spin. Nếu queue rỗng, sleep ngắn hoặc dùng primitive blocking queue. Production code nên có `context.Context` để shutdown gọn, timeout cho network call, và structured logging.

## Config Từ Env Và Flag

Env variable phù hợp cho container deployment, flag phù hợp cho CLI/operator. Dùng default an toàn và validate kiểu dữ liệu sớm.

```text
CUBE_HOST=0.0.0.0
CUBE_PORT=5555
CUBE_DB_TYPE=memory
```

Khi parse port bằng `strconv.Atoi`, lỗi parse nên làm process fail fast với message rõ. Dùng placeholder cho secret như `<TOKEN>` hoặc `<PASSWORD>`, không ghi secret thật vào note, config mẫu hay command history.

## CLI Boundary

Cobra phù hợp cho CLI có nhiều subcommand. Cấu trúc operator dễ nhớ:

```text
tool manager --host 0.0.0.0 --port 5555
tool worker --name worker-a --manager http://10.0.0.10:5555
tool run --image nginx:stable --memory 128M --cpu 1
tool stop <task-id>
tool status <task-id>
tool node list
```

CLI nên là client của manager API, không phải đường tắt vào store local. Điều này giữ một source of truth cho state và cho phép audit, auth, validation, retry ở manager.

Một Cobra-style app thường có:

```text
main.go        -> gọi cmd.Execute()
cmd/root.go    -> root command, global flags, config init
cmd/worker.go  -> start worker service
cmd/manager.go -> start manager service
cmd/run.go     -> submit task qua manager API
cmd/stop.go    -> stop task qua manager API
cmd/status.go  -> đọc task status
cmd/node.go    -> đọc node/worker list
```

`main.go` nên càng mỏng càng tốt. Logic thật nằm trong package domain/service, còn `cmd/*.go` chỉ parse flag, validate input, gọi service hoặc API client. Nếu command trực tiếp mutate store hoặc gọi worker bypass manager, CLI sẽ phá source of truth của control plane.

CLI tốt nên có:

- `--help` hữu ích cho từng command;
- flag rõ tên và có default hợp lý;
- output machine-readable khi cần automation, ví dụ `--output json`;
- exit code khác 0 khi API trả lời lỗi;
- timeout cho request;
- không in secret ra stdout/stderr.

## Service Command Và Client Command

Trong orchestrator nhỏ, có hai loại command:

- service command: `manager`, `worker` khởi động process lâu dài, mở API server và background loop;
- client command: `run`, `stop`, `status`, `node` gửi request tới manager API rồi thoát.

Hai loại này không nên dùng chung lifecycle. Service command cần signal handling, graceful shutdown, log liên tục, health endpoint. Client command cần timeout ngắn, output rõ, exit code chính xác.

Khi chuyển từ env sang flag, giữ nguyên nguyên tắc: flag của CLI/operator nên override default; env phù hợp khi chạy trong container hoặc systemd unit; config file phù hợp khi số option tăng nhiều.

## Error Handling

Trong API và background loop, lỗi nên được gắn context:

- input lỗi: trả cho client biết field nào sai;
- state conflict: nói task đang ở state nào và transition nào bị từ chối;
- worker API lỗi: ghi worker address, task ID, attempt count;
- runtime lỗi: ghi container/runtime operation, nhưng không leak secret env;
- store lỗi: phân biệt not found, serialization error, transaction error.

Với orchestrator, "không gọi được worker API" không đồng nghĩa "task đã chết". Manager cần health model và timeout rõ trước khi reschedule để tránh duplicate workload.

## Goroutine Lifecycle

Go làm việc với goroutine rất tiện, nhưng mỗi goroutine lâu dài cần có lifecycle rõ:

```text
go worker.RunTasks(ctx)
go worker.CollectStats(ctx)
go worker.UpdateTasks(ctx)
api.Start(ctx)
```

Lab code có thể dùng `context.Background()` và sleep cố định để dễ hiểu. Code vận hành nên truyền `context.Context`, đóng queue hoặc channel khi shutdown, và đảm bảo API server dừng nhận request trước khi store/runtime bị đóng.

## Liên Quan

- [Go Programming](./overview.md)
- [Go Project Structure And Domain Modeling For Ops Tools](./01-go-project-structure-and-domain-modeling.md)
- [Go Runtime Integration, Metrics And Persistence](./03-go-runtime-integration-metrics-and-persistence.md)
- [Go Orchestrator Implementation Patterns](./04-go-orchestrator-implementation-patterns.md)
