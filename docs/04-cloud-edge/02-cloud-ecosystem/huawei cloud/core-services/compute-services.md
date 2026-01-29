# Overview
- Included Services : 
Elastic Cloud Service (ECS) — virtual machine instances.

Bare Metal Server (BMS) — physical servers as a service.

Image Management Service (IMS) — image creation/management for provisioning.

Dedicated Host (DeH) concept is also relevant (physical host dedicated to a tenant).


## Elastic Cloud Service (ECS)
### ECS Feature 

- After purchasing an ECS, you can:
1. Use the ECS like a regular server (install OS, applications, configure services).
2. Enjoy full permissions on the ECS — you manage the OS and upper-layer components.
3. Adjust compute resources as required (change instance type / scale).
4. Only pay for resources you use (various billing modes).
5. Treat an ECS as a disposable resource (create/terminate as needed).

### ECS Purchase Process

Typical configuration workflow (high-level):

1. Basic settings
- Billing mode (on-demand, subscription/reserved, spot, etc.)
- Region and Availability Zone
- Instance type (family, generation, size, memory:vCPU ratio)
- Image (public / private / shared / gallery)
- Boot/EVS disk selection (type, size, IOPS)

2. Network settings
- VPC and subnet selection
- Security group rules
- EIP and bandwidth/traffic plan (if public access is needed)

3. Advanced settings
- ECS name, backup policy, server group placement, and additional options

4. Confirmation and payment/creation

### Billing Mode 
- Pay-per-use (On-demand)
On-demand usage; pay for time/resources used; good for elastic or temporary workloads.

- Yearly/Monthly (Subscription)
Fixed-term subscriptions (monthly/yearly); stable discounts for longer commitments.

- Reserved instances
Long-term commitment with stable discounts; suitable for predictable long-term workloads.

- Spot pricing
Demand-based dynamic pricing; low cost but resources can be reclaimed by provider; suitable for fault-tolerant or batch workloads.

### Select Region 

Key factors to consider:
1. Compliance is a must — local data residency and regulations may force region selection.
2. User experience comes first — pick regions close to users to reduce latency.
3. Functions are region-specific — some services/features might be available only in certain regions.
4. Cost differences — pricing and discounts may vary by region.

### Select Instance Types
**How instance names encode information:**

Example: `c6.8xlarge.4`

- Part 1 (letter prefix): instance family (e.g., c = compute/general computing-plus; m = memory-optimized; s = general-purpose — provider naming may vary).
- Part 2 (generation digit): instance generation (e.g., 1 = gen1, 2 = gen2).
- Part 3 (size token, e.g., 8xlarge): instance size (medium, large, xlarge, etc.).
- Part 4 (trailing digit after dot): memory-to-vCPU ratio (e.g., .4 -> memory:vCPU = 4).

**Selection guidance**
- Select an instance family and size based on service components (web/app/db).
- If you pick the wrong type you can change the instance type (often requires stop/change/start) or create a new ECS.
- Instance type optimization is ongoing — base changes on monitoring data.

### Configue Network
When configuring ECS networking, consider:
1. Isolation and connectivity requirements — determine whether services need full isolation or controlled connectivity.
2. Logical layering — design tiers (public load balancer, app tier, DB tier) using subnets.
3. Public exposure decision — choose whether to assign EIP/public IP or place behind NAT/load balancer.
4. Network security — enforce least-privilege via security groups/firewall rules and restrict SSH/RDP access.


### Advanced Configure
- Key pair recommended for login — use SSH key pairs rather than passwords for secure access.
- Select a backup policy — schedule snapshots/backups for recovery.
- Inject user-data — provide cloud-init or shell scripts to initialize instances automatically at first boot.


## Lifecycle management
Typical ECS lifecycle states and transitions:
- Purchase → Creating → Starting → Running
- From Running: can Restart (→ Restarting → Running)
- Stop → Stopping → Stopped
- From Stopped: Start → Starting → Running

Delete → Deleting → Deleted
## DeH Overview
Dedicated Host (DeH) = a physical host allocated exclusively to a tenant. It provides physical isolation, often used for compliance, licensing (per-socket), and workloads requiring dedicated hardware. 

### DeH Feature 
DeH may allow better control of CPU allocation and licensing; check provider docs for DeH-specific features and limitations.
## BMS Overview 
Bare Metal Server = a physical server provisioned to the customer without hypervisor-level virtualization overhead. Suitable for I/O-intensive, latency-sensitive workloads and cases where direct hardware control is needed.
### BMS Feature
BMS typically offers near-native performance but less elasticity and possibly longer provisioning time compared to ECS.
## Using an Image to initialize an ECS - IMS
### Image types
- Public images — OS images provided by the provider or community, available to all tenants.
- Gallery images (KooGallery — slide term) — curated gallery/catalog of images (verify exact product name). [Chưa xác minh]
- Private images — custom images created by the user from a configured ECS (for rapid provisioning).
- Shared images — private images shared between accounts/projects.

## Image usage workflow

1. Choose an appropriate image (OS + preinstalled software if needed).
2. Choose a compatible instance type and boot disk.
3. Optionally provide user-data to complete runtime configuration.
4. Launch and verify the instance.
5. To capture a golden image: configure a running ECS → stop services/clean secrets → create image/snapshot via IMS.


**Snapshot vs Image**
- Snapshot: point-in-time copy of a volume (useful for backups or restoring a volume).
- Image: full instance template (OS + configuration) for creating new instances.
