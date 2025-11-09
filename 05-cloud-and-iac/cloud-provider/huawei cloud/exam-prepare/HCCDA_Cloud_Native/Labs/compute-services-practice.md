# Compute Services Practice Guide

## 📋 Contents
- [Objectives and Requirements](#objectives-and-requirements)
- [ECS Lifecycle Management](#ecs-lifecycle-management)
- [Creating a Windows System Disk Image from an ECS](#creating-a-windows-system-disk-image-from-an-ecs)
- [Creating a Linux System Disk Image from an ECS](#creating-a-linux-system-disk-image-from-an-ecs)

---

## Objectives and Requirements
1. Create and log in to an ECS
2. Modify ECS specifications
3. Create a Windows system disk image from an ECS
4. Create a Linux system disk image from an ECS
5. Modify and share an image

---

Pre-requisites : Log in to Huawei Cloud Console (AP-Singapore region)

## ECS Lifecycle Management
### Step 1: Create VPC 

1. Navigate **Virtual Private Cloud** from the service list.
2. Click Create VPC
3. Configure VPC parameters:
- Region: AP-Singapore
- Name: vpc-WP (replace with your assigned account name)
- IPv4 CIDR Block: 192.168.0.0/16
- Default Subnet:
+ AZ: AZ1
+ Name: subnet-WP (replace with your assigned account name)
+ IPv4 CIDR Block: 192.168.0.0/24

4. View the created VPC on the Virtual Private Cloud page

### Step 2: Create Windows ECS

1. Navigate to Compute > Elastic Cloud Server
2. Click Buy ECS
3. Configure basic settings:
- Billing Mode: Pay-per-use
- Region: AP-Singapore
- AZ: Random
- CPU Architecture: x86
- Specifications: General computing, s6.large.2 (2 vCPUs | 4 GB)
- Image: Public Image, Windows Server 2012 R2 Standard 64bit English
- Host Security: Enable (basic edition)
- System Disk: High I/O, 40 GB
4. Configure network:
- Network: Select the created VPC
- EIP: Not required
5. Configure advanced settings:
- ECS Name: ecs-windows
- Login Mode: Password
- Password: Huawei@1234 (or your chosen password)
6. Confirm configurations and create ECS

### Step 3: Create Linux ECS

1. Repeat Windows ECS creation process with these differences:
- ECS Name: ecs-linux
- Image: Public image, CentOS 7.6 64-bit
- EIP: Auto assign

### Step 4: Log in to ECS Instances

1. Windows ECS Login:
- On Elastic Cloud Server page, click Remote Login for ecs-windows
- Click Log In and then Send CtrlAltDel
- Enter password via Input Commands

2. Linux ECS Login:
- On Elastic Cloud Server page, click Remote Login for ecs-linux
- Login with:
+ Username: root
+ Password: Huawei@123 (or your chosen password)

### Step 5: Modify ECS Specifications

1. Stop the Windows ECS (select Forcibly stop if needed)
2. Click More > Modify Specifications
3. Change memory from 4 GB to 8 GB
4. Confirm and submit changes
5. Start the ECS to apply new specifications

---

**Prerequisite:** Use the ecs-windows ECS created previously

## Creating a Windows System Disk Image from an ECS
**Configuring a Windows ECS**
### Step 1: Remote Login to ECS

Log in to the Windows ECS using remote desktop connection

### Step 2: Configure DHCP for Network Interface

1. Open Control Panel > Network and Sharing Center
2. Click on the network connection (e.g., Ethernet 2)
3. Click Properties > Internet Protocol Version 4 (TCP/IPv4)
4. Ensure both options are selected:
- ✅ Obtain an IP address automatically
- ✅ Obtain DNS server address automatically
5. Click OK to save changes

### Step 3: Enable Remote Desktop

1. Right-click This PC and select Properties
2. Click Remote settings in left navigation pane
3. Select Allow remote connections to this computer
4. Click OK to confirm

### Step 4: Configure Windows Firewall

1. Open Control Panel > Windows Firewall
2. Select Allow an app or feature through Windows Firewall
3. Enable Remote Desktop for both private and public networks
4. Click OK to save settings

### Step 5: Verify Cloudbase-Init Installation

1. Open Control Panel > Programs and Features
2. Check if Cloudbase-Init is installed
- Note: Public images typically have Cloudbase-Init pre-installed
- If not installed, custom information injection won't work for new ECSs

**Creating a Windows Private Image**
### Step 1: Access Image Management Service

Navigate to Compute > Image Management Service

### Step 2: Initiate Image Creation

Click Create Image button

### Step 3: Configure Image Parameters

- Region: AP-Singapore
- Type: System disk image
- Source: Select your Windows ECS (ecs-windows)
- Name: image-windows2012 (or your preferred name)
- Retain default settings for other parameters
- Click Next

### Step 4: Confirm and Submit

- Review all settings
- Select checkbox: I have read and agree to the Image Disclaimer
- Click Submit

### Step 5: Monitor Image Creation

- Switch to Private Images tab
- Image status will show creation progress
- Completion time: 10-20 minutes (depending on image size)
- Status changes to Normal when complete

**Modifying Image Information**
### Step 1: Access Image Modification

- Locate your created image in Private Images list
- Click Modify in the Operation column
### Step 2: Update Image Details

- You can modify:
+ Image name
+ Description
+ Minimum memory requirements
+ Other configuration details

- Save changes when complete
**Replicating an Image Within a Region**
### Step 1: Initiate Replication

- In Private Images list, locate your image
- Click More > Replicate in Operation column
### Step 2: Configure Replication

- Enter new name for the replicated image
- Do not select KMS encryption (for this exercise)
- Click OK to confirm

**Creating ECS from Private Image**
### Step 1: Apply for Server

- In Private Images list, locate your image
- Click Apply for Server in Operation column
### Step 2: Verify Image Selection

- On ECS purchase page, ensure your private image is selected
- Complete ECS creation process as before
### Step 3: Verify New ECS

- Return to ECS list to view the new ECS created from your private image
- The new ECS will have all the configurations from your original Windows ECS

---

Prerequisite: Use the ecs-linux ECS created previously

## Creating a Linux System Disk Image from an ECS
**Configuring a Linux ECS**
### Step 1: Remote Login to ECS
Log in to the Linux ECS using SSH or VNC remote login

### Step 2: Configure DHCP for Network Interface
1. Edit the network configuration file:

```bash
vi /etc/sysconfig/network-scripts/ifcfg-eth0
```
2. Ensure the following parameter is present:

```text
PERSISTENT_DHCLIENT="y"
```
3. Save and exit the editor

### Step 3: Verify One-Click Password Reset Plugin
Check if CloudResetPwdAgent is installed:

```bash
ls -lh /Cloud*
```
- If files are listed, the plugin is installed (default for public images)

### Step 4: Verify Cloud-Init Installation

- Check if Cloud-Init is installed:

```bash
rpm -qa | grep cloud-init
```
- If no output is displayed, install Cloud-Init:

```bash
yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum install cloud-init
```
### Step 5: Check Network Rule Files
- Verify no network rule files exist:

```bash
ls -l /etc/udev/rules.d
```
- If network rule files exist (unlikely for public images), delete them following Huawei documentation

**Creating a Linux Private Image**
### Step 1: Access Image Management Service
Navigate to Compute > Image Management Service

### Step 2: Initiate Image Creation
Click Create Image button

### Step 3: Configure Image Parameters
- Type: System disk image
- Source: Select your Linux ECS (ecs-linux)
- Name: image-centos7.6 (or your preferred name)
- Click Next

### Step 4: Confirm and Submit
- Review all settings
- Select checkbox: I have read and agree to the Image Disclaimer
- Click Submit

### Step 5: Monitor Image Creation
- Switch to Private Images tab
- Image status will show creation progress
- Completion time: 10-20 minutes (depending on image size)
- Status changes to Normal when complete

**Sharing an Image**
### Step 1: Obtain Your Project ID
1. Log in to your main Huawei Cloud account (not Sandbox)
2. Click username in top right > My Credentials
3. Note the Project ID for AP-Singapore region

### Step 2: Share Image from Sandbox Account
1. In Sandbox console, go to Private Images tab
2. Select your private image
3. Click More > Share in Operation column
4. Enter your Project ID and click Add
5. Click OK to confirm sharing

### Step 3: Accept Shared Image
1. Log in to your main Huawei Cloud account
2. Go to IMS console for AP-Singapore region
3. Click Shared Images tab
4. Click Accept to receive the shared image

**Managing Shared Image Tenants**
### Step 1: Add Additional Tenants
1. In Sandbox console, go to Private Images
2. Click the name of your shared image
3. Go to Shared with Tenants tab
4. Click Add Tenant
5. Enter additional Project IDs to share with more users

### Step 2: Modify Sharing Settings
- To reshare with yourself, first remove your account from the list
- Then add your Project ID again using the Add Tenant function

#### Important Notes:
- Linux images require different configuration than Windows images
- Cloud-Init is essential for custom information injection in Linux
- Network configuration cleanup prevents NIC naming issues
- Image sharing allows collaboration across different accounts
- Always verify image status is "Normal" before use

#### Completion Checklist:
- Linux ECS properly configured with DHCP
- Cloud-Init verified/installed
- Password reset plugin confirmed
- Network rules checked/cleaned
- Private image created successfully
- Image shared with main account
- Shared image accepted in main account