Cloud Native Infrastructure: Kubernetes trên Huawei Cloud
Container Cluster Management
Giới thiệu về Quản lý Cluster Container
Quản lý cluster container là nền tảng của kiến trúc cloud-native, cho phép triển khai, vận hành và quản lý các ứng dụng container hóa ở quy mô lớn.

Các thành phần chính trong quản lý cluster
Container Engine: Công cụ thời gian chạy container (thường là Docker hoặc containerd)

Orchestration Layer: Lớp điều phối (Kubernetes)

Network Plugin: Cung cấp mạng cho container

Storage Plugin: Cung cấp lưu trữ liên tục

Control Plane: Mặt phẳng điều khiển quản lý trạng thái cluster

Quản lý Cluster trên Huawei Cloud
Huawei Cloud Container Engine (CCE) cung cấp giải pháp quản lý cluster Kubernetes toàn diện:

Tính năng chính:

Triển khai cluster nhanh chóng (vài phút)

Hỗ trợ cluster cao cấp (Master nodes được quản lý)

Tích hợp với các dịch vụ Huawei Cloud khác

Tự động sửa chữa và mở rộng cluster

Quản lý vòng đời cluster đầy đủ

Các loại cluster:

CCE Standard: Cluster Kubernetes tiêu chuẩn

CCE Turbo: Hiệu suất cao với mạng container tốc độ cực nhanh

Công cụ quản lý:

Cloud Container Engine Console

Kubectl CLI

Kubernetes Dashboard

REST API

Kubernetes Architecture and Core Concepts
Kiến trúc Kubernetes
Kubernetes có kiến trúc client-server với các thành phần chính:

Control Plane Components
kube-apiserver: Front-end của control plane, xử lý các API requests

etcd: Kho lưu trữ key-value nhất quán cao cho dữ liệu cluster

kube-scheduler: Theo dõi các pod mới và chọn node để chạy

kube-controller-manager: Chạy các controller processes

cloud-controller-manager: Liên kết với cloud provider API

Node Components
kubelet: Đại lý chạy trên mỗi node, đảm bảo containers chạy trong pod

kube-proxy: Quản lý rules network trên mỗi node

Container Runtime: Phần mềm chạy containers (Docker, containerd, CRI-O)

Core Concepts Kubernetes
Pod
Đơn vị triển khai nhỏ nhất trong Kubernetes, chứa một hoặc nhiều container:

yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: nginx:latest
    ports:
    - containerPort: 80
Deployment
Quản lý việc triển khai và scaling của các pod replica sets:

yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
Service
Cung cấp điểm truy cập mạng ổn định đến tập hợp các pod:

yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
  type: LoadBalancer
Namespace
Cơ chế phân vùng tài nguyên cluster thành các không gian tên riêng biệt:

bash
# Tạo namespace
kubectl create namespace my-namespace

## Liệt kê namespace
kubectl get namespaces
ConfigMap và Secret
ConfigMap: Lưu trữ dữ liệu cấu hình không nhạy cảm

Secret: Lưu trữ thông tin nhạy cảm như mật khẩu, token

yaml
## ConfigMap example
apiVersion: v1
kind: ConfigMap
metadata:
  name: game-config
data:
  game.properties: |
    enemy.types=aliens,monsters
    player.maximum-lives=5
  ui.properties: |
    color.good=purple
    color.bad=yellow
Kubernetes Application Orchestration and Management
Triển khai ứng dụng
Deployment Strategies
Rolling Update: Cập nhật từng pod một (mặc định)

Recreate: Xóa tất cả pod cũ trước khi tạo pod mới

Blue-Green: Triển khai phiên bản mới song song, sau đó chuyển traffic

Canary: Triển khai phiên bản mới cho một phần người dùng

Health Checks
Liveness Probes: Kiểm tra container có đang chạy không

Readiness Probes: Kiểm tra container đã sẵn sàng nhận traffic chưa

Startup Probes: Kiểm tra ứng dụng đã khởi động xong chưa

yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-example
spec:
  containers:
  - name: liveness
    image: nginx
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 3
      periodSeconds: 3
Quản lý tài nguyên
Resource Requests và Limits
yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "250m"
  limits:
    memory: "128Mi"
    cpu: "500m"
Horizontal Pod Autoscaler (HPA)
Tự động scaling số lượng pod dựa trên CPU utilization hoặc custom metrics:

yaml
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
Quản lý configuration
Environment Variables
yaml
env:
- name: ENV_VAR_NAME
  value: "value"
- name: ENV_VAR_FROM_CONFIGMAP
  valueFrom:
    configMapKeyRef:
      name: special-config
      key: special.how
- name: ENV_VAR_FROM_SECRET
  valueFrom:
    secretKeyRef:
      name: secret-name
      key: username
Kubernetes Services Release
Service Types
ClusterIP
Service chỉ có thể truy cập từ bên trong cluster (mặc định):

yaml
apiVersion: v1
kind: Service
metadata:
  name: my-internal-service
spec:
  type: ClusterIP
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 9376
NodePort
Mở port trên mỗi node để truy cập service từ bên ngoài:

yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport-service
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 9376
    nodePort: 30007
LoadBalancer
Tạo external load balancer trong cloud provider:

yaml
apiVersion: v1
kind: Service
metadata:
  name: my-loadbalancer-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 9376
ExternalName
Ánh xạ service đến external DNS name:

yaml
apiVersion: v1
kind: Service
metadata:
  name: my-external-service
spec:
  type: ExternalName
  externalName: my.database.example.com
Ingress
Quản lý truy cập HTTP/HTTPS từ bên ngoài vào services:

yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
Service Mesh với Huawei Cloud
Huawei Cloud cung cấp Service Mesh (CSM) dựa trên Istio:

Quản lý traffic nâng cao

Observability

Bảo mật service-to-service

Policy enforcement

Kubernetes Storage Management
Persistent Storage Concepts
Persistent Volumes (PV)
Tài nguyên lưu trữ trong cluster được cung cấp bởi administrator:

yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: slow
  hostPath:
    path: "/mnt/data"
Persistent Volume Claims (PVC)
Yêu cầu lưu trữ từ user:

yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 3Gi
  storageClassName: slow
Storage Classes
Định nghĩa các "classes" storage với different profiles:

yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-storage
provisioner: disk.csi.huaweicloud.com
parameters:
  type: SSD
  fstype: ext4
reclaimPolicy: Delete
allowVolumeExpansion: true
Storage Options trên Huawei Cloud
Elastic Volume Service (EVS)
Block storage persistent, hiệu suất cao:

yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: evs-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: csi-disk
Scalable File Service (SFS)
File storage chia sẻ được nhiều pod truy cập đồng thời:

yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: sfs-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
  storageClassName: csi-nas
Object Storage Service (OBS)
Lưu trữ object với dung lượng lớn, chi phí thấp:

Không sử dụng PVC trực tiếp

Truy cập qua SDK hoặc mounted qua obsfs

Volume Types
EmptyDir
Volume tạm thời tồn tại cùng vòng đời pod:

yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pd
spec:
  containers:
  - image: nginx
    name: test-container
    volumeMounts:
    - mountPath: /cache
      name: cache-volume
  volumes:
  - name: cache-volume
    emptyDir: {}
HostPath
Mount file hoặc directory từ node host vào pod:

yaml
volumes:
- name: test-volume
  hostPath:
    path: /data
    type: Directory
CSI Drivers trên Huawei Cloud
Huawei Cloud cung cấp CSI drivers cho:

csi-disk: EVS block storage

csi-nas: SFS file storage

csi-sfs: SFS Turbo high-performance file storage

csi-obs: OBS object storage (through obsfs)

Backup và Restore
Volume Snapshots
yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-snapshot
spec:
  volumeSnapshotClassName: csi-disk-snapshot-class
  source:
    persistentVolumeClaimName: my-pvc
Application Backup với Velero
Huawei Cloud tích hợp với Velero để backup ứng dụng:

Backup persistent volumes

Backup Kubernetes resources

Cluster migration

Disaster recovery

Best Practices cho Storage Management
Sử dụng StorageClass thay vì PV tĩnh

Đặt reclaimPolicy phù hợp (Retain cho dữ liệu quan trọng)

Sử dụng ReadWriteMany cho dữ liệu chia sẻ

Monitoring storage usage và thiết lập alerts

Regular backup của persistent volumes

Sử dụng volume snapshots trước khi cập nhật ứng dụng quan trọng

Đây là kiến thức toàn diện về Kubernetes trên Huawei Cloud, từ quản lý cluster cơ bản đến các tính năng nâng cao như storage management và service release.
