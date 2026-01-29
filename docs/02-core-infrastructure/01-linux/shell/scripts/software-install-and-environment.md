# "Các lệnh tham khảo cho Software Installation and Environment  "
---

# Cài đặt nhanh các package cần thiết
```bash
#!/bin/bash
# Automated Software Installation Script
PACKAGES=("curl" "wget" "vim" "git" "htop" "unzip")

echo "Updating package lists..."
sudo apt-get update

for package in "${PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "^ii  $package"; then
        echo "Installing $package..."
        sudo apt-get install -y "$package"
    else
        echo "$package is already installed"
    fi
done

echo "Software installation completed"
```

# Thiết lập môi trường phát triển cơ bản
```bash
#!/bin/bash
# Basic Environment Setup Script

echo "Setting up basic environment..."

# Cài đặt các package cơ bản
sudo apt-get update
sudo apt-get install -y git vim curl

# Thiết lập git config
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Tạo thư mục projects
mkdir -p ~/projects ~/downloads

# Thêm aliases cơ bản
echo -e '\nalias ll="ls -alh"\nalias update="sudo apt-get update && sudo apt-get upgrade"' >> ~/.bashrc

echo "Basic environment setup completed"
```

# Cài đặt nhanh stack phát triển
```bash
#!/bin/bash
# Quick Dev Stack Installer

echo "Installing development stack..."

# Cài đặt Node.js (nếu cần)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Cài đặt Python và pip
sudo apt-get install -y python3 python3-pip

# Cài đặt Docker (tùy chọn)
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER

echo "Dev stack installation completed"
echo "Please logout and login again for Docker group changes to take effect"
```

## Thiết lập nhanh project mới
```bash
#!/bin/bash
# Simple Project Setup Script

if [ -z "$1" ]; then
    echo "Usage: $0 <project-name>"
    exit 1
fi

PROJECT_NAME=$1
PROJECT_DIR="$HOME/projects/$PROJECT_NAME"

echo "Creating project: $PROJECT_NAME"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Khởi tạo git repository
git init
echo "# $PROJECT_NAME" > README.md

# Tạo cấu trúc thư mục cơ bản
mkdir src docs tests

echo "Project $PROJECT_NAME created at $PROJECT_DIR"
```
Cách sử dụng:

Lưu thành file `new_project.sh`

Chạy: `chmod +x new_project.sh && ./new_project.sh my-project`

