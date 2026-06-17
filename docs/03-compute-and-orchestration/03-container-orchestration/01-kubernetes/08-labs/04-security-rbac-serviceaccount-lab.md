# Kubernetes Security RBAC Và ServiceAccount Lab

## Goal

Tạo ServiceAccount, Role và RoleBinding để thấy RBAC cho phép hoặc chặn thao tác API theo namespace.

## What You Will Learn

- ServiceAccount là identity cho Pod/controller trong cluster.
- RBAC quyết định identity được làm gì với resource nào.
- `kubectl auth can-i` là lệnh kiểm tra nhanh quyền.

## Topology

```text
ServiceAccount
-> RoleBinding
-> Role
-> allowed verbs/resources
```

## Prerequisites

- Cluster lab.
- Quyền tạo Role/RoleBinding trong namespace lab.

## Safety Notes

Không bind `cluster-admin` trong lab nếu không cần. Không dùng namespace production.

## Steps

```bash
kubectl create ns k8s-lab
kubectl create serviceaccount app-reader -n k8s-lab
kubectl create role pod-reader --verb=get,list,watch --resource=pods -n k8s-lab
kubectl create rolebinding app-reader-pods --role=pod-reader --serviceaccount=k8s-lab:app-reader -n k8s-lab
```

Kiểm tra quyền:

```bash
kubectl auth can-i list pods --as=system:serviceaccount:k8s-lab:app-reader -n k8s-lab
kubectl auth can-i delete pods --as=system:serviceaccount:k8s-lab:app-reader -n k8s-lab
```

## Validation

Kết quả mong đợi:

```text
yes
no
```

## Cleanup

```bash
kubectl delete ns k8s-lab
```

## Common Failure Cases

- Bind nhầm namespace nên quyền không có hiệu lực.
- Dùng `ClusterRoleBinding` khi chỉ cần quyền namespace.
- Nhầm authentication với authorization: user/SA tồn tại không có nghĩa là có quyền.

## Related Theory

- [RBAC, Pod Security Và Admission](../04-security/01-rbac-pod-security-and-admission.md)
- [ConfigMap, Secret, Downward API Và API Access](../09-application-integration/01-configmap-secret-downward-api-and-api-access.md)
