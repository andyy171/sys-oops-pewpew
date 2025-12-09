# Resolve Lambda URL Error - Lỗi "signature not match" khi sử dụng POST/PUT

Bài viết này tập trung vào việc giải quyết lỗi xác thực (authentication) khi sử dụng AWS Lambda Function URL phía sau CloudFront, cụ thể là lỗi "signature not match" khi thực hiện các request POST hoặc PUT.

## Vấn đề hiện tại 
Thông báo lỗi thường gặp:
```json
{
  "message": "The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details."
}
```

Một vấn đề phổ biến mà nhiều người gặp phải (ví dụ như thảo luận [này](https://repost.aws/questions/QUbHCI9AfyRdaUPCCo_3XKMQ/lambda-function-url-behind-cloudfront-invalidsignatureexception-only-on-post)) là:

**Mô tả:** Sử dụng CloudFront đứng trước Lambda Function URL. Chỉ có phương thức GET hoạt động bình thường, trong khi POST hoặc PUT đều bị từ chối.

**Phân tích nguyên nhân**
Lambda URL hỗ trợ 2 loại xác thực (authentication types):

1. **NONE:** Bất kỳ ai có URL đều có thể truy cập function.

2. **AWS_IAM:** Yêu cầu request phải có signed-header.

![](./images/signature%20not%20match.webp)

Nếu bạn đang sử dụng AWS_IAM, người dùng không thể truy cập trực tiếp Lambda URL mà không có header được ký (cụ thể là x-amz-content-sha256).

## Giải pháp (Solution)

- Có hai giải pháp chính để xử lý vấn đề này:

### Giải pháp 1: Tạo signed-header bằng boto3 session (Client-side)
- Với cách này, custom header sẽ được thêm thủ công từ phía client trước khi gửi request.
    - Lưu ý: Việc sử dụng CloudFront lúc này là tùy chọn (chủ yếu cho mục đích CDN), vì việc ký header (signing) được thực hiện ở client chứ không phải tại CloudFront.

    - Nếu dùng CloudFront, bạn có thể gửi GET mà không cần header x-amz-content-sha256, nhưng nếu gọi trực tiếp vào Lambda URL, nó sẽ từ chối mọi method nếu thiếu chữ ký.

- Các bước thực hiện:

**Bước 1:** Tạo boto3 session để ký header
Sử dụng đoạn code Python sau để tạo lớp SigV4ASign:

```Python

import boto3
from botocore import crt, awsrequest

class SigV4ASign:
    def __init__(self, boto3_session=boto3.Session()):
        self.session = boto3_session

    def get_headers(self, service, region, aws_request_config):
        sigV4A = crt.auth.CrtS3SigV4AsymAuth(self.session.get_credentials(), service, region)
        request = awsrequest.AWSRequest(**aws_request_config)
        sigV4A.add_auth(request)
        prepped = request.prepare()
        return prepped.headers

    def get_headers_basic(self, service, region, method, url):
        sigV4A = crt.auth.CrtS3SigV4AsymAuth(self.session.get_credentials(), service, region)
        request = awsrequest.AWSRequest(method=method, url=url)
        sigV4A.add_auth(request)
        prepped = request.prepare()
        return prepped.headers
```
**Bước 2:** Sử dụng header trong request
Áp dụng lớp trên để gửi request:

```Python

from sigv4a_sign import SigV4ASign
import requests

service = 'lambda'
region = '*'
method = 'GET'
url = 'https://4xmze5deqxjjy4ltw2ze3h7gr40tlvcp.lambda-url.us-east-1.on.aws'

# Lấy signed headers
headers = SigV4ASign().get_headers_basic(service, region, method, url)

# Gửi request với headers đã ký
r = requests.get(url, headers=headers)
print(f'status_code: {r.status_code} \nobject text: {r.text}')
```

### Giải pháp 2: Bypass signed-header bằng cách dùng Lambda@Edge
- Giải pháp này sử dụng Lambda@Edge để gán token ngay tại CloudFront.

    - Tất cả traffic sẽ được ký tại CloudFront bởi Lambda@Edge, bất kể ai gửi request.

    - Mọi người đều có thể gọi Lambda URL thông qua domain của CloudFront.

    - Cách này hữu ích để ngăn traffic truy cập trực tiếp vào Lambda function (bỏ qua CloudFront), nhưng không dùng để xác thực người dùng (user validation).

Tham khảo cách triển khai ký custom header tại tài liệu : https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-edge-how-it-works-tutorial.html

## Đọc thêm (Further Read)

> Tại sao chỉ phương thức GET có thể bypass CloudFront để invoke Lambda URL?

Chúng ta biết Lambda URL (auth type AWS_IAM) yêu cầu mọi request phải được ký. Vậy tại sao GET lại đi qua được CloudFront?

Khi kiểm tra một request GET đi qua CloudFront, ta thấy CloudFront tự động thêm các headers, bao gồm x-amz-content-sha256:

```json
{
  "message": "Hello from Lambda!",
  "headers": {
    "x-amz-content-sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ...
  }
}
```

- Điều này cho thấy CloudFront **tự động ký request header** cho các request sử dụng phương thức `GET`.

- Tuy nhiên, khi gọi `POST`, lỗi sẽ xuất hiện: `"The request signature we calculated does not match..."`

=> Rõ ràng là phương thức `POST` **không được CloudFront ký mặc định.** Chúng ta cần tạo signed token cho header như ở Giải pháp 1.

>Theo tài liệu AWS, việc bật mặc định cho GET giúp truy cập dễ dàng hơn, trong khi `POST` vẫn yêu cầu signed payloads để bảo mật. Việc bypass cho GET giúp giảm công sức ký request và tiết kiệm chi phí/thời gian (vì GET rất phổ biến), nhưng nhược điểm là kém bảo mật hơn.

## Tài liệu tham khảo (Refs)
- https://github.com/vuongbachdoan/sigv4a-signing-examples/tree/main/python
- https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-lambda.html
- https://community.aws/content/2fuBTcoVg7nnRIVLnqjIsIC8LAi/enhancing-security-for-lambda-function-urls?lang=en