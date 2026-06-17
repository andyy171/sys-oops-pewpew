# Renew kubeadm Control-Plane Certificates

Runbook này dùng khi cluster Kubernetes dựng bằng `kubeadm` bị hết hạn hoặc sắp hết hạn certificate control plane. Mục tiêu là renew certificate, nạp lại static Pod control plane, cập nhật kubeconfig và validate cluster an toàn.

## Phạm Vi Áp Dụng

Áp dụng cho:

- cluster dùng `kubeadm`;
- control plane chạy static Pod qua `kubelet`;
- admin có quyền SSH vào control-plane node;
- có quyền chạy `sudo kubeadm`.

Không áp dụng nguyên xi cho managed Kubernetes như EKS/GKE/AKS hoặc cluster được lifecycle tool khác quản lý.

## Triệu Chứng

- `kubectl` báo lỗi `x509: certificate has expired or is not yet valid`.
- Không truy cập được API server.
- Pod hệ thống hoặc Pod mới kẹt `Pending`.
- Log `kube-apiserver`, `kube-controller-manager`, `kube-scheduler` có lỗi certificate/authentication.
- `kubeadm certs check-expiration` báo certificate đã hết hạn hoặc `<invalid>`.

## Nguyên Tắc An Toàn

- Không reboot đồng loạt tất cả control-plane node.
- Với HA cluster, thao tác từng control-plane node một.
- Backup `/etc/kubernetes` trước khi renew.
- Kiểm tra time sync trước khi kết luận certificate lỗi.
- Không commit kubeconfig, certificate hoặc private key thật vào repo.

## Precheck

Chạy trên từng control-plane node:

```bash
sudo kubeadm certs check-expiration
timedatectl
sudo systemctl status kubelet
```

Kiểm tra node và Pod nếu API server còn truy cập được:

```bash
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
```

## Backup

```bash
sudo tar -czf /root/kubernetes-certs-backup-$(date +%F-%H%M).tgz /etc/kubernetes

# Nếu cluster dùng external etcd hoặc cert etcd nằm riêng, backup thêm path tương ứng.
sudo tar -czf /root/etcd-certs-backup-$(date +%F-%H%M).tgz /etc/ssl/etcd/ssl 2>/dev/null || true
```

## Renew Certificate

Thực hiện trên từng control-plane node:

```bash
sudo kubeadm certs renew all
sudo kubeadm certs check-expiration
```

Nếu vẫn còn `<invalid>` hoặc thời hạn không đổi, dừng lại và kiểm tra:

- giờ hệ thống trên node;
- version `kubeadm`;
- node có đúng là control-plane node không;
- file certificate/key có đúng path không;
- cert etcd có được quản lý riêng không.

## Cập Nhật Kubeconfig

Trên control-plane node:

```bash
mkdir -p "$HOME/.kube"
sudo cp -i /etc/kubernetes/admin.conf "$HOME/.kube/config"
sudo chown "$(id -u):$(id -g)" "$HOME/.kube/config"
```

Nếu admin dùng `kubectl` từ máy ngoài, copy kubeconfig mới về máy client theo quy trình bảo mật nội bộ.

## Nạp Lại Certificate Cho Control Plane

Với kubeadm, control plane thường chạy dạng static Pod. Restart kubelet để static Pod được recreate và đọc cert mới:

```bash
sudo systemctl restart kubelet
```

Sau đó kiểm tra:

```bash
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
```

## Reboot Tuần Tự Nếu Cần

Nếu restart kubelet không đủ hoặc node vẫn giữ trạng thái lỗi, reboot từng control-plane node:

```bash
sudo reboot
```

Quy trình HA:

1. Reboot một control-plane node.
2. Chờ node quay lại `Ready`.
3. Kiểm tra static Pod control plane trên node đó.
4. Kiểm tra API server vẫn phục vụ request.
5. Chỉ tiếp tục node kế tiếp khi node trước đã ổn.

## Validation

```bash
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl run cert-renew-test --image=nginx --restart=Never --namespace=default
kubectl get pod cert-renew-test -n default -w
kubectl delete pod cert-renew-test -n default
```

Kết quả mong muốn:

- node ở trạng thái `Ready`;
- Pod control plane và kube-system không crash loop;
- Pod test chuyển sang `Running`;
- `kubectl` không còn lỗi x509;
- certificate mới có thời hạn hợp lệ trong `kubeadm certs check-expiration`.

## Rollback / Escalation

Nếu sau renew API server vẫn lỗi:

- xem `journalctl -u kubelet`;
- kiểm tra static Pod manifest trong `/etc/kubernetes/manifests`;
- kiểm tra certificate/key được mount đúng vào static Pod;
- kiểm tra etcd certificate nếu API server không kết nối được etcd;
- dùng backup `/etc/kubernetes` để so sánh hoặc rollback có kiểm soát.

Không xóa certificate/key cũ hoặc regenerate lung tung khi chưa backup. Với production, nên có console/SSH path độc lập và snapshot/backup etcd trước khi thao tác.
