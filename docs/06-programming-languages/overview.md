# Programming Languages

Domain này chứa kiến thức học ngôn ngữ lập trình phục vụ system engineering, cloud, DevOps, SRE, automation và infrastructure tooling. Mục tiêu là học ngôn ngữ như một năng lực nền: cú pháp, type system, project structure, runtime model, concurrency, package/module, testing, CLI/API/service patterns và cách ứng dụng vào vận hành hạ tầng.

## Chứa Gì

- Go: service, CLI, agent, controller, runtime integration, control-plane tooling.
- Python: scripting, automation, data processing, API client, glue code, testing và ops tooling.
- C++: systems programming, memory model, performance, Linux/native integration và runtime-level concepts.
- Cross-language patterns: error handling, packaging, dependency management, testing, CLI design, API client, concurrency model.

## Không Chứa Gì

- Workflow vận hành cụ thể bằng Terraform, Ansible, CI/CD, Prometheus, Grafana; đặt ở [Infrastructure Automation](../05-infrastructure-automation/overview.md).
- Kubernetes object/control plane behavior; đặt ở [Kubernetes](../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/overview.md).
- Linux kernel, filesystem, networking, storage internals; đặt ở [Core Infrastructure](../02-core-infrastructure/overview.md).

## Learning Path

- [Go Programming](./01-go/overview.md)
- [Python Programming](./02-python/overview.md)
- [C++ Programming](./03-cpp/overview.md)
- [Cross-Language Patterns](./90-cross-language-patterns/overview.md)

## Tổ Chức

Mỗi ngôn ngữ nên có:

- `overview.md`: mục tiêu học, khi dùng, learning path;
- language foundations: type, function, module/package, error;
- application patterns: CLI, HTTP API, service, background job;
- systems/infrastructure integration nếu phù hợp;
- testing/debugging/performance notes.

Không tạo note theo chapter/course/book nếu nội dung có thể chuyển thành concept bền vững.
