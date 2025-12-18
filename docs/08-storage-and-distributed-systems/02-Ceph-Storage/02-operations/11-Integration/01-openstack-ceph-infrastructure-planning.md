# CAPACITY PLANNING FOR OPENSTACK + CEPH 

## 1. Ceph 
### 1.1. Raw Capacity và Usable Capacity
- Raw Capacity là Tổng dung lượng có sẵn của tất cả các ổ đĩa mà chưa bị trừ đi bất kỳ phần nào cho hệ thống. 
- Usable Capacity là Dung lượng thực tế chứa dữ liệu sau khi trừ đi cơ chế bảo vệ (Replica/Erasure Coding).

- Trong hoạch định dung lượng khả dụng của Ceph ta có 
1. **Replicated Mode (Thường dùng cho Block Storage - RBD):**

$$
Usable = \frac{Raw}{Replica}
$$

2. **Erasure Coding (Thường dùng cho Object/Archive - RGW):**

$$Usable = Raw \times \frac{k}{k+m}$$

3. **Near-full Ratio (Ngưỡng an toàn thực tế):** Ceph sẽ chặn ghi (IO blocking) khi ổ đĩa đầy 95%, và bắt đầu cảnh báo/cân bằng lại (backfill) khó khăn khi đạt 85%. Do đó, "Safe Usable" nên được tính ở mức **75% - 80%** của Usable Capacity để đảm bảo khi một Node bị chết, dữ liệu từ Node đó có thể tràn sang các Node còn lại mà không làm đầy ổ cứng

$$Safe\ Usable \approx Usable \times 0.75$$

- **Ví dụ với chỉ số ratio = 0.7:**
    Replicated Mode :
    - 24 TB raw, replica 3
    - Usable ≈ 8 TB
    - Safe usable ≈ 5.6 TB
    Erasure Coding :
    - 120 TB raw, k (Data chunks) = 4, m (Parity chunks) = 2
    - Usable ≈ 80 TB
    - Safe usable ≈ 56 TB

Sau khi đã hiểu qua về dung lượng khả dụng khuyến nghị thì ta đến với cách tính dung lượng thực tế cần thiết để hệ thống Ceph vận hành ổn định 
### 1.2. Dự phòng các yếu tố và ước lượng - Overhead Planning
Để một cụm Ceph chạy tốt, bạn không bao giờ được dùng 100% dung lượng. Các thành phần sau đây chiếm dụng không gian trống:

- **Data Growth (30–50%):**Khoảng trống dự trữ cho sự tăng trưởng dữ liệu trong tương lai (thường tính cho 12-24 tháng).

- **Rebalance / Recovery (10–20%):** Không gian trống bắt buộc để Ceph có thể di chuyển và tái tạo dữ liệu khi có OSD hoặc Node bị hỏng.

- **Snapshot / Image Overhead (~10%):** Dung lượng dành cho các bản sao lưu tức thời (snapshots) hoặc dữ liệu phát sinh từ cơ chế copy-on-write của RBD/CephFS.

- Công thức tính toán thực tế giúp xác định tổng dung lượng Khả dụng (Usable) cần phải trang bị dựa trên lượng Dữ liệu thực tế (Expected data) bạn định lưu trữ:

$$
Required\ usable = Expected\ data × 1.5 – 1.8
$$ 

### 1.3. Dự đoán hiệu năng (Performance Planning)

Khi chạy OpenStack trên Ceph, mỗi loại máy ảo (VM) tiêu thụ một lượng tài nguyên vào/ra (I/O) khác nhau:

- Idle (5–10 IOPS): Các VM đang chạy nhưng không có người dùng hoặc tác vụ xử lý (hệ điều hành chỉ ghi log hoặc giữ kết nối).

- Web/App (50–100 IOPS): Các server web có lưu lượng trung bình, đọc ghi file cấu hình và log thường xuyên.

- DB (300–1000 IOPS): Các Database server (MySQL, PostgreSQL). Đây là workload nặng nhất vì yêu cầu độ trễ thấp và ghi liên tục.

- CI/CD (500+ IOPS): Các tác vụ build code, compile, test... tạo ra lượng I/O cực lớn trong thời gian ngắn.

$$\text{Total IOPS} = \sum (\text{Số lượng VM} \times \text{IOPS theo loại VM})$$

Ví dụ thực tế:
- Bạn có một cụm OpenStack dự kiến chạy:
    - 100 VM Web ($100 \times 70 = 7,000$ IOPS)
    - 10 VM Database ($10 \times 500 = 5,000$ IOPS)
    - 50 VM Idle ($50 \times 10 = 500$ IOPS)
    - Tổng cộng: $7,000 + 5,000 + 500 = \mathbf{12,500\ IOPS}$

> Lưu ý về Write Penalty : Ceph là hệ thống Strong Consistency. Khi Client ghi dữ liệu, Ceph phải ghi thành công vào Primary OSD và tất cả Replica OSDs rồi mới báo về Client.
- Con số 12,500 IOPS ở trên là mức mà các VM "nhìn thấy". Tuy nhiên, thực tế Ceph phải làm việc nhiều hơn thế vì cơ chế bảo vệ dữ liệu:

    $$\text{IOPS}_{Backend} =  \text{IOPS} _{Read}+ \text{Write IOPS} \times \text{Replica} $$

    - Replicated Mode (3x): Mỗi lệnh Write từ VM sẽ biến thành 3 lệnh Write dưới ổ đĩa.
    - EC Mode: Tệ hơn đối với IOPS ghi vì phải đọc mảnh cũ, tính toán Parity rồi mới ghi mảnh mới.


- Công thức Write IOPS theo Mirantis :

$\text{Write IOPS} = \frac{Device\ IOPS \times số Devices \times 0.65}{ cluster size}$ (0.65 là hệ số overhead, là đại diện cho phần dư ra của hiệu suất dự phòng cho các tác vụ không phải compute chính, có thể tùy chỉnh nhưng khuyến nghị không <0.6 và >0.75)

### 1.4. Quy trình tính toán Sizing
1. **Xác định nhu cầu Frontend IOPS** - IOPS mà ứng dụng/VM “nhìn thấy” và “yêu cầu”

$ \text{Total IOPS}_{Front} = Σ (VM_{Count}  \times IOPS_{Profile})$

2. **Xác định tỷ lệ Read/Write**

$$ 
\text{IOPS}_{Read} = \text{Total IOPS}_{Front} \times \text{Read\ Ratio}
\text{IOPS}_{Write} = \text{Total IOPS}_{Front} \times \text{Write\ Ratio}
$$
**Ví dụ :** 70% Read 30% Write

3. **Tính Backend IOPS cần xử lý** - IOPS thực tế mà các disk/OSD phải xử lý

$$ 
\text{IOPS}_{Back} = (\text{Total}_{Front} + \text{Read\ Percent}) + (\text{Total}_{Front} \times \text{Write Percent} \times Replica )
$$

4. **Tính số lượng OSD cần thiết**

$$
\text{OSD}_{\text{Count}} = \frac{\text{IOPS}_{Back}}{\text{IOPS}_{trên\ mỗi\ OSD\ thực\ tế}} \times 1.25
$$

> 1.25 = 25 % Headroom (recovery, burst) , con số khuyến nghị thường ở mức 30-50%

**Ví dụ :** 
```
Mixed workload:
- 100 VMs Web:     100 × 100 = 10,000 IOPS
- 20 VMs Database: 20 × 800  = 16,000 IOPS
- 50 VMs Idle:     50 × 10   = 500 IOPS
────────────────────────────────────────
Total Frontend:              26,500 IOPS

Tính IOPS Read/Write
Tỷ lệ Read/Write: 70% Read / 30% Write mix, Replica 3x:
Read:  26,500 × 0.7 = 18,550
Write: 26,500 × 0.3 = 7,950

Backend IOPS = 18,550 + 7,950 × 3
        = 42,400 IOPS

Tính số OSD cần (Performance-based) - ví dụ sử dụng SATA SSD (10K IOPS/OSD):
OSDs = 42,400 / 10,000 × 1.25 = 4.24 × 1.25
     = 5.3 → 6 OSDs minimum

Tính số OSD cần (Capacity-based)
Dung lượng cần: 100 TB (usable)
Replica 3 → Raw data = 100 × 3 = 300 TB
Hiệu suất lưu trữ: 25% (0.25) - do thin provisioning, snapshot, metadata
→ Raw capacity needed = 100 / 0.25 = 400 TB
Mỗi OSD: 4 TB
→ OSD cần cho capacity = 400 / 4 = 100 OSDs

```
- Khả năng cung cấp IOPS thực tế của OSD (Ceph OSD Performance): Đừng nhìn vào thông số Vendor (ví dụ SSD ghi là 80k IOPS). Khi chạy qua lớp phần mềm Ceph (Software Defined Storage), CPU và Network latency sẽ kéo tụt xuống. Con số quy ước an toàn (Conservative estimates):

| Loại Disk | IOPS thực tế (Mixed 70/30) | Ưu điểm | Nhược điểm thực tế | Use Case |
| :--- | :--- | :--- | :--- | :--- |
| HDD (7.2k RPM) | ~70 - 100 | Rẻ nhất, dung lượng lớn. | Độ trễ (Latency) cực cao khi có nhiều VM cùng truy xuất. | Archive, cold storage |
| HDD (10k RPM) | ~100 - 120 | Rẻ, dung lượng lớn. | Độ trễ (Latency) cao khi có nhiều VM cùng truy xuất. | Warm storage |
| SATA SSD | ~5k - 8k | Ổn định, phổ biến. | Bị giới hạn bởi băng thông cổng SATA (6Gbps) và controller. | General purpose |
| NVMe (Enterprise) | ~100k - 800k+ | Tốc độ cực cao, độ trễ thấp. | Cần hệ thống mạng 25Gbps/100Gbps mới phát huy hết sức mạnh. | Hot data, database |

**Workload IOPS Profile**

| Workload       | IOPS/VM    | Read/Write | Latency | Block Size | Notes             |
|----------------|------------|------------|---------|------------|-------------------|
| Idle           | 5-15       | 50/50      | <50ms   | 4-8KB      | Background OS     |
| Web Server     | 50-150     | 80/20      | <10ms   | 4-16KB     | Static content    |
| App Server     | 100-300    | 70/30      | <10ms   | 4-32KB     | Business logic    |
| Database OLTP  | 500-2,000  | 60/40      | <5ms    | 4-8KB      | Critical          |
| Database OLAP  | 200-800    | 90/10      | <20ms   | 64-512KB   | Analytics         |
| VDI (per user) | 10-30      | 70/30      | <15ms   | 4-16KB     | Desktop           |
| CI/CD Build    | 500-1,500  | 30/70      | <10ms   | 4-64KB     | Burst heavy       |

### 1.5. Hardware Sizing Standards 
#### 1.5.1. RAM
- Trong kiến trúc BlueStore hiện đại, RAM đóng vai trò cực kỳ quan trọng làm bộ đệm (cache) để tăng tốc độ đọc/ghi.

- Công thức ước tính:

$$RAM_{Cần thiết} \approx RAM_{Hệ thống} + (Số\ lượng\ {OSD} \times RAM\ Mỗi\ {OSD}) + RAM_{Dịch\ vụ\ khác}$$

- Trong đó :
    - RAM hệ thống : Thường được khuyến nghị 2-4 GB , chủ yếu dành cho Kernel, log, và các tiến trình nền của Linux.
    - RAM cho các OSD : 
        - OSD sử dụng HDD : Tối thiểu 4 – 8 GB / OSD để duy trì BlueStore cache và Metadata. ( Tính cả overhead của OS và Recovery )
        - OSD sử dụng SSD/NVMe : Tối thiểu (SSD/NVMe)	6 – 8 GB / OSD để đáp ứng tốc độ cao mà không bị nghẽn ( bottleneck)
    - RAM cho MON/MGR: Tối thiểu 2 – 4 GB / Service , RAM bổ sung nếu cài chung MON/MGR trên cùng node với OSD.

| Component        | Minimum | Recommended | Notes                  |
|------------------|---------|-------------|------------------------|
| OS Baseline      | 4GB     | 8GB         | Per node              |
| OSD (All types)  | 5GB     | 8GB         | Per OSD (BlueStore)   |
| MON service      | 2GB     | 4GB         | If co-located         |
| MGR service      | 2GB     | 4GB         | If co-located         |
| Recovery buffer  | -       | 25% extra   | For OSD failures      |

**Công thức :**

$ \text{RAM}_{Node} = \text{4GB (OS)} + \text{OSD}_{Count} \times 8GB + \text{4GB (MON/MGR)} + \text{Buffer} $

$ \text{Buffer} = \text{OSD}_{Count} \times 2GB $ (recovery spike protection)

- Một ví dụ về ước lượng RAM :
```
Node: 12 OSDs + MON + MGR

RAM = 4 + (12×5) + 4 + (12×2)
    = 4 + 60 + 4 + 24
    = 92GB
    
→ Provision: 128GB RAM
```

- Ví dụ về việc thiếu RAM 
    - Trong các kịch bản Recovery (khi có ổ đĩa hỏng), các tiến trình OSD sẽ tiêu thụ RAM đột biến (có thể lên tới 6-8 GB/OSD) để thực hiện tính toán lại bản đồ dữ liệu (Placement Groups). Nếu thiếu RAM, OSD sẽ bị OS "giết" (OOM Killer), gây ra lỗi dây chuyền.

#### 1.6.2. CPU
- Ceph sử dụng CPU để tính toán checksum (đảm bảo an toàn dữ liệu), nén dữ liệu (compression) và quản lý luồng dữ liệu.
- Công thức ước tính:

$$CPU_{Mỗi\ Node} \approx {CPU Cần thiết}_{MON/MGR} + (Số\ lượng_{OSD} \times Số Core_{mỗi\ OSD})$$

- Trong đó :
    - MON / MGR : 1 -2 Core 
    - OSD (HDD) : 1 Core / OSD - Workload thấp 
    - OSD (SSD) : 2+ Cores / OSD - I/O cao hơn 
    - OSD ( NVMe) : Tỷ lệ khuyến nghị CPU:NVMe là 6:1 với số core vật lý 


- Ví dụ :
    - Bạn có 1 Server vật lý lắp 12 ổ đĩa SSD :
        - Tổng RAM : 4GB(OS) + (12 x 4GB) 
        - Tổng CPU : 2 Cores ( MON/MGR) + ( 12 x 2 Cores)
        - Network : IOPS cho 12 SSD : 6k x 12 
        => Kết luận 54-64GB + 26-32 Cores + 2 x 25 Gbps( Bonding)
### 1.6.3. Network Sizing 

$\text{Cluster Network Banwidth} = \text{Frontend Banwidth} \times Relica \times 1.3 (overhead) $

> 10 GbE per 12 OSDs 

## 2. Openstack 
Trong OpenStack, việc quy hoạch không chỉ là cộng dồn tài nguyên mà là nghệ thuật cân bằng giữa **mật độ máy ảo** và **hiệu năng ổn định**.

### 2.1. vCPU Overcommit Rationale
- vCPU không phải là Core vật lý. Đây là khả năng chia sẻ thời gian thực thi của CPU (Time-slicing).

    - **General Purpose (2:1 đến 4:1):** Phù hợp cho đa số ứng dụng Web, Microservices. Giúp tận dụng tối đa chu kỳ nghỉ của CPU.

    - **High Performance / DB (1:1):** Bắt buộc dùng CPU Pinning cho Database. Việc tranh chấp CPU (CPU Steal time) sẽ làm tăng Latency của DB cực kỳ nghiêm trọng.

    - **Kinh nghiệm thực tế:** Đừng bao giờ tính Overcommit dựa trên số "Thread" ảo nếu CPU không hỗ trợ hoặc tải quá nặng. Luôn giữ mức sử dụng CPU tổng của Host dưới 80% để tránh hiện tượng "noisy neighbor".

### 2.2. RAM Allocation & Overcommit
RAM là tài nguyên "cứng", không thể nén hay chia sẻ linh hoạt như CPU.

-**Production (1:1):** Bắt buộc. Nếu Host hết RAM, Linux sẽ kích hoạt OOM Killer và "giết" ngẫu nhiên các tiến trình `qemu-kvm` (máy ảo).

- **Reserved Memory:** Phải luôn trừ ra khoảng 8-16GB RAM cho mỗi Compute Node để chạy OS, Hypervisor (KVM), OpenStack Agents và đặc biệt là Ceph OSD nếu chạy chung (Hyper-converged).

$$\text{Reserved} = 4GB_{OS} + 4GB_{OVS/Agent} + (Ceph\ RAM\ nếu\ là\ HCI)$$

### 2.3. Disk Local & Boot Strategy
- **Local Disk (SSD/NVMe):** Dùng để chứa hệ điều hành Host và thư mục tạm `/var/lib/nova/instances` (cho `swap/ephemeral disk`).

- **Cấu hình RAID:** Luôn dùng RAID 1 cho ổ Boot của Host để đảm bảo 1 ổ chết Host vẫn không sập.

### 2.4. Network Capacity Planning
- Mạng là "mạch máu" của toàn hệ thống Cloud. Nghẽn mạng sẽ tạo ra cảm giác "lag" máy ảo dù CPU/RAM vẫn trống.

#### 2.4.1. Phân rã Traffic vật lý
- Để đạt chuẩn Production, cần tách tối thiểu 3 loại traffic sau lên các đường truyền vật lý khác nhau (hoặc VLAN với Priority cao):
    - **Management :** Vai trò API, điều khiển, RabbitMQ, DB nội bộ (1 Gbps)
    - **Tenant/Public :** Lưu lượng máy ảo đi ra ngoài và giữa các VM ( 10 Gbps)
    - **Storage (Front) :** VM truy cập dữ liệu vào Ceph (Cinder/Glance) ( 10 Gbps hoặc 25 Gbps)
    - **Storage (Back) :** Ceph tự replication và rebalance ( Bắt buộc ≥ 10 Gbps và tách biệt với Front-end)

> Khi một Node Ceph bị hỏng, traffic phục hồi (Back-end) có thể quét sạch băng thông 10Gbps trong vài giờ. Nếu không tách riêng, toàn bộ máy ảo sẽ bị treo I/O trong suốt thời gian phục hồi.

### 2.5. High Availability (HA) & Scaling Strategy

#### 2.5.1 Control Plane HA
- **3 Controller Nodes:** Để đạt Quorum (số đông) cho MariaDB Galera và RabbitMQ.

- **Load Balancer (VIP):** Sử dụng Keepalived + HAProxy để tạo IP ảo cho các API OpenStack.

#### 2.Compute Scaling (Scale-out)
- **Nguyên tắc N+1:** Luôn có ít nhất 1 Server Compute dự phòng hoàn toàn.

- **Ví dụ:** Nếu bạn cần chạy 100 VM trên 4 Host, hãy tính toán sao cho nếu 1 Host chết đột ngột, 3 Host còn lại vẫn đủ RAM để chứa toàn bộ 100 VM đó (Evacuation).

## 3. Production Considaration 
- **Oversubscription Ratio (Tỷ lệ chia sẻ băng thông):**
    - Trong Datacenter, ta thường quy hoạch tỷ lệ **10:1** hoặc **20:1**.
    - Ví dụ: Uplink Server là 10 Gbps. Nếu chia sẻ tỷ lệ 10:1 (khá thoải mái), tổng băng thông cấp phát cho các VM là 100 Gbps. Nếu mỗi VM cần đảm bảo 100 Mbps, ta chạy được $\approx$ 1000 VM (lý thuyết).
    - *Thực tế:* Giới hạn số VM thường đến từ RAM và CPU trước khi đến từ Network (trừ khi làm Streaming/CDN).

- **Quy tắc "Số Node tối thiểu"**
    - **3 Nodes:** Chỉ dùng cho Lab/POC. Nếu 1 Node chết, Cluster rơi vào trạng thái nguy hiểm (Degraded), không đủ chỗ để tự healing về Replica 3.

    - **5 Nodes:** Tối thiểu cho Production nhỏ. Cho phép 1 Node chết mà vẫn còn 4 Node để Rebalance dữ liệu an toàn.

    - **Node Density:** Không nên nhồi quá nhiều OSD vào 1 Node (ví dụ 30-40 OSD). Nếu Node đó chết, lượng traffic recovery khổng lồ sẽ đánh sập mạng. Con số vàng: **12 - 16 OSD / Node** (với HDD 3.5") hoặc **10 - 12 OSD / Node** (với SSD/NVMe).

- **Hyper-Converged (HCI)** vs **Decoupled**
    - **HCI (Compute chạy chung Storage):** Tiết kiệm phần cứng nhưng rủi ro cao. CPU/RAM bị tranh chấp giữa máy ảo và Ceph OSD. Cần cấu hình Cgroups/Systemd slice để giới hạn tài nguyên cho Ceph, tránh việc Ceph ăn hết RAM của VM và ngược lại.

    - **Decoupled (Tách riêng):** Khuyến nghị cho Production lớn. Dễ dàng scale Compute và Storage độc lập.

### 3.1. Case Study Sizing (Web/App Cluster)
- **Yêu cầu:** 100 VM (4 vCPU, 8GB RAM, 50GB Disk). Workload Web (Mixed IO).
    - Giả định:
        - IOPS/VM: 100 (Peak). Tổng Frontend: 10,000 IOPS.
        - Read/Write: 70/30.
        - Replica: 3.
        
- **Tính toán Storage:**
    - **Capacity:** 100 VM x 50GB = 5TB Usable. $\rightarrow$ Raw = 15TB. (Quá nhỏ, sizing theo Performance sẽ quyết định).
    - **Performance:**
        - Backend IOPS = $(10,000 \times 0.7) + (10,000 \times 0.3 \times 3) = 16,000$ IOPS.
        - Dùng SSD Enterprise (3,000 IOPS/OSD safe margin cho mixed workload).
        - Số OSD = $16,000 / 3,000 \times 1.25 \approx 6.6 \rightarrow 7$ OSD.
        - Reality Check: 7 OSD là quá ít để đảm bảo an toàn dữ liệu (Min 3 Node). Ta cần số lượng OSD sao cho chia đều ra ít nhất 3 Node.
        - Đề xuất: 3 Nodes, mỗi Node 4 SSD (Tổng 12 OSD). Vừa đảm bảo Performance (dư thừa), vừa đảm bảo Failure Domain.
- **Tính toán Compute:**
    - Total vCPU: 400. Với Overcommit 4:1 $\rightarrow$ Cần 100 Physical Cores.
    - Total RAM: 800GB.
    - Nếu dùng 3 Node $\rightarrow$ Mỗi Node cần: ~33 Cores và ~270GB RAM (cho VM) + 32GB (cho OS/Ceph).
    - **Cấu hình Server (3 servers):** Dual Socket CPU (Total 40+ Cores/Server), 384GB RAM, 4x SSD 1.92TB.