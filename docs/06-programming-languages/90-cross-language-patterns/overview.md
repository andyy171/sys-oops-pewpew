# Cross-Language Patterns

Cross-language patterns là nơi đặt các pattern học lập trình dùng chung cho Go, Python, C++ và các ngôn ngữ khác. Mục tiêu là tránh lặp lại cùng một mental model ở từng ngôn ngữ, đồng thời vẫn link về implementation cụ thể khi cần.

## Chủ Đề Nên Đặt Ở Đây

- Project structure và separation of concerns.
- Error handling, retry, timeout, cancellation.
- CLI UX: subcommand, flag, config, output, exit code.
- HTTP API client/server boundary.
- Testing strategy: unit, integration, fake, fixture, golden file.
- Logging, metrics, tracing trong tool nhỏ.
- Dependency management và packaging.
- Concurrency mental model: thread, goroutine, async task, queue, worker pool.

## Chủ Đề Không Đặt Ở Đây

- Syntax hoặc library cụ thể của một ngôn ngữ; đặt trong nhánh ngôn ngữ đó.
- Runbook vận hành hạ tầng; đặt trong domain vận hành tương ứng.
- Vendor/tool-specific workflow; đặt gần vendor/tool đó.

## Liên Quan

- [Programming Languages](../overview.md)
- [Go Programming](../01-go/overview.md)
- [Python Programming](../02-python/overview.md)
- [C++ Programming](../03-cpp/overview.md)
