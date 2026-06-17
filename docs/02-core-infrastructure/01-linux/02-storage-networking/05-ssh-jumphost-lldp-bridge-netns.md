# SSH, JumpHost, LLDP, Bridge và Network Namespace

## 1. SSH Remote Access

SSH là kênh quản trị từ xa phổ biến nhất trên Linux.

```bash
ssh user@server
ssh -p 2222 user@server
ssh -v user@server
```

Các file quan trọng:

| Path | Vai trò |
| --- | --- |
| `~/.ssh/id_ed25519` | Private key của user |
| `~/.ssh/id_ed25519.pub` | Public key |
| `~/.ssh/authorized_keys` | Public key được phép login vào account |
| `~/.ssh/known_hosts` | Host key của server đã từng kết nối |
| `~/.ssh/config` | Client config |
| `/etc/ssh/ssh_config` | Global client config |
| `/etc/ssh/sshd_config` | Server config |
| `/etc/ssh/ssh_known_hosts` | Known hosts dùng chung toàn hệ thống |

## 2. SSH Key và Config

Tạo key:

```bash
ssh-keygen -t ed25519 -C "user@example.com"
```

Copy public key:

```bash
ssh-copy-id -n user@server
ssh-copy-id user@server
```

`ssh-copy-id -n` là dry-run: xem key nào sẽ được thêm vào server trước khi thay đổi `authorized_keys`. Sau khi copy key, test bằng session mới trước khi tắt password authentication.

Ví dụ `~/.ssh/config`:

```sshconfig
Host app-1
    HostName 10.0.10.11
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

Hardening cơ bản phía server:

```text
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowGroups ssh-admins
```

Sau khi sửa:

```bash
sudo sshd -t
sudo systemctl reload sshd
```

Hardening chi tiết hơn nằm ở [SUID, SGID, SELinux, PAM, auditd và Hardening](../03-security-logs-troubleshooting/03-suid-sgid-selinux-pam-auditd-hardening.md).

### Host Key Và Known Hosts

Host key định danh server SSH. Lần đầu kết nối, client thường hỏi có tin fingerprint của server không; production nên xác minh fingerprint qua kênh độc lập hoặc quản lý `/etc/ssh/ssh_known_hosts` bằng automation.

Nếu thấy cảnh báo `REMOTE HOST IDENTIFICATION HAS CHANGED`, không xóa dòng trong `known_hosts` theo thói quen. Trước tiên xác nhận:

```bash
ssh-keygen -l -f /etc/ssh/ssh_host_ed25519_key.pub
ssh-keygen -F <host>
ssh -vvv user@server
```

Nguyên nhân hợp lệ có thể là rebuild host, rotate host key hoặc đổi IP/DNS trỏ sang host khác. Nguyên nhân rủi ro là MITM, DNS spoofing hoặc host compromise.

### SSH Agent

`ssh-agent` giữ private key đã unlock trong session, giúp dùng key có passphrase mà không phải nhập lại liên tục:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh-add -l
ssh-add -d ~/.ssh/id_ed25519
```

Guardrails:

- Private key nên có passphrase nếu dùng trên workstation/admin laptop.
- Không bật agent forwarding mặc định vào bastion không tin cậy.
- Khi rời máy shared/bastion, remove key khỏi agent hoặc kết thúc session agent.

## 3. JumpHost / Bastion With ProxyJump

Kết nối qua bastion:

```bash
ssh -J bastion-user@bastion.example.com app-user@10.0.20.10
```

Config:

```sshconfig
Host bastion
    HostName bastion.example.com
    User bastion-user
    IdentityFile ~/.ssh/id_ed25519

Host app-private
    HostName 10.0.20.10
    User app-user
    ProxyJump bastion
    IdentityFile ~/.ssh/id_ed25519
```

Legacy `ProxyCommand`:

```sshconfig
Host app-private-legacy
    HostName 10.0.20.10
    User app-user
    ProxyCommand ssh bastion -W %h:%p
```

Agent forwarding warning:

- `ForwardAgent yes` tiện nhưng có rủi ro nếu bastion bị compromise.
- Ưu tiên key riêng cho bastion hoặc certificate-based SSH nếu có.
- Không đặt private key production lung tung trên bastion.

## 4. SCP Và Copy File Qua SSH

`scp` dùng SSH transport để copy file giữa local và remote host. Nó tiện cho thao tác nhỏ, nhưng với dữ liệu lớn, resume, bandwidth limit hoặc sync lặp lại, `rsync -e ssh` thường vận hành tốt hơn.

```bash
# Remote -> local
scp user@server:/var/log/app.log ./app.log

# Local -> remote
scp ./config.yml user@server:/tmp/config.yml

# Dùng port SSH khác
scp -P 2222 ./file.txt user@server:/tmp/

# Copy thư mục
scp -r ./site user@server:/var/www/
```

Lưu ý vận hành:

- `scp -P` dùng chữ hoa `P`, khác với `ssh -p`.
- Không copy private key hoặc file secret vào host trung gian nếu không có lý do rõ.
- Kiểm tra ownership/permission sau khi copy file cấu hình hoặc script deploy.
- Với production, ưu tiên checksum hoặc `rsync --dry-run` khi copy nhiều file quan trọng.

## 5. LLDP For Datacenter Mapping

LLDP giúp host biết port switch/kết nối vật lý lân cận.

Install:

```bash
sudo apt install lldpd
sudo dnf install lldpd
sudo systemctl enable --now lldpd
```

Kiểm tra:

```bash
lldpctl
lldpcli show neighbors
```

Use case:

- Xác nhận server cắm vào switch/port nào.
- Điều tra sai VLAN/cabling.
- Mapping network trong datacenter/private cloud.

## 6. Linux Bridge và veth

Linux bridge hoạt động như switch layer 2 trong kernel. Nó thường dùng cho VM, container hoặc lab network.

```bash
sudo ip link add br0 type bridge
sudo ip link set br0 up
sudo ip link set eth1 master br0
```

`veth` là cặp interface ảo nối hai network namespace hoặc nối container với bridge.

```bash
sudo ip link add veth-a type veth peer name veth-b
ip link show type veth
```

## 7. Network Namespace

Network namespace cô lập network stack: interface, route, ARP table, iptables/nft rule riêng.

Flow lab cơ bản:

1. Tạo namespace.
2. Tạo veth pair.
3. Đưa mỗi đầu veth vào một namespace.
4. Gán IP và bật link.
5. Test bằng `ping`, `ip route`, `tcpdump` nếu cần.

Tạo lab đơn giản:

```bash
sudo ip netns add ns1
sudo ip netns add ns2
sudo ip link add veth1 type veth peer name veth2
sudo ip link set veth1 netns ns1
sudo ip link set veth2 netns ns2
sudo ip netns exec ns1 ip addr add 10.10.10.1/24 dev veth1
sudo ip netns exec ns2 ip addr add 10.10.10.2/24 dev veth2
sudo ip netns exec ns1 ip link set veth1 up
sudo ip netns exec ns2 ip link set veth2 up
sudo ip netns exec ns1 ping -c 3 10.10.10.2
```

Xóa:

```bash
sudo ip netns del ns1
sudo ip netns del ns2
```

## 8. libvirt Virtual Networking

libvirt thường tạo NAT network mặc định `virbr0`.

```bash
virsh net-list --all
virsh net-info default
virsh net-dumpxml default
ip addr show virbr0
```

Network mode thường gặp:

- NAT: VM đi ra ngoài qua host NAT.
- Bridged: VM xuất hiện trực tiếp trên LAN/VLAN.
- Isolated: VM chỉ giao tiếp trong private network.

Chọn mode theo mục tiêu: NAT phù hợp lab/desktop, bridge phù hợp VM cần hiện diện như một host thật trong VLAN, isolated phù hợp sandbox không cần ra ngoài.

## 9. Troubleshooting

### SSH Failed

```bash
ssh -vvv user@server
sudo journalctl -u sshd -xe
sudo sshd -t
ls -ld ~/.ssh
ls -l ~/.ssh/authorized_keys
```

Checklist:

- DNS/IP đúng chưa.
- Port reachable chưa.
- Key đúng chưa.
- Permission `~/.ssh` thường là `700`, `authorized_keys` là `600`.
- Server có deny root/password/group không.

### JumpHost Failed

```bash
ssh -vvv -J bastion app-private
ssh bastion
ssh app-private
```

Tách lỗi thành hai chặng: client -> bastion và bastion -> target.

### Bridge/netns Failed

```bash
ip link
bridge link
bridge fdb show
ip netns list
sudo ip netns exec ns1 ip addr
sudo ip netns exec ns1 ip route
```

Kiểm tra interface up, IP/subnet, route, bridge membership và firewall.
