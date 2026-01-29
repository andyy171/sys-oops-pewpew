# Tổng quan 
Git là công cụ dòng lệnh (CLI) hoặc công nghệ nền tảng cho phép phiên bản hóa mã nguồn và sự cộng tác giữa nhiều nhà phát triển. Còn Github là kho chứa mã dựa trên Git có thể truy cập công khai, nơi bạn đẩy code của mình lên. Và nó có một giao diện web nơi bạn có thể mời các nhà phát triển mới, quản lý dự án, quản lý các vấn đề (issues) với dự án, thêm tài liệu cho code, v.v


## Các khái niệm cơ bản 

**Repo:** chứa dữ liệu của dự án code,… gồm repo localhos và remote trên các máy server server.

**Commit:** thay đổi, thêm sửa, xóa file, code thì mỗi lần nvay là 1 conmit.

**Branch:** nhánh trong git, tách thành các nhánh để code dễ hơn ( mỗi chức năng là 1 nhánh).

## Thao tác cơ bản 

- Xem cấu hình cơ bản của git 
```
git config --list
```

- Thiết lập username/email cho git 
```
git config --global user.name "username"
git config --global user.email "email"
```

### Các trạng thái cơ bản của file trong git
- **Untracked:** không đươc theo dõi bởi git

- **Unmodified:** không có thay đổi gì
- **committed :** Dữ liệu đã lưu trữ an toàn tên local
- **modified :** Dữ liệu có sự thay đổi nhuwg chưa thực hiện lưu trữ local
- **staged :** Đánh dấu các file sử đổi **modified** chuẩn bị **commit **

<img src="/images/git/bs-status.png">


