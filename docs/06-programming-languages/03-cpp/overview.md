# C++ Programming

C++ là nhánh học ngôn ngữ dành cho systems programming, performance-sensitive code, native Linux integration, memory model và runtime-level concepts. Trong vault này, C++ nên được học như nền tảng để hiểu sâu hơn về hệ thống, runtime, networking, storage engine, database engine và phần mềm hạ tầng hiệu năng cao.

## Khi Dùng C++

- Cần kiểm soát memory layout, allocation, object lifetime và performance.
- Làm việc gần OS, network stack, storage engine, database engine, runtime hoặc embedded/native integration.
- Cần hiểu RAII, ownership, move semantics, concurrency primitive và build/link model.
- Đọc hoặc debug phần mềm hạ tầng viết bằng C/C++.

## Learning Path Dự Kiến

- C++ language foundations: type, function, class, template, namespace.
- Memory and ownership: stack/heap, pointer, reference, RAII, smart pointer.
- Build model: compiler, linker, header/source, CMake hoặc build system.
- STL and algorithms: container, iterator, algorithm, string, chrono.
- Concurrency: thread, mutex, atomic, condition variable, memory ordering.
- Systems integration: file descriptor, socket, Linux API, performance profiling.

## Ranh Giới Với Core Infrastructure

- Kiến thức C++ language/runtime đặt ở đây.
- Linux kernel, filesystem, networking, storage concepts đặt ở [Core Infrastructure](../../02-core-infrastructure/overview.md).
- Khi note C++ dùng một concept Linux để giải thích code, link sang Core Infrastructure thay vì copy lại toàn bộ.

## Liên Quan

- [Programming Languages](../overview.md)
- [Core Infrastructure](../../02-core-infrastructure/overview.md)
