# Các lệnh Linux thông dụng 

```bash
# Setup thư mục git lần đầu 
- Khởi tạo thư mục git 
git init 

- Add remote 

git remote add origin https://github.com/username/reponame.git

git remote -v // kiểm tra các remote đã add 
- Cấu hình user:
git config --global user.name "John Doe"
git config --global user.email johndoe@example.com

- Cấu hình alias ( optional):
git config --global alias.co checkout
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.l 'log --all --decorate --oneline --graph'
git config --global alias.unstage 'reset HEAD --'
File config: $HOME/.gitconfig

# Quy trình thực hiện một commit cơ bản 
- Tạo 1 commit 
git add . → stage toàn bộ thay đổi
git add file.txt → stage file cụ thể
git commit -m "message" → commit thay đổi đã stage
git commit -am "message" → stage và commit (không bao gồm file mới)

## Các thao tác cơ bản 
- Unstag - Loại bỏ các tệp khỏi vùng trung gian ( staging) của Git 
+ Đưa những thay đổi đã thêm vào commit đó quay trở lại thư mục làm việc (work dir) hoặc trạng thái trước đó 

git reset → bỏ stage toàn bộ
git reset HEAD -- file.txt → bỏ stage file cụ thể

- Sửa đổi commit cuối cùng gần nhất 

git commit --amend -m "new message" → sửa message commit cuối
git commit --amend --no-edit → thêm thay đổi nhưng giữ nguyên message

⚠️ Chỉ dùng khi commit chưa push lên remote.

## Thao tác với nhánh ( Branch )
-  Tạo local branch:
git branch new-feature
git checkout new-feature
git checkout -b new-feature

- Tạo remote branch:
git checkout -b new-feature
git push -u origin new-feature

- Liệt kê branch:
git branch → local
git branch -r → remote
git branch -a → tất cả

- Chuyển sang remote branch khác:
git checkout branch-name

- Xóa nhánh 
git branch -d branch-name

- Xem lịch sử commit :
git log
git log --all --decorate --oneline --graph (alias git l)

- Hoàn tác commit
+ Local (unpublished):

git reset --hard <commit> → reset và bỏ thay đổi

git reset --soft <commit> → reset nhưng giữ thay đổi trong staging

git reset –soft HEAD~1 //xóa commit cuối cùng nhưng những dữ liệu thay đổi sẽ được đưa vào staged để có thể chỉnh sửa và commit.

git reset –hard HEAD~1 //xóa commit cuối cùng k phục hồi lại đc

git reset <commit> → reset, giữ thay đổi (không stage)

+ Remote (published):
git revert <commit> → tạo commit mới để revert thay đổi

- Checkout commits
git checkout <commit>  //xem lại trạng thái repo tại commit

git checkout master  //Quay về branch chính

# Commit references
HEAD → commit hiện tại

HEAD~1 → commit cha của HEAD

master~1 → commit cha của tip của branch master

- Commit search
+ Theo nội dung:
git log -S "Hello, World!" --oneline

+ Theo message:
git log // lịch sử commit đầy đủ 

git log --oneline  // tóm tắt lịch sử commit 

git diff → kiểm tra những thay đổi chưa stage

git diff --staged → kiểm tra những thay đổi đã stage

git diff <commit> → so sánh với commit cụ thể

git diff <commit1> <commit2> → so sánh giữa 2 commit

git diff <commit> -- ./file.txt → so sánh một file cụ thể


git checkout --<tên file> : phục hồi các file của commit nào đó.

git status: kiểm tra trạng thái giữa các vùng làm việc.

git restore <têm file> or git restore . hủy các file trong staged đưa về trạng thái modified.

# Gán tag cho commit
git tag –a “<tên tag>” –m”<thông điêp của tag>” <id của commit>

git showw tag_name // kiểm tra thông tin chi tiết của tag 

git tag -d <ten-tag> // xóa tag

git push -delete <ten-remote> <ten-tag> // xóa tag trong remote

```