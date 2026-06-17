# Compute Platforms

## Overview

Compute không chỉ là CPU. Trong hạ tầng hiện đại, từng loại workload có thể cần loại accelerator khác nhau: GPU cho parallel training/inference, TPU cho workload ML quy mô Google, NPU cho edge/mobile inference, DPU cho offload network/storage/security trong data center, và LPU cho inference latency thấp theo kiến trúc chuyên biệt.

## Canonical Notes

- [Virtual Machines And Hypervisors](./01-virtual-machines-and-hypervisors.md)
- [Node.js Và Express Runtime Operations](./02-nodejs-express-runtime-operations.md)

## CPU, GPU, TPU, NPU, LPU, DPU

| Loại | Phù hợp với | Điểm mạnh | Giới hạn thường gặp |
|---|---|---|---|
| CPU | Orchestration, control plane, general workload, preprocessing | Linh hoạt, chạy OS và nhiều loại task | Không tối ưu cho parallel math lớn |
| GPU | Training, inference, deep learning, graphics, batch parallel compute | Massive parallelism, ecosystem CUDA lớn | Tốn điện, đắt, có overhead cho task nhỏ |
| TPU | ML workload rất lớn, tensor/matrix operation | Tối ưu cho matrix ops và scale pod lớn | Phụ thuộc ecosystem/framework/cloud hỗ trợ |
| NPU | Mobile/edge inference, low-power AI | Latency thấp, tiết kiệm điện, dữ liệu ở gần thiết bị | Chủ yếu inference, model size hạn chế |
| LPU | Real-time LLM serving/inference chuyên biệt | Latency thấp, deterministic execution cho một số workload | Dùng hẹp, phụ thuộc vendor và mô hình triển khai |
| DPU | Data center infrastructure offload | Offload networking, storage, encryption, firewall khỏi CPU host | Phức tạp vận hành, phù hợp data center hơn edge nhỏ |

## Cách Chọn Nhanh

- Cần chạy OS, scheduler, API server, controller, preprocessing: dùng CPU.
- Cần training hoặc inference song song lớn: cân nhắc GPU.
- Cần ML scale rất lớn và platform hỗ trợ tốt: cân nhắc TPU.
- Cần inference trên thiết bị edge/mobile, ít điện, latency thấp: cân nhắc NPU.
- Cần LLM serving realtime với latency cực thấp và stack phù hợp: cân nhắc LPU.
- Cần giảm tải networking/storage/security khỏi CPU trong data center: cân nhắc DPU/SmartNIC.

## Góc Nhìn Hạ Tầng

Khi đưa accelerator vào platform, đừng chỉ nhìn throughput. Cần đánh giá:

- Latency và tail latency.
- Power draw và cooling.
- Driver, firmware, runtime và scheduler support.
- Khả năng monitor utilization, memory, temperature và error.
- Cost per workload, không chỉ cost per device.
- Tích hợp với Kubernetes device plugin, quota và node pool.

## Related Pages

- [Kubernetes Overview](../03-container-orchestration/01-kubernetes/overview.md)
- [Container Runtime](../02-container-runtime/01-docker/overview.md)
- [HTTP Và Web Application Operations](../../02-core-infrastructure/02-network/04-protocols-and-services/06-http-web-application-operations.md)
