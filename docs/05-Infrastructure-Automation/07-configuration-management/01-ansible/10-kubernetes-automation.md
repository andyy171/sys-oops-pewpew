# Ansible Kubernetes Automation

## Overview

Ansible co the tuong tac voi Kubernetes theo ba lop:

- bootstrap cluster/host: cai runtime, kubelet, kubeadm, CNI va dependency tren node tu quan;
- apply/read Kubernetes object qua Kubernetes API;
- chay task dac biet trong Pod bang `kubectl` connection plugin hoac `kubectl exec`.

Trong production, Ansible nen co ranh gioi ro voi Kubernetes/GitOps. Ansible phu hop cho bootstrap, one-off migration co kiem soat, hoac automation nho. Voi application release dai han, GitOps controller, Helm/Kustomize va manifest repository thuong la source of truth tot hon.

## Mental Model

```text
Ansible playbook
-> kubeconfig / Kubernetes API client
-> kube-apiserver
-> desired state stored in etcd
-> controllers / scheduler / kubelet reconcile actual state
```

Ansible khong schedule Pod truc tiep. No tao/sua object tren API server; Kubernetes controller moi dua actual state ve desired state.

## When To Use

Dung Ansible voi Kubernetes khi:

- bootstrap self-managed cluster hoac lab cluster;
- cai dat node prerequisite truoc khi `kubeadm init/join`;
- apply mot so manifest nen tang co owner ro;
- validate cluster readiness sau khi provision;
- doc resource info de phuc vu runbook co audit.

Can can nhac cong cu khac khi:

- deploy app lien tuc: GitOps/CI/CD;
- quan ly chart release: Helm/Kustomize/GitOps controller;
- lifecycle cluster production tren cloud: managed Kubernetes + Terraform/OpenTofu/provider API;
- cluster self-managed lon: Kubespray, Cluster API hoac platform lifecycle tool rieng.

## Cluster Bootstrap Guardrails

Voi cluster tu quan, Ansible co the chuan bi host va goi kubeadm, nhung phai xem day la platform lifecycle work, khong phai playbook lab don gian.

Pre-check toi thieu:

```bash
ansible all -i inventory.ini -m ping
ansible all -i inventory.ini -b -m command -a "hostname -I"
ansible all -i inventory.ini -b -m command -a "free -m"
ansible all -i inventory.ini -b -m command -a "swapon --show"
ansible all -i inventory.ini -b -m command -a "systemctl is-active containerd"
```

Production checklist:

- pin Kubernetes, kubelet, kubectl, kubeadm va container runtime version theo compatibility matrix cua platform;
- disable/configure swap theo policy cluster;
- chon CNI, Pod CIDR va Service CIDR khong conflict voi datacenter/VPC;
- co endpoint API server on dinh, load balancer neu HA;
- backup PKI, kubeconfig bootstrap va etcd snapshot neu self-managed;
- khong phat tan `admin.conf` lam kubeconfig hang ngay cho user/CI;
- validate node `Ready`, CoreDNS, CNI, kube-proxy, metrics/logging va storage class sau bootstrap.

## Apply Kubernetes Objects With Ansible

Ansible Kubernetes modules nen duoc xem nhu Kubernetes API client. Desired state van nen nam trong manifest/Helm values/Kustomize overlay co review.

Workflow an toan:

```text
render manifest
-> lint/schema/policy check
-> kubectl diff or tool diff
-> apply with Ansible/Kubernetes module
-> wait rollout/readiness
-> validate service path and events
```

Doc resource truoc khi thay doi:

```bash
kubectl get deploy,svc,endpointslices -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl auth can-i apply deployments -n <namespace>
```

Guardrails:

- dung namespace ro rang, khong apply vao `default` neu khong co ly do;
- gan label/annotation owner, app, environment, managed-by;
- khong hard-code Secret plaintext trong playbook hoac manifest;
- khong dung image tag mutable nhu `latest` cho production;
- kiem tra `state: absent` nhu thao tac destructive vi co the xoa Deployment, Service, RBAC hoac Secret;
- khong de Ansible va GitOps controller cung ghi cung object/field neu chua co ownership boundary.

## Helm From Ansible

Tai lieu cu thuong nhac Helm v2 va Tiller. Trong production hien dai, xem Tiller la legacy/security risk vi no chay trong cluster va thuong duoc gan quyen rong. Neu gap cluster cu con Tiller, can co plan migrate sang Helm v3 hoac GitOps-managed Helm.

Voi Helm v3:

- identity goi Helm chinh la identity goi Kubernetes API;
- RBAC cua runner/operator quyet dinh object nao duoc tao/sua/xoa;
- `helm template`, `helm lint`, `helm diff`/GitOps diff nen chay truoc install/upgrade;
- pin chart version va image tag/digest;
- khong commit Secret plaintext trong values.

Ansible co the orchestrate Helm CLI/module, nhung source of truth nen ro:

```text
Git chart/values
-> render/diff/review
-> Ansible or GitOps applies release
-> helm/kubectl status
-> app validation
```

## NodePort, LoadBalancer Va Exposure

NodePort phu hop cho lab, bare-metal demo hoac troubleshooting co gioi han. Production exposure thuong can Ingress/Gateway/LoadBalancer, TLS, DNS, firewall/security group va observability.

Khi playbook tao Service:

- xac dinh vi sao dung `ClusterIP`, `NodePort`, `LoadBalancer` hay Ingress/Gateway;
- verify Service co EndpointSlice backend ready;
- khong expose database/admin UI ra node/public network neu chua co auth/TLS/network policy;
- voi NodePort, ghi ro port range, firewall va ai duoc truy cap.

## Kubectl Connection Plugin

`kubectl` connection plugin cho phep Ansible chay command ben trong Pod. Day la pattern huu ich cho lab, break-glass hoac legacy app chua co API tot, nhung khong nen la deployment model mac dinh.

Rui ro:

- Pod la disposable; command chay trong Pod co the mat khi Pod recreate;
- container co the khong co Python, nen nhieu module Ansible khong chay duoc;
- `kubectl exec` co the doc/ghi runtime state va can audit nhu thao tac nhay cam;
- debug trong Pod de tao drift thu cong neu thay doi filesystem/runtime thay vi manifest.

Dung pattern nay khi co:

- namespace va Pod selector ro;
- RBAC rieng cho `pods/exec` neu can;
- command read-only truoc;
- evidence/log luu lai;
- permanent fix dua ve image, manifest, config hoac app API.

## Validation And Rollback

Sau khi automation tac dong cluster:

```bash
kubectl get nodes -o wide
kubectl get pods -A
kubectl get events -A --sort-by=.lastTimestamp
kubectl rollout status deployment/<name> -n <namespace>
kubectl get svc,endpointslices -n <namespace>
```

Rollback phu thuoc loai thay doi:

- manifest/app release: revert Git commit, Helm rollback hoac apply version da biet tot;
- cluster bootstrap/add-on: rollback manifest/add-on version, restore config va kiem tra control plane;
- etcd/control plane: chi restore tu snapshot bang runbook da test;
- data/PV: dung backup/storage snapshot/database restore, khong gia dinh Pod rollback se rollback data.

## Related Pages

- [Ansible Overview](./overview.md)
- [Docker Container Automation](./09-docker-container-automation.md)
- [Kubernetes Cluster Lifecycle Va Setup](../../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/07-cluster-lifecycle/overview.md)
- [Kubernetes Packaging Va GitOps](../../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/06-packaging-and-gitops/overview.md)
- [Kubernetes Helm Chart, Values Va Template](../../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/06-packaging-and-gitops/02-helm-chart-values-and-template.md)
- [Kubernetes RBAC, Pod Security Va Admission](../../../03-compute-and-orchestration/03-container-orchestration/01-kubernetes/04-security/01-rbac-pod-security-and-admission.md)
