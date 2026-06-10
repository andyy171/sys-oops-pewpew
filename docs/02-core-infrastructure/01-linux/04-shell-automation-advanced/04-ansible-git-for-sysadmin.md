# Git và Ansible cho Sysadmin

## 1. Git Workflow Cho Note và Cấu Hình

Git giúp theo dõi thay đổi tài liệu, config, script và IaC.

```bash
git status
git diff
git add <file>
git commit -m "docs: update linux storage note"
git log --oneline --graph --decorate -10
```

Workflow đơn giản:

1. Kiểm tra `git status`.
2. Sửa theo một chủ đề nhỏ.
3. Review `git diff`.
4. Commit với message rõ.
5. Push hoặc tạo PR nếu repo dùng review.

Branch workflow:

```bash
git switch -c cleanup/linux-notes
git switch main
git merge cleanup/linux-notes
```

Stage từng phần khi agent sửa nhiều file:

```bash
git add -p
```

## 2. Git Rollback An Toàn

Xem thay đổi:

```bash
git diff
git diff -- <file>
```

Khôi phục file về trạng thái HEAD:

```bash
git restore <file>
```

Khôi phục file đã staged:

```bash
git restore --staged <file>
```

Xem file ở commit cũ:

```bash
git show <commit>:path/to/file
```

Production notes:

- Trước khi cho agent sửa hàng loạt, kiểm tra `git status`.
- Không dùng `git reset --hard` nếu chưa chắc muốn bỏ toàn bộ thay đổi local.
- Commit nhỏ giúp rollback dễ hơn.

## 3. `.gitignore` Cho Note/Sysadmin Repo

Ví dụ:

```gitignore
.env
*.key
*.pem
*.p12
*.log
tmp/
.DS_Store
Thumbs.db
```

Không commit secret, token, private key, password hoặc customer data.

## 4. Ansible Inventory

Inventory INI:

```ini
[linux]
node-1 ansible_host=10.0.0.10 ansible_user=ubuntu
node-2 ansible_host=10.0.0.11 ansible_user=ubuntu

[linux:vars]
ansible_python_interpreter=/usr/bin/python3
```

Inventory YAML:

```yaml
all:
  children:
    linux:
      hosts:
        node-1:
          ansible_host: 10.0.0.10
          ansible_user: ubuntu
```

## 5. Ad-hoc Commands

```bash
ansible linux -i inventory.ini -m ping
ansible linux -i inventory.ini -m command -a "uptime"
ansible linux -i inventory.ini -m shell -a "df -h | grep /data"
ansible linux -i inventory.ini -m copy -a "src=file.conf dest=/tmp/file.conf"
ansible linux -i inventory.ini -m service -a "name=nginx state=restarted" --become
ansible linux -i inventory.ini -m package -a "name=curl state=present" --become
```

`command` an toàn hơn `shell` nếu không cần pipe/redirection/glob.

## 6. Playbook Basic

```yaml
- name: Basic Linux maintenance
  hosts: linux
  become: true
  tasks:
    - name: Ensure curl is installed
      package:
        name: curl
        state: present

    - name: Ensure nginx is running
      service:
        name: nginx
        state: started
        enabled: true
```

Chạy:

```bash
ansible-playbook -i inventory.ini site.yml
```

## 7. Variables, Handlers, Templates

Variables:

```yaml
vars:
  app_port: 8080
```

Template task:

```yaml
- name: Render app config
  template:
    src: app.conf.j2
    dest: /etc/app/app.conf
  notify: Restart app
```

Handler:

```yaml
handlers:
  - name: Restart app
    service:
      name: app
      state: restarted
```

Idempotency: playbook chạy nhiều lần vẫn đưa hệ thống về desired state, không tạo thay đổi thừa.

## 8. Check Mode, Diff Mode và Limit Host

Dry-run:

```bash
ansible-playbook -i inventory.ini site.yml --check
```

Diff:

```bash
ansible-playbook -i inventory.ini site.yml --diff
```

Giới hạn host:

```bash
ansible-playbook -i inventory.ini site.yml --limit node-1
ansible-playbook -i inventory.ini site.yml --check --diff --limit node-1
```

## 9. Production Safety Notes

- Luôn chạy `--check --diff` nếu module hỗ trợ.
- Dùng `--limit` khi rollout từng phần.
- Dùng serial/canary cho thay đổi nhiều host.
- Tránh `shell` khi có module chuẩn.
- Chỉ dùng `shell` khi cần pipe, redirect, glob hoặc shell feature.
- Không lưu secret plain text; dùng Ansible Vault hoặc secret manager.
- Log lại inventory, playbook version và command đã chạy.

Ví dụ rollout tuần tự:

```yaml
- hosts: linux
  become: true
  serial: 1
  tasks:
    - name: Restart nginx safely
      service:
        name: nginx
        state: restarted
```

## 10. Python Virtual Environment Cho Tool Nhỏ

Không cài Python package tùy tiện vào system Python trên server dùng chung. Với tool nội bộ, lab nhỏ hoặc script hỗ trợ vận hành, ưu tiên virtual environment để cô lập dependency và dễ xóa bỏ.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install <package>
pip freeze
deactivate
```

Trong production, lưu lại dependency bằng `requirements.txt` hoặc lock file phù hợp, kiểm tra nguồn package và tránh chạy tool chưa review bằng quyền cao.
