# GlusterFS

## Cach Hieu Nhanh

GlusterFS la distributed filesystem gom nhieu server thanh mot namespace file chung. Moi server cung cap mot hoac nhieu brick, Gluster ghep cac brick thanh volume de client mount va doc/ghi file.

Mental model:

```text
client mount
-> Gluster volume
-> translator stack
-> brick selection / replica set
-> file operation on backend filesystem
-> replication / healing
```

GlusterFS phu hop khi ung dung can shared filesystem va co the chap nhan tradeoff cua distributed file operations. Neu workload can database-grade consistency/latency hoac object/block semantics, can danh gia Ceph, NFS, object storage hoac application-level replication.

## Core Concepts

| Concept | Y nghia |
|---|---|
| Brick | Directory tren server dung lam backend storage cho volume |
| Volume | Logical filesystem ma client mount |
| Replica | So ban sao cua file tren cac brick khac nhau |
| Peer | Gluster node trong trusted pool |
| Heal | Qua trinh dong bo lai ban sao khi node/brick bi lech |
| Mount point | Duong dan client dung de truy cap volume |

Replication trong Gluster tang availability/durability truoc loi node/disk nhat dinh, nhung khong phai backup. Xoa nham, ghi sai du lieu hoac ransomware co the duoc replicate sang cac replica.

## Basic Setup Flow

Flow tong quat cho replicated volume:

```text
install gluster packages on all nodes
-> create brick directory on each node
-> open required firewall ports between storage nodes/clients
-> peer probe nodes into trusted pool
-> create replicated volume
-> start volume
-> mount volume on clients
-> validate peer/volume/heal state
```

Automation bang Ansible co the dung module/package/service/mount de lam idempotent hon, nhung cac thao tac volume van can pre-check va validation nhu storage operation.

## Ansible Automation Pattern

Pattern role/playbook:

```yaml
- name: Ensure brick and mount directories exist
  file:
    path: "{{ item }}"
    state: directory
    mode: "0775"
  loop:
    - "{{ gluster_brick_dir }}"
    - "{{ gluster_mount_dir }}"

- name: Create replicated Gluster volume
  gluster_volume:
    state: present
    name: "{{ gluster_volume_name }}"
    brick: "{{ gluster_brick_dir }}"
    replicas: 2
    cluster: "{{ groups['gluster'] | join(',') }}"
    host: "{{ inventory_hostname }}"
  run_once: true

- name: Mount Gluster volume
  mount:
    path: "{{ gluster_mount_dir }}"
    src: "{{ inventory_hostname }}:/{{ gluster_volume_name }}"
    fstype: glusterfs
    opts: "defaults,_netdev"
    state: mounted
```

Guardrails:

- Dung `run_once: true` cho volume create de tranh race condition.
- Khong dung `force: yes` tren production tru khi da hieu vi sao Gluster tu choi tao brick; `force` co the bo qua safety check ve brick/backend.
- Brick nen nam tren filesystem/disk rieng, khong phai root filesystem, neu la production.
- Firewall chi mo port Gluster giua node/client can thiet; port can kiem tra theo version va transport dang dung.
- Mount voi `_netdev` de tranh boot block khi network/storage chua san sang.

## Pre-Check

Truoc khi tao/chinh sua volume:

```bash
ansible gluster -i inventory.ini -b -m command -a "gluster peer status"
ansible gluster -i inventory.ini -b -m command -a "gluster volume info"
ansible gluster -i inventory.ini -b -m command -a "df -h"
```

Kiem tra:

- Tat ca node reachable va DNS/hostname/IP on dinh.
- Disk/backend filesystem cho brick co dung capacity va mount point.
- Time sync hoat dong.
- Firewall giua peers/client da mo dung scope.
- Khong co volume heal/rebalance dang chay neu thao tac co rui ro.
- Da co backup/snapshot cho du lieu quan trong.

## Validation

Sau khi deploy:

```bash
gluster peer status
gluster volume status <volume>
gluster volume info <volume>
gluster volume heal <volume> info
mount | grep gluster
```

Data path validation:

```bash
touch /mnt/gluster/test-file
ls -l /mnt/gluster/test-file
```

Trong production, validation nen bao gom:

- application read/write test co rollback.
- check latency/error tu app.
- heal backlog khong tang bat thuong.
- disk usage khong lech qua muc giua bricks.

## Failure Modes

| Symptom | Huong kiem tra |
|---|---|
| Client mount fail | DNS/IP, firewall, volume status, glusterd service |
| File thieu tren mot node | Heal info, split-brain, node da tung down |
| Latency tang | Network, disk IO, heal/rebalance, small-file workload |
| Volume started nhung app loi | Permission/UID/GID, SELinux/AppArmor, mount options |
| Disk gan day | Brick usage, log volume, rebalance plan |

## Production Risks

- Split-brain co the xay ra khi replica set mat quorum/ket noi va nhieu phia cung ghi.
- Small-file workload co the tao overhead metadata lon.
- Heal/rebalance co the lam tang IO latency.
- Xoa volume/brick hoac sua brick path la destructive operation.
- Mo firewall rong cho storage ports lam tang attack surface.

Destructive commands nhu delete volume, remove brick, replace brick, peer detach, wipe disk hoac force create phai co approval, backup, maintenance window, rollback/restore plan va validation sau thao tac.

## Trang Lien Quan

- [Storage Systems](../overview.md)
- [Distributed Storage Overview](../../04-distributed-storage-concepts/01-distributed-storage-overview.md)
- [Replication Erasure Coding Quorum](../../04-distributed-storage-concepts/02-replication-erasure-coding-quorum.md)
