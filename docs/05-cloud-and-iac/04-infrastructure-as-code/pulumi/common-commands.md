# Pulumi CLI Commands Quick Reference

## 1. Khởi tạo & Đăng nhập

`pulumi new <template>` – Tạo dự án mới từ template  
_Ví dụ_: `pulumi new aws-python`

`pulumi login [backend]` – Đăng nhập Pulumi Service hoặc backend tự host  
_Ví dụ_: `pulumi login s3://my-pulumi-state`

## 2. Quản lý Stack & Config

`pulumi stack init <name>` – Tạo stack mới cho môi trường  
`pulumi stack select <name>` – Chuyển stack hiện tại sang <name>  
`pulumi stack ls` – Liệt kê các stack có sẵn  
`pulumi stack rm <name>` – Xoá stack  

`pulumi config set <key> <value>` – Đặt config cho stack hiện tại  
_Ví dụ_: `pulumi config set aws:region us-east-1`

`pulumi config set <key> <value> --secret` – Đặt config dạng secret (mã hoá)  
`pulumi config get <key>` – Lấy giá trị config  
`pulumi config rm <key>` – Xoá config  
`pulumi config refresh` – Đồng bộ config với backend  

## 3. Deploy & Quản lý Hạ tầng

`pulumi preview` – Xem trước các thay đổi (diff)  
`pulumi up` – Deploy / update hạ tầng theo code  
`pulumi destroy` – Xoá toàn bộ hạ tầng trong stack hiện tại  
`pulumi refresh` – Đồng bộ trạng thái thực tế trên cloud với state Pulumi  

## 4. Quản lý Resource & State

`pulumi state` – Quản lý state trực tiếp (liệt kê, import, xoá…)  
`pulumi state delete <urn>` – Xoá resource khỏi state (không xoá trên cloud)  

`pulumi import <type> <name> <id>` – Import tài nguyên có sẵn trên cloud  
_Ví dụ_:  
`pulumi import aws:s3/bucket:Bucket mybucket my-existing-bucket`

`pulumi cancel` – Huỷ một deployment đang chạy  

## 5. Secrets & Outputs

`pulumi stack output` – Xem các output đã export  
`pulumi stack output --json` – Xuất output dưới dạng JSON  

`pulumi secrets` – Quản lý secret provider  
`pulumi config set <key> <value> --secret` – Đặt secret cho config  

## 6. Tiện ích khác

`pulumi about` – Xem thông tin version, môi trường  
`pulumi version` – Kiểm tra version Pulumi CLI  
`pulumi plugin ls` – Liệt kê plugin providers đang cài  
`pulumi plugin install <type> <version>` – Cài plugin provider cụ thể  
`pulumi whoami` – Kiểm tra tài khoản Pulumi đang đăng nhập  

## 7. Workflow mẫu AWS / GCP

```bash
# AWS
pulumi new aws-python
pulumi stack init dev
pulumi config set aws:region us-east-1
pulumi up

# GCP
pulumi new gcp-python
pulumi stack init prod
pulumi config set gcp:project my-gcp-project
pulumi config set gcp:region us-central1
pulumi up