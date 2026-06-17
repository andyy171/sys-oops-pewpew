# Maven Lifecycle And Build Pipeline

## Overview

Note này chuyển hóa file thô `maven-life-cycle.md`. Maven là build tool phổ biến cho Java project, thường xuất hiện trong CI pipeline để compile, test, package và publish artifact.

## Maven Lifecycle

Maven tổ chức build theo lifecycle. Khi gọi một phase, Maven chạy các phase trước đó trong cùng lifecycle theo thứ tự.

### Clean Lifecycle

Dùng để dọn output build cũ:

```bash
mvn clean
```

`clean` thường chạy ở đầu pipeline để tránh artifact cũ làm nhiễu kết quả build.

### Default Lifecycle

Đây là lifecycle chính:

| Phase | Ý nghĩa |
|---|---|
| `validate` | kiểm tra project có đủ thông tin để build |
| `compile` | compile source code |
| `test` | chạy unit test |
| `package` | đóng gói artifact như JAR/WAR |
| `verify` | chạy thêm kiểm tra integration/quality nếu cấu hình |
| `install` | đưa artifact vào local Maven repository |
| `deploy` | publish artifact lên remote repository |

Lệnh hay dùng:

```bash
mvn test
mvn package
mvn clean package
mvn clean install
```

Nếu chạy `mvn package`, Maven sẽ chạy các phase trước đó như `validate`, `compile`, `test` rồi mới `package`.

### Site Lifecycle

Dùng để tạo documentation/site report:

```bash
mvn site
```

Trong CI thông thường, `site` ít nằm trong đường build chính hơn `test/package/deploy`, nhưng hữu ích khi project cần publish documentation/report.

## Maven Trong CI/CD

Pipeline Java thường có:

```text
checkout -> mvn clean test -> mvn package -> scan/report -> publish artifact
```

Ví dụ:

```bash
mvn --batch-mode clean test
mvn --batch-mode clean package
```

`--batch-mode` phù hợp CI vì giảm output tương tác và tránh prompt.

## Artifact Repository

Sau khi package, artifact như `.jar` hoặc `.war` nên được publish vào repository như Nexus hoặc Artifactory. Điều này giúp:

- version artifact rõ ràng;
- rollback về bản cũ;
- deploy cùng một artifact qua nhiều môi trường;
- trace được artifact đến commit/build number.

## Common CI Notes

- Không bỏ qua test bằng `-DskipTests` trong pipeline chính nếu không có lý do rõ ràng.
- Cache Maven dependency giúp build nhanh hơn, nhưng cần tránh cache che lỗi dependency.
- Tách unit test và integration test nếu integration test cần service ngoài.
- Không đưa credential repository trực tiếp vào `pom.xml`; dùng CI secret hoặc settings được quản lý.

## Related Pages

- [Pipeline stages build, test, deploy](./02-Pipeline%20stages%20build,%20test,%20deploy.md)
- [Artifact Management](./03-Artifact%20management%20%28Nexus,%20Artifactory%29.md)
- [DevOps Lifecycle, Environments And Interview Flow](../00-devops-lifecycle-environments-and-interview-flow.md)
