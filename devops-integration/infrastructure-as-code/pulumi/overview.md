# Tổng quan Pulumi

## 1. Pulumi là gì?
Pulumi là **Infrastructure as Code (IaC)** hiện đại cho phép bạn **mô tả, triển khai, quản lý hạ tầng** bằng các ngôn ngữ lập trình phổ biến (TypeScript, Python, Go, C#, Java…).  
Bạn có thể dùng cùng một codebase để deploy tài nguyên lên nhiều cloud như AWS, GCP, Azure, Kubernetes…

## 2. Pulumi khác gì so với các IaC tools khác?

- **Ngôn ngữ lập trình thực**: Thay vì HCL (Terraform) hay YAML/JSON (CloudFormation), Pulumi dùng TypeScript/Python/Go… ⇒ dễ reuse code, chia module, viết test.
- **Hệ sinh thái & testing**: Tận dụng luôn package & framework của ngôn ngữ ⇒ unit test, integration test hạ tầng như code ứng dụng.
- **Quản lý state linh hoạt**: Pulumi Service (SaaS), hoặc backend tự host (S3, Azure Blob, local…).
- **Đa cloud**: Một dự án có thể deploy song song nhiều cloud provider (AWS + GCP).
- **Thân thiện Dev & CI/CD**: CLI, SDK, stack config, secrets tích hợp pipeline dễ dàng.

## 3. Cài đặt nhanh

### 3.1 Cài đặt CLI
```bash
# MacOS/Linux
curl -fsSL https://get.pulumi.com | sh

# Windows (PowerShell)
iex ((New-Object System.Net.WebClient).DownloadString('https://get.pulumi.com/install.ps1'))

# Kiểm tra
pulumi version
```

### 3.2 Đăng nhập backend lưu state
```bash
# Dùng Pulumi Service (mặc định)
pulumi login

# Hoặc backend tự quản lý (AWS S3)
pulumi login s3://my-pulumi-state

# Hoặc backend tự quản lý (GCP GCS)
pulumi login gs://my-pulumi-state

```

## 4. Khởi tạo dự án (Bootstrapping)
```yaml
mkdir sample-infra && cd sample-infra
pulumi new sample-python  # hoặc sample-typescript

# Kết quả sẽ sinh ra 2 file : File Pulumi.yaml chứa metadata của dự án  và file __main__.py chứa các infra define 

```

### Tạo môi trường cho các stack riêng 
```yaml
pulumi stack init dev
pulumi stack init prod
```

### Sample __main.py__
```python
import pulumi
import pulumi_aws as aws

# ----------------------------
# 1. VPC + Subnet + Internet Gateway + Route Table
# ----------------------------
vpc = aws.ec2.Vpc(
    "main-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": "main-vpc"}
)

subnet = aws.ec2.Subnet(
    "public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    tags={"Name": "public-subnet"}
)

igw = aws.ec2.InternetGateway(
    "igw",
    vpc_id=vpc.id,
    tags={"Name": "main-igw"}
)

route_table = aws.ec2.RouteTable(
    "public-rt",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=igw.id
    )],
    tags={"Name": "public-rt"}
)

aws.ec2.RouteTableAssociation(
    "public-rt-assoc",
    route_table_id=route_table.id,
    subnet_id=subnet.id
)

# ----------------------------
# 2. Security Group mở toàn bộ traffic (allow all)
# ----------------------------
allow_all_sg = aws.ec2.SecurityGroup(
    "allow-all-sg",
    vpc_id=vpc.id,
    description="Allow all inbound and outbound",
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        protocol="-1",  # all
        from_port=0,
        to_port=0,
        cidr_blocks=["0.0.0.0/0"]
    )],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        protocol="-1",
        from_port=0,
        to_port=0,
        cidr_blocks=["0.0.0.0/0"]
    )],
    tags={"Name": "allow-all-sg"}
)

# ----------------------------
# 3. AMI Amazon Linux 2
# ----------------------------
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[{"name": "name", "values": ["amzn2-ami-hvm-*"]}]
)

# ----------------------------
# 4. EC2 Instances (web1, web2, web3)
# ----------------------------
instances = []
for name in ["web1", "web2", "web3"]:
    instance = aws.ec2.Instance(
        name,
        instance_type="t2.micro",
        ami=ami.id,
        subnet_id=subnet.id,
        vpc_security_group_ids=[allow_all_sg.id],
        associate_public_ip_address=True,
        tags={"Name": name}
    )
    instances.append(instance)

# ----------------------------
# 5. Route53 Public DNS Record (giả sử bạn đã có Hosted Zone)
# ----------------------------
# Thay "example.com." bằng domain bạn đã đăng ký
hosted_zone = aws.route53.get_zone(name="example.com.", private_zone=False)

# Tạo record A cho web1 trỏ về IP công khai web1
dns_record = aws.route53.Record(
    "web1-dns",
    zone_id=hosted_zone.zone_id,
    name="web1.example.com",
    type="A",
    ttl=300,
    records=[instances[0].public_ip]
)

# ----------------------------
# 6. Export Output
# ----------------------------
pulumi.export("vpc_id", vpc.id)
pulumi.export("subnet_id", subnet.id)
pulumi.export("security_group_id", allow_all_sg.id)
pulumi.export("web1_public_ip", instances[0].public_ip)
pulumi.export("web2_public_ip", instances[1].public_ip)
pulumi.export("web3_public_ip", instances[2].public_ip)
pulumi.export("web1_dns", dns_record.fqdn)
```

## 5. Một số kịch bản phổ biến
### 5.1 AWS Example: S3 Bucket + EC2 Instance + Security Group (Python)
```yaml
import pulumi
import pulumi_aws as aws

# Tạo S3 bucket
bucket = aws.s3.Bucket("my-bucket")

# Security Group mở cổng 80
sg = aws.ec2.SecurityGroup("web-sg",
    description="Allow HTTP",
    ingress=[{"protocol":"tcp","from_port":80,"to_port":80,"cidr_blocks":["0.0.0.0/0"]}],
    egress=[{"protocol":"-1","from_port":0,"to_port":0,"cidr_blocks":["0.0.0.0/0"]}]
)

# Lấy AMI Amazon Linux 2 mới nhất
ami = aws.ec2.get_ami(most_recent=True, owners=["amazon"], 
    filters=[{"name":"name","values":["amzn2-ami-hvm-*"]}])

# EC2 Instance
server = aws.ec2.Instance("web-server",
    instance_type="t2.micro",
    vpc_security_group_ids=[sg.id],
    ami=ami.id)

pulumi.export("bucket_name", bucket.id)
pulumi.export("instance_public_ip", server.public_ip)
```
### 5.2 GCP Example: Storage Bucket + Compute Instance + Firewall Rule (Python)
```yaml
import pulumi
import pulumi_gcp as gcp

# Storage bucket
bucket = gcp.storage.Bucket("my-bucket", location="US")

# Firewall Rule mở cổng 80
fw = gcp.compute.Firewall("allow-http",
    network="default",
    allows=[gcp.compute.FirewallAllowArgs(
        protocol="tcp",
        ports=["80"],
    )],
    source_ranges=["0.0.0.0/0"]
)

# Compute Instance
instance = gcp.compute.Instance("vm-instance",
    machine_type="e2-micro",
    boot_disk=gcp.compute.InstanceBootDiskArgs(
        initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
            image="debian-cloud/debian-11"
        ),
    ),
    network_interfaces=[gcp.compute.InstanceNetworkInterfaceArgs(
        network="default",
        access_configs=[{}], # cấp IP công khai
    )])

pulumi.export("bucket_name", bucket.url)
pulumi.export("instance_external_ip", instance.network_interfaces[0].access_configs[0].nat_ip)
```
### 5.3 Triển khai
```yaml
pulumi preview   # Xem trước thay đổi
pulumi up        # Apply hạ tầng
pulumi destroy   # Xoá hạ tầng
```