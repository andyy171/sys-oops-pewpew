# HA Cluster, Pacemaker và Corosync

## 1. Cluster Là Gì

Cluster là nhóm nhiều node phối hợp để cung cấp một dịch vụ hoặc workload. Trong Linux HA, cluster thường dùng để đảm bảo service tiếp tục chạy khi một node lỗi.

Các khái niệm chính:

- Node: server trong cluster.
- Resource: service/IP/filesystem/application do cluster quản lý.
- Failover: chuyển resource sang node khác khi node/service lỗi.
- Quorum: cơ chế quyết định cluster còn đủ số phiếu để hoạt động.
- Fencing/STONITH: cô lập node lỗi để tránh split-brain.

## 2. HA Cluster Giải Quyết Vấn Đề Gì

HA cluster giúp giảm downtime khi:

- Node chết.
- Service crash.
- Network/storage path lỗi.
- Cần maintenance từng node.

HA cluster không tự giải quyết:

- Data corruption.
- Application bug.
- Backup/restore.
- Thiết kế database replication sai.

## 3. Corosync: Membership và Messaging

Corosync cung cấp:

- Cluster membership: node nào đang tham gia cluster.
- Messaging: kênh trao đổi trạng thái giữa node.
- Quorum communication.

Kiểm tra:

```bash
corosync-cfgtool -s
corosync-quorumtool
journalctl -u corosync
```

## 4. Pacemaker: Resource Manager

Pacemaker quyết định resource chạy ở đâu, restart/failover thế nào và áp dụng constraint.

Kiểm tra:

```bash
pcs status
pcs cluster status
pcs resource status
crm_mon -1
journalctl -u pacemaker
```

Resource thường gặp:

- Virtual IP.
- Filesystem mount.
- systemd service.
- Database resource agent.
- Load balancer service.

## 5. Quorum và Split-brain

Quorum giúp cluster tránh trường hợp hai phía cùng nghĩ mình được quyền chạy resource.

Split-brain là trạng thái nguy hiểm khi cluster bị chia mạng và nhiều phía cùng active resource, đặc biệt nguy hiểm với shared storage.

Kiểm tra quorum:

```bash
corosync-quorumtool
pcs status
```

Production notes:

- Cluster 2 node cần thiết kế quorum/fencing cẩn thận.
- Không disable quorum trong production nếu chưa hiểu rủi ro.

## 6. Fencing / STONITH

Fencing cô lập node lỗi để đảm bảo node đó không còn ghi vào shared resource.

STONITH nghĩa là “Shoot The Other Node In The Head”, thường qua:

- IPMI/iDRAC/iLO power fence.
- Cloud API fence.
- Storage fence.

Kiểm tra:

```bash
pcs stonith status
pcs stonith config
```

Production notes:

- HA cluster production nên có fencing thật.
- Không dùng cluster quản lý shared storage write nếu fencing chưa hoạt động.

## 7. Resource, Constraint, Failover

Pacemaker quản lý resource thông qua resource agent. Ví dụ:

- `ocf:heartbeat:IPaddr2`
- `ocf:heartbeat:Filesystem`
- `systemd:<service>`

Kiểm tra resource agent:

```bash
pcs resource standards
pcs resource agents ocf:heartbeat
pcs resource describe ocf:heartbeat:IPaddr2
```

Kiểm tra resource:

```bash
pcs resource status
pcs resource config
pcs constraint
```

Disable/enable resource:

```bash
pcs resource disable <resource>
pcs resource enable <resource>
```

Move resource tạm thời:

```bash
pcs resource move <resource> <node>
pcs resource clear <resource>
```

Lưu ý: sau khi manual move, cần clear constraint tạm nếu không resource có thể bị pin ở node.

## 8. Các Lệnh Kiểm Tra Cơ Bản

```bash
pcs status
pcs cluster status
pcs node status
pcs resource status
pcs constraint
pcs property config
crm_mon -1
corosync-cfgtool -s
corosync-quorumtool
journalctl -u pacemaker
journalctl -u corosync
```

## 9. Troubleshooting Cluster Cơ Bản

### Resource Failed

```bash
pcs status
pcs resource failcount show
journalctl -u pacemaker --since "1 hour ago"
journalctl -u <resource-service> --since "1 hour ago"
```

Reset failcount sau khi sửa nguyên nhân:

```bash
pcs resource failcount show
pcs resource failcount reset <resource>
```

Kiểm tra:

- Service config.
- Permission.
- Port.
- Filesystem mount.
- Dependency.

Clear failure sau khi sửa:

```bash
pcs resource cleanup <resource>
```

### Node Offline

```bash
pcs status nodes
corosync-cfgtool -s
journalctl -u corosync --since "1 hour ago"
```

Kiểm tra network cluster, firewall, hostname resolution, time sync.

### Quorum Lost

```bash
corosync-quorumtool
pcs status
```

Không force start resource nếu chưa hiểu phía còn lại của cluster đang ở đâu.

## 10. Production Safety Notes

- Test fencing trước khi go-live.
- Ghi rõ runbook failover và failback.
- Theo dõi clock sync giữa node.
- Không thao tác trực tiếp service do Pacemaker quản lý bằng `systemctl restart` trừ khi runbook cho phép.
- Trước maintenance, đưa node/resource vào trạng thái phù hợp bằng `pcs`.

Maintenance mode:

```bash
pcs property set maintenance-mode=true
pcs property set maintenance-mode=false
```

Standby node:

```bash
pcs node standby <node>
pcs node unstandby <node>
```

Fencing validation chỉ chạy trong maintenance/test có phê duyệt:

```bash
pcs stonith fence <node>
```
