---
title: "Tóm tắt CAP Theorem"
date: 2025-09-09T20:00:00+07:00
draft: false
author: ""
description: "Tổng quan về CAP Theorem – nguyên lý cốt lõi trong thiết kế hệ thống phân tán"
categories: ["Hệ thống phân tán"]
tags: ["CAP", "Consistency", "Availability"]
---

## Giới thiệu
**CAP Theorem** (Định lý CAP) là nguyên lý quan trọng trong thiết kế **hệ thống phân tán**. Nó cho biết trong một hệ thống phân tán, **không thể đồng thời đảm bảo hoàn hảo** cả ba tính chất:
- **Consistency (Nhất quán)**
- **Availability (Sẵn sàng)**
- **Partition Tolerance (Chịu phân hoạch)**

Định lý này được đề xuất bởi **Eric Brewer** và trở thành nền tảng khi xây dựng các cơ sở dữ liệu và dịch vụ phân tán hiện đại.

---

## Ba tính chất chính

### 1. Consistency – Nhất quán
Mọi node trong hệ thống luôn trả về cùng một dữ liệu tại cùng một thời điểm.  
Ví dụ: Khi bạn ghi dữ liệu mới vào hệ thống, mọi node sẽ ngay lập tức cập nhật và trả về dữ liệu mới đó.

### 2. Availability – Sẵn sàng
Hệ thống luôn phản hồi yêu cầu đọc/ghi, dù có lỗi ở một phần của hệ thống.  
Ví dụ: Ngay cả khi một node gặp sự cố, người dùng vẫn nhận được phản hồi từ các node còn lại.

### 3. Partition Tolerance – Chịu phân hoạch
Hệ thống vẫn hoạt động khi xảy ra **mất kết nối mạng** hoặc phân tách giữa các node.  
Ví dụ: Nếu một phần mạng bị cắt, hệ thống vẫn xử lý yêu cầu của người dùng thay vì dừng hoàn toàn.

---

## Nguyên lý cốt lõi
Trong thực tế, **Partition Tolerance** gần như bắt buộc trong các hệ thống phân tán (vì mạng không bao giờ hoàn hảo). Khi xảy ra phân hoạch, hệ thống buộc phải chọn **hoặc Consistency** hoặc **Availability**:

- **CA (Consistency + Availability):** Chỉ khả thi khi không có phân hoạch (hệ thống tập trung).
- **CP (Consistency + Partition Tolerance):** Ưu tiên tính nhất quán, chấp nhận giảm sẵn sàng khi có phân hoạch.
- **AP (Availability + Partition Tolerance):** Ưu tiên tính sẵn sàng, chấp nhận dữ liệu có thể không nhất quán tạm thời.

---

## Minh họa
| Lựa chọn | Đặc điểm chính | Ví dụ |
|----------|---------------|-------|
| **CA** | Nhất quán + Sẵn sàng, không chịu phân hoạch | Hệ thống tập trung, RDBMS truyền thống |
| **CP** | Nhất quán + Chịu phân hoạch | HBase, MongoDB (chế độ ưu tiên nhất quán) |
| **AP** | Sẵn sàng + Chịu phân hoạch | Cassandra, DynamoDB |

---

## Kết luận
**CAP Theorem** giúp các kiến trúc sư và kỹ sư hệ thống phân tán **định hướng thiết kế**. Thay vì cố đạt cả 3 yếu tố, cần **xác định ưu tiên** theo nhu cầu ứng dụng:
- Nếu yêu cầu **nhất quán tuyệt đối**, chọn **CP**.
- Nếu yêu cầu **sẵn sàng cao**, chọn **AP**.
