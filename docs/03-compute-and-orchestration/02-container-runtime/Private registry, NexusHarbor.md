# Private Registry, Nexus, Harbor Và OCI Distribution

## Overview

Container registry là nơi lưu và phân phối container image. Ở mức thấp, registry hiện đại thường đi theo OCI Distribution Specification: một HTTP API nhỏ đặt trên content-addressable blob store.

Người dùng thường thao tác qua `docker pull`, `docker push`, Kubernetes manifest hoặc Helm chart. Nhưng khi debug production, hiểu registry API giúp trả lời các câu hỏi khó hơn:

- Tag đang trỏ tới manifest nào?
- Image pull chọn sai platform vì sao?
- Layer nào bị thiếu hoặc corrupt?
- Xóa tag đã đủ để xóa image thật chưa?
- Multi-platform image được biểu diễn như thế nào?

## Mental Model

Một image trong registry không phải là một file duy nhất:

- **Blob**: dữ liệu bất kỳ được lưu theo digest, ví dụ layer tarball, image config, SBOM, provenance, Helm chart.
- **Digest**: địa chỉ nội dung, thường là `sha256:<hash>`.
- **Manifest**: JSON document mô tả image, trỏ tới config blob và các layer blob.
- **Tag**: tên thân thiện như `v1`, `latest`, `1.2.3`, trỏ tới một manifest.
- **Image index / manifest list**: manifest cấp cao cho multi-platform image, trỏ tới nhiều manifest theo platform.

Registry vì vậy giống một blob store có index JSON hơn là một kho lưu file image nguyên khối.

## Registry API Cốt Lõi

Các endpoint quan trọng:

```text
POST /v2/<repo>/blobs/uploads/
PUT  /v2/<repo>/blobs/uploads/<upload-id>?digest=<digest>
GET  /v2/<repo>/blobs/<digest>
PUT  /v2/<repo>/manifests/<tag-or-digest>
GET  /v2/<repo>/manifests/<tag-or-digest>
GET  /v2/<repo>/tags/list
DELETE /v2/<repo>/manifests/<tag-or-digest>
DELETE /v2/<repo>/blobs/<digest>
```

Push image về bản chất là:

1. Hash từng layer và config để có digest.
2. Upload layer/config như blob.
3. Push manifest JSON để nối các blob lại.
4. Gán tag cho manifest.

Pull image là chiều ngược lại:

1. Fetch manifest theo tag hoặc digest.
2. Đọc digest của config và layer trong manifest.
3. Download từng blob theo digest.
4. Runtime unpack layer và tạo rootfs.

## Ví Dụ Debug Bằng Curl

Liệt kê tag:

```bash
curl -s "https://registry.example.com/v2/<repo>/tags/list" | jq .
```

Fetch manifest và chỉ rõ media type mong muốn:

```bash
curl -s -L \
  -H "Accept: application/vnd.oci.image.manifest.v1+json, application/vnd.oci.image.index.v1+json" \
  "https://registry.example.com/v2/<repo>/manifests/<tag>" \
  | jq .
```

Download một blob theo digest:

```bash
curl -L -o layer.tar.gz \
  "https://registry.example.com/v2/<repo>/blobs/sha256:<digest>"
```

Khi debug lỗi image pull, luôn kiểm tra cả tag, manifest digest, media type, platform và digest của từng layer.

## Xóa Image Không Đơn Giản Là Xóa Tag

Tag chỉ là reference tới manifest. Xóa tag có thể chỉ làm manifest mất tên thân thiện, nhưng manifest và blob vẫn còn addressable bằng digest.

Muốn xóa thật cần hiểu quan hệ tham chiếu:

- Một manifest có thể có nhiều tag.
- Nhiều manifest có thể dùng chung layer blob.
- Multi-platform image có image index trỏ tới nhiều manifest con.
- Registry có thể cần garbage collection riêng để dọn blob không còn reference.

Vì vậy không nên xóa blob trực tiếp nếu chưa chắc blob đó không được manifest khác dùng chung. Với registry production, ưu tiên dùng chính sách retention/garbage collection của registry thay vì script tự xóa blob.

## Multi-Platform Image

Multi-platform image không thêm endpoint mới. Registry vẫn dùng endpoint manifest, nhưng document trả về có thể là:

- Single-platform manifest: có `config` và `layers`.
- Image index / manifest list: có `manifests[]`, mỗi phần tử có `digest` và `platform`.

Client cần nhìn `Content-Type` hoặc `mediaType` để biết đang nhận manifest thường hay image index.

Ví dụ inspect nhanh:

```bash
curl -s -L \
  -H "Accept: application/vnd.oci.image.manifest.v1+json, application/vnd.oci.image.index.v1+json" \
  "https://registry.example.com/v2/<repo>/manifests/<tag>" \
  | jq '{mediaType, config, layers, manifests}'
```

Nếu pull sai architecture, hãy kiểm tra image index có entry đúng `linux/amd64`, `linux/arm64` hoặc platform mong muốn hay không.

## Harbor, Nexus Và Private Registry

Harbor và Nexus thường bổ sung các tính năng quản trị quanh registry API:

- Authentication và authorization theo project/repository.
- HTTPS/TLS và certificate management.
- Image scan, SBOM, signature hoặc policy.
- Retention policy và garbage collection.
- Replication giữa registry.
- Audit log cho push/pull/delete.

Trong production, registry nên được xem như một phần của supply chain, không chỉ là nơi lưu image.

## Registry Như Thành Phần Platform

Khi container platform mở rộng ra nhiều team, registry trở thành control point cho artifact, policy và audit. Thiết kế registry cần trả lời được:

- Ai được push, pull, promote, delete hoặc sửa retention policy?
- Image đi từ dev sang staging/prod bằng cùng digest hay bị rebuild lại?
- Registry có tích hợp được với CI/CD, scanner, signing/provenance, artifact store và audit log không?
- Retention/garbage collection có giữ đủ artifact cho rollback nhưng không làm storage phình vô hạn không?
- Nếu registry chính lỗi, node mới hoặc rollout mới có pull được image từ replica/cache không?

Production guardrails:

- Tách project/repository theo ownership và environment boundary khi cần, nhưng vẫn giữ promotion trace được theo digest.
- Dùng robot/service account scope hẹp cho pipeline; không dùng account cá nhân để push release image.
- Hạn chế quyền delete/overwrite tag production; nếu cần cleanup, chạy qua retention policy có audit.
- Backup metadata/config và storage backend trước upgrade hoặc garbage collection lớn.
- Log actor, source digest, target repository, tag, scan/signature status và thời điểm promote.

Registry nên tích hợp với artifact management rộng hơn thay vì sống tách biệt. Ví dụ: release package, Helm chart, SBOM, provenance và container image cần cùng một câu chuyện ownership, retention, audit và rollback.

## Image Promotion Giữa Môi Trường

Continuous delivery nên promote cùng một image digest qua các stage thay vì rebuild lại ở từng môi trường. Registry có thể phản ánh stage bằng repository/project riêng, tag promotion hoặc metadata tùy platform, nhưng artifact gốc cần truy vết được.

Mental model:

```text
CI build -> registry/dev@sha256:...
test pass -> promote same digest to staging
approval/pass -> promote same digest to prod
```

Guardrails:

- Ưu tiên promote theo digest, không chỉ theo tag mutable.
- Người hoặc pipeline promote cần quyền tối thiểu: pull từ source repo, push/copy sang target repo; không cần quyền xóa blob.
- Trước khi promote, kiểm tra scan/signature/provenance policy đã pass.
- Sau khi promote, verify manifest digest ở registry đích trùng với digest nguồn.

Ví dụ copy bằng Docker CLI khi không có registry-native replication/copy:

```bash
docker pull registry-a.example.com/project/app:<tag>
docker tag registry-a.example.com/project/app:<tag> registry-b.example.com/project/app:<tag>
docker push registry-b.example.com/project/app:<tag>
```

Với production, ghi log source registry, target registry, tag, digest, actor/pipeline id và thời điểm promote. Không chạy cleanup/prune trên host promotion nếu chưa xác nhận image/layer còn cần cho rollback hay không.

## Transfer Khi Không Có Registry Hoặc Băng Thông Hạn Chế

Registry vẫn là cách chuẩn để phân phối image. Khi air-gap, low-bandwidth hoặc môi trường tạm không có registry, có thể dùng TAR artifact nhưng phải hiểu khác biệt:

| Lệnh | Giữ layer/history/metadata | Dùng khi |
|---|---|---|
| `docker save` / `docker load` | Có | Di chuyển image nguyên vẹn giữa daemon/host |
| `docker export` / `docker import` | Không; chỉ filesystem phẳng | Migration/lab hoặc flatten có kiểm soát |

Ví dụ chuyển image nguyên vẹn:

```bash
docker save registry.example.com/project/app:<tag> -o app-image.tar
sha256sum app-image.tar > app-image.tar.sha256
```

Ở phía nhận:

```bash
sha256sum -c app-image.tar.sha256
docker load -i app-image.tar
docker image inspect registry.example.com/project/app:<tag>
```

Guardrails:

- TAR image là artifact supply-chain; lưu checksum/signature, kiểm soát quyền truy cập và retention.
- Không dùng `export/import` cho release artifact nếu cần provenance, label, config, history hoặc scan metadata.
- Nếu image từng chứa secret trong layer, `save/load` sẽ giữ secret đó; xử lý như incident và rotate secret.
- Với low-bandwidth link, ưu tiên registry replication, pull-through cache hoặc công cụ đồng bộ có deduplication được vận hành rõ; tự chế pool/chunk phải có cleanup, integrity check và audit.

## Local Registry Pattern

Với lab hoặc môi trường nội bộ nhỏ, có thể chạy registry distribution tối thiểu:

```bash
docker run -d --name registry \
  -p 5000:5000 \
  -v registry-data:/var/lib/registry \
  registry:2
```

Pattern này hữu ích để test push/pull, cache image gần lab hoặc chia sẻ artifact trong network kín. Nó không phải baseline production nếu chưa có TLS, auth, backup, retention, monitoring và access control.

Nếu client cần cấu hình insecure registry, hãy coi đó là ngoại lệ tạm thời:

```json
{
  "insecure-registries": ["registry.example.com:5000"]
}
```

Guardrails:

- Ưu tiên HTTPS với certificate được trust rõ ràng thay vì `insecure-registries`.
- Không expose registry lab ra internet hoặc network multi-tenant.
- Backup volume/storage backend của registry trước khi nâng cấp hoặc chạy garbage collection.
- Bật auth/authorization nếu registry chứa proprietary image.
- Kiểm tra pull/push bằng tag test trước khi đưa registry vào pipeline.

## Geo-Replication Và Image Distribution

Khi workload chạy ở nhiều region, registry cũng trở thành một dependency của rollout và self-healing. Nếu node ở region xa phải pull image từ một registry duy nhất, thời gian start Pod, recovery sau node failure và rollout speed đều bị ảnh hưởng bởi latency, bandwidth và availability của registry đó.

Các pattern phổ biến:

- cloud/container registry có geo-replication managed;
- nhiều registry theo region như `us.registry.example.com`, `eu.registry.example.com`;
- một hostname dùng GeoDNS hoặc Anycast để đưa pull request tới registry gần nhất.

Trade-off:

| Pattern | Ưu điểm | Rủi ro |
|---|---|---|
| Managed geo-replication | Ít vận hành, policy tập trung | phụ thuộc capability/provider |
| Registry theo region | đơn giản, rõ region nào dùng registry nào | manifest/values phải parameterize image registry |
| GeoDNS/Anycast registry | một endpoint duy nhất cho cluster | networking phức tạp, debug khó hơn |

Với hệ thống nhỏ, một registry có HA tốt có thể đủ. Với rollout toàn cầu hoặc nhiều cluster production, image replication nên là một bước tự động trong pipeline trước khi mở rollout sang region đó.

## Docker Login Và Credential Risk

`docker login` lưu credential/token để client có thể pull/push image. Tùy phiên bản Docker và credential helper, thông tin có thể nằm trong Docker config của user, thường dưới `~/.docker/config.json`, hoặc được chuyển sang OS credential store.

Kiểm tra an toàn:

```bash
cat ~/.docker/config.json
docker logout registry.example.com
```

Production notes:

- Không dùng account cá nhân lâu dài cho CI/CD push image; ưu tiên robot/service account có scope hẹp.
- Không commit `~/.docker/config.json` hoặc credential helper output vào repository.
- Dùng HTTPS và certificate trust rõ ràng cho private registry.
- Rotate token khi runner, laptop hoặc bastion bị nghi ngờ lộ.
- Với Kubernetes, quản lý registry credential qua Secret/External Secrets và RBAC phù hợp.

## Best Practices

- Luôn dùng HTTPS cho registry có authentication.
- Pin image bằng digest cho workload quan trọng thay vì chỉ dùng tag mutable như `latest`.
- Dùng tag có ý nghĩa release: `1.2.3`, git SHA, build number.
- Không xóa blob thủ công nếu chưa kiểm tra reference.
- Bật retention policy và garbage collection có kiểm soát.
- Scan image và lưu SBOM/provenance nếu pipeline yêu cầu compliance.
- Với Kubernetes, kiểm tra `imagePullPolicy`, registry secret và platform của node khi gặp lỗi pull.

## Related Pages

- [Docker Overview](./01-docker/overview.md)
- [Image Layer, Dockerfile Best Practices](./Image%20layer,%20Dockerfile%20best%20practices.md)
